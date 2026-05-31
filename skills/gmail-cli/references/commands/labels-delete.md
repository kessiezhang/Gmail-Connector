> **Status: planned for v2 - not yet implemented.** This document describes the intended interface; the command currently exits with code 64.

# labels delete — Delete Label

Delete a user label. Messages keep their labels' history but the label itself is removed.

## Usage

```bash
gmail-cli labels delete <LABEL-ID> [--yes]
```

System labels (`INBOX`, `UNREAD`, etc.) cannot be deleted.
