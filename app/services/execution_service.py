from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import (
    CompatibilityResolutionState,
    LaneFamily,
    OutputPosture,
    PolicyBundleKind,
    ReplayState,
    ResultStatus,
    StaleState,
    TraceTier,
)
from app.models.evaluation import LaneEvaluation
from app.models.governance import new_uuid
from app.schemas.evaluation import (
    LaneEvaluationCreate,
    LaneFactorValueCreate,
    LaneOutputValueCreate,
    TraceBundleCreate,
    TraceEventCreate,
)
from app.schemas.execution import LaneExecutionCreate, LaneExecutionResultRead
from app.schemas.execution_contracts import (
    ExposureFactorParameterContract,
    LaneSpecPayloadContract,
    RecurrencePressureParameterContract,
    ThresholdSetPayloadContract,
    VariableRegistryPayloadContract,
    VerificationBurdenParameterContract,
)
from app.services import evaluation_service, runtime_admission_service
from app.services.registry_service import (
    GovernanceValidationError,
    _clean_identifier,
    _clean_optional_text,
    get_lane_spec,
    get_parameter_set,
    get_policy_bundle,
    get_runtime_profile,
    get_threshold_set,
    get_variable_registry,
)


SUPPORTED_LANES = frozenset(
    {
        "verification_burden",
        "recurrence_pressure",
        "exposure_factor",
    }
)

PHASE6_RUNTIME_REQUIREMENTS = {
    field_name: sorted(allowed_values)[0]
    for field_name, allowed_values in runtime_admission_service.BIT_EXACT_RUNTIME_POLICY.items()
}

DECIMAL_CONTEXT = Context(prec=34, rounding=ROUND_HALF_EVEN)
ZERO = Decimal("0")
ONE = Decimal("1")

UNCERTAINTY_BAND_MAP = {
    "low": Decimal("0.10"),
    "moderate": Decimal("0.35"),
    "elevated": Decimal("0.65"),
    "severe": Decimal("1.00"),
}

SEVERITY_UPLIFT_MAP = {
    "low": Decimal("0.00"),
    "moderate": Decimal("0.08"),
    "high": Decimal("0.16"),
    "critical": Decimal("0.25"),
}


@dataclass(frozen=True)
class DerivedFactor:
    factor_name: str
    raw_value: Decimal
    normalized_value: Decimal
    weighted_value: Decimal
    provenance_class: str
    volatility_class: str
    trace_summary: str


@dataclass(frozen=True)
class DerivedLaneArtifacts:
    raw_score: Decimal
    band_label: str
    outputs: list[LaneOutputValueCreate]
    factors: list[LaneFactorValueCreate]
    trace_events: list[TraceEventCreate]

def _decimal_to_str(value: Decimal) -> str:
    normalized = value.normalize()
    return format(normalized, "f")


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool):
        raise GovernanceValidationError(f"{label} must be numeric, not boolean.")
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise GovernanceValidationError(f"{label} must be numeric.") from exc
    return decimal_value


def _clamp_unit(value: Decimal) -> Decimal:
    if value < ZERO:
        return ZERO
    if value > ONE:
        return ONE
    return value


def _cap_norm(value: Decimal, cap: Decimal) -> Decimal:
    if cap <= ZERO:
        raise GovernanceValidationError("cap values must be greater than zero.")
    if value < ZERO:
        raise GovernanceValidationError("raw factor values must be non-negative.")
    return min(value / cap, ONE)


def _saturating_transform(value: Decimal, k: Decimal) -> Decimal:
    if value < ZERO:
        raise GovernanceValidationError("recurrence counts must be non-negative.")
    if k <= ZERO:
        raise GovernanceValidationError("saturation coefficients must be greater than zero.")
    return ONE - (-(k * value)).exp()


def _binary_flag(value: Any, label: str) -> Decimal:
    if isinstance(value, bool):
        return ONE if value else ZERO
    decimal_value = _decimal(value, label)
    if decimal_value not in {ZERO, ONE}:
        raise GovernanceValidationError(f"{label} must be boolean or 0/1.")
    return decimal_value


