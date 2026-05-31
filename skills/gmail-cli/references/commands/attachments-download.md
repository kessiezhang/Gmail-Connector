# attachments download — Download an Attachment

## Usage

```bash
gmail-cli attachments download <MESSAGE-ID> <ATTACHMENT-ID> [--out PATH]
```

## Options

- `--out` (optional): Output path. Defaults to `./<original-filename>`.

## Examples

```bash
# List then download
gmail-cli attachments list 18a3f...
gmail-cli attachments download 18a3f... ANGjdJ... --out /tmp/report.pdf
```

## Safety

Downloads count as a write (file system change). The agent must confirm before downloading attachments from messages whose origin is not pre-trusted.
