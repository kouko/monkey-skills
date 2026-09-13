---
name: a-one-shot-acceptance-proof-against-a-moving-baseline-outlives-its-change
description: A test written to prove one change's acceptance ("nothing in X changed during this move") by comparing the working tree against a moving ref such as origin/main is correct exactly once — after that change merges, the baseline becomes the new state and the assertion silently turns into "X may never change again", failing the first legitimate use of whatever X is; bind such a proof to a fixed commit, or delete it when the change merges
type: gotcha
sources:
  - resource: 2026-09-11, memory-timing arc — `test_store_fidelity.py` proved 293 migrated lessons were byte-identical across a relocation; once that change was the trunk, the first new lesson recorded afterwards failed it, and three of the four operations the skill ships would each have done the same
---

A relocation change had to prove it moved a skill without touching the
store. The proof compared `docs/loom/memory/` against `origin/main`,
path-for-path and byte-for-byte, and it was a good test: recomputed from
git rather than pinned to a snapshot, non-ASCII-safe, and hardened so a
missing baseline failed loudly in CI instead of skipping.

It shipped inside the plugin's permanent test suite. Once the change
merged, `origin/main` *was* the migrated store, and the assertion no
longer said "this move changed nothing". It said **"this store may never
change"** — and the skill it ships beside has four operations, three of
which change the store. Record adds a file, Reconcile rewrites one, Retire
deletes one. Each turns the proof red, permanently, for doing exactly what
the contract says to do.

**Why it is invisible at the time.** At the moment it is written, the
assertion is true, meaningful, and cheap. Reviewers read it against the
diff and it is correct there. Its defect is not in what it asserts but in
how long it asserts it, and lifetime is not a property any review
dimension looks at. It stays green through its own change and through
every change that does not touch the subject — so the failure arrives
later, in an unrelated branch, looking like that branch's fault.

**Narrowing usually does not save it.** "Allow additions, freeze existing
files" sounds like the fix, and it was rejected here: Reconcile rewrites an
existing entry by design, so no version of the assertion survives contact
with the contract it sits next to. When the subject is something the
system is *supposed* to modify, there is no standing invariant to salvage.

**How to apply.**
1. When a test exists to prove one change's acceptance, decide its lifetime
   as you write it. Two dispositions are correct: **bind it to a fixed
   commit** (the merge-base or the sha being migrated from), or **delete it
   at merge** and let the attestation carry the proof.
2. A moving ref in an acceptance proof is the tell. `origin/main`, `HEAD~`,
   "the trunk" — all of them make the assertion's meaning change under it.
3. Before writing a test over a directory, ask what the shipped contract
   says may happen to that directory. A proof that contradicts the
   operations shipping beside it is wrong however green it is today.
4. Deleting it later is not weakening a test. Say in the commit which
   acceptance line it discharged, that the change is merged, and why no
   narrowed form survives — that is what separates it from silencing.

Related: [[an-acceptance-line-is-measured-against-the-trunk-before-it-is-written]]
— the same arc, the other end: there the baseline was never measured, here
it was measured correctly and then moved. Also
[[a-graduated-probe-that-pins-a-fact-of-the-moment-goes-red-at-the-next-change]]
— the probe-shaped version of the same lifetime defect.
