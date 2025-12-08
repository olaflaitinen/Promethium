from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from promethium.core.config import get_settings
from promethium.core.logging import logger
from promethium.core.database import engine, Base
from promethium.api.routers import datasets, jobs, ml

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create DB tables if not exist (dev mode)
    # In production, recommend using Alembic migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")
    yield
    # Shutdown
    logger.info("Shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
origins = ["http://localhost:3000", "http://localhost:8000", "*"] # Configure appropriately for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(datasets.router, prefix=settings.API_PREFIX)
app.include_router(jobs.router, prefix=settings.API_PREFIX)
app.include_router(ml.router, prefix=settings.API_PREFIX)

@app.get("/health")
async def health_check():
    """
    System health check endpoint.
    Returns status of all system components.
    """
    status = "ok"
    db_status = "connected"
    
    # Database connectivity check
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        status = "degraded"
    
    return {
        "status": status,
        "version": settings.APP_VERSION,
        "database": db_status,
        "components": {
            "api": "running",
            "database": db_status
        }
    }
