# loom-code

> **Five stations that carry one change from a plan to a merged pull
> request, and a checker that refuses a push whose review never happened.**
> loom-code assumes you know basic software engineering, not this plugin:
> it asks you three questions per change and decides the rest itself,
> because the quality comes from machines checking machines — the agent
> that writes is never the agent that reviews.

**Status**: v1.0.0 — 5 skills. Breaking: the pre-1.0 skills, agents and
scripts were deleted, not renamed. See [CHANGELOG.md](CHANGELOG.md).
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: part of [`monkey-skills`](https://github.com/kouko/monkey-skills)

---

## The five stations

| Station | Produces | Read it |
|---|---|---|
| `write-plan` | `docs/loom/<change-id>/plan.md` — a task DAG | [SKILL.md](skills/write-plan/SKILL.md) |
| `build` | commits, one per task, each carrying a `Task: <id>` trailer | [SKILL.md](skills/build/SKILL.md) |
| `review` | `docs/loom/<change-id>/review.json` — verdicts, probes, findings | [SKILL.md](skills/review/SKILL.md) |
| `ship` | the pull request, the memory trailers, the merge | [SKILL.md](skills/ship/SKILL.md) |
| `maintain` | an intent, out of an alert or an incident | [SKILL.md](skills/maintain/SKILL.md) |

Say what you want; `write-plan` is the door. With `loom-design` installed,
`capture-intent` and `write-spec` sit upstream of it; without it,
`write-plan` does both jobs itself.

## The three questions you are asked

Everything else is decided for you, with the reason recorded.

1. **Is this what you want?** — your intent, restated in plain words
   before any code exists.
2. **You type X and you see Y — right?** — the visible behaviour, asked
   only for a product change, never for an engineering one.
3. **Did it do it?** — you read a blind-run report written by an agent
   that never touched the change, not the diff.

An irreversible fork (deleting data, a public interface, a one-way
migration) is added to whichever of ① or ② is open, phrased as its
consequence.

## The contract package

`contract/manifest.yaml` declares the stations, the actions, and every
field of the four artifacts — intent, spec, plan, review. `loom-design`
reads it and declares `requires-contract`; `loom-workflow` does not —
only its `decision-map` skill runs `contract --require` before a
delivery. Only loom-code writes it. `contract/templates/` holds the
blank of each.

## The checker

`scripts/loom_checker.py` is the whole deterministic layer — 20 rules,
listed by `--list-rules`. It runs on the SessionStart hook and before
`git push` / `gh pr create` / `gh pr merge`, and it recomputes rather than
believes: it re-runs the package-test and adversarial probes itself and
reads the exit code. It stops a slip, not a determined cheat.

## Install

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-code@monkey-skills
claude plugin list | grep loom-code       # expect: enabled
```

`loom-design` and `loom-workflow` install the same way. The three are
independently installable: loom-code needs neither of them, and when a
station reaches an optional handoff whose sibling is absent it reports that
handoff as N/A with the reason and continues where its own contract allows.
They compose only through plugin-qualified skill names such as
`loom-design:write-spec`, the contract package, and the project's own
`docs/loom/` artifacts — never through another plugin's private `hooks/`,
`skills/` or `scripts/` paths.

### Codex CLI

Codex has no plugin marketplace, so the checker is copied into the repo
instead:

```bash
python3 scripts/codex_scaffold.py --repo .
python3 scripts/codex_scaffold.py --self-test
```

The first writes `.codex/hooks.json` and a stamped copy of the checker; the
second fires a fake push at that copy to prove it runs. Neither proves
Codex will run it: an untrusted hook is skipped in silence, and only a
command Codex itself issues goes through its hook engine. That probe — a
doomed push whose answer must start with `BLOCK push.` — belongs to the
station (`write-plan` step 0b), which tells the user to run `/hooks` once
when git answers instead of the checker.

## Licence

MIT, as part of `monkey-skills`.
