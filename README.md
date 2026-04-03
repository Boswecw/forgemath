# ForgeMath

ForgeMath is the Forge ecosystem's canonical math and rule authority surface.
This repo implements Phase 1 only: governed vocabulary freezing, immutable
registry foundations, deterministic runtime profiles, scope declarations, and
migration package persistence. It does not implement the math engine.

## Phase 1 Scope

- Freeze governed status vocabularies and the compatibility tuple contract.
- Persist versioned lane specs, variable registries, parameter sets,
  threshold sets, policy bundles, runtime profiles, scopes, and migration
  packages.
- Enforce append-only lineage for canonical governance objects.
- Fail closed when required Phase 1 bindings are missing or invalid.
- Keep API request models and read models separate from canonical tables.

## Non-Goals

- Lane execution or formula evaluation
- Projection/read-model persistence for canonical results
- Replay workers, state machines, or operator orchestration
- Formula semantics beyond the contract payloads supplied to registries

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

