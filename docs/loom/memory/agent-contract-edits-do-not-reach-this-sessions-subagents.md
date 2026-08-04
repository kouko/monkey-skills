---
name: agent-contract-edits-do-not-reach-this-sessions-subagents
description: An ordinary subagent dispatch loads its role contract from the installed plugin, not from the repo working tree, so an agent-contract edit on a branch does not reach the reviewers that branch dispatches — and the subagent cannot reliably report which version it loaded, because it may have read the repo copy as a review artifact and mistake that for its own system prompt
type: gotcha
origin: PR #645 (2026-08-04) — the delta-scope rule was edited into loom-code/agents/docs-reviewer.md and every reviewer dispatched that session still ran the cached 0.47.0 contract
---

Editing `loom-code/agents/<role>.md` on a branch changes the file the
orchestrator and reviewers *read as an artifact*. On an **ordinary
dispatch** it does not change the system prompt of any subagent dispatched
with that `subagent_type` — that comes from the installed plugin cache
(`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`), which only
moves when the plugin is published and updated.

**Scope, because a sibling entry covers the exception**:
[[headless-branch-plugin-testing-recipe]] loads an unpushed branch's plugin
with `claude … --plugin-dir <repo>/<plugin>`, which is a deliberate override
of the path this entry describes. Whether that override reaches subagent
role contracts specifically is untested — the point here is only that an
ordinary in-session dispatch does not, so "I dispatched a reviewer and it
behaved correctly" is not evidence about a contract edit that has not
shipped.

The gap is invisible unless you look at the cache. On PR #645 the working
tree carried a new `### Round scope` input section and an `out_of_scope:`
output block; `grep -c "Round scope"` over every cached version, including
the installed one, returned 0. Reviewers appeared to honour the new rule
only because the dispatch prompt restated it inline.

**Two arms in the same round reported opposite things about their own
contract.** One wrote that it had "run this dispatch off the reworded agent
contract" and that its `### Round scope` section "was sufficient to scope the
round without consulting the skill" — it had read the repo file, which was in
its review scope, and mistook that for its own system prompt. The other
reported that "the agent definition this dispatch ran under carried the
PRE-delta text". The cache showed the second was right. Both accounts were
quoted as evidence before the cache was checked.

**Why:** an agent-contract change is exactly the kind of change whose whole
point is behavioural, so the temptation to claim behavioural verification is
strongest precisely where the session cannot supply it. Accepting a
reviewer's account of its own contract version converts that into a false
positive — the reviewer is not lying, it has no reliable access to the
question. This is the general rule in
[[verify-agent-mechanisms-on-disk-not-self-report]] meeting a specific
carrier, and the same cache-versus-repo mechanism
[[deploy-surface-ab-legs-run-post-merge]] records for headless A/B probes,
generalised to every in-session dispatch.

**How to apply:** when a branch edits an agent contract, state plainly that
the change is unverified behaviourally and say why — do not cite a
reviewer's self-description as evidence it landed. To check what is actually
live, grep the installed cache path, not the repo. Ordinary review rounds
cannot supply behavioural verification of such a change, so do not schedule
it as one. Two instruments remain before publication: a deliberate
`--plugin-dir` probe, whose reach into role contracts is untested and so
worth establishing before relying on it
([[headless-branch-plugin-testing-recipe]]), and static checks that need no
probe at all — a diff read by a reviewer, or a check pairing the skill
against the agent contract
(`docs/loom/backlog/2026-08-04-a-rule-can-ship-into-a-skill-and-never-reach-its-agent-contract.md`).