def _require_active_binding(record: Any, label: str) -> None:
    if getattr(record, "superseded_at", None) is not None:
        raise GovernanceValidationError(f"{label} must be active for canonical execution.")


def _require_lane_binding(record: Any, lane_id: str, label: str) -> None:
    bound_lane_id = getattr(record, "lane_id", None)
    if bound_lane_id is not None and bound_lane_id != lane_id:
        raise GovernanceValidationError(f"{label} must bind to lane_id {lane_id}.")


def _require_supported_lane(lane_id: str) -> None:
    if lane_id not in SUPPORTED_LANES:
        raise GovernanceValidationError(
            f"lane_id {lane_id} is not supported by the bounded Phase 6 execution substrate."
        )


def _validate_phase6_runtime_profile(runtime_profile: Any) -> None:
    runtime_admission_service.validate_runtime_profile_for_canonical_execution(
        runtime_profile,
        runtime_profile.runtime_profile_id,
    )
    mismatches: list[str] = []
    for field_name, expected_value in PHASE6_RUNTIME_REQUIREMENTS.items():
        actual_value = getattr(runtime_profile, field_name, None)
        if actual_value != expected_value:
            mismatches.append(f"{field_name}={actual_value!r} expected {expected_value!r}")
    if mismatches:
        raise GovernanceValidationError(
            "Phase 6 execution substrate requires the deterministic runtime policy set "
            + ", ".join(mismatches)
            + "."
        )


def _load_lane_spec_payload(lane_spec: Any) -> LaneSpecPayloadContract:
    try:
        payload = LaneSpecPayloadContract.model_validate(lane_spec.payload)
    except Exception as exc:
        raise GovernanceValidationError(
            f"LaneSpec {lane_spec.lane_id} version {lane_spec.version} payload does not satisfy the supported execution contract."
        ) from exc
    if payload.lane_id != lane_spec.lane_id:
        raise GovernanceValidationError(
            f"LaneSpec {lane_spec.lane_id} version {lane_spec.version} payload lane_id must match the bound lane spec."
        )
    return payload


def _load_variable_registry_payload(record: Any) -> VariableRegistryPayloadContract:
    try:
        return VariableRegistryPayloadContract.model_validate(record.payload)
    except Exception as exc:
        raise GovernanceValidationError(
            f"VariableRegistry {record.variable_registry_id} version {record.version} does not satisfy the supported execution contract."
        ) from exc


def _load_threshold_contract(threshold_set: Any) -> ThresholdSetPayloadContract:
    try:
        return ThresholdSetPayloadContract.model_validate(threshold_set.payload)
    except Exception as exc:
        raise GovernanceValidationError(
            f"ThresholdSet {threshold_set.threshold_set_id} version {threshold_set.version} does not satisfy the supported execution contract."
        ) from exc


def _load_parameter_contract(lane_id: str, parameter_set: Any) -> (
    VerificationBurdenParameterContract
    | RecurrencePressureParameterContract
    | ExposureFactorParameterContract
):
    contract_type: type[
        VerificationBurdenParameterContract
        | RecurrencePressureParameterContract
        | ExposureFactorParameterContract
    ]
    if lane_id == "verification_burden":
        contract_type = VerificationBurdenParameterContract
    elif lane_id == "recurrence_pressure":
        contract_type = RecurrencePressureParameterContract
    elif lane_id == "exposure_factor":
        contract_type = ExposureFactorParameterContract
    else:
        raise GovernanceValidationError(f"lane_id {lane_id} is not supported by the bounded Phase 6 execution substrate.")
    try:
        return contract_type.model_validate(parameter_set.payload)
    except Exception as exc:
        raise GovernanceValidationError(
            f"ParameterSet {parameter_set.parameter_set_id} version {parameter_set.version} does not satisfy the supported execution contract."
        ) from exc


def _required_variables_for_lane(lane_id: str) -> tuple[str, ...]:
    if lane_id == "verification_burden":
        return (
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        )
    if lane_id == "recurrence_pressure":
        return (
            "recurrence_count_30d",
            "recurrence_count_90d",
            "same_system_recurrence_count",
            "cross_system_count",
            "post_control_recurrence_count",
        )
    if lane_id == "exposure_factor":
        return (
            "public_exposure_flag",
            "operator_surface_flag",
            "persistence_truth_flag",
            "approval_surface_flag",
            "cross_system_flag",
            "local_cloud_boundary_flag",
            "severity_band",
        )
    raise GovernanceValidationError(f"Unsupported lane_id {lane_id}.")


