"""Access control — user whitelist."""

from __future__ import annotations

from app.config import settings


def is_allowed(user_id: int) -> bool:
    """Return True if user_id is allowed to use the bot.

    An empty whitelist means *everyone* is allowed.
    """
    allowed = settings.allowed_user_ids
    if not allowed:
        return True
    return user_id in allowed
