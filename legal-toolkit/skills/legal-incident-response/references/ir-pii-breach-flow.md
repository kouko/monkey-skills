# PII-breach 法律流程 narrative reference

> Companion narrative to `protocols/pii-breach.md` + `checklists/compliance-pii-breach.md`.
> Use this when the LLM (or human reviewer) needs to navigate edge cases that
> the procedural protocol doesn't spell out — typical fork points: 通報時程是
> 否合規 / 委託處理場景下誰負通報義務 / 特種個資觸發書面同意機制 / 跨境傳輸
> 涉及主管機關公告等。
>
> Path A discipline: this file expresses every rule by naming the **correct**
> current Taiwan statutory citation and phrasing. The authoritative
> out-of-scope phrasing list lives in `scripts/grade_response.py`
> `PATH_A_ANTIPATTERNS` — extend that file, not this narrative.

## §0 適用範圍

本流程處理 **Taiwan 境內當事人個資外洩事件** 的法律回應，路徑包含：

1. PDPC 通報（個資法 §12 + 施行細則 §22）
2. 當事人通知（個資法 §12 衍生 + §8 揭露義務 cross-reference）
3. 內部事件記錄（公司法 §202 董事會職權 cross-reference + §27 安全維護義務）

不在本流程範圍：境外受影響當事人（涉外法律由 SP4 Phase 4.5 上市櫃 Compliance
研究階段延伸覆蓋）、HKSAR / 新加坡 / EU 個資法、營業秘密法外洩（屬於營業秘密
法第 11 條侵害救濟途徑）。

## §1 個資法 §12 通報義務（核心法源）

### §1.1 法源全文摘要

個資法 §12（2025-11-11 公布；行政院尚未公告施行日期）：

> 公務機關或非公務機關違反本法規定，致個人資料遭不法蒐集、處理、利用或其他
> 侵害當事人權利者，應即查明並以適當方式通知當事人。
>
> 違反本法規定致個人資料外洩之情形，主管機關得依個人資料之種類、外洩規模、
> 影響程度等，公告一定通報範圍及通報期間，要求公務機關或非公務機關，於該
> 通報期間內依規定向主管機關通報。

### §1.2 「即時」基準的法源依據

母法 §12 §4 授權主管機關以子法公告具體通報期間。母法施行日期未定、子法亦
尚未發布；現行可援引之最高位階法源仍為施行細則 §22：

> 公務機關或非公務機關依本法第十二條規定為通知或通報時，**應即時**為之。

實務含義：

- `incident_datetime → notification_datetime` 的延遲，須以「即時」標準
  自我評估；無法定具體小時數（具體小時數屬未來授權子法事項，標記為
  `TBD_PDPC_timeframe`）。
- 公司內部 SOP 可自訂具體時間目標（例：發現後 12 小時內通報），但該數字
  **僅屬內部績效指標**，不寫入 PDPC 通報文 body，避免被誤認為法源依據。
- 「即時」的合理性檢視點：（a）發現後是否立即啟動 incident response；
  （b）通報前是否已完成基本影響範圍評估；（c）通報文是否包含完整事故時間 /
  範圍 / 措施 / DPO 聯絡四要素。

### §1.3 §12 §2 通報範圍的 TBD 處理

§12 §2 授權主管機關公告通報範圍（依個資種類 / 外洩規模 / 影響程度）。子法
尚未發布；目前 incident response 採取「保守通報」策略：**任何涉及可識別
特定當事人之外洩事件即通報**，不自設豁免閾值。

若公司內部風險評估顯示為極低風險（例：影響筆數 < 內部閾值、無敏感資料），
仍應通報，並在 §6 Compliance Checklist 標記 `TBD_PDPC_threshold` 以利
子法公布後重評。

## §2 個資法 §4 委託處理場景的通報主體歸屬

### §2.1 法源

個資法 §4：

> 受公務機關或非公務機關委託蒐集、處理或利用個人資料者，於本法適用範圍內，
> 視同委託機關。

實務含義：**受託者** 在處理委託範圍內個資時，**視同委託機關**。但通報義務
的歸屬仍以「資料處理鏈中誰為對外責任主體」為準，通常落在 **委託者**。

### §2.2 三種典型場景的通報主體判定

| 場景 | 通報主體 | 法源 |
|---|---|---|
| 公司自有資料庫外洩 | 公司本身 | §12 + §4 (無受託者) |
| 委託雲端服務商，外洩源於服務商基礎設施 | 公司 + 服務商各自通報；公司負對當事人通知義務 | §4 視同委託機關 + §12 |
| 委託資料處理服務商，外洩源於處理過程 | 公司負主要通報義務；服務商配合 | §4 委託者全責原則 |

### §2.3 incident record 中的責任表述

