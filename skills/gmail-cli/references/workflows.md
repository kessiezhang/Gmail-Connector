# Common Workflow Patterns

> **v1 status note.** Workflows below that use `messages modify`, `messages send`, `drafts *`, `messages reply`, `labels delete/rename`, etc. depend on commands planned for v2. The read-only steps (`messages list`, `messages view`, `threads view`, `attachments list/download`, `whoami`, `env`) work today.

Multi-step operations and common workflows with `gmail-cli`. All snippets assume the shim is on `scripts/gmail-cli` (relative to the skill installation directory).

For snippets that pipe to `jq`, request JSON explicitly: `--format json`.

## Inbox Triage

### List → Read → Label → Archive

```bash
# 1. Find unread in inbox
scripts/gmail-cli messages list --query "is:unread in:inbox"

# 2. Read the top message
scripts/gmail-cli messages view <MESSAGE-ID> --markdown

# 3. Apply a follow-up label and archive (remove INBOX)
scripts/gmail-cli messages modify <MESSAGE-ID> \
  --add-label Followup \
  --remove-label INBOX

# 4. Confirm
scripts/gmail-cli messages list --label Followup --limit 10
```

## Bulk Triage by Sender

```bash
# 1. Find every message from a noisy sender
IDS=$(scripts/gmail-cli --format json messages list \
  --query "from:notifications@example.com newer_than:7d" \
  | jq -r '.data[].id')

# 2. Apply a label and archive each (confirm count first)
echo "$IDS" | wc -l
for id in $IDS; do
  scripts/gmail-cli messages modify "$id" \
    --add-label "Auto/Notifications" \
    --remove-label INBOX
done
```

> Always confirm the candidate set with the user before running the loop.

## Send → Track → Follow Up

```bash
# 1. Send
MSG=$(scripts/gmail-cli --format json messages send \
  --to dest@example.com \
  --subject "Q3 plan" \
  --body "Initial proposal attached." \
  --attach ./q3-plan.pdf | jq -r '.data.id')

# 2. Star it for follow-up
scripts/gmail-cli messages modify "$MSG" --add-label STARRED

# 3. Pull the thread later
THREAD=$(scripts/gmail-cli --format json messages view "$MSG" \
  | jq -r '.data.threadId')
scripts/gmail-cli threads view "$THREAD" --markdown
```

## Draft, Iterate, Send

```bash
# 1. Create draft
DRAFT=$(scripts/gmail-cli --format json drafts create \
  --to dest@example.com \
  --subject "Q3 plan" \
  --body "Draft body" | jq -r '.data.id')

# 2. Iterate
scripts/gmail-cli drafts update "$DRAFT" --body "Revised body"

# 3. Send when ready (confirm with user)
scripts/gmail-cli drafts send "$DRAFT"
```

## Attachment Roundup

```bash
# 1. Find messages with attachments
scripts/gmail-cli messages list \
  --query "has:attachment newer_than:30d larger:5M"

# 2. List attachments on one
scripts/gmail-cli attachments list <MESSAGE-ID>

# 3. Download a specific attachment
scripts/gmail-cli attachments download <MESSAGE-ID> <ATTACHMENT-ID> \
  --out ./downloads/report.pdf
```

## Label Hygiene

```bash
# 1. Audit user labels
scripts/gmail-cli --format json labels list \
  | jq '.data[] | select(.type == "user") | {id,name,messagesTotal}'

# 2. Rename
scripts/gmail-cli labels rename Label_42 --name "Receipts/2026"

# 3. Delete an unused label (confirm first)
scripts/gmail-cli labels delete Label_99
```

## Reply Quickly to a Recent Thread

```bash
# 1. Find the most recent message from someone
LATEST=$(scripts/gmail-cli --format json messages list \
  --query "from:boss@example.com" --limit 1 \
  | jq -r '.data[0].id')

# 2. Reply (preserves threading via In-Reply-To)
scripts/gmail-cli messages reply "$LATEST" --body "Got it, thanks."
```

## Auth Recovery

```bash
# 1. Check who we're signed in as
scripts/gmail-cli whoami

# 2. If failing, show resolved env
scripts/gmail-cli env

# 3. Re-run setup
scripts/gmail-cli config --account personal
```

## See Also

- `commands/README.md` — full command index
- `query-guide.md` — Gmail search query syntax
- `troubleshooting.md` — auth, quota, and rate-limit fixes
