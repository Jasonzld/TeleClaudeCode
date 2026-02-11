"""Integration tests for webhook flow."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_webhook_no_message(client):
    resp = client.post("/telegram/webhook", json={"update_id": 1})
    assert resp.status_code == 200


def test_webhook_empty_text(client):
    resp = client.post("/telegram/webhook", json={
        "update_id": 2,
        "message": {"chat": {"id": 100}, "from": {"id": 1}, "text": ""},
    })
    assert resp.status_code == 200


@patch("app.api.webhook.send_message", new_callable=AsyncMock)
def test_webhook_start_command(mock_send, client):
    resp = client.post("/telegram/webhook", json={
        "update_id": 3,
        "message": {"chat": {"id": 100}, "from": {"id": 1}, "text": "/start"},
    })
    assert resp.status_code == 200
    mock_send.assert_called_once()
    call_text = mock_send.call_args[0][1]
    assert "TeleClaudeCode" in call_text


@patch("app.api.webhook.send_message", new_callable=AsyncMock)
def test_webhook_ask_empty(mock_send, client):
    resp = client.post("/telegram/webhook", json={
        "update_id": 4,
        "message": {"chat": {"id": 100}, "from": {"id": 1}, "text": "/ask"},
    })
    assert resp.status_code == 200
    mock_send.assert_called_once()
    call_text = mock_send.call_args[0][1]
    assert "provide" in call_text.lower() or "question" in call_text.lower()
