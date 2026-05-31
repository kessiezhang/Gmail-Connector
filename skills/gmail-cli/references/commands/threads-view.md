# threads view — View a Thread

View a thread with all of its messages in chronological order.

## Usage

```bash
gmail-cli threads view <THREAD-ID> [--markdown] [--full]
```

## Arguments

- `thread-id` (required): Thread ID (returned by `threads list`)

## Options

- `--markdown`: Render bodies as Markdown
- `--full`: Include full headers and all body parts for every message

## Examples

```bash
gmail-cli threads view 18a3f... --markdown
gmail-cli --format json threads view 18a3f... --full
```
