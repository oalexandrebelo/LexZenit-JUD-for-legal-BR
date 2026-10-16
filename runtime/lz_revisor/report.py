"""Relatório em Markdown a partir do resultado do motor."""
from __future__ import annotations

ROTULO_ESTADO = {
    "nao_conformidade_evidenciada": "Não conformidade evidenciada",
    "inconclusivo": "Inconclusivo",
    "nao_aplicavel_justificado": "Não aplicável",
    "satisfeito_no_escopo": "Satisfeito no escopo",
    "erro": "Erro",
}
ROTULO_VERIF = {"oficial_conferido": "fonte oficial conferida", "fonte_secundaria": "fonte secundária",
                "nao_localizado": "fonte não localizada"}
NOME_NIVEL = {"N1": "N1 · Brasil", "N2": "N2 · país", "N3": "N3 · mundo"}


def _jur(j: str) -> str:
    if j == "BR":
        return "União"
    if j.startswith("BR-"):
        return f"UF {j[3:]}"
    return j


def _c(x) -> str:
    """Célula de tabela Markdown: sem quebra de linha e com '|' escapado."""
    return str(x if x is not None else "").replace("\n", " ").replace("|", "\\|")


def _linha_achado(a: dict) -> str:
    ev = a["evidencias_localizadas"] or a["evidencias_declaradas"]
    if ev:
        evid = "; ".join(f"`{e['local']}`" for e in ev[:3])
    elif a["mencoes"]:
        evid = "menção em " + "; ".join(f"`{e['local']}`" for e in a["mencoes"][:2])
    else:
        evid = "nenhuma no escopo"
    fonte = a["fonte"]
    link = f"[{a['citacao']}]({fonte['url']})" if fonte.get("url") else a["citacao"]
    disp = f" — {a['dispositivo']}" if a.get("dispositivo") else ""
    modelo = f" · minuta: `{a['modelo']}`" if a.get("modelo") and a["lacuna"] else ""
    alerta = f" ⚠ Competência: {a['alerta_competencia']}" if a.get("alerta_competencia") and "competência" not in a["motivo"] else ""
    return (f"| {ROTULO_ESTADO[a['estado']]} | {a['severidade']} | {_jur(a['jurisdicao'])} | "
            f"{_c(a['obrigacao'] + disp)} | {link} ({ROTULO_VERIF[fonte['verificacao']]}) | {evid} | {_c(a['motivo'] + alerta)}{modelo} |")


