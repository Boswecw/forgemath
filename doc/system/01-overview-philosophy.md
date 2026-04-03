## 1. Overview & Philosophy

ForgeMath is a backend-only canonical authority service for governed lane math.
The current repository state implements Phase 1 through Phase 7:
versioned governance registries, canonical evaluation persistence,
explicit lifecycle governance for replay, stale posture,
recomputation posture, supersession lineage,
deterministic runtime admission control,
governed projection/read-model inspection surfaces,
and a bounded canonical execution substrate for the initial numeric lane wave.
The current repo state also hardens the authority boundary so manual ingest
cannot mint computed canonical truth, derives canonical output hashes from the
persisted artifact bundle, and stores canonical numeric artifacts as decimal
strings instead of floats. Phase 7 adds persistence-level active canonical
execution exclusivity, determinism-sensitive migration metadata,
runtime-recovery inspection posture, and stricter supersession safety checks.

### 1.1 Core Principles

- Canonical truth is append-only and versioned.
- Registry and persisted evaluation payloads do not mutate in place.
- Read models are not canonical truth.
- Missing required bindings fail closed.
- Runtime determinism is enforced, not assumed.
- Lifecycle posture is explicit, not inferred by downstream consumers.
- Deterministic runtime admission truth is explicit and persisted.
- Projection DTOs are read models only and do not become canonical truth.
- Canonical execution remains bounded to governed supported lanes and fails closed otherwise.
- Manual ingest remains available only for non-computed historical visibility.
- Canonical numeric artifacts persist in deterministic decimal-string form.
- Active canonical execution truth must be explicitly superseded before replacement.
- Persistence-level active canonical execution exclusivity backs the service-level guardrail.
- Determinism-sensitive migrations must declare the deterministic artifacts they affect.
- Runtime-admission reads expose recovery posture when canonical runtime bindings degrade.

### 1.2 Current Product Boundary

| Area | Current status |
|------|----------------|
| Governance registries | Implemented |
| Canonical evaluation persistence | Implemented |
| Lifecycle governance | Implemented |
| Runtime profile persistence | Implemented |
| Runtime admission enforcement | Implemented |
| Runtime recovery posture inspection | Implemented |
| Projection DTO/read-model surfaces | Implemented |
| Bounded lane execution substrate | Implemented |
| Durability and lifecycle-control hardening | Implemented |
| Scope registry | Implemented |
| Migration package metadata | Implemented |
| Broad multi-lane orchestration | Not implemented |
| Replay orchestration workers | Not implemented |
| Stale-state automation engine | Not implemented |