def _get_required_input_values(input_bundle: Any, required_variables: tuple[str, ...]) -> dict[str, Any]:
    values = input_bundle.inline_values or {}
    missing = [name for name in required_variables if name not in values]
    if missing:
        raise GovernanceValidationError(
            "canonical lane execution requires all admitted input variables. Missing: "
            + ", ".join(missing)
            + "."
        )
    return values


def _validate_variable_registry(record: Any, lane_id: str, required_variables: tuple[str, ...]) -> None:
    _require_active_binding(
        record,
        f"VariableRegistry {record.variable_registry_id} version {record.version}",
    )
    payload_variables = _load_variable_registry_payload(record).variables
    missing = [name for name in required_variables if name not in payload_variables]
    if missing:
        raise GovernanceValidationError(
            f"VariableRegistry {record.variable_registry_id} version {record.version} does not admit lane {lane_id} variables: "
            + ", ".join(missing)
            + "."
        )


def _load_bands(threshold_set: Any) -> list[dict[str, Any]]:
    threshold_contract = _load_threshold_contract(threshold_set)
    return [band.model_dump(mode="python") for band in threshold_contract.bands]


def _resolve_band_label(score: Decimal, threshold_set: Any) -> str:
    bands = _load_bands(threshold_set)
    matched_label: str | None = None
    for band in bands:
        if not isinstance(band, dict):
            raise GovernanceValidationError("threshold bands must be objects.")
        label = band.get("label")
        if not isinstance(label, str) or not label.strip():
            raise GovernanceValidationError("threshold bands require a non-blank label.")
        minimum = _decimal(band.get("min_inclusive"), f"{label}.min_inclusive")
        maximum_exclusive = band.get("max_exclusive")
        maximum_inclusive = band.get("max_inclusive")
        if (maximum_exclusive is None) == (maximum_inclusive is None):
            raise GovernanceValidationError(
                f"threshold band {label} requires exactly one of max_exclusive or max_inclusive."
            )
        if maximum_exclusive is not None:
            maximum = _decimal(maximum_exclusive, f"{label}.max_exclusive")
            in_range = minimum <= score < maximum
        else:
            maximum = _decimal(maximum_inclusive, f"{label}.max_inclusive")
            in_range = minimum <= score <= maximum
        if minimum < ZERO or maximum > ONE or minimum > maximum:
            raise GovernanceValidationError(f"threshold band {label} must stay within [0,1].")
        if in_range:
            if matched_label is not None:
                raise GovernanceValidationError("threshold bands overlap for the computed score.")
            matched_label = label.strip()
    if matched_label is None:
        raise GovernanceValidationError(
            "threshold set does not classify the computed output score."
        )
    return matched_label


def _trace_event(step_order: int, event_type: str, payload_ref: str, summary: str) -> TraceEventCreate:
    return TraceEventCreate(
        trace_step_order=step_order,
        trace_event_type=event_type,
        trace_payload_ref=payload_ref,
        trace_summary=summary,
    )


def _factor_create(factor: DerivedFactor) -> LaneFactorValueCreate:
    return LaneFactorValueCreate(
        factor_name=factor.factor_name,
        raw_value=factor.raw_value,
        normalized_value=factor.normalized_value,
        weighted_value=factor.weighted_value,
        provenance_class=factor.provenance_class,
        volatility_class=factor.volatility_class,
    )


