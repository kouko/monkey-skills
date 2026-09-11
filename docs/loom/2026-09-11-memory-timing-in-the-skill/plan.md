# Memory timing in the skill — plan
intent: 2026-09-11-memory-timing-in-the-skill@f55785199

## Current State Evidence

- Forward: `docs/loom/memory/README.md` under `## When to record` carries the rule in full, in this repository's data, where a project installing the plugin never reads it.
- Reverse: `loom-workflow/skills/loom-memory/SKILL.md` under `**Steps:**` for Record classifies what qualifies but says nothing about when to record relative to the branch.
- Error: `loom-code/skills/review/SKILL.md` mentions memory nowhere across its six sections, so the station that surfaces lessons never asks whether any were kept.
- Data: `docs/loom/memory/` holds 293 lesson concepts, grown at roughly two a day with no systematic prompt; the change must not raise that rate.
- Boundary: `loom-code/scripts/test_simplified_station_text.py` reads `loom-workflow/` prose, the cross-plugin coupling this family already pays for; a new test must not add another, so each plugin's text is pinned by a test inside that same plugin.

## Task DAG

### Wave 1 — The rule travels with the plugin

**W1-01 Put timing and scarcity into the memory skill's Record contract**  after: --  acceptance: 1, 2, 3, 6
- Files: loom-workflow/skills/loom-memory/SKILL.md, loom-workflow/skills/loom-memory/references/operations.md
- Test: A1 positive: rule-readable-from-the-installed-skill-alone; negative: no-dependency-on-a-repository-store-file. A2 positive: fresh-agent-records-in-branch; boundary: rule-states-the-cost-of-the-late-branch. A3 positive: post-merge-exception-and-batching-stated; negative: exception-not-widened-beyond-observed-after-merge. A6 positive: four-operations-unchanged; negative: no-station-invocation-added.
- Risk: Agent-decided: the rule's wording is carried over from the store charter rather than rewritten, because the intent fixes its content and only moves its home; a reworded rule would be a second drift surface against the charter.

**W1-02 Pin both halves of the rule from inside loom-workflow**  after: W1-01  acceptance: 4
- Files: loom-workflow/skills/loom-memory/scripts/test_skill_contract.py
- Test: A4 positive: both-halves-pinned-timing-and-scarcity; negative: deleting-either-half-turns-the-test-red; boundary: the-guard-s-own-tolerances-are-documented-in-the-test-module-not-here. A4 positive: failure-message-and-docstring-name-the-2026-07-deletion; negative: no-bare-assert-without-a-reason.
- Risk: Agent-decided: the test lives beside the skill it pins, not in the repo-root suite, so the plugin keeps proving its own contract in an isolated install.
- Risk: Agent-decided: the test carries its own justification in the docstring and in every failure message. A phrase-presence assertion is a golden test at string granularity, and its documented failure mode is that a red test gets updated rather than investigated — which is how the 2026-07 instruction and its test were removed together. No tooling defends against that; only a message that tells the next editor what they are about to delete.

**W1-03 Freeze a cold-reader eval that catches dilution**  after: W1-01  acceptance: 2, 4
- Files: loom-workflow/skills/loom-memory/evals/record-timing.md, loom-workflow/skills/loom-memory/evals/record-timing-cases.json
- Test: A4 positive: fresh-agent-given-only-the-record-contract-and-one-real-case-records-in-branch; negative: same-agent-rejects-the-majority-of-candidates. A2 positive: baseline-run-recorded-with-its-verdict; boundary: eval-is-a-frozen-reference-run-not-a-ci-job.
- Risk: Agent-decided: follows the shape `loom-workflow/skills/critique/evals/` already uses — a machine-readable case file plus a frozen reference run — rather than inventing a harness. An agent cannot run in CI, so the eval is re-validated when the contract text changes, and the regression test is what runs every push.

### Wave 2 — The flow asks at the right moment

