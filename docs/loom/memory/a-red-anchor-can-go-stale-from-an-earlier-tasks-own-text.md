---
name: a-red-anchor-can-go-stale-from-an-earlier-tasks-own-text
description: A later task's RED grep anchor can be made prematurely green by an EARLIER task's own shipped text (a placeholder, an example, a docstring) that happens to contain the anchor string — the plan's acceptance greps are themselves a seam with sibling tasks' prose; pick anchors that only the later task's own edit can introduce, and have the per-task reviewer check sibling-task REDs against the artifact just shipped
type: gotcha
origin: seam-contracts arc (2026-08-25) — T1's Seam grammar placeholder `<name of the executed cross-seam probe ...>` contained the substring "cross-seam probe", which was T2's RED anchor; T1's spec-reviewer caught the stale RED before T2 dispatched, and the plan was amended to a `seam obligates` anchor that only T2's obligation paragraph introduces
---

Task 2's RED was `grep -q 'cross-seam probe'` exits 1. Task 1 — implementing
exactly its own spec — shipped grammar placeholder text containing that
substring, so T2's RED was green before T2 ever ran. Nobody wrote a wrong
line; the collision lived between two tasks' correct outputs.

**Why:** grep-anchor REDs on prose files assert against the whole file, and
earlier tasks in the same plan legally write to the same file. The anchor is
an undeclared seam: its payload is "this string does not yet exist", and any
sibling task can break that silently.

**How to apply:** (1) choose RED anchors from wording only the task's own
edit will introduce (a distinctive phrase of the new paragraph, not a term
the domain vocabulary already uses); (2) when a task ships text near a
sibling task's anchor, the per-task reviewer checks the sibling REDs still
fail against the just-shipped artifact — T1's spec-reviewer doing exactly
that is what caught this; (3) an anchor gone stale is a plan amendment
(re-anchor + re-review), not a reason to skip the RED.
