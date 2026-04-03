# ForgeMath

ForgeMath is the Forge ecosystem's canonical math and rule authority surface.

Current implemented repo truth:
- Phase 1 governance registries and immutable version sequencing
- Phase 2 canonical evaluation persistence
- Phase 3 lifecycle governance for replay, stale posture, recomputation, and supersession lineage
- Phase 4 deterministic runtime admission persistence and validation
- Phase 5 projection DTO and read-model inspection surfaces
- Phase 6 bounded canonical execution for `verification_burden`, `recurrence_pressure`, and `exposure_factor`
- authority-boundary and canonical numeric hardening for manual ingest, derived output hashes, and active execution lineage control
- Phase 7 durability and lifecycle-control hardening for persistence-level active canonical execution exclusivity, determinism-sensitive migration metadata, runtime recovery posture inspection, and stricter supersession safety

Current hardening posture:
- `POST /lane-evaluations` is limited to governed manual ingest for non-computed historical records
- canonical computed truth is expected to enter through `POST /lane-executions`
- canonical execution mode is server-owned and may not be caller-supplied on the execution route
- canonical numeric artifacts persist as deterministic decimal strings, not floats
- `raw_output_hash` is derived from the persisted canonical output/factor/trace artifact bundle
- optional prior/decay compatibility bindings must resolve when present
- supported parameter and threshold payloads fail closed when topology or semantic constraints are invalid
- duplicate active canonical execution truth for the same execution context fails closed unless explicit supersession is declared
- determinism-sensitive migration packages must declare affected deterministic artifacts and may not claim hard-compatible posture
- runtime admission inspection surfaces explicit recovery posture, action, and operator-review guidance when a bound runtime profile is missing, incomplete, non-deterministic, or retired

Current non-goals:
- full lane math engine beyond the bounded Phase 6 lane wave
- replay workers, stale-state automation, or queue processors
- hybrid-gate execution rollout
- projection persistence or downstream UI surfaces

Current documentation authority:
- [SYSTEM.md](/home/charlie/Forge/ecosystem/ForgeMath/SYSTEM.md) is the assembled repo-truth reference
- `docs/*.md` files are retained as historical planning artifacts unless explicitly updated to current state

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8011
pytest
```
