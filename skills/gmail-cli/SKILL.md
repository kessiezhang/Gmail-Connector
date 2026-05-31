---
name: gmail-cli
description: Gmail read-only operations via gmail-cli. v1 covers list/view/search for messages, threads, labels, and attachments. Writes (send, modify, delete, drafts) are planned for v2.
allowed-tools: Read, Bash(scripts/gmail-cli:*)
---

Progressive disclosure: keep responses short, expand only on request.

## v1 scope

**Implemented and safe to use today:**

- `config`, `whoami`, `env`
- `messages list`, `messages view`, `messages search`
- `threads list`, `threads view`
- `labels list`
- `attachments list`, `attachments download`

**Documented but not yet implemented** (every write operation): `messages send/reply/forward/modify/trash/delete`, `threads modify/trash/delete`, `labels create/rename/delete/apply/remove`, all of `drafts/*`. Their reference docs in `references/commands/` carry a "Status: planned for v2" banner. Do not pretend these work — if a user asks for one, say it's not in v1 and offer the closest read-only alternative.

## Output Policy

- Default `--format text` (Rich tables for lists, plain text for `view`).
- Use `--format json` when piping to `jq` or returning data to an agent. The shape is `{"data": ..., "truncated": bool}` for list commands.
- TOON is **not** supported in v1. Don't pass `--format toon` or `--toon-max-items`.
- Avoid `messages view --raw` by default; run it only when the user explicitly asks for the raw RFC 822 source.

## Environment

```bash
scripts/gmail-cli <command>
```

The shim creates a local `.venv/` on first run and installs `requirements.txt` into it. Subsequent runs reuse the venv. Plain Python + pip — no nix, no `uv`, no `pipx`.

All `scripts/` paths are relative to this skill's installation directory.

**Setup pre-requisites** (one-time, per user):

1. Python 3.10+ on PATH (or set `GMAIL_CLI_PYTHON`).
2. A Google OAuth desktop client. The user creates this in their own Google Cloud project — see `references/setup.md` for the 5-step walkthrough. The resulting `client_secret.json` goes at `~/.config/gmail-cli/client_secret.json` (or set `GMAIL_CLI_CLIENT_SECRET`).
3. `gmail-cli config --account <name>` — runs OAuth, stores the access + refresh tokens in the OS keyring (Keychain/Credential Manager/Secret Service). Plaintext tokens never touch disk.

If the user hasn't set up step 2, the CLI will say so explicitly with a pointer to `references/setup.md`. Don't try to work around it — point them at the setup doc.

## Account Selection

**Default**: Use default account (no `--account` flag needed). The default is whichever account ran `gmail-cli config` first; it's stored in `~/.config/gmail-cli/config.toml`.

**Only add `--account <name>` when**:
- User explicitly names an account
- URL/context indicates a different account

**Examples**:
```bash
# Default account
scripts/gmail-cli messages list --query "is:unread"

# Explicit account override
scripts/gmail-cli --account work messages list --query "is:unread"

# JSON output for piping to jq or returning data to the agent
scripts/gmail-cli --format json messages list --query "from:alerts@"
```

## Safety model

- v1 is read-only end-to-end. No mutating commands are wired up; the CLI cannot send, delete, or modify anything.
- If a user asks for a write operation (e.g. "send an email", "archive this", "add a label"), tell them v1 doesn't implement it and offer to draft the message body or surface the IDs they'd act on once v2 lands.
- Never print full OAuth tokens or refresh tokens in output.

## Workflow

1. Confirm auth with `gmail-cli whoami`. If it errors, point at `references/setup.md` or `gmail-cli config`.
2. Use the right read command for the question (`messages list` for individual emails, `threads list` for conversations, `labels list` to discover labels).
3. Pass `--format json` whenever you need to consume the result programmatically.
4. Respect `--limit` — default is 20; bump it when the user asks for breadth, but watch for `truncated: true` in the JSON output.

## Core Commands (v1, all read-only)

**Messages**:
- `messages list [--query "GMAIL_QUERY"] [--label LABEL] [--limit N]` — list messages
- `messages view <MESSAGE-ID> [--markdown] [--raw]` — view a message
- `messages search "QUERY" [--limit N]` — alias for `messages list --query`

**Threads**:
- `threads list [--query "..."] [--limit N]` — list threads
- `threads view <THREAD-ID> [--markdown]` — view a thread with all messages

**Labels**:
- `labels list` — list all labels (system + user)

**Attachments**:
- `attachments list <MESSAGE-ID>` — list attachments
- `attachments download <MESSAGE-ID> <ATTACHMENT-ID> [--out PATH]` — download an attachment

**Utility**:
- `config [--account NAME]` — OAuth flow and secure credential storage
- `whoami` — verify authentication and show active account
- `env` — show resolved environment

For all commands (including v2-planned writes): see `references/commands/README.md` or specific `references/commands/<command>.md`. Files marked "Status: planned for v2" describe the intended interface but do not work yet.

## Gmail Query Quick Reference

```bash
# Unread in inbox
scripts/gmail-cli messages list --query "is:unread in:inbox"

# From a sender, last 7 days
scripts/gmail-cli messages list --query "from:alerts@example.com newer_than:7d"

# With attachment, larger than 5MB
scripts/gmail-cli messages list --query "has:attachment larger:5M"

# Specific label
scripts/gmail-cli messages list --label Receipts
```

**Complete query guide**: `references/query-guide.md`

## Additional Resources

- `README.md` — human-facing quickstart and setup
- `references/setup.md` — Google OAuth client walkthrough (one-time)
- `references/commands/README.md` — all commands index
- `references/query-guide.md` — Gmail search-query syntax
- `references/workflows.md` — common workflow patterns
- `references/troubleshooting.md` — auth, quota, and rate-limit fixes

## Discovery

```bash
# Top-level command help
scripts/gmail-cli --help

# Per-subcommand help
scripts/gmail-cli messages list --help

# Browse reference docs
ls references/commands/*.md
```
