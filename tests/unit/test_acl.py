"""Tests for app.core.acl."""

import os
from unittest.mock import patch


def test_empty_whitelist_allows_all():
    with patch.dict(os.environ, {"TELEGRAM_ALLOWED_USER_IDS": ""}, clear=False):
        from app.core.acl import is_allowed
        assert is_allowed(12345)


def test_whitelist_allows_listed_user():
    with patch.dict(os.environ, {"TELEGRAM_ALLOWED_USER_IDS": "111,222,333"}, clear=False):
        from importlib import reload
        import app.config
        reload(app.config)
        from app.config import settings
        assert 222 in settings.allowed_user_ids


def test_whitelist_blocks_unlisted_user():
    with patch.dict(os.environ, {"TELEGRAM_ALLOWED_USER_IDS": "111,222"}, clear=False):
        from importlib import reload
        import app.config
        reload(app.config)
        from app.config import settings
        assert 999 not in settings.allowed_user_ids
