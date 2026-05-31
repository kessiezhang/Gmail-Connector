# messages view — View a Message

Fetch and render a single message.

## Usage

```bash
gmail-cli messages view <MESSAGE-ID> [--markdown] [--raw] [--full]
```

## Arguments

- `message-id` (required): Gmail message ID (returned by `messages list`)

## Options

- `--markdown`: Render the body as Markdown (HTML → Markdown conversion)
- `--raw`: Output the raw RFC 822 source (no TOON/JSON envelope)
- `--full`: Include full headers, all body parts, and inline attachments metadata

## Examples

```bash
# Default: compact TOON envelope with key headers + body snippet
gmail-cli messages view 18a3f1234567890

# Markdown body for terminal reading
gmail-cli messages view 18a3f1234567890 --markdown

# Raw RFC 822 (for piping to mail tools)
gmail-cli messages view 18a3f1234567890 --raw

# Full payload for automation
gmail-cli --format json messages view 18a3f1234567890 --full
```

## See Also

- `messages-list.md` — find message IDs
- `attachments-list.md` — list attachments on the message
