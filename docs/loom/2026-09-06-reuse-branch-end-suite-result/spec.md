# Single-owner local push-gate package test — spec
intent: 2026-09-06-reuse-branch-end-suite-result@ddee7445
confirmed-behavior: 2026-09-07 @aed53de
pre-build-review: required — this change moves an executable release gate between workflow stages and changes the public Ship contract

## Requirements
REQ-1 — The local push gate owns package tests
  WHEN Ship issues the named-branch push after the branch-end checkpoint and user acceptance, the supported host's local push hook shall invoke the deterministic push checker, which shall execute the repository's resolved complete package-test command exactly once in the selected repository before allowing the network push; the checker shall capture the validated HEAD and clean working-tree state before package and adversarial execution, then block unless HEAD and the working tree remain unchanged afterward → Acceptance #1, #2

REQ-2 — Ship has no duplicate preflight run
  WHEN Ship reaches its Push step, the Loom flow shall not invoke the push checker as a separate preflight before `git push`; the hook-triggered checker shall remain the only package-test execution in that unchanged Ship attempt, and a missing or inactive supported-host hook shall block Ship rather than permit an unchecked push → Acceptance #2

REQ-3 — Repository-neutral behaviour
  WHERE a repository supplies or permits detection of a complete package-test command through Loom's existing command-resolution contract, the push gate shall operate without classifying source paths, filename extensions, programming languages, frameworks, dependency graphs, or Monkey Skills-specific directories → Acceptance #3

REQ-4 — Explicit command-resolution outcomes
  IF `package-tests` is absent but existing repository markers identify a command, THEN the push gate shall run that detected command; if neither declaration nor detection yields a command, it shall block; an explicit `package-tests: none` shall preserve the existing visible no-run exemption; and malformed argv, a missing executable, timeout, interruption, dirty tree, or non-zero exit shall block before push → Acceptance #4

REQ-5 — Failure returns to the owning station
  IF the package-test gate fails and resolving it changes tracked repository content, THEN the Loom flow shall return to Build and require a new complete branch-end checkpoint before another Ship attempt; if resolution changes only the local environment and Git content remains byte-identical, it shall preserve the checkpoint and permit retrying the push gate → Acceptance #5

REQ-6 — Preserve only existing close-record shapes
  IF Ship adds only the existing mechanically validated review-only acceptance or question entries and the existing intent-status-only close line after branch-end, THEN the Loom flow shall preserve the checkpoint relationship; every other tracked-content change shall invalidate it and require a new branch-end checkpoint → Acceptance #2

REQ-7 — Measured reduction over the same Ship-to-push boundary
  WHEN baseline and candidate replay the same representative accepted branch-end checkpoint from the start of Ship's Push step until the local gate either blocks or releases the network push, the evidence shall record the observed package-command invocation count and monotonic elapsed time for every invocation; the candidate shall execute exactly once, execute fewer times than the observed baseline, preserve the same release verdict, and have lower measured local-gate wait → Acceptance #6

## Design decision
- user-decided — Make the supported host's local push gate the sole owner and executor of the complete package-test gate, after the complete branch-end review and user acceptance; Ship removes its explicit preflight invocation and the actual push remains blocked until the observed run passes.
- user-decided — A package-test failure that requires tracked-content changes returns to Build and a new complete branch-end review; a local-environment-only repair with byte-identical Git content may retry the same push checkpoint.
- user-decided — Optimize only the duplicate Ship-to-push package-suite execution and measure baseline versus candidate during implementation; do not add a general cache, affected-test analysis, dependency graph, attestation, or CI integration.
- user-decided — Keep the behaviour repository-neutral rather than infer a "program body" from language-specific paths or filename extensions.
- agent-decided — Keep package execution inside the deterministic push checker instead of trusting a historical result or inventing a signed receipt: the hook observes the exit code in the same transition it blocks or releases.
- agent-decided — Preserve existing command resolution: an explicit command wins, absent declarations may use existing repository detection, absence without detection blocks, and explicit `none` remains a visible no-run exemption.
- agent-decided — Require the host hook for this workflow. A manual push outside the supported Claude Code or scaffolded Codex hook is outside the claimed Ship path and must not be presented as Loom-verified.
- agent-decided — Run the single suite only after all tree-changing branch-end probe, evidence, nit, and review work. Preserve only the existing checker-validated review-only acceptance/question entries and intent-status-only close line; every other later tracked change requires a new branch-end checkpoint.
- agent-decided — Execute in the repository selected from the intercepted push command, snapshot its validated HEAD and clean working-tree state, and recompute both after the package suite and adversarial probes; a command that moves HEAD or changes the working tree blocks the push even when it exits zero.
- agent-decided — Keep adversarial probes as push-time recomputes because this intent removes only the duplicate complete package suite.
- user-decided — Use Claude as the second-vendor reader for this change.

