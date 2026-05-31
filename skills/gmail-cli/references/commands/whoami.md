# whoami — Verify Authentication

Report the active Gmail account and confirm credentials work.

## Usage

```bash
gmail-cli whoami [--format text|json]
```

## Output

Human-readable line by default:

```
gmail-cli: signed in as user@example.com (account: personal)
```

JSON form for automation:

```bash
gmail-cli --format json whoami
# {"data":{"email":"user@example.com","account":"personal","scopes":[...]}}
```

## See Also

- `config.md` — sign in / switch account
