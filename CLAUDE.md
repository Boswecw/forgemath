# ForgeMath (MAT) — Claude Code Context

Fail-closed governed registry authority: append-only versioned canonical records. A canonical
authority subsystem, **not a helper library**.

Canonical reference: `doc/MATSYSTEM.md`, assembled from `doc/system/` via `bash doc/system/BUILD.sh`.

---

## Boundaries

- **Append-only lineage.** Never mutate a persisted payload field in place; only lifecycle closure
  fields may change. Enforced at the session layer by `app/services/immutability.py`.
- **Fail closed** when required bindings, versions, or deterministic posture are missing.
- Write schemas stay separate from read models, and **a read model is never source truth**.
- **Do not implement formula execution or invent formula semantics in this repo phase.**
- Phase 1 stays local to repo-owned truth — there is no runtime integration with DataForge or any
  other Forge service yet. Compatibility, replay, and engine execution semantics are deferred.

---

## Verification

```bash
alembic upgrade head && python -m pytest tests -q
```

That is `.github/workflows/ci.yml`. Coverage must keep route-level contract translation,
immutability enforcement, deterministic runtime admission, and version lineage green.

Migration or schema doc updates land in the same change as a canonical table or route contract
change.

```bash
./scripts/context-bundle.sh --preset foundation|api|schema
```
