"""gmail-cli — read-only Gmail operations over the Gmail REST API.

Single-file implementation. Layout (top-to-bottom):
  1. Imports + constants
  2. Config (default-account file)
  3. Auth (OAuth flow + keyring storage + refresh)
  4. Client wrapper (paginate + light retry)
  5. Commands (config, whoami, env, messages/threads/labels/attachments)
  6. main() — argparse dispatch

Designed to stay in one file until it genuinely outgrows it.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import keyring
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.table import Table

try:  # 3.11+
    import tomllib
except ModuleNotFoundError:  # 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]

# ---------------------------------------------------------------------------
# 1. Constants
# ---------------------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]

KEYRING_SERVICE = "gmail-cli"
CONFIG_DIR = Path(os.environ.get("GMAIL_CLI_CONFIG_DIR", Path.home() / ".config" / "gmail-cli"))
CONFIG_FILE = CONFIG_DIR / "config.toml"
CLIENT_SECRET_PATH = Path(
    os.environ.get("GMAIL_CLI_CLIENT_SECRET", CONFIG_DIR / "client_secret.json")
)

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# 2. Config
# ---------------------------------------------------------------------------


def read_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    with CONFIG_FILE.open("rb") as f:
        return tomllib.load(f)


def write_config(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for k, v in data.items():
        if isinstance(v, str):
            lines.append(f'{k} = "{v}"')
        else:
            lines.append(f"{k} = {json.dumps(v)}")
    CONFIG_FILE.write_text("\n".join(lines) + "\n")


def resolve_account(account: str | None) -> str:
    if account:
        return account
    env = os.environ.get("GMAIL_CLI_ACCOUNT")
    if env:
        return env
    cfg = read_config()
    if "default_account" in cfg:
        return cfg["default_account"]
    raise UserError(
        "No account configured. Run `gmail-cli config --account NAME` first."
    )


# ---------------------------------------------------------------------------
# 3. Auth
# ---------------------------------------------------------------------------


class UserError(Exception):
    """Surface as a single-line stderr message + nonzero exit, no traceback."""


def _creds_from_payload(payload: str) -> Credentials:
    return Credentials.from_authorized_user_info(json.loads(payload), SCOPES)


def _creds_to_payload(creds: Credentials) -> str:
    return creds.to_json()


def load_credentials(account: str) -> Credentials:
    payload = keyring.get_password(KEYRING_SERVICE, account)
    if not payload:
        raise UserError(
            f"No saved credentials for account '{account}'. "
            f"Run `gmail-cli config --account {account}` to sign in."
        )
    creds = _creds_from_payload(payload)
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            keyring.set_password(KEYRING_SERVICE, account, _creds_to_payload(creds))
        except RefreshError as e:
            raise UserError(
                f"Token refresh failed for '{account}': {e}. "
                f"Run `gmail-cli config --account {account}` to re-authenticate."
            ) from e
    return creds


def run_oauth_flow(account: str) -> Credentials:
    if not CLIENT_SECRET_PATH.exists():
        raise UserError(
            f"OAuth client secret not found at {CLIENT_SECRET_PATH}.\n"
            f"See references/setup.md for how to create one."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)
    keyring.set_password(KEYRING_SERVICE, account, _creds_to_payload(creds))

    cfg = read_config()
    cfg.setdefault("default_account", account)
    write_config(cfg)
    return creds


# ---------------------------------------------------------------------------
# 4. Client wrapper
# ---------------------------------------------------------------------------


@dataclass
class Page:
    items: list[dict[str, Any]]
    truncated: bool
    total_estimate: int | None = None


def _retryable(status: int) -> bool:
    return status in (429, 500, 502, 503, 504)


def _execute(request, *, max_attempts: int = 5) -> dict[str, Any]:
    """Execute a Gmail API request with bounded exponential backoff."""
    delay = 1.0
    for attempt in range(1, max_attempts + 1):
        try:
            return request.execute()
        except HttpError as e:
            status = e.resp.status if e.resp is not None else 0
            if not _retryable(status) or attempt == max_attempts:
                raise
            sleep_for = delay + random.uniform(0, delay / 2)
            time.sleep(min(sleep_for, 32))
            delay = min(delay * 2, 32)
    raise RuntimeError("unreachable")  # pragma: no cover


class GmailClient:
    def __init__(self, creds: Credentials) -> None:
        self.service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    def paginate(
        self,
        list_method: Callable[..., Any],
        items_key: str,
        *,
        limit: int,
        **params: Any,
    ) -> Page:
        """Loop nextPageToken, capping at `limit` items.

        Returns truncated=True when the cap is hit and the API still has a
        nextPageToken — so callers don't silently lose data.
        """
        items: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            req_params = dict(params)
            if page_token:
                req_params["pageToken"] = page_token
            req_params["maxResults"] = min(100, limit - len(items))
            resp = _execute(list_method(**req_params))
            items.extend(resp.get(items_key, []))
            page_token = resp.get("nextPageToken")
            if not page_token or len(items) >= limit:
                break
        truncated = bool(page_token) and len(items) >= limit
        return Page(items=items[:limit], truncated=truncated, total_estimate=None)


# ---------------------------------------------------------------------------
# 5. Commands
# ---------------------------------------------------------------------------


def cmd_config(args: argparse.Namespace) -> int:
    account = args.account or "default"
    run_oauth_flow(account)
    err_console.print(f"[green]Signed in as account '{account}'.[/green]")
    return EXIT_OK


def cmd_whoami(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    creds = load_credentials(account)
    client = GmailClient(creds)
    profile = _execute(client.service.users().getProfile(userId="me"))
    output(args, {"account": account, "email": profile.get("emailAddress"),
                  "messagesTotal": profile.get("messagesTotal"),
                  "threadsTotal": profile.get("threadsTotal")})
    return EXIT_OK


def cmd_env(args: argparse.Namespace) -> int:
    cfg = read_config()
    out = {
        "config_dir": str(CONFIG_DIR),
        "config_file": str(CONFIG_FILE),
        "client_secret_path": str(CLIENT_SECRET_PATH),
        "client_secret_present": CLIENT_SECRET_PATH.exists(),
        "default_account": cfg.get("default_account"),
        "scopes": SCOPES,
    }
    output(args, out)
    return EXIT_OK


def cmd_messages_list(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    client = GmailClient(load_credentials(account))
    query = args.query or ""
    if args.label:
        query = f"label:{args.label} {query}".strip()
    page = client.paginate(
        client.service.users().messages().list,
        items_key="messages",
        limit=args.limit,
        userId="me",
        q=query,
    )
    detailed = [
        _execute(client.service.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ))
        for m in page.items
    ]
    rows = [_summarize_message(m) for m in detailed]
    output(args, {"data": rows, "truncated": page.truncated},
           render_table=lambda: _render_message_table(rows))
    return EXIT_OK


def cmd_messages_view(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    client = GmailClient(load_credentials(account))
    msg = _execute(client.service.users().messages().get(
        userId="me", id=args.message_id, format="full",
    ))
    rendered = _render_message_full(msg, markdown=args.markdown, raw=args.raw)
    output(args, msg if args.format == "json" else None, render_text=lambda: rendered)
    return EXIT_OK


def cmd_messages_search(args: argparse.Namespace) -> int:
    args.query = args.query_positional
    args.label = None
    return cmd_messages_list(args)


def cmd_threads_list(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    client = GmailClient(load_credentials(account))
    query = args.query or ""
    if args.label:
        query = f"label:{args.label} {query}".strip()
    page = client.paginate(
        client.service.users().threads().list,
        items_key="threads",
        limit=args.limit,
        userId="me",
        q=query,
    )
    rows = [{"id": t["id"], "snippet": t.get("snippet", "")} for t in page.items]
    output(args, {"data": rows, "truncated": page.truncated},
           render_table=lambda: _render_thread_table(rows))
    return EXIT_OK


def cmd_threads_view(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    client = GmailClient(load_credentials(account))
    thread = _execute(client.service.users().threads().get(
        userId="me", id=args.thread_id, format="full",
    ))
    if args.format == "json":
        output(args, thread)
    else:
        for m in thread.get("messages", []):
            console.print(_render_message_full(m, markdown=args.markdown, raw=False))
            console.print("---")
    return EXIT_OK


def cmd_labels_list(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    client = GmailClient(load_credentials(account))
    resp = _execute(client.service.users().labels().list(userId="me"))
    labels = resp.get("labels", [])
    output(args, {"data": labels}, render_table=lambda: _render_labels_table(labels))
    return EXIT_OK


def cmd_attachments_list(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    client = GmailClient(load_credentials(account))
    msg = _execute(client.service.users().messages().get(
        userId="me", id=args.message_id, format="full",
    ))
    rows = list(_iter_attachments(msg.get("payload", {})))
    output(args, {"data": rows},
           render_table=lambda: _render_attachments_table(rows))
    return EXIT_OK


def cmd_attachments_download(args: argparse.Namespace) -> int:
    account = resolve_account(args.account)
    client = GmailClient(load_credentials(account))
    att = _execute(client.service.users().messages().attachments().get(
        userId="me", messageId=args.message_id, id=args.attachment_id,
    ))
    raw = base64.urlsafe_b64decode(att["data"])
    out_path = Path(args.out) if args.out else Path(args.attachment_id + ".bin")
    out_path.write_bytes(raw)
    err_console.print(f"[green]Wrote {len(raw)} bytes to {out_path}[/green]")
    return EXIT_OK


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _header(headers: list[dict[str, str]], name: str) -> str:
    name_lower = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name_lower:
            return h.get("value", "")
    return ""


def _summarize_message(msg: dict[str, Any]) -> dict[str, Any]:
    headers = msg.get("payload", {}).get("headers", [])
    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "from": _header(headers, "From"),
        "subject": _header(headers, "Subject"),
        "date": _header(headers, "Date"),
        "snippet": msg.get("snippet", ""),
    }


def _render_message_table(rows: list[dict[str, Any]]) -> Table:
    table = Table(show_lines=False, header_style="bold")
    for col in ("id", "from", "subject", "date"):
        table.add_column(col)
    for r in rows:
        table.add_row(r["id"], r["from"][:40], r["subject"][:60], r["date"][:30])
    return table


def _render_thread_table(rows: list[dict[str, Any]]) -> Table:
    table = Table(show_lines=False, header_style="bold")
    table.add_column("id")
    table.add_column("snippet")
    for r in rows:
        table.add_row(r["id"], r["snippet"][:80])
    return table


def _render_labels_table(labels: list[dict[str, Any]]) -> Table:
    table = Table(show_lines=False, header_style="bold")
    for col in ("id", "name", "type"):
        table.add_column(col)
    for lab in labels:
        table.add_row(lab.get("id", ""), lab.get("name", ""), lab.get("type", ""))
    return table


def _render_attachments_table(rows: list[dict[str, Any]]) -> Table:
    table = Table(show_lines=False, header_style="bold")
    for col in ("attachmentId", "filename", "mimeType", "size"):
        table.add_column(col)
    for r in rows:
        table.add_row(r["attachmentId"], r["filename"], r["mimeType"], str(r["size"]))
    return table


def _iter_attachments(part: dict[str, Any]) -> Iterable[dict[str, Any]]:
    if part.get("filename") and part.get("body", {}).get("attachmentId"):
        body = part["body"]
        yield {
            "attachmentId": body["attachmentId"],
            "filename": part["filename"],
            "mimeType": part.get("mimeType", ""),
            "size": body.get("size", 0),
        }
    for child in part.get("parts", []) or []:
        yield from _iter_attachments(child)


def _decode_body(part: dict[str, Any]) -> str:
    data = part.get("body", {}).get("data")
    if not data:
        return ""
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")


def _find_text_part(part: dict[str, Any]) -> str:
    if part.get("mimeType", "").startswith("text/plain"):
        return _decode_body(part)
    for child in part.get("parts", []) or []:
        text = _find_text_part(child)
        if text:
            return text
    return ""


def _render_message_full(msg: dict[str, Any], *, markdown: bool, raw: bool) -> str:
    if raw:
        return _decode_body(msg.get("payload", {})) or msg.get("snippet", "")
    headers = msg.get("payload", {}).get("headers", [])
    head = "\n".join(
        f"{name}: {_header(headers, name)}"
        for name in ("From", "To", "Cc", "Date", "Subject")
        if _header(headers, name)
    )
    body = _find_text_part(msg.get("payload", {})) or msg.get("snippet", "")
    return f"{head}\n\n{body}"


# ---------------------------------------------------------------------------
# Output dispatch
# ---------------------------------------------------------------------------


def output(
    args: argparse.Namespace,
    data: Any,
    *,
    render_table: Callable[[], Table] | None = None,
    render_text: Callable[[], str] | None = None,
) -> None:
    if args.format == "json":
        console.print_json(data=data)
        return
    if render_table is not None:
        console.print(render_table())
        return
    if render_text is not None:
        console.print(render_text())
        return
    console.print(data)


# ---------------------------------------------------------------------------
# 6. main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gmail-cli", description="Gmail read-only CLI")
    p.add_argument("--account", help="account name (default: configured default)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    pc = sub.add_parser("config", help="run OAuth flow and store credentials")
    pc.set_defaults(func=cmd_config)

    pw = sub.add_parser("whoami", help="show signed-in account")
    pw.set_defaults(func=cmd_whoami)

    pe = sub.add_parser("env", help="show resolved environment")
    pe.set_defaults(func=cmd_env)

    pm = sub.add_parser("messages", help="message operations")
    pm_sub = pm.add_subparsers(dest="subcommand", required=True)

    pml = pm_sub.add_parser("list", help="list messages")
    pml.add_argument("-q", "--query", default="")
    pml.add_argument("-L", "--label", default=None)
    pml.add_argument("-l", "--limit", type=int, default=20)
    pml.set_defaults(func=cmd_messages_list)

    pmv = pm_sub.add_parser("view", help="view a message")
    pmv.add_argument("message_id")
    pmv.add_argument("--markdown", action="store_true")
    pmv.add_argument("--raw", action="store_true")
    pmv.set_defaults(func=cmd_messages_view)

    pms = pm_sub.add_parser("search", help="alias for `messages list --query`")
    pms.add_argument("query_positional", metavar="QUERY")
    pms.add_argument("-l", "--limit", type=int, default=20)
    pms.set_defaults(func=cmd_messages_search)

    pt = sub.add_parser("threads", help="thread operations")
    pt_sub = pt.add_subparsers(dest="subcommand", required=True)

    ptl = pt_sub.add_parser("list", help="list threads")
    ptl.add_argument("-q", "--query", default="")
    ptl.add_argument("-L", "--label", default=None)
    ptl.add_argument("-l", "--limit", type=int, default=20)
    ptl.set_defaults(func=cmd_threads_list)

    ptv = pt_sub.add_parser("view", help="view a thread")
    ptv.add_argument("thread_id")
    ptv.add_argument("--markdown", action="store_true")
    ptv.set_defaults(func=cmd_threads_view)

    pl = sub.add_parser("labels", help="label operations")
    pl_sub = pl.add_subparsers(dest="subcommand", required=True)
    pll = pl_sub.add_parser("list", help="list labels")
    pll.set_defaults(func=cmd_labels_list)

    pa = sub.add_parser("attachments", help="attachment operations")
    pa_sub = pa.add_subparsers(dest="subcommand", required=True)

    pal = pa_sub.add_parser("list", help="list attachments on a message")
    pal.add_argument("message_id")
    pal.set_defaults(func=cmd_attachments_list)

    pad = pa_sub.add_parser("download", help="download an attachment")
    pad.add_argument("message_id")
    pad.add_argument("attachment_id")
    pad.add_argument("--out", default=None)
    pad.set_defaults(func=cmd_attachments_download)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except UserError as e:
        err_console.print(f"[red]error:[/red] {e}")
        return EXIT_ERROR
    except HttpError as e:
        err_console.print(f"[red]Gmail API error:[/red] {e}")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
