# Graduated probes stay green on a squashed main — plan
intent: 2026-09-06-graduated-probes-survive-squash@9c9cadf9
charter: 1.0

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py:2023` `find_plan_commit_sha` reads the subject `docs(loom): plan <id>` from git log.
- Reverse: `loom-code/scripts/loom_checker.py:2292` returns BLOCK `no plan commit found` when that subject is absent.
- Error: on merged main, `plan-edits 2026-09-05-artifact-charter-boundaries-and-edit-rights` exits 1; the squash removed the subject.
- Data: `loom-code/scripts/test_probes_charter_wave_end_2.py:216` asserts that command exits 0 for its own change-id.
- Boundary: `loom-code/scripts/rehearse_probes.py:168` `_clone_ci_shaped` clones full branch history, where the plan commit still exists.

## Task DAG

**W1-01 plan-edits reports not-applicable for a shipped change**
- Files: `loom-code/scripts/loom_checker.py`, new `loom-code/scripts/test_plan_edits_shipped_change.py`
- Test: a repo whose intent reads `status: closed` and whose plan commit is absent exits 0 naming not-applicable; the same repo with `status: confirmed` still blocks `no plan commit found`.
- Risk: agent-decided — the closed intent, not the missing commit, is the signal, so an in-flight change with a lost plan commit still blocks.

**W1-02 rehearsal also runs the probes in a squashed shape**
- Files: `loom-code/scripts/rehearse_probes.py`, `loom-code/scripts/test_rehearse_probes.py`
- Test: a probe asserting on its own change's plan commit passes the current clone and fails the squashed one, named in the output with its reason; removing the dependency turns both green.
- Risk: agent-decided — squash the clone to one commit off the trunk rather than re-cloning, so the existing CI-shaped check keeps running unchanged.

**W1-03 the charter probe states which shape it is in** after: W1-01
- Files: `loom-code/scripts/test_probes_charter_wave_end_2.py`, `docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_wave_end_2.py`
- Test: the positive control passes on a branch with the plan commit and on a squashed tree without it, asserting the reason each time rather than exit 0 alone.
- Risk: agent-decided — the evidence original is edited alongside its twin, the divergence rule of the branch-end twin-diff probe permitting only that.

**W2-01 the graduation paragraph carries the rule** after: W1-02
- Files: `loom-code/skills/build/SKILL.md`, `loom-code/scripts/test_build_station_text.py`
- Test: the graduation paragraph names the squashed rehearsal in an affirmative sentence with no negation token, and the word cap still holds.
- Risk: agent-decided — the sentence rides in the existing rehearsal prose gate rather than opening a second gate for one rule.

**W2-memory Memory step — graduated probes and store entries** after: W1-03, W2-01
- Files: graduated probe copies under `loom-code/scripts/`, `docs/loom/memory/` entries, `docs/loom/memory/README.md`
- Test: `python3 scripts/check_loom_memory_integrity.py` exits 0 and the graduated copies pass under the rehearsal.
- Risk: agent-decided — copies are byte-equal but for their path line, so a later reader can diff them against the evidence originals.

## Questions asked
1 — what — 你要的是合併之後 main 不要再因為這種事變紅，做完後你可以：在合併後的 main 上跑整包測試不再有測試因為找不到自己 change 的 commit 而紅；把一支故意依賴自己歷史的探針丟進畢業前的排練，排練當場紅並指名哪一支與為什麼；對一個已出貨的 change 問 checker plan 定稿後有沒有被亂改，得到「不適用」而不是看起來像「有人亂改了」的封鎖；在 build 站畢業段落讀到這條規則且有測試釘住。對嗎？（答：好）
1 — what — 這次要不要用 Codex 當第二位讀者？（答：好，用 Codex）

## Risks
1. A squashed rehearsal doubles the clone cost of graduation, measured at 2.7s per clone; accepted because it runs once per change, not per push.
2. Reading the intent's closed status makes the checker depend on a file the branch may not carry; W1-01 treats an unreadable intent as in-flight and blocks.
3. The rule lands in prose the cold reader must follow; the pinned test in W2-01 is what keeps it from drifting, as it did for the rehearsal sentence.
