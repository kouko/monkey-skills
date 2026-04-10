# README Completeness Checklist Gate

## Evaluation Instructions

You are a strict README auditor. Check each item below against the README.md
under evaluation. This is a MUST gate — it blocks on any fatal failure.

Checklist items are aligned to the Standard README specification by Richard
Littauer (`standards/readme-standard.md` referenced via `protocols/write-readme.md`).

You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with
specific evidence.

## Checklist

- [ ] **CHK-README-001 (Title)** [FATAL]: The README starts with a single H1
  title matching the repo/package name. If an alternate name is used, it is
  italicized. Missing title or title that does not match the repo is a fatal
  failure.

- [ ] **CHK-README-002 (Short Description)** [FIXABLE]: A short description
  follows the title, under 120 characters, summarizing what the project does.
  Longer descriptions belong in a Background section.

- [ ] **CHK-README-003 (Install Section)** [FIXABLE]: An "Install" section
  exists with at least one code block showing how to install the project.
  For documentation-only repos, this may be omitted with an explicit note.

- [ ] **CHK-README-004 (Usage Section)** [FIXABLE]: A "Usage" section exists
  with at least one code block demonstrating the project in action. The
  example should be minimal and verifiable.

- [ ] **CHK-README-005 (Contributing Section)** [FIXABLE]: A "Contributing"
  section exists describing the PR policy, questions policy, or linking to
  CONTRIBUTING.md.

- [ ] **CHK-README-006 (License Last Section)** [FATAL]: A "License" section
  exists and is the **final section** of the README. It includes an SPDX
  identifier (e.g., `MIT`, `Apache-2.0`) and the copyright holder. License
  not being last is a fatal violation of the Standard README spec.

- [ ] **CHK-README-007 (Table of Contents)** [FIXABLE]: If the README exceeds
  100 lines, a Table of Contents section exists and links to every level-2
  heading. If under 100 lines, this item passes automatically.

- [ ] **CHK-README-008 (No Broken Links)** [FIXABLE]: All internal links resolve
  to existing files or anchors. All external links are well-formed URLs.
  (Note: actual reachability of external URLs is out of scope for this gate.)

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` → final verdict is `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` items (no FATALs) → final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` → final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-README-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific README content or line reference",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```

## Source

- [Standard README spec (RichardLitt)](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) — required sections and order
