## 15. Handover / Migration Notes

### 15.1 Governing Inputs

The repo is grounded by these documents:

- `bds_ai_assisted_development_operations_protocol.md`
- `BDS_DOCUMENTATION_PROTOCOL_v1.md`
- `vscode_forgemath_initial_implementation_prompt_and_plan.md`
- `forge_math_canonical_equation_stack_top_level_overview.md`
- `forge_math_canonical_equation_specification_v_1_initial.md`
- `forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md`

### 15.2 Qualification Posture

The authoritative verification path is `.github/workflows/ci.yml` plus the
commands in §14. CI installs dependencies, applies every migration to a clean
temporary SQLite database, runs the complete suite with the pinned
ForgeLineage SDK, validates both health modes, assembles and validates canonical
documentation, and fails on generated-document drift.

Test counts are dated evidence rather than system truth. Re-run the complete
command and record the observed pass/skip result in the pull request. The only
documented environment-dependent tests are localhost HTTP tests when socket
binding is prohibited and the Postgres schema invariant when
`FORGEMATH_POSTGRES_TEST_URL` is absent.

The `forgemath_projection_records` table described by an earlier contract is
not implemented. Current projections are intentional ephemeral read models in
`projection_service.py` and do not own truth.

### 15.3 Deferred Work

- `forgemath_projection_records` persistence table (contract §11) — projections currently ephemeral
- compatibility resolution engine beyond bounded validation and persisted binding checks
- runtime admission evolution beyond bounded deterministic validation and persisted evidence
- replay workers and queue processors
- stale-state automation engine
- execution expansion beyond `verification_burden`, `recurrence_pressure`, and `exposure_factor`
- hybrid gate execution and broader multi-lane orchestration
- broader database-level exclusion or partitioning strategies if future execution expansion outgrows the current unique active execution key
- a locked or constraints-based resolution for the currently ranged Pydantic and JSON Schema dependencies
- operational deployment evidence, branch-protection policy, and external-service readiness, which remain outside this repository change
