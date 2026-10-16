"""Regras: sinais + respostas → jurisdições (N1/N2/N3) → obrigações → estado de cada obrigação.

Estados seguem a política do pacote (docs/POLICY.md):
satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro.
O motor nunca declara 'satisfeito_no_escopo': localizar um documento não prova que ele cumpre a norma.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .catalog import SEVERIDADE, UFS
from .scanner import Varredura

CONF_ORDEM = {"alta": 3, "media": 2, "baixa": 1}
ESCOPO_GLOBAL = {"EU", "INT", "ISO"}  # N3 avaliado como prontidão mesmo sem país no alcance
ESTAGIOS = ("ideia", "mvp", "tracao", "escala")


# ── respostas ───────────────────────────────────────────────────────────────

_LISTAS = ("ufs_atuacao", "paises_alvo", "us_estados")
_TEXTOS = ("sede_uf", "mercado_principal", "pais_n2", "estagio")


def validar_respostas(catalog, respostas: dict | None) -> dict:
    """Recusa respostas com tipo errado: 'false' em texto não pode virar verdadeiro."""
    r = respostas or {}
    if not isinstance(r, dict):
        raise ValueError("respostas deve ser um objeto JSON")
    sinais = r.get("sinais") or {}
    if not isinstance(sinais, dict):
        raise ValueError("respostas.sinais deve ser um objeto {sinal: true|false|null}")
    for sid, v in sinais.items():
        if sid not in catalog.sinais:
            raise ValueError(f"Sinal desconhecido em respostas.sinais: {sid}")
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"respostas.sinais.{sid} deve ser true, false ou null (recebido {v!r})")
    for k in _LISTAS:
        if r.get(k) is not None and not (isinstance(r[k], list) and all(isinstance(x, str) for x in r[k])):
            raise ValueError(f"respostas.{k} deve ser lista de textos")
    for k in _TEXTOS:
        if r.get(k) is not None and not isinstance(r[k], str):
            raise ValueError(f"respostas.{k} deve ser texto")
    if r.get("estagio") and r["estagio"] not in ESTAGIOS:
        raise ValueError(f"respostas.estagio deve ser um de {', '.join(ESTAGIOS)}")
    if r.get("evidencias") is not None and not isinstance(r["evidencias"], dict):
        raise ValueError("respostas.evidencias deve ser um objeto {evidencia: local}")
    for eid in (r.get("evidencias") or {}):
        if eid not in catalog.evidencias:
            raise ValueError(f"Evidência desconhecida em respostas.evidencias: {eid}")
    return r


# ── sinais ──────────────────────────────────────────────────────────────────

@dataclass
class EstadoSinal:
    valor: bool | None          # True, False ou None (desconhecido)
    origem: str                  # declarado | detectado | nao_detectado | desconhecido
    confianca: str | None = None
    indicios: list = field(default_factory=list)


def resolver_sinais(catalog, varredura: Varredura | None, respostas: dict) -> dict[str, EstadoSinal]:
    declarados = (respostas or {}).get("sinais", {}) or {}
    out: dict[str, EstadoSinal] = {}
    for sid, s in catalog.sinais.items():
        if sid in declarados and declarados[sid] is not None:
            out[sid] = EstadoSinal(declarados[sid], "declarado", "alta")
            continue
        detectores = s.get("dependencias") or s.get("codigo") or s.get("arquivos")
        indicios = varredura.sinais.get(sid, []) if varredura else []
        if indicios:
            conf = max((i.confianca for i in indicios), key=lambda c: CONF_ORDEM[c])
            out[sid] = EstadoSinal(True, "detectado", conf, [vars(i) for i in indicios])
        elif detectores and varredura is not None and not (varredura.truncada or varredura.ignorados_por_regra):
            out[sid] = EstadoSinal(False, "nao_detectado")
        else:
            out[sid] = EstadoSinal(None, "desconhecido")
    return out


def avaliar(expr, sinais: dict[str, EstadoSinal]):
    """Lógica de três valores (Kleene). Retorna (valor, sinais_usados)."""
    if expr is True or expr is None:
        return True, set()
    if isinstance(expr, str):
        return sinais[expr].valor, {expr}
    (op, val), = expr.items()
    if op == "nao":
        v, used = avaliar(val, sinais)
        return (None if v is None else not v), used
    resultados = [avaliar(e, sinais) for e in val]
    used = set().union(*(u for _, u in resultados))
    vals = [v for v, _ in resultados]
    if op == "todos":
        if any(v is False for v in vals):
            return False, used
        return (None if any(v is None for v in vals) else True), used
    if any(v is True for v in vals):
        return True, used
    return (None if any(v is None for v in vals) else False), used


# ── N2 ──────────────────────────────────────────────────────────────────────

def escolher_n2(catalog, sinais: dict[str, EstadoSinal], respostas: dict) -> dict:
    regra = catalog.regra_n2
    disponiveis = regra["jurisdicoes_disponiveis"]
    ue = set(regra["membros_ue"])
    r = respostas or {}
    fixado = (r.get("pais_n2") or "").upper().strip()
    if fixado:
        bloco = "EU" if fixado in ue else fixado
        return {"pais": fixado, "bloco": bloco, "regra": "fixado",
                "motivo": f"País N2 fixado no questionário: {disponiveis.get(fixado, fixado)}.",
                "pacote_disponivel": bloco in disponiveis}
    alvos = [p.upper() for p in (r.get("paises_alvo") or []) if p and p.upper() != "BR"]
    principal = (r.get("mercado_principal") or "").upper().strip()
    if principal and principal != "BR":
        bloco = "EU" if principal in ue else principal
        return {"pais": principal, "bloco": bloco, "regra": "mercado_principal",
                "motivo": f"Mercado estrangeiro principal declarado (receita ou usuários): {disponiveis.get(principal, principal)}.",
                "pacote_disponivel": bloco in disponiveis}
    if "US" in alvos:
        return {"pais": "US", "bloco": "US", "regra": "eua_no_alvo",
                "motivo": "Os EUA estão entre os países-alvo declarados.", "pacote_disponivel": True}
    if alvos:
        p = alvos[0]
        bloco = "EU" if p in ue else p
        return {"pais": p, "bloco": bloco, "regra": "primeiro_alvo_estrangeiro",
                "motivo": f"Primeiro país estrangeiro declarado: {disponiveis.get(p, p)}."
                          + (" Membro da UE: aplica-se o regime europeu com a lei nacional anotada." if p in ue else ""),
                "pacote_disponivel": bloco in disponiveis}
    if sinais.get("publico_ue") and sinais["publico_ue"].valor:
        return {"pais": "EU", "bloco": "EU", "regra": "sinal_ue",
                "motivo": "Sem país declarado; o código indica público na União Europeia (euro ou idioma da UE).",
                "pacote_disponivel": True}
    if sinais.get("publico_reino_unido") and sinais["publico_reino_unido"].valor:
        return {"pais": "GB", "bloco": "GB", "regra": "sinal_reino_unido",
                "motivo": "Sem país declarado; o código indica público no Reino Unido.", "pacote_disponivel": True}
    return {"pais": "US", "bloco": "US", "regra": "padrao",
            "motivo": "Nenhum país-alvo declarado: EUA por padrão, quase padrão internacional para IA e startups.",
            "pacote_disponivel": True}


# ── jurisdição ──────────────────────────────────────────────────────────────

def _ufs_relevantes(respostas: dict):
    r = respostas or {}
    sede = (r.get("sede_uf") or "").upper().strip() or None
    atuacao = r.get("ufs_atuacao")
    if atuacao is None:
        return sede, None
    atuacao = [u.upper() for u in atuacao]
    if "*" in atuacao:
        return sede, set(UFS)
    return sede, set(atuacao) | ({sede} if sede else set())


def modo_jurisdicao(norma: dict, n2: dict, sinais, respostas: dict, ue: set) -> tuple[str, str]:
    """Retorna (modo, motivo). modo: aplicavel | prontidao | fora | desconhecido."""
    j = norma["jurisdicao"]
    r = respostas or {}
    if j == "BR":
        return "aplicavel", "Projeto brasileiro."
    if j.startswith("BR-"):
        uf = j[3:]
        sede, ufs = _ufs_relevantes(r)
        if ufs is None and sede is None:
            return "desconhecido", f"Informe sede e UFs de atuação para avaliar normas de {uf}."
        if (sede == uf) or (ufs and uf in ufs):
            return "aplicavel", f"Projeto sediado ou atuante em {uf}."
        if ufs is None:
            return "desconhecido", f"Informe as UFs de atuação para saber se {uf} se aplica."
        return "fora", f"{uf} não está entre a sede e as UFs de atuação declaradas."
    alvos = {p.upper() for p in (r.get("paises_alvo") or [])}
    pais = j.split("-", 1)[0]
    alcance = pais in alvos or (pais == "EU" and bool(alvos & ue))
    detectado = (pais == "EU" and sinais.get("publico_ue") and sinais["publico_ue"].valor) or \
                (pais == "GB" and sinais.get("publico_reino_unido") and sinais["publico_reino_unido"].valor)
    if pais == "US" and "-" in j:
        estados = {e.upper() for e in (r.get("us_estados") or [])}
        estado = j.split("-", 1)[1]
        if alcance and ("*" in estados or estado in estados):
            return "aplicavel", f"Usuários declarados em {estado} (EUA)."
        if alcance and not estados:
            return "desconhecido", f"EUA no alcance: informe em us_estados se há usuários em {estado}."
        if norma["nivel"] == "N2" and n2["bloco"] == "US":
            return "prontidao", f"EUA é o N2 do projeto; {estado} entra como prontidão até haver usuários declarados lá."
        return "fora", "Estado americano fora do alcance declarado."
    if alcance:
        return "aplicavel", f"{pais} está entre os países-alvo declarados."
    if detectado:
        return "prontidao", f"O código indica público em {pais}, mas o país não foi declarado: prontidão até constar em paises_alvo."
    if pais in (n2["bloco"], n2["pais"]):
        return "prontidao", f"{pais} é o N2 escolhido: avaliado como prontidão para entrada nesse mercado."
    if norma["nivel"] == "N3" and pais in ESCOPO_GLOBAL:
        return "prontidao", "Referência global: avaliada como prontidão (clientes, investidores e expansão)."
    return "fora", f"{pais} não é o N2 nem está no alcance do projeto."


# ── avaliação ───────────────────────────────────────────────────────────────

def _evidencia(eids: list, varredura: Varredura | None, respostas: dict):
    declaradas = (respostas or {}).get("evidencias", {}) or {}
    docs, mencoes, decl = [], [], []
    for e in eids:
        if declaradas.get(e):
            decl.append({"evidencia": e, "local": str(declaradas[e])})
        if varredura:
            b = varredura.evidencias.get(e, {})
            docs += [{"evidencia": e, "local": l} for l in b.get("documentos", [])]
            mencoes += [{"evidencia": e, "local": l} for l in b.get("mencoes", [])]
    return docs, mencoes, decl


def _perguntas_para(sinais_usados: set, sinais, catalog) -> list[str]:
    perguntas = {p["sinal"]: p["pergunta"] for p in catalog.questionario["sinais_perguntas"]}
    out = []
    for s in sorted(sinais_usados):
        if sinais[s].valor is None:
            out.append(perguntas.get(s, f"Confirme: {catalog.sinais[s]['rotulo']}"))
    return out


def revisar(catalog, varredura: Varredura | None, respostas: dict | None, hoje: date | None = None) -> dict:
    respostas = validar_respostas(catalog, respostas)
    hoje = hoje or date.today()
    sinais = resolver_sinais(catalog, varredura, respostas)
    n2 = escolher_n2(catalog, sinais, respostas)
    ue = set(catalog.regra_n2["membros_ue"])
    achados, radar, fora, oportunidades = [], [], [], []
    pendencias: dict[str, set] = {}

    for norma in catalog.normas:
        if norma["status"] == "revogada":
            continue
        modo, motivo_j = modo_jurisdicao(norma, n2, sinais, respostas, ue)
        base = {
            "norma_id": norma["id"], "norma": norma["nome"], "citacao": norma["citacao"],
            "jurisdicao": norma["jurisdicao"],
            "nivel": "N1" if norma["jurisdicao"].startswith("BR") else ("N2" if modo != "fora" and (
                norma["jurisdicao"].split("-", 1)[0] in (n2["bloco"], n2["pais"])) else norma["nivel"]),
            "status_norma": norma["status"], "vigencia": norma.get("vigencia"),
            "fonte": norma["fonte"], "modo": modo, "motivo_jurisdicao": motivo_j,
            "alerta_competencia": norma.get("alerta_competencia"),
        }
        if norma["status"] in ("em_tramitacao", "suspensa"):
            v, used = avaliar(norma["gatilho"], sinais)
            if modo != "fora" and v is not False:
                radar.append({**base, "relevancia": "provavel" if v else "a_confirmar", "notas": norma.get("notas", "")})
            continue
        if modo == "fora":
            fora.append({**base, "estado": "nao_aplicavel_justificado"})
            continue
        v_norma, used_n = avaliar(norma["gatilho"], sinais)
        if norma.get("relevancia") == "oportunidade":
            if v_norma is not False:
                oportunidades.append({**base, "relevancia": "provavel" if v_norma else "a_confirmar",
                                      "notas": norma.get("notas", ""),
                                      "pontos": [o["texto"] for o in norma["obrigacoes"]]})
            continue
        for ob in norma["obrigacoes"]:
            v_ob, used_o = avaliar(ob.get("gatilho", True), sinais)
            used = used_n | used_o
            if v_norma is False or v_ob is False:
                v = False
            elif v_norma is None or v_ob is None:
                v = None
            else:
                v = True
            docs, mencoes, decl = _evidencia(ob["evidencias"], varredura, respostas)
            confs = [sinais[s].confianca for s in used if sinais[s].valor and sinais[s].confianca]
            conf_gatilho = min(confs, key=lambda c: CONF_ORDEM[c]) if confs else ("alta" if not used else None)
            item = {
                **base, "obrigacao_id": ob["id"], "obrigacao": ob["texto"], "dispositivo": ob.get("dispositivo"),
                "natureza": ob["natureza"], "severidade": ob["severidade"], "evidencias_esperadas": ob["evidencias"],
                "modelo": ob.get("modelo"), "sinais_gatilho": sorted(used),
                "confianca_gatilho": conf_gatilho, "evidencias_localizadas": docs, "mencoes": mencoes,
                "evidencias_declaradas": decl, "lacuna": False,
            }
            if modo == "desconhecido":
                item.update(estado="inconclusivo", motivo=motivo_j, lacuna=None)
                pendencias.setdefault("__jurisdicao__", set()).add(motivo_j)
                achados.append(item)
                continue
            if v is False:
                ausentes = [s for s in used if sinais[s].valor is False]
                origem = {sinais[s].origem for s in ausentes}
                item.update(estado="nao_aplicavel_justificado",
                            motivo="Gatilho ausente: " + ", ".join(catalog.sinais[s]["rotulo"] for s in ausentes)
                                   + (" (não detectado no código; confirme)" if "nao_detectado" in origem else " (declarado)"))
                fora.append(item)
                continue
            if v is None:
                perguntas = _perguntas_para(used, sinais, catalog)
                for p in perguntas:
                    pendencias.setdefault(p, set()).add(norma["id"])
                item.update(estado="inconclusivo", motivo="Faltam respostas: " + " / ".join(perguntas), lacuna=None)
                achados.append(item)
                continue
            # gatilho verdadeiro
            inicio = (norma.get("vigencia") or {}).get("inicio")
            futura = bool(inicio and inicio > hoje.isoformat()) or (norma["status"] == "vigencia_futura" and not inicio)
            if docs or decl:
                item.update(estado="inconclusivo", motivo="Evidência localizada; o conteúdo precisa de revisão profissional.")
            elif ob["natureza"] == "vedacao":
                item.update(estado="inconclusivo", lacuna=True,
                            motivo="Vedação: a falta de documento não prova a prática proibida. Confirmar que o produto não a realiza e registrar a decisão.")
            elif mencoes:
                item.update(estado="inconclusivo", lacuna=True,
                            motivo="Só há menção ou link; o documento não está no escopo examinado (pode estar fora do repositório).")
            else:
                item["lacuna"] = True
                firme = (modo == "aplicavel" and not futura and norma["fonte"]["verificacao"] == "oficial_conferido"
                         and ob["natureza"] == "obrigacao_legal" and conf_gatilho in ("alta", "media")
                         and bool(ob.get("dispositivo")) and not norma.get("alerta_competencia"))
                if firme:
                    item.update(estado="nao_conformidade_evidenciada",
                                motivo="Gatilho presente e nenhuma evidência no escopo examinado. Limitação: o documento pode existir fora do repositório.")
                else:
                    razoes = []
                    if modo == "prontidao":
                        razoes.append("prontidão para jurisdição sem usuários declarados")
                    if futura:
                        razoes.append(f"norma com vigência futura ({(norma.get('vigencia') or {}).get('inicio')})")
                    if norma["fonte"]["verificacao"] != "oficial_conferido":
                        razoes.append("fonte ainda não conferida no texto oficial")
                    if ob["natureza"] != "obrigacao_legal":
                        razoes.append("boa prática ou exigência de mercado, não obrigação legal")
                    if conf_gatilho == "baixa":
                        razoes.append("gatilho detectado com baixa confiança")
                    if not ob.get("dispositivo"):
                        razoes.append("dispositivo não identificado no catálogo")
                    if norma.get("alerta_competencia"):
                        razoes.append("alerta de competência constitucional: " + norma["alerta_competencia"])
                    item.update(estado="inconclusivo", motivo="Lacuna sem evidência; " + "; ".join(razoes) + ".")
            achados.append(item)

    ordem_sev = {s: i for i, s in enumerate(SEVERIDADE)}
    ordem_estado = {"nao_conformidade_evidenciada": 0, "inconclusivo": 1, "nao_aplicavel_justificado": 2, "erro": 3}
    ordem_nivel = {"N1": 0, "N2": 1, "N3": 2}
    achados.sort(key=lambda a: (ordem_nivel[a["nivel"]], ordem_estado[a["estado"]], not a["lacuna"],
                                ordem_sev[a["severidade"]], a["jurisdicao"], a["norma_id"], a["obrigacao_id"]))

    def conta(nivel):
        sel = [a for a in achados if a["nivel"] == nivel]
        return {
            "nao_conformidade_evidenciada": sum(a["estado"] == "nao_conformidade_evidenciada" for a in sel),
            "lacunas_inconclusivas": sum(a["estado"] == "inconclusivo" and a["lacuna"] is True for a in sel),
            "evidencia_a_revisar": sum(a["estado"] == "inconclusivo" and a["lacuna"] is False for a in sel),
            "dependem_de_resposta": sum(a["lacuna"] is None for a in sel),
            "por_severidade": {s: sum(a["severidade"] == s and a["lacuna"] is not False for a in sel) for s in SEVERIDADE},
        }

    modelos = sorted({a["modelo"] for a in achados if a.get("modelo") and a["lacuna"]})
    return {
        "marca": "MINUTA — REVISÃO PROFISSIONAL OBRIGATÓRIA",
        "gerado_em": hoje.isoformat(),
        "catalogo": {"versao": catalog.versao, "normas": len(catalog.normas), "arquivos": catalog.arquivos_normas},
        "escopo": varredura.to_dict() if varredura else None,
        "respostas": {k: v for k, v in respostas.items() if k != "evidencias"},
        "sinais": {k: vars(v) for k, v in sinais.items()},
        "n2": n2,
        "resumo": {"N1": conta("N1"), "N2": conta("N2"), "N3": conta("N3"), "radar": len(radar), "oportunidades": len(oportunidades)},
        "perguntas_pendentes": sorted(p for p in pendencias if p != "__jurisdicao__")
                               + sorted(pendencias.get("__jurisdicao__", [])),
        "achados": achados,
        "radar_regulatorio": radar,
        "oportunidades": oportunidades,
        "nao_aplicaveis": fora,
        "modelos_sugeridos": modelos,
        "limitacoes": [
            "Detecção por padrões é indício: ausência de detecção não prova ausência da característica.",
            "Localizar um documento não prova conformidade; o conteúdo exige revisão profissional.",
            "Documentos fora do repositório (site, contrato assinado, cartório) precisam ser declarados em respostas.evidencias.",
            "Normas com fonte não conferida no texto oficial, sem dispositivo identificado ou com alerta de competência nunca geram não conformidade, só lacuna inconclusiva.",
            "Vedações (o que o produto não pode fazer) não se provam por documento: ficam inconclusivas até confirmação.",
            "Sinal detectado só no código (moeda, idioma) não torna um país aplicável: declare paises_alvo.",
            "Projeto de lei não é lei: aparece apenas no radar regulatório.",
            "O catálogo tem data de corte; leis mudam. Conferir vigência na data dos fatos.",
        ],
    }
