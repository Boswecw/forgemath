## 5. Configuration & Environment

### 5.1 Environment Variables

| Variable | Type | Default | Read by |
|---------|------|---------|---------|
| `FORGEMATH_DATABASE_URL` | string | `sqlite:///./forgemath.db` | `app/config.py`, `app/database.py`, `alembic/env.py` |
| `FORGEMATH_HOST` | string | `127.0.0.1` | `app/config.py` |
| `FORGEMATH_PORT` | integer | `8011` | `app/config.py` |
| `FORGEMATH_LINEAGE_URL` | URL | unset (disabled) | `app/lineage/spine_emit.py`, readiness configuration check |
| `FORGEMATH_LINEAGE_TOKEN` | string | unset | `app/lineage/spine_emit.py`, readiness configuration check |

### 5.2 Validation Rules

- database URL must not be empty
- host must not be empty
- port must be between `1` and `65535`
- a configured lineage URL must be an absolute HTTP(S) URL
- a lineage token without a lineage URL is a degraded configuration

### 5.3 Health Modes

- `python -m app.health_cli` checks only Evaluation Spine authority and contract
  imports. Database, migrations, FastAPI construction, lane registration, and
  lineage transport are explicitly reported as not checked.
- `python -m app.health_cli --readiness` validates configuration, connects to an
  existing configured database, compares its Alembic revision with repository
  heads, constructs FastAPI, verifies the exact supported lane set, and checks
  optional lineage URL and SDK availability when enabled. It never creates a database, applies a
  migration, sends lineage, mutates truth, or contacts an unconfigured service.

