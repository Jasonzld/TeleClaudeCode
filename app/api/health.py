"""Health-check endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz() -> dict[str, str]:
    try:
        from redis import Redis
        from app.config import settings
        r = Redis.from_url(settings.redis_url, socket_timeout=2)
        r.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception:
        return {"status": "degraded", "redis": "unreachable"}
