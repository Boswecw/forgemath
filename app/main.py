from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.evaluation_router import router as evaluation_router
from app.api.registry_router import router as governance_router
from app.config import SERVICE_NAME, SERVICE_VERSION, validate_config
import app.services.immutability  # noqa: F401


@asynccontextmanager
async def lifespan(_app: FastAPI):
    validate_config()
    yield


app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    description="ForgeMath Phase 1 and Phase 2 canonical governance foundation",
    lifespan=lifespan,
)

app.include_router(governance_router)
app.include_router(evaluation_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "phase": "phase_2_evaluation_foundation",
    }
