## 14. Testing Infrastructure

### 14.1 Current Test Coverage

| Test file | Coverage |
|----------|----------|
| `tests/test_phase1_api.py` | Route-function contract coverage and HTTP error translation |
| `tests/test_phase1_invariants.py` | Immutability, supersession lineage, compatibility tuple hash stability |

### 14.2 Execution

```bash
python -m pytest tests -q
```

### 14.3 Test Boundary

The current suite validates Phase 1 write logic and invariants.
It does not yet cover migration application on a live Postgres instance or any evaluation/replay logic because those phases are not implemented.

