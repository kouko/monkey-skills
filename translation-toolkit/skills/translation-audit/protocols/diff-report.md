# Diff Report — markdown template for audit output

> Layer 5 step 1 of `translation-audit`. The diff report is the human-readable
> output of an audit run; the `audit-trail.json` is its machine-readable
> companion. Both are emitted; neither modifies the source or target file
> on disk.
>
> The report has six fixed sections in fixed order. Reviewers triage from
> top (summary) to bottom (sign-off). Per-gate detail and inline issues are
> the load-bearing middle; recommendations and sign-off close the loop with
> the human.

## Output filename

Default: `<target_path>.audit.md` next to the target. Caller may override
via the service interface output-path field. Audit-trail JSON sits beside
it as `<target_path>.audit-trail.json`.

## Report structure (six sections, fixed order)

### 1. Header

```markdown
# Translation audit — <source_basename> ↔ <target_basename>

- **Source path**: `path/to/source.po`
- **Target path**: `path/to/target.po`
- **Audit timestamp**: 2026-05-06T14:32:11Z
- **Source format**: PO (auto-detected)
- **Target format**: PO (auto-detected)
- **Source locale**: en-US
- **Target locale**: ja-JP
- **Intake snapshot**:
  - mode: faithful (auto-inferred)
  - register: neutral (caller-supplied)
  - strategy: domestication (auto-inferred)
  - domain: ui (auto-inferred)
  - intent: "consumer-app onboarding strings"
- **Glossary**:
  - L1: `<repo>/docs/i18n/glossary-ja-JP.md` v0.3.2
  - L2: `glossary/glossary-en-US--ja-JP.md` (build 2026-05-06)
  - L3: web search ON
- **Web search**: ON
- **Audit-trail JSON**: `path/to/target.po.audit-trail.json`
```

The header is the audit-trail's `intake` block + glossary metadata in
human-readable form. The audit-trail JSON is authoritative for downstream
tools; the header makes the report self-contained for human review.

### 2. Summary verdict

```markdown
## Summary

**Overall verdict**: FAIL

| Gate | Verdict | Rationale |
|---|---|---|
| M1 | FAIL | 1 chunk has placeholder count mismatch (chunk 2: source 5 / target 4) |
| M2 | FAIL | 2 L1 glossary terms ignored: `cancel` → `取消` (used: `キャンセル`); `submit` → `送信` (used: `提出`) |
| S1 | WARN | 1 of 5 chunks below 0.85 similarity (chunk 4: 0.78); audit S1 is HARD → reported as FAIL |
| S2 | PASS | Register matches intake (formal expected, formal judged) |
| I1 | INFO | 1 untranslatable phrase recorded (`御朱印` → borrow with gloss) |
```

Overall verdict aggregation:
- **PASS** — every gate is `PASS` or `PASS_ADVISORY` (M2) or `INFO` (I1) or `SKIPPED` (S1 only, with documented reason).
- **FAIL** — at least one gate is `FAIL`. In audit mode, S1 / S2 sub-threshold verdicts produce `FAIL` (not `WARN`) — they roll up into overall FAIL.
- **NEEDS_REVIEW** — every gate is PASS / PASS_ADVISORY / INFO, BUT the inline issues section contains items the gate matrix did not catch (e.g. cultural reference handling that I1 logged as recorded but the reviewer flagged for re-examination), or S1 is SKIPPED with a documented reason and the reviewer should decide whether to re-run on an isolation-capable runtime. NEEDS_REVIEW is the "no objective failure but a human eye is warranted" state — it is rare; PASS and FAIL cover most runs.

The one-line rationale per gate is the gate-verdict summary; full diff
detail lives in §3.

### 3. Per-gate verdict block

One subsection per gate (M1, M2, S1, S2, I1) in that fixed order. Each
subsection has: verdict header, diff (gate-specific structured detail),
and concrete examples from the target.

#### Template

