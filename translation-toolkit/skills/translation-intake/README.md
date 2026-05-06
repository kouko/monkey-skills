# translation-intake

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Layer 1 of translation-toolkit — clarifies the 5 axes (mode / register / strategy / locale / domain) plus skopos.
> Runs before any translation specialist starts work.

Part of the [translation-toolkit](../..) plugin. Operational spec
Claude loads is [`SKILL.md`](SKILL.md); this README is for humans.

## Why a separate intake skill

The four format-specialist skills (`translation-i18n`, `translation-doc`,
`translation-creative`, `translation-audit`) all need the same five
parameters before they can do their job: **what kind of translation**,
**how formal**, **how culturally adapted**, **between which locales**,
**in which domain**. Hard-coding defaults silently pushes choices the
user might not have made — `register=neutral` ships fine for a runbook
but is wrong for a marketing tagline; `mode=literal` produces unusable
ad copy.

Intake captures these axes once, in one place, and downstream skills
read the result. The auto mode infers from the source content; the
explicit mode walks the user through each axis when auto is wrong or
the user has strong opinions the source alone doesn't reveal.

## The 5 axes

| Axis | Allowable values | Affects |
|---|---|---|
| `mode` | `literal` / `faithful` / `localized` / `transcreation` | Reflection-axis count (4D vs 5D) and S1 gate threshold |
| `register` | `formal` / `neutral` / `warm` / `playful` | S2 register-preservation gate |
| `strategy` | `domestication` / `foreignization` | Cultural-reference handling; independent of mode |
| `locale` | BCP-47 source + target (e.g. `en-US` → `ja-JP`) | Required at invocation; never auto-inferred |
| `domain` | One or more from a 13-domain taxonomy (`general`, `ui`, `tech.software`, `tech.web`, `tech.data`, `tech.crypto`, `gov`, `legal`, `medical`, `finance`, `marketing`, `statistics`, `typography`) | Glossary subset selection + critique framing |

Plus **skopos / intent** — a free-form one-liner answering "who reads
this and what action should they take?".

## Two modes

| Mode | Trigger | What happens |
|---|---|---|
| `auto` (default) | No flag | Single source-analysis call infers all 5 axes; locale pair still user-supplied |
| `explicit` (`--explicit` / `-e`) | User flag | Walks the user through each axis; auto inferences seed prompts as defaults |

Per-mode pipeline + worked examples in
[`protocols/intake-auto.md`](protocols/intake-auto.md) and
[`protocols/intake-explicit.md`](protocols/intake-explicit.md).

## When to use

- Invoked by [`using-translation-toolkit`](../using-translation-toolkit)
  when input lacks clear axis signals (short raw text, no format / domain hint)
- Invoked directly via `--intake` on any of the 4 active skills, when
  you want to inspect / lock the spec before the format-specialist runs
- Re-invoked with `--explicit` after a dissatisfying auto pass to override
  one or more axes interactively

## When NOT to use

- User already passes a complete intake spec (all 5 axes + locale pair
  + skopos) — skip intake; let the format-specialist consume it directly
- Task is not translation — see the router's "When NOT to use" for
  cross-plugin routing

## Output

Writes an `intake-spec` consumed by the next skill in the pipeline.
Schema (subset of the audit-trail `intake` block):

```json
{
  "mode": "literal | faithful | localized | transcreation",
  "register": "formal | neutral | warm | playful",
  "strategy": "domestication | foreignization",
  "source_locale": "BCP-47",
  "target_locale": "BCP-47",
  "domain": "single value or comma-joined values",
  "intent": "free-form skopos hint",
  "inferred": {
    "mode": true, "register": true, "strategy": true, "domain": true
  },
  "inferred_values": {
    "mode": "faithful"
  }
}
```

`inferred` is per-axis: `true` means auto-inferred, `false` means
user-supplied. `source_locale` and `target_locale` are always
implicitly `false`. `inferred_values` records what the heuristic
*would* have picked when `--explicit` overrides an inferred axis.

## What this skill does NOT do

- **Does not translate.** Intake captures parameters only. A user who
  pastes source text directly here gets an intake-spec response, never
  a translation.
- **Does not parse format files.** PO / JSON / XLIFF / Markdown AST
  parsing is each format-specialist's Layer 2 job.
- **Does not run verification gates.** M1 / M2 / S1 / S2 / I1 are Layer 4,
  owned by the format-specialists.
- **Does not invoke downstream skills.** The harness performs the
  chained invocation; intake just emits the spec.

## Audit-trail integration

Intake decisions flow into the shared audit trail via
`lib/audit_trail.AuditTrailBuilder`. See
[`SKILL.md`](SKILL.md) §"Audit-trail integration" for the
`builder.set_intake(...)` and `builder.add_inferred_value(...)` calls,
and `scripts/canonical/audit-trail-spec.md` for the full schema.

## Reference distribution note

`translation-intake` is intentionally **NOT** in the `ACTIVE_SKILLS`
list of `scripts/distribute.py`. Intake only needs the 5-axis taxonomy
+ auto-inference heuristics (already inlined in `protocols/intake-auto.md`)
and the intake-block subset of the audit-trail schema (inlined in
`SKILL.md`). Distributing the full canonical reference set here would
add 7+ irrelevant prompt / gate files for no behavioral gain. Drift is
impossible because intake holds no copy.

## See also

- [`SKILL.md`](SKILL.md) — operational spec (5-axis table, output schema,
  audit-trail integration)
- [`protocols/intake-auto.md`](protocols/intake-auto.md) — auto-mode pipeline
- [`protocols/intake-explicit.md`](protocols/intake-explicit.md) —
  explicit-mode interaction + sample transcript
- Plugin overview: [`../../README.md`](../../README.md)
- Router: [`../using-translation-toolkit`](../using-translation-toolkit)
- Downstream: [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative) ·
  [`translation-audit`](../translation-audit)
- Canonical sources: `../../scripts/canonical/orthogonal-axes.md` ·
  `../../scripts/canonical/audit-trail-spec.md`
