# <title> — spec
intent: <change-id>@<sha>
confirmed-behavior: <date> @<spec-blob-sha7>   # 只在 kind: product；決策點②後由 agent 寫
#   <spec-blob-sha7> = 寫這一行「之前」的 spec 檔 blob sha 前七碼（`git hash-object spec.md`）；
#   spec 之後被改寫，這一行就對不上，checker 會要求重新呈現一次可見行為

## Requirements                                    【使用者可讀；product 時呈現】
REQ-1 — <name>
  <一句可驗的義務> → Acceptance #<n>

## Design decision                                 【混合；不呈現】
<做什麼、不做什麼、為什麼；agent-decided 的岔路各附一句理由；user-decided 的單向門標 user-decided>

## Alternatives considered                         【工程；不呈現】
- <否決的替代與理由>

## Current state evidence                          【工程；不呈現】
- Forward：<路徑與錨點>
- Reverse：<…>
- Error：<…>
- Data：<…>
- Boundary：<…>

## UI flows                                        【使用者可讀；product 時呈現】
<每個操作與系統的反應（指令／畫面 → 輸出／狀態）；無介面寫 N/A>
