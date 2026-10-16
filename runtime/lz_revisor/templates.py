"""Minutas brasileiras: listagem e preenchimento de campos {{campo}}.

As minutas ficam no plugin (br-project-review/references/templates). Preencher campos não
torna o documento válido: a saída continua marcada como minuta para revisão profissional.
"""
from __future__ import annotations

import re
from pathlib import Path

CAMPO = re.compile(r"\{\{\s*([a-z0-9_]+)\s*\}\}")


def templates_dir(catalog_root: Path) -> Path:
    return Path(catalog_root).parent / "templates"


def _frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    head, body = text[4:].split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        if ": " in line:
            k, v = line.split(": ", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, body


def listar(catalog_root: Path) -> list[dict]:
    out = []
    for p in sorted(templates_dir(catalog_root).glob("*.md")):
        meta, body = _frontmatter(p.read_text(encoding="utf8"))
        out.append({"id": p.stem, "titulo": meta.get("titulo", p.stem), "uso": meta.get("uso", ""),
                    "base_legal": meta.get("base_legal", ""), "campos": sorted(set(CAMPO.findall(body)))})
    return out


def gerar(catalog_root: Path, modelo: str, campos: dict | None = None) -> dict:
    if not re.fullmatch(r"[a-z0-9-]+", modelo or ""):
        raise ValueError("Identificador de minuta inválido.")
    path = templates_dir(catalog_root) / f"{modelo}.md"
    if not path.is_file():
        raise ValueError(f"Minuta não encontrada: {modelo}")
    meta, body = _frontmatter(path.read_text(encoding="utf8"))
    campos = {k: str(v) for k, v in (campos or {}).items() if re.fullmatch(r"[a-z0-9_]+", k)}
    faltando = sorted({c for c in CAMPO.findall(body) if c not in campos})
    texto = CAMPO.sub(lambda m: campos.get(m.group(1), m.group(0)), body)
    return {"id": modelo, "titulo": meta.get("titulo", modelo), "texto": texto.strip() + "\n",
            "campos_pendentes": faltando,
            "aviso": "MINUTA — REVISÃO PROFISSIONAL OBRIGATÓRIA. Campos entre {{ }} ainda precisam ser preenchidos."}
