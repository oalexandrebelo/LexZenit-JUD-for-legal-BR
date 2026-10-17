"""Exporta o resultado em SARIF 2.1.0 (GitHub code scanning e outras ferramentas de CI).

Só lacunas entram: não conformidade evidenciada vira "error"; lacuna inconclusiva, "warning".
O local é o indício do gatilho (arquivo:linha) quando existe; sem indício, o resultado vai sem local.
"""
from __future__ import annotations

import re

from . import __version__

NIVEL = {"nao_conformidade_evidenciada": "error"}
LOCAL = re.compile(r"^([^\s:]+):(\d+)$")


def _locais(achado: dict, sinais: dict) -> list[dict]:
    out = []
    for sid in achado.get("sinais_gatilho") or []:
        for ind in (sinais.get(sid) or {}).get("indicios") or []:
            for loc in ind.get("locais") or []:
                m = LOCAL.match(loc)
                if m and len(out) < 3:
                    out.append({"physicalLocation": {"artifactLocation": {"uri": m.group(1)},
                                                     "region": {"startLine": int(m.group(2))}}})
    return out


def to_sarif(res: dict) -> dict:
    regras, resultados, vistos = [], [], set()
    for a in res["achados"]:
        if a["estado"] != "nao_conformidade_evidenciada" and not (a["estado"] == "inconclusivo" and a["lacuna"] is True):
            continue
        rid = f"{a['norma_id']}/{a['obrigacao_id']}"
        if rid not in vistos:
            vistos.add(rid)
            regra = {"id": rid, "name": a["norma_id"],
                     "shortDescription": {"text": a["obrigacao"][:300]},
                     "fullDescription": {"text": f"{a['citacao']}" + (f" — {a['dispositivo']}" if a.get("dispositivo") else "")},
                     "properties": {"nivel": a["nivel"], "jurisdicao": a["jurisdicao"], "severidade": a["severidade"],
                                    "natureza": a["natureza"], "verificacao_fonte": a["fonte"]["verificacao"]}}
            if a["fonte"].get("url"):
                regra["helpUri"] = a["fonte"]["url"]
            regras.append(regra)
        r = {"ruleId": rid, "level": NIVEL.get(a["estado"], "warning"),
             "message": {"text": f"[{a['nivel']} · {a['severidade']}] {a['obrigacao']} — {a['motivo']}"
                                 + (f" Minuta: {a['modelo']}." if a.get("modelo") else "")},
             "properties": {"estado": a["estado"], "modo": a["modo"]}}
        locs = _locais(a, res.get("sinais") or {})
        if locs:
            r["locations"] = locs
        resultados.append(r)
    return {"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": "lz-revisor", "version": __version__,
                                          "informationUri": "https://github.com/oalexandrebelo/LexZenit-JUD-for-legal-BR",
                                          "rules": regras}},
                      "results": resultados,
                      "properties": {"marca": res["marca"], "proveniencia": res.get("proveniencia")}}]}
