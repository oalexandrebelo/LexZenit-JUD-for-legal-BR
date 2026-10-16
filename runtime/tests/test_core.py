"""Testes locais de contratos, cálculos, gate e cadeia; não testes de IA jurídica."""
from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN, localcontext
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from lexguard_core.audit import AuditEvent, AuditStore
from lexguard_core.calculations import calculate_bdi, calculate_sla, screen_engineering_price
from lexguard_core.dag import DAGRunner, Node
from lexguard_core.models import (
    BDIRequest, CheckResult, CheckState, EvidenceRef, Finding, Interval,
    ObjectClass, PriceRequest, Regime, ReleaseContext, SLARequest, VerificationStatus,
)
from lexguard_core.verdict import assess_release

D = Decimal
NOW = datetime(2026, 10, 12, tzinfo=timezone.utc)


def evidence() -> EvidenceRef:
    return EvidenceRef(evidence_id="test-evidence", sha256=hashlib.sha256(b"test input").hexdigest(),
                       locator="Dado sintético de teste; não é fonte jurídica.")


def result(name: str, state: CheckState = CheckState.SATISFIED, severity: int = 1) -> CheckResult:
    findings = ()
    if state == CheckState.NONCONFORMITY:
        findings = (Finding(code="test-finding", description="Achado sintético de teste.",
                            severity=severity, evidence=(evidence(),)),)
    return CheckResult(skill_id=name, state=state, justification="Verificação de contrato de software.",
                       evidence=(evidence(),), findings=findings)


def context(required: tuple[str, ...] = ("a",), **changes: object) -> ReleaseContext:
    data = dict(execution_id=uuid4(), tenant_id=uuid4(), document_sha256="a" * 64,
                assessment_date=date(2026, 10, 12), required_skills=required,
                document_coverage=D("1"), legal_verification=VerificationStatus.DOCUMENTED,
                audit_persisted=True)
    data.update(changes)
    return ReleaseContext(**data)


class PriceTests(unittest.TestCase):
    def calculate(self, submitted: str, **changes: object):
        data = dict(regime=Regime.LAW_14133, object_class=ObjectClass.ENGINEERING,
                    estimated_total=D("1000000.00"), submitted_total=D(submitted))
        data.update(changes)
        return screen_engineering_price(PriceRequest(**data))

    def test_below_75_requires_diligence(self):
        answer = self.calculate("749999.99")
        self.assertTrue(answer.below_75)
        self.assertEqual(answer.action, "diligencia_e_revisao")

    def test_equal_75_is_not_below(self):
        self.assertFalse(self.calculate("750000.00").below_75)

    def test_guarantee_scenarios_do_not_hide_interpretation(self):
        answer = self.calculate("800000.00")
        self.assertEqual(answer.guarantee_if_full_budget, D("200000.00"))
        self.assertEqual(answer.guarantee_if_85pct_budget, D("50000.00"))
        self.assertIsNone(answer.additional_guarantee)
        self.assertEqual(answer.guarantee_resolution, "interpretacao_pendente")

    def test_guarantee_cents_rounding_is_explicit(self):
        answer = self.calculate("0.01", estimated_total=D("0.03"))
        self.assertEqual(answer.guarantee_if_85pct_budget, D("0.02"))
        self.assertTrue(answer.below_85)

    def test_guarantee_outside_engineering_has_no_scenario(self):
        answer = self.calculate("10.00", object_class=ObjectClass.GOODS_SERVICES)
        self.assertIsNone(answer.guarantee_if_full_budget)
        self.assertIsNone(answer.guarantee_if_85pct_budget)

    def test_equal_85_no_additional_guarantee(self):
        self.assertEqual(self.calculate("850000.00").additional_guarantee, D("0"))

    def test_goods_not_subject_to_engineering_rule(self):
        answer = self.calculate("100000.00", object_class=ObjectClass.GOODS_SERVICES)
        self.assertFalse(answer.applicable)
        self.assertIsNone(answer.below_75)

    def test_mixed_object_not_automatically_engineering(self):
        self.assertFalse(self.calculate("100000.00", object_class=ObjectClass.MIXED).applicable)

    def test_state_owned_regime_not_subject_to_14133(self):
        self.assertFalse(self.calculate("100000.00", regime=Regime.STATE_OWNED).applicable)

    def test_unresolved_regime_not_applied(self):
        self.assertFalse(self.calculate("100000.00", regime=Regime.UNRESOLVED).applicable)

    def test_zero_estimate_rejected(self):
        with self.assertRaises(ValidationError):
            self.calculate("100.00", estimated_total=D("0"))

    def test_float_money_rejected(self):
        with self.assertRaises(ValidationError):
            self.calculate("100.00", estimated_total=100.0)

    def test_nonfinite_money_rejected(self):
        for number in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(number=number), self.assertRaises(ValidationError):
                self.calculate("100.00", estimated_total=D(number))

    def test_negative_price_rejected(self):
        with self.assertRaises(ValidationError):
            self.calculate("-1.00")

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValidationError):
            self.calculate("100.00", unit_prices=(D("10"),))

    def test_more_than_two_money_decimals_rejected(self):
        with self.assertRaises(ValidationError):
            self.calculate("100.001")

    def test_json_money_strings_supported(self):
        request = PriceRequest.model_validate_json(json.dumps(dict(
            regime="lei_14133", object_class="obras_servicos_engenharia",
            estimated_total="1000000.00", submitted_total="740000.00")))
        self.assertTrue(screen_engineering_price(request).below_75)


