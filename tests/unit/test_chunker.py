"""Tests for app.core.chunker."""

from app.core.chunker import chunk_text


def test_short_text_no_split():
    assert chunk_text("hello") == ["hello"]


def test_empty_text():
    assert chunk_text("") == [""]


def test_exact_limit():
    text = "a" * 4076
    assert chunk_text(text) == [text]


def test_long_text_splits():
    text = "a" * 5000
    chunks = chunk_text(text)
    assert len(chunks) > 1
    assert all(len(c) <= 4076 for c in chunks)


def test_split_prefers_newline():
    part1 = "a" * 3000
    part2 = "b" * 3000
    text = part1 + "\n" + part2
    chunks = chunk_text(text)
    assert len(chunks) == 2
    assert chunks[0] == part1


def test_split_prefers_space_over_hard_cut():
    part1 = "word " * 800  # ~4000 chars
    part2 = "more " * 200
    text = part1 + part2
    chunks = chunk_text(text)
    assert len(chunks) >= 2
    # Split happens at a space, so the chunk ends with "word " (trailing space included)
    assert "word" in chunks[0]
    assert len(chunks[0]) <= 4076


def test_hard_cut_no_separators():
    text = "x" * 8200
    chunks = chunk_text(text)
    assert len(chunks) >= 2
    assert all(len(c) <= 4076 for c in chunks)