## Alternatives considered
- Let Ship trust the package-test result string in `review.json` — rejected because the repository principles forbid a gate from trusting an agent-authored claim and Git cannot prove that a historical process ran.
- Run the suite only at branch-end and accept that checkpoint at Ship — rejected because a copied, fabricated, interrupted, or legacy checkpoint has the same repository-visible shape; proving execution would require a new trusted attestation mechanism.
- Maintain a safe-path or source-extension allowlist — rejected because Markdown skills, contracts, templates, configuration, generated inputs, and other repositories do not share a reliable definition of source code.
- Add a content-addressed test cache — rejected because cache storage, input discovery, environment hashing, invalidation, and cross-machine trust are larger mechanisms than the single duplicated run warrants.
- Keep both Ship's explicit checker call and the hook-triggered call — rejected because the same deterministic gate runs twice against unchanged content immediately before one push.
- Use dependency-graph affected tests — rejected because it changes test coverage and requires language- and build-system-specific integration, while this change must preserve the existing complete command.

## Current state evidence
- Forward: `loom-code/skills/review/SKILL.md` section `Package tests` requires a branch-end run and records a `kind: package-tests` entry, creating the first execution site this change removes.
- Reverse: `loom-code/skills/ship/SKILL.md` section `Push` explicitly invokes the checker and then states that the host PreToolUse hook invokes the same command again when `git push` is issued, creating two local-gate executions in one unchanged Ship attempt.
- Error: `loom-code/scripts/loom_checker.py` function `cmd_push` ignores non-push-shaped hook payloads, resolves the repository selected by the actual push command and calls `_cmd_push`; `_cmd_push` calls `check_probes_package_tests`, which checks the current working tree before execution, resolves the repository command, executes it without a shell and blocks on malformed argv, missing executable, timeout, or non-zero exit. It does not yet recompute HEAD and working-tree state after package and adversarial execution.
- Data: `loom-code/contract/manifest.yaml` declares the repository `package-tests` command and `review.json` probe fields `kind`, `command`, `sha`, `result`, `artifact`, and `scope`.
- Boundary: `loom-code/skills/ship/SKILL.md` and `loom-code/scripts/loom_checker.py` separately enforce review-only HEAD, reviewed-sha continuity, review schema, reviewer floors, adversarial probes, task coverage, and second-vendor requirements; these remain outside the package-test ownership move.

## UI flows
### Branch-end
- 所有 Build task 完成後 → 系統完成正式審閱、盲跑、對抗驗證以及其產生的所有 repository 內容修改，再建立綁定最終實作版本的 checkpoint；此階段不執行完整 suite。
- branch-end 後除了既有 checker 能驗證的 review-only 接受／問題紀錄與 intent-status-only close line 之外，出現任何 tracked-content 修改 → 原 checkpoint 失效，必須重新完成 branch-end；不以檔案類型猜測修改是否安全。

### Ship
- 使用者接受盲跑報告並進入 Ship → Ship 不先執行完整 suite，而是直接發出具名分支的 `git push`。
- 支援的本機 host hook 攔截 push → deterministic push checker 核對 checkpoint 與 Git continuity，記住當下 HEAD 與 clean working tree，並執行完整 suite 唯一一次及既有 adversarial probes；只有所有命令成功且結束後 HEAD／working tree 仍完全不變，才讓 network push 繼續。
- host hook 缺少或未啟用 → Ship 停止，不能把未受本機 gate 保護的手動 push 宣稱為 Loom Ship。
- 完整 suite 因程式、測試或設定問題失敗且需要修改 repository → 回到 Build 修正，再重新完成完整 branch-end review。
- 完整 suite 只因本機工具或暫時環境問題失敗，且 Git 內容完全未變 → 修復環境後保留 checkpoint，直接重試 push gate。
- `package-tests` 未宣告但可由既有 marker 偵測 → 執行偵測命令；無法宣告或偵測、命令不可執行、逾時、中斷、dirty tree 或非零退出 → 阻止 push；明確宣告 `none` → 顯示沒有 suite 的既有缺口並繼續其他 gates。

### Measurement
- 實作途中從 Ship 的 Push step 開始，到本機 gate 阻止或釋放 network push 為止，對同一個已接受 checkpoint 執行 baseline／candidate replay。
- 報告列出實際觀察到的完整測試執行次數、每次 monotonic 經過秒數、總本機 gate 等待秒數與 release verdict；不先假定 baseline 次數。只有 candidate 恰好執行一次、少於 baseline、實測更快且 verdict 相同時才宣告加速。
