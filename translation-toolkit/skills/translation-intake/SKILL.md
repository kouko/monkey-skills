---
name: translation-intake
description: Layer 1 of translation-toolkit. Clarifies translation parameters (5 axes — mode / register / strategy / locale / domain — plus skopos) via auto-detect or explicit user input. Output is an intake-spec consumed by downstream skills (translation-i18n / -doc / -creative / -audit).
version: 0.1.0
---

# translation-intake

## Purpose

Translates user intent into a structured 5-axis intake spec that downstream skills consume. This is the **Layer 1 owner** in the translation-toolkit 5-layer pipeline; subsequent layers (parse / protect / draft / reflect / improve / verify / output) are owned by the four format-specialist skills (`translation-i18n` / `translation-doc` / `translation-creative` / `translation-audit`), each of which **reads** the intake spec produced here.

## Modes

- **auto** (default): single source-analysis call infers all 5 axes from source content. Zero-friction default; locale pair still user-supplied.
- **explicit** (`--explicit` / `-e`): user is prompted for each of 5 axes + skopos. Use when the auto inference misfired or when the user has strong opinions source content alone wouldn't reveal.

See [`protocols/intake-auto.md`](protocols/intake-auto.md) and [`protocols/intake-explicit.md`](protocols/intake-explicit.md) for the per-mode pipeline / interaction details.

## When to use

- Invoked by `using-translation-toolkit` (the router) when user input lacks clear axis signals — e.g. a short raw-text request with no format / domain hint.
- Invoked directly by the user via the `--intake` flag on any of the 4 active skills, when they want to inspect / lock the 5-axis spec before the format-specialist runs.
- Re-invoked with `--explicit` after a dissatisfying auto pass to override one or more axes interactively (auto inferences seed the prompts as defaults).

## When NOT to use

- The user already passes a complete intake spec (all 5 axes + locale pair + skopos) on the command line — skip intake and let the format-specialist consume the supplied values directly.
- The task isn't translation. See the router's "When NOT to use" for cross-plugin routing (copywriting → `copywriting-toolkit`; original-language docs → `domain-teams:docs-team`).

## What this skill does NOT do

- **Does not translate.** Intake captures parameters only; the format-specialist skill is responsible for actually generating any target text. A user who pastes source text directly here gets an intake-spec response, never a translation.
- **Does not parse format files.** PO / JSON / XLIFF / Markdown AST parsing is each format-specialist's Layer 2 responsibility, not intake's.
- **Does not run verification gates.** M1 / M2 / S1 / S2 / I1 are Layer 4, owned by the format-specialists.
- **Does not invoke downstream skills via the Skill tool.** The harness performs the actual chained invocation; intake just emits the spec.

## 5 axes (canonical reference: orthogonal-axes)

| Axis | Allowable values | Notes |
|---|---|---|
| **mode** | `literal` \| `faithful` \| `localized` \| `transcreation` | controls reflection-axis count (4D vs 5D) and S1 threshold |
| **register** | `formal` \| `neutral` \| `warm` \| `playful` | checked downstream by S2 gate |
| **strategy** | `domestication` \| `foreignization` | independent of mode |
| **locale** | BCP-47 (e.g. `en-US`, `ja-JP`, `zh-TW`, `zh-CN`) | both source and target REQUIRED at invocation; never auto-inferred |
| **domain** | one or more from {`general`, `ui`, `tech.software`, `tech.web`, `tech.data`, `tech.crypto`, `gov`, `legal`, `medical`, `finance`, `marketing`, `statistics`, `typography`} | comma-join when multiple (e.g. `ui,tech.software`) |

Plus **skopos / intent** — free-form one-liner answering "who reads this and what action should they take?".