class BDITests(unittest.TestCase):
    def request(self, **changes: Decimal) -> BDIRequest:
        data = dict(administration=D("0.04"), risk=D("0.01"), insurance=D("0.005"),
                    guarantee=D("0.005"), finance=D("0.01"), profit=D("0.08"),
                    taxes_on_sales=D("0.05"))
        data.update(changes)
        return BDIRequest(**data)

    def test_formula(self):
        answer = calculate_bdi(self.request())
        self.assertAlmostEqual(answer.percentage, D("21.71031578947368421052631578947368421050"), places=30)
        self.assertEqual(answer.legal_assessment, "nao_realizada")

    def test_zero_denominator_rejected(self):
        with self.assertRaises(ValidationError):
            self.request(taxes_on_sales=D("1"))

    def test_percent_must_be_fraction(self):
        with self.assertRaises(ValidationError):
            self.request(taxes_on_sales=D("5"))

    def test_determinism_not_changed_by_global_rounding(self):
        expected = calculate_bdi(self.request())
        with localcontext() as ctx:
            ctx.rounding = ROUND_DOWN
            actual = calculate_bdi(self.request())
        self.assertEqual(expected, actual)


class SLATests(unittest.TestCase):
    def interval(self, start: int, end: int) -> Interval:
        return Interval(start=NOW + timedelta(seconds=start), end=NOW + timedelta(seconds=end))

    def calculate(self, outages=(), exclusions=(), seconds=1000, target="0.99"):
        return calculate_sla(SLARequest(window=self.interval(0, seconds), target=D(target),
                                        outages=tuple(outages), exclusions=tuple(exclusions)))

    def test_no_outages(self):
        self.assertEqual(self.calculate().available_fraction, D("1"))

    def test_overlapping_outages_counted_once(self):
        answer = self.calculate((self.interval(10, 30), self.interval(20, 40)))
        self.assertEqual(answer.unavailable_seconds, D("30"))

    def test_duplicate_outages_counted_once(self):
        item = self.interval(10, 30)
        self.assertEqual(self.calculate((item, item)).unavailable_seconds, D("20"))

    def test_intersection_with_exclusions(self):
        answer = self.calculate((self.interval(10, 40),), (self.interval(20, 30),))
        self.assertEqual(answer.unavailable_seconds, D("20"))
        self.assertEqual(answer.eligible_seconds, D("990"))

    def test_intervals_are_clipped(self):
        answer = self.calculate((self.interval(-10, 10), self.interval(990, 1100)))
        self.assertEqual(answer.unavailable_seconds, D("20"))

    def test_outside_window_ignored(self):
        self.assertEqual(self.calculate((self.interval(-100, -10),)).unavailable_seconds, D("0"))

    def test_entire_window_excluded_is_undefined(self):
        with self.assertRaises(ValueError):
            self.calculate(exclusions=(self.interval(0, 1000),))

    def test_reversed_interval_rejected(self):
        with self.assertRaises(ValidationError):
            self.interval(10, 1)

    def test_timezone_required(self):
        with self.assertRaises(ValidationError):
            Interval(start=datetime(2026, 1, 1), end=datetime(2026, 1, 2))

    def test_30_days_99_5_budget_is_216_minutes(self):
        answer = self.calculate(seconds=30 * 86400, target="0.995")
        self.assertEqual(answer.downtime_budget_seconds / 60, D("216"))

    def test_dst_folds_use_absolute_time(self):
        zone = ZoneInfo("America/New_York")
        window = Interval(start=datetime(2025, 11, 2, 1, 30, tzinfo=zone, fold=0),
                          end=datetime(2025, 11, 2, 1, 15, tzinfo=zone, fold=1))
        answer = calculate_sla(SLARequest(window=window, target=D("0.99")))
        self.assertEqual(answer.eligible_seconds, D("2700"))

    def test_glosa_not_invented(self):
        self.assertEqual(self.calculate().glosa, "nao_calculada_sem_regra_contratual")


