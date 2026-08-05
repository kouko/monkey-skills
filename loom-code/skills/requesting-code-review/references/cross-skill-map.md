Source: `requesting-code-review/SKILL.md` §"Cross-skill contract" — serves `requesting-code-review`.

# Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream invocation** | `finishing-a-development-branch` | Calls this skill as Step 1 of the close-branch flow |
| **Downstream (docs arm)** | `requesting-docs-review` | Step 1 delegates docs-only branches to it whole; its contract governs the `.md` arm of mixed branches (verdict join: worse of the two arms) |
| **Downstream (after PASS)** | `finishing-a-development-branch` proceeds to verification-before-completion + commit + push | |
| **Downstream (after NEEDS_REVISION)** | User remediates → re-dispatch this skill, OR invoke `subagent-driven-development` to dispatch implementer fixes if scoped enough | |
| **Lateral (optional)** | `domain-teams:code-team` | For LARGE audit work (>500 LOC changed, security-sensitive surface, or production-incident-driven review). The skill itself is sized for branch-pre-merge; major audits should escalate. |
| **Lateral (rubrics SSOT)** | Rubrics / checklists loaded from `../subagent-driven-development/{rubrics,checklists}/` (path relative to the skill directory, as in SKILL.md; functional copies of `code-team`) | Same SSOT as SDD's per-task reviewer — no drift between per-task and whole-branch review |
