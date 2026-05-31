# gmail-connector

A small set of tools for reading Gmail from the command line. Designed to be portable, sharable, and runnable on any machine with Python 3.10+.

## What's in this repo

```
gmail-connector/
└── skills/
    └── gmail-cli/        # the actual CLI (a Claude Code skill, but stands alone)
```

Right now there's one tool, [skills/gmail-cli/](skills/gmail-cli/). It's a single-file Python CLI that reads your Gmail (list, view, search messages/threads/labels/attachments). v1 is read-only on purpose — sending and modifying come later, once the read path is trusted.

## Quick start

```bash
git clone https://github.com/<you>/gmail-connector.git
cd gmail-connector/skills/gmail-cli
```

Then follow the per-skill setup at [skills/gmail-cli/README.md](skills/gmail-cli/README.md). The short version:

1. Create your own Google OAuth client ([5-step walkthrough](skills/gmail-cli/references/setup.md)).
2. Drop `client_secret.json` at `~/.config/gmail-cli/client_secret.json`.
3. Run `./scripts/gmail-cli config --account personal` — the shim auto-creates a venv and installs deps.
4. `./scripts/gmail-cli whoami` to confirm.

That's it. Each user creates their own OAuth client (it's tied to *their* Google project, not yours), so the repo can be shared without sharing credentials.

## Why a "skill"?

Each tool here is structured as a Claude Code skill — a folder with `SKILL.md` (instructions for AI agents), `scripts/` (the executable), and `references/` (per-command docs). That's just a layout convention; the tools work fine when invoked directly from a regular shell.

## Repo layout conventions

- **One skill per directory** under `skills/`.
- Each skill is self-contained: its own `requirements.txt`, its own venv, its own tests. No shared state across skills.
- Per-skill files (venv, downloaded credentials, caches) are gitignored.

## Contributing / sharing

This is primarily a personal project, but the code is MIT-licensed — feel free to fork and adapt. If you find a bug in `gmail-cli` that's not specific to your setup, an issue or PR is welcome.

## License

[MIT](LICENSE).
