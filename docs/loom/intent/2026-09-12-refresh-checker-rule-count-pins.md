# 更新 checker 規則數量的測試基準
originator: kouko
kind: engineering
needs-design: no — 僅同步既有測試對 checker 規則集合與數量的預期，不改變使用者介面或執行行為
evidence: [loom-code/scripts/test_loom_checker_cli.py, loom-code/scripts/test_probes_language_policy.py]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
新增 `standing.second-vendor-valid` 後，三個測試仍固定期待舊的 19 條規則，導致完整套件在 1154 個測試通過後仍失敗，阻止 attestation 與 PR。

## Proposed outcome
把規則集合與數量基準同步為 checker 目前可重算的 20 條，讓完整套件準確反映已登記的新規則。

## Acceptance
1. checker 規則集合測試包含 `standing.second-vendor-valid`，並與 `--list-rules` 完全一致。
2. 兩個規則數量測試都期待 20，完整 package suite 不再因舊的 19 條基準失敗。
3. 修正只更新測試預期，不改 checker、`suggest` 行為或其他產品程式碼。

## Constraints
- 保留 `standing.second-vendor-valid` 與 mechanisms registry 現況。
- 不藉此調整其他測試或清理無關程式碼。

## Out of scope
- 改變 second-vendor 模式或判斷邏輯。
- 修正前一輪 Review 留下的非阻擋 nit。
- 更新 plugin 版本或發行說明。

## Open questions
- none
