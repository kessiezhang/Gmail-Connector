# Gmail CLI Commands Reference

Complete reference for all gmail-cli commands. Each command has its own detailed documentation file.

## Output Modes

Use global output flags for consistent agent behavior:

```bash
gmail-cli --format toon <command>
gmail-cli --format json <command>
```

- Global: `--format text|json|toon`, `--toon-max-items <N>`
- Default global format: `toon`
- List overrides: most `*-list` commands also accept `--output table|text|toon|json`

## Messages

| Command | Description | File |
|---------|-------------|------|
| `messages list` | List messages by Gmail query | [messages-list.md](messages-list.md) |
| `messages view` | View one message (headers/body) | [messages-view.md](messages-view.md) |
| `messages search` | Alias for `list --query` | [messages-search.md](messages-search.md) |
| `messages send` | Send a new message | [messages-send.md](messages-send.md) |
| `messages reply` | Reply to a message | [messages-reply.md](messages-reply.md) |
| `messages forward` | Forward a message | [messages-forward.md](messages-forward.md) |
| `messages modify` | Add/remove labels on a message | [messages-modify.md](messages-modify.md) |
| `messages trash` | Move to Trash (reversible) | [messages-trash.md](messages-trash.md) |
| `messages delete` | Permanent delete | [messages-delete.md](messages-delete.md) |

## Threads

| Command | Description | File |
|---------|-------------|------|
| `threads list` | List threads | [threads-list.md](threads-list.md) |
| `threads view` | View thread with all messages | [threads-view.md](threads-view.md) |
| `threads modify` | Label change on every message in thread | [threads-modify.md](threads-modify.md) |
| `threads trash` | Trash a whole thread | [threads-trash.md](threads-trash.md) |
| `threads delete` | Permanent delete | [threads-delete.md](threads-delete.md) |

## Labels

| Command | Description | File |
|---------|-------------|------|
| `labels list` | List system + user labels | [labels-list.md](labels-list.md) |
| `labels create` | Create user label | [labels-create.md](labels-create.md) |
| `labels rename` | Rename a label | [labels-rename.md](labels-rename.md) |
| `labels delete` | Delete a label | [labels-delete.md](labels-delete.md) |
| `labels apply` | Add a label to a message | [labels-apply.md](labels-apply.md) |
| `labels remove` | Remove a label from a message | [labels-remove.md](labels-remove.md) |

## Drafts

| Command | Description | File |
|---------|-------------|------|
| `drafts list` | List drafts | [drafts-list.md](drafts-list.md) |
| `drafts view` | View a draft | [drafts-view.md](drafts-view.md) |
| `drafts create` | Create a draft | [drafts-create.md](drafts-create.md) |
| `drafts update` | Update a draft | [drafts-update.md](drafts-update.md) |
| `drafts send` | Send an existing draft | [drafts-send.md](drafts-send.md) |
| `drafts delete` | Delete a draft | [drafts-delete.md](drafts-delete.md) |

## Attachments

| Command | Description | File |
|---------|-------------|------|
| `attachments list` | List attachments on a message | [attachments-list.md](attachments-list.md) |
| `attachments download` | Download an attachment | [attachments-download.md](attachments-download.md) |

## Configuration & Utility

| Command | Description | File |
|---------|-------------|------|
| `config` | Configure account + secure credential storage | [config.md](config.md) |
| `whoami` | Verify authentication | [whoami.md](whoami.md) |
| `env` | Show environment config | [env.md](env.md) |

## Quick Reference

### Most Common Operations

```bash
# Auth check
gmail-cli whoami

# List unread
gmail-cli messages list --query "is:unread in:inbox"

# View one
gmail-cli messages view 18a3f...

# Send
gmail-cli messages send \
  --to dest@example.com \
  --subject "Hello" \
  --body "Hi there."

# Apply a label
gmail-cli labels apply 18a3f... Receipts

# Trash
gmail-cli messages trash 18a3f...
```

### Inbox Triage Workflow

```bash
# Find unread
gmail-cli messages list --query "is:unread in:inbox"

# Read the top one
gmail-cli messages view <ID> --markdown

# Label it and archive (remove INBOX)
gmail-cli messages modify <ID> --add-label Followup --remove-label INBOX
```

### Send & Track

```bash
# Draft first
DRAFT=$(gmail-cli --format json drafts create \
  --to dest@example.com \
  --subject "Q3 plan" \
  --body "Draft body" | jq -r '.data.id')

# Update body
gmail-cli drafts update "$DRAFT" --body "Final body"

# Send it
gmail-cli drafts send "$DRAFT"
```

## See Also

- `../query-guide.md` — Gmail search query syntax
- `../workflows.md` — common workflow patterns
- `../troubleshooting.md` — auth and rate-limit fixes
