## 13. Error Handling Contract

### 13.1 HTTP Status Mapping

| Status | Trigger |
|-------|---------|
| `201` | Successful create |
| `400` | Validation failure in governed service logic |
| `404` | Requested governed version not found |
| `409` | Duplicate or conflicting governed version |
| `422` | FastAPI request-body validation failure |

### 13.2 Error Translation

Route handlers translate governed service exceptions into explicit HTTP failures.
No route silently degrades a missing or incompatible binding into a success path.

### 13.3 Lifecycle Failure Posture

- invalid replay-safe claims fail with `400`
- invalid stale-state downgrades fail with `400`
- lineage conflicts or duplicate supersession links fail with `409`
- missing lifecycle inspection targets fail with `404`

### 13.4 Runtime Admission Failure Posture

- non-deterministic runtime profiles fail canonical admission with `400`
- incomplete runtime profiles fail canonical admission with `400`
- retired runtime profiles fail canonical admission with `400`
- missing evaluation targets for runtime inspection fail with `404`

### 13.5 Projection Failure Posture

- missing source evaluations fail projection reads with `404`
- missing source trace bundles fail trace projection reads with `404`
- missing projection schema bindings fail projection composition with `400`

### 13.6 Execution Failure Posture

- unsupported Phase 6 lanes fail execution with `400`
- missing required input variables fail execution with `400`
- missing governance bindings fail execution with `404`
- runtime profiles outside the supported deterministic Phase 6 substrate fail execution with `400`
- invalid supported-lane parameter semantics or threshold topology fail execution with `400`
- duplicate active canonical execution context without explicit supersession fails with `400`

### 13.7 Authority-Boundary Failure Posture

- manual ingest attempts to persist computed canonical truth fail request validation with `422`
- caller-supplied `execution_mode` on the execution route fails request validation with `422`
- caller-supplied raw_output_hash values that do not match the persisted artifact bundle fail with `400`
- incomplete optional prior/decay compatibility bindings fail request validation with `422`
- cross-lane parameter, threshold, or policy bindings fail with `400`