**W2-01 State the moment and the bar in the closing review**  after: W1-02  acceptance: 5
- Files: loom-code/skills/review/SKILL.md
- Test: A5 positive: text-sits-between-convergence-and-finalize; negative: names-no-plugin-and-invokes-nothing; boundary: no-gate-marker-so-the-mechanism-count-is-unchanged.
- Risk: Agent-decided: placed at the end of the convergence section rather than in Finalize, because the sentence must be read before the attestation exists — recording after it is generated invalidates it, which is the excuse that pushed the two previous changes past the line.

**W2-02 Pin the review station's text from inside loom-code**  after: W2-01  acceptance: 4, 5
- Files: loom-code/scripts/test_review_convergence_contract.py
- Test: A4 positive: review-text-pinned-in-loom-codes-own-suite; negative: no-new-cross-plugin-read. A5 positive: pin-covers-both-timing-and-scarcity; boundary: every-assertion-scoped-to-the-passage-never-to-the-whole-station-file.
- Risk: Agent-decided: extends the test that already pins this same station's same section, not `test_simplified_station_text.py` — that module reads `loom-workflow/` prose and is one of the four cross-plugin couplings the previous change worked to stop deepening. How the matcher behaves — what it tolerates, what falsely reds, what to do about it — is stated in that module and nowhere else; this plan states the outcome only, because a mechanism's properties restated across documents drift the moment one is corrected.

### Wave 3 — The change obeys its own rule

**W3-01 Record this session's lessons under the new bar**  after: W2-02  acceptance: 2
- Files: docs/loom/memory/, docs/loom/2026-09-11-memory-timing-in-the-skill/evidence/, loom-workflow/skills/loom-memory/scripts/test_store_fidelity.py (deleted — it compared the store against a moving origin/main, so post-merge it forbade the store from ever changing)
- Test: A2 positive: lessons-land-in-this-branch-not-a-follow-up; negative: candidates-rejected-by-the-scarcity-bar-are-named-with-their-reason and the recorded count is smaller than the candidate count.
- Risk: Agent-decided: the change applies its own rule to itself as the first real exercise; every rejected candidate is named with the reason so the bar's effect is visible rather than asserted.

## Questions asked

- 1 — what — 你要的是：把「什麼時候記憶體」這條規則從這個 repo 的資料檔，搬進記憶 skill 自己的契約。對嗎？
- 1 — consequence — 要不要給它牙齒：只寫進 skill（不擋人、零機制成本）還是再加 checker 規則（擋得住，但判準是判斷、會誤報，且永久多一個機制加 budget exception）。
- 1 — what — 這次要不要用 Codex 當第二位讀者？
- 1 — what — 機制放在 loom-memory 裡還是 loom-code 裡？
- 1 — what — review 產生的 memory 會不會是一堆零散的實作錯誤？
- 1 — consequence — Acceptance 4 要一支測試同時擋刪除與稀釋，但字串斷言測不到稀釋：要拆成兩個機制（測試擋刪除、冷讀評測擋稀釋），還是把「或被稀釋」拿掉？

## Risks

1. user-decided — kouko chose option A2: the rule in the skill's contract plus a non-invoking sentence in the review station, protected by regression tests, with no checker rule. The rule's own criterion is a judgement, and a gate built on a judgement misfires often enough to be learned and ignored.
2. user-decided — kouko declined a second vendor for this change.
3. The store grows at roughly two entries a day with no prompt at all. A prompt that carried only timing would raise that; the text has to lower it, and W3-01 is where that claim is first tested against real candidates.
4. The review station is loom-code's, and memory is loom-workflow's. A sentence that names the plugin, or a test that reads across, rebuilds the coupling the previous change removed — each half is pinned from inside its own plugin for that reason.
5. The regression test is itself the thing most likely to be edited away. Verified 2026-09-11: asserting that prose still contains required phrases has no established industry practice, and the nearest documented relative — golden and snapshot testing — fails by being blindly re-approved. W1-02 answers this with wording, not tooling, because no tooling exists for it.
6. An unmarked paragraph is not a gate and cannot block. Nothing here guarantees the rule is followed; it guarantees the question is asked at the moment when answering it is free.
