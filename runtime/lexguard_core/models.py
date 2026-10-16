"""Contratos internos estritos. Entradas não representam fatos já comprovados."""
from __future__ import annotations

from datetime import date, timezone
from decimal import Decimal
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", validate_default=True,
        allow_inf_nan=False, hide_input_in_errors=True,
    )


Money = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=2)]
PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=2)]
Rate = Annotated[Decimal, Field(ge=0, le=1, max_digits=18, decimal_places=12)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Identifier = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$")]


class Regime(str, Enum):
    LAW_14133 = "lei_14133"
    STATE_OWNED = "lei_13303"
    LEGACY = "legado"
    UNRESOLVED = "nao_resolvido"


class ObjectClass(str, Enum):
    ENGINEERING = "obras_servicos_engenharia"
    GOODS_SERVICES = "bens_servicos_gerais"
    MIXED = "misto_nao_segmentado"
    UNRESOLVED = "nao_resolvido"


class PriceRequest(StrictModel):
    regime: Regime
    object_class: ObjectClass
    estimated_total: PositiveMoney
    submitted_total: Money


class PriceSignals(StrictModel):
    applicable: bool
    below_75: bool | None
    below_85: bool | None
    comparison_ratio: Decimal
    additional_guarantee: Money | None
    guarantee_if_full_budget: Money | None
    guarantee_if_85pct_budget: Money | None
    guarantee_resolution: Literal["interpretacao_pendente", "fora_do_limiar", "nao_aplicavel"]
    action: Literal["diligencia_e_revisao", "revisao_sem_gatilho_75", "regra_nao_aplicada"]
    rationale: str
    formula_version: Literal["br-14133-art59-screen-v2-scenarios"] = "br-14133-art59-screen-v2-scenarios"


class BDIRequest(StrictModel):
    administration: Rate
    risk: Rate
    insurance: Rate
    guarantee: Rate
    finance: Rate
    profit: Rate
    taxes_on_sales: Rate

    @model_validator(mode="after")
    def denominator_must_be_positive(self) -> BDIRequest:
        if self.taxes_on_sales >= 1:
            raise ValueError("A alíquota agregada sobre vendas deve ser inferior a 1.")
        return self


class BDIResult(StrictModel):
    fraction: Decimal
    percentage: Decimal
    formula_version: Literal["bdi-multiplicative-v1"] = "bdi-multiplicative-v1"
    legal_assessment: Literal["nao_realizada"] = "nao_realizada"


class Interval(StrictModel):
    start: AwareDatetime
    end: AwareDatetime

    @model_validator(mode="after")
    def ordered(self) -> Interval:
        if self.start.astimezone(timezone.utc) >= self.end.astimezone(timezone.utc):
            raise ValueError("Intervalo deve ter duração positiva.")
        return self


class SLARequest(StrictModel):
    window: Interval
    target: Rate
    outages: tuple[Interval, ...] = ()
    exclusions: tuple[Interval, ...] = ()


class SLAResult(StrictModel):
    eligible_seconds: Decimal
    unavailable_seconds: Decimal
    available_fraction: Rate
    downtime_budget_seconds: Decimal
    target_met: bool
    glosa: Literal["nao_calculada_sem_regra_contratual"] = "nao_calculada_sem_regra_contratual"


class CheckState(str, Enum):
    SATISFIED = "satisfeito_no_escopo"
    NONCONFORMITY = "nao_conformidade_evidenciada"
    INCONCLUSIVE = "inconclusivo"
    NOT_APPLICABLE = "nao_aplicavel"
    ERROR = "erro"


class VerificationStatus(str, Enum):
    DOCUMENTED = "documentado"
    INCONCLUSIVE = "inconclusivo"
    STALE = "desatualizado"
    UNAVAILABLE = "indisponivel"


class EvidenceRef(StrictModel):
    """Referência atribuída pelo serviço de evidências, nunca pelo LLM público.

    A validação estrutural não autentica origem, atualidade ou veracidade.
    O núcleo não faz resolução automática de precedentes nem consultas externas.
    """
    evidence_id: Identifier
    sha256: Digest
    locator: Annotated[str, Field(min_length=1, max_length=512)]


class Finding(StrictModel):
    code: Identifier
    description: Annotated[str, Field(min_length=1, max_length=8192)]
    severity: Annotated[int, Field(ge=1, le=5)]
    evidence: tuple[EvidenceRef, ...] = Field(min_length=1)


class CheckResult(StrictModel):
    skill_id: Identifier
    state: CheckState
    justification: Annotated[str, Field(min_length=1, max_length=8192)]
    findings: tuple[Finding, ...] = ()
    evidence: tuple[EvidenceRef, ...] = ()

    @model_validator(mode="after")
    def consistency(self) -> CheckResult:
        if self.state == CheckState.NONCONFORMITY and not self.findings:
            raise ValueError("Não conformidade exige achado com evidência localizada.")
        if self.state != CheckState.NONCONFORMITY and self.findings:
            raise ValueError("Achados conclusivos exigem estado de não conformidade.")
        if self.state in (CheckState.SATISFIED, CheckState.NOT_APPLICABLE) and not self.evidence:
            raise ValueError("Satisfeito/não aplicável exige referência de evidência.")
        return self


class ReleaseContext(StrictModel):
    execution_id: UUID
    tenant_id: UUID
    document_sha256: Digest
    assessment_date: date
    required_skills: tuple[Identifier, ...] = Field(min_length=1)
    document_coverage: Rate
    legal_verification: VerificationStatus
    audit_persisted: bool

    @model_validator(mode="after")
    def unique_skills(self) -> ReleaseContext:
        if len(set(self.required_skills)) != len(self.required_skills):
            raise ValueError("Skills obrigatórias duplicadas.")
        return self


class ReleaseDecision(StrictModel):
    execution_id: UUID
    state: Literal["bloqueado", "inconclusivo", "revisao_obrigatoria", "pronto_para_revisao_humana"]
    can_publish_automatically: Literal[False] = False
    blockers: tuple[str, ...]
    maximum_severity: Annotated[int, Field(ge=0, le=5)]
    missing_skills: tuple[Identifier, ...]
