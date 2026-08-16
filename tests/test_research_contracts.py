"""Validation gates for non-runtime ForgeMath research contracts."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contracts" / "research"
FIXTURE_ROOT = CONTRACT_ROOT / "fixtures" / "valid"

SCHEMA_PATHS = {
    "receipt": CONTRACT_ROOT / "MathDecisionReceipt.v1.schema.json",
    "manifest": CONTRACT_ROOT / "EquationPackageManifest.v1.schema.json",
    "signed_package": CONTRACT_ROOT / "SignedEquationPackageResearch.v1.schema.json",
}
FIXTURE_PATHS = {
    "receipt": FIXTURE_ROOT / "math-decision-receipt.json",
    "manifest": FIXTURE_ROOT / "equation-package-manifest.json",
    "signed_package": FIXTURE_ROOT / "signed-equation-package.json",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


SCHEMAS = {name: _load(path) for name, path in SCHEMA_PATHS.items()}
FIXTURES = {name: _load(path) for name, path in FIXTURE_PATHS.items()}

REGISTRY = Registry()
for schema in SCHEMAS.values():
    REGISTRY = REGISTRY.with_resource(schema["$id"], Resource.from_contents(schema))


def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(
        SCHEMAS[name],
        registry=REGISTRY,
        format_checker=FormatChecker(),
    )


def _assert_invalid(name: str, instance: dict) -> None:
    errors = list(_validator(name).iter_errors(instance))
    assert errors, f"Expected {name} research fixture mutation to fail closed."


def _manifest_digest(manifest: dict) -> str:
    fixture_bytes = json.dumps(
        manifest,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(fixture_bytes).hexdigest()}"


def _assert_content_addresses(receipt: dict, signed_package: dict) -> None:
    digest = _manifest_digest(signed_package["manifest"])
    assert signed_package["manifest_digest"] == digest
    assert receipt["equation_package_ref"]["manifest_digest"] == digest


@pytest.mark.parametrize("name", tuple(SCHEMA_PATHS))
def test_research_contract_schemas_are_valid_draft_2020_12(name: str) -> None:
    Draft202012Validator.check_schema(SCHEMAS[name])


@pytest.mark.parametrize("name", tuple(FIXTURE_PATHS))
def test_research_contract_fixtures_validate(name: str) -> None:
    _validator(name).validate(FIXTURES[name])


def test_receipt_rejects_float_semantics_unsupported_lanes_and_runtime_claims() -> None:
    exponent_value = deepcopy(FIXTURES["receipt"])
    exponent_value["outputs"][0]["numeric_value"] = "3.9e-1"
    _assert_invalid("receipt", exponent_value)

    unsupported_lane = deepcopy(FIXTURES["receipt"])
    unsupported_lane["lane_evaluation"]["lane_id"] = "control_effectiveness"
    _assert_invalid("receipt", unsupported_lane)

    runtime_claim = deepcopy(FIXTURES["receipt"])
    runtime_claim["contract_status"] = "canonical_runtime_authority"
    _assert_invalid("receipt", runtime_claim)

    prefixed_persisted_hash = deepcopy(FIXTURES["receipt"])
    prefixed_persisted_hash["lane_evaluation"]["raw_output_hash"] = (
        f"sha256:{prefixed_persisted_hash['lane_evaluation']['raw_output_hash']}"
    )
    _assert_invalid("receipt", prefixed_persisted_hash)


@pytest.mark.parametrize(
    "lane_id",
    (
        "verification_burden",
        "recurrence_pressure",
        "exposure_factor",
        "priority_score",
        "reviewability",
    ),
)
def test_research_contracts_admit_exact_runtime_lane_set(lane_id: str) -> None:
    receipt = deepcopy(FIXTURES["receipt"])
    receipt["lane_evaluation"]["lane_id"] = lane_id
    _validator("receipt").validate(receipt)

    manifest = deepcopy(FIXTURES["manifest"])
    manifest["lane_id"] = lane_id
    _validator("manifest").validate(manifest)


def test_manifest_requires_governance_artifacts_and_forbids_execution() -> None:
    executable = deepcopy(FIXTURES["manifest"])
    executable["governance"]["executable"] = True
    _assert_invalid("manifest", executable)

    arbitrary_expression = deepcopy(FIXTURES["manifest"])
    arbitrary_expression["governance"]["arbitrary_expression_allowed"] = True
    _assert_invalid("manifest", arbitrary_expression)

    missing_golden_vectors = deepcopy(FIXTURES["manifest"])
    missing_golden_vectors["artifacts"] = [
        artifact
        for artifact in missing_golden_vectors["artifacts"]
        if artifact["role"] != "golden_vectors"
    ]
    _assert_invalid("manifest", missing_golden_vectors)

    duplicate_lane_spec = deepcopy(FIXTURES["manifest"])
    duplicate_lane_spec["artifacts"].append(
        {
            "path": "lane-spec-copy.json",
            "role": "lane_spec",
            "digest": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
            "media_type": "application/json",
        }
    )
    _assert_invalid("manifest", duplicate_lane_spec)


def test_signed_envelope_requires_claims_but_remains_unverified_and_non_executable() -> None:
    unsigned = deepcopy(FIXTURES["signed_package"])
    unsigned["signatures"] = []
    _assert_invalid("signed_package", unsigned)

    executable = deepcopy(FIXTURES["signed_package"])
    executable["executable"] = True
    _assert_invalid("signed_package", executable)

    signed_package = FIXTURES["signed_package"]
    assert signed_package["signature_status"] == "unverified_research_fixture"
    assert signed_package["verification_policy"]["threshold"] <= len(signed_package["signatures"])
    assert {
        signature["key_id"] for signature in signed_package["signatures"]
    } <= set(signed_package["verification_policy"]["trusted_key_ids"])


def test_manifest_content_address_is_stable_across_references() -> None:
    manifest = FIXTURES["manifest"]
    assert FIXTURES["signed_package"]["manifest"] == manifest
    _assert_content_addresses(FIXTURES["receipt"], FIXTURES["signed_package"])

    mismatched_package = deepcopy(FIXTURES["signed_package"])
    mismatched_package["manifest"]["version"] = 2
    with pytest.raises(AssertionError):
        _assert_content_addresses(FIXTURES["receipt"], mismatched_package)
