# Plan: dogfood-skill-testing v0.1

Source brief: docs/loom/specs/2026-06-03-dogfood-skill-testing.md
Total tasks: 9 (uncapped; width is fine)
Critical-path depth: 4 (≤5) — T1 → T2 → T5 → T6
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (14/14, 2026-06-03) — amended post-PASS: T8
Independent false→true per reviewer advisory note (additive, schema-safe, DAG
unchanged; re-review skipped per writing-plans amend rule).

Skill dir: `dev-workflow/skills/dogfood-skill-testing/`
Pure-prompt skill (no Python runtime). TDD RED/GREEN lands on a structural test
suite (`test_skill_structure.py`) whose per-file test functions go GREEN as each
content task lands. Package-level verification: `pytest dev-workflow/`.

Dependency levels:
- L1 (parallel): T1 (test suite, RED) · T7 (plugin.json bump) · T9 (READMEs)
- L2 (parallel): T2 (defect-taxonomy) · T3 (report-template) · T4 (trigger-eval) · T8 (CHANGELOG, dep T7)
- L3: T5 (SKILL.md frontmatter+refs, dep T2,T3)
- L4: T6 (SKILL.md workflow body, dep T5)

---

## Task 1 — Author structural test suite (RED)
- Description: Write `test_skill_structure.py` with 7 test functions asserting the
  skill's structure; all RED now (no skill files exist). Functions: `test_frontmatter`,
  `test_flat_folder`, `test_defect_taxonomy_content`, `test_report_template_content`,
  `test_trigger_eval_schema`, `test_skill_md_refs`, `test_skill_md_workflow`. Stdlib
  only (json, pathlib, re; parse frontmatter by hand-splitting `---` fences — no yaml dep).
- Module: dev-workflow/skills/dogfood-skill-testing (test file)
- Files touched: dev-workflow/skills/dogfood-skill-testing/test_skill_structure.py
- Context paths:
  - dev-workflow/.claude-plugin/test_plugin_manifest.py  (stdlib-only test style to mirror)
  - dev-workflow/skills/distill-sessions/trigger-eval.json  (corpus schema reference)