```markdown
## Per-gate verdicts

### M1 — Placeholder integrity

**Verdict**: FAIL

**Diff**:

| Chunk | Source count | Target count | Missing in target | Extra in target |
|---|---|---|---|---|
| 0 | 3 | 3 | — | — |
| 1 | 2 | 2 | — | — |
| 2 | 5 | 4 | `P:04` | — |
| 3 | 1 | 1 | — | — |
| 4 | 0 | 0 | — | — |

**Concrete example (chunk 2)**:

- **Source**: `Hello ⟦P:04⟧, your order ⟦P:01⟧ ⟦P:02⟧ ⟦P:03⟧ ⟦P:05⟧.`
  (token `P:04` = `{user_name}`)
- **Target**: `こんにちは、ご注文 ⟦P:01⟧ ⟦P:02⟧ ⟦P:03⟧ ⟦P:05⟧。`
- **Issue**: target dropped the user-name placeholder. Runtime substitution
  will produce a greeting without the user's name.

### M2 — Project glossary compliance

**Verdict**: FAIL

**Diff**:

| Term | Source occurrence | Project glossary | Target used | Tier | Severity |
|---|---|---|---|---|---|
| cancel | "Cancel order" (chunk 1) | 取消 | キャンセル | L1 | fail |
| submit | "Submit form" (chunk 3) | 送信 | 提出 | L1 | fail |
| engagement | "drive engagement" (chunk 0) | エンゲージメント | 関与度 | L1 (notes: context-dependent) | advisory |

**Concrete example (chunk 1)**:

- **Source**: `Cancel order`
- **Target**: `キャンセル注文`
- **Issue**: project glossary `<repo>/docs/i18n/glossary-ja-JP.md` v0.3.2
  pins `cancel` → `取消`. Target used `キャンセル`, breaking project-wide
  consistency. Audit path = direct (no pivot).

### S1 — Back-translation diff

**Verdict**: FAIL (audit-mode HARD)

**Diff**:

| Chunk | Similarity | Threshold | Verdict |
|---|---|---|---|
| 0 | 0.92 | 0.85 | PASS |
| 1 | 0.88 | 0.85 | PASS |
| 2 | 0.86 | 0.85 | PASS |
| 3 | 0.91 | 0.85 | PASS |
| 4 | 0.78 | 0.85 | FAIL |

**Concrete example (chunk 4)**:

- **Original source**: `Tap to retry the upload.`
- **Existing target**: `アップロードに失敗しました。`
- **Back-translation**: `The upload has failed.`
- **Issue**: target dropped the call-to-action ("tap to retry") and
  reframed as a status message. Embedding similarity 0.78 reflects the
  semantic drift. In a forward run this would be WARN; in audit it is
  FAIL.

### S2 — Register preservation

**Verdict**: PASS

**Diff**:

- Expected register (from intake): formal
- Judged register (target): formal
- Rationale: target uses `です` / `ます` consistently; appropriate keigo
  on user-facing strings; matches intake-spec `register: formal`.

### I1 — Untranslatability flagging

**Verdict**: INFO

**Recorded handlings**:

- `御朱印` (chunk 0) → **borrow** with gloss: `御朱印 (goshuin — temple
  seal stamp)`. Acceptable; no action needed.

**Missing handlings**: none.
```

If a gate is SKIPPED (only S1 can SKIPPED, when the runtime has no
subagent isolation), record:

```markdown
### S1 — Back-translation diff

**Verdict**: SKIPPED

**Reason**: runtime provided no subagent / task-isolation capability;
back-translation cannot be run blind. Per `references/verification-gates.md`
§S1 "When SKIPPED": re-run on a runtime that supports isolation if S1
quality matters. In audit mode SKIPPED rolls up into overall verdict =
NEEDS_REVIEW.
```

### 4. Inline issues

One row per issue. Issues are ordered by source line number ascending.
The inline issues section is the **reviewer's triage queue** — each row
is one actionable item with enough context to fix without re-reading the
files.

#### Required fields per issue

- **Source line / col reference**: `source.po:42:8` style, or `chunk 2` if
  the format does not have line numbers (inline strings, JSON without
  source-map).
- **Target line / col reference**: same format, target side.
- **Issue category** (one of):
  - `placeholder` — M1 issue
  - `glossary` — M2 issue
  - `register` — S2 issue
  - `accuracy` — S1 issue (semantic drift, missing content, hallucinated
    content)
  - `cultural` — I1 issue (untranslatability handling missing or weak)
- **Severity** (one of):
  - `HARD-FAIL` — gate produced FAIL; output blocked in a forward run; in
    audit it must be addressed before sign-off.
  - `SHOULD-WARN` — gate would have been SHOULD/WARN in a forward run;
    audit upgrades S1/S2 to HARD-FAIL, but PASS_ADVISORY (M2 context-
    dependent) shows here as SHOULD-WARN.
  - `INFO` — I1 entries; informational only; sign-off may close without
    action.
- **Quoted source text** — the offending span in the source.
- **Quoted target text** — the corresponding span in the target.
- **Improvement suggestion** — concrete alternative phrasing or
  structural fix. Phrasing-level: a proposed target string. Structural:
  "split into two strings", "add `msgctxt`", "swap to mapped glossary
  form", etc. Suggestions are guidance for the reviewer, not edits to
  the file.

