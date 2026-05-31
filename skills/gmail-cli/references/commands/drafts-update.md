> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# drafts update — Update a Draft

## Usage

```bash
gmail-cli drafts update <DRAFT-ID> \
  [--to ADDR] [--cc ADDR] [--bcc ADDR] \
  [--subject "..."] [--body "..."] [--html] [--attach FILE]...
```

Any flag passed replaces that field on the draft. Recipients (`--to`, `--cc`, `--bcc`) replace the existing list — pass them all if you want to keep prior values.

## Examples

```bash
gmail-cli drafts update r123 --body "Final body"
```
