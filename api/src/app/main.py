"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import routes as auth_routes
from app.core.config import settings

app = FastAPI(
    title="Minecraft Server Dashboard API",
    description="API for managing Minecraft servers",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {"message": "Minecraft Server Dashboard API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}


@app.get("/api/status")
async def api_status() -> dict[str, str]:
    """API status endpoint for frontend testing.

    Returns:
        dict: API status information
    """
    return {
        "api": "online",
        "message": "Minecraft Server Dashboard API is running",
        "environment": "development",
    }