def _derive_verification_burden(
    parameter_set: Any,
    threshold_set: Any,
    input_values: dict[str, Any],
) -> DerivedLaneArtifacts:
    parameter_contract = _load_parameter_contract("verification_burden", parameter_set)
    weights = parameter_contract.weights
    caps = parameter_contract.caps

    with localcontext(DECIMAL_CONTEXT):
        normalized_inputs = [
            (
                "implementation_minutes",
                _decimal(input_values["implementation_minutes"], "implementation_minutes"),
                _cap_norm(
                    _decimal(input_values["implementation_minutes"], "implementation_minutes"),
                    caps.I_cap,
                ),
                weights.w_I,
                "observed_duration_minutes",
            ),
            (
                "verification_minutes",
                _decimal(input_values["verification_minutes"], "verification_minutes"),
                _cap_norm(
                    _decimal(input_values["verification_minutes"], "verification_minutes"),
                    caps.V_cap,
                ),
                weights.w_V,
                "observed_duration_minutes",
            ),
            (
                "rework_minutes",
                _decimal(input_values["rework_minutes"], "rework_minutes"),
                _cap_norm(_decimal(input_values["rework_minutes"], "rework_minutes"), caps.R_cap),
                weights.w_R,
                "observed_duration_minutes",
            ),
            (
                "interruption_count",
                _decimal(input_values["interruption_count"], "interruption_count"),
                _cap_norm(
                    _decimal(input_values["interruption_count"], "interruption_count"),
                    caps.X_cap,
                ),
                weights.w_X,
                "observed_count",
            ),
            (
                "downstream_fix_minutes",
                _decimal(input_values["downstream_fix_minutes"], "downstream_fix_minutes"),
                _cap_norm(
                    _decimal(input_values["downstream_fix_minutes"], "downstream_fix_minutes"),
                    caps.D_cap,
                ),
                weights.w_D,
                "observed_duration_minutes",
            ),
        ]
        uncertainty_band = input_values["uncertainty_band"]
        if not isinstance(uncertainty_band, str) or uncertainty_band not in UNCERTAINTY_BAND_MAP:
            raise GovernanceValidationError(
                "uncertainty_band must be one of low, moderate, elevated, severe."
            )
        uncertainty_scalar = UNCERTAINTY_BAND_MAP[uncertainty_band]
        factors: list[DerivedFactor] = []
        total = ZERO
        for factor_name, raw_value, normalized_value, weight, volatility_class in normalized_inputs:
            weighted_value = normalized_value * weight
            total += weighted_value
            factors.append(
                DerivedFactor(
                    factor_name=factor_name,
                    raw_value=raw_value,
                    normalized_value=normalized_value,
                    weighted_value=weighted_value,
                    provenance_class="input_bundle_inline_value",
                    volatility_class=volatility_class,
                    trace_summary=(
                        f"Factor {factor_name} normalized to {_decimal_to_str(normalized_value)} "
                        f"and weighted to {_decimal_to_str(weighted_value)}."
                    ),
                )
            )
        uncertainty_weighted = uncertainty_scalar * weights.w_U
        total += uncertainty_weighted
        factors.append(
            DerivedFactor(
                factor_name="uncertainty_band",
                raw_value=uncertainty_scalar,
                normalized_value=uncertainty_scalar,
                weighted_value=uncertainty_weighted,
                provenance_class="input_bundle_inline_band_mapping",
                volatility_class="ordinal_band",
                trace_summary=(
                    f"Factor uncertainty_band mapped to {_decimal_to_str(uncertainty_scalar)} "
                    f"and weighted to {_decimal_to_str(uncertainty_weighted)}."
                ),
            )
        )
        score = _clamp_unit(total)
    band_label = _resolve_band_label(score, threshold_set)
    return _build_lane_artifacts(
        lane_id="verification_burden",
        score=score,
        band_label=band_label,
        factors=factors,
    )


def _derive_recurrence_pressure(
    parameter_set: Any,
    threshold_set: Any,
    input_values: dict[str, Any],
) -> DerivedLaneArtifacts:
    parameter_contract = _load_parameter_contract("recurrence_pressure", parameter_set)
    weights = parameter_contract.weights
    coefficients = parameter_contract.saturation

    with localcontext(DECIMAL_CONTEXT):
        configured_factors = [
            ("recurrence_count_30d", "w30", "k30"),
            ("recurrence_count_90d", "w90", "k90"),
            ("same_system_recurrence_count", "wsame", "ksame"),
            ("cross_system_count", "wcross", "kcross"),
            ("post_control_recurrence_count", "wpost", "kpost"),
        ]
        factors: list[DerivedFactor] = []
        total = ZERO
        for factor_name, weight_key, coefficient_key in configured_factors:
            raw_value = _decimal(input_values[factor_name], factor_name)
            normalized_value = _saturating_transform(raw_value, getattr(coefficients, coefficient_key))
            weighted_value = normalized_value * getattr(weights, weight_key)
            total += weighted_value
            factors.append(
                DerivedFactor(
                    factor_name=factor_name,
                    raw_value=raw_value,
                    normalized_value=normalized_value,
                    weighted_value=weighted_value,
                    provenance_class="input_bundle_inline_value",
                    volatility_class="observed_count",
                    trace_summary=(
                        f"Factor {factor_name} saturated to {_decimal_to_str(normalized_value)} "
                        f"and weighted to {_decimal_to_str(weighted_value)}."
                    ),
                )
            )
        score = _clamp_unit(total)
    band_label = _resolve_band_label(score, threshold_set)
    return _build_lane_artifacts(
        lane_id="recurrence_pressure",
        score=score,
        band_label=band_label,
        factors=factors,
    )


def _derive_exposure_factor(
    parameter_set: Any,
    threshold_set: Any,
    input_values: dict[str, Any],
) -> DerivedLaneArtifacts:
    parameter_contract = _load_parameter_contract("exposure_factor", parameter_set)
    coefficients = parameter_contract.coefficients

    with localcontext(DECIMAL_CONTEXT):
        configured_flags = [
            ("public_exposure_flag", "alpha_pub"),
            ("operator_surface_flag", "alpha_op"),
            ("persistence_truth_flag", "alpha_persist"),
            ("approval_surface_flag", "alpha_approve"),
            ("cross_system_flag", "alpha_cross"),
            ("local_cloud_boundary_flag", "alpha_boundary"),
        ]
        factors: list[DerivedFactor] = []
        product = ONE
        for factor_name, coefficient_key in configured_flags:
            raw_value = _binary_flag(input_values[factor_name], factor_name)
            weighted_value = getattr(coefficients, coefficient_key) * raw_value
            product *= ONE - weighted_value
            factors.append(
                DerivedFactor(
                    factor_name=factor_name,
                    raw_value=raw_value,
                    normalized_value=raw_value,
                    weighted_value=weighted_value,
                    provenance_class="input_bundle_inline_flag",
                    volatility_class="binary_flag",
                    trace_summary=(
                        f"Factor {factor_name} admitted as {_decimal_to_str(raw_value)} "
                        f"with bounded-union coefficient {_decimal_to_str(weighted_value)}."
                    ),
                )
            )
        severity_band = input_values["severity_band"]
        if not isinstance(severity_band, str) or severity_band not in SEVERITY_UPLIFT_MAP:
            raise GovernanceValidationError(
                "severity_band must be one of low, moderate, high, critical."
            )
        severity_uplift = SEVERITY_UPLIFT_MAP[severity_band]
        factors.append(
            DerivedFactor(
                factor_name="severity_band",
                raw_value=severity_uplift,
                normalized_value=severity_uplift,
                weighted_value=severity_uplift,
                provenance_class="input_bundle_inline_band_mapping",
                volatility_class="ordinal_band",
                trace_summary=(
                    f"Factor severity_band mapped to uplift {_decimal_to_str(severity_uplift)}."
                ),
            )
        )
        score = _clamp_unit((ONE - product) + severity_uplift)
    band_label = _resolve_band_label(score, threshold_set)
    return _build_lane_artifacts(
        lane_id="exposure_factor",
        score=score,
        band_label=band_label,
        factors=factors,
    )


