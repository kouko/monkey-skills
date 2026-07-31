---
name: substring-assertions-must-pin-the-phrase-their-message-names
description: A structural grep-test over a prompt artifact fails silently when its assertion matches a token that also occurs elsewhere in the guarded text — the assertion passes, its own failure message names a clause nobody is guarding, and only a word-level mutation of that exact clause exposes it; this recurred FOUR times in one branch, each instance introduced by the fix for the previous one, and every instance was caught by review rather than by the mutation battery, because deleting whole sentences leaves the duplicate token intact
type: practice
origin: harden-memory-store-integrity-checkpoint whole-branch review (2026-07-31), rounds 1-3
---

Guarding a prompt artifact (a SKILL.md step) with substring assertions, four assertions in one branch passed while the clause each claimed to guard was deletable:

| Assertion | Message claimed | Actually satisfied by |
|---|---|---|
| `"check_loom_memory_integrity.py" in text` | names the script | any cross-reference anywhere in the file |
| `"n/a" or "absent" or "not present"` | prescribes the loud N/A line | the word "absent" in the bullet's *condition* clause |
| `"docs/loom/memory/" in bullet` | names the trigger path | the parallel-wave clause and the §Index sentence |
| `"repo root" in bullet` | states the cwd qualifier | the sentence saying where the script *lives* |

Each was introduced by the fix for the previous one. The `byte-identical` assertion was disarmed the same way by an unrelated 🟢 fix: adding a fifth invariant to a failure enumeration put a second copy of the token in the bullet, so deleting the load-bearing run instruction left every test green.

The mutation battery did not catch any of them. It deleted whole sentences and whole bullets — and a duplicate token survives sentence deletion, because the duplicate lives in a *different* sentence. Every instance was found by a reviewer probing at word level.

**Why:** an assertion's failure message is a claim about what it guards, and a bare `in` test over a document does not honour that claim — it only asks whether the string exists somewhere in scope. The narrower the scope, the safer, but scoping to the bullet is not enough when the bullet itself repeats the term (a well-written instruction repeats its key terms deliberately: once to prescribe, once to explain, once to enumerate). The failure is invisible to the author, who reads the assertion and its message together and sees agreement, and invisible to sentence-level mutation testing. The cost here was three review rounds, and each round's fix seeded the next instance.

**How to apply:** (1) Assert the **phrase the failure message names**, not a token inside it — `"copied **byte-identical**"`, not `"byte-identical"`; `"from the repo root"`, not `"repo root"`; `"added or edited a file under \`docs/loom/memory/\`"`, not the path. (2) Before trusting a guard, `count()` the token in the guarded scope; more than one occurrence means the assertion is pinning an unknown one of them. (3) Mutate at **word level, inside the specific clause**, not by deleting sentences — the shape that catches this class is "reword this clause while leaving the rest of the bullet intact". (4) Re-run the whole battery after every fix, including fixes to unrelated findings: three of the four instances here were created by a fix, and two were created by fixes to findings in a different dimension. Related: [[a-test-can-be-correct-and-still-unable-to-fail]], [[assertion-must-encode-the-property-it-claims]], [[construction-guaranteed-invariant-proves-nothing]].
