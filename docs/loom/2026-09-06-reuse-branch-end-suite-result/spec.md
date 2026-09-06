# Single-owner branch-end package test — spec
intent: 2026-09-06-reuse-branch-end-suite-result@d8306c65
confirmed-behavior: 2026-09-06 @a092643
pre-build-review: required — this change moves an executable release gate between workflow stages and changes the public Ship contract

## Requirements
REQ-1 — Branch end owns the package-test gate
  WHEN all Build tasks are complete and branch-end review begins, the Loom flow shall execute the repository-declared complete package-test command exactly once against the final implementation commit in a clean tree, and a missing declaration, unusable command, dirty tree, or non-zero exit shall block the branch-end checkpoint → Acceptance #1

REQ-2 — Ship recomputes continuity without rerunning the suite
  WHEN Ship receives a passing branch-end checkpoint, the Loom flow shall recompute from Git that the checkpoint is valid, its reviewed implementation commit is still the commit being shipped, and every later commit has the permitted review-only or close-record shape; if all checks pass Ship shall not execute the package-test command, and otherwise it shall return the change to branch-end verification → Acceptance #2

REQ-3 — Repository-neutral behaviour
  WHERE a repository supplies a complete package-test command through Loom's existing command-resolution contract, the single-owner behaviour shall operate without classifying source paths, filename extensions, programming languages, frameworks, dependency graphs, or Monkey Skills-specific directories → Acceptance #3

REQ-4 — Measured reduction on the same case
  WHEN the baseline and candidate replay the same representative branch-end-to-Ship case with the same repository, implementation commit, package-test command, and expected release verdict, the evidence shall record each actual command invocation and monotonic elapsed time; the baseline shall execute the package suite twice, the candidate exactly once, both shall produce the same release verdict, and the candidate's measured wait shall be lower → Acceptance #4

## Design decision
- user-decided — Make branch-end the sole owner and executor of the complete package-test gate; Ship recomputes checkpoint and Git continuity but does not run the suite again.
- user-decided — Optimize only the duplicate branch-end-to-Ship package-suite execution and measure baseline versus candidate during implementation; do not add a general cache, affected-test analysis, dependency graph, or CI integration.
- user-decided — Keep the behaviour repository-neutral rather than infer a "program body" from language-specific paths or filename extensions.
- agent-decided — Move the existing executable package-test rule to the branch-end transition instead of adding a second receipt or cache mechanism; one owner preserves repository recomputation while deleting duplicated responsibility.
- agent-decided — Resolve the package command through the existing repository declaration and fallback rules so adopted repositories keep their current command and error behaviour.
- agent-decided — Treat any commit-continuity ambiguity as a return to branch-end rather than a Ship-time rerun; this keeps Ship fast and fail-closed with one recovery path.
- agent-decided — Keep adversarial probes as push-time recomputes because this intent removes only the duplicate complete package suite.
- user-decided — Use Claude as the second-vendor reader for this change.

## Alternatives considered
- Let Ship trust the package-test result string in `review.json` — rejected because the repository principles forbid a gate from trusting an agent-authored claim.
- Maintain a safe-path or source-extension allowlist — rejected because Markdown skills, contracts, templates, configuration, generated inputs, and other repositories do not share a reliable definition of source code.
- Add a content-addressed test cache — rejected because cache storage, input discovery, environment hashing, invalidation, and cross-machine trust are larger mechanisms than the single duplicated run warrants.
- Move the only complete suite run to Ship — rejected because branch-end would be able to declare a passing checkpoint before the repository's full tests had passed.
- Use dependency-graph affected tests — rejected because it changes test coverage and requires language- and build-system-specific integration, while this change must preserve the existing complete command.

## Current state evidence
- Forward: `loom-code/skills/review/SKILL.md` under the branch-end probe instructions requires the repository package-test command to run and records a `kind: package-tests` entry before `reviewed_sha` advances.
- Reverse: `loom-code/skills/ship/SKILL.md` Step 4 invokes the push checker after acceptance, and states that it re-runs the package tests recorded in `review.json` in a clean tree at `reviewed_sha`.
- Error: `loom-code/scripts/loom_checker.py` rule `push.probes-package-tests` resolves the declared command, creates a clean worktree at the reviewed commit, executes the command again, and blocks on a non-zero result.
- Data: `loom-code/contract/manifest.yaml` declares the repository `package-tests` command and `review.json` probe fields `kind`, `command`, `sha`, `result`, `artifact`, and `scope`.
- Boundary: `loom-code/skills/ship/SKILL.md` and `loom-code/scripts/loom_checker.py` separately enforce review-only HEAD, reviewed-sha continuity, review schema, reviewer floors, adversarial probes, task coverage, and second-vendor requirements; these remain outside the package-test ownership move.

## UI flows
### Branch-end
- 所有 Build task 完成後進入 branch-end → 系統在乾淨的最終實作版本上執行該 repository 原本宣告的完整測試一次，並顯示實際命令與結果。
- repository 沒有可用的完整測試命令、工作目錄不乾淨或測試失敗 → branch-end 明確顯示原因並停止，不建立通過的 checkpoint；修正後從 branch-end 重試。
- 完整測試通過 → 系統繼續 branch-end 的正式審閱、盲跑與對抗驗證，完成後建立綁定該實作版本的 checkpoint。

### Ship
- 使用者接受盲跑報告並進入 Ship，且 Git 顯示實作版本與 branch-end checkpoint 完全一致 → 系統核對 checkpoint 與後續關閉紀錄後繼續發布，不再次執行完整測試。
- branch-end 後出現新的實作變更、checkpoint 不合法或 Git 關係無法證明 → Ship 停止並指出必須回到 branch-end；它不在 Ship 臨時補跑測試來繞過失效的 checkpoint。
- checkpoint 與 Git continuity 合法，但其他既有發布檢查失敗 → Ship 維持原本的錯誤與修復路徑；完整測試不因無關 gate 失敗而重跑。

### Measurement
- 實作途中執行 baseline／candidate replay → 報告列出同一案例各自的完整測試執行次數、每次實際經過秒數、總等待秒數與最終發布 verdict；只有 candidate 少跑一次、實測更快且 verdict 相同時才宣告加速。