#### Template row

```markdown
## Inline issues

### Issue 1 — placeholder / HARD-FAIL

- **Source**: `source.po:42:8` — `Hello {user_name}, your order is ready.`
- **Target**: `target.po:42:8` — `こんにちは、ご注文の準備ができました。`
- **Improvement suggestion**: `こんにちは、{user_name}さん。ご注文の準備ができました。`
  (restore the `{user_name}` placeholder so runtime substitution produces
  a personalised greeting)

### Issue 2 — glossary / HARD-FAIL

- **Source**: `source.po:8:1` — `Cancel order`
- **Target**: `target.po:8:1` — `キャンセル注文`
- **Improvement suggestion**: `注文を取消す` (apply project glossary
  mapping `cancel → 取消` per `<repo>/docs/i18n/glossary-ja-JP.md` v0.3.2)

### Issue 3 — accuracy / HARD-FAIL

- **Source**: `source.po:97:1` — `Tap to retry the upload.`
- **Target**: `target.po:97:1` — `アップロードに失敗しました。`
- **Improvement suggestion**: `タップしてアップロードを再試行。` (restore
  the call-to-action; current target reframes as status message and
  loses the actionable user instruction)
```

### 5. Recommendations

A bulleted list of next actions ordered by impact. The list operationalises
the per-gate diffs and inline issues into a triage queue:

```markdown
## Recommendations

- **Fix 1 M1 placeholder mismatch** (chunk 2): restore `{user_name}` in
  target. Re-run audit after fix.
- **Fix 2 M2 glossary violations**: apply `cancel → 取消` and
  `submit → 送信` from `<repo>/docs/i18n/glossary-ja-JP.md` v0.3.2.
- **Re-translate chunk 4** (`Tap to retry the upload.`): current target
  drops the CTA. Either hand-edit or re-run `translation-i18n` on chunk
  4 alone with focus on action-verb fidelity.
- **Add glossary entry** for `goshuin` if domain becomes
  `tourism.religious` in future strings — current `borrow` decision is
  acceptable but a glossary entry would make the handling consistent
  across translators.
- **Consider re-translation of chunks 1 + 3 + 4** if more than 5 issues
  surface in the next audit pass — the cumulative drift suggests the
  initial translator was working without the project glossary.
```

### 6. Sign-off

A section the human reviewer fills in after triage:

```markdown
## Sign-off

- **Reviewer**: <name>
- **Date**: 2026-05-07
- **Decision**: APPROVE | NEEDS_FIXES | ESCALATE
- **Notes**:
  - Fixed M1 issue inline; verified by re-running audit (PASS).
  - Glossary violations on `cancel` / `submit` deferred to translator
    follow-up; tracking issue #1234.
  - Re-translation of chunk 4 done; new audit attached.
```

