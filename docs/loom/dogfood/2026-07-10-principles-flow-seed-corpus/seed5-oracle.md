# Oracle — seed5 線上預約排班 SaaS (grader only; operator never sees this)

named_anchors: Working Backwards; Material Design; WCAG 2.2; React; TypeScript; FastAPI; PostgreSQL; 12-Factor App
# note: each MUST appear in ## Anchors with a non-empty version/edition cell.
# WCAG 2.2 — named standard counts as canon; AA level stated. React/FastAPI —
# frontend/backend stack, named in prose, must still anchor. 12-Factor App —
# deployment convention named in passing prose. Dual-stack (frontend +
# backend) both must anchor.

deferred_items: 預約記錄保留期; SLA/uptime 目標
# note: each MUST appear in ## Open Questions with a — re-trigger:.
# 預約記錄保留期（法規待查，Q8）; SLA/uptime 目標（待首批店家營業時間分布）.

out_of_jurisdiction_bait:  # must be explicitly noted OUT, never become principles
  - 月費三檔（免費/390/990）          # pricing
  - Q4 上線搶旺季                     # timeline

stances:          # each individual stance needs a carrying principle (merging OK)
  - 時段庫存即時正確性（零重複預約）
  - 顧客 30 秒完成預約（流暢優先）
  - 雙使用者（店家後台/顧客前台）
  - LINE + email 通知（簡訊除外）
  - 快速迭代優先                      # packed in ONE bullet with the next four
  - 決策偏可逆（用現成的）
  - 雲端成本上限月一萬（超過降級）    # note: this one is DECIDED, not deferred
  - 個資最小化＋電話遮罩
  - 工程全委派（只看結果）            # escalation appetite → may be process-context; must not be silently dropped (explicit note or principle)

negative: 企業版; 簡訊通知作為 v1 原則
# note: 企業版 is explicitly scoped out; 簡訊通知作為 v1 原則 is a deferred
# channel (SMS is out for v1, LINE + email only) — presence of either as a
# committed principle is a regression.

traps_summary: 5-stance single bullet; stack named in prose; canon (Material Design/12-Factor) in passing prose; TWO deferred items; cost stance is decided (trap: don't confuse with deferred); dual-stack (frontend+backend) both must anchor.
