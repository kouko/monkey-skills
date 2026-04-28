# kobo-auth

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Authentication lifecycle for Kobo. Owns the credential file and binary.

Part of the [tsundoku](../..) plugin. The skill that Claude actually loads
is [`SKILL.md`](SKILL.md); this README is for humans browsing the folder.

## When to use this skill

| Trigger | Action |
|---|---|
| Very first time using tsundoku | Flow A (interactive activation) |
| `kobo-library` reports auth required | Flow A |
| Switching to a different Kobo account | Flow A or D |
| Already have credentials from a prior install | Flow B (import) |

Login is a once-per-account event. After that, [`kobo-library`](../kobo-library)
takes over for daily search/download.

## Quick start

```bash
# Install kobodl binary (~14 MB, idempotent)
bash scripts/kobo_install.sh

# Interactive activation
bash scripts/kobo_login.sh add
# → kobodl prints "Open kobo.com/activate and enter XXXXXX"
# → user opens browser, signs in, enters the code

# Verify
bash scripts/kobo_login.sh status
```

For prior installs (legacy `~/KobodlLibrarySync/` shell script, or upstream's
`~/.config/kobodl/`):

```bash
bash scripts/kobo_install.sh
bash scripts/kobo_login.sh import-from ~/KobodlLibrarySync/config/kobodl.json
```

## What lands on disk

After successful login:

```
~/.tsundoku/kobo/
├── auth/                              chmod 700
│   └── kobodl.json                    chmod 600  ← Kobo session credentials
└── bin/kobodl-macos                   ~14 MB upstream binary
```

`kobodl.json` is **equivalent to your Kobo password**. Never commit, paste,
or upload.

## Files in this folder

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | The skill spec Claude loads. 200+ lines, all flows. |
| [`scripts/kobo_install.sh`](scripts/kobo_install.sh) | Binary download (idempotent) |
| [`scripts/kobo_login.sh`](scripts/kobo_login.sh) | Subcommands: `status` / `add` / `remove` / `import-from` / `path` |

The path resolver `tsundoku_paths.sh` lives at the plugin root
([`tsundoku/lib/`](../../lib)) and is sourced by every script.

## See also

- [`tsundoku` README](../..) — overall plugin orientation
- [`kobo-library`](../kobo-library) — what consumes the auth from this skill
