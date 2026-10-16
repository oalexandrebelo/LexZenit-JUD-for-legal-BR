"""Leitura do projeto: sinais (o que o projeto faz) e evidências (o que ele já documenta).

Princípios:
- só leitura; nenhum arquivo do projeto é alterado ou executado;
- o relatório guarda caminho e linha do indício, nunca o texto casado (pode conter dado pessoal ou segredo);
- ausência de detecção não prova ausência da característica.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import stat
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

IGNORAR_DIRS = {".git", ".hg", ".svn", "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build", "out",
                "coverage", ".venv", "venv", "env", "__pycache__", ".turbo", ".cache", "vendor", "Pods", ".gradle",
                "target", ".expo", ".idea", ".pytest_cache", ".mypy_cache", ".tox", "site-packages", ".dart_tool",
                ".terraform", "bower_components", ".parcel-cache", "storybook-static"}
IGNORAR_ARQUIVOS = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "Cargo.lock",
                    "composer.lock", "Gemfile.lock", "bun.lockb", "go.sum"}
EXT_TEXTO = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro", ".py", ".rb", ".go", ".java",
             ".kt", ".kts", ".swift", ".dart", ".php", ".cs", ".rs", ".scala", ".ex", ".exs", ".sql", ".prisma",
             ".graphql", ".gql", ".html", ".htm", ".css", ".scss", ".md", ".mdx", ".txt", ".rst", ".json", ".yaml",
             ".yml", ".toml", ".xml", ".env.example", ".sh", ".tf", ".ini", ".cfg", ".properties", ".gradle"}
NOMES_TEXTO = {"LICENSE", "LICENCE", "COPYING", "NOTICE", "Dockerfile", "Makefile", "Gemfile", "Pipfile", "Procfile",
               "README", "SECURITY", "CODEOWNERS"}
EXT_DOC = {".md", ".mdx", ".txt", ".rst", ".pdf", ".html", ".htm", ".docx", ".odt", ".rtf", ".adoc"}
NOMES_DOC = {"LICENSE", "LICENCE", "COPYING", "NOTICE", "SECURITY", "THIRD_PARTY_NOTICES"}
MAX_ARQUIVOS = 25000
MAX_BYTES = 400_000
MAX_LOCAIS = 4


def _match(path: str, pattern: str) -> bool:
    path = path.lower()
    pattern = pattern.lower()
    if fnmatch.fnmatchcase(path, pattern):
        return True
    if pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]):
        return True
    return False


def _match_doc(path: str, pattern: str) -> bool:
    """Glob de evidência: sem extensão explícita no padrão, só casa documento (md, pdf, html...)."""
    if not _match(path, pattern):
        return False
    if re.search(r"\.[a-z0-9]+\*?$", pattern.lower()):
        return True
    nome = path.rsplit("/", 1)[-1]
    base = nome.split(".", 1)[0].upper()
    suf = ("." + nome.rsplit(".", 1)[-1].lower()) if "." in nome else ""
    return suf in EXT_DOC or base in NOMES_DOC


def _termo_regex(termo: str) -> re.Pattern:
    """Termo com fronteira de palavra nas pontas alfanuméricas ('SAC' não casa 'transaction')."""
    pre = r"(?<!\w)" if termo[:1].isalnum() else ""
    pos = r"(?!\w)" if termo[-1:].isalnum() else ""
    return re.compile(pre + re.escape(termo) + pos, re.I)


def _norm_dep(name: str) -> str:
    return name.strip().lower()


def _parse_deps(rel: str, text: str) -> set[str]:
    nome = rel.rsplit("/", 1)[-1]
    deps: set[str] = set()
    try:
        if nome == "package.json" or nome == "composer.json":
            data = json.loads(text)
            for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies", "require", "require-dev"):
                deps.update(_norm_dep(k) for k in (data.get(key) or {}))
        elif re.fullmatch(r"requirements.*\.txt", nome):
            for line in text.splitlines():
                line = line.split("#", 1)[0].strip()
                if line and not line.startswith("-"):
                    deps.add(_norm_dep(re.split(r"[<>=!~;\[\s]", line, maxsplit=1)[0]))
        elif nome in ("pyproject.toml", "Pipfile", "Cargo.toml"):
            data = tomllib.loads(text)
            for spec in (data.get("project", {}).get("dependencies") or []):
                deps.add(_norm_dep(re.split(r"[<>=!~;\[\s]", spec, maxsplit=1)[0]))
            for grp in (data.get("project", {}).get("optional-dependencies") or {}).values():
                for spec in grp:
                    deps.add(_norm_dep(re.split(r"[<>=!~;\[\s]", spec, maxsplit=1)[0]))
            poetry = data.get("tool", {}).get("poetry", {})
            deps.update(_norm_dep(k) for k in (poetry.get("dependencies") or {}))
            for grp in (poetry.get("group") or {}).values():
                deps.update(_norm_dep(k) for k in (grp.get("dependencies") or {}))
            for key in ("packages", "dev-packages", "dependencies", "dev-dependencies"):
                if isinstance(data.get(key), dict):
                    deps.update(_norm_dep(k) for k in data[key])
        elif nome == "go.mod":
            for m in re.finditer(r"^[ \t]*(?:require[ \t]+)?([\w.\-]+\.[a-z]{2,}/[\w./\-]+)[ \t]+v", text, re.M):
                path = m.group(1).lower()
                deps.add(path)
                deps.add(path.rsplit("/", 1)[-1])
        elif nome == "Gemfile":
            deps.update(_norm_dep(m.group(1)) for m in re.finditer(r"^[ \t]*gem[ \t]+['\"]([^'\"]+)", text, re.M))
        elif nome == "pubspec.yaml":
            bloco = re.search(r"^dependencies:\s*\n((?:[ \t]+.*\n?)*)", text, re.M)
            if bloco:
                deps.update(_norm_dep(m.group(1)) for m in re.finditer(r"^\s{2}([a-z0-9_]+):", bloco.group(1), re.M))
            if "flutter:" in text:
                deps.add("flutter")
        elif nome.startswith("build.gradle"):
            deps.update(_norm_dep(m.group(1)) for m in re.finditer(r"['\"][\w.\-]+:([\w.\-]+):", text))
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, AttributeError, TypeError):
        pass
    if nome in ("requirements.txt",) or nome.endswith(".toml") or nome == "Pipfile":
        deps |= {d.replace("_", "-") for d in deps}
    return {d for d in deps if d}


MANIFESTOS = re.compile(r"(package\.json|composer\.json|requirements.*\.txt|pyproject\.toml|Pipfile|Cargo\.toml|go\.mod|Gemfile|pubspec\.yaml|build\.gradle(\.kts)?)$")


@dataclass
class Indicio:
    origem: str          # dependencia | codigo | arquivo
    rotulo: str
    confianca: str       # alta | media | baixa
    locais: list = field(default_factory=list)
    ocorrencias: int = 0


@dataclass
class Varredura:
    raiz: str
    arquivos_lidos: int
    arquivos_ignorados: int
    truncada: bool
    dependencias: list
    sinais: dict          # id -> list[Indicio]
    evidencias: dict      # id -> {"documentos": [...], "mencoes": [...]}
    ignorados_por_regra: list

    def to_dict(self) -> dict:
        return {
            "raiz": self.raiz, "arquivos_lidos": self.arquivos_lidos, "arquivos_ignorados": self.arquivos_ignorados,
            "truncada": self.truncada, "dependencias_detectadas": len(self.dependencias),
            "sinais": {k: [vars(i) for i in v] for k, v in self.sinais.items()},
            "evidencias": self.evidencias, "regras_de_exclusao": self.ignorados_por_regra,
        }


def _ignore_patterns(root: Path) -> list[str]:
    path = root / ".lzrevisorignore"
    if not path.is_file():
        return []
    return [l.strip() for l in path.read_text(encoding="utf8", errors="replace").splitlines()
            if l.strip() and not l.strip().startswith("#")]


def _is_text(path: Path) -> bool:
    if path.name in NOMES_TEXTO or path.name.split(".")[0] in NOMES_TEXTO:
        return True
    suf = "".join(path.suffixes[-2:]) if path.name.endswith(".env.example") else path.suffix.lower()
    return suf in EXT_TEXTO


def scan(root: str | Path, catalog) -> Varredura:
    root = Path(root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Diretório não encontrado: {root}")
    ignore = _ignore_patterns(root)
    sinais_cat = catalog.sinais
    evid_cat = catalog.evidencias

    regex_sinais = []
    for sid, s in sinais_cat.items():
        for p in s.get("codigo", []):
            regex_sinais.append((sid, re.compile(p["padrao"], re.I), p["rotulo"], p["confianca"]))
    regex_evid_termos = []
    for eid, e in evid_cat.items():
        for termo in e.get("termos", []):
            regex_evid_termos.append((eid, _termo_regex(termo), termo))
        for padrao in e.get("codigo", []):
            regex_evid_termos.append((eid, re.compile(padrao, re.I), "rota ou código"))

    achados: dict[str, dict[tuple, Indicio]] = {}
    evid: dict[str, dict] = {}
    deps: set[str] = set()
    lidos = ignorados = 0
    truncada = False
    arquivos_rel: list[str] = []

    def add(sid, origem, rotulo, conf, local=None):
        bucket = achados.setdefault(sid, {})
        key = (origem, rotulo)
        ind = bucket.get(key)
        if not ind:
            ind = bucket[key] = Indicio(origem=origem, rotulo=rotulo, confianca=conf)
        ind.ocorrencias += 1
        if local and len(ind.locais) < MAX_LOCAIS and local not in ind.locais:
            ind.locais.append(local)

    def add_evid(eid, tipo, local):
        b = evid.setdefault(eid, {"documentos": [], "mencoes": []})
        if local not in b[tipo] and len(b[tipo]) < MAX_LOCAIS:
            b[tipo].append(local)

    for dirpath, dirnames, filenames in os.walk(root):
        reldir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        reldir = "" if reldir == "." else reldir
        keep = []
        for d in dirnames:
            rel = f"{reldir}/{d}" if reldir else d
            if d in IGNORAR_DIRS or any(_match(rel, p) or _match(rel + "/", p) for p in ignore):
                ignorados += 1
                continue
            if os.path.islink(os.path.join(dirpath, d)):
                ignorados += 1
                continue
            keep.append(d)
        dirnames[:] = sorted(keep)
        for fn in sorted(filenames):
            rel = f"{reldir}/{fn}" if reldir else fn
            full = Path(dirpath) / fn
            if fn in IGNORAR_ARQUIVOS or fn.endswith((".min.js", ".map")) or full.is_symlink() \
                    or any(_match(rel, p) for p in ignore):
                ignorados += 1
                continue
            if lidos >= MAX_ARQUIVOS:
                truncada = True
                break
            arquivos_rel.append(rel)
            # sinais por caminho de arquivo
            for sid, s in sinais_cat.items():
                for pat in s.get("arquivos", []):
                    if _match(rel, pat):
                        add(sid, "arquivo", pat, s.get("confianca_arquivos", "alta"), rel)
            # evidências por documento dedicado
            for eid, e in evid_cat.items():
                if any(_match_doc(rel, pat) for pat in e.get("arquivos", [])):
                    add_evid(eid, "documentos", rel)
            if not _is_text(full):
                continue
            try:
                if not stat.S_ISREG(full.stat().st_mode):   # FIFO, socket, dispositivo: nunca ler
                    ignorados += 1
                    continue
            except OSError:
                ignorados += 1
                continue
            try:
                if full.stat().st_size > MAX_BYTES:
                    ignorados += 1
                    continue
                text = full.read_text(encoding="utf8", errors="replace")
            except OSError:
                ignorados += 1
                continue
            lidos += 1
            if MANIFESTOS.search(fn):
                deps |= _parse_deps(rel, text)
            linhas = text.splitlines()
            for sid, rx, rotulo, conf in regex_sinais:
                for i, line in enumerate(linhas, 1):
                    if rx.search(line):
                        add(sid, "codigo", rotulo, conf, f"{rel}:{i}")
                        break
            for eid, rx, termo in regex_evid_termos:
                for i, line in enumerate(linhas, 1):
                    if rx.search(line):
                        add_evid(eid, "mencoes", f"{rel}:{i}")
                        break
        if truncada:
            break

    for sid, s in sinais_cat.items():
        for dep in s.get("dependencias", []):
            if _norm_dep(dep) in deps:
                add(sid, "dependencia", dep, s.get("confianca_dependencias", "alta"))
    for eid, e in evid_cat.items():
        for dep in e.get("dependencias", []):
            if _norm_dep(dep) in deps:
                add_evid(eid, "documentos", f"dependência {dep}")

    return Varredura(
        raiz=str(root), arquivos_lidos=lidos, arquivos_ignorados=ignorados, truncada=truncada,
        dependencias=sorted(deps),
        sinais={k: list(v.values()) for k, v in sorted(achados.items())},
        evidencias=dict(sorted(evid.items())),
        ignorados_por_regra=ignore,
    )