`{{processor_involvement}}` 為「是」時，incident record 須額外揭露：

- 受託者公司名稱
- 委託契約中 §4 配套條款（資料處理協議 / DPA 引用）
- 通報義務分工：誰主動發 PDPC 通報文 / 誰主動發當事人通知

`{{processor_detail}}` 變數收容此段資訊。

## §3 §6 特種個資觸發的書面同意機制

### §3.1 法源

個資法 §6 列舉特種個資：**病歷 / 醫療 / 基因 / 性生活 / 健康檢查 / 犯罪
前科**。原則不得蒐集處理利用，例外見 §6 第一項各款（其中第 6 款為「經
當事人**書面**同意」）。

### §3.2 incident 場景下的驗證點

incident 若涉及特種個資，COMPLY_CHECK 需驗證 **原蒐集** 階段是否依 §6
合法事由：

- 若原蒐集依書面同意 → PASS（並引用當時取得同意之 mechanism 紀錄）
- 若原蒐集依其他 §6 第一項各款例外（法律明文許可 / 公務機關職務必要 /
  學術研究 / 當事人自行公開 / 為當事人重大利益必要 / 增進公共利益等）→
  PASS，引用對應款項
- 若無法定事由 → FAIL；此 incident 構成 §6 + §47 行政罰責任，須於業務
  摘要中標記為 CRITICAL 嚴重度

### §3.3 §9 第三人提供告知

§9 規定非經當事人同意之第三人提供，須於提供前告知。incident 若涉及特種
個資且原蒐集係 §6 但書場景（非書面同意路徑），則 §9 第三人提供告知機制
亦需檢視是否齊備。

## §4 §21 跨境傳輸的告知要點

### §4.1 法源

個資法 §21：主管機關得限制非公務機關對特定國家或地區之跨境傳輸。實務上
主管機關以公告方式發布限制（公告層級而非子法）。

### §4.2 incident 場景的揭露要素

`{{cross_border_assessment}} = 是` 時，PDPC 通報文 + 當事人通知均需揭露：

- 目的地清單（國家 + 地區層級；若為雲端服務商，列服務商主資料中心地理位置）
- 當地法律保護水準評估（簡述；非詳盡比較分析）
- 公司採取之保護措施（標準契約條款 / 加密 / 存取控制 / 等）
- 是否觸及主管機關公告之限制行業（金融 / 醫療 / 政府機關等）；若觸及，
  以 `TBD_GOV_CLOUD_restrictions` 標記，待 Tier-A 主要法源確認後再 lock

### §4.3 incident record 中的對應變數

`{{cross_border_detail}}` 收容上述四項揭露要素；若 `{{cross_border_assessment}} = 否`，
仍須在 incident record 中說明「已評估，不涉及跨境傳輸」，留下 audit trail。

## §5 §27 安全維護義務與「應變措施」對應

### §5.1 法源

個資法 §27：

> 非公務機關保有個人資料檔案者，應採行適當之安全措施，防止個人資料被竊取、
> 竄改、毀損、滅失或洩漏。

「適當之安全措施」未於母法定義具體內容；實務參考主管機關（含目的事業主管
機關）公告之安全維護計畫指引。

### §5.2 incident 場景的兩面落實

incident 後 §27 落實情況分為 **技術** + **行政** 兩面，分別由 incident
record 之 `{{technical_actions_bullets}}` + `{{administrative_actions_bullets}}`
記錄：

**技術措施** 典型項目：
- 阻斷異常存取（IP block / 帳號停權 / API token revoke）
- 修補漏洞（軟體更新 / 設定強化 / 加密層升級）
- 監控強化（log monitoring / IDS rules 補強 / WAF rule add）

**行政措施** 典型項目：
- 通報相關當事人（PDPC + 受影響當事人 + 內部關係人）
- 教育訓練（針對 incident root cause 之全員或重點對象訓練）
- 政策更新（修正 SOP / 修正 access control policy / 修正委託契約 §4 條款）

### §5.3 §20-1 audit framework 的 TBD 處理

§20-1（2025-11-11 公布，施行日期未定）課予 audit 義務。在子法（稽核辦法）
公布前，incident record 之 §27 段落以 `TBD_PDPA_audit_framework` 標記
audit framework 段落為「待補」。

## §6 民法 §12-13 未成年人保護

### §6.1 法源

民法 §12（2023-01-01 起修正生效）：

> 滿十八歲為成年。

民法 §13：

> 未滿七歲之未成年人，無行為能力。
> 滿七歲以上之未成年人，有限制行為能力。

實務含義：未滿十八歲之當事人為限制行為能力人，其法律行為原則需法定代理人
同意 / 承認。incident 場景下，當事人通知與後續救濟措施須加註法定代理人
收受 / 代為行使機制。

