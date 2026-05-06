# translation-audit

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Review an existing `(source, target)` pair against the full 5-gate suite and emit a diff report.

Part of the [translation-toolkit](../..) plugin. Operational spec
Claude loads is [`SKILL.md`](SKILL.md); this README is for humans.

## Why a separate audit skill

Forward skills (`translation-i18n`, `translation-doc`, `translation-creative`)
calibrate their gates to "don't block legitimate stylistic restructuring
during draft → revise". That calibration is wrong when the target is
fixed and the question is **"is this target acceptable"**.

Audit runs the **full M1 + M2 + S1 + S2 + I1** matrix and
**upgrades S1 + S2 from SHOULD to HARD** — sub-threshold verdicts
become FAIL (not WARN), giving the reviewer a concrete triage queue.
This is the only context in the toolkit where S1 / S2 produce HARD
failures, and the only skill whose output is a **review document**
rather than a translated artifact. Layer 3 (DRAFT / REFLECT / IMPROVE)
is intentionally skipped — the user-provided target is the unit under
review.

## Inputs

| Input | Required | Notes |
|---|---|---|
| `source` | Yes | Any format the toolkit can parse (`.po` / `.json` / `.xliff` / `strings.xml` / `.strings` / `.md` / `.mdx` / plain text) |
| `existing target` | Yes | File path or inline string. Format MAY differ from source (migration audit, vendor delivery review). |
| `intake-spec` | Recommended | From `translation-intake`. If missing, run intake against the source first. Carries `mode` / `register` / locale pair, all of which inform S2 strictness and I1 framing. |
| `glossary_path` | Optional | Defaults to `<repo>/docs/i18n/glossary-{target_locale}.md` |

## Pipeline

```
intake-spec (from translation-intake; or auto-inferred from source)
        │
Layer 2 — Preparation
        ├── parse BOTH source and target (formats may differ)
        ├── protect-pass on BOTH sides (dual tokenization makes M1
        │   count-parity check meaningful)
        ├── source analysis on BOTH sides (target may exhibit issues
        │   independent of source)
        └── glossary resolve (4-tier; resolves against source terms,
            checks compliance against target)
        │
Layer 3 — SKIPPED (user-provided target is the unit under review)
        │
Layer 4 — Verification (FULL M1 + M2 + S1 + S2 + I1; S1 + S2 upgraded HARD)
        │
Layer 5 — Output
        ├── diff report (markdown; 6 sections; NO rewrite)
        └── audit-trail.json (full provenance)
```

## Verification gate matrix

The full matrix with stricter semantics — the reason this skill exists.

| Gate | Tier in audit | What it checks |
|---|---|---|
| **M1** | HARD | Compare source / target placeholder counts after dual protect-pass. Diff format records `source_count` / `target_count` / `missing_in_target` / `extra_in_target` per chunk. |
| **M2** | HARD | Project glossary compliance. Violations reported per term with `project_glossary` vs `target_used` and tier / audit_path provenance. PASS_ADVISORY still applies to `notes: context-dependent` entries. |
| **S1** | **HARD** (was SHOULD) | Subagent translates target → source-language; embedding-cosine similarity vs original source. Threshold = **0.85**. Below threshold → **FAIL** in the diff report, not WARN. |
| **S2** | **HARD** (was SHOULD) | LLM JUDGE classifies the existing target's register and compares against the register expected from source + intake-spec. Mismatch → **FAIL**. JUDGE rationale included so the reviewer can decide whether the mismatch is an acceptable shift or a defect. |
| **I1** | INFO | Untranslatability handling — for every source phrase flagged untranslatable, the target must show a borrow / explain / approximate handling. Missing handling reported, never blocks. |

**Why S1 / S2 upgrade to HARD here**: WARN-only is calibrated for the
forward skills' draft → revise loop. When the target is fixed, every
objective and structured-judgment issue should surface as a concrete
failure for the reviewer's triage queue. M2's `notes: context-dependent`
PASS_ADVISORY exception is preserved — that exception is about the
entry, not the gate tier.

## Diff report

A markdown document per [`protocols/diff-report.md`](protocols/diff-report.md)
with six sections: header (paths + timestamp + intake snapshot +
glossary version), summary verdict, per-gate verdict block (M1 / M2 /
S1 / S2 / I1 with diffs), inline issues with line refs, recommendations
(guidance, not edits), and a sign-off block for reviewer decision capture.

Improvement suggestions appear per inline issue but the report **never**
writes a corrected target. The reviewer applies fixes downstream
(typically by re-running `translation-{i18n,doc,creative}` on the source,
or by hand-editing and re-auditing).

## Output paths

Default emit (caller may override via the service interface):

- `<target_path>.audit.md` — diff report
- `<target_path>.audit-trail.json` — machine-readable companion

Audit never modifies the target file on disk.

## When to use

- Pre-merge translation review
- Vendor / agency delivery quality check
- Regression check after a re-translation
- Internal QA gate before publishing a localized release
- A/B comparison between two competing translations of the same source
  (run twice, once per candidate)

## When NOT to use

- Forward translation — use `translation-{i18n,doc,creative}`
- Intake clarification alone — use [`translation-intake`](../translation-intake)
- Producing a competing translation — audit will not generate one

## Web search policy

ON by default. Audit mode benefits the most from web search across the
four active skills — L3 (web) glossary lookups frequently surface
authoritative target forms the existing target ignored. Override to
OFF only for offline runs (e.g. on a network-isolated CI host):

```
--web-search=off
```

## Roles

Same vocabulary as the rest of the toolkit, **minus WRITER / REVISER**
which Layer 3's skip removes:

- **CRITIC** — produces the structured 4D / 5D critique on the existing
  target during S2 / I1 framing; never rewrites
- **BACK-TRANSLATOR** — blind target → source retranslation, used by S1
- **JUDGE** — register classification, used by S2

## What this skill does NOT do

- **Does NOT rewrite the existing target.** Audit is read-only by design.
  Layer 3 is skipped; no `--produce-target` flag exists (that path is a
  forward skill).
- **Does NOT apply improvement suggestions** — they're guidance for the
  reviewer, not edits.
- **Does NOT change file format.** No write-back. The original target
  file on disk is untouched.
- **Does NOT bypass M1 / M2 / S1 / S2.** No `--bypass-gates` flag
  (anti-pattern per spec Decision #15). All five gates run.
- **Does NOT prompt during I1.** Untranslatability handling present in
  the target is recorded; missing handling is reported as an issue.
- **Does NOT replace human reviewer judgment.** FAIL verdicts on S1 / S2
  flag issues for review; the diff report's sign-off section captures
  the ship / no-ship decision, not the skill.

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/diff-report.md`](protocols/diff-report.md) ·
  [`checklists/audit-completeness-checklist.md`](checklists/audit-completeness-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/protect-pass-spec.md`](references/protect-pass-spec.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
- Forward skills: [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative)