def _build_lane_artifacts(
    *,
    lane_id: str,
    score: Decimal,
    band_label: str,
    factors: list[DerivedFactor],
) -> DerivedLaneArtifacts:
    raw_output_field_name = f"{lane_id}_raw"
    band_output_field_name = f"{lane_id}_band"

    outputs = [
        LaneOutputValueCreate(
            output_field_name=raw_output_field_name,
            output_posture=OutputPosture.RAW,
            numeric_value=score,
            value_range_class=band_label,
            is_primary_output=True,
        ),
        LaneOutputValueCreate(
            output_field_name=band_output_field_name,
            output_posture=OutputPosture.BANDED,
            enum_value=band_label,
            value_range_class=band_label,
            is_primary_output=False,
        ),
    ]

    trace_events = [
        _trace_event(
            0,
            "execution_request_bound",
            f"trace://lane/{lane_id}/execution-request",
            "Execution request admitted through the bounded Phase 6 execution substrate.",
        )
    ]
    for offset, factor in enumerate(factors, start=1):
        trace_events.append(
            _trace_event(
                offset,
                "factor_derived",
                f"trace://lane/{lane_id}/factor/{factor.factor_name}",
                factor.trace_summary,
            )
        )
    trace_events.append(
        _trace_event(
            len(trace_events),
            "output_derived",
            f"trace://lane/{lane_id}/output/{raw_output_field_name}",
            f"Primary raw output {_decimal_to_str(score)} classified into band {band_label}.",
        )
    )

    return DerivedLaneArtifacts(
        raw_score=score,
        band_label=band_label,
        outputs=outputs,
        factors=[_factor_create(factor) for factor in factors],
        trace_events=trace_events,
    )


def _derive_lane_artifacts(
    lane_id: str,
    parameter_set: Any,
    threshold_set: Any,
    input_values: dict[str, Any],
) -> DerivedLaneArtifacts:
    if lane_id == "verification_burden":
        return _derive_verification_burden(parameter_set, threshold_set, input_values)
    if lane_id == "recurrence_pressure":
        return _derive_recurrence_pressure(parameter_set, threshold_set, input_values)
    if lane_id == "exposure_factor":
        return _derive_exposure_factor(parameter_set, threshold_set, input_values)
    raise GovernanceValidationError(
        f"lane_id {lane_id} is not supported by the bounded Phase 6 execution substrate."
    )


def _active_canonical_execution_conflict(
    db: Session,
    *,
    lane_id: str,
    lane_spec_version: int,
    runtime_profile_id: str,
    runtime_profile_version: int,
    input_bundle_id: str,
    compatibility_tuple_hash: str,
    scope_id: str | None,
    scope_version: int | None,
) -> LaneEvaluation | None:
    return db.scalar(
        select(LaneEvaluation).where(
            LaneEvaluation.lane_id == lane_id,
            LaneEvaluation.lane_spec_version == lane_spec_version,
            LaneEvaluation.runtime_profile_id == runtime_profile_id,
            LaneEvaluation.runtime_profile_version == runtime_profile_version,
            LaneEvaluation.input_bundle_id == input_bundle_id,
            LaneEvaluation.compatibility_tuple_hash == compatibility_tuple_hash,
            LaneEvaluation.execution_mode == "governed_canonical_execution",
            LaneEvaluation.superseded_by_evaluation_id.is_(None),
            LaneEvaluation.scope_id.is_(scope_id) if scope_id is None else LaneEvaluation.scope_id == scope_id,
            LaneEvaluation.scope_version.is_(scope_version)
            if scope_version is None
            else LaneEvaluation.scope_version == scope_version,
        )
    )


