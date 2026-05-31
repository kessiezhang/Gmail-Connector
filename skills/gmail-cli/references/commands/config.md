# config — Configure Account & Credentials

Configure the active Gmail account and store OAuth credentials in the OS secure backend.

## Usage

```bash
gmail-cli config [--account NAME] [--service-account PATH] [--migrate] [--show] [--open-token-page]
```

## Options

- `--account` (optional): Friendly account name (e.g. `personal`, `work`)
- `--service-account` (optional): Path to a Google service-account JSON for non-interactive auth
- `--migrate`: Move legacy plaintext credentials into the OS keychain and remove them from disk
- `--show`: Print non-secret config (account list, default account, scopes)
- `--open-token-page`: Open the OAuth consent screen in the browser (default behavior on first run)

## Behavior

- Tokens and refresh tokens are stored in Keychain (macOS), Credential Manager (Windows), or `pass`/Secret Service (Linux).
- The CLI **never** prints full tokens or refresh tokens.
- Multiple accounts are supported via `--account NAME`; the first one configured becomes the default.

## Examples

```bash
# First-time setup (interactive OAuth)
gmail-cli config --account personal

# Add a second account
gmail-cli config --account work

# Show current config
gmail-cli config --show

# Migrate legacy on-disk credentials
gmail-cli config --migrate
```

## See Also

- `whoami.md` — verify the active account
- `env.md` — show resolved environment
