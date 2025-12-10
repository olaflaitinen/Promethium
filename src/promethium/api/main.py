from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from promethium.core.config import get_settings
from promethium.core.config import get_settings
from promethium.core.logging import logger
from promethium.core.database import engine, Base
from promethium.api.routers import datasets, jobs, ml, auth, users, pipelines, experiments, results, system, websockets, benchmarks

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
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(datasets.router, prefix=settings.API_PREFIX)
app.include_router(jobs.router, prefix=settings.API_PREFIX)
app.include_router(ml.router, prefix=settings.API_PREFIX)
app.include_router(pipelines.router, prefix=settings.API_PREFIX)
app.include_router(experiments.router, prefix=settings.API_PREFIX)
app.include_router(results.router, prefix=settings.API_PREFIX)
app.include_router(system.router, prefix=settings.API_PREFIX)
app.include_router(benchmarks.router, prefix=settings.API_PREFIX)
app.include_router(websockets.router)
