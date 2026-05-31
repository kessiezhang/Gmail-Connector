# Troubleshooting

Common failures with `gmail-cli` and how to recover.

## `whoami` reports no active account

```bash
gmail-cli whoami
# error: no account configured
```

Run `gmail-cli config --account <name>` to start the OAuth flow. On first run a browser window opens for consent; if it can't open, the CLI prints a URL — open it manually.

## OAuth token expired or revoked

```
error: invalid_grant — token has been expired or revoked
```

Re-authenticate the affected account:

```bash
gmail-cli config --account <name>
```

If multiple accounts share the same client credentials, only the affected one needs to re-auth.

## 429 / rate limit

The Gmail API enforces per-user (250 quota units/sec) and per-project quotas. The CLI retries with exponential backoff for transient `429` and `5xx` responses. If retries exhaust:

- Reduce `--limit` on list calls.
- Stagger bulk modify loops with a small `sleep` between calls.
- Check `gmail-cli env` for the active project — quota is per project.

## "Insufficient Permission" on send / modify

The token is missing a scope. Re-run `gmail-cli config --account <name>` and accept the full set of requested scopes. Read-only tokens cannot be promoted in place.

## Attachment download fails with `decoding error`

Gmail attachments are base64url-encoded. If a downloaded file looks corrupted:

- Confirm `--out` extension matches the `mimeType` reported by `attachments list`.
- Re-run with `--format json attachments list <MESSAGE-ID>` and inspect `size` vs the file you got.

## Multiple accounts: wrong one is used

```bash
gmail-cli env        # see resolved account + scope set
gmail-cli config --show
```

Pin the account explicitly with `--account <name>`, or change the default with `gmail-cli config --account <name> --set-default`.

## Tokens leaking into logs

The CLI never prints full tokens. If you see partial values, they should be the first/last few characters only (e.g. `ya29.…ABCD`). If full secrets ever appear in output, treat it as a bug and rotate via `gmail-cli config --account <name>`.

## See Also

- `commands/config.md`
- `commands/whoami.md`
- `commands/env.md`
