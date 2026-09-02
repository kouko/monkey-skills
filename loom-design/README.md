# loom-design

> **Two stations that turn a rough idea into a confirmed intent and a spec
> the user has read back in their own words, and two tools that give a
> product its principles and its look.** loom-design drafts; it never
> grades. Every verdict on what it produces is rendered in `loom-code`'s
> review station, by an agent that did not write the draft.

**Status**: v1.0.0 — 4 skills. Breaking: the pre-1.0 skills, scripts and
split READMEs were deleted, not renamed. See [CHANGELOG.md](CHANGELOG.md).
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: part of [`monkey-skills`](https://github.com/kouko/monkey-skills)

---

## The two stations

| Station | Produces | Read it |
|---|---|---|
| `capture-intent` | `docs/loom/intent/<change-id>.md` — the change in the user's words, with `status: confirmed` | [SKILL.md](skills/capture-intent/SKILL.md) |
| `write-spec` | `docs/loom/<change-id>/spec.md` — requirements, decisions and who made each, current-state evidence, UI flows | [SKILL.md](skills/write-spec/SKILL.md) |

`capture-intent` is the door for a change that starts as an idea rather
than a plan. It interviews, writes the intent, and hands off — to
`write-spec` when the change needs design, straight to `loom-code`'s
`write-plan` when it does not. Without loom-design installed, `write-plan`
does both jobs itself, less well.

## The two tools

| Tool | Produces | Read it |
|---|---|---|
| `product-principles` | `PRINCIPLES.md` — Who, Non-negotiables (≥3), Won't do, Failure we must avoid, Fixed choices, and a `ratified-by: <name> <date>` line the user's own yes puts there | [SKILL.md](skills/product-principles/SKILL.md) |
| `design-system` | `docs/loom/DESIGN.md` — colour, type, layout and component tokens for a GUI; a conventions stub for TUI/CLI | [SKILL.md](skills/design-system/SKILL.md) |

A tool runs when you ask for it, produces one file, and stops.
`design-system` never blocks a change: a missing DESIGN.md is a note, not
a gate. `product-principles` is different — for a change marked
`kind: product`, loom-code's checker refuses the change until a
`PRINCIPLES.md` exists with at least three non-negotiables and a
`ratified-by:` line, because nobody but the user can ratify it.

## The two decision points

loom-design owns the first two of the three questions a change ever asks
its user. The third (`did it do it?`) belongs to `loom-code`'s ship
station.

1. **① Is this what you want?** — `capture-intent` restates the change in
   plain words, with no file paths, module names or script names in the
   problem statement, and waits for a yes. Nothing downstream accepts an
   intent that is not `status: confirmed`.
2. **② You do X and you see Y — right?** — `write-spec` reads the visible
   behaviour back, asked only for a product change and never for an
   engineering one, and records the answer as `confirmed-behavior:`.

An irreversible fork — deleting data, a public interface, a one-way
migration — is folded into whichever of ① or ② is open and phrased as its
consequence, rather than asked as a separate question.

## Requires loom-code ≥ 1.0

loom-design reads, and never writes, `loom-code`'s contract package:
`contract/manifest.yaml` declares the artifact schemas, and
`contract/templates/` holds the blank of each. `plugin.json` declares
`requires-contract: ">=1.0"`, and every station and tool begins with

```bash
python3 <loom-code>/scripts/loom_checker.py contract --require 1.0
```

which blocks on a mismatch rather than drafting against a contract it does
not understand. The checker itself is loom-code's; loom-design never runs
the gates, only names them.

## Install

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-design@monkey-skills
claude plugin list | grep loom-design     # expect: enabled
```

`loom-code` installs the same way and is required. The plugins compose
only through plugin-qualified skill names such as `loom-design:write-spec`,
the contract package, and the project's own `docs/loom/` artifacts — never
through another plugin's private `hooks/`, `skills/` or `scripts/` paths.

### Codex CLI

There is no marketplace on Codex; the plugin is read from the checkout and
loom-code's checker is scaffolded into the repo as
`.codex/hooks/loom_checker.py`. See loom-code's README for the one command
that writes it, and run `/hooks` when it tells you to — an untrusted Codex
hook is skipped silently, which looks exactly like a passing check.

## Running the tests

```bash
python3 -m pytest loom-design/scripts/
```

One invocation collects all three station directories — `interface/`,
`principles/`, `spec/`. `scripts/pytest.ini` sets
`--import-mode=importlib` so same-named test modules can sit side by side,
and `pythonpath` puts the station directories back on `sys.path` for bare
sibling imports. `test_unified_pytest_root.py` pins that arrangement, so
a fan-out into one job per directory cannot come back by accident.

## Licence

MIT, as part of `monkey-skills`.
