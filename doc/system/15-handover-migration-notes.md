## 15. Handover / Migration Notes

### 15.1 Governing Inputs

The repo is grounded by these documents:

- `bds_ai_assisted_development_operations_protocol.md`
- `BDS_DOCUMENTATION_PROTOCOL_v1.md`
- `vscode_forgemath_initial_implementation_prompt_and_plan.md`
- `forge_math_canonical_equation_stack_top_level_overview.md`
- `forge_math_canonical_equation_specification_v_1_initial.md`
- `forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md`

### 15.2 Completed Hardening (Gap-Closure Pass, 2026-04-04)

Gap-closure hardening pass completed against `forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md`. Six gaps were identified and closed:

| Gap | Resolution |
|-----|------------|
| No per-factor golden-vector pinning | `tests/test_golden_vectors.py`: pins raw/normalized/weighted per factor for verification_burden |
| No trace summary format stability test | `tests/test_golden_vectors.py`: pins _decimal_to_str output for known edge values |
| No _clamp_unit > 1.0 path exercised | `tests/test_golden_vectors.py`: exposure_factor with alpha_pub=1.0 + severity="critical" → score 1.25 → clamped 1.0 |
| No variable registry coverage check test | `tests/test_phase6_execution.py`: registry exists but payload.variables insufficient → 400 |
| No stale_input_invalidated positive path | `tests/test_phase3_lifecycle.py`: successful transition with input_bundle_invalidated=True |
| No stale_upstream_changed positive path | `tests/test_phase3_lifecycle.py`: successful transition after variable registry supersession |

**Baseline:** 57 passing tests. **After this hardening pass:** 63 passing tests.

The 4 failures in `test_http_contracts.py` are **not** a DataForge dependency: that module starts a uvicorn subprocess through a hardcoded `PYTHON_BIN` interpreter path, so it fails on any host where that path is absent. They are environment/harness failures, not governance regressions.

**Current suite (2026-06-08):** `python -m pytest tests -q --ignore=tests/lineage` → 72 passing, 1 skipped, 4 failing (the `test_http_contracts.py` cases above). A bare `python -m pytest tests -q` currently aborts during collection because `tests/lineage/` imports the external `forge_lineage_sdk`, which is not in `requirements.txt`.

**Remaining open gap from contract audit:** `forgemath_projection_records` table (contract §11) is not implemented — projections are ephemeral read models in `projection_service.py`. This is architecturally intentional for the current phase and documented as deferred.

### 15.3 Deferred Work

- `forgemath_projection_records` persistence table (contract §11) — projections currently ephemeral
- compatibility resolution engine beyond bounded validation and persisted binding checks
- runtime admission evolution beyond bounded deterministic validation and persisted evidence
- replay workers and queue processors
- stale-state automation engine
- execution expansion beyond the bounded Phase 6 lane wave
- hybrid gate execution and broader multi-lane orchestration
- broader database-level exclusion or partitioning strategies if future execution expansion outgrows the current unique active execution key
- `doc/system/` documentation-scheme consolidation — two chapter numbering schemes currently coexist (the granular content chapters `01-overview-philosophy.md` … `15-handover-migration-notes.md` and the Forge Documentation Protocol v1 skeleton chapters `00-overview.md`, `01-architecture.md`, `10-scope.md`, `20-structure.md`, `30-governance.md`, `40-change-control.md`, `90-appendices.md`). `BUILD.sh` assembles the granular content chapters; consolidating onto one scheme is deferred
- test-harness portability — `tests/test_http_contracts.py` hardcodes `PYTHON_BIN`, and `tests/lineage/` depends on the un-vendored `forge_lineage_sdk`; both should be made environment-independent (e.g. `sys.executable` / guarded optional import)
