# Setup — creating your own Google OAuth client

`gmail-cli` does not ship with shared OAuth credentials. You create your own — it takes about 3 minutes — and the resulting `client_secret.json` stays on your machine.

## Why you need this

Google requires every app that touches Gmail to identify itself with an OAuth client ID. That ID is tied to a Google Cloud project you own. The CLI then uses your client ID to ask *you* for permission to read *your own* Gmail.

This is a one-time setup per Google account.

## Steps

### 1. Open Google Cloud Console

Go to https://console.cloud.google.com and sign in with the Google account whose Gmail you want to read.

### 2. Create a project

- Top bar → project dropdown → **New Project**.
- Name it something like `gmail-cli-personal`. Click **Create**.
- Wait a few seconds, then make sure the new project is selected in the project dropdown.

### 3. Enable the Gmail API

- Left nav → **APIs & Services** → **Library**.
- Search for "Gmail API". Click it. Click **Enable**.

### 4. Configure the OAuth consent screen

- Left nav → **APIs & Services** → **OAuth consent screen**.
- User type: **External**. Click **Create**.
- App name: `gmail-cli` (or anything). User support email: yourself. Developer contact: yourself. Click **Save and continue**.
- **Scopes**: skip (we request scopes from the CLI). Click **Save and continue**.
- **Test users**: click **Add users**, add the email address whose Gmail you'll be reading. Click **Save and continue**.
- Review → **Back to dashboard**.

> Leaving the app in "Testing" mode is fine for personal use. You don't need to publish it. Tokens for test users are valid for 7 days at a time and re-auth is one command.

### 5. Create the OAuth client

- Left nav → **APIs & Services** → **Credentials**.
- Click **Create Credentials** → **OAuth client ID**.
- Application type: **Desktop app**. Name: `gmail-cli`. Click **Create**.
- A dialog shows your client ID and secret. Click **Download JSON**.
- Move the downloaded file to where the CLI looks for it:

```bash
mkdir -p ~/.config/gmail-cli
mv ~/Downloads/client_secret_*.json ~/.config/gmail-cli/client_secret.json
```

(If you'd rather keep it elsewhere, set `GMAIL_CLI_CLIENT_SECRET=/path/to/your.json` in your shell.)

### 6. Sign in

```bash
./scripts/gmail-cli config --account personal
```

A browser window opens. Approve the requested scope (read Gmail). The CLI stores the resulting access + refresh tokens in your OS keyring (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux). The `client_secret.json` only gets used during this OAuth handshake; it's not a secret in the same sense — it identifies your app, not you.

```bash
./scripts/gmail-cli whoami
# → user@example.com (account: personal)
```

You're done.

## Sharing the CLI with friends

Each friend repeats steps 1–6 with their own Google account. The CLI source can be shared freely; the OAuth client cannot (it's tied to your project's quota).

## Revoking access later

- https://myaccount.google.com/permissions → find your `gmail-cli` app → **Remove access**.
- The next CLI command will fail with a re-auth message. Run `gmail-cli config --account <name>` to sign back in.

## Common setup problems

| Symptom | Fix |
|---|---|
| "Access blocked: this app's request is invalid" | The OAuth consent screen wasn't fully completed. Go back to step 4. |
| "Access blocked: <you> has not completed verification" | You're signed in as a non-test-user. Add yourself in step 4's "Test users" section. |
| "Error 400: redirect_uri_mismatch" | The client type isn't "Desktop app". Recreate it in step 5. |
| `OAuth client secret not found at ~/.config/gmail-cli/client_secret.json` | You haven't moved the downloaded file. See step 5. |
