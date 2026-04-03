from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import time
from urllib import error, request
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from tests.test_phase2_api import _create_input_bundle as _create_phase2_input_bundle
from tests.test_phase2_api import _seed_phase1_bindings
from tests.test_phase6_execution import _create_input_bundle as _create_phase6_input_bundle
from tests.test_phase6_execution import _execution_request, _seed_execution_bindings


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = "/home/charlie/Forge/ecosystem/DataForge/.venv/bin/python"


def _pick_free_port() -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])
    except PermissionError:
        pytest.skip("sandbox does not permit binding localhost ports for HTTP integration tests.")


def _seed_sqlite_database(db_path: Path, seed_fn):
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        context = seed_fn(session)
    finally:
        session.close()
        engine.dispose()
    return database_url, context


def _start_uvicorn(database_url: str):
    port = _pick_free_port()
    env = os.environ.copy()
    env["FORGEMATH_DATABASE_URL"] = database_url
    env["FORGEMATH_HOST"] = "127.0.0.1"
    env["FORGEMATH_PORT"] = str(port)

    process = subprocess.Popen(
        [
            PYTHON_BIN,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"

    deadline = time.time() + 15
    while time.time() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1)
            raise AssertionError(f"uvicorn exited early.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
        try:
            status, _ = _request("GET", f"{base_url}/health")
            if status == 200:
                return process, base_url
        except Exception:
            time.sleep(0.1)

    process.terminate()
    stdout, stderr = process.communicate(timeout=5)
    raise AssertionError(f"uvicorn did not become ready.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")


def _request(method: str, url: str, payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            parsed = json.loads(raw) if raw else None
            return response.status, parsed
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        parsed = json.loads(raw) if raw else None
        return exc.code, parsed


def _run_http_integration(seed_fn, assertion_fn):
    db_path = Path(f"/tmp/forgemath-http-{uuid.uuid4().hex}.sqlite3")
    database_url, context = _seed_sqlite_database(db_path, seed_fn)
    process, base_url = _start_uvicorn(database_url)
    try:
        assertion_fn(base_url, context)
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if db_path.exists():
            db_path.unlink()


def test_manual_lane_evaluation_route_rejects_computed_canonical_truth():
    def seed(session):
        bindings = _seed_phase1_bindings(session)
        _create_phase2_input_bundle(session, bindings)
        return bindings

    def assertions(base_url: str, bindings):
        status, payload = _request(
            "POST",
            f"{base_url}/api/v1/forgemath/lane-evaluations",
            {
                "lane_evaluation_id": "manual-computed-001",
                "lane_id": bindings["lane_spec"].lane_id,
                "lane_spec_version": bindings["lane_spec"].version,
                "lane_family": bindings["lane_spec"].lane_family,
                "result_status": "computed_strict",
                "compatibility_resolution_state": "resolved_hard_compatible",
                "runtime_profile_id": bindings["runtime_profile"].runtime_profile_id,
                "runtime_profile_version": bindings["runtime_profile"].version,
                "input_bundle_id": "bundle-001",
                "replay_state": "replay_safe",
                "stale_state": "fresh",
                "recomputation_action": "no_recompute_needed",
                "lifecycle_reason_code": "manual_computed_attempt",
                "lifecycle_reason_detail": "Attempt to mint canonical computed truth through manual ingest.",
                "compatibility_binding": {
                    "variable_registry_id": bindings["variable_registry"].variable_registry_id,
                    "parameter_set_id": bindings["parameter_set"].parameter_set_id,
                    "threshold_set_id": bindings["threshold_set"].threshold_set_id,
                    "null_policy_bundle_id": bindings["null_policy"].policy_bundle_id,
                    "degraded_mode_policy_bundle_id": bindings["degraded_policy"].policy_bundle_id,
                    "compatibility_tuple": {
                        "lane_spec_version": bindings["lane_spec"].version,
                        "variable_registry_version": bindings["variable_registry"].version,
                        "parameter_set_version": bindings["parameter_set"].version,
                        "threshold_registry_version": bindings["threshold_set"].version,
                        "null_policy_version": bindings["null_policy"].version,
                        "degraded_mode_policy_version": bindings["degraded_policy"].version,
                        "trace_schema_version": 1,
                        "projection_schema_version": 1,
                        "submodule_build_version": "forge-math-hardening",
                    },
                },
                "trace_bundle": {
                    "trace_bundle_id": "trace-manual-computed-001",
                    "trace_tier": "tier_1_full",
                    "trace_schema_version": 1,
                    "reconstructable_flag": True,
                    "trace_events": [
                        {
                            "trace_step_order": 0,
                            "trace_event_type": "manual_ingest_attempted",
                            "trace_payload_ref": "trace://manual/attempt",
                            "trace_summary": "Manual attempt to persist computed truth.",
                        }
                    ],
                },
                "created_by": "http-test",
            },
        )

        assert status == 422
        assert "manual lane evaluation ingestion may only persist blocked, audit_only, or invalid results" in json.dumps(payload)

    _run_http_integration(seed, assertions)


def test_lane_execution_route_serializes_decimal_artifacts_as_strings():
    def seed(session):
        bindings = _seed_execution_bindings(
            session,
            lane_id="verification_burden",
            variable_names=[
                "implementation_minutes",
                "verification_minutes",
                "rework_minutes",
                "interruption_count",
                "downstream_fix_minutes",
                "uncertainty_band",
            ],
            parameter_payload={
                "weights": {
                    "w_I": 0.15,
                    "w_V": 0.25,
                    "w_R": 0.25,
                    "w_X": 0.10,
                    "w_D": 0.10,
                    "w_U": 0.15,
                },
                "caps": {
                    "I_cap": 60,
                    "V_cap": 80,
                    "R_cap": 40,
                    "X_cap": 4,
                    "D_cap": 60,
                },
            },
            threshold_payload={
                "bands": [
                    {"label": "low", "min_inclusive": 0.0, "max_exclusive": 0.25},
                    {"label": "moderate", "min_inclusive": 0.25, "max_exclusive": 0.50},
                    {"label": "high", "min_inclusive": 0.50, "max_exclusive": 0.75},
                    {"label": "critical", "min_inclusive": 0.75, "max_inclusive": 1.0},
                ]
            },
        )
        _create_phase6_input_bundle(
            session,
            bindings,
            {
                "implementation_minutes": 30,
                "verification_minutes": 40,
                "rework_minutes": 10,
                "interruption_count": 2,
                "downstream_fix_minutes": 15,
                "uncertainty_band": "moderate",
            },
        )
        return bindings

    def assertions(base_url: str, bindings):
        request_body = _execution_request(bindings, lane_evaluation_id="http-exec-vb-001").model_dump(mode="json")
        status, payload = _request(
            "POST",
            f"{base_url}/api/v1/forgemath/lane-executions",
            request_body,
        )

        assert status == 201
        assert payload["lane_evaluation_id"] == "http-exec-vb-001"
        assert payload["evaluation"]["output_values"][0]["numeric_value"] == "0.39"
        assert payload["evaluation"]["factor_values"][0]["raw_value"] == "30"
        assert payload["evaluation"]["factor_values"][0]["normalized_value"] == "0.5"
        assert payload["evaluation"]["factor_values"][0]["weighted_value"] == "0.075"

    _run_http_integration(seed, assertions)


def test_lane_execution_route_rejects_duplicate_active_current_truth_without_supersession():
    def seed(session):
        bindings = _seed_execution_bindings(
            session,
            lane_id="verification_burden",
            variable_names=[
                "implementation_minutes",
                "verification_minutes",
                "rework_minutes",
                "interruption_count",
                "downstream_fix_minutes",
                "uncertainty_band",
            ],
            parameter_payload={
                "weights": {
                    "w_I": 0.15,
                    "w_V": 0.25,
                    "w_R": 0.25,
                    "w_X": 0.10,
                    "w_D": 0.10,
                    "w_U": 0.15,
                },
                "caps": {
                    "I_cap": 60,
                    "V_cap": 80,
                    "R_cap": 40,
                    "X_cap": 4,
                    "D_cap": 60,
                },
            },
            threshold_payload={
                "bands": [
                    {"label": "low", "min_inclusive": 0.0, "max_exclusive": 0.25},
                    {"label": "moderate", "min_inclusive": 0.25, "max_exclusive": 0.50},
                    {"label": "high", "min_inclusive": 0.50, "max_exclusive": 0.75},
                    {"label": "critical", "min_inclusive": 0.75, "max_inclusive": 1.0},
                ]
            },
        )
        _create_phase6_input_bundle(
            session,
            bindings,
            {
                "implementation_minutes": 30,
                "verification_minutes": 40,
                "rework_minutes": 10,
                "interruption_count": 2,
                "downstream_fix_minutes": 15,
                "uncertainty_band": "moderate",
            },
        )
        return bindings

    def assertions(base_url: str, bindings):
        first_request = _execution_request(bindings, lane_evaluation_id="http-exec-vb-dup-001").model_dump(mode="json")
        second_request = _execution_request(bindings, lane_evaluation_id="http-exec-vb-dup-002").model_dump(mode="json")

        first_status, _ = _request(
            "POST",
            f"{base_url}/api/v1/forgemath/lane-executions",
            first_request,
        )
        assert first_status == 201

        second_status, second_payload = _request(
            "POST",
            f"{base_url}/api/v1/forgemath/lane-executions",
            second_request,
        )
        assert second_status == 400
        assert "active governed_canonical_execution evaluation already exists" in json.dumps(second_payload)

    _run_http_integration(seed, assertions)


def test_lane_execution_route_rejects_caller_supplied_execution_mode():
    def seed(session):
        bindings = _seed_execution_bindings(
            session,
            lane_id="verification_burden",
            variable_names=[
                "implementation_minutes",
                "verification_minutes",
                "rework_minutes",
                "interruption_count",
                "downstream_fix_minutes",
                "uncertainty_band",
            ],
            parameter_payload={
                "weights": {
                    "w_I": 0.15,
                    "w_V": 0.25,
                    "w_R": 0.25,
                    "w_X": 0.10,
                    "w_D": 0.10,
                    "w_U": 0.15,
                },
                "caps": {
                    "I_cap": 60,
                    "V_cap": 80,
                    "R_cap": 40,
                    "X_cap": 4,
                    "D_cap": 60,
                },
            },
            threshold_payload={
                "bands": [
                    {"label": "low", "min_inclusive": 0.0, "max_exclusive": 0.25},
                    {"label": "moderate", "min_inclusive": 0.25, "max_exclusive": 0.50},
                    {"label": "high", "min_inclusive": 0.50, "max_exclusive": 0.75},
                    {"label": "critical", "min_inclusive": 0.75, "max_inclusive": 1.0},
                ]
            },
        )
        _create_phase6_input_bundle(
            session,
            bindings,
            {
                "implementation_minutes": 30,
                "verification_minutes": 40,
                "rework_minutes": 10,
                "interruption_count": 2,
                "downstream_fix_minutes": 15,
                "uncertainty_band": "moderate",
            },
        )
        return bindings

    def assertions(base_url: str, bindings):
        request_body = _execution_request(bindings, lane_evaluation_id="http-exec-vb-extra-001").model_dump(
            mode="json"
        )
        request_body["execution_mode"] = "manual_override_attempt"
        status, payload = _request(
            "POST",
            f"{base_url}/api/v1/forgemath/lane-executions",
            request_body,
        )

        assert status == 422
        assert "extra_forbidden" in json.dumps(payload)

    _run_http_integration(seed, assertions)
