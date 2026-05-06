---
name: translation-audit
description: Audit existing translations against source. Takes (source, existing-target) input, runs full 5-gate verification, outputs diff report + improvement suggestions. No translation produced. Web search ON, all gates run with stricter semantics.
version: 0.1.0
---

# translation-audit

Layer 2 + 4 + 5 owner for **review of an existing (source, target) pair** in `translation-toolkit`. Reads an `intake-spec` produced by `translation-intake` (Layer 1) — or auto-infers one from the source — parses **both** source and target independently, **skips Layer 3** (no DRAFT / REFLECT / IMPROVE — the user-provided target is the unit under review), runs the **full M1 + M2 + S1 + S2 + I1** gate matrix with stricter tier semantics, and emits a diff report plus an `audit-trail.json`. Read-only — never rewrites the target, never writes back to the source format.

This is the only skill in the toolkit whose output is a **review document**, not a translated artifact.

## Inputs

- **source** — file path (any format the toolkit can parse: `.po` / `.json` / `.xliff` / `strings.xml` / `.strings` / `.md` / `.mdx` / plain text) or an inline source string.
- **existing target** — file path or inline string (REQUIRED — distinguishes this skill from `translation-i18n`, `translation-doc`, `translation-creative`, all of which produce a target). Source format and target format MAY differ — e.g. source PO + target XLIFF in a migration audit, or source markdown + target plain text in a vendor delivery review.
- **intake-spec** — from `translation-intake`. If invoked directly without one, run intake against the **source** first (`--intake` flag) before continuing. Intake-spec carries `mode` / `register` / `strategy` / `domain` / `intent` / locale pair, all of which inform the strictness of S2 and the framing of I1.
- **glossary_path** *(optional)* — repo-local project glossary (L1 tier of the 4-tier resolver). Defaults to `<caller_repo>/docs/i18n/glossary-{target_locale}.md`; missing → fall through to L2 bundled glossary in `glossary/`.

Service-interface contract (the four shared fields plus `web_search`) is defined in the design spec §Service Interface; no per-skill duplication here.

## When to use

- Routed in by `using-translation-toolkit` when the user supplies **both** a source and an existing translation and asks to review / QA / verify / audit / score / compare.
- Invoked directly by name when the user already knows audit is the right specialist.
- Typical scenarios: pre-merge translation review, vendor / agency delivery quality check, regression check after a re-translation, internal QA gate before publishing a localised release, A/B comparison between two competing translations of the same source (run twice, one per candidate).
- **Not** for forward translation — use `translation-i18n` / `translation-doc` / `translation-creative`. **Not** for intake clarification alone — use `translation-intake`.

## Web search policy

