> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# messages reply — Reply to a Message

Reply to an existing message, preserving In-Reply-To / References headers.

## Usage

```bash
gmail-cli messages reply <MESSAGE-ID> --body "..." [--reply-all] [--html] [--attach FILE]...
```

## Arguments

- `message-id` (required): The message being replied to.

## Options

- `-b, --body` (required): Reply body
- `--reply-all`: Include all original recipients (To + Cc)
- `--html`: Treat body as HTML
- `--attach` (repeatable): Attach a local file

## Examples

```bash
gmail-cli messages reply 18a3f... --body "Got it, thanks."

# Reply-all with attachment
gmail-cli messages reply 18a3f... --reply-all \
  --body "Updated draft attached." \
  --attach ./v2.pdf
```

## See Also

- `messages-send.md` — new message instead of reply
- `messages-forward.md` — forward to a new recipient
