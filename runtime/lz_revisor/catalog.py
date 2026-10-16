"""Carga e validação do catálogo normativo (Legislação como Código)."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

NIVEIS = {"N1", "N2", "N3"}
STATUS = {"vigente", "parcialmente_vigente", "vigencia_futura", "em_tramitacao", "suspensa", "revogada"}
VERIFICACAO = {"oficial_conferido", "fonte_secundaria", "nao_localizado"}
SEVERIDADE = ["critica", "alta", "media", "baixa"]
NATUREZA = {"obrigacao_legal", "boa_pratica", "exigencia_mercado", "vedacao"}
RELEVANCIA = {"obrigacao", "oportunidade"}
UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB",
       "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}


class CatalogError(ValueError):
    """Catálogo inválido: o motor recusa operar com regra quebrada."""


def default_catalog_dir() -> Path:
    env = os.environ.get("LZ_REVISOR_CATALOG")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "br-project-review" / "references" / "catalog"


def _load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"{path.name}: {exc}") from exc


@dataclass
class Catalog:
    root: Path
    versao: str
    sinais: dict
    evidencias: dict
    questionario: dict
    regra_n2: dict
    normas: list
    arquivos_normas: list = field(default_factory=list)

    def norma(self, norma_id: str) -> dict | None:
        return next((n for n in self.normas if n["id"] == norma_id), None)


def _expr_signals(expr, out: set) -> None:
    if expr is True or expr is None:
        return
    if isinstance(expr, str):
        out.add(expr)
        return
    if isinstance(expr, dict) and len(expr) == 1:
        (op, val), = expr.items()
        if op in ("todos", "algum"):
            if not isinstance(val, list) or not val:
                raise CatalogError(f"'{op}' exige lista não vazia")
            for item in val:
                _expr_signals(item, out)
            return
        if op == "nao":
            _expr_signals(val, out)
            return
    raise CatalogError(f"Expressão de gatilho inválida: {expr!r}")


def _check_jurisdicao(j: str, nivel: str) -> None:
    if nivel == "N1":
        if j == "BR":
            return
        if j.startswith("BR-") and j[3:] in UFS:
            return
        raise CatalogError(f"Jurisdição N1 inválida: {j}")
    if not j or not j.replace("-", "").isalnum() or j != j.upper():
        raise CatalogError(f"Jurisdição inválida: {j}")


def validate(cat: Catalog) -> None:
    sinais = set(cat.sinais)
    evid = set(cat.evidencias)
    ids = set()
    for n in cat.normas:
        nid = n.get("id")
        if not nid or nid in ids:
            raise CatalogError(f"ID de norma ausente ou duplicado: {nid}")
        ids.add(nid)
        for key in ("nivel", "jurisdicao", "nome", "citacao", "tipo", "status", "fonte", "gatilho", "obrigacoes"):
            if key not in n:
                raise CatalogError(f"{nid}: campo obrigatório ausente: {key}")
        if n["nivel"] not in NIVEIS:
            raise CatalogError(f"{nid}: nível inválido")
        _check_jurisdicao(n["jurisdicao"], n["nivel"])
        if n["status"] not in STATUS:
            raise CatalogError(f"{nid}: status inválido {n['status']}")
        fonte = n["fonte"]
        url = fonte.get("url")
        if url:
            parts = urlsplit(url)
            if parts.scheme != "https" or not parts.hostname:
                raise CatalogError(f"{nid}: fonte precisa ser https")
        if fonte.get("verificacao") not in VERIFICACAO:
            raise CatalogError(f"{nid}: estado de verificação inválido")
        if fonte["verificacao"] == "oficial_conferido" and not (url and fonte.get("verificado_em")):
            raise CatalogError(f"{nid}: conferência oficial exige URL e data")
        inicio = (n.get("vigencia") or {}).get("inicio")
        if n["status"] == "vigencia_futura" and not inicio:
            raise CatalogError(f"{nid}: vigência futura exige vigencia.inicio")
        if inicio and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(inicio)):
            raise CatalogError(f"{nid}: vigencia.inicio deve ser data ISO (AAAA-MM-DD)")
        if fonte.get("verificado_em") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(fonte["verificado_em"])):
            raise CatalogError(f"{nid}: verificado_em deve ser data ISO (AAAA-MM-DD)")
        if n.get("relevancia", "obrigacao") not in RELEVANCIA:
            raise CatalogError(f"{nid}: relevância inválida")
        if n.get("relevancia", "obrigacao") == "obrigacao" and n["status"] not in ("em_tramitacao", "suspensa") \
                and not n["obrigacoes"]:
            raise CatalogError(f"{nid}: norma de obrigação sem obrigações")
        usados: set = set()
        _expr_signals(n["gatilho"], usados)
        for ob in n["obrigacoes"]:
            for key in ("id", "texto", "severidade", "natureza", "evidencias"):
                if key not in ob:
                    raise CatalogError(f"{nid}: obrigação sem {key}")
            if ob["severidade"] not in SEVERIDADE:
                raise CatalogError(f"{nid}/{ob['id']}: severidade inválida")
            if ob["natureza"] not in NATUREZA:
                raise CatalogError(f"{nid}/{ob['id']}: natureza inválida")
            for e in ob["evidencias"]:
                if e not in evid:
                    raise CatalogError(f"{nid}/{ob['id']}: evidência desconhecida {e}")
            _expr_signals(ob.get("gatilho", True), usados)
        desconhecidos = usados - sinais
        if desconhecidos:
            raise CatalogError(f"{nid}: sinais desconhecidos {sorted(desconhecidos)}")


def load_catalog(root: Path | None = None) -> Catalog:
    root = Path(root) if root else default_catalog_dir()
    if not root.is_dir():
        raise CatalogError(f"Catálogo não encontrado em {root}")
    sinais_doc = _load(root / "sinais.json")
    evid_doc = _load(root / "evidencias.json")
    sinais = {s["id"]: s for s in sinais_doc["sinais"]}
    if len(sinais) != len(sinais_doc["sinais"]):
        raise CatalogError("Sinal duplicado")
    evidencias = {e["id"]: e for e in evid_doc["evidencias"]}
    if len(evidencias) != len(evid_doc["evidencias"]):
        raise CatalogError("Evidência duplicada")
    normas: list = []
    arquivos = []
    for path in sorted((root / "normas").glob("*.json")):
        doc = _load(path)
        arquivos.append({"arquivo": path.name, "normas": len(doc.get("normas", [])), "gerado_em": doc.get("gerado_em")})
        for n in doc.get("normas", []):
            n = dict(n)
            n["_arquivo"] = path.name
            normas.append(n)
    cat = Catalog(root=root, versao=sinais_doc.get("versao", "?"), sinais=sinais, evidencias=evidencias,
                  questionario=_load(root / "questionario.json"), regra_n2=_load(root / "regra-n2.json"),
                  normas=normas, arquivos_normas=arquivos)
    validate(cat)
    return cat
