# loom-code

> **Five stations that carry one change from a plan to a merged pull
> request, with functional verification reused until functional content changes.**
> loom-code assumes you know basic software engineering, not this plugin:
> it asks you three questions per change and decides the rest itself,
> because the quality comes from machines checking machines — the agent
> that writes is never the agent that reviews.

**Status**: v1.9.0 — 5 skills. See [CHANGELOG.md](CHANGELOG.md).
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: part of [`monkey-skills`](https://github.com/kouko/monkey-skills)

---

## The five stations

| Station | Produces | Read it |
|---|---|---|
| `write-plan` | `docs/loom/<change-id>/plan.md` — a task DAG | [SKILL.md](skills/write-plan/SKILL.md) |
| `build` | tested functional commits | [SKILL.md](skills/build/SKILL.md) |
| `review` | generated `docs/loom/<change-id>/attestation.json` | [SKILL.md](skills/review/SKILL.md) |
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
field of the operative artifacts — intent, spec, plan, and attestation. `loom-design`
reads it and declares `requires-contract`; `loom-workflow` does not —
only its `decision-map` skill runs `contract --require` before a
delivery. Only loom-code writes it. `contract/templates/` holds the
blank of each.

## The checker

`scripts/loom_checker.py` is the deterministic layer (`--list-rules` is the
source of truth). `finalize-review` runs functional verification once and
generates content-bound evidence. The publication hook later recomputes the
digest and validates that evidence without replaying package tests or probes.

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

### Codex

Install `loom-code` through the Codex plugin marketplace. Its installed
`PreToolUse` hook owns publication interception; adopting repositories no
longer carry a checker copy, copied contract, or trust ledger.

## Licence

MIT, as part of `monkey-skills`.
