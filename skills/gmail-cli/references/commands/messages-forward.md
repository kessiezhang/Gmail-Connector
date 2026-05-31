> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# messages forward — Forward a Message

Forward an existing message to one or more recipients.

## Usage

```bash
gmail-cli messages forward <MESSAGE-ID> --to ADDR [--body "..."] [--cc ADDR] [--attach FILE]...
```

## Options

- `-t, --to` (required, repeatable): Forward target
- `-b, --body` (optional): Note prepended above the forwarded content
- `--cc` (optional, repeatable): CC recipient
- `--attach` (optional, repeatable): Additional attachment to add

## Examples

```bash
gmail-cli messages forward 18a3f... --to teammate@example.com

gmail-cli messages forward 18a3f... \
  --to teammate@example.com \
  --body "FYI — see thread below."
```
