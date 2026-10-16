"""Radar de projetos de lei pela API de dados abertos da Câmara dos Deputados.

Único módulo do revisor que acessa a rede, e só quando o operador roda
`python -m lz_revisor radar`. O servidor MCP e a revisão nunca o chamam.
Não altera o catálogo: lista o status atual de cada projeto e marca o que mudou
depois da última conferência, para revisão humana pela skill atualizar-catalogo.
"""
from __future__ import annotations

import json
import re
import urllib.request
from urllib.parse import urlsplit

API = "https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}"
HOSTS = {"dadosabertos.camara.leg.br"}
FICHA = re.compile(r"camara\.leg\.br/proposicoesWeb/fichadetramitacao\?idProposicao=(\d+)")


def _fetch(url: str) -> dict:
    if urlsplit(url).hostname not in HOSTS or not url.startswith("https://"):
        raise ValueError(f"Host não permitido no radar: {url}")
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "lz-revisor-radar/0.3.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 — host fixo e https
        return json.loads(resp.read().decode("utf8"))


def proposicoes(catalog) -> list[tuple[dict, str]]:
    """Normas do catálogo cuja fonte é a ficha de tramitação da Câmara."""
    out = []
    for n in catalog.normas:
        m = FICHA.search((n.get("fonte") or {}).get("url") or "")
        if m:
            out.append((n, m.group(1)))
    return out


def consultar(catalog, fetch=_fetch) -> list[dict]:
    itens = []
    for norma, pid in proposicoes(catalog):
        base = {"norma_id": norma["id"], "norma": norma["nome"], "id_camara": pid,
                "verificado_em": norma["fonte"].get("verificado_em"), "status_catalogo": norma["status"]}
        try:
            dados = fetch(API.format(id=pid))["dados"]
        except Exception as exc:  # rede, HTTP ou JSON inesperado: registrar e seguir
            itens.append({**base, "erro": f"{type(exc).__name__}: {exc}"})
            continue
        st = dados.get("statusProposicao") or {}
        data = (st.get("dataHora") or "")[:10]
        itens.append({**base,
                      "proposicao": f"{dados.get('siglaTipo')} {dados.get('numero')}/{dados.get('ano')}",
                      "situacao": st.get("descricaoSituacao"), "tramitacao": st.get("descricaoTramitacao"),
                      "orgao": st.get("siglaOrgao"), "data": data, "despacho": st.get("despacho"),
                      "mudou": bool(data and base["verificado_em"] and data > base["verificado_em"])})
    return itens


def to_markdown(itens: list[dict]) -> str:
    L = ["# Radar de projetos de lei · Câmara dos Deputados", "",
         "Fonte: API de dados abertos da Câmara. O catálogo não foi alterado; atualize-o pela skill atualizar-catalogo após revisão.", "",
         "| Norma | Proposição | Situação | Última movimentação | Mudou desde a conferência |", "|---|---|---|---|---|"]
    for i in itens:
        if i.get("erro"):
            L.append(f"| {i['norma_id']} | id {i['id_camara']} | erro: {i['erro']} | — | — |")
            continue
        mov = f"{i['data']} · {i.get('orgao') or ''} · {i.get('tramitacao') or ''}".replace("|", "/")
        L.append(f"| {i['norma_id']} | {i['proposicao']} | {(i.get('situacao') or '').replace('|', '/')} | {mov} | "
                 f"{'sim' if i['mudou'] else 'não'} (conferida em {i.get('verificado_em') or 'sem data'}) |")
    return "\n".join(L) + "\n"
