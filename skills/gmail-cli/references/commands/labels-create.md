> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# labels create — Create Label

Create a user label.

## Usage

```bash
gmail-cli labels create --name NAME [--color HEX] [--visibility show|hide] [--message-visibility show|hide]
```

## Options

- `-n, --name` (required): Label name (supports `/` for nesting, e.g. `Project/Q3`)
- `--color` (optional): Background color hex (Gmail accepts a fixed palette)
- `--visibility` (optional): `show` or `hide` in the label list (default `show`)
- `--message-visibility` (optional): `show` or `hide` on individual messages (default `show`)

## Examples

```bash
gmail-cli labels create --name Receipts
gmail-cli labels create --name "Project/Q3" --color "#16a766"
```
