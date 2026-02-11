"""Telegram webhook endpoint (production mode)."""

from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any

from fastapi import APIRouter, Header, Request, Response

from app.config import settings
from app.core.acl import is_allowed
from app.bot.telegram_client import send_message

router = APIRouter()
logger = logging.getLogger(__name__)

_seen: OrderedDict[int, None] = OrderedDict()
_SEEN_MAX = 10_000


def _dedup(update_id: int) -> bool:
    if update_id in _seen:
        return True
    _seen[update_id] = None
    if len(_seen) > _SEEN_MAX:
        _seen.popitem(last=False)
    return False


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
) -> Response:
    # Verify secret
    if settings.telegram_webhook_secret:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            return Response(status_code=403)

    data: dict[str, Any] = await request.json()
    update_id = data.get("update_id", 0)

    if _dedup(update_id):
        return Response(status_code=200)

    message = data.get("message")
    if not message:
        return Response(status_code=200)

    chat_id: int = message["chat"]["id"]
    user_id: int = message.get("from", {}).get("id", 0)
    text: str = message.get("text", "")

    if not text:
        return Response(status_code=200)

    # Extract command
    cmd, arg = "", text
    if text.startswith("/"):
        parts = text.split(None, 1)
        cmd = parts[0].lower().split("@")[0]
        arg = parts[1] if len(parts) > 1 else ""

    if cmd == "/start":
        mode_hint = "Send any message directly" if settings.direct_chat else "Use `/ask <question>`"
        await send_message(
            chat_id,
            f"Welcome to TeleClaudeCode!\n\n"
            f"{mode_hint} to query Claude Code.\n"
            f"Example: `How to read CSV in Python?`\n\n"
            f"Send `/help` for more info.",
        )
        return Response(status_code=200)

    if cmd == "/help":
        lines = [
            "*TeleClaudeCode Help*\n",
            "- `/ask <question>` -- Ask Claude Code",
            "- `/start` -- Welcome message",
            "- `/help` -- This help\n",
        ]
        if settings.direct_chat:
            lines.insert(1, "You can also just type your question directly!\n")
        await send_message(chat_id, "\n".join(lines))
        return Response(status_code=200)

    if cmd == "/ask":
        if not is_allowed(user_id):
            await send_message(chat_id, "Access denied.")
            return Response(status_code=200)
        if not arg.strip():
            await send_message(chat_id, "Please provide a question.")
            return Response(status_code=200)
        # Enqueue to Redis
        from redis import Redis
        from rq import Queue
        conn = Redis.from_url(settings.redis_url)
        q = Queue(settings.queue_name, connection=conn)
        q.enqueue("app.worker.jobs.execute_claude_task", chat_id, user_id, arg.strip())
        await send_message(chat_id, "Accepted, processing...")
        return Response(status_code=200)

    # Direct chat
    if not cmd and settings.direct_chat:
        if not is_allowed(user_id):
            await send_message(chat_id, "Access denied.")
            return Response(status_code=200)
        from redis import Redis
        from rq import Queue
        conn = Redis.from_url(settings.redis_url)
        q = Queue(settings.queue_name, connection=conn)
        q.enqueue("app.worker.jobs.execute_claude_task", chat_id, user_id, text.strip())
        await send_message(chat_id, "Accepted, processing...")
        return Response(status_code=200)

    return Response(status_code=200)
