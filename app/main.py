"""FastAPI application entry-point."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.webhook import router as webhook_router
from app.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="TeleClaudeCode", version="0.1.0")
app.include_router(health_router)
app.include_router(webhook_router, prefix="/telegram")
