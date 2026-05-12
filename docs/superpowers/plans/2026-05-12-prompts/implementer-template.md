# Implementer subagent prompt template

Use this for each of the 8 Phase A implementer subagents. Fill in the
`{{}}` placeholders before dispatch.

---

You are a Phase A implementer subagent for the systems-thinking-toolkit
v0.1.0 build.

## Your task

`{{TASK_TYPE}}` — Either **MERGE-AND-POLISH** (combine two source SKILL.md
into one, then apply 9 improvements) or **POLISH-ONLY** (apply 9
improvements to a single standalone source SKILL.md).

## Your target

- Skill slug: `{{TARGET_SLUG}}`
- Source SKILL.md path(s):
  - For MERGE: two sources
    - `{{CACHE}}/{{SOURCE_A_SLUG}}/SKILL.md`
    - `{{CACHE}}/{{SOURCE_B_SLUG}}/SKILL.md`
  - For POLISH: one source
    - `{{CACHE}}/{{SOURCE_SLUG}}/SKILL.md`
- Destination dir: `{{PLUGIN_ROOT}}/skills/{{TARGET_SLUG}}/`

## Required reading (in order, fully)

1. **Spec**: `{{REPO}}/docs/superpowers/specs/2026-05-12-systems-thinking-toolkit-v0.1.0-design.md` §3.5, §5, §7
2. **Pilot reference**: `{{REPO}}/systems-thinking-toolkit/skills/cld-craft/SKILL.md` (the pattern reference for both merge mechanic and 9 improvements)
3. **Pilot commit**: `git show {{PILOT_COMMIT_HASH}}` (the actual diff)
4. **INDEX-original**: `{{PLUGIN_ROOT}}/references/INDEX-original.md` (14-node Stage-3 relations — use the re-mapping rule in spec §3.5 to derive 9-node `related_skills` for your target)
5. **Source SKILL.md file(s)** for your target

## Required output

ONE atomic commit on the current branch containing:

- `{{PLUGIN_ROOT}}/skills/{{TARGET_SLUG}}/SKILL.md`
- `{{PLUGIN_ROOT}}/skills/{{TARGET_SLUG}}/references/cases.md` (conditional, body > 180 lines after polish per spec §5 Tier 2 #4)

Commit message format:

```
feat(systems-thinking-toolkit): {{TARGET_SLUG}} {{merge | polish}} (5-item improvements applied)

<body>
```

## Hard constraints

1. `related_skills` entries MUST be a subset of INDEX-original 17 relations re-mapped per spec §3.5; never invent relations
2. Body MUST be ≤ 4500 words (≤ ~6000 tokens); trigger `references/cases.md` extraction if exceeded
3. Frontmatter MUST parse as valid YAML
4. Hook `bash .claude/hooks/validate-skill-folder-structure.sh` MUST exit 0 against your output
5. Shorthand `sk0[0-9]` and `sk1[0-4]` MUST be glossed at first occurrence per section
6. `{{TARGET_SLUG}}`-specific Tier-3 override (if any): `{{TIER_3_OVERRIDE_INSTRUCTION_OR_NONE}}`
7. Audit metadata MUST preserve ALL source-unit codes from source SKILL.md (or both, if MERGE) — no provenance loss

## What you must NOT do

- Do NOT modify any file outside `{{PLUGIN_ROOT}}/skills/{{TARGET_SLUG}}/`
- Do NOT add new files beyond SKILL.md + references/cases.md
- Do NOT invent new `related_skills` not in the 17-relation INDEX-original
- Do NOT modify or paraphrase source-unit codes (f01, p28, ce27, etc.)
- Do NOT delete or reword existing Boundary "Author's blind spots" sections — these are V1.5 transparency artifacts

## Done criteria

Your commit lands cleanly; `git log -1` shows it; hook exits 0; YAML parses; word count is below 4500.

Report DONE with the commit hash.
