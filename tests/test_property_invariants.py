"""Property-based qualification for existing ForgeMath invariants.

These tests expand input and lifecycle coverage without defining new lanes or
changing canonical formulas. Golden vectors remain the exact semantic pins;
the properties below verify bounds, monotonicity, stable serialization, and
append-only supersession behavior around those governed formulas.
"""

from decimal import Decimal
from itertools import pairwise
from types import SimpleNamespace

import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule, run_state_machine_as_test
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.enums import (
    CompatibilityResolutionState,
    RecomputationAction,
    ReplayState,
    ResultStatus,
    StaleState,
)
from app.models.evaluation import LaneEvaluation
from app.services import evaluation_service, lifecycle_service, registry_service
from app.services.execution_service import (
    ONE,
    ZERO,
    _canonical_output_decimal,
    _clamp_unit,
    _decimal_to_str,
    _derive_exposure_factor,
    _derive_recurrence_pressure,
    _derive_verification_burden,
)
from tests.test_phase2_api import _create_input_bundle, _evaluation_create, _seed_phase1_bindings


FULL_RANGE_THRESHOLDS = SimpleNamespace(
    threshold_set_id="property-thresholds",
    version=1,
    payload={
        "bands": [
            {
                "label": "bounded",
                "min_inclusive": "0",
                "max_inclusive": "1",
            }
        ]
    },
)

VERIFICATION_PARAMETERS = SimpleNamespace(
    parameter_set_id="property-verification-parameters",
    version=1,
    payload={
        "weights": {
            "w_I": "0.15",
            "w_V": "0.25",
            "w_R": "0.25",
            "w_X": "0.10",
            "w_D": "0.10",
            "w_U": "0.15",
        },
        "caps": {
            "I_cap": "60",
            "V_cap": "80",
            "R_cap": "40",
            "X_cap": "4",
            "D_cap": "60",
        },
    },
)

RECURRENCE_PARAMETERS = SimpleNamespace(
    parameter_set_id="property-recurrence-parameters",
    version=1,
    payload={
        "weights": {
            "w30": "0.25",
            "w90": "0.20",
            "wsame": "0.20",
            "wcross": "0.20",
            "wpost": "0.15",
        },
        "saturation": {
            "k30": "0.15",
            "k90": "0.08",
            "ksame": "0.20",
            "kcross": "0.25",
            "kpost": "0.30",
        },
    },
)

EXPOSURE_PARAMETERS = SimpleNamespace(
    parameter_set_id="property-exposure-parameters",
    version=1,
    payload={
        "coefficients": {
            "alpha_pub": "0.35",
            "alpha_op": "0.15",
            "alpha_persist": "0.20",
            "alpha_approve": "0.10",
            "alpha_cross": "0.15",
            "alpha_boundary": "0.05",
        }
    },
)

FINITE_CANONICAL_DECIMALS = st.decimals(
    min_value=Decimal("-1000000"),
    max_value=Decimal("1000000"),
    places=12,
    allow_nan=False,
    allow_infinity=False,
)


@given(FINITE_CANONICAL_DECIMALS)
@settings(max_examples=100)
def test_canonical_decimal_text_round_trips_without_exponents(value: Decimal) -> None:
    rendered = _decimal_to_str(value)

    assert "e" not in rendered.lower()
    assert Decimal(rendered) == value
    assert _decimal_to_str(Decimal(rendered)) == rendered


@given(
    implementation_minutes=st.integers(min_value=0, max_value=10_000),
    verification_minutes=st.integers(min_value=0, max_value=10_000),
    rework_minutes=st.integers(min_value=0, max_value=10_000),
    interruption_count=st.integers(min_value=0, max_value=10_000),
    downstream_fix_minutes=st.integers(min_value=0, max_value=10_000),
    uncertainty_band=st.sampled_from(("low", "moderate", "elevated", "severe")),
)
@settings(max_examples=75)
def test_verification_burden_remains_bounded_and_repeatable(
    implementation_minutes: int,
    verification_minutes: int,
    rework_minutes: int,
    interruption_count: int,
    downstream_fix_minutes: int,
    uncertainty_band: str,
) -> None:
    inputs = {
        "implementation_minutes": implementation_minutes,
        "verification_minutes": verification_minutes,
        "rework_minutes": rework_minutes,
        "interruption_count": interruption_count,
        "downstream_fix_minutes": downstream_fix_minutes,
        "uncertainty_band": uncertainty_band,
    }

    artifacts = _derive_verification_burden(
        VERIFICATION_PARAMETERS,
        FULL_RANGE_THRESHOLDS,
        inputs,
    )
    repeated = _derive_verification_burden(
        VERIFICATION_PARAMETERS,
        FULL_RANGE_THRESHOLDS,
        inputs,
    )

    assert artifacts == repeated
    assert ZERO <= artifacts.raw_score <= ONE
    assert artifacts.outputs[0].numeric_value == artifacts.raw_score
    assert artifacts.raw_score == _canonical_output_decimal(
        _clamp_unit(sum((factor.weighted_value for factor in artifacts.factors), ZERO))
    )
    assert all(ZERO <= factor.normalized_value <= ONE for factor in artifacts.factors)
    assert all(factor.weighted_value >= ZERO for factor in artifacts.factors)


