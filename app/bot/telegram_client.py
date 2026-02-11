"""Async Telegram message sender (for webhook mode)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings
from app.core.chunker import chunk_text

logger = logging.getLogger(__name__)

_API_BASE = "https://api.telegram.org/bot{token}"


def _url(method: str) -> str:
    return f"{_API_BASE.format(token=settings.telegram_bot_token)}/{method}"


async def send_message(chat_id: int, text: str, parse_mode: str | None = "Markdown") -> None:
    """Send a (possibly long) message, splitting into chunks."""
    chunks = chunk_text(text)
    total = len(chunks)
    async with httpx.AsyncClient(timeout=30) as client:
        for i, chunk in enumerate(chunks, 1):
            body = chunk
            if total > 1:
                body = f"[{i}/{total}]\n{chunk}"
            payload: dict[str, Any] = {"chat_id": chat_id, "text": body}
            if parse_mode:
                payload["parse_mode"] = parse_mode
            try:
                resp = await client.post(_url("sendMessage"), json=payload)
                if resp.status_code == 400 and parse_mode:
                    payload.pop("parse_mode", None)
                    await client.post(_url("sendMessage"), json=payload)
            except Exception:
                logger.exception("send_error chat_id=%s chunk=%d/%d", chat_id, i, total)


def send_message_sync(chat_id: int, text: str, parse_mode: str | None = "Markdown") -> None:
    """Synchronous wrapper for use in RQ workers."""
    chunks = chunk_text(text)
    total = len(chunks)
    with httpx.Client(timeout=30) as client:
        for i, chunk in enumerate(chunks, 1):
            body = chunk
            if total > 1:
                body = f"[{i}/{total}]\n{chunk}"
            payload: dict[str, Any] = {"chat_id": chat_id, "text": body}
            if parse_mode:
                payload["parse_mode"] = parse_mode
            try:
                resp = client.post(_url("sendMessage"), json=payload)
                if resp.status_code == 400 and parse_mode:
                    payload.pop("parse_mode", None)
                    client.post(_url("sendMessage"), json=payload)
            except Exception:
                logger.exception("send_error chat_id=%s chunk=%d/%d", chat_id, i, total)