`APPROVE` = ship the target. `NEEDS_FIXES` = return to translator with the
recommendations. `ESCALATE` = the audit surfaced an issue the reviewer
cannot resolve alone (e.g. project glossary itself is wrong; brand voice
question outside the audit's scope).

## Worked example — 5-string PO file with 1 M1 + 2 M2 + 1 S1 issues

A complete diff report for a small PO file. Source `messages.po` (en-US),
target `messages.ja.po` (ja-JP). Five strings; some pass, some fail.

```markdown
# Translation audit — messages.po ↔ messages.ja.po

- **Source path**: `messages.po`
- **Target path**: `messages.ja.po`
- **Audit timestamp**: 2026-05-06T14:32:11Z
- **Source format**: PO (auto-detected)
- **Target format**: PO (auto-detected)
- **Source locale**: en-US
- **Target locale**: ja-JP
- **Intake snapshot**:
  - mode: faithful (auto-inferred from `domain: ui`)
  - register: formal (caller-supplied)
  - strategy: domestication (auto-inferred)
  - domain: ui (auto-inferred from .po + short strings)
  - intent: "consumer-app onboarding strings"
- **Glossary**:
  - L1: `docs/i18n/glossary-ja-JP.md` v0.3.2
  - L2: `glossary/glossary-en-US--ja-JP.md` (build 2026-05-06)
  - L3: web search ON
- **Web search**: ON
- **Audit-trail JSON**: `messages.ja.po.audit-trail.json`

## Summary

**Overall verdict**: FAIL

| Gate | Verdict | Rationale |
|---|---|---|
| M1 | FAIL | string 4 dropped `{user_name}` placeholder |
| M2 | FAIL | 2 L1 glossary terms ignored: `cancel` → `取消`; `submit` → `送信` |
| S1 | WARN | string 5 below 0.85 (sim 0.78); audit HARD → FAIL |
| S2 | PASS | register: formal expected, formal judged |
| I1 | INFO | no untranslatable phrases flagged |

## Per-gate verdicts

### M1 — Placeholder integrity

**Verdict**: FAIL

| String | Source count | Target count | Missing | Extra |
|---|---|---|---|---|
| 1 | 0 | 0 | — | — |
| 2 | 0 | 0 | — | — |
| 3 | 0 | 0 | — | — |
| 4 | 1 | 0 | `P:01` (= `{user_name}`) | — |
| 5 | 0 | 0 | — | — |

**Concrete example (string 4)**:
- Source: `Welcome back, {user_name}!`
- Target: `おかえりなさい！`
- Issue: target dropped the `{user_name}` placeholder. Runtime greeting
  will lack the user's name.

### M2 — Project glossary compliance

**Verdict**: FAIL

| Term | Source occurrence | L1 mapping | Target used | Severity |
|---|---|---|---|---|
| cancel | "Cancel" (string 1) | 取消 | キャンセル | fail |
| submit | "Submit" (string 3) | 送信 | 提出 | fail |

### S1 — Back-translation diff

**Verdict**: FAIL (audit-mode HARD)

| String | Similarity | Threshold | Verdict |
|---|---|---|---|
| 1 | 0.94 | 0.85 | PASS |
| 2 | 0.91 | 0.85 | PASS |
| 3 | 0.89 | 0.85 | PASS |
| 4 | 0.86 | 0.85 | PASS |
| 5 | 0.78 | 0.85 | FAIL |

**Concrete example (string 5)**:
- Source: `Tap to retry the upload.`
- Target: `アップロードに失敗しました。`
- Back-translation: `The upload has failed.`
- Issue: target reframed CTA as status message; semantic drift below
  threshold.

### S2 — Register preservation

**Verdict**: PASS

- Expected: formal. Judged: formal. Rationale: consistent `です` / `ます`
  + appropriate keigo on user-facing strings.

### I1 — Untranslatability flagging

**Verdict**: INFO

- No phrases flagged by Layer 2 source analysis; no recorded handlings
  needed.

## Inline issues

### Issue 1 — glossary / HARD-FAIL
- Source: `messages.po:5:1` — `Cancel`
- Target: `messages.ja.po:5:1` — `キャンセル`
- Improvement suggestion: `取消` (apply L1 glossary mapping)

### Issue 2 — glossary / HARD-FAIL
- Source: `messages.po:13:1` — `Submit`
- Target: `messages.ja.po:13:1` — `提出`
- Improvement suggestion: `送信` (apply L1 glossary mapping)

### Issue 3 — placeholder / HARD-FAIL
- Source: `messages.po:18:1` — `Welcome back, {user_name}!`
- Target: `messages.ja.po:18:1` — `おかえりなさい！`
- Improvement suggestion: `{user_name}さん、おかえりなさい！` (restore
  `{user_name}` placeholder; preserve formal register with `さん`)

### Issue 4 — accuracy / HARD-FAIL
- Source: `messages.po:23:1` — `Tap to retry the upload.`
- Target: `messages.ja.po:23:1` — `アップロードに失敗しました。`
- Improvement suggestion: `タップしてアップロードを再試行してください。`
  (restore CTA; preserve formal register with `ください`)

## Recommendations

- Fix 2 M2 glossary violations (apply project glossary mappings).
- Restore `{user_name}` placeholder in string 4.
- Re-translate string 5 with focus on action-verb fidelity.
- Re-run audit after fixes; target overall verdict = PASS.

## Sign-off

- Reviewer: _________________
- Date: _________________
- Decision: [ ] APPROVE  [ ] NEEDS_FIXES  [ ] ESCALATE
- Notes:
```

The worked example shows: report stays compact for small files; per-gate
tables scale linearly with chunk count; inline issues = the reviewer's
TODO list; sign-off closes the loop.

## See also

- `../SKILL.md` §"Layer 5: Output" — invokes this protocol
- `../checklists/audit-completeness-checklist.md` — 5-item completeness
  check that runs before report emit; ensures the report has all required
  fields
- `../references/verification-gates.md` — gate verdict shapes that the
  per-gate verdict block in §3 surfaces verbatim
- `../references/audit-trail-spec.md` — the JSON companion the report
  references in its header