@given(
    base=st.lists(st.integers(min_value=0, max_value=100), min_size=5, max_size=5),
    increments=st.lists(st.integers(min_value=0, max_value=100), min_size=5, max_size=5),
)
@settings(max_examples=75, deadline=None)
def test_recurrence_pressure_is_bounded_and_monotone(
    base: list[int],
    increments: list[int],
) -> None:
    names = (
        "recurrence_count_30d",
        "recurrence_count_90d",
        "same_system_recurrence_count",
        "cross_system_count",
        "post_control_recurrence_count",
    )
    lower_inputs = dict(zip(names, base, strict=True))
    upper_inputs = dict(
        zip(names, (value + increment for value, increment in zip(base, increments, strict=True)), strict=True)
    )

    lower = _derive_recurrence_pressure(
        RECURRENCE_PARAMETERS,
        FULL_RANGE_THRESHOLDS,
        lower_inputs,
    )
    upper = _derive_recurrence_pressure(
        RECURRENCE_PARAMETERS,
        FULL_RANGE_THRESHOLDS,
        upper_inputs,
    )

    assert ZERO <= lower.raw_score <= upper.raw_score <= ONE
    assert all(ZERO <= factor.normalized_value <= ONE for factor in lower.factors)
    assert all(ZERO <= factor.normalized_value <= ONE for factor in upper.factors)


@given(
    enabled_mask=st.integers(min_value=0, max_value=63),
    additional_mask=st.integers(min_value=0, max_value=63),
    severity_band=st.sampled_from(("low", "moderate", "high", "critical")),
)
@settings(max_examples=75)
def test_exposure_factor_is_bounded_and_monotone_for_added_flags(
    enabled_mask: int,
    additional_mask: int,
    severity_band: str,
) -> None:
    flag_names = (
        "public_exposure_flag",
        "operator_surface_flag",
        "persistence_truth_flag",
        "approval_surface_flag",
        "cross_system_flag",
        "local_cloud_boundary_flag",
    )

    def inputs_for(mask: int) -> dict[str, bool | str]:
        values: dict[str, bool | str] = {
            name: bool(mask & (1 << index)) for index, name in enumerate(flag_names)
        }
        values["severity_band"] = severity_band
        return values

    lower = _derive_exposure_factor(
        EXPOSURE_PARAMETERS,
        FULL_RANGE_THRESHOLDS,
        inputs_for(enabled_mask),
    )
    upper = _derive_exposure_factor(
        EXPOSURE_PARAMETERS,
        FULL_RANGE_THRESHOLDS,
        inputs_for(enabled_mask | additional_mask),
    )

    assert ZERO <= lower.raw_score <= upper.raw_score <= ONE
    assert all(factor.raw_value in {ZERO, ONE} for factor in lower.factors[:-1])
    assert all(factor.raw_value in {ZERO, ONE} for factor in upper.factors[:-1])


