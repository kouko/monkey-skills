<!-- ESCALATION OVERRIDE BLOCK — byte-identical across all skills that ship it.
     If you edit this file, you MUST also edit:
       legal-toolkit/skills/legal-contract-review/assets/escalation-override.md
       (Phase 2+: every other skill's assets/escalation-override.md)
     Phase 6 adds a CI gate that diffs all copies for byte-identity.

     This block is PREPENDED to the affected output file's header when ANY
     of these conditions is met (see TECH-SPEC §6.2 for the full list):

       - risk_default: red on matched entry
       - walk_away_triggered: true
       - LLM confidence < 0.7
       - always_escalate rule hit (criminal liability / 重大訊息揭露 /
         賠償 > 年營收 10%)
       - deal_size > profile.escalation_threshold
       - cross-border + 個資事故 (mandatory)

     Banner PLACEMENT SCOPE (v0.3.4+ Phase 1.8):
       - PREPENDED TO: legal.md (lawyer-facing, absorbs former
         memo-legal + escalation + issues + redline sections)
       - NOT prepended to: business.md (non-lawyer audience never
         carries the banner)
       Rationale: banner on the non-lawyer business doc trains users
       to skip the warning. Lawyer-facing audience needs the warning
       prominent at top. self_grade.py ANS-05 enforces [!danger] in
       legal.md head only when override_triggered=true.

     v0.3.3 (pre-consolidation) rule was: banner on memo-legal.md +
     escalation.md only (2 files of the 5-file set). Consolidation
     to 2 .md merges those into one — banner placement reduces from
     2 files to 1 file.

     The [trigger 1] / [trigger 2] placeholders are filled by the emitting
     skill at runtime with concrete trigger descriptions.

     Strip rule: even when --external-share strips playbook IDs, this
     Override is NEVER stripped — the counterparty/third party needs to
     see the warning even more than internal readers do.
-->

# [原本的標題]

> [!danger] ⚠️ 高風險議題——本工具強烈建議諮詢執業律師
>
> 本次 review 偵測到以下高風險訊號：
> - [觸發條件 1]：[簡述]
> - [觸發條件 2]：[簡述]
>
> 本工具的分析**僅供初步參考**。涉及上述議題時：
> 1. **不要**直接採用本工具輸出做最終決定
> 2. **必須**諮詢執業律師（建議：理律 / 寰瀛 / 眾達 / 協合 / 漢威 / 或公司現有外部律師）
> 3. 將本工具輸出作為**律師討論的初稿材料**，加速但不取代律師判斷

---

[原本的內容]
