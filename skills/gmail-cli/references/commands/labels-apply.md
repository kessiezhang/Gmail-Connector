> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# labels apply — Apply Label to Message

Convenience shorthand for `messages modify --add-label`.

## Usage

```bash
gmail-cli labels apply <MESSAGE-ID> <LABEL>
```

`<LABEL>` may be a label name or ID.

## Examples

```bash
gmail-cli labels apply 18a3f... Receipts
```

## See Also

- `messages-modify.md` — multi-label, same call
