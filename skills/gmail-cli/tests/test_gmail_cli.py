"""Unit tests for gmail_cli.

Offline only. We mock the Gmail API at two layers:

* `gmail_cli._execute` for command-level tests (lets us hand back canned
  dicts without spinning up the discovery client).
* A fake `list_method` callable for `paginate` tests.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import keyring
import pytest
from googleapiclient.errors import HttpError

# Ensure the package import points at the single-file module sitting next
# to the tests/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gmail_cli  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class InMemoryKeyring(keyring.backend.KeyringBackend):
    priority = 1

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], str] = {}

    def get_password(self, service, username):
        return self._store.get((service, username))

    def set_password(self, service, username, password):
        self._store[(service, username)] = password

    def delete_password(self, service, username):
        self._store.pop((service, username), None)


@pytest.fixture(autouse=True)
def _isolated_keyring(monkeypatch):
    backend = InMemoryKeyring()
    monkeypatch.setattr(keyring, "_keyring_backend", backend, raising=False)
    monkeypatch.setattr(keyring, "get_keyring", lambda: backend)
    monkeypatch.setattr(keyring.core, "get_keyring", lambda: backend)
    yield backend


@pytest.fixture(autouse=True)
def _isolated_config(monkeypatch, tmp_path):
    monkeypatch.setattr(gmail_cli, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(gmail_cli, "CONFIG_FILE", tmp_path / "config.toml")
    monkeypatch.setattr(gmail_cli, "CLIENT_SECRET_PATH", tmp_path / "client_secret.json")


def _saved_creds_payload() -> str:
    return json.dumps({
        "token": "fake-access",
        "refresh_token": "fake-refresh",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "id",
        "client_secret": "secret",
        "scopes": gmail_cli.SCOPES,
    })


# ---------------------------------------------------------------------------
# Account resolution
# ---------------------------------------------------------------------------


def test_resolve_account_uses_default_when_unspecified():
    gmail_cli.write_config({"default_account": "personal"})
    assert gmail_cli.resolve_account(None) == "personal"


def test_resolve_account_respects_flag():
    gmail_cli.write_config({"default_account": "personal"})
    assert gmail_cli.resolve_account("work") == "work"


def test_resolve_account_raises_when_unconfigured():
    with pytest.raises(gmail_cli.UserError, match="No account configured"):
        gmail_cli.resolve_account(None)


def test_load_credentials_missing_account_is_actionable():
    with pytest.raises(gmail_cli.UserError, match="gmail-cli config --account"):
        gmail_cli.load_credentials("nope")


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


def _fake_list_method(pages: list[dict]):
    """Return a callable that drains `pages` on successive calls."""
    calls = iter(pages)

    def list_method(**params):
        page = next(calls)
        request = MagicMock()
        request.execute.return_value = page
        return request

    return list_method


def test_paginate_concatenates_pages():
    list_method = _fake_list_method([
        {"messages": [{"id": "1"}, {"id": "2"}], "nextPageToken": "tok"},
        {"messages": [{"id": "3"}]},
    ])
    client = gmail_cli.GmailClient.__new__(gmail_cli.GmailClient)
    page = client.paginate(list_method, "messages", limit=10, userId="me", q="")
    assert [m["id"] for m in page.items] == ["1", "2", "3"]
    assert page.truncated is False


def test_paginate_marks_truncated_when_limit_hit():
    list_method = _fake_list_method([
        {"messages": [{"id": "1"}, {"id": "2"}], "nextPageToken": "tok"},
    ])
    client = gmail_cli.GmailClient.__new__(gmail_cli.GmailClient)
    page = client.paginate(list_method, "messages", limit=2, userId="me", q="")
    assert len(page.items) == 2
    assert page.truncated is True


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------


class _FakeResp:
    def __init__(self, status: int) -> None:
        self.status = status
        self.reason = "test"


def _http_error(status: int) -> HttpError:
    return HttpError(_FakeResp(status), b"error")


def _request_failing_then_ok(statuses: list[int], final: dict):
    request = MagicMock()
    side_effects = [_http_error(s) for s in statuses] + [final]
    request.execute.side_effect = side_effects
    return request


def test_429_is_retried_and_succeeds(monkeypatch):
    monkeypatch.setattr(gmail_cli.time, "sleep", lambda *_: None)
    monkeypatch.setattr(gmail_cli.random, "uniform", lambda a, b: 0)
    request = _request_failing_then_ok([429, 429], {"ok": True})
    assert gmail_cli._execute(request) == {"ok": True}
    assert request.execute.call_count == 3


def test_400_is_not_retried(monkeypatch):
    monkeypatch.setattr(gmail_cli.time, "sleep", lambda *_: None)
    request = MagicMock()
    request.execute.side_effect = _http_error(400)
    with pytest.raises(HttpError):
        gmail_cli._execute(request)
    assert request.execute.call_count == 1


def test_5xx_retries_exhaust(monkeypatch):
    monkeypatch.setattr(gmail_cli.time, "sleep", lambda *_: None)
    monkeypatch.setattr(gmail_cli.random, "uniform", lambda a, b: 0)
    request = MagicMock()
    request.execute.side_effect = [_http_error(503)] * 5
    with pytest.raises(HttpError):
        gmail_cli._execute(request, max_attempts=5)
    assert request.execute.call_count == 5


# ---------------------------------------------------------------------------
# Output rendering
# ---------------------------------------------------------------------------


def test_summarize_message_picks_headers():
    msg = {
        "id": "abc",
        "threadId": "thr",
        "snippet": "hello there",
        "payload": {
            "headers": [
                {"name": "From", "value": "a@example.com"},
                {"name": "Subject", "value": "Hi"},
                {"name": "Date", "value": "Mon, 1 Jan 2026"},
            ],
        },
    }
    assert gmail_cli._summarize_message(msg) == {
        "id": "abc",
        "threadId": "thr",
        "from": "a@example.com",
        "subject": "Hi",
        "date": "Mon, 1 Jan 2026",
        "snippet": "hello there",
    }


def test_iter_attachments_walks_nested_parts():
    payload = {
        "parts": [
            {"mimeType": "text/plain", "body": {"data": ""}},
            {
                "mimeType": "multipart/mixed",
                "parts": [
                    {
                        "filename": "report.pdf",
                        "mimeType": "application/pdf",
                        "body": {"attachmentId": "att-1", "size": 1234},
                    },
                ],
            },
        ],
    }
    rows = list(gmail_cli._iter_attachments(payload))
    assert rows == [{
        "attachmentId": "att-1",
        "filename": "report.pdf",
        "mimeType": "application/pdf",
        "size": 1234,
    }]


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------


def test_token_refresh_failure_surfaces_actionable_error(monkeypatch):
    keyring.set_password(gmail_cli.KEYRING_SERVICE, "personal", _saved_creds_payload())

    fake = MagicMock()
    fake.expired = True
    fake.refresh_token = "r"
    fake.refresh.side_effect = gmail_cli.RefreshError("invalid_grant")
    monkeypatch.setattr(gmail_cli, "_creds_from_payload", lambda _: fake)

    with pytest.raises(gmail_cli.UserError, match="re-authenticate"):
        gmail_cli.load_credentials("personal")


# ---------------------------------------------------------------------------
# whoami end-to-end (mocked at _execute + load_credentials)
# ---------------------------------------------------------------------------


def test_whoami_prints_email(monkeypatch, capsys):
    monkeypatch.setattr(gmail_cli, "load_credentials", lambda _: MagicMock())
    monkeypatch.setattr(
        gmail_cli, "GmailClient",
        lambda creds: MagicMock(service=MagicMock()),
    )
    monkeypatch.setattr(
        gmail_cli, "_execute",
        lambda req: {"emailAddress": "user@example.com",
                     "messagesTotal": 10, "threadsTotal": 5},
    )
    gmail_cli.write_config({"default_account": "personal"})

    rc = gmail_cli.main(["--format", "json", "whoami"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "user@example.com" in out
