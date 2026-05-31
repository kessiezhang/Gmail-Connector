> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# threads modify — Modify Thread Labels

Add and/or remove labels on every message in a thread.

## Usage

```bash
gmail-cli threads modify <THREAD-ID> [--add-label LABEL]... [--remove-label LABEL]...
```

## Examples

```bash
# Archive whole thread
gmail-cli threads modify 18a3f... --remove-label INBOX

# Apply Followup label across the conversation
gmail-cli threads modify 18a3f... --add-label Followup
```

## See Also

- `messages-modify.md` — single-message variant
