"""
FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import get_settings
from core.dependencies import get_container
from api.routes import pokemon


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")
    
    container = get_container()
    
    yield
    
    print("Shutting down...")
    await container.cleanup()
    print("Shutdown complete")


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

app.include_router(pokemon.router)


@app.get("/")
async def read_root():
    """Root endpoint returning application info."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}