## 2. Architecture

The implemented Phase 1 architecture is a single FastAPI service backed by
SQLAlchemy models and Alembic migrations.

### 2.1 High-Level Flow

```text
Client
  -> FastAPI route
  -> registry service
  -> validation + version sequencing
  -> SQLAlchemy session
  -> canonical Phase 1 tables
```

### 2.2 Module Boundaries

| Layer | Files | Responsibility |
|------|-------|----------------|
| API | `app/api/registry_router.py` | Route contract and HTTP error translation |
| Schemas | `app/schemas/governance.py` | Request DTOs, read DTOs, compatibility tuple freeze |
| Services | `app/services/registry_service.py` | Fail-closed creation logic and supersession sequencing |
| Persistence | `app/models/governance.py` | Canonical Phase 1 ORM models |
| Migrations | `alembic/versions/20260402_0001_phase1_foundation.py` | Database schema authority |

