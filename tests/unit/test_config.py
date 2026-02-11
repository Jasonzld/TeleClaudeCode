"""Tests for app.config."""

import os
from unittest.mock import patch


def test_default_settings():
    from app.config import Settings
    s = Settings(telegram_bot_token="test")
    assert s.claude_bin == "claude"
    assert s.claude_timeout_sec == 300
    assert s.direct_chat is True
    assert s.mode == "polling"


def test_allowed_user_ids_parsing():
    from app.config import Settings
    s = Settings(telegram_allowed_user_ids="123,456,789")
    assert s.allowed_user_ids == {123, 456, 789}


def test_allowed_user_ids_empty():
    from app.config import Settings
    s = Settings(telegram_allowed_user_ids="")
    assert s.allowed_user_ids == set()


def test_allowed_user_ids_whitespace():
    from app.config import Settings
    s = Settings(telegram_allowed_user_ids=" 111 , 222 , ")
    assert s.allowed_user_ids == {111, 222}