def to_markdown(res: dict, titulo: str = "Revisão jurídica do projeto") -> str:
    L = [f"# {titulo}", "", f"**{res['marca']}**", ""]
    esc = res.get("escopo") or {}
    L += [f"Gerado em {res['gerado_em']} · catálogo {res['catalogo']['versao']} com {res['catalogo']['normas']} normas"
          + (f" · {esc.get('arquivos_lidos', 0)} arquivos lidos" if esc else " · sem varredura de código")
          + (" · **varredura truncada**" if esc and esc.get("truncada") else ""), ""]
    if esc and esc.get("regras_de_exclusao"):
        L += ["**Exclusões do `.lzrevisorignore`:** " + ", ".join(f"`{_c(x)}`" for x in esc["regras_de_exclusao"][:20])
              + ". Com exclusões ou truncamento, sinal não detectado fica desconhecido.", ""]
    n2 = res["n2"]
    L += ["## Jurisdições", "",
          "- **N1 Brasil:** União e UFs de sede/atuação.",
          f"- **N2:** {n2['pais']} — {n2['motivo']}" + ("" if n2.get("pacote_disponivel") else " (sem pacote de normas para este país no catálogo)"),
          "- **N3 mundo:** normas extraterritoriais, tratados e padrões globais.", ""]
    L += ["## Resumo", "", "| Nível | Não conformidades | Lacunas inconclusivas | Evidências a revisar | Dependem de resposta |",
          "|---|---:|---:|---:|---:|"]
    for n in ("N1", "N2", "N3"):
        c = res["resumo"][n]
        L.append(f"| {NOME_NIVEL[n]} | {c['nao_conformidade_evidenciada']} | {c['lacunas_inconclusivas']} | "
                 f"{c['evidencia_a_revisar']} | {c['dependem_de_resposta']} |")
    L += ["", f"Radar regulatório (projetos e normas suspensas): {res['resumo']['radar']} itens.", ""]
    if res.get("divergencias"):
        L += ["## Respostas que o código contradiz", "",
              "A resposta declarada vale para a análise, mas confira: o código tem indícios do contrário.", ""]
        L += [f"- **{_c(d['rotulo'])}** respondido como não; indícios em " + ", ".join(f"`{_c(x)}`" for x in d["indicios"]) for d in res["divergencias"]]
        L.append("")
    if res["perguntas_pendentes"]:
        L += ["## Perguntas que destravam a análise", ""]
        L += [f"{i}. {p}" for i, p in enumerate(res["perguntas_pendentes"], 1)]
        L.append("")
    detect = {k: v for k, v in res["sinais"].items() if v["valor"]}
    if detect:
        L += ["## O que o projeto faz (sinais)", "", "| Sinal | Origem | Confiança | Indícios |", "|---|---|---|---|"]
        for k, v in detect.items():
            locs = []
            for i in v.get("indicios", [])[:2]:
                locs += i.get("locais", [])[:2] or [i.get("rotulo")]
            L.append(f"| {k} | {v['origem']} | {v['confianca'] or '—'} | {'; '.join(f'`{x}`' for x in locs[:3])} |")
        L.append("")
    cab = ["| Estado | Severidade | Jurisdição | Obrigação | Norma | Evidência | Motivo |",
           "|---|---|---|---|---|---|---|"]
    for n in ("N1", "N2", "N3"):
        sel = [a for a in res["achados"] if a["nivel"] == n]
        if not sel:
            continue
        L += [f"## {NOME_NIVEL[n]}", ""]
        aplic = [a for a in sel if a["modo"] != "prontidao"]
        pront = [a for a in sel if a["modo"] == "prontidao"]
        if aplic:
            L += cab + [_linha_achado(a) for a in aplic] + [""]
        if pront:
            L += ["### Prontidão (jurisdição sem usuários declarados)", ""] + cab + [_linha_achado(a) for a in pront] + [""]
    if res["radar_regulatorio"]:
        L += ["## Radar regulatório", "", "Projetos de lei e normas suspensas: não geram obrigação hoje.", "",
              "| Norma | Jurisdição | Status | Relevância | Nota |", "|---|---|---|---|---|"]
        for r in res["radar_regulatorio"]:
            link = f"[{r['citacao']}]({r['fonte']['url']})" if r["fonte"].get("url") else r["citacao"]
            L.append(f"| {_c(r['norma'])} ({link}) | {_jur(r['jurisdicao'])} | {r['status_norma']} | {r['relevancia']} | {_c(r.get('notas', ''))} |")
        L.append("")
    if res.get("oportunidades"):
        L += ["## Oportunidades (sandbox, compras de inovação, fomento)", "",
              "Não são obrigações: são programas e regimes que o projeto pode usar.", "",
              "| Norma | Jurisdição | Pontos | Fonte |", "|---|---|---|---|"]
        for o in res["oportunidades"]:
            link = f"[{o['citacao']}]({o['fonte']['url']})" if o["fonte"].get("url") else o["citacao"]
            L.append(f"| {_c(o['norma'])} | {_jur(o['jurisdicao'])} | {_c('; '.join(o['pontos'][:3]))} | {link} ({ROTULO_VERIF[o['fonte']['verificacao']]}) |")
        L.append("")
    if res["modelos_sugeridos"]:
        L += ["## Minutas sugeridas", "", "Gere com `python -m lz_revisor minuta <id>` ou pela ferramenta MCP `gerar_minuta`:", ""]
        L += [f"- `{m}`" for m in res["modelos_sugeridos"]]
        L.append("")
    if res["nao_aplicaveis"]:
        L += ["<details><summary>Não aplicáveis neste escopo ({})</summary>".format(len(res["nao_aplicaveis"])), ""]
        for a in res["nao_aplicaveis"][:400]:
            alvo = a.get("obrigacao") or a["norma"]
            L.append(f"- {_jur(a['jurisdicao'])} · {a['norma_id']}: {alvo} — {a.get('motivo') or a.get('motivo_jurisdicao')}")
        L += ["", "</details>", ""]
    L += ["## Limitações", ""] + [f"- {x}" for x in res["limitacoes"]] + [""]
    pv = res.get("proveniencia") or {}
    if pv:
        L += [f"Proveniência: {pv.get('motor')} · data de referência {pv.get('data_de_referencia')} · catálogo `{pv.get('catalogo_sha256', '')[:12]}` · respostas `{pv.get('respostas_sha256', '')[:12]}`", ""]
    L += ["Responsável pela revisão: ______________________  OAB/UF: ________  Data: ___/___/______", ""]
    return "\n".join(L)
