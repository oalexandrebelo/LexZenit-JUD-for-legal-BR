"""Cálculos exatos e sinais de triagem; nenhuma conclusão jurídica por palavras-chave."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from .models import (
    BDIRequest, BDIResult, Interval, ObjectClass, PriceRequest, PriceSignals,
    Regime, SLARequest, SLAResult,
)


D = Decimal
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def screen_engineering_price(request: PriceRequest) -> PriceSignals:
    """Testa art. 59, §§ 4º/5º somente no escopo expressamente informado.

    Não decide a classificação do objeto, a lei aplicável, a exequibilidade
    efetiva nem a incidência final da garantia. Há leituras distintas da base
    de cálculo do § 5º: a diferença integral e o exemplo do manual do TCU
    baseado em 85% do orçamento. Ambos os cenários são expostos; nenhum
    valor exigível é selecionado automaticamente quando o limiar incide.
    """
    with localcontext() as context:
        context.prec = 40
        context.rounding = ROUND_HALF_EVEN
        ratio = request.submitted_total / request.estimated_total
        applicable = (request.regime == Regime.LAW_14133
                      and request.object_class == ObjectClass.ENGINEERING)
        if not applicable:
            return PriceSignals(
                applicable=False, below_75=None, below_85=None,
                comparison_ratio=ratio, additional_guarantee=None,
                guarantee_if_full_budget=None, guarantee_if_85pct_budget=None,
                guarantee_resolution="nao_aplicavel",
                action="regra_nao_aplicada",
                rationale="Objeto/regime não habilita este cálculo de engenharia; falta regra específica.",
            )
        below_75 = request.submitted_total < request.estimated_total * D("0.75")
        below_85 = request.submitted_total < request.estimated_total * D("0.85")
        full = request.estimated_total - request.submitted_total if below_85 else D("0.00")
        threshold = request.estimated_total * D("0.85") - request.submitted_total if below_85 else D("0.00")
        # Os valores são cenários financeiros, não uma escolha jurídica do código.
        full = full.quantize(D("0.01"))
        threshold = threshold.quantize(D("0.01"))
        return PriceSignals(
            applicable=True, below_75=below_75, below_85=below_85,
            comparison_ratio=ratio, additional_guarantee=None if below_85 else D("0.00"),
            guarantee_if_full_budget=full, guarantee_if_85pct_budget=threshold,
            guarantee_resolution="interpretacao_pendente" if below_85 else "fora_do_limiar",
            action="diligencia_e_revisao" if below_75 else "revisao_sem_gatilho_75",
            rationale=("Limiar aritmético atingido; encaminhar à diligência e revisão do caso."
                       if below_75 else "Limiar de 75% não atingido; isso não comprova exequibilidade."),
        )


def calculate_bdi(request: BDIRequest) -> BDIResult:
    """Taxas em fração: 0.05 = 5%. Não determina alíquotas ou tetos legais."""
    with localcontext() as context:
        context.prec = 40
        context.rounding = ROUND_HALF_EVEN
        numerator = ((1 + request.administration + request.risk + request.insurance + request.guarantee)
                     * (1 + request.finance) * (1 + request.profit))
        fraction = numerator / (1 - request.taxes_on_sales) - 1
        return BDIResult(fraction=fraction, percentage=fraction * 100)


def _micros(value: datetime) -> int:
    delta = value.astimezone(timezone.utc) - _EPOCH
    return ((delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds)


def _union(intervals: tuple[Interval, ...], start: int, end: int) -> list[tuple[int, int]]:
    clipped = sorted((max(start, _micros(item.start)), min(end, _micros(item.end)))
                     for item in intervals)
    merged: list[tuple[int, int]] = []
    for left, right in clipped:
        if left >= right:
            continue
        if merged and left <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], right))
        else:
            merged.append((left, right))
    return merged


def _length(intervals: list[tuple[int, int]]) -> int:
    return sum(right - left for left, right in intervals)


def _intersection_length(a: list[tuple[int, int]], b: list[tuple[int, int]]) -> int:
    i = j = total = 0
    while i < len(a) and j < len(b):
        total += max(0, min(a[i][1], b[j][1]) - max(a[i][0], b[j][0]))
        if a[i][1] <= b[j][1]:
            i += 1
        else:
            j += 1
    return total


def calculate_sla(request: SLARequest) -> SLAResult:
    """Disponibilidade por janela, intervalos semiabertos [início,fim).

    Consolida sobreposições, recorta à janela e remove apenas exclusões
    explicitamente fornecidas. Não presume exclusão por manutenção/vandalismo.
    """
    start, end = _micros(request.window.start), _micros(request.window.end)
    outages = _union(request.outages, start, end)
    exclusions = _union(request.exclusions, start, end)
    eligible_us = end - start - _length(exclusions)
    if eligible_us <= 0:
        raise ValueError("Não há janela elegível: disponibilidade é indefinida.")
    unavailable_us = _length(outages) - _intersection_length(outages, exclusions)
    with localcontext() as context:
        context.prec = 40
        context.rounding = ROUND_HALF_EVEN
        eligible = D(eligible_us) / 1_000_000
        unavailable = D(unavailable_us) / 1_000_000
        fraction_exact = 1 - D(unavailable_us) / D(eligible_us)
        fraction_report = fraction_exact.quantize(D("0.000000000001"))
        return SLAResult(
            eligible_seconds=eligible, unavailable_seconds=unavailable,
            available_fraction=fraction_report,
            downtime_budget_seconds=eligible * (1 - request.target),
            # A decisão usa o valor exato; o arredondamento só afeta exibição.
            target_met=fraction_exact >= request.target,
        )
