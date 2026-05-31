# messages list — List Messages

List messages matching a Gmail search query.

## Usage

```bash
gmail-cli messages list [--query "GMAIL_QUERY"] [--label LABEL] [--limit N] [--output table|text|toon|json]
```

## Options

- `-q, --query` (optional): Gmail search query string (`is:unread`, `from:`, `subject:`, etc.)
- `-L, --label` (optional): Filter by label name or ID (shorthand for `label:` in the query)
- `-l, --limit` (optional): Max results (default: 20)
- `--output` (optional): `table`, `text`, `toon`, `json`

## Examples

```bash
# Unread in inbox
gmail-cli messages list --query "is:unread in:inbox"

# From a sender, last 7 days
gmail-cli messages list --query "from:alerts@example.com newer_than:7d"

# By label, with limit
gmail-cli messages list --label Receipts --limit 10

# JSON output for automation
gmail-cli messages list --query "is:unread" --output json

# Compact TOON output for agents
gmail-cli messages list --query "is:unread" --output toon
```

## Output

- Default global mode is `toon`, so plain `gmail-cli messages list ...` returns a compact TOON payload.
- Use `--output table` (or global `--format text`) for human-readable output.
- Use `--output json` for full payload (ids, threadId, snippet, headers, internalDate).

## See Also

- `messages-view.md` — view a single message
- `messages-search.md` — `messages search` alias
- `../query-guide.md` — Gmail query syntax
