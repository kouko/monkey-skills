# 補齊清理版 evidence 的永久安全檢查
originator: maintenance-loop
kind: engineering
needs-design: no — only the committed adversarial evidence verifier changes
evidence: [docs/loom/2026-09-12-publish-sanitized-capture-evidence/evidence/probes/test_sanitized_evidence_public_safe.py]
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem
清理版 dogfood evidence 本身已通過人工與機械掃描，但永久 adversarial probe 漏掉先前實際出現的 UUIDv7，只檢查檔案總數而沒有鎖定完整路徑集合，也沒有直接拒絕所有已知敏感 metadata key，因此前一個 closing review 無法收斂並產生 attestation。

## Proposed outcome
讓永久 probe 直接重現並阻擋已觀察到的識別資訊、metadata 與檔案集合回歸，使清理版 evidence 可以在新的 bounded review episode 中被可靠驗證。

## Acceptance
1. Probe 使用版本無關的 UUID 判斷，並以最小 known-bad case 證明先前的 UUIDv7 形狀會被拒絕。
2. Probe 比對完整的 79 條相對路徑，而不只比對檔案數量。
3. Probe 直接拒絕已知的 session、request、hook、connector、tool/plugin inventory、memory/socket 與 thinking-signature metadata key，且從 hostile cwd 執行仍通過現有清理版 evidence。

## Constraints
- 只修改 adversarial probe 的安全覆蓋；不修改 79 份清理版 evidence、report 或實驗結論。
- 不新增 manifest、ID schema、checker rule、station 或 review loop。
- 未清理的 `raw-private/` 繼續只留在本機且不進 Git。

## Out of scope
- 重新執行或重新評分 dogfood。
- 改變 sanitizer、Loom station 或 publication 行為。
- 發布任何本機 executor metadata。

## Open questions
- none
