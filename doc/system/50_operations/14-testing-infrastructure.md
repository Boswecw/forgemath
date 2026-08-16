## 14. Testing Infrastructure

### 14.1 Current Test Coverage

| Test file | Coverage |
|----------|----------|
| `tests/test_phase1_api.py` | Route-function contract coverage and HTTP error translation |
| `tests/test_phase1_invariants.py` | Immutability, supersession lineage, compatibility tuple hash stability |
| `tests/test_phase2_api.py` | Canonical evaluation write/read coverage, optional compatibility-binding validation, and fail-closed artifact-shape checks |
| `tests/test_phase2_invariants.py` | Frozen input bundle immutability checks |
| `tests/test_phase3_lifecycle.py` | Lifecycle inspection, stale/replay transitions, and lineage visibility |
| `tests/test_phase4_runtime_admission.py` | Deterministic runtime admission persistence, inspection, and fail-closed invalid profile checks |
| `tests/test_phase5_projections.py` | Projection metadata, truth-preserving summary/detail/factor/trace/replay reads, and fail-closed missing-source checks |
| `tests/test_phase6_execution.py` | Supported lane execution happy paths, repeatability/hash-stability checks, and fail-closed missing-binding, missing-input, unsupported-lane, invalid-parameter, invalid-threshold, runtime-profile, and variable-registry insufficient-coverage execution checks |
| `tests/test_phase7_hardening.py` | Persistence-level active canonical execution exclusivity, determinism-sensitive migration package validation, runtime-recovery inspection, and supersession hardening checks |
| `tests/test_golden_vectors.py` | Per-factor raw/normalized/weighted value pinning for verification_burden; trace summary format stability (_decimal_to_str edge cases); _clamp_unit saturation at unit ceiling via exposure_factor with saturating coefficient inputs |
| `tests/test_property_invariants.py` | Hypothesis-generated decimal serialization, formula bounds and monotonicity, replay posture, lifecycle severity, and stateful append-only supersession-chain invariants |
| `tests/test_http_contracts.py` | Real HTTP route checks for manual-ingest boundary, execution route behavior, and caller-supplied execution-mode rejection when the environment allows localhost binding |
| `tests/test_postgres_invariants.py` | Postgres-backed migration/schema invariant checks when `FORGEMATH_POSTGRES_TEST_URL` is supplied |
| `tests/test_evaluation_spine_phase05.py` | Evaluation Spine contract validation, deterministic decimal scoring, file runner, and fail-closed input behavior |
| `tests/lineage/` | ForgeLineage emission, identity-only node posture, upstream discovery, non-blocking failure, and default-off behavior against the pinned SDK |
| `tests/test_health_cli.py` | Lightweight health contract, real version reporting, degraded imports, and optional-lineage readiness posture |

### 14.2 Execution

```bash
FORGEMATH_DATABASE_URL=sqlite:///./qualification.sqlite3 alembic upgrade head
PYTHONPATH=.ci/forge_lineage/sdk python -m pytest tests -q
python -m app.health_cli
FORGEMATH_DATABASE_URL=sqlite:///./qualification.sqlite3 python -m app.health_cli --readiness
bash doc/system/BUILD.sh
bash doc/system/validate_snapshots.sh
git diff --exit-code -- doc/MATSYSTEM.md
```

CI checks out the ForgeLineage SDK at the revision pinned in
`.github/workflows/ci.yml` before running the complete suite. Test database
paths use the host temporary directory so the same suite runs on Windows and
POSIX hosts.

### 14.3 Test Boundary

The current suite validates Phase 1 through Phase 7 write logic and invariants.
It also validates the hardening slices for:

- manual-ingest boundary restriction
- derived raw-output hashing
- lane-affinity binding checks
- optional prior/decay compatibility binding enforcement
- computed output/factor payload shape enforcement
- deterministic decimal-string artifact persistence
- active canonical execution conflict handling
- repeatability and hash stability across explicit superseding reruns
- persistence-level active canonical execution uniqueness
- determinism-sensitive migration package metadata rules
- runtime-profile recovery posture derivation on inspection
- supersession temporal-order and cycle protection
- per-factor golden-vector pinning (raw, normalized, weighted values)
- trace summary format stability (_decimal_to_str output for known inputs)
- _clamp_unit saturation at 1.0 when exposure_factor arithmetic exceeds unit ceiling
- variable registry insufficient coverage rejection (registry present, variables missing)
- stale_input_invalidated positive transition path with input_bundle_invalidated evidence
- stale_upstream_changed positive transition path when upstream registry is superseded
- property-generated decimal serialization round trips without exponent notation
- property-generated formula inputs preserve canonical bounds, determinism, and monotonicity
- property-generated replay postures preserve compatibility and audit-result restrictions
- property-generated lifecycle sequences never reduce stale-state severity
- stateful supersession sequences preserve one active canonical truth and an acyclic append-only lineage chain

HTTP route checks and Postgres-backed invariant checks are present but may skip in
restricted environments that block localhost binding or do not provide a Postgres URL.
The Postgres skip is explicit and reproducible: supply
`FORGEMATH_POSTGRES_TEST_URL` to enable it. CI does not silently ignore any
other test failure.

Exact pass counts are qualification evidence, not canonical facts. Reproduce
the current inventory with the complete command above; PRs record the observed
result and environment at review time instead of preserving stale counts here.