The full canonical definitions, mode-strategy interactions, and auto-inference heuristic table live in the plugin-level reference at `scripts/canonical/orthogonal-axes.md` (functional copies of which are distributed into each of the 4 active skills' `references/` directories — see "Reference distribution" below).

## Output

Writes an intake spec consumed by the next skill in the pipeline. Schema (subset of the audit-trail `intake` block — see canonical `audit-trail-spec.md` §`intake`):

```json
{
  "mode": "literal | faithful | localized | transcreation",
  "register": "formal | neutral | warm | playful",
  "strategy": "domestication | foreignization",
  "source_locale": "BCP-47",
  "target_locale": "BCP-47",
  "domain": "<single value or comma-joined values from the 13-domain taxonomy>",
  "intent": "free-form short string (skopos hint)",
  "inferred": {
    "mode": true,
    "register": true,
    "strategy": true,
    "domain": true
  },
  "inferred_values": {
    "mode": "faithful"
  }
}
```

Shape rules:

- `inferred` — per-axis boolean: `true` means the value came from auto-inference, `false` means user-supplied. `source_locale` and `target_locale` are always implicitly `false` (never auto-inferred).
- `inferred_values` — populated only when the user **overrode** an auto-inferred axis; records what the heuristic *would* have picked. Empty `{}` when not in use.
- `domain` is currently a single string (comma-joined when multiple). Structured-array form is deferred to schema v0.2.

Downstream skills read this as either an inline JSON blob in the conversation or via a sidecar `intake-spec.json` file, depending on runtime convention.

## Audit-trail integration

This skill uses `lib/audit_trail.AuditTrailBuilder` (plugin-level shared library at `translation-toolkit/scripts/lib/audit_trail.py`) to record intake decisions:

```python
from lib.audit_trail import AuditTrailBuilder

builder = AuditTrailBuilder()
builder.set_intake(
    mode=...,
    register=...,
    strategy=...,
    source_locale=...,
    target_locale=...,
    domain=...,
    intent=...,
    inferred={"mode": True, "register": True, "strategy": True, "domain": True},
)
# When --explicit overrides an auto-inferred axis, also call:
builder.add_inferred_value("mode", "faithful")  # auto's pick, preserved for analysis
```

`AuditTrailBuilder` and the broader audit-trail JSON schema are documented in the canonical spec at `translation-toolkit/scripts/canonical/audit-trail-spec.md`. (Intake's intake block is a subset of the full audit-trail schema that the format-specialist later completes with `glossary_resolution`, `chunks`, `gate_verdicts`, `untranslatables`, `sources_used`, `warnings`.)

## Reference distribution

`translation-intake` is intentionally **NOT** in the `ACTIVE_SKILLS` list of `scripts/distribute.py`. Rationale:

- The 4 format-specialist skills receive functional copies of the full canonical reference set (`core-loop` / `4d-reflection` / `5d-effectiveness` / `orthogonal-axes` / `verification-gates` / `audit-trail-spec` / `protect-pass-spec` + typography + corpus + glossaries) because they actually execute Layers 2-5 and need the prompts / gate logic at hand.
- Intake only needs the **5-axis taxonomy + auto-inference heuristics** (already inlined in `protocols/intake-auto.md`) and the **intake block subset of the audit-trail schema** (already inlined here in §Output and §Audit-trail integration).
- Adding intake to `ACTIVE_SKILLS` would distribute 7+ irrelevant prompt / gate files into this skill, bloating its surface area for no behavioral gain.

When intake authors need to consult the full canonical orthogonal-axes / audit-trail-spec, they read it via the plugin path (`translation-toolkit/scripts/canonical/orthogonal-axes.md` etc.) rather than from a local copy. Drift is impossible because intake holds no copy.

## Reference

- [`protocols/intake-auto.md`](protocols/intake-auto.md) — auto-mode pipeline + worked example
- [`protocols/intake-explicit.md`](protocols/intake-explicit.md) — explicit-mode interaction + sample transcript
- `../../scripts/canonical/orthogonal-axes.md` — canonical 5-axis definitions + auto-inference heuristics
- `../../scripts/canonical/audit-trail-spec.md` — full audit-trail JSON schema (intake block is the subset this skill writes)
- `../../scripts/lib/audit_trail.py` — `AuditTrailBuilder` Python helper
- `../using-translation-toolkit/SKILL.md` — router that invokes intake when input is ambiguous
- `../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` — full design spec (Layer 1 Intake section + 13-domain taxonomy)
