"""TeleClaudeCode — one-click launcher."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys

from app.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def _start_polling_mode() -> None:
    token = settings.telegram_bot_token
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set. Check your .env file.")
        sys.exit(1)

    print("=" * 50)
    print("  TeleClaudeCode — Polling Mode (Local Dev)")
    print("=" * 50)
    print(f"  Bot token : ...{token[-6:]}")
    print(f"  Claude bin: {settings.claude_bin}")
    print(f"  Timeout   : {settings.claude_timeout_sec}s")
    print(f"  Model     : {settings.claude_model or '(default)'}")
    print(f"  Direct chat: {settings.direct_chat}")
    wl = settings.allowed_user_ids
    print(f"  Whitelist : {wl if wl else '(all users)'}")
    print("=" * 50)
    print()

    from app.bot.polling import run_polling
    run_polling()


def _start_webhook_mode() -> None:
    print("Starting webhook mode (API + Worker)...")
    # Check Redis
    try:
        from redis import Redis
        r = Redis.from_url(settings.redis_url, socket_timeout=3)
        r.ping()
        print(f"Redis OK: {settings.redis_url}")
    except Exception as exc:
        print(f"ERROR: Cannot connect to Redis: {exc}")
        sys.exit(1)

    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", settings.app_host, "--port", str(settings.app_port)],
    )
    worker_proc = subprocess.Popen(
        [sys.executable, "-m", "app.worker.runner"],
    )

    try:
        api_proc.wait()
    except KeyboardInterrupt:
        api_proc.terminate()
        worker_proc.terminate()
        print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="TeleClaudeCode launcher")
    parser.add_argument("--webhook", action="store_true", help="Run in webhook mode (needs Redis)")
    args = parser.parse_args()

    if args.webhook:
        _start_webhook_mode()
    else:
        _start_polling_mode()


if __name__ == "__main__":
    main()
