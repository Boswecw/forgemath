# bds · ForgeMath

> **System identity — bds family (Boswell Digital Solutions business system, local-systems tier).**
> ForgeMath is the Forge ecosystem's canonical math and rule authority surface, operated as a business/backend local system under `ecosystem/local-systems`.
> **Purpose:** canonical, deterministic math and rule-evaluation authority — governance registries, canonical evaluation persistence, and lifecycle-governed execution — for the Forge ecosystem.

ForgeMath is the Forge ecosystem's canonical math and rule authority surface.

It has two distinct runtime entry points:

- the FastAPI service for governance registries, canonical persistence, lifecycle, runtime admission, projections, and bounded execution;
- the file-in/file-out Evaluation Spine CLI (`python -m app.evaluation_spine_cli`), with default-off, opt-in ForgeLineage emission to DataForge-Local.

Forge_Command consumes the lightweight `python -m app.health_cli` producer probe. That command does not claim database or FastAPI readiness; use `python -m app.health_cli --readiness` against an existing migrated database for the explicit local readiness surface.

Current implemented repo truth:
- Phase 1 governance registries and immutable version sequencing
- Phase 2 canonical evaluation persistence
- Phase 3 lifecycle governance for replay, stale posture, recomputation, and supersession lineage
- Phase 4 deterministic runtime admission persistence and validation
- Phase 5 projection DTO and read-model inspection surfaces
- bounded canonical execution for numeric lanes `verification_burden`, `recurrence_pressure`, `exposure_factor`, and `priority_score`, plus the `reviewability` hybrid gate
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
- execution beyond the five governed bounded lanes
- arbitrary caller-supplied expression evaluation or general symbolic algebra
- replay workers, stale-state automation, or queue processors
- broader multi-lane orchestration beyond the registered lane-local execution contracts
- projection persistence or downstream UI surfaces

Current documentation authority:
- [doc/MATSYSTEM.md](doc/MATSYSTEM.md) is the assembled, canonical repo-truth reference (canonical artifacts carry the three-letter `MAT` designator)
- `contracts/research/` contains non-runtime receipt and signed equation-package research schemas; they do not activate math or verify signatures
- completed Phase 1–7 implementation plans are archived under `Drive/Forge/Plans/Implemented/forgemath`: https://drive.google.com/file/d/1OYXg7vOGjZmIiuaxl1d4nDK-_wgvsMfu/view
- remaining `docs/*.md` files are active design references or historical context; canonical system truth stays in `doc/MATSYSTEM.md`
- archive SHA-256: `0c5b34c7b6712fdb452e6ec6a992ff273be51d75e3aa18ec5c85b598e2960b97`

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8011
python -m pytest tests -q
python -m app.health_cli
python -m app.health_cli --readiness
bash doc/system/BUILD.sh
bash doc/system/validate_snapshots.sh
```

The complete lineage tests require the ForgeLineage SDK revision pinned by CI on `PYTHONPATH`. The Postgres schema invariant test skips unless `FORGEMATH_POSTGRES_TEST_URL` is configured.
