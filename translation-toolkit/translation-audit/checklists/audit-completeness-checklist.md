# Audit completeness checklist — 5-item

> Run before Layer 5 emit. Any unchecked item halts the run with a clear
> actionable message; do not silently degrade. The five items combined
> are cheap (file-stat checks + AST construction status flags + gate
> verdict roll-up + report-section presence scan).
>
> The checklist is the "the audit is structurally complete" gate — it
> verifies the report is **about** to be emitted with all required
> machinery in place, not the **quality** of the audit verdicts (those
> are the gate verdicts themselves).

## The 5 items

- [ ] **1. Source readable.** The source file is accessible at the
      provided path AND the format was successfully detected (auto-detect
      from extension first, then content sniff). `inline string` source
      counts as readable when the string is non-empty. A source that
      fails this check halts at Layer 2 step 1 with a message like
      "source path `<path>` not readable" or "source format not
      recognised — supported extensions: .po / .json / .xliff /
      strings.xml / .strings / .md / .mdx / .markdown / .mdx; for plain
      text, set format explicitly via the service interface". The diff
      report is NOT emitted on failure of this item — there is nothing
      to audit.

- [ ] **2. Target readable.** The existing target file is accessible at
      the provided path AND its format was successfully detected. Target
      format MAY differ from source format (migration audits, vendor
      delivery reviews) — the check is that **target** is independently
      detectable, not that it matches source. A target that fails this
      check halts with "target path `<path>` not readable" or the same
      format-not-recognised message. The diff report is NOT emitted on
      failure — `translation-audit` cannot review a target it cannot
      parse.

- [ ] **3. Both formats parseable.** Beyond detection (item 1 + item 2),
      both source and target ASTs must be constructed without errors.
      Parseable ≠ readable: a well-formed file that fails the format-
      specific parser (e.g. PO with broken `msgid_plural` block,
      markdown with unterminated frontmatter, XLIFF with missing
      `<source>` element) trips this item. Halt with the parser's
      structured error (line / column / parse rule violated). The diff
      report is NOT emitted on failure — gates downstream depend on
      well-formed ASTs.

- [ ] **4. All 5 gates ran.** M1, M2, S1, S2, I1 must each have an
      attempt recorded in `audit-trail.json` `gate_verdicts`. A gate
      that did not attempt to run (silent skip) trips this item. The
      legitimate skip is **S1: SKIPPED** when the runtime provides no
      subagent isolation capability — that skip MUST be documented in
      `gate_verdicts.S1.metadata.isolation_capability: false` AND
      surfaced in the diff report's per-gate verdict block (per
      `protocols/diff-report.md` §3 "Per-gate verdict block — SKIPPED
      template"). Any other "did not run" condition is a pipeline bug
      and halts emit. M2 may legitimately produce `PASS_ADVISORY`
      (context-dependent entries); that is a verdict, not a skip, and
      passes this item. I1's `INFO` verdict with empty
      `untranslatables` list passes this item — the gate ran and found
      nothing to record.

- [ ] **5. Report includes all required sections.** Before emit, scan
      the rendered diff report for the six fixed sections per
      `protocols/diff-report.md` §"Report structure":
      1. Header (paths, timestamp, intake snapshot, glossary version)
      2. Summary verdict (overall + per-gate one-liner)
      3. Per-gate verdict block (one subsection per M1, M2, S1, S2, I1
         in that fixed order)
      4. Inline issues with line refs (one row per issue, with required
         fields per §4)
      5. Recommendations (bulleted list of next actions)
      6. Sign-off (template fields for reviewer name / date / decision
         / notes)

      Inline issues §4 must additionally have, per row: source line/col
      ref, target line/col ref, issue category (placeholder / glossary /
      register / accuracy / cultural), severity (HARD-FAIL / SHOULD-WARN
      / INFO), quoted source text, quoted target text, improvement
      suggestion. A missing field on any row halts emit with "issue row
      <N> missing field <name>".

## When to run

| Step | Items |
|---|---|
| Layer 2 step 1 (source parse) | 1 |
| Layer 2 step 1 (target parse) | 2 |
| Layer 2 step 2 (AST validation) | 3 |
| Layer 4 end (after all gates produced verdicts) | 4 |
| Layer 5 step 1 (report assembled, before emit) | 5 |

Items 1-3 are file / parse preflight — they halt early so the rest of
the pipeline doesn't run on broken inputs. Items 4-5 are post-pipeline
sanity checks — they catch silent skips and missing report sections
before the reviewer sees them.

## What this checklist does NOT cover

- **Gate verdict quality** — that's M1 / M2 / S1 / S2 / I1 themselves,
  recorded in `audit-trail.json` `gate_verdicts`. This checklist verifies
  the gates **ran**, not whether they **passed**.
- **Inline issue prioritisation** — recommendations §5 of the diff
  report orders by impact; this checklist verifies the section exists,
  not its content quality.
- **Sign-off completion** — the sign-off section is a template the
  human reviewer fills in after triage. This checklist verifies the
  template is present, not signed.
- **Source / target locale agreement with intake-spec** — that is the
  intake skill's responsibility (`translation-intake`); audit consumes
  the resolved intake and trusts it.
- **Format-specific roundtrip integrity** — audit never writes back to
  the target file, so there is no roundtrip to verify (vs
  `translation-doc`'s 6-item doc-quality-checklist).

## See also

- `../SKILL.md` §"Layer 2: Preparation" + §"Layer 4: Verification" +
  §"Layer 5: Output" — invokes this checklist at the four step
  boundaries listed above
- `../protocols/diff-report.md` — the report structure this checklist's
  item 5 verifies
- `../references/verification-gates.md` — the gate-verdict shapes whose
  presence this checklist's item 4 verifies
- `../references/audit-trail-spec.md` — the `gate_verdicts` schema the
  audit-trail JSON must conform to
