## 9. Backend

### 9.1 Service Responsibilities

| File | Responsibility |
|------|----------------|
| `app/services/registry_service.py` | create/list/get logic, version sequencing, supersession closure |
| `app/services/immutability.py` | session-level protection against payload mutation |
| `app/models/governance.py` | versioned canonical tables |
| `app/database.py` | engine and session factory |

### 9.2 Backend Invariants

- first version must be `1`
- later versions must be sequential
- superseding an active version requires `retired_reason`
- only lifecycle closure fields may change after persistence
- canonical runtime profiles reject non-deterministic admission

