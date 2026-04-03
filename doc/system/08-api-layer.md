## 8. API Layer

All implemented routes live under `/api/v1/forgemath/governance`.

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

