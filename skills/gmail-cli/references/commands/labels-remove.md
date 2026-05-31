> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# labels remove — Remove Label from Message

Convenience shorthand for `messages modify --remove-label`.

## Usage

```bash
gmail-cli labels remove <MESSAGE-ID> <LABEL>
```

## Examples

```bash
gmail-cli labels remove 18a3f... INBOX   # archive
```
