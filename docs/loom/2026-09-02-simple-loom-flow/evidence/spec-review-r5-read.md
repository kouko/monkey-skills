# spec 讀審 — round 9（r5 對抗後的 delta）— 2026-09-02

兩個 fresh reviewer（opus、sonnet）只審 `6eb0a6a9..3cab1a4a` 的 delta 與 SR5-01..14 是否關閉。前提：kouko 已逐項確認三處可見行為（決策點②重確認）。

| reviewer | verdict | 關閉 | notes（處置） |
|---|---|---|---|
| opus | PASS_WITH_NOTES | 14/14（5/7 數字覆核通過） | NF-1 無可逆選項時無出口→§4 補「停住不做、交決策點③」；NF-2 對抗 probe 仍自填→§7 改為兩類 probe 皆由 checker 自跑、W1-06 加 `push.probes-adversarial`；NF-3 build SKILL／manifest 仍寫硬帽→同步為預算措辭；NF-4 即興提問無落點→review.json 加 `questions[]`；NF-5 記帳 pending→回填 sha；intent Acceptance #2 應註切換日重授信（待 kouko 一句確認） |
| sonnet | PASS_WITH_NOTES | 12/14（2 條在 plan，範圍外） | 🔴 review.json resolved 仍 pending（同 NF-5，已回填）；requires-contract 無 §7 條目→補；A-1 無 push 重算→同 NF-2；user-judgment-leak 未進維度表→補；`scope` 無消費者→checker 的 spec-pass 讀它（已有） |

spec_vs_intent：一致；唯一漂移＝REQ-2 的切換日重授信未反映在 intent Acceptance #2。
