> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# drafts create — Create a Draft

Create a draft message. Same flag surface as `messages send`, but does not transmit.

## Usage

```bash
gmail-cli drafts create --to ADDR --subject "..." --body "..." \
  [--cc ADDR] [--bcc ADDR] [--html] [--attach FILE]...
```

## Examples

```bash
gmail-cli drafts create \
  --to dest@example.com \
  --subject "Q3 plan" \
  --body "Initial draft."

# Capture the draft ID for follow-up edits
DRAFT=$(gmail-cli --format json drafts create \
  --to dest@example.com --subject "Q3" --body "draft" \
  | jq -r '.data.id')
```

## See Also

- `drafts-update.md` — edit before sending
- `drafts-send.md` — transmit
