## 8. API Layer

Implemented routes live under `/api/v1/forgemath/governance` and `/api/v1/forgemath`.

### 8.1 Health Route

| Method | Path | Purpose |
|-------|------|---------|
| `GET` | `/health` | Service health and phase marker |

### 8.2 Governance Routes

| Family | Create | List | Get version |
|-------|--------|------|-------------|
| Lane specs | `POST /lane-specs` | `GET /lane-specs` | `GET /lane-specs/{lane_id}/versions/{version}` |
| Variable registries | `POST /variable-registries` | `GET /variable-registries` | `GET /variable-registries/{variable_registry_id}/versions/{version}` |
| Parameter sets | `POST /parameter-sets` | `GET /parameter-sets` | `GET /parameter-sets/{parameter_set_id}/versions/{version}` |
| Threshold sets | `POST /threshold-sets` | `GET /threshold-sets` | `GET /threshold-sets/{threshold_set_id}/versions/{version}` |
| Policy bundles | `POST /policy-bundles` | `GET /policy-bundles` | `GET /policy-bundles/{policy_bundle_id}/versions/{version}` |
| Runtime profiles | `POST /runtime-profiles` | `GET /runtime-profiles` | `GET /runtime-profiles/{runtime_profile_id}/versions/{version}` |
| Scopes | `POST /scopes` | `GET /scopes` | `GET /scopes/{scope_id}/versions/{version}` |
| Migration packages | `POST /migration-packages` | `GET /migration-packages` | `GET /migration-packages/{migration_id}/versions/{version}` |

### 8.3 Evaluation Routes

| Family | Create | List | Get |
|-------|--------|------|-----|
| Input bundles | `POST /input-bundles` | `GET /input-bundles` | `GET /input-bundles/{input_bundle_id}` |
| Lane evaluations | `POST /lane-evaluations` | `GET /lane-evaluations` | `GET /lane-evaluations/{lane_evaluation_id}` |
| Replay queue events | `POST /replay-queue-events` | `GET /replay-queue-events` | `GET /replay-queue-events/{replay_event_id}` |
| Incident records | `POST /incidents` | `GET /incidents` | `GET /incidents/{incident_id}` |

`POST /lane-evaluations` is now restricted to governed manual ingest for
non-computed historical records. Canonical computed truth is expected to enter
through `POST /lane-executions`.

### 8.4 Execution Routes

| Family | Action | Path |
|-------|--------|------|
| Bounded canonical execution | `POST` | `/lane-executions` |

### 8.5 Lifecycle Routes

| Family | Action | Path |
|-------|--------|------|
| Lifecycle inspection | `GET` | `/lane-evaluations/{lane_evaluation_id}/lifecycle` |
| Lifecycle transition | `POST` | `/lane-evaluations/{lane_evaluation_id}/lifecycle-transitions` |
| Lineage inspection | `GET` | `/lane-evaluations/{lane_evaluation_id}/lineage` |

### 8.6 Runtime Admission Routes

| Family | Action | Path |
|-------|--------|------|
| Runtime admission inspection | `GET` | `/lane-evaluations/{lane_evaluation_id}/runtime-admission` |

Runtime-admission inspection returns both persisted admission truth and derived
runtime-recovery posture when the bound runtime profile is missing, incomplete,
non-deterministic, or retired.

### 8.7 Projection Routes

| Family | Action | Path |
|-------|--------|------|
| Evaluation summary projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/summary` |
| Evaluation detail projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/detail` |
| Factor inspection projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/factors` |
| Trace inspection projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/trace` |
| Replay diagnostic projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/replay-diagnostics` |
