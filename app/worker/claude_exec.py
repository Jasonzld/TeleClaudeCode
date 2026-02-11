"""Claude Code CLI executor — runs `claude -p` as a subprocess."""

from __future__ import annotations

import logging
import platform
import subprocess

from app.config import settings

logger = logging.getLogger(__name__)

_IS_WINDOWS = platform.system() == "Windows"


def run_claude(prompt: str) -> str:
    """Execute Claude Code CLI with the given prompt and return stdout.

    Raises RuntimeError on failure or timeout.
    """
    cmd = [settings.claude_bin, "-p"]

    if settings.claude_model:
        cmd.extend(["--model", settings.claude_model])
    if settings.claude_permission_mode:
        cmd.extend(["--permission-mode", settings.claude_permission_mode])
    if settings.claude_max_budget_usd:
        cmd.extend(["--max-budget-usd", settings.claude_max_budget_usd])

    cmd.append(prompt)
    logger.info("claude_exec prompt_len=%d timeout=%d", len(prompt), settings.claude_timeout_sec)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=settings.claude_timeout_sec,
            shell=_IS_WINDOWS,  # Windows needs shell=True for .cmd wrappers
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude timed out after {settings.claude_timeout_sec}s")
    except FileNotFoundError:
        raise RuntimeError(f"claude binary not found: {settings.claude_bin}")

    if result.returncode != 0:
        stderr = result.stderr.strip()[:500] if result.stderr else "(no stderr)"
        raise RuntimeError(f"claude exited with code {result.returncode}: {stderr}")

    output = result.stdout.strip()
    max_chars = settings.claude_max_output_chars
    if len(output) > max_chars:
        output = output[:max_chars] + "\n\n... (output truncated)"

    return output
