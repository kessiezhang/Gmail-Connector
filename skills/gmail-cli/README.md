# gmail-cli

A small, single-file command-line tool for reading Gmail. Lives as a Claude Code skill, but the CLI itself stands alone.

**v1 is read-only.** It can list, view, and search your messages, threads, labels, and attachments. Sending and modifying are deliberately out of scope until the read path is trusted.

## What it does today

| Command | What it does |
|---|---|
| `gmail-cli config [--account NAME]` | OAuth flow; saves token in your OS keyring |
| `gmail-cli whoami` | Show signed-in account |
| `gmail-cli env` | Show resolved config and where things live |
| `gmail-cli messages list [--query Q] [--label L] [--limit N]` | List messages |
| `gmail-cli messages view <ID> [--markdown\|--raw]` | View one message |
| `gmail-cli messages search "QUERY"` | Alias for `messages list --query` |
| `gmail-cli threads list [--query Q] [--limit N]` | List threads |
| `gmail-cli threads view <ID>` | View a thread |
| `gmail-cli labels list` | List labels |
| `gmail-cli attachments list <MSG-ID>` | List attachments on a message |
| `gmail-cli attachments download <MSG-ID> <ATT-ID> [--out PATH]` | Download an attachment |

Global flags: `--account NAME`, `--format text\|json`, `-v`.

## Setup

You need:

1. Python 3.10 or newer.
2. A Google OAuth desktop client. See [references/setup.md](references/setup.md) for the 5-step walkthrough — you'll end up with a `client_secret.json` file.

Then:

```bash
# Drop your OAuth client where the CLI looks for it.
mkdir -p ~/.config/gmail-cli
mv ~/Downloads/client_secret_*.json ~/.config/gmail-cli/client_secret.json

# Sign in. The shim creates a venv and installs deps the first time.
./scripts/gmail-cli config --account personal

# Confirm.
./scripts/gmail-cli whoami
```

That's it. Subsequent runs reuse the venv (the shim hashes `requirements.txt` and only reinstalls when it changes).

## Daily use

```bash
# Unread in inbox
./scripts/gmail-cli messages list --query "is:unread in:inbox"

# Read a message
./scripts/gmail-cli messages view 18a3f1234... --markdown

# Pipe a list to jq
./scripts/gmail-cli --format json messages list \
  --query "from:alerts@" --limit 100 \
  | jq '.data[] | {from, subject}'
```

For the full Gmail query syntax (`is:`, `from:`, `newer_than:`, `has:attachment`, …) see [references/query-guide.md](references/query-guide.md).

## Multiple accounts

```bash
./scripts/gmail-cli config --account personal   # first one becomes default
./scripts/gmail-cli config --account work
./scripts/gmail-cli --account work whoami
```

Tokens for each account live in your OS keyring under `gmail-cli/<account>`. Plaintext tokens never touch disk.

## Where things live

| Path | What |
|---|---|
| `~/.config/gmail-cli/config.toml` | Default account name |
| `~/.config/gmail-cli/client_secret.json` | Your Google OAuth client (you supply this) |
| OS keyring, service `gmail-cli` | Per-account access + refresh tokens |
| `<skill>/.venv/` | Auto-created virtualenv (shim manages this) |

Override the config dir with `GMAIL_CLI_CONFIG_DIR=...` and the OAuth client path with `GMAIL_CLI_CLIENT_SECRET=...`.

## Running tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest tests/
```

All tests are offline — they mock the Gmail API. No real credentials needed.

## What's planned for v2

The reference docs in [references/commands/](references/commands/) describe the full command surface, including writes. Anything not in the table at the top of this README is **planned but not yet implemented** — those command files start with a "Status: planned for v2" banner.

When v2 lands it adds: `messages send/reply/forward/modify/trash/delete`, `threads modify/trash/delete`, `labels create/rename/delete/apply/remove`, and the full `drafts` surface.

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md). Common issues:

- **"OAuth client secret not found"** — you haven't placed `client_secret.json`. See [references/setup.md](references/setup.md).
- **"Token refresh failed … re-authenticate"** — Google revoked the token. Run `gmail-cli config --account <name>` again.
- **`python3` not found** — install Python 3.10+, or set `GMAIL_CLI_PYTHON` to the interpreter you want.

## Layout

```
gmail-cli/
├── SKILL.md                     # for Claude Code agents
├── README.md                    # this file
├── gmail_cli.py                 # the whole CLI, ~500 lines
├── scripts/gmail-cli            # bash shim → ensures venv, runs Python
├── requirements.txt             # 4 pinned deps
├── requirements-dev.txt         # + pytest, responses
├── tests/test_gmail_cli.py      # offline unit tests
└── references/                  # command docs, query guide, setup, workflows
```

One file. Plain Python. Plain pip. Sharable.
