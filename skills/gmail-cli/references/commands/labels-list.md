# labels list — List Labels

List all labels (system + user) on the active account.

## Usage

```bash
gmail-cli labels list [--output table|text|toon|json]
```

## Examples

```bash
gmail-cli labels list
gmail-cli --format json labels list | jq '.data[] | select(.type == "user")'
```

## Output

Each entry includes `id`, `name`, `type` (`system` | `user`), `messagesUnread`, `messagesTotal`.
