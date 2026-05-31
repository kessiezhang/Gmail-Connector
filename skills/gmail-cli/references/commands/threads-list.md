# threads list — List Threads

List conversation threads matching a Gmail query.

## Usage

```bash
gmail-cli threads list [--query "QUERY"] [--label LABEL] [--limit N] [--output table|text|toon|json]
```

## Options

Same as `messages list`, but returns thread IDs instead of message IDs.

## Examples

```bash
gmail-cli threads list --query "is:unread in:inbox"
gmail-cli threads list --label Followup --limit 25
```

## See Also

- `threads-view.md` — expand a thread
- `messages-list.md` — list at the message level