- Acceptance:
  - RED: `pytest dev-workflow/skills/dogfood-skill-testing/test_skill_structure.py`
    collects 7 tests and all 7 FAIL (assertion failures / missing-file, not collection error).
  - GREEN: the test module imports and collects cleanly; the 7 functions exist and
    fail meaningfully (they reference paths that don't exist yet).
- External surfaces: none (stdlib pytest only).
- Dependencies: none
- Independent: true
- Brief item covered: "結構測試 test_skill_structure.py（frontmatter/flat-folder/bundled-files-referenced/trigger-eval schema）"

## Task 2 — references/defect-taxonomy.md
- Description: Create the defect taxonomy: 4 severities (Critical/High/Medium/Low with
  definitions) × the 9 categories (Trigger-miss / Over-trigger / Cold-start /
  Workflow-drift / Gate-bypass / Jargon-leak / Convention-violation /
  Progressive-disclosure / Output-quality), each annotated with measured community
  frequency where known (Trigger-miss 68% / desc-too-short 41% / missing-version 62%).
  Port+adapt of agent-browser `issue-taxonomy.md`.
- Module: dev-workflow/skills/dogfood-skill-testing/references
- Files touched: dev-workflow/skills/dogfood-skill-testing/references/defect-taxonomy.md
- Context paths:
  - docs/loom/specs/2026-06-03-dogfood-skill-testing.md  (§Dogfood method, taxonomy)
- Acceptance:
  - RED: `test_defect_taxonomy_content` fails (file missing).
  - GREEN: file exists; contains all 4 severity labels, ≥7 category names, ≥1 frequency %.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "references/defect-taxonomy.md（severity×category + 實測頻率）"

## Task 3 — templates/dogfood-report-template.md
- Description: Create the report template: metadata header (skill path/version/date/
  passes/model-pinned) → severity summary table → per-finding block fields (FINDING-###,
  severity, category, pass[blind|informed], probe prompt, expected, actual, transcript
  evidence, root cause, **why static review missed it**, location, suggested fix
  direction, repro) → **Raw outputs appendix** (executor artifact + probe transcript +
  activation query→result). Port+adapt of agent-browser `dogfood-report-template.md`.
- Module: dev-workflow/skills/dogfood-skill-testing/templates
- Files touched: dev-workflow/skills/dogfood-skill-testing/templates/dogfood-report-template.md
- Context paths:
  - docs/loom/specs/2026-06-03-dogfood-skill-testing.md  (report contract)
- Acceptance:
  - RED: `test_report_template_content` fails (file missing).
  - GREEN: file exists; contains metadata fields, per-finding fields incl. "root cause",
    "why static", "location", "suggested fix", and a "Raw outputs" appendix heading.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "templates/dogfood-report-template.md（fix-actionable 欄位 + raw outputs 附錄）"

## Task 4 — trigger-eval.json (self-dogfood corpus)
- Description: Create the skill's own trigger-eval corpus: JSON array of
  `{query, should_trigger}` — ≥6 should_trigger:true (zh-TW/ja/en phrasings of "dogfood
  this skill in development / test my skill's triggers / 測試開發中的 skill") + ≥4
  should_trigger:false near-misses (e.g. "score this SKILL.md" → skill-judge;
  "mine my session logs" → distill-sessions; "shrink this skill's tokens" → skill-refactor;
  "create a new skill" → skill-creator-advance).
- Module: dev-workflow/skills/dogfood-skill-testing (corpus file)
- Files touched: dev-workflow/skills/dogfood-skill-testing/trigger-eval.json
- Context paths:
  - dev-workflow/skills/distill-sessions/trigger-eval.json  (schema + style)
- Acceptance:
  - RED: `test_trigger_eval_schema` fails (file missing).
  - GREEN: valid JSON; non-empty array; each item has query(str)+should_trigger(bool);
    ≥1 true and ≥1 false present.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "trigger-eval.json（自我觸發測試語料）"

## Task 5 — SKILL.md frontmatter + overview + bundled-file references
- Description: Create SKILL.md frontmatter (name: dogfood-skill-testing; rich
  description with zh-TW/ja/en trigger phrases + "Do NOT use for" boundaries vs
  skill-judge/skill-creator-advance/distill-sessions/skill-refactor; version: 0.1.0) +
  Overview opening with the "a bad SKILL.md doesn't throw an error — it just never gets
  invoked" (silently-broken) framing + the two-dimension intent (trigger + output-quality)
  + reference both bundled files by relative path (`references/defect-taxonomy.md`,
  `templates/dogfood-report-template.md`).
- Module: dev-workflow/skills/dogfood-skill-testing (SKILL.md — section set A)
- Files touched: dev-workflow/skills/dogfood-skill-testing/SKILL.md
- Context paths:
  - docs/loom/specs/2026-06-03-dogfood-skill-testing.md
  - dev-workflow/skills/skill-judge/SKILL.md  (frontmatter "Do NOT use" boundary style)
- Acceptance:
  - RED: `test_frontmatter`, `test_flat_folder`, `test_skill_md_refs` fail (SKILL.md missing).
  - GREEN: frontmatter valid (name/description/version); flat-folder clean; SKILL.md body
    references both bundled paths and they resolve.
- Dependencies: Tasks 2, 3 complete first (references must resolve)
- Independent: false
- Brief item covered: "SKILL.md（workflow + 方法論 inline）" + "silently broken 作為存在理由"

## Task 6 — SKILL.md workflow body (3 probes + method inline + report contract)
- Description: Add the operational body to SKILL.md: the 3 probes —
  (A) **activation-harness** (primary: temp `.claude/skills/` + distractors + `claude -p
  --max-turns 1 --allowedTools Skill --output-format stream-json`, parse `Skill()` events,
  ~20 should-fire + ≥5 should-NOT-fire, ≥2 runs; **fallback**: description-injection menu
  marked `fidelity:approximate`); (B) **executor + blind auditor** (executor runs end-to-end
  on real input "user has NOT installed", forced cold-start path; blind auditor judges
  output, rubric = skill's self-declared contract + domain standard; judge guardrails:
  rubric-not-artifact, ≥2 runs + pin model, judge trajectory, coarse buckets);
  (C) **blind cold-reader** (fixed question set). Plus method rules INLINE (firewall /
  floor-not-ceiling / real-data / axis-sweep predict-then-execute / force-fallback-path /
  environment guards / human-is-final-calibrator) + output contract (fix-actionable findings,
  raw outputs surfaced, report → `docs/skill-dogfood/`, hand to main agent — no feedback form).
- Module: dev-workflow/skills/dogfood-skill-testing (SKILL.md — section set B)
- Files touched: dev-workflow/skills/dogfood-skill-testing/SKILL.md
- Context paths:
  - docs/loom/specs/2026-06-03-dogfood-skill-testing.md  (§Dogfood method, passes)
- Acceptance:
  - RED: `test_skill_md_workflow` fails (workflow markers absent).
  - GREEN: SKILL.md contains the 3-probe markers ("activation", "cold-reader",
    "executor"/"auditor"), "claude -p", "docs/skill-dogfood", and a fallback/"fidelity" mention.
- Dependencies: Task 5 completes first (same file, sequential edit)
- Independent: false
- Brief item covered: "三探針 + 方法論 inline + 報告→docs/skill-dogfood/"

## Task 7 — plugin.json version bump + keyword
- Description: Bump `dev-workflow/.claude-plugin/plugin.json` version 2.14.1 → 2.15.0
  (minor: new skill) and add "dogfood-skill-testing" to the keywords array.
- Module: dev-workflow/.claude-plugin (manifest)
- Files touched: dev-workflow/.claude-plugin/plugin.json
- Context paths:
  - dev-workflow/.claude-plugin/test_plugin_manifest.py  (asserts minor bump, patch==0)
- Acceptance:
  - RED: `pytest dev-workflow/.claude-plugin/test_plugin_manifest.py` fails on patch==0
    (current 2.14.1 has patch 1).
  - GREEN: version is 2.15.0; manifest test passes; "dogfood-skill-testing" in keywords.
- External surfaces: plugin.json manifest schema (Claude Code plugin contract).
- Dependencies: none
- Independent: true
- Brief item covered: "plugin.json bump 2.14.1→2.15.0 + keyword"

## Task 8 — CHANGELOG.md entry
- Description: Add a `## [2.15.0] — 2026-06-03` entry to `dev-workflow/CHANGELOG.md`
  (Keep-a-Changelog format) under "Added": new `dogfood-skill-testing` skill — behavioral
  black-box dogfood for skills-in-development (activation harness + executor/blind-auditor +
  cold-reader; fix-actionable report).
- Module: dev-workflow (CHANGELOG)
- Files touched: dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/CHANGELOG.md  (existing format/head)
- Acceptance:
  - RED: `grep -q '## \[2.15.0\]' dev-workflow/CHANGELOG.md` fails.
  - GREEN: top entry is 2.15.0 dated 2026-06-03, names dogfood-skill-testing.
- Dependencies: Task 7 completes first (version SSOT = plugin.json)
- Independent: true
- Brief item covered: "dev-workflow/CHANGELOG.md 條目"

## Task 9 — README skill-list entries (3 languages)
- Description: Add a one-row entry for `dogfood-skill-testing` to the skills
  list/table in `dev-workflow/README.md`, `README.ja.md`, `README.zh-TW.md` (mirror the
  existing skill-row format in each). If a README has no skill enumeration, no-op that file
  and note it.
- Module: dev-workflow (READMEs)
- Files touched: dev-workflow/README.md, dev-workflow/README.ja.md, dev-workflow/README.zh-TW.md
- Context paths:
  - dev-workflow/README.md  (existing skill-list format)
- Acceptance:
  - RED: `grep -rl dogfood-skill-testing dev-workflow/README*.md` returns nothing.
  - GREEN: each README that enumerates skills lists dogfood-skill-testing once.
- Dependencies: none
- Independent: true
- Brief item covered: discoverability of the shipped skill (Decision: lands in dev-workflow)

## Notes
- T1/T7/T9 are L1 parallel (disjoint files). T2/T3/T4 are L2 parallel (disjoint files).
- T5/T6 are the only deep chain (same SKILL.md, sequential) → depth driver.
- If T6 implementer returns BLOCKED (SKILL.md body too big for one unit), apply Beck
  Child Test fallback: split into T6a (3-probe workflow) + T6b (method-inline + report
  contract), sequential.
