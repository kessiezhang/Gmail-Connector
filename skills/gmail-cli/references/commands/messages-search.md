# messages search — Search Messages

Alias for `messages list --query`.

## Usage

```bash
gmail-cli messages search "QUERY" [--limit N] [--output table|text|toon|json]
```

## Examples

```bash
gmail-cli messages search "from:boss@example.com has:attachment"
gmail-cli messages search "subject:invoice newer_than:30d" --limit 50
```

## See Also

- `messages-list.md` — full options
- `../query-guide.md` — query syntax