### §6.2 incident 場景的對應

`{{minor_involvement}} = 是` 時：

- 當事人通知正文增加「未成年當事人之法定代理人收受說明」段落
- 提供法定代理人專用聯絡管道（typically 同 customer_service_contact，但
  專人處理）
- 後續救濟（更改密碼 / 凍結帳戶 / 等）若涉及契約變更，須註明法定代理人
  同意 / 承認程序

注意：個資法本身未訂年齡門檻；本段法源係民法行為能力規定 cross-reference。

## §7 嚴重度判斷與業務摘要層級

`{{severity_level}}` 的判定不寫入法律 body（避免被誤認為法源依據），但
影響業務摘要的對外溝通強度：

| Severity | 觸發條件（任一） | 業務摘要 Top 3 動作示例 |
|---|---|---|
| LOW | 影響 < 100 人 + 無特種個資 + 已內部圍堵 | 內部複盤 + 客服話術 + 通報 |
| MEDIUM | 影響 100-1000 人 OR 涉跨境傳輸 OR 委託處理鏈 | 加：CEO 簡報 + 媒體 statement 待命 |
| HIGH | 影響 1000-10000 人 OR 涉特種個資 OR 涉未成年 | 加：主動發布 statement + 高階主管聯繫主要客戶 |
| CRITICAL | 影響 > 10000 人 OR 涉 §6 特種個資且原蒐集無 §6 例外事由 | 加：董事會召集（公司法 §202）+ 外部法律顧問 + 危機公關啟動 |

具體閾值由公司內部 SOP 決定；本表為典型範例，僅供業務摘要文案參考，**不
寫入 legal.md body**。

## §8 TBD canonical ids 一覽 + migration paths

下列 7 個 ids 為 `scripts/grade_response.py` 認可的 canonical OPEN list。
任何 `TBD_*` 出現在 `legal.md` / `business.md` 但不在此清單，會被 grader
判為 fabricated 並 FAIL。

### TBD_PDPC_pending

- **代表**：PDPC 由籌備處階段過渡至正式委員會階段；正式通報機制未驗證
- **trigger**：法務部 / PDPC 公告正式委員會掛牌
- **migration**：更新通報入口 URL + 通報主體名稱（籌備處 → 正式委員會）

### TBD_PDPC_threshold

- **代表**：個資法 §12 §2 通報範圍授權子法
- **trigger**：主管機關公告通報範圍規定
- **migration**：依新閾值規則重評本案是否仍需通報；若閾值規定可豁免低風險案件，補入「依新子法不需通報」之記錄

### TBD_PDPC_timeframe

- **代表**：個資法 §12 §4 通報期間授權子法
- **trigger**：主管機關公告具體通報期間
- **migration**：依具體時程規則 audit 本案 incident_datetime → notification_datetime 延遲是否合規；若否，補入「延遲說明」段落

### TBD_PDPC_notification_url

- **代表**：正式通報入口 URL（form / email / paper）
- **trigger**：PDPC 正式網站上線
- **migration**：更新 PDPC 通報文發送管道紀錄；retro 補列正確發送方式

### TBD_PDPA_effective_date

- **代表**：行政院公告 2025/11 批次條文施行日期
- **trigger**：行政院公報發布
- **migration**：整體 incident response SOP 重新檢視 §12 / §20-1 / §47-48
  等條文配套；本 reference 文件之相關段落由 "施行日期未定" 改為具體日期

### TBD_PDPA_audit_framework

- **代表**：個資法 §20-1 稽核架構
- **trigger**：主管機關公告稽核辦法
- **migration**：incident record §27 安全維護段落補入 audit-framework 子段落
  + 公司年度 audit 計畫更新

### TBD_GOV_CLOUD_restrictions

- **代表**：政府機關雲端服務之大陸地區限制具體規定（可能落於政府採購法 /
  資通安全管理法，非個資法）
- **trigger**：Tier-A 法源確認（全國法規資料庫條文 + 主管機關公告）
- **migration**：若 incident 涉政府機關雲端場景，補入限制條款引註

## §9 引用 + 維護

本 narrative 引用之法源 URL 一律經由 `references/statute-citations.md`，不
inline construct URL。若 `legal-toolkit/scripts/canonical/legal-sources.json`
URL 模板變更（極罕見；上次格式變更約 2015），需同步更新 `statute-citations.md`
+ 本檔之引用。

SP2 ground truth：`legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`
是本流程之 ground truth 來源；7 個 canonical TBD ids 與 5 項 GDPR 污染
反向標記皆出自該 research note。

更新觸發：當 SP2 research note 因子法公布 / 行政院公告 / 主管機關公告而
更新時，本檔 §1-8 相關段落須同步檢視。
