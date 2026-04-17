# 消費系 / Consumption

Japan macro indicators -- retail and service sector spending.
Part of `japan-macro` skill. See `indicator-index.md` for full index.

---

### 小売業販売額 / Retail Sales

- **Source / データソース**: 統計ダッシュボード (preset=retail-sales, indicator=0601010201010010000)
- **Unit / 単位**: JPY 100 million (億円), nominal
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~4 weeks after reference month
- **Managing agency / 所管**: 経済産業省 (Ministry of Economy, Trade and Industry, METI)

**What it measures / 経済的意味**:
(EN) The total nominal value of goods sold by retail establishments across Japan. This is the primary measure of consumer spending on goods, equivalent to US Retail Sales.
(JP) 全国の小売業事業所における商品販売額（名目）。財に対する個人消費の実態を示す主要指標。米国のRetail Salesに相当。

**How to interpret / 解読方法**:
- Rising / 上昇 → Consumer spending on goods is increasing. Positive for domestic demand-oriented companies and consumption recovery narrative. / 財への消費支出が増加。内需企業・消費回復にポジティブ。
- Falling / 下落 → Consumer spending on goods is weakening. Negative for retail sector and domestic demand outlook. / 財への消費支出が減少。小売セクター・内需見通しにネガティブ。

**Market significance / 市場での重要度**: ⭐⭐
Retail sales data is released relatively quickly (~4 weeks lag) and provides a timely read on consumer spending trends. JPY can move on the release. However, this is a nominal figure (includes price effects), so it must be cross-checked with real consumption data for accurate volume assessment. Strong retail sales driven purely by price increases (inflation) do not indicate genuine consumption growth.

**When to use / 使用場面**:
Consumer spending trends, domestic demand assessment, retail sector analysis,
inflation pass-through to consumers (nominal vs real comparison).

**Japan-specific context / 日本固有の文脈**:
Japanese retail sales are heavily influenced by consumption tax hikes (last hike
from 8% to 10% in October 2019), which cause a demand surge before the hike and
a sharp drop after. Seasonal patterns include year-end/New Year shopping and
summer Obon gift-giving. The inbound tourism boom (post-2023 yen weakness) has
also boosted retail sales, particularly in department stores and luxury goods,
making it harder to isolate domestic consumer sentiment.

**Common pitfalls / よくある間違い**:
- This is NOMINAL data. Rising retail sales during inflation may reflect higher prices, not higher volumes. Cross-check with real household consumption expenditure (家計調査) for volume trends.
- Retail sales cover goods only, not services. In a services-led economy, this gives an incomplete consumption picture.
- Online sales are included but may be underrepresented due to survey methodology. The shift to e-commerce can distort establishment-based retail surveys.
- Do not confuse with "Commercial Sales Statistics" (商業動態統計), which includes both wholesale and retail. The retail-only figure is the relevant consumer spending proxy.

---

### サービス産業売上高 / Service Industry Sales

- **Source / データソース**: 統計ダッシュボード (preset=service-sales, indicator=0603010200000010000)
- **Unit / 単位**: JPY 100 million (億円), nominal
- **Frequency / 頻度**: Monthly
- **Publication lag / 公表遅延**: ~6 weeks after reference month
- **Managing agency / 所管**: 総務省統計局 (Ministry of Internal Affairs and Communications, Statistics Bureau)

**What it measures / 経済的意味**:
(EN) The total nominal revenue (sales) of service industry establishments, covering a wide range of services including information/communications, transport, accommodation, food services, entertainment, and professional services. Based on the Monthly Survey on Service Industries.
(JP) サービス産業の事業所における売上高（営業収入）の名目値。情報通信、運輸、宿泊、飲食、娯楽、専門サービス等を広範にカバー。月次サービス産業動態統計調査に基づく。

**How to interpret / 解読方法**:
- Rising / 上昇 → Service sector revenue growing. Can reflect volume growth, price increases, or both. / サービスセクターの収入増加。数量増・値上げ、またはその両方を反映。
- Falling / 下落 → Service sector revenue declining. Signals weakening demand for services. / サービスセクターの収入減少。サービス需要の弱さを示唆。

**Market significance / 市場での重要度**: ⭐
As a standalone indicator, market impact is low. However, when combined with the Tertiary Industry Activity Index (real, volume-based), it reveals pricing dynamics: if nominal service sales rise while the Tertiary Index is flat, the gap indicates service-sector price increases (値上げ). This combination is useful for detecting "quiet inflation" in services, which is the type of inflation the BOJ most wants to see for sustained 2% target achievement.

**When to use / 使用場面**:
Service sector revenue analysis, price vs volume decomposition (paired with
Tertiary Index), sector-level consumption analysis, services inflation detection.

**Japan-specific context / 日本固有の文脈**:
Japan's service sector has historically been characterized by "cost disease"
(productivity growth lagging manufacturing) and resistance to price increases.
The post-COVID period saw the first significant service-sector price increases
in decades, driven by labor shortages and input cost pass-through. The
hospitality sub-sector (accommodation, food services) was most affected by
COVID restrictions and has shown the strongest recovery, boosted by inbound
tourism and domestic travel campaigns (全国旅行支援).

**Common pitfalls / よくある間違い**:
- This is NOMINAL revenue, not real activity. Rising sales may reflect price increases rather than volume growth. Always pair with the Tertiary Industry Activity Index for a complete picture.
- The Monthly Survey on Service Industries (月次サービス産業動態統計) covers establishments with 10+ employees. Small establishments (which dominate Japan's service sector) are underrepresented.
- Sub-sector composition matters greatly. "Service industry" spans from high-value IT consulting to low-margin food services. Aggregate trends can mask divergent sub-sector dynamics.
- Do not confuse with the BOJ's Services Producer Price Index (SPPI, PR02), which measures B2B service prices, not revenue.
