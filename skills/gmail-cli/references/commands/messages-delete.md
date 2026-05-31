> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# messages delete — Permanent Delete

Permanently delete a message. **Irreversible** — always confirm with the user.

## Usage

```bash
gmail-cli messages delete <MESSAGE-ID> [--yes]
```

## Options

- `--yes`: Skip the interactive confirmation prompt (still requires user approval at the agent layer)

## Examples

```bash
gmail-cli messages delete 18a3f...
```

## See Also

- `messages-trash.md` — reversible alternative
