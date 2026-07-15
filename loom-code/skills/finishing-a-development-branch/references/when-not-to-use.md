# When NOT to use — exemptions

Load when questioning whether close-out applies to the current branch. Each row: the exempt category → what genuinely qualifies → the near-miss that does NOT (the rationalization to refuse).

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Mid-task work** | The SDD task plan is not yet complete; tasks still pending | "I'm tired of this branch" — that's bailing, not finishing. SDD plan completes first. |
| **Trivial direct-to-main commits** | Solo project, no review process, tiny doc fix | Feature branch with multiple commits — even solo, the discipline catches regressions |
| **Branch you're abandoning** | The work isn't merging; you're discarding | Skill doesn't apply — just delete the branch. But re-examine whether the work was real: if so, the branch deserves close-out before deletion (decisions worth recording via git-memory) |
| **Explicit user override** | User says "skip review, just push" AND there's a real reason (cherry-pick to release branch / known-trivial cleanup) | "I trust myself" — that's the rationalization this skill exists for |

**git-memory is never waived by an exemption.** These exemptions waive the close-out *orchestration* (review / verification / PR), not `dev-workflow:git-memory` (P3-D). git-memory is a mandatory gate before *every* commit — even a trivial direct-to-main commit goes through it (it will usually return "no trailers, routine," and the invocation itself is the discipline). Skipping the close-out flow does NOT mean skipping git-memory.
