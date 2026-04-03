# ForgeMath Governance Foundation Module Spec

> Legacy Phase 1 module-spec artifact. Current repo truth is maintained in
> [SYSTEM.md](/home/charlie/Forge/ecosystem/ForgeMath/SYSTEM.md).

**Date:** April 2, 2026  
**Time:** America/Kentucky/Louisville  
**Intended destination:** `ForgeMath/docs/forgemath_governance_foundation_module_spec.md`

---

## Purpose

This module spec covers the Phase 1 governance foundation implemented in the repo.

## Scope

The module owns:

- registry create/list/get APIs
- immutable version sequencing
- runtime profile admission rules
- scope declarations
- migration package metadata

It does not own:

- formula execution
- replay orchestration
- evaluation persistence
- projection persistence

## Route Contract

All routes live under `/api/v1/forgemath/governance`.

| Family | Create | List | Version detail |
|--------|--------|------|----------------|
| Lane specs | `POST /lane-specs` | `GET /lane-specs` | `GET /lane-specs/{lane_id}/versions/{version}` |
| Variable registries | `POST /variable-registries` | `GET /variable-registries` | `GET /variable-registries/{variable_registry_id}/versions/{version}` |
| Parameter sets | `POST /parameter-sets` | `GET /parameter-sets` | `GET /parameter-sets/{parameter_set_id}/versions/{version}` |
| Threshold sets | `POST /threshold-sets` | `GET /threshold-sets` | `GET /threshold-sets/{threshold_set_id}/versions/{version}` |
| Policy bundles | `POST /policy-bundles` | `GET /policy-bundles` | `GET /policy-bundles/{policy_bundle_id}/versions/{version}` |
| Runtime profiles | `POST /runtime-profiles` | `GET /runtime-profiles` | `GET /runtime-profiles/{runtime_profile_id}/versions/{version}` |
| Scopes | `POST /scopes` | `GET /scopes` | `GET /scopes/{scope_id}/versions/{version}` |
| Migration packages | `POST /migration-packages` | `GET /migration-packages` | `GET /migration-packages/{migration_id}/versions/{version}` |

## Invariants

- first version must be `1`
- later versions must be sequential
- supersession must name the immediately previous version
- superseding an active version requires a retirement reason
- payloads are immutable once persisted
- canonical runtime profiles reject `non_determinism_allowed_flag = true`