def execute_lane(db: Session, body: LaneExecutionCreate) -> LaneExecutionResultRead:
    lane_id = _clean_identifier(body.lane_id, "lane_id")
    _require_supported_lane(lane_id)

    lane_spec = get_lane_spec(db, lane_id, body.lane_spec_version)
    _require_active_binding(lane_spec, f"LaneSpec {lane_id} version {body.lane_spec_version}")
    if not lane_spec.is_admissible:
        raise GovernanceValidationError(f"LaneSpec {lane_id} version {body.lane_spec_version} is not admissible.")
    if lane_spec.lane_family != LaneFamily.CANONICAL_NUMERIC.value:
        raise GovernanceValidationError("Phase 6 execution substrate supports canonical_numeric lanes only.")
    _load_lane_spec_payload(lane_spec)

    required_variables = _required_variables_for_lane(lane_id)
    variable_registry = get_variable_registry(
        db,
        body.compatibility_binding.variable_registry_id,
        body.compatibility_binding.compatibility_tuple.variable_registry_version,
    )
    _validate_variable_registry(variable_registry, lane_id, required_variables)

    parameter_set = get_parameter_set(
        db,
        body.compatibility_binding.parameter_set_id,
        body.compatibility_binding.compatibility_tuple.parameter_set_version,
    )
    _require_active_binding(
        parameter_set,
        f"ParameterSet {parameter_set.parameter_set_id} version {parameter_set.version}",
    )
    _require_lane_binding(
        parameter_set,
        lane_id,
        f"ParameterSet {parameter_set.parameter_set_id} version {parameter_set.version}",
    )

    threshold_set = get_threshold_set(
        db,
        body.compatibility_binding.threshold_set_id,
        body.compatibility_binding.compatibility_tuple.threshold_registry_version,
    )
    _require_active_binding(
        threshold_set,
        f"ThresholdSet {threshold_set.threshold_set_id} version {threshold_set.version}",
    )
    _require_lane_binding(
        threshold_set,
        lane_id,
        f"ThresholdSet {threshold_set.threshold_set_id} version {threshold_set.version}",
    )

    null_policy = get_policy_bundle(
        db,
        body.compatibility_binding.null_policy_bundle_id,
        body.compatibility_binding.compatibility_tuple.null_policy_version,
    )
    _require_active_binding(
        null_policy,
        f"PolicyBundle {null_policy.policy_bundle_id} version {null_policy.version}",
    )
    _require_lane_binding(
        null_policy,
        lane_id,
        f"PolicyBundle {null_policy.policy_bundle_id} version {null_policy.version}",
    )
    if null_policy.policy_kind != PolicyBundleKind.NULL_POLICY.value:
        raise GovernanceValidationError(
            f"PolicyBundle {null_policy.policy_bundle_id} version {null_policy.version} "
            "must be policy_kind=null_policy."
        )

    degraded_policy = get_policy_bundle(
        db,
        body.compatibility_binding.degraded_mode_policy_bundle_id,
        body.compatibility_binding.compatibility_tuple.degraded_mode_policy_version,
    )
    _require_active_binding(
        degraded_policy,
        f"PolicyBundle {degraded_policy.policy_bundle_id} version {degraded_policy.version}",
    )
    _require_lane_binding(
        degraded_policy,
        lane_id,
        f"PolicyBundle {degraded_policy.policy_bundle_id} version {degraded_policy.version}",
    )
    if degraded_policy.policy_kind != PolicyBundleKind.DEGRADED_MODE_POLICY.value:
        raise GovernanceValidationError(
            f"PolicyBundle {degraded_policy.policy_bundle_id} version {degraded_policy.version} "
            "must be policy_kind=degraded_mode_policy."
        )

    runtime_profile = get_runtime_profile(db, body.runtime_profile_id, body.runtime_profile_version)
    _validate_phase6_runtime_profile(runtime_profile)

    input_bundle = evaluation_service.get_input_bundle(db, body.input_bundle_id)
    if not input_bundle.frozen_flag:
        raise GovernanceValidationError("canonical lane execution requires a frozen input bundle.")
    input_values = _get_required_input_values(input_bundle, required_variables)
    compatibility_tuple_hash = body.compatibility_binding.canonical_hash()
    execution_scope_id = _clean_optional_text(body.scope_id)
    execution_scope_version = body.scope_version
    if input_bundle.scope_id is not None:
        if execution_scope_id is None:
            execution_scope_id = input_bundle.scope_id
            execution_scope_version = input_bundle.scope_version
        elif (
            execution_scope_id != input_bundle.scope_id
            or execution_scope_version != input_bundle.scope_version
        ):
            raise GovernanceValidationError(
                "canonical lane execution scope linkage must match the frozen input bundle scope linkage."
            )
    active_conflict = _active_canonical_execution_conflict(
        db,
        lane_id=lane_id,
        lane_spec_version=body.lane_spec_version,
        runtime_profile_id=body.runtime_profile_id,
        runtime_profile_version=body.runtime_profile_version,
        input_bundle_id=body.input_bundle_id,
        compatibility_tuple_hash=compatibility_tuple_hash,
        scope_id=execution_scope_id,
        scope_version=execution_scope_version,
    )
    supersedes_evaluation_id = _clean_optional_text(body.supersedes_evaluation_id)
    if active_conflict is not None:
        if supersedes_evaluation_id is None:
            raise GovernanceValidationError(
                "an active governed_canonical_execution evaluation already exists for this canonical execution context; "
                "execution must explicitly supersede that lineage target."
            )
        if active_conflict.lane_evaluation_id != supersedes_evaluation_id:
            raise GovernanceValidationError(
                "execution supersession target must match the current active canonical execution lineage record."
            )

    if supersedes_evaluation_id is not None:
        prior_evaluation = evaluation_service.get_lane_evaluation(db, supersedes_evaluation_id)
        if prior_evaluation.lane_id != lane_id:
            raise GovernanceValidationError("execution supersession target must belong to the same lane_id.")
        if prior_evaluation.superseded_by_evaluation_id is not None:
            raise GovernanceValidationError("execution supersession target is already closed by lineage.")

    artifacts = _derive_lane_artifacts(lane_id, parameter_set, threshold_set, input_values)

    lane_evaluation_id = (
        _clean_identifier(body.lane_evaluation_id, "lane_evaluation_id")
        if body.lane_evaluation_id is not None
        else new_uuid()
    )
    trace_bundle_id = new_uuid()
    compatibility_tuple = body.compatibility_binding.compatibility_tuple

    evaluation_create = LaneEvaluationCreate(
        lane_evaluation_id=lane_evaluation_id,
        supersedes_evaluation_id=supersedes_evaluation_id,
        supersession_class=body.supersession_class,
        supersession_reason=body.supersession_reason,
        supersession_timestamp=body.supersession_timestamp,
        lane_id=lane_id,
        lane_spec_version=body.lane_spec_version,
        lane_family=LaneFamily.CANONICAL_NUMERIC,
        execution_mode=_clean_identifier(body.execution_mode, "execution_mode"),
        result_status=ResultStatus.COMPUTED_STRICT,
        compatibility_resolution_state=body.compatibility_resolution_state,
        runtime_profile_id=_clean_identifier(body.runtime_profile_id, "runtime_profile_id"),
        runtime_profile_version=body.runtime_profile_version,
        input_bundle_id=_clean_identifier(body.input_bundle_id, "input_bundle_id"),
        replay_state=(
            ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION
            if body.compatibility_resolution_state
            == CompatibilityResolutionState.RESOLVED_WITH_BOUNDED_MIGRATION
            else ReplayState.REPLAY_SAFE
        ),
        stale_state=StaleState.FRESH,
        recomputation_action="no_recompute_needed",
        lifecycle_reason_code="phase6_execution_created",
        lifecycle_reason_detail="Canonical lane execution persisted through the bounded Phase 6 substrate.",
        raw_output_hash=None,
        scope_id=execution_scope_id,
        scope_version=execution_scope_version,
        compatibility_binding=body.compatibility_binding,
        output_values=artifacts.outputs,
        factor_values=artifacts.factors,
        trace_bundle=TraceBundleCreate(
            trace_bundle_id=trace_bundle_id,
            trace_tier=TraceTier.TIER_1_FULL,
            trace_schema_version=compatibility_tuple.trace_schema_version,
            reconstructable_flag=True,
            trace_events=artifacts.trace_events,
        ),
        created_by=_clean_optional_text(body.created_by),
    )
    evaluation_service.create_lane_evaluation(db, evaluation_create)
    evaluation = evaluation_service.get_lane_evaluation_detail(db, lane_evaluation_id)
    return LaneExecutionResultRead(
        lane_evaluation_id=evaluation.lane_evaluation_id,
        lane_id=evaluation.lane_id,
        result_status=evaluation.result_status,
        compatibility_resolution_state=evaluation.compatibility_resolution_state,
        deterministic_admission_state=evaluation.deterministic_admission_state,
        replay_state=evaluation.replay_state,
        stale_state=evaluation.stale_state,
        trace_bundle_id=evaluation.trace_bundle_id,
        raw_output_hash=evaluation.raw_output_hash,
        created_at=evaluation.created_at,
        evaluation=evaluation,
    )
