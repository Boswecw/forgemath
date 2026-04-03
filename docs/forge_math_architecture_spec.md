# ForgeMath Architecture Spec

**Date:** April 2, 2026  
**Time:** America/Kentucky/Louisville  
**Intended destination:** `ForgeMath/docs/forge_math_architecture_spec.md`

---

## Purpose

This architecture spec localizes the governing ForgeMath design into the new repo.
It describes the current repository boundary and Phase 1 implementation posture.

## Authority Boundary

ForgeMath is the canonical authority surface for governed lane math.
Phase 1 does not execute formulas.
Phase 1 establishes the versioned registry and runtime substrate required before canonical evaluation writes are allowed.

## Implemented Phase 1 Modules

| Module | Current responsibility | Notes |
|--------|------------------------|-------|
| Enums and tuple vocabulary | Freeze governed status and compatibility vocabulary | No evaluation engine yet |
| Versioned registries | Persist lane specs, variable registries, parameter sets, threshold sets, policy bundles | Payloads are append-only |
| Runtime profiles | Persist deterministic runtime bindings | Non-deterministic canonical profiles are rejected |
| Scope registry | Persist local/cloud/hybrid scope declarations | Used to prevent a false universal comparison domain |
| Migration packages | Persist migration intent and approval metadata | No executor yet |
| API surface | Create/list/get endpoints for Phase 1 tables | Read models remain separate from tables |
| Immutability guard | Prevent in-place payload mutation | Lifecycle closure only |

## Data Model Posture

Every governed record in Phase 1 is versioned and carries:

- stable identity
- sequential version
- payload hash
- effective time
- supersession metadata
- creation metadata

Supersession creates a new row and closes the prior version through lifecycle fields.
Payload mutation in place is forbidden.

## Non-Goals

- Lane execution
- Compatibility resolution engine
- Replay workers
- Projection persistence
- Incident and evaluation tables
- Policy orchestration or operator approval workflows

## Integration Posture

The repo is intentionally standalone in Phase 1.
It does not currently call other Forge services at runtime.
Downstream ecosystem consumers are expected later, but those integrations remain roadmap items until the canonical substrate is stable.

