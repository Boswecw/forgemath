## 1. Overview & Philosophy

ForgeMath is a backend-only canonical authority service for governed lane math.
The current repository state implements Phase 1 only: vocabulary freezing,
versioned registry truth, deterministic runtime profile admission, scope
declaration, and migration metadata.

### 1.1 Core Principles

- Canonical truth is append-only and versioned.
- Registry payloads do not mutate in place.
- Read models are not canonical truth.
- Missing required bindings fail closed.
- Runtime determinism is enforced, not assumed.
- Formula execution is deferred until the substrate is stable.

### 1.2 Current Product Boundary

| Area | Current status |
|------|----------------|
| Governance registries | Implemented |
| Runtime profile persistence | Implemented |
| Scope registry | Implemented |
| Migration package metadata | Implemented |
| Lane execution | Not implemented |
| Evaluation persistence | Not implemented |
| Replay orchestration | Not implemented |

