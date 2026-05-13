# Authority-letter mode — compliance review checklist

> Hand-curated checklist aligned with current in-force Taiwan PDPA + 公文程式
> conventions + relevant 主管機關 監理 / 函詢 / 處分 法源.
> Each item is verified by the LLM during the COMPLY_CHECK step of
> `protocols/authority-letter.md`.
> Verdict options: PASS / FAIL / TBD_<id> where <id> is from
> `references/pdpa-current-state.md` canonical OPEN list (fabricated ids fail
> SELF_GRADE); TBD applies only when the 函詢事項 has PII-breach overlap.
>
> Path A discipline: each item phrases the rule by naming the **correct**
> statutory citation + Taiwan PDPA terminology (委託者 / 受託者 etc., per
> 個資法 §4). Forbidden phrasings are enumerated in
> `scripts/grade_response.py` `PATH_A_ANTIPATTERNS` (single source of truth);
> do not inline them here, even in "NOT X" form.

## §1 函要求齊備性（incoming extraction completeness）

- [ ] 收文日 ISO 8601 date 標示於 §1 incoming 函要求摘要？ — **{{verdict}}**
- [ ] 主管機關名稱 + 字號 verbatim quote 完整於 §1 / §時間軸？ — **{{verdict}}**
- [ ] 法源依據 (incoming 引用條文) 完整列舉於 §2 法源依據？ — **{{verdict}}**
- [ ] 要求項目 verbatim quote 或 summary 完整於 §3 函覆草稿「說明 一、來文要求」？ — **{{verdict}}**
- [ ] deadline 清楚標示於 §1 + §時間軸？ — **{{verdict}}**

## §2 函覆 deadline 標示

- [ ] §時間軸 含 deadline ISO 8601 date (`YYYY-MM-DD` 格式)？ — **{{verdict}}**
- [ ] 我方擬定回函日 (`reply_date`) leave buffer ≥ 2 天 before deadline？ — **{{verdict}}**
- [ ] business.md §3 deadline 警示 顏色正確 (🔴 < 3 天 (0-2 天) / 🟡 3-7 天 (含) / 🟢 > 7 天)？ — **{{verdict}}**

## §3 法源引用 valid（無 invented §s）

- [ ] §3 函覆草稿「說明 三、法源依據」 每個 cited §number 都在
  `legal-toolkit/scripts/canonical/legal-sources.json` `statute_sources`？ — **{{verdict}}**
- [ ] URL pattern 為 `law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=...&flno=...`
  （per canonical `single_article_url_template`）？ — **{{verdict}}**
- [ ] 沒有 LLM 自行 invent 的 §number（任何 §s 不在 canonical 即 FAIL）？ — **{{verdict}}**
- [ ] 若 incoming 來文引用之法源 未列於 canonical，已 surface 到 user 並取得確認？ — **{{verdict}}**

## §4 主管機關權限對齊

- [ ] 函詢事項屬於 incoming_authority 之權限範圍？
  （e.g., 金管會 證券交易監理 vs 個資組 個資監理 vs 公平會 競爭法 vs
  勞動部 勞動基準 — 跨組常見錯置）— **{{verdict}}**
- [ ] 若 incoming 與 authority 之 statutory 權限 mismatch，函覆中 raise objection
  或 escalate 給 user？ — **{{verdict}}** (PASS / N/A 若 mismatch 不存在)
- [ ] 若涉及多重主管機關（e.g., 金管會 + 個資組 平行函詢），是否分別 reply
  或在單份函覆中 cross-reference？ — **{{verdict}}** (PASS / N/A)

## §5 公文格式（Taiwan administrative letter format）

- [ ] §3 函覆草稿 公文結構齊備：受文者 / 發文字號 / 主旨 / 說明 / 附件清單 / 落款？ — **{{verdict}}**
- [ ] 主旨 為 1 句具體 summarize 函要求重點 + 本公司回應方向？ — **{{verdict}}**
- [ ] 「說明」 段含 一/二/三 (或 一/二/三/四) 項細分 (來文要求 / 本公司回應 / 法源依據 / 後續行動)？ — **{{verdict}}**
- [ ] 落款 含 company / company_id (統一編號) / DPO 姓名 / DPO email / DPO phone /
  公司登記地址 / 日期 (ISO 8601) 七項齊備？ — **{{verdict}}**
- [ ] 附件清單 明列 (or 「無」 if no attachments)？ — **{{verdict}}**

## §6 對外溝通 flag

- [ ] 若回函涉及客戶責任 / 公開揭露（e.g., 證交所重訊查詢 涉股價敏感資訊），
  flag PR + IR 同步需求？ — **{{verdict}}** (PASS / N/A)
- [ ] 若回函涉及個資外洩 / §12 通報 cross-reference，flag 是否 trigger PII-breach
  protocol 同 session 補跑？ — **{{verdict}}** (PASS / N/A)
- [ ] 若 sanction_risk = 「行政處分 imminent」，flag CEO + 外部律師同步通知？ — **{{verdict}}** (PASS / N/A)

## §7 TBD migration tracker（optional — only when PII-breach overlap）

- [ ] TBD_PDPC_pending 是否 applicable？
  (e.g., authority 為 PDPC 籌備處，且 函詢涉及 §12 sub-reg specifics 尚未公布
  施行細則之問題) — **{{verdict}}** (PASS / N/A / TBD_PDPC_pending)
- [ ] TBD_PDPC_threshold 是否 applicable？
  (函詢涉及 通報範圍授權子法 之 threshold 認定) — **{{verdict}}** (PASS / N/A / TBD_PDPC_threshold)
- [ ] TBD_PDPC_timeframe 是否 applicable？
  (函詢涉及 通報時限授權子法 之 具體時程認定) — **{{verdict}}** (PASS / N/A / TBD_PDPC_timeframe)

## 結構性

- [ ] §時間軸 完整：至少含 收文日 / 我方回函日 / deadline 三個 ISO 8601 anchors
  (處分日如未發以 `⏳ 待` 標記)？ — **{{verdict}}**
- [ ] DPO 聯絡完整：name / email / phone 三項皆填於落款？ — **{{verdict}}**
- [ ] 文件字號 (`document_reference_number`) 已填？ — **{{verdict}}**
- [ ] business.md §2 Top 3 即時動作 each 含 owner + deadline？ — **{{verdict}}**
- [ ] business.md §4 風險摘要 1-3 sentences 描述 worst case？ — **{{verdict}}**
