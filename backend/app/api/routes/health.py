"""Liveness / readiness probes."""

from fastapi import APIRouter

from app.core.redis import get_redis

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict:
    """Readiness check — verifies Redis connectivity."""
    redis = get_redis()
    await redis.ping()
    return {"status": "ready", "redis": "ok"}
