"""FastAPI application factory."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from html2ppt import __version__
from html2ppt.config.logging import setup_logging, get_logger
from html2ppt.config.settings import get_settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    settings = get_settings()

    # Setup logging
    log_format = settings.log_format.lower()
    json_format = log_format == "json"
    if log_format == "auto":
        json_format = not settings.debug
    setup_logging(
        level=settings.log_level,
        json_format=json_format,
    )

    logger.info(
        "Starting HTML2PPT",
        version=__version__,
        debug=settings.debug,
        llm_provider=settings.llm_provider,
    )

    # Create data directories
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    yield

    logger.info("Shutting down HTML2PPT")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    settings = get_settings()

    app = FastAPI(
        title="HTML2PPT API",
        description="AI-powered presentation generator: from requirements to Slidev PPT",
        version=__version__,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    from html2ppt.api.routes import health, sessions, settings as settings_router

    app.include_router(health.router, tags=["Health"])
    app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
    app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])

    return app


# Create app instance for uvicorn
app = create_app()
