> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# messages modify — Change Message Labels

Add and/or remove labels on a single message. **Mutating** — confirm before bulk runs.

## Usage

```bash
gmail-cli messages modify <MESSAGE-ID> [--add-label LABEL]... [--remove-label LABEL]...
```

## Options

- `--add-label` (repeatable): Label name or ID to add
- `--remove-label` (repeatable): Label name or ID to remove

System labels are accepted by name: `INBOX`, `UNREAD`, `STARRED`, `IMPORTANT`, `SPAM`, `TRASH`, `CATEGORY_PERSONAL`, etc.

## Examples

```bash
# Archive (remove from INBOX)
gmail-cli messages modify 18a3f... --remove-label INBOX

# Mark read
gmail-cli messages modify 18a3f... --remove-label UNREAD

# Apply user label and star
gmail-cli messages modify 18a3f... --add-label Receipts --add-label STARRED
```

## See Also

- `labels-apply.md` / `labels-remove.md` — convenience shorthands
- `threads-modify.md` — apply to every message in a thread
