## 14. Testing Infrastructure

### 14.1 Current Test Coverage

| Test file | Coverage |
|----------|----------|
| `tests/test_phase1_api.py` | Route-function contract coverage and HTTP error translation |
| `tests/test_phase1_invariants.py` | Immutability, supersession lineage, compatibility tuple hash stability |
| `tests/test_phase2_api.py` | Canonical evaluation write/read coverage and fail-closed compatibility checks |
| `tests/test_phase2_invariants.py` | Frozen input bundle immutability checks |
| `tests/test_phase3_lifecycle.py` | Lifecycle inspection, stale/replay transitions, and lineage visibility |
| `tests/test_phase4_runtime_admission.py` | Deterministic runtime admission persistence, inspection, and fail-closed invalid profile checks |
| `tests/test_phase5_projections.py` | Projection metadata, truth-preserving summary/detail/factor/trace/replay reads, and fail-closed missing-source checks |
| `tests/test_phase6_execution.py` | Supported lane execution happy paths and fail-closed missing-binding, missing-input, unsupported-lane, and runtime-profile execution checks |
| `tests/test_http_contracts.py` | Real HTTP route checks for manual-ingest boundary and execution route behavior when the environment allows localhost binding |
| `tests/test_postgres_invariants.py` | Postgres-backed migration/schema invariant checks when `FORGEMATH_POSTGRES_TEST_URL` is supplied |

### 14.2 Execution

```bash
python -m pytest tests -q
FORGEMATH_DATABASE_URL=sqlite:///./hardening_verify.db alembic upgrade head
```

### 14.3 Test Boundary

The current suite validates Phase 1 through Phase 6 write logic and invariants.
It also validates the hardening slice for:

- manual-ingest boundary restriction
- derived raw-output hashing
- lane-affinity binding checks
- deterministic decimal-string artifact persistence
- active canonical execution conflict handling

HTTP route checks and Postgres-backed invariant checks are present but may skip in
restricted environments that block localhost binding or do not provide a Postgres URL.
