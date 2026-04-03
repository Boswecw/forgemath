## 9. Backend

### 9.1 Service Responsibilities

| File | Responsibility |
|------|----------------|
| `app/services/registry_service.py` | create/list/get logic, version sequencing, supersession closure |
| `app/services/evaluation_service.py` | canonical evaluation persistence, manual-ingest boundary enforcement, canonical artifact hashing, trace, replay queue, and incident persistence |
| `app/services/lifecycle_service.py` | replay/stale/recomputation validation, supersession lifecycle control, lineage reads |
| `app/services/runtime_admission_service.py` | deterministic runtime validation, runtime certificate derivation, runtime admission inspection |
| `app/services/execution_service.py` | bounded canonical execution for supported Phase 6 lanes, supported-lane contract validation, and active execution lineage control |
| `app/services/projection_service.py` | governed projection/read-model composition over canonical truth |
| `app/services/immutability.py` | session-level protection against payload mutation |
| `app/models/governance.py` | versioned governance tables |
| `app/models/evaluation.py` | canonical evaluation, lifecycle, and runtime-admission tables |
| `app/database.py` | engine and session factory |

### 9.2 Backend Invariants

- first version must be `1`
- later versions must be sequential
- superseding an active version requires `retired_reason`
- canonical evaluations require frozen input, runtime profile, and full compatibility binding
- canonical evaluations persist explicit deterministic runtime admission truth
- canonical admission fails closed when runtime profile fields are incomplete
- canonical admission fails closed when runtime profile is retired or non-deterministic
- manual ingest may not persist computed canonical truth, caller-supplied output bundles, or caller-supplied output hashes
- canonical execution mode is server-owned on the execution route and may not be caller-supplied
- raw_output_hash is derived from the persisted canonical output/factor/trace artifact bundle
- trace bundle hashing excludes storage ids so identical reruns preserve stable canonical artifact hashes
- parameter, threshold, and policy bindings must match the evaluation lane when those records declare a lane binding
- optional prior and decay compatibility bindings must resolve when present
- canonical numeric output/factor values persist as deterministic decimal strings rather than floats
- output field names and factor names are unique per evaluation
- output and factor DTOs fail closed when computed rows are semantically incomplete
- bounded execution supports only governed Phase 6 lanes and canonical_numeric lane family
- bounded execution fails closed when variable, parameter, threshold, policy, runtime, or input bindings are missing or inactive
- bounded execution fails closed when supported parameter payloads or threshold topologies violate the bounded execution contract
- bounded execution persists through the existing evaluation service and does not bypass canonical truth tables
- bounded execution emits inspectable factor rows and tier_1_full trace events for supported lanes
- bounded execution fails closed when an active canonical execution already exists for the same execution context unless explicit supersession is declared
- repeat execution over the same governed context preserves stable output, factor, trace, and raw-output hashing when lineage supersession is explicit
- projection routes are read-only and derive metadata from canonical compatibility bindings
- projection composition fails closed when source evaluation or source trace truth is missing
- replay posture fails closed when required bindings are missing
- stale posture may not be downgraded or silently reset to fresh
- supersession preserves visibility and records append-only lifecycle events
- only governed lifecycle fields may change after persisted evaluation creation
- canonical runtime profiles reject non-deterministic admission
