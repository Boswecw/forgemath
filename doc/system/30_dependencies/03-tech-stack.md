## 3. Tech Stack

### 3.1 Runtime Dependencies

| Layer | Dependency | Version |
|------|------------|---------|
| API | FastAPI | `0.109.0` |
| ASGI server | Uvicorn | `0.27.0` |
| ORM | SQLAlchemy | `2.0.36` |
| Migrations | Alembic | `1.13.1` |
| Validation | Pydantic | `>=2.10.0` |
| Database driver | psycopg2-binary | `2.9.10` |
| Environment loading | python-dotenv | `1.0.0` |

### 3.2 Test Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | `7.4.3` | Repo test runner |
| httpx | `0.27.2` | FastAPI-compatible request tooling and dependency surface |

`pydantic` and `jsonschema` use bounded ranges rather than exact full-lock
resolution. CI's clean dependency installation tests the resolved set, but a
reproducible lock or constraints-file decision remains a separate dependency
governance follow-up.