class VerdictTests(unittest.TestCase):
    def test_no_automatic_publication(self):
        answer = assess_release(context(), (result("a"),))
        self.assertEqual(answer.state, "pronto_para_revisao_humana")
        self.assertFalse(answer.can_publish_automatically)

    def test_unknown_required_skill_cannot_pass(self):
        answer = assess_release(context(("not-implemented",)), ())
        self.assertEqual(answer.state, "inconclusivo")
        self.assertEqual(answer.missing_skills, ("not-implemented",))

    def test_stale_law_blocks_ready_status(self):
        answer = assess_release(context(legal_verification=VerificationStatus.STALE), (result("a"),))
        self.assertEqual(answer.state, "inconclusivo")

    def test_partial_coverage_blocks_ready_status(self):
        self.assertEqual(assess_release(context(document_coverage=D("0.99")), (result("a"),)).state,
                         "inconclusivo")

    def test_no_audit_hard_blocks(self):
        self.assertEqual(assess_release(context(audit_persisted=False), (result("a"),)).state, "bloqueado")

    def test_one_critical_finding_not_diluted_by_100_good_results(self):
        names = tuple(f"a-{index}" for index in range(100)) + ("critical",)
        outputs = tuple(result(name) for name in names[:-1]) + (result("critical", CheckState.NONCONFORMITY, 5),)
        self.assertEqual(assess_release(context(names), outputs).state, "bloqueado")

    def test_error_never_passes(self):
        self.assertEqual(assess_release(context(), (result("a", CheckState.ERROR),)).state, "inconclusivo")

    def test_noncritical_nonconformity_requires_revision(self):
        self.assertEqual(assess_release(context(), (result("a", CheckState.NONCONFORMITY, 2),)).state,
                         "revisao_obrigatoria")

    def test_duplicate_outputs_rejected(self):
        with self.assertRaises(ValueError):
            assess_release(context(), (result("a"), result("a")))

    def test_unplanned_output_rejected(self):
        with self.assertRaises(ValueError):
            assess_release(context(), (result("b"),))

    def test_duplicate_required_rejected(self):
        with self.assertRaises(ValidationError):
            context(("a", "a"))

    def test_nonconformity_without_evidence_rejected(self):
        with self.assertRaises(ValidationError):
            CheckResult(skill_id="a", state=CheckState.NONCONFORMITY, justification="Teste.")

    def test_satisfied_without_evidence_rejected(self):
        with self.assertRaises(ValidationError):
            CheckResult(skill_id="a", state=CheckState.SATISFIED, justification="Teste.")

    def test_nonapplicability_requires_evidence(self):
        with self.assertRaises(ValidationError):
            CheckResult(skill_id="a", state=CheckState.NOT_APPLICABLE, justification="Teste.")

    def test_uuid_validated(self):
        with self.assertRaises(ValidationError):
            context(execution_id="exec-lexguard-2026-0994")

    def test_boolean_severity_rejected(self):
        with self.assertRaises(ValidationError):
            Finding(code="a", description="Teste.", severity=True, evidence=(evidence(),))


