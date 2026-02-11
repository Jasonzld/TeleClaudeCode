"""RQ job definition for webhook mode."""

from __future__ import annotations

import logging

from app.bot.telegram_client import send_message_sync
from app.worker.claude_exec import run_claude

logger = logging.getLogger(__name__)


def execute_claude_task(chat_id: int, user_id: int, prompt: str) -> None:
    """Run Claude Code and send the result back via Telegram."""
    logger.info("execute_claude_task user_id=%s prompt_len=%d", user_id, len(prompt))
    try:
        output = run_claude(prompt)
    except RuntimeError as exc:
        error_msg = str(exc)
        if "timed out" in error_msg:
            send_message_sync(chat_id, "Timed out. Try a shorter question or retry later.")
        elif "not found" in error_msg:
            send_message_sync(chat_id, "Claude Code binary not found. Contact the admin.")
        else:
            send_message_sync(chat_id, f"Error: {error_msg}")
        return
    except Exception:
        logger.exception("unexpected_error user_id=%s", user_id)
        send_message_sync(chat_id, "System error. Please retry later.")
        return

    send_message_sync(chat_id, output)
    logger.info("done user_id=%s output_len=%d", user_id, len(output))