ON by default per `using-translation-toolkit` §"Web search trade-off note" (spec Decision #15). Audit mode benefits the most from web search across all four active skills — the goal is the most thorough review the runtime can produce, and L3 (web) glossary lookups frequently surface authoritative target forms that the existing target ignored. Override to OFF only for offline runs (e.g. on a network-isolated CI host):

```
--web-search=off
```

When OFF, glossary resolution stops at L2 (bundled) — L3 (web) is skipped, L4 (LLM-fallback) still runs. For audit work, leaving web search ON is recommended even at the cost of slower runs.

## Pipeline

This skill executes **Layers 2, 4, 5** of the toolkit's 5-layer pipeline. (Layer 1 — intake — is the upstream `translation-intake` skill. **Layer 3 is intentionally skipped** — see below.)

### Layer 2: Preparation

1. **Parse BOTH source and target.** Auto-detect each format independently from extension + content sniffing. Source and target are NOT assumed to share a format — migration-audit and vendor-delivery-review scenarios commonly mix formats. Per-format read rules are the same as those used by the format-specialist skills (i18n PO/JSON/XLIFF/strings; doc markdown AST + code/URL/HTML protect); audit implements them locally as part of its own Layer 2 — see `protocols/diff-report.md` for the audit-specific output expectations.

2. **Protect-pass on BOTH sides.** Mask every placeholder span on the source AND the target with `⟦P:NN⟧` sentinels per `references/protect-pass-spec.md` (8 base classes — ICU plural, curly braces, printf, fenced code, inline code, HTML, URL, email), then layer format-specific extensions (markdown AST patterns / i18n placeholder patterns / creative URL+brand-token patterns) as appropriate. The dual protect-pass is what makes M1's count parity check meaningful — both sides must be tokenized under the same rules before counts are compared.

3. **Source analysis on BOTH sides.** Per chunk, extract candidate difficult terms from the source AND from the target. The target may exhibit its own terminology issues independent of the source (mistranslated coined terms, drifted glossary entries, inconsistent register markers) — these are caught here, not at M2 alone. Feeds glossary resolve and the JUDGE prompts.

4. **Glossary resolve.** 4-tier fallthrough per `references/orthogonal-axes.md` and the plugin-level `docs/glossary-format-spec.md`:
   1. **L1 project** — `<repo>/docs/i18n/glossary-{target_locale}.md` (caller-supplied, highest priority)
   2. **L2 bundled** — `glossary/glossary-{source}--{target}.md` (Pontoon / GNOME / JLT / e-Stat / Tokyo / Cabinet / NAER ingested at build time)
   3. **L3 web search** — only if web search is ON; cite URL in audit-trail
   4. **L4 LLM fallback** — model proposes a translation; flagged in audit-trail with tier `L4` and lowest trust

   Resolution runs against the **source** terms; results feed M2's compliance check against the **target**.

### Layer 3: SKIPPED

There is no DRAFT / REFLECT / IMPROVE in audit mode. The user-provided target is the unit under review — the skill's job is to verify, not regenerate. This is the load-bearing structural difference between `translation-audit` and the three forward-translation skills.

If a caller wants both a fresh translation AND a review against the existing target, run `translation-{i18n,doc,creative}` to produce the fresh translation, then run `translation-audit` twice (once per candidate target) — the audit skill itself never produces a competing translation.

### Layer 4: Verification (full M1 + M2 + S1 + S2 + I1, stricter semantics)

Per `references/verification-gates.md` §"Per-skill gate application". Audit mode runs the **full gate matrix** and **upgrades S1 and S2 from SHOULD to HARD** — sub-threshold gate verdicts produce `FAIL` (not `WARN`) and surface in the diff report's per-gate verdict block. Audit mode is the **only** context in the toolkit where S1 / S2 produce HARD failures.

| Gate | Tier in audit | Action |
|---|---|---|
| **M1** | HARD | Compare source / target placeholder counts after dual protect-pass. Same regex check as the forward skills; the diff format (`source_count` / `target_count` / `missing_in_target` / `extra_in_target`) is recorded per chunk in the report. |
| **M2** | HARD | Project glossary compliance — every L1-mandated source term must render as its mapped target form in the existing target. Violations are reported per term with `project_glossary` vs `target_used` and `tier` / `audit_path` provenance. PASS_ADVISORY still applies to `notes: context-dependent` entries. |
| **S1** | HARD (was SHOULD) | Subagent translates target → source-language; compute embedding-cosine similarity vs the original source. Threshold = **0.85** (the audit baseline; mode-conditional thresholds from forward skills do not apply because the existing target was not produced by this run). Below threshold → **FAIL** in the diff report, not WARN. SKIPPED only when the runtime provides no subagent isolation; SKIPPED in audit is itself a quality concern and surfaces prominently. |
| **S2** | HARD (was SHOULD) | LLM JUDGE classifies the existing target's register and compares against the register expected from the source + intake-spec. Mismatch → **FAIL**, not WARN. JUDGE rationale is included in the diff report so the reviewer can decide whether the "mismatch" is an acceptable register-shift decision or an actual translation defect. |
| **I1** | INFO | Untranslatability decisions present and justified — for every source phrase Layer 2 source-analysis flagged as untranslatable, the target must show a borrow / explain / approximate handling. Missing handling = report it; never block. Same non-interactive contract as elsewhere — no user prompt is ever raised. |

**Why S1 and S2 are HARD here**: when reviewing an existing translation, the goal is to flag every objective and structured-judgment issue for the reviewer. WARN-only verdicts in the forward skills are calibrated to "don't block legitimate stylistic restructuring during draft → revise"; that calibration does not apply when the target is fixed and the question is "is this target acceptable". HARD verdicts in the diff report make the reviewer's triage queue concrete.

**M2 advisory exception is preserved.** `notes: context-dependent` glossary entries still produce PASS_ADVISORY (not FAIL) — that exception is about the entry, not the gate tier.

### Layer 5: Output

1. **Diff report (no rewrite).** A markdown document per `protocols/diff-report.md`. Six sections: header (paths + timestamp + intake snapshot + glossary version), summary verdict, per-gate verdict block, inline issues with line refs, recommendations, sign-off. The report includes **improvement suggestions** per inline issue but **never** writes a corrected target; the reviewer applies fixes downstream (typically by re-running `translation-{i18n,doc,creative}` on the source, or by hand-editing the existing target and re-auditing).

2. **`audit-trail.json` with full provenance.** Schema per `references/audit-trail-spec.md`. Records: intake snapshot, every gate verdict with diff and metadata, every glossary resolution with tier + audit_path, every untranslatability decision present in the target. The audit trail is the machine-readable companion to the human-readable diff report.

3. **No format roundtrip / write-back.** Audit never modifies the target file on disk. The diff report and audit trail are emitted as new files (default: `<target_path>.audit.md` and `<target_path>.audit-trail.json`; the caller may override paths via the service interface).

## Roles

Same vocabulary as the rest of the toolkit (per `using-translation-toolkit` §Roles vocabulary), minus WRITER / REVISER which Layer 3's skip removes:

- **CRITIC** — produces the structured 4D / 5D critique on the existing target during S2 / I1 framing; never rewrites.
- **BACK-TRANSLATOR** — blind target → source retranslation, used by S1.
- **JUDGE** — register classification, used by S2.

Roles are behavioral. Any LLM model can fill any role; this skill specifies behavior, not models.

## When to use vs forward skills (recap)

| Situation | Skill |
|---|---|
| Source only — produce target | `translation-i18n` / `translation-doc` / `translation-creative` |
| Source + existing target — review only | `translation-audit` |
| Source + existing target — review AND produce alternative | run forward skill, then audit each candidate (audit twice) |
| No source, just want intake clarification | `translation-intake` |

## What this skill does NOT do

- **Does NOT rewrite the existing target.** Audit is read-only by design. The output is a review document; the reviewer (or a subsequent forward-skill run) applies fixes.
- **Does NOT generate any translation.** Layer 3 is skipped. There is no `--produce-target` flag — that path is a forward skill, not audit.
- **Does NOT apply improvement suggestions.** Suggestions appear in the diff report as concrete alternative phrasings or structural fixes; they are guidance for the reviewer, not edits to the file.
- **Does NOT change file format.** No format roundtrip / write-back. The original target file on disk is untouched.
- **Does NOT run intake automatically when source is unparseable.** If Layer 2 step 1 fails on the source or target, the run halts at the audit-completeness checklist (items 1-3) with a parse-error message; intake can re-run after the parse error is fixed.
- **Does NOT bypass M1 / M2 / S1 / S2.** No `--bypass-gates` flag exists (anti-pattern per spec Decision #15). All five gates run; the diff report records every verdict.
- **Does NOT prompt the user during I1.** Untranslatability decisions present in the target are recorded; missing handling is reported as an issue. No interactive prompts.
- **Does NOT replace human reviewer judgment.** A FAIL verdict on S2 (register) or S1 (back-translation similarity) flags an issue for review; whether the issue blocks shipping is a decision the diff report's sign-off section captures, not a decision the skill makes.

## See also

- `protocols/diff-report.md` — diff report markdown template (6 sections + worked example)
- `checklists/audit-completeness-checklist.md` — 5-item completeness check (source readable / target readable / both parseable / all 5 gates ran / report includes required fields)
- `references/protect-pass-spec.md` — canonical protect-pass algorithm and `⟦P:NN⟧` token format (applied to BOTH source and target in audit mode)
- `references/verification-gates.md` — gate semantics + audit-trail entry shapes; §"Per-skill gate application" lists audit's full-matrix-with-stricter-semantics row
- `references/audit-trail-spec.md` — full audit-trail JSON schema (gate_verdicts shape, glossary_resolution shape)
- `references/4d-reflection.md` — critique axes that frame S2 / I1 in audit mode
- `references/5d-effectiveness.md` — Effectiveness axis used when intake `mode == transcreation` (creative-target audits)
- `references/orthogonal-axes.md` — 5 intake axes + 4-tier glossary resolver definition
- `references/core-loop.md` — DRAFT / REFLECT / IMPROVE contracts (referenced for Layer 3 SKIPPED rationale only; not run here)
- `references/audit-trail-spec.md` — full audit-trail JSON schema
- `glossary/glossary-{source}--{target}.md` — bundled L2 glossary (5 pair files)
- `typography/jlreq-summary.md` — JLReq typography rules for `target_locale=ja-JP`
- `typography/clreq-summary.md` — CLReq typography rules for `target_locale=zh-CN` / `zh-TW`
- `../using-translation-toolkit/SKILL.md` — router (when to land here)
- `../translation-intake/SKILL.md` — Layer 1 owner
- `../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` — full design spec (Sub-skill Responsibility Matrix + Decision #17 on audit-as-separate-skill)
