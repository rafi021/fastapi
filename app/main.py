from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.categories.router import router as category_router
from app.config import settings
from app.database import AsyncSessionLocal, Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(category_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Health"], summary="Database connectivity check")
async def health_check():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT,
        }
    except Exception as exc:
        return {"status": "unhealthy", "database": str(exc)}
