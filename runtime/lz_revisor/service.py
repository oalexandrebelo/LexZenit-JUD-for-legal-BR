"""Operações de alto nível compartilhadas pela CLI e pelo servidor MCP."""
from __future__ import annotations

from pathlib import Path

from . import templates
from .catalog import load_catalog
from .engine import resolver_sinais, escolher_n2, revisar, validar_respostas
from .report import to_markdown
from .scanner import scan


class Revisor:
    def __init__(self, catalog_dir: Path | None = None):
        self.catalog = load_catalog(catalog_dir)

    def revisar(self, caminho: str | None, respostas: dict | None = None) -> dict:
        varredura = scan(caminho, self.catalog) if caminho else None
        return revisar(self.catalog, varredura, respostas or {})

    def markdown(self, resultado: dict, titulo: str | None = None) -> str:
        return to_markdown(resultado, titulo or "Revisão jurídica do projeto")

    def sinais(self, caminho: str, respostas: dict | None = None) -> dict:
        respostas = validar_respostas(self.catalog, respostas)
        varredura = scan(caminho, self.catalog)
        sin = resolver_sinais(self.catalog, varredura, respostas)
        return {"escopo": varredura.to_dict(), "sinais": {k: vars(v) for k, v in sin.items() if v.valor is not False}}

    def n2(self, caminho: str | None, respostas: dict | None = None) -> dict:
        respostas = validar_respostas(self.catalog, respostas)
        varredura = scan(caminho, self.catalog) if caminho else None
        return escolher_n2(self.catalog, resolver_sinais(self.catalog, varredura, respostas), respostas)

    def perguntas(self, caminho: str | None, respostas: dict | None = None) -> dict:
        res = self.revisar(caminho, respostas)
        campos = [c for c in self.catalog.questionario["campos"] if c["id"] not in (respostas or {})]
        return {"campos": campos, "perguntas_de_sinais": res["perguntas_pendentes"]}

    def normas(self, nivel: str | None = None, jurisdicao: str | None = None, uf: str | None = None,
               busca: str | None = None) -> list[dict]:
        out = []
        for n in self.catalog.normas:
            if nivel and n["nivel"] != nivel.upper():
                continue
            if jurisdicao and not n["jurisdicao"].startswith(jurisdicao.upper()):
                continue
            if uf and n["jurisdicao"] != f"BR-{uf.upper()}":
                continue
            if busca and busca.lower() not in (n["nome"] + " " + n["citacao"] + " " + n.get("notas", "")).lower():
                continue
            out.append({"id": n["id"], "nivel": n["nivel"], "jurisdicao": n["jurisdicao"], "nome": n["nome"],
                        "citacao": n["citacao"], "status": n["status"], "vigencia": n.get("vigencia"),
                        "fonte": n["fonte"], "obrigacoes": [o["texto"] for o in n["obrigacoes"]],
                        "notas": n.get("notas", "")})
        return out

    def modelos(self) -> list[dict]:
        return templates.listar(self.catalog.root)

    def minuta(self, modelo: str, campos: dict | None = None) -> dict:
        return templates.gerar(self.catalog.root, modelo, campos)
