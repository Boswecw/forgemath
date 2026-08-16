# ForgeMath (MAT) — Claude Code context

Read and follow `AGENTS.md`. Canonical system truth is authored under `doc/system/` and assembled to `doc/MATSYSTEM.md` with `bash doc/system/BUILD.sh`; never hand-edit the generated file.

## Boundaries

- Preserve append-only governed payloads and supersession lineage. Only lifecycle fields declared mutable by `app/services/immutability.py` may change after persistence.
- Fail closed for missing, inactive, incompatible, cross-lane, or non-deterministic bindings. Projections and read models are not source truth.
- Canonical numeric work stays in deterministic `Decimal` arithmetic and persists as decimal strings.
- Computed canonical truth enters through governed `POST /lane-executions`; `POST /lane-evaluations` is limited to non-computed manual historical/audit ingest.
- The supported FastAPI execution lanes are exactly `verification_burden`, `recurrence_pressure`, and `exposure_factor`. Do not add lanes or change formulas, weights, thresholds, rounding, quantization, or golden vectors without separate authority.
- Never add arbitrary caller-supplied expression execution or broaden ForgeMath into a symbolic-algebra or general policy engine.

## Surfaces

- FastAPI owns governance, evaluation, lifecycle, runtime-admission, projection, and bounded execution routes.
- `python -m app.evaluation_spine_cli` is a separate file-based Evaluation Spine authority.
- ForgeLineage emission to DataForge-Local is opt-in via `FORGEMATH_LINEAGE_URL`, default-off, and non-blocking. Forge_Command consumes `python -m app.health_cli` and may walk emitted artifact references; this repo does not own either external service.
- `python -m app.health_cli --readiness` is non-destructive and may inspect only an existing configured database.

## Gates

Run the exact qualification commands in `AGENTS.md`. Schema changes require a new Alembic migration plus matching model, contract, test, and canonical-doc updates. A change is not complete until tests, health contracts, migrations, document assembly, snapshot validation, and generated-doc drift checks pass with mathematical semantics unchanged.