class DAGTests(unittest.IsolatedAsyncioTestCase):
    async def test_dependencies_and_bounded_concurrency(self):
        active, maximum = 0, 0
        completed = set()
        async def compute(name, dependencies):
            nonlocal active, maximum
            self.assertTrue(set(dependencies) <= completed)
            active += 1
            maximum = max(maximum, active)
            # Agendamento cooperativo de teste; não representa inferência.
            await asyncio.sleep(0)
            active -= 1
            completed.add(name)
            return result(name)
        def make(name, deps):
            async def run(previous):
                return await compute(name, previous)
            return Node(name, deps, 1.0, run)
        runner = DAGRunner((make("a", ()), make("b", ()), make("c", ("a", "b"))), concurrency=2)
        outputs = await runner.execute()
        self.assertEqual(len(outputs), 3)
        self.assertLessEqual(maximum, 2)
        self.assertEqual(completed, {"a", "b", "c"})

    async def test_cycle_rejected(self):
        async def run(previous):
            return result("a")
        with self.assertRaises(ValueError):
            DAGRunner((Node("a", ("b",), 1.0, run), Node("b", ("a",), 1.0, run)))

    async def test_unknown_dependency_rejected(self):
        async def run(previous):
            return result("a")
        with self.assertRaises(ValueError):
            DAGRunner((Node("a", ("unknown",), 1.0, run),))

    async def test_empty_graph_rejected(self):
        with self.assertRaises(ValueError):
            DAGRunner(())

    async def test_node_failure_propagates_as_inconclusive(self):
        ran_dependent = False
        async def fail(previous):
            raise RuntimeError("CPF_SENSIVEL_NAO_DEVE_SAIR")
        async def dependent(previous):
            nonlocal ran_dependent
            ran_dependent = True
            return result("b")
        outputs = await DAGRunner((Node("a", (), 1.0, fail), Node("b", ("a",), 1.0, dependent))).execute()
        self.assertEqual(outputs[0].state, CheckState.ERROR)
        self.assertEqual(outputs[1].state, CheckState.INCONCLUSIVE)
        self.assertFalse(ran_dependent)
        self.assertNotIn("CPF_SENSIVEL", outputs[0].justification)

    async def test_node_timeout(self):
        async def wait_forever(previous):
            await asyncio.Event().wait()
            return result("a")
        outputs = await DAGRunner((Node("a", (), 0.01, wait_forever),)).execute()
        self.assertEqual(outputs[0].state, CheckState.ERROR)

    async def test_pipeline_deadline(self):
        cancelled = asyncio.Event()
        async def wait_forever(previous):
            try:
                await asyncio.Event().wait()
                return result("a")
            finally:
                cancelled.set()
        outputs = await DAGRunner((Node("a", (), 60.0, wait_forever),)).execute(total_timeout_seconds=0.01)
        self.assertEqual(outputs[0].state, CheckState.ERROR)
        self.assertTrue(cancelled.is_set())

    async def test_wrong_node_result_is_error(self):
        async def wrong(previous):
            return result("b")
        outputs = await DAGRunner((Node("a", (), 1.0, wrong),)).execute()
        self.assertEqual(outputs[0].state, CheckState.ERROR)

    async def test_invalid_node_name_rejected(self):
        async def run(previous):
            return result("a")
        with self.assertRaises(ValueError):
            DAGRunner((Node("not a valid id", (), 1.0, run),))


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "audit.db"
        self.store = AuditStore(self.path)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def event(self, number=1, **changes):
        data = dict(event_id=f"event-{number}", tenant_id="tenant-1", execution_id="execution-1",
                    occurred_at=NOW, event_type="calculation", payload_sha256="a" * 64)
        data.update(changes)
        return AuditEvent(**data)

    def test_append_and_verify(self):
        anchor = self.store.append(self.event())
        self.assertTrue(self.store.verify(expected_anchor=anchor))

    def test_idempotent_event(self):
        first = self.store.append(self.event())
        self.assertEqual(first, self.store.append(self.event()))

    def test_same_id_different_payload_rejected(self):
        self.store.append(self.event())
        with self.assertRaises(ValueError):
            self.store.append(self.event(payload_sha256="b" * 64))
        self.assertTrue(self.store.verify())

    def test_body_tampering_detected(self):
        anchor = self.store.append(self.event())
        with sqlite3.connect(self.path) as connection:
            connection.execute("UPDATE events SET body = ?", ('{}',))
        self.assertFalse(self.store.verify(expected_anchor=anchor))

    def test_tail_deletion_only_detected_with_external_anchor(self):
        self.store.append(self.event())
        anchor = self.store.append(self.event(2))
        with sqlite3.connect(self.path) as connection:
            connection.execute("DELETE FROM events WHERE sequence = 2")
        self.assertTrue(self.store.verify())
        self.assertFalse(self.store.verify(expected_anchor=anchor))

    def test_reopen_persists(self):
        anchor = self.store.append(self.event())
        self.store.close()
        self.store = AuditStore(self.path)
        self.assertTrue(self.store.verify(expected_anchor=anchor))

    def test_second_connection_appends(self):
        self.store.append(self.event())
        second = AuditStore(self.path)
        try:
            anchor = second.append(self.event(2))
        finally:
            second.close()
        self.assertTrue(self.store.verify(expected_anchor=anchor))


if __name__ == "__main__":
    unittest.main()
