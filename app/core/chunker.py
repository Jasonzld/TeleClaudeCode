"""Split long text into Telegram-safe chunks (≤ 4096 chars)."""

from __future__ import annotations

_TG_LIMIT = 4096
_RESERVE = 20  # room for "[n/N]\n" prefix
_MAX = _TG_LIMIT - _RESERVE


def chunk_text(text: str, limit: int = _MAX) -> list[str]:
    """Return a list of chunks, each ≤ *limit* characters."""
    if not text:
        return [text]
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Try to split at a newline in the second half
        cut = text.rfind("\n", limit // 2, limit)
        if cut == -1:
            cut = text.rfind(" ", limit // 2, limit)
        if cut == -1:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return chunks
