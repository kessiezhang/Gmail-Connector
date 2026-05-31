> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# messages send — Send a Message

Send a new email. **Mutating** — confirm with the user before running.

## Usage

```bash
gmail-cli messages send --to ADDR --subject "..." --body "..." \
  [--cc ADDR] [--bcc ADDR] [--from ALIAS] [--html] [--attach FILE]...
```

## Options

- `-t, --to` (required, repeatable): Recipient address
- `-s, --subject` (required): Subject line
- `-b, --body` (required): Body content (text by default; pass `--html` to send as HTML)
- `--cc` (optional, repeatable): CC recipient
- `--bcc` (optional, repeatable): BCC recipient
- `--from` (optional): Send from a configured alias (`Send mail as`)
- `--html`: Treat `--body` as HTML
- `--attach` (optional, repeatable): Path to a local file to attach
- `--reply-to-message-id` (optional): Set headers so the message threads under an existing one (use `messages reply` for the convenient form)

## Examples

```bash
# Plain text
gmail-cli messages send \
  --to dest@example.com \
  --subject "Hello" \
  --body "Hi there."

# HTML body with multiple recipients and attachment
gmail-cli messages send \
  --to a@example.com --to b@example.com \
  --cc team@example.com \
  --subject "Q3 update" \
  --html \
  --body "<p>See attached.</p>" \
  --attach ./report.pdf
```

## Output

Returns the new message ID and threadId. Use `--format json` to capture for follow-up:

```bash
MSG=$(gmail-cli --format json messages send \
  --to dest@example.com --subject "Hi" --body "Hi" \
  | jq -r '.data.id')
```

## See Also

- `messages-reply.md` — reply preserving threading
- `drafts-create.md` — draft first, send later
