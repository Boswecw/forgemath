## 2. Architecture

The implemented architecture is a single FastAPI service backed by
SQLAlchemy models and Alembic migrations, with Phase 1 governance,
Phase 2 evaluation persistence, Phase 3 lifecycle control,
Phase 4 runtime admission control,
Phase 5 read-model composition,
Phase 6 bounded lane execution,
and two hardening slices that tighten authority boundaries,
canonical numeric persistence, active execution lineage, persistence-level
current-truth exclusivity, determinism-sensitive migration metadata, and
runtime-recovery inspection inside one canonical service boundary.

### 2.1 High-Level Flow

```text
Client
  -> FastAPI route
  -> route-specific governed service
  -> fail-closed validation, lifecycle derivation, runtime admission derivation,
     projection composition, or bounded execution derivation
  -> SQLAlchemy session
  -> canonical governance/evaluation/lifecycle tables
```

### 2.2 Module Boundaries

| Layer | Files | Responsibility |
|------|-------|----------------|
| API | `app/api/registry_router.py`, `app/api/evaluation_router.py` | Governance, manual non-computed ingest, lifecycle, runtime-admission, projection read, and execution routes |
| Schemas | `app/schemas/governance.py`, `app/schemas/evaluation.py`, `app/schemas/execution.py`, `app/schemas/execution_contracts.py`, `app/schemas/projection.py` | Write DTOs, canonical reads, supported-lane payload contracts, execution contracts, and projection DTOs |
| Services | `app/services/registry_service.py`, `app/services/evaluation_service.py`, `app/services/lifecycle_service.py`, `app/services/runtime_admission_service.py`, `app/services/execution_service.py`, `app/services/projection_service.py` | Fail-closed governed writes, authority-boundary enforcement, canonical artifact hashing, lifecycle validation, runtime admission and recovery, bounded lane execution, and projection composition |
| Persistence | `app/models/governance.py`, `app/models/evaluation.py` | Canonical registry, evaluation, lifecycle, runtime-admission, and durability ORM models |
| Migrations | `alembic/versions/20260402_0001_phase1_foundation.py` through `20260403_0006_phase7_durability_and_control_hardening.py` | Database schema authority |
