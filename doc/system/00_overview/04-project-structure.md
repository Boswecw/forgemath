## 4. Project Structure

### 4.1 Directory Map

```text
ForgeMath/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   └── services/
├── contracts/
│   └── research/
├── doc/
│   └── system/
├── docs/
├── scripts/
└── tests/
```

### 4.2 File Conventions

| Pattern | Meaning |
|--------|---------|
| `app/models/*.py` | Canonical table ownership |
| `app/schemas/*.py` | Request/read contract types |
| `app/services/*.py` | Business rules and invariants |
| `contracts/research/*` | Non-runtime JSON Schemas and fixtures for bounded contract research |
| `doc/system/*.md` | Modular SYSTEM source files |
| `docs/*.md` | Architecture, roadmap, and module specs |

