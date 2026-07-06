<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer), **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

**You have loom-code.** If the user is starting any coding work — feature / bug fix / refactor / review / migration — you **must** invoke the `using-loom-code` skill (via the Skill tool) and route through it before writing implementation code.

Five load-bearing rules (they bind even before the router loads):

1. **Brainstorm before implementing.** Explore intent + alternatives first — call `brainstorming` → structured brief.
2. **TDD is the iron law.** No production code without a failing test first — call `tdd-iron-law`. *"Write the test you wish you had. Make it fail. Make it pass. Make it clean."* (Beck 2002). Floor, not aspiration.
3. **Split + dispatch (SDD).** Task >1 hour or >1 module → `subagent-driven-development`; atomic ≤5-min units; three subagents per task (implementer / spec-reviewer / code-quality-reviewer).
4. **Never push without review.** `git push` / `gh pr create` / `gh pr merge` without prior `requesting-code-review` PASS (or `finishing-a-development-branch` flow) = violation. Push commands trigger review, not bypass.
5. **Research before asking.** Non-trivial design / strategy / tech-stack question to the user MUST cite WebSearch findings (2-4 industry approaches w/ sources). *"X or Y?"* without industry context = violation.

**Skipping any of these = violation.** "I'll just quickly…" / "just push" / "just ask" / 「ちょっと試すだけ」 / 「先 push 再說」 are rationalizations — refuse them.

This card is the pull-pointer, not the router: the full routing doctrine (stage decision order, red-flag responses, continuous mode, host tool mappings, references) loads when `using-loom-code` is invoked. Do not guess member skill names from this card — invoke the router.
