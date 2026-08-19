---
name: redaction-binds-every-downstream-artifact-not-only-the-scrubbed-file
description: Scrubbing a document of private material does not scrub what other documents quote from it. Identifiers judged individually harmless — node ids, branch names, ticket slugs — reconstruct the subject when read together, and a downstream brief that quotes one line verbatim reintroduces the whole. The scrubbed file's own 脫敏聲明 then asserts something false. Sweep every artifact that cites the source, including commit bodies, and do it before the first push, because a public repo makes it unrecoverable.
type: gotcha
origin: think-orbit 0.1.4 transparency arc (2026-08-19) — the orchestrator scrubbed the checkpoint doc, explicitly judged ~10 node ids abstract enough to keep, and the whole-branch reviewer showed they reconstructed the subject matter; caught pre-push, nothing left the machine
---

A real-material checkpoint was written from a project belonging to the user's
employer, in a public repo. The document was scrubbed of subject matter, product and
company names, and carried an explicit 脫敏聲明 saying so.

Ten node and branch identifiers survived the scrub — kept deliberately, because each
one in isolation reads as abstract engineering vocabulary and they were load-bearing
evidence for which nodes passed a measurement. Read together they named the domain,
the actors, the decision being made and the three alternatives that were weighed. A
downstream brief also quoted one node's body verbatim as an illustration of good
prose.

So three artifacts and a commit message each asserted the subject matter was absent,
and that assertion was false — including in the very document whose 脫敏聲明 made it.

**What made the misjudgment easy:** the identifiers were evaluated one at a time,
against the question "does this word reveal anything?" The right question is
"does the SET reconstruct the thing?", and it has a different answer. Reconstruction
is what an adversary does, and it is cheap when the identifiers are descriptive —
which is exactly what good naming makes them.

**What made it recoverable:** the branch had never been pushed, so no history rewrite
was needed. Had it been pushed, the identifiers survive in `git log` and `git show`
even after a later commit renames them, and on a public remote that is permanent.

**How to apply:**
1. Redaction is a property of the ARC, not of one file. When you scrub a source,
   immediately grep every artifact that cites it — briefs, plans, commit bodies,
   CHANGELOG, PR body — for what you removed.
2. Judge identifiers as a set, not individually. Ask a fresh reader to reconstruct
   the subject from the list alone; if they can, so can anyone.
3. A verbatim quote defeats a scrub completely. Illustrating a shape needs a
   synthetic example, and a synthetic one usually teaches better anyway because it
   can be built to show exactly the property under discussion.
4. Do the sweep before the first push, and say plainly whether the branch has ever
   been pushed — that fact decides whether the mistake is cheap or permanent.
5. When you notice yourself reasoning "these are probably abstract enough", that is
   the moment to ask rather than to proceed. The cost of asking is one message; the
   cost of being wrong is unrecoverable on a public remote.
