---
name: parallel-implementers-shared-tree-need-index-race-guard
description: Parallel implementer waves sharing ONE working tree race on the git index — `git add` + `git commit` interleave across agents, sweeping sibling files into the wrong commit; every dispatch packet needs the three-line guard (re-check staged set immediately before commit / unstage strays / pathspec-scoped commit), and the stash ban needs "including for isolation testing" spelled out
type: practice
origin: feat-copywriting-convergence-modernization (2026-07-30) — wave 2 race swallowed a sibling's staged files (soft-reset recovery); wave 3 with the guard: 4+ races all caught pre-commit; separately a subagent used `git stash` for "isolation testing" despite a plain stash ban and popped a foreign stash into a UU conflict (3rd occurrence of the stash-pop trap in this repo). RECURRENCE feat/progress-display-hardening (2026-08-08) — the orchestrator's fix-wave packets said only "stage by explicit path", omitting the three-line guard verbatim; the race fired again (pathless `git commit` swept the sibling's staged files; both agents self-repaired via soft-reset). The failure mode is RECALL, not knowledge: the entry existed and was not pulled into the packet — parallel-wave dispatch packets must paste the guard, not paraphrase it. THIRD RECURRENCE feat/requirement-identity-hybrid (2026-08-18) — the wave-1 packet again paraphrased ("add only the files your task touches"), three of four implementers hit the race and self-repaired via soft-reset, and an unrelated path (a stashed-branch test file) went UU mid-wave and blocked every commit repo-wide until the orchestrator restored it from HEAD; the guard was added to later packets only after the first reports. The lesson is unchanged and now three-for-three: paste, don't paraphrase — and put it in the packet BEFORE the first wave, not after the first collision
---

When several implementer subagents work the same checkout concurrently (no
worktree isolation), the git index is shared mutable state: agent A's `git
add` lands between agent B's `add` and `commit`, and B's commit silently
carries A's files. The plain instruction "stage only your own files" does not
survive this — B *did* stage only its own files; the index changed under it.

**Why:** the race window is add→commit, so the check must sit inside that
window, and the commit itself must be scoped so a missed stray still can't
enter. Worktree isolation avoids the class entirely but costs setup per agent;
for doc/test-sized tasks the guard is cheaper.

**How to apply:** every parallel-wave dispatch packet carries verbatim:
(1) `git diff --cached --name-only` IMMEDIATELY before commit; (2) unstage any
file not yours; (3) commit with explicit pathspec (`git commit -m ... --
<your files>`), which also survives an unrelated UU conflict blocking
whole-index commits. Ban clause must read "git stash is FORBIDDEN for any
purpose including isolation testing — use `git show <rev>:<path>` instead":
the bare ban was violated exactly by an agent that classified its stash use as
testing, not workflow, and `stash pop` then grabbed a foreign stash — recovery:
`git show HEAD:<path> >` restore + single-path `git add` clears the orphan
UU without touching the stash stack.
Related: [[parallel-wave-commit-discipline]] (the orchestrator-serial layer of
the same defense — that entry governs who commits when; this one governs what
each agent must do inside its own add→commit window),
[[untracked-replacement-while-deletion-staged]].
