# env — Show Environment

Print resolved environment configuration: active account, default format, token storage backend, scopes, and any overrides from environment variables.

## Usage

```bash
gmail-cli env [--format text|json]
```

## Examples

```bash
gmail-cli env
gmail-cli --format json env | jq '.data.scopes'
```

Useful when troubleshooting `whoami` failures or unexpected account selection.