@given(
    replay_state=st.sampled_from(tuple(ReplayState)),
    compatibility_state=st.sampled_from(tuple(CompatibilityResolutionState)),
    result_status=st.sampled_from(tuple(ResultStatus)),
)
def test_replay_safe_creation_requires_compatible_non_audit_posture(
    replay_state: ReplayState,
    compatibility_state: CompatibilityResolutionState,
    result_status: ResultStatus,
) -> None:
    body = SimpleNamespace(
        replay_state=replay_state,
        compatibility_resolution_state=compatibility_state,
        result_status=result_status,
        stale_state=StaleState.FRESH,
        recomputation_action=RecomputationAction.NO_RECOMPUTE_NEEDED,
    )
    is_audit_result = result_status in {ResultStatus.AUDIT_ONLY, ResultStatus.INVALID}
    expected_valid = (
        replay_state == ReplayState.REPLAY_SAFE
        and compatibility_state == CompatibilityResolutionState.RESOLVED_HARD_COMPATIBLE
        and not is_audit_result
    ) or (
        replay_state == ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION
        and compatibility_state == CompatibilityResolutionState.RESOLVED_WITH_BOUNDED_MIGRATION
        and not is_audit_result
    ) or replay_state in {ReplayState.AUDIT_READABLE_ONLY, ReplayState.NOT_REPLAYABLE}

    if expected_valid:
        lifecycle_service.validate_evaluation_creation_lifecycle(body)
    else:
        with pytest.raises(registry_service.GovernanceValidationError):
            lifecycle_service.validate_evaluation_creation_lifecycle(body)


@given(st.lists(st.sampled_from(tuple(StaleState)), min_size=1, max_size=40))
def test_lifecycle_stale_sequences_never_regress(requested_states: list[StaleState]) -> None:
    current = StaleState.FRESH.value

    for requested in requested_states:
        next_state = lifecycle_service._effective_stale_state(current, requested.value)
        assert lifecycle_service.STALE_RANK[next_state] >= lifecycle_service.STALE_RANK[current]
        assert lifecycle_service._effective_stale_state(next_state, requested.value) == next_state
        current = next_state

    assert lifecycle_service.STALE_RANK[current] == max(
        lifecycle_service.STALE_RANK[state.value]
        for state in (StaleState.FRESH, *requested_states)
    )


class SupersessionStateMachine(RuleBasedStateMachine):
    """Exercise arbitrary valid and conflicting canonical supersession sequences."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.db = self.session_factory()
        self.bindings = _seed_phase1_bindings(self.db)
        _create_input_bundle(self.db, self.bindings)
        self.sequence = 1
        self.chain = ["stateful-eval-001"]
        evaluation_service.create_lane_evaluation(
            self.db,
            _evaluation_create(
                self.bindings,
                lane_evaluation_id=self.chain[0],
                execution_mode="governed_canonical_execution",
            ),
        )

    def _next_id(self, prefix: str) -> str:
        self.sequence += 1
        return f"{prefix}-{self.sequence:03d}"

    @rule()
    def supersede_active_truth(self) -> None:
        successor_id = self._next_id("stateful-eval")
        evaluation_service.create_lane_evaluation(
            self.db,
            _evaluation_create(
                self.bindings,
                lane_evaluation_id=successor_id,
                supersedes_evaluation_id=self.chain[-1],
                execution_mode="governed_canonical_execution",
            ),
        )
        self.chain.append(successor_id)

    @rule()
    def reject_parallel_active_truth(self) -> None:
        conflicting_id = self._next_id("stateful-conflict")
        with pytest.raises(registry_service.GovernanceConflictError):
            evaluation_service.create_lane_evaluation(
                self.db,
                _evaluation_create(
                    self.bindings,
                    lane_evaluation_id=conflicting_id,
                    execution_mode="governed_canonical_execution",
                ),
            )

    @invariant()
    def preserve_one_active_acyclic_append_only_chain(self) -> None:
        evaluations = list(self.db.scalars(select(LaneEvaluation)).all())
        by_id = {item.lane_evaluation_id: item for item in evaluations}
        active = [item for item in evaluations if item.active_canonical_execution_key is not None]

        assert set(by_id) == set(self.chain)
        assert [item.lane_evaluation_id for item in active] == [self.chain[-1]]
        assert by_id[self.chain[-1]].superseded_by_evaluation_id is None
        for predecessor_id, successor_id in pairwise(self.chain):
            predecessor = by_id[predecessor_id]
            assert predecessor.superseded_by_evaluation_id == successor_id
            assert predecessor.active_canonical_execution_key is None

        lineage = lifecycle_service.get_lane_evaluation_lineage(self.db, self.chain[-1])
        assert [item.lane_evaluation_id for item in lineage.lineage] == self.chain

    def teardown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()


def test_canonical_supersession_state_machine() -> None:
    run_state_machine_as_test(
        SupersessionStateMachine,
        settings=settings(max_examples=10, stateful_step_count=12, deadline=None),
    )
