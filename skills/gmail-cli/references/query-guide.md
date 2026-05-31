# Gmail Query Guide

Gmail uses the same search-query syntax as the web UI. This guide collects the operators most useful from the CLI.

## Basics

| Operator | Example | Meaning |
|----------|---------|---------|
| `from:` | `from:boss@example.com` | Sender |
| `to:` | `to:me` | Recipient |
| `cc:` / `bcc:` | `cc:team@example.com` | Carbon copy |
| `subject:` | `subject:invoice` | Subject contains |
| `"phrase"` | `"weekly report"` | Exact phrase |
| `OR` / `AND` | `from:a@x.com OR from:b@x.com` | Boolean (caps required) |
| `-` | `is:unread -from:noreply@` | Negation |
| `()` | `(from:a@x.com OR from:b@x.com) is:unread` | Grouping |

## State

| Operator | Meaning |
|----------|---------|
| `is:unread` | Unread |
| `is:read` | Read |
| `is:starred` | Starred |
| `is:important` | Marked important |
| `is:snoozed` | Snoozed |
| `has:attachment` | Has at least one attachment |
| `has:drive` | Has a Google Drive link |
| `has:youtube` | Has a YouTube link |

## Folders / Labels

| Operator | Meaning |
|----------|---------|
| `in:inbox` / `in:trash` / `in:spam` | System folder |
| `in:anywhere` | Include Spam & Trash |
| `label:NAME` | Has a specific label |
| `category:primary` | Inbox category (also `social`, `promotions`, `updates`, `forums`) |

## Time

| Operator | Example |
|----------|---------|
| `newer_than:` | `newer_than:7d` (`d`, `m`, `y`) |
| `older_than:` | `older_than:1y` |
| `after:` | `after:2026/01/01` |
| `before:` | `before:2026/03/01` |

## Size

| Operator | Example |
|----------|---------|
| `larger:` | `larger:5M` (also `K`, `M`) |
| `smaller:` | `smaller:200K` |
| `size:` | `size:1000000` (bytes) |

## Attachments

| Operator | Example |
|----------|---------|
| `filename:` | `filename:pdf` or `filename:report.pdf` |
| `has:attachment` | Any attachment |

## Compound Examples

```bash
# Unread invoices in last 30 days
gmail-cli messages list --query "is:unread subject:invoice newer_than:30d"

# Big PDFs from a sender
gmail-cli messages list --query "from:vendor@example.com filename:pdf larger:5M"

# Inbox needing follow-up (starred but not yet replied)
gmail-cli messages list --query "in:inbox is:starred -in:sent"

# Anything mentioning a project, excluding noise
gmail-cli messages list --query '"project phoenix" -from:noreply@ newer_than:14d'
```

## See Also

- `commands/messages-list.md`
- `workflows.md`
