"""Gate conservador sem média de notas e sem autorização de protocolo/publicação."""
from __future__ import annotations

from .models import CheckResult, CheckState, ReleaseContext, ReleaseDecision, VerificationStatus


def assess_release(context: ReleaseContext, results: tuple[CheckResult, ...]) -> ReleaseDecision:
    ids = tuple(result.skill_id for result in results)
    if len(set(ids)) != len(ids):
        raise ValueError("Resultado duplicado: agregação recusada.")
    required = set(context.required_skills)
    if set(ids) - required:
        raise ValueError("Resultados de skills não previstas no plano de execução.")
    missing = tuple(skill for skill in context.required_skills if skill not in ids)
    blockers: list[str] = []
    maximum = max((finding.severity for result in results for finding in result.findings), default=0)
    if not context.audit_persisted:
        blockers.append("auditoria_nao_persistida")
    if maximum == 5:
        blockers.append("achado_critico_evidenciado")
    hard_block = bool(blockers)
    if missing:
        blockers.append("skills_obrigatorias_ausentes")
    if context.document_coverage < 1:
        blockers.append("cobertura_documental_incompleta")
    if context.legal_verification != VerificationStatus.DOCUMENTED:
        blockers.append("validacao_normativa_insuficiente")
    if any(result.state in (CheckState.ERROR, CheckState.INCONCLUSIVE) for result in results):
        blockers.append("verificacao_obrigatoria_inconclusiva")
    if hard_block:
        state = "bloqueado"
    elif blockers:
        state = "inconclusivo"
    elif any(result.state == CheckState.NONCONFORMITY for result in results):
        state = "revisao_obrigatoria"
    else:
        state = "pronto_para_revisao_humana"
    return ReleaseDecision(execution_id=context.execution_id, state=state,
                           blockers=tuple(blockers), maximum_severity=maximum,
                           missing_skills=missing)
