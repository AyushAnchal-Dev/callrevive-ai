"""CallRevive AI — FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.core.config import get_settings
from app.core.exceptions import AppException, app_exception_handler
from app.core.middleware import register_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    print(f"\U0001f680 CallRevive AI starting in {settings.APP_ENV} mode")
    yield
    print("\U0001f44b CallRevive AI shutting down")


app = FastAPI(
    title="CallRevive AI API",
    description="AI-Powered Missed Call Recovery & Revenue Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# --- Middleware & Rate Limiting ---
register_middleware(app)

# --- Exception Handlers ---
app.add_exception_handler(AppException, app_exception_handler)

# --- Routes ---
from app.api.v1.router import api_v1_router  # noqa: E402

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "callrevive-ai", "version": "1.0.0"}


# --- Prometheus metrics (conditional) ---
if settings.PROMETHEUS_ENABLED:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except ImportError:
        pass
