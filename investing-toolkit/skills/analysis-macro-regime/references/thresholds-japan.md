# Japan / 日本 — Macro Regime Thresholds & Calibration

**Authority**: 日本銀行 (Bank of Japan, BOJ) | **Currency**: JPY |
**Calibration vintage**: 2026-Q2

## Grounding Status (as of 2026-04-18)

**Last full verification**: 2026-04-18 via `../research/grounding-v1.9.0.md`
(5-country parallel grounding note; JP section).

**Verified (✅)**: 2013-01-22 2% 目標採用日、2026-02 完全失業率 2.6%、
Williams-like 定性語言。

**Corrected (🔴 in prior draft → fixed below)**:
1. **BOJ 政策利率 0.75%** — 2025-12 升息至 30 年來最高（prior draft
   wrote 0.5%）
2. **JILPT 均衡失業率 2.80%** (2026-02 latest) — NOT 3.5-3.6%.
   需要不足失業率 -0.17%。Current unemp 2.6% 是**軽度タイト only**，
   not "~1 pp below NAIRU".
3. **BOJ 展望 2025-10 FY 見通し**: FY2025/26/27 = 2.7% / 1.8% / 2.0%
   (prior draft wrote FY2024/25/26 = 2.5/1.9/1.9 — wrong by 1 year
   AND wrong 0.8 pp on FY2025).
4. **野村 森田京平 main scenario**: ターミナル 1.50% via 3 hikes
   (2026-06, 2026-12, 2027-06); prior draft wrote 2 hikes to 1.0%.
5. **10Y JP real yield -0.386% 数値削除** — 伊藤忠 2024-04 コラム
   本文不含此数値 (unverifiable fabrication risk).

**Partial (⚠️)**: WP24-J-09 r\* "mean -0.25%" → refined as **range
midpoint derivation**, not原典表述。

**New primary sources added**: BOJ 日銀レビュー rev26j05 (2026-03-27 —
最新官方 r\* 見解), lab18j02 (1980 年代以来 r\* 下降 4 pp 分解).

**2026-04-18 supplementary grounding**: Added BOJ 政策金利 3 層構造
details (誘導目標 0.75% 程度 / IOER 0.75% / 基準貸付 1.00%) + 実績
市場利率 (STRDCLUCON 0.727%) vs 目標 2-3 bp 乖離 mechanism +
2025-12-19 決議 PDF 長期国債減額ペース. Confirms toolkit's
FM01/STRDCLUCON fetch returns ~target ± 3 bp — acceptable precision
for regime call but should be cited as "target approximation".

### v1.10.0 addendum (2026-04-19)

Real-rate decomposition section populated with C+D+E multi-source framework:
- MoF 国債入札結果 (JGBi 第29-30回 auction real yields 単利, 2024-05 → 2025-08)
- ECB Data Portal SDMX series `FM.M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA` (ex-post monthly real)
- BOJ Tankan 企業物価見通し codes TK99F0000204/205/206HCQ00000 (1Y/3Y/5Y CPI outlook)

Correction #5 ("-0.386% 数値削除") superseded — v1.10.0 now supplies verified
anchor points. See `## Real Rate Decomposition` section below for full framework.
Full daily JGBi YTM solver (MoF 連動係数 + QuantLib) deferred to v1.11.0.

Grounding note: `../research/grounding-v1.10.0.md` documents primary-source
vetting for the 3 newly-trusted sources and JSDA / JBTS rejection rationale.

### v1.11.0 full refresh (2026-04-19)

Full re-audit since v1.9.0 (2026-04-18) + v1.10.0 (2026-04-19) Real Rate
Decomposition addendum. Covers 2026-Q1 BOJ meetings (1/23 + 3/19), 2026-01
展望レポート, 2025 春闘 最終集計, 2026 春闘 進展, BOJ rev26j05 follow-up, and
市場金利 / 審議委員人事 updates.

🔴 **BOJ FY2026 core CPI 見通し中央値**: 1.8% → **1.9%** (2026-01-23
展望レポート 上方修正; FY2025 2.7% / FY2027 2.0% unchanged). Sources:
https://www.boj.or.jp/mopo/outlook/gor2601a.pdf,
https://www.nikkei.com/article/DGXZQOUB231PP0T20C26A1000000/

🔴 **BOJ 実質 GDP 見通し中央値**: FY2025 0.7% → **0.9%**、
FY2026 0.7% → **1.0%** (2026-01 展望 両方上方修正). Source:
https://www.boj.or.jp/mopo/outlook/gor2601a.pdf

🔴 **2025 春闘 最終集計**: **5.25%** (連合 2025-07-03 最終発表;
1991 年以来 34 年ぶり高水準、ベア 3.56%) — v1.9.0 では "2024
春闘以降の移行期" とのみ言及、最終数値欠落。Source:
https://www.jil.go.jp/kokunai/blt/backnumber/2025/10/shuntou_01.html

🔴 **2026 春闘 第 3 回集計**: 全体 **5.09%** / 300 人未満中小 5.00%
(連合 2026-04-03 発表; 前年同時点比 -0.33 pp だが 3 年連続で 5% 超)。
第 1 回は 5.26%、第 2 回 5.12%。Source:
https://www.jil.go.jp/kokunai/topics/mm/20260327a.html,
https://www.jiji.com/jc/article?k=2026040300929

🔴 **10Y JGB nominal yield**: ~1.5% (2026-Q1 snapshot in v1.9.0) →
**~2.41-2.45%** (2026-04 mid; 28 年ぶり高水準、2025-12-19 利上げ +
Takaichi 政権下財政拡張観測 + 2026-01 展望 上方修正が複合要因)。
10Y 実質利回り は Block 4 real-rate framework の入力として要再測定。
Source: https://www.bloomberg.com/jp/markets/rates-bonds/government-bonds/japan,
https://jp.tradingeconomics.com/japan/government-bond-yield

🔴 **日銀審議委員人事**: **野口旭** (最後のリフレ派) 任期満了
2026-03-31 → 後任 **浅田統一郎** (中央大学名誉教授) 2026-04-01 就任。
中川順子 審議委員は 2026-06-29 任期満了予定 (後任未発表)。Source:
https://www.boj.or.jp/about/organization/policyboard/pb260401a.htm,
https://business.nikkei.com/atcl/seminar/19/00122/00270/

🔴 **実質賃金 プラス転化定着**: 2026-01 **+1.4% YoY**、2026-02
**+1.9% YoY** (厚労省 毎月勤労統計; "持家の帰属家賃を除く総合" CPI
で実質化)。2025-12 以来のプラス継続 → BOJ 「賃金と物価の好循環」
narrative に sustained 証拠。Source:
https://www.dlri.co.jp/report/macro/581131.html,
https://www.dlri.co.jp/report/macro/593034.html

⚠️ **BOJ 金融政策決定会合 2026-01-23 + 2026-03-19**: 両会合とも
**0.75% 据え置き** (8 対 1、**高田創** 審議委員が 1.00% への利上げ
提案も否決)。v1.9.0 draft で野村 森田 メインシナリオ「2026-06
+25 bp → 1.00%」は現時点で pending (未実施)。Source:
https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260123a.pdf,
https://www.cnbc.com/2026/03/19/bank-of-japan-keeps-rates-steady.html

⚠️ **植田総裁 2026-04-13 演説 トーン変化**: イスラエル・イラン戦況を
念頭に "developments in the Middle East remain uncertain" と
明示。4/28 会合の利上げ確率 (OIS 市場織り込み) は 4/11 時点
60% → 4/14 朝 45% → 演説後 **33%** へ急低下。ターミナル 1.50%
シナリオ継続するも 2026-Q2 hike は geopolitical risk-contingent。
Source: https://www.bloomberg.com/news/articles/2026-04-13/ueda-s-speech-shows-rising-caution

⚠️ **BOJ 長期国債買入れ減額ペース**: 予定通り 2026-04-06 期以降
毎四半期 4,000 億円 → **2,000 億円** 減額に緩和 (2025-06 決定)。
2026-06 会合で中間評価予定。Source:
https://www.boj.or.jp/mopo/mpmdeci/mpr_2025/k250617b.pdf

⚠️ **JGBi 第 31 回 (新発) は 2026-Q1 時点未発行**: 2026 年 1-3 月 は
**第 22-30 回** のみ買入対象 (第 21 回は 1 月のみ)。月 1 回 200 億円
程度の買入オペ継続。新規 10Y JGBi (第 31 回) の入札タイミングは
2026-Q2 以降の財務省 プレスリリース待ち。`jgbi-auction-history.yml`
更新は次期 auction 実施後。Source:
https://www.mof.go.jp/jgbs/topics/press_release/20251225-01.htm

**Verified unchanged**:
- 2013-01-22 2% 物価安定目標 (日銀・政府共同声明)
- JILPT 均衡失業率 ~2.80% (2026-02 latest; 次回更新 2026-Q2 末見込み)
- 完全失業率 2.6% (2026-02 季調; 2026-03 は未発表)
- 植田総裁任期 2028-04-08、氷見野・内田副総裁任期 2028-03-19
- BOJ 政策金利 3 層構造 (誘導目標 0.75% / IOER 0.75% / 基準貸付
  1.00%); STRDCLUCON ~2-3 bp 下の乖離メカニズム
- r\* range -1.0% to +0.5%, 中点 ~-0.25% (WP24-J-09 + rev26j05;
  新しい公式 BOJ 推計 paper 未発表)
- BOJ 日銀レビュー rev26j05 の "複数指標による総合評価" 枠組み
  (2026-03-27 発表; single r\* への依存回避)
- 野村 森田京平 ターミナル 1.50% シナリオ (3 hikes via 2026-06 /
  12 / 2027-06; main 60% weight) — 4/28 hike 確率が市場で低下も
  シナリオ自体は撤回されていない

**New primary-source URLs**:
- BOJ 2026-01 展望リポート 基本的見解:
  https://www.boj.or.jp/mopo/outlook/gor2601a.pdf
- BOJ 2026-01-23 金融市場調節方針 (据え置き決議):
  https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260123a.pdf
- BOJ 2026-01-26 植田総裁記者会見:
  https://www.boj.or.jp/about/press/kaiken_2026/kk260126a.pdf
- BOJ rev26j05 自然利子率と金融緩和度合いの評価 (2026-03-27):
  https://www.boj.or.jp/research/wps_rev/rev_2026/rev26j05.htm
- BOJ 審議委員浅田統一郎発令 (2026-04-01):
  https://www.boj.or.jp/about/organization/policyboard/pb260401a.htm
- 連合 2026 春闘 第 1 回集計 (2026-03-23、JILPT 整理):
  https://www.jil.go.jp/kokunai/topics/mm/20260327a.html
- 連合 2026 春闘 第 3 回集計 (時事通信 2026-04-03):
  https://www.jiji.com/jc/article?k=2026040300929&g=eco
- JILPT 2025 春闘最終集計 (5.25%、BLT 2025-10):
  https://www.jil.go.jp/kokunai/blt/backnumber/2025/10/shuntou_01.html
- 財務省 物価連動債 2026 年 1-3 月 発行計画 (2025-12-25):
  https://www.mof.go.jp/jgbs/topics/press_release/20251225-01.htm
- BOJ 長期国債買入れ減額計画 (2025-06-17 決定):
  https://www.boj.or.jp/mopo/mpmdeci/mpr_2025/k250617b.pdf

See `../research/grounding-v1.11.0.md` (to be written in next commit)
for consolidated cross-country audit.

**Next recalibration**: July 2026 (BOJ 2026-04-28 展望レポート 公表後、
2026 春闘 連合 最終集計 確定後; v1.12.0 target)。

---

---

## Inflation Target / 物価安定の目標

- **Official target**: **2% CPI YoY** (headline 全国CPI, set 2013-01)
- **Tolerance band**: **none published** — BOJ uses qualitative
  "概ね整合的な水準" ("roughly consistent level") rather than a
  numerical band. Academic proposals (Canada-style 1-3%) exist but
  not adopted.
- **Current outlook**: Core CPI (除生鮮食品) FY2026 見通し中央値 +1.9%,
  FY2027 +2.0% (**2026-01 展望レポート**, 政策委員中央値; FY2026 は
  2025-10 時点 +1.8% から 0.1 pp 上方修正)。FY2025 は +2.7%
  (据え置き) と輸入インフレ・米価押上げ等でオーバーシュート状態。
- **FY outlook (BOJ 展望レポート 2026-01, 政策委員中央値)**:
  - Core CPI (除生鮮食品): FY2025 **+2.7%** / FY2026 **+1.9%** / FY2027 **+2.0%**
  - 実質 GDP: FY2025 **+0.9%** / FY2026 **+1.0%** / FY2027 +1.0%
    (FY2025/2026 ともに +0.2-0.3 pp 上方修正)
  - Projection horizon 末尾: 「物価安定の目標と概ね整合的な水準」
  - Source: https://www.boj.or.jp/mopo/outlook/gor2601a.pdf
- **Signal (using BOJ 2% anchor)**:
  - `> 2.2%` Above target
  - `1.8% ≤ x ≤ 2.2%` At target (this IS BOJ's goal state)
  - `< 1.8%` Below target (historically Japan's default regime)

### Important framing caveat

Japan's **decades-long deflation legacy** means the 2% target is a
**policy goal** rather than an ambient equilibrium. A reading of 1.9%
should be treated as **success** (not "below target"), not as
disinflationary concern — context matters. The regime call for Japan
should give more weight to **direction of change** (rate-of-change) than
level-vs-target gap.

---

## Labor Market Tightness (NAIRU / 均衡失業率)

- **NAIRU proxy (JILPT 均衡失業率)**: **~2.80%** (2026-02 latest;
  2025Q4 = 2.78%); 需要不足失業率 -0.17% で労働需給は**充足状態**
- **Current unemployment** (労働力調査 2026-02): **2.6%** (季調;
  2026-01 は 2.7%)
- **Implication**: unemployment は均衡失業率を **~0.2 pp 下回る** →
  労働需給充足から**軽度タイト**。post-2015 の構造的タイト化は継続
  しているが、prior draft の "1 pp 下回る Tight" は過大評価。
- **Bands (JILPT 均衡失業率 ± 0.3 pp, 絶対値が低い JP 特性を反映)**:
  - `unemp < 2.5%` → Tight (overheating 兆候)
  - `2.5% ≤ unemp ≤ 3.1%` → Balanced (現在 2.6% はこのバンド)
  - `unemp > 3.1%` → Slack
- **春闘 wage signal (2025-2026 actuals)**:
  - **2025 春闘 連合最終集計 (2025-07)**: **5.25%** (ベア 3.56% + 定昇)、
    1991 年以来 34 年ぶり水準、2 年連続 5% 超
  - **2026 春闘 連合第 3 回集計 (2026-04-03)**: 全体 **5.09%** (ベア
    分離不詳、4/29 段階の概数) / 中小 (300 人未満) 5.00% — 前年同時点
    比 -0.33 pp だが **3 年連続 5% 超** を維持
  - 実質賃金 (毎月勤労統計): 2026-01 +1.4% YoY、2026-02 +1.9% YoY —
    2 ヶ月連続プラス → BOJ 「賃金と物価の好循環」 narrative に
    sustained empirical 裏付け
  - 2024 春闘 以降の構造的賃金上昇は定着 — regime call で "wage-less
    tightness" 前提は 2026 年以降無効

---

## Policy Rate Neutrality

### BOJ 政策金利の正体 — 3 層構造

日銀の政策金利は **単一数字ではなく、3 層の金利体系**として運用される。
2024-03 YCC 終了後、2025-12-19 利上げ後の現行構成 (2026-Q2 据え置き継続)：

| 階層 | 名称 | 利率 | 役割 |
|------|------|------|------|
| **目標** | 無担保コールレート(オーバーナイト物) の誘導目標 | **0.75% 程度** | BOJ 決定会合の文字決議。「X% 程度で推移するよう促す」の表現 |
| **Floor-ish** | 補完当座預金制度 適用利率 (IOER 相当) | **0.75%** | 超過準備への付利金利。2024-03 以降は階層構造廃止、単一利率を一律適用。従来は floor だが、非銀行の裁定によりやや穴がある |
| **Ceiling** | 補完貸付制度 (基準貸付利率 / 旧「公定歩合」) | **1.00%** | 誘導目標 + 25 bp。BOJ が民間銀行に当日貸付ける際の上限利率として corridor ceiling 機能 |

**決議の原文用語** (2025-12-19 k251219a.pdf): 「無担保コールレート
(オーバーナイト物) を、0.75% 程度で推移するよう促す」— この「程度」
(approximately) に ±数 bp 許容が含意される。

### 実績市場利率 vs 目標の乖離

我々の投資 toolkit は `japan-macro` skill の `rates` 群組で
**BOJ FM01 / STRDCLUCON**（無担保コールO/N物レート）を取得する：

```
2026-04-15 実績 (STRDCLUCON): 0.727%
           ↕  ~2-3 bp 差
2026-Q1/Q2 目標:            0.75% 程度 (2026-01-23, 2026-03-19 据え置き)
```

**なぜ 2-3 bp 下か？**: 投資信託委託会社や一部のノンバンクは BOJ 当座
預金を持てないため IOER 0.75% を直接受け取れず、コール市場で僅かに
下の利率で貸し出す（ゼロより得ならば貸す）。これが市場利率を
IOER 下に 2-5 bp 押し下げる。Fed funds rate vs IOER の 2018-2019
年の乖離 (3-15 bp) よりは狭い。

**実務上の扱い**: regime call で「政策利率水準」を言及する際、
**STRDCLUCON の実績値は目標の ~2-3 bp 下である近似**として使う。
正確な目標は最新 金融政策決定会合 声明 (https://www.boj.or.jp/mopo/mpmdeci/) を参照。

### 歷史軌跡 (post-YCC 正常化パス)

| 会合 | 誘導目標 | IOER | 基準貸付 | 備考 |
|------|----------|------|----------|------|
| 2024-03-19 | 0.00% 程度 (0-0.1%) | 0.10% | 0.30% | YCC 終了・マイナス金利解除 |
| 2024-07-31 | 0.25% 程度 | 0.25% | 0.50% | 初回利上げ |
| 2025-01-24 | 0.50% 程度 | 0.50% | 0.75% | 2 回目 |
| **2025-12-19** | **0.75% 程度** | **0.75%** | **1.00%** | **3 回目・30 年ぶり水準** |
| 2026-01-23 | 0.75% 程度 (据え置き) | 0.75% | 1.00% | 8-1 票決、高田委員が 1.0% 提案も否決。展望上方修正 |
| 2026-03-19 | 0.75% 程度 (据え置き) | 0.75% | 1.00% | 8-1 票決 (高田委員 1.0% 提案)、中東情勢を上振れリスクに明記 |
| 2026-04-28 | — pending — | — | — | 展望レポート 公表予定会合; 植田 4/13 演説で中東リスク強調、市場 hike 確率 33% |

### 2025-12-19 決議の他の重要内容 + 2026-04 更新

- **長期国債買入れ減額ペース** (2025-06-17 決定 + 2025-12 確認):
  - 2026年1-3月: 毎四半期 4,000億円程度ずつ減額
  - **2026年4月以降**: 毎四半期 **2,000億円** 程度ずつ減額 (ペース緩和)
  - 2026年6月会合: 中間評価予定
  - 2027年1-3月: 2 兆円程度に到達予定
  - Source: https://www.boj.or.jp/mopo/mpmdeci/mpr_2025/k250617b.pdf

### 2026-01 / 2026-03 会合のポイント (v1.11.0 追加)

- **1/23 会合 (展望レポート更新)**: 政策金利 0.75% 据え置き (8-1)。
  **展望 上方修正**: FY2025/FY2026 実質 GDP 両方 +0.2-0.3 pp、
  FY2026 核 CPI +0.1 pp (1.8% → 1.9%)。「基調的インフレ率は見通し
  後半に 2% 程度で推移」の文言継続。
- **3/19 会合**: 0.75% 据え置き (8-1、高田委員 1.0% 提案)。中東情勢
  (イスラエル・イラン) を物価の **上振れリスク** に明記。原油価格
  上昇圧力への注視。
- **4/28 会合 (予定)**: 展望レポート 更新会合。**植田総裁 2026-04-13
  演説** で "developments in the Middle East remain uncertain" と
  明示、市場 hike 織込確率 60% → **33%** へ低下。野村 森田メイン
  シナリオの 6 月利上げタイミングが前倒しされる可能性は低下。

### Neutral rate 推定

- **Nominal neutral rate estimate**: ~**1.0-1.75%** (市場コンセンサス
  + 野村メインシナリオターミナル 1.50% を包含). BOJ themselves do not
  publish a neutral rate; both because r\* 不透明性 is a deliberate
  policy choice (like BOK), and because r\* estimates diverge widely
  in Japan's unique regime.
- **Real r\* (BOJ Working Paper 24-J-09 2024-08 + 日銀レビュー rev26j05 2026-03)**:
  - Range estimates: **-1.0% to +0.5%** (複数モデルの幅; 原典が「相当な
    ばらつきがある」と明記)
  - Range 中点: ~**-0.25%** (単一推計値ではなく派生; "mean" 一語は
    原典表現でないため避ける)
  - 長期トレンド: 1980 年代から約 **4 pp 低下** (lab18j02 分解: 技術進歩
    ~2 pp + 金融仲介機能 ~1 pp + 人口動態)
  - 日本の r\* は G7 最低水準; 長寿化・生産性鈍化・銀行危機傷跡が主因
  - 2026-03 rev26j05 は WP24-J-09 を GDP 基準改定後に再推計した BOJ 最新公式見解
- **Nominal hiking path (野村 森田京平 2026-01-26 メインシナリオ 60%)**:
  - 2026-06 +25 bp → 1.00%、2026-12 +25 bp → 1.25%、2027-06 +25 bp → 1.50%
  - **ターミナルレート: 1.50%**
  - リスクシナリオ (円安圧力継続, 40%): 2026-04/10, 2027-04/10
    各 +25 bp → ターミナル **1.75%**

---

## Real Rate Decomposition

**v1.10.0 status: Multi-source framework active (C + D + E).** Free-tier
primary-source paths replicate BOJ's own composite expected-inflation
methodology (market + survey + auction). Data layer lives in
`japan-macro` skill; full source-by-source documentation at
`investing-toolkit/skills/japan-macro/references/indicators-japan-real-rates.md`.

### Data paths

| Path | Source | Cadence | Preset | Authority tier |
|------|--------|---------|--------|----------------|
| C | MoF JGBi 落札利回り (`jgbi-auction-history.yml`) | ~quarterly (~4/yr) | `real-10y-auction` | ⭐⭐⭐⭐ primary anchor, 単利 |
| D | ECB Data Portal `M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA` | monthly | `real-10y-monthly` | ⭐⭐⭐ primary, **ex-post** (NOT market BEI) |
| E | BOJ Tankan 企業物価見通し (CO DB, `TK99F0000204/205/206HCQ00000`) | quarterly | `inflation-tankan-1y/3y/5y` | ⭐⭐⭐⭐ BOJ Outlook Report component |

**Sources deliberately NOT used**:
- **JSDA 日次 JGBi CSV** — yield fields masked `999.999` (JSDA 公開は 単価 only).
- **JBTS BEI** — 利用規約 prohibits 複製・送信・再配信.

### Signal thresholds (Block 4)

**`real-10y-monthly` (ECB ex-post)** — applies to monthly period-average:

| Level | Threshold | Reading |
|-------|-----------|---------|
| Accommodative | `< 0%` | Real yield below neutral; policy supportive |
| Neutral | `0% to 1%` | Near r\* midpoint of BOJ estimated range |
| Restrictive | `≥ 1%` | Real yield above BOJ r\* upper range (+0.5%) plus ~0.5 pp ex-post vs. ex-ante wedge |

Calibration rationale: BOJ WP24-J-09 2024-08 / rev26j05 2026-03 give
r\* range **-1.0% to +0.5%** with midpoint ≈ **-0.25%**. The ex-post
ECB series runs ~0.5-1.0 pp different from ex-ante market real yield
in most regimes, so thresholds are widened vs. ex-ante framework
(pre-2024 drafts had proposed `< -0.5% / -0.5% to 0.5% / > 0.5%` for
ex-ante context).

**Explicit caveat**: ECB series is **ex-post** (nominal minus realised
CPI). It is not market-implied expected-inflation; the "real yield"
label matches the ECB title but the construction differs from US TIPS
market-implied real yield. Triangulate against Path E (Tankan ex-ante
corporate expectations) when the ex-post signal drifts during
inflation-surprise episodes.

**`real-10y-auction` (MoF JGBi 単利)** — validation anchor, not a
continuous signal:

- Snapshot refreshed manually per auction (v1.11.0 automates via MoF
  scraper).
- Read alongside ECB monthly series: when MoF auction spot and ECB
  monthly diverge by >30 bp, flag data-consistency check.
- 2025-08 cross-section: auction +0.078% ≈ ECB ex-post compression to
  near-zero → consistent post-YCC-exit regime.

**`inflation-tankan-1y` (BOJ Tankan 全企業・全産業平均)**:

| Level | Threshold | Reading |
|-------|-----------|---------|
| Below target | `< 1.5%` | Corporate 1Y expectations below BOJ 2% target -50 bp |
| At target | `1.5% to 2.5%` | Anchored at BOJ target ±50 bp |
| Overshoot | `> 2.5%` | Corporate 1Y expectations above target +50 bp (regime-shift signal) |

**`inflation-tankan-5y`** — long-term anchoring:

| Level | Threshold | Reading |
|-------|-----------|---------|
| De-anchored low | `< 1.5%` | Structural sub-target regime risk |
| Anchored | `1.5% to 2.5%` | BOJ-target-consistent regime |
| De-anchored high | `> 2.5%` | Sustained above-target regime (post-2023 Japan is here) |

### v1.11.0 roadmap

- **MoF 連動係数 daily feed** (official XLS + daily CSV).
- **QuantLib-based JGBi YTM solver** — daily 単価 (from JSDA CSV)
  + 連動係数 + coupon → daily real YTM at Bloomberg-grade ±5 bp accuracy.
- Adds fourth signal `real-10y-daily` to Block 4 thresholds table above.
- Ships as standalone PR with dedicated primary-source grounding audit
  (MoF 応募要領 + 仕組み書 → 単利 / 複利 / 連動係数 semantics fully
  anchored, no fabricated conversion formulas).

---

## Structural Regime Notes

- **Post-deflation transition** (since 2022-2024): Japan is leaving
  the "2% is aspirational" regime into "2% is achieved". This shifts
  the IC mapping:
  - Pre-2022: Japan was almost always **Phase 4 Reflation** (falling
    growth + falling inflation below target)
  - 2024-2026: first sustained **Phase 2 Overheat** (rising both) in
    decades; regime identification should acknowledge this rare shift.
- **BOJ YCC ended 2024-03**: pre-2024 JGB 10Y curve was artificially
  pinned; post-2024 readings more market-driven.
- **Demographic overhang**: aging population + shrinking workforce
  → structurally low r*, low trend growth (~0.5% real). This
  **caps sustainable policy rate ceiling**.
- **JPY regime**: Japan is a creditor nation with massive FX reserves
  + overseas assets (~3x GDP). JPY appreciation in risk-off is a
  regime-cross-check signal.

---

## Asset-Class Tilt Calibration

- **Equity index**: TOPIX (broad, ~2,100 names) preferred for regime
  mapping over Nikkei 225 (price-weighted, 225 names). Sector
  structure more balanced than KOSPI/TAIEX. Tech weight ~15-20%
  (vs TW ~65%).
- **Corporate governance reform**: post-2023 TSE reform driving P/B
  rerating — **structural re-rating can dominate regime signal** for
  JP equities.
- **Fixed income**: JGB curve post-YCC → finally market-priced;
  10Y yield **~2.41-2.45%** (2026-04 mid; 28 年ぶり高水準)。
  2025-12 利上げ + Takaichi 政権下の財政拡張観測 + 2026-01 展望
  上方修正 + BOJ 買入れ減額 の複合要因で Q1 から急上昇。
  Real yield は正領域へ転換可能性 (2026-Q1 時点 ECB ex-post
  ~0% vs 10Y JGB 2.4% 強 → 実質 ~0.5-0.8% の可能性; Block 4
  framework で再測定要)。
- **Commodities**: Japan is major commodity importer — commodity
  strength = terms-of-trade drag. Energy (crude) especially critical
  (not self-sufficient).
- **FX**: JPY weakness drives imported inflation directly (Japan CPI
  reacts ~0.4% per 10% JPY depreciation). JPY direction often a
  regime factor, not just a consequence.

### Sector Tilts (JP-specific adjustments to IC cheatsheet)

| IC Phase | JP-specific Overweight | JP-specific Underweight |
|----------|------------------------|--------------------------|
| Recovery | Financials (banks benefit from positive rates), automakers, tech-value | Utilities, defensive staples |
| Overheat | Trading houses (商社), commodity-linked, shippers | Import-heavy consumer, JGB |
| Stagflation | JPY cash, energy, healthcare | Real estate, consumer discretionary |
| Reflation | JGB, REITs (J-REIT), telecoms | Automakers, export-oriented |

---

## Primary-Source Verification URLs

- 日銀 物価安定の目標: https://www.boj.or.jp/mopo/outline/target.htm
- 日銀 経済・物価情勢の展望: https://www.boj.or.jp/mopo/outlook/
- 日銀 WP 自然利子率 WP24-J-09: https://www.boj.or.jp/research/wps_rev/wps_2024/wp24j09.htm
- JILPT 均衡失業率・需要不足失業率: https://www.jil.go.jp/kokunai/statistics/topics/uv/uv.html
- 労働力調査 (e-Stat): https://www.e-stat.go.jp/stat-search/files?tclass=000001226526

## Sources (citations)

Primary (原典, 日本語):
- BOJ 金融市場調節方針の変更について 2025-12-19 (k251219a.pdf) —
  https://www.boj.or.jp/mopo/mpmdeci/mpr_2025/k251219a.pdf —
  0.75% 程度利上げ + 長期国債買入れ減額計画
- BOJ 補完当座預金制度 基本要領 —
  https://www.boj.or.jp/mopo/measures/term_cond/yoryo37.htm
- BOJ 金融市場局「2024 年度の金融市場調節」概要 2025-06-04 (mor250604b.pdf) —
  https://www.boj.or.jp/research/brp/mor/data/mor250604b.pdf —
  市場調節の運営実績 + 3 層金利構造の解説
- BOJ 物価安定の目標 (2013-01-22 共同声明)
- **BOJ 経済・物価情勢の展望 2026-01-23 (gor2601a.pdf)** —
  https://www.boj.or.jp/mopo/outlook/gor2601a.pdf — FY2026 核 CPI
  1.8% → 1.9% 上方修正、FY2025/FY2026 実質 GDP 両方上方修正
- **BOJ 金融市場調節方針 (2026-01-23 k260123a.pdf)** —
  https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260123a.pdf —
  0.75% 据え置き 8-1 票決
- **BOJ 植田総裁 2026-01-26 記者会見 (kk260126a.pdf)** —
  https://www.boj.or.jp/about/press/kaiken_2026/kk260126a.pdf
- **BOJ 審議委員 浅田統一郎 発令 2026-04-01 (pb260401a.htm)** —
  https://www.boj.or.jp/about/organization/policyboard/pb260401a.htm —
  野口旭 退任後任
- BOJ 経済・物価情勢の展望 2025-10 (展望レポート本文 + ハイライト)
- **BOJ Working Paper WP24-J-09 (2024-08, 杉岡・中野・山本)** — 自然利子率の計測をめぐる近年の動向
- **BOJ 日銀レビュー rev26j05 (2026-03-27, 企画局)** — 自然利子率の動向と金融緩和度合いの評価 (最新 BOJ 公式 r\* 見解)
- **BOJ リサーチラボ lab18j02 (2018-06, 須藤・岡崎・瀧塚)** — わが国の自然利子率の決定要因 (r\* 下降 4pp 分解)
- BOJ WP03-J-05 (2003-10, 小田・村永) — 自然利子率 分析原点
- BOJ 総裁記者会見 (2026-01-23 kk260126a.pdf)
- JILPT UV 分析 (均衡失業率 2026-02 最新)
- **JILPT 2025 春闘 最終集計 (BLT 2025-10)** —
  https://www.jil.go.jp/kokunai/blt/backnumber/2025/10/shuntou_01.html —
  賃上げ率 5.25% (34 年ぶり高水準)
- **JILPT 2026 春闘 第 1 回集計整理 (2026-03-27)** —
  https://www.jil.go.jp/kokunai/topics/mm/20260327a.html —
  3 年連続 5% 超
- **時事通信 2026-04-03 連合第 3 回集計** —
  https://www.jiji.com/jc/article?k=2026040300929&g=eco — 全体 5.09%
- **厚労省 毎月勤労統計 2026-01 / 02** (実質賃金プラス転化確認経由
  第一ライフ資産運用経済研究所 新家)
- **BOJ 長期国債買入れ減額計画 2025-06-17 (k250617b.pdf)** —
  https://www.boj.or.jp/mopo/mpmdeci/mpr_2025/k250617b.pdf —
  2026-04 以降ペース緩和 (4,000 億 → 2,000 億/四半期)
- **財務省 物価連動債 2026-Q1 発行計画 (2025-12-25)** —
  https://www.mof.go.jp/jgbs/topics/press_release/20251225-01.htm —
  第 21-30 回のみ買入対象、新発 第 31 回は Q2 以降
- 総務省統計局 労働力調査
- 日経 参議院 Research Note 2024-12 — 物価安定の目標をめぐる経緯と論点

Secondary (日本語):
- 野村ウェルスタイル 0571 (2026-01-26, 森田京平) — 日銀利上げシナリオ (main ターミナル 1.50%)
- NRI 木内登英 2025-12-16 コラム — 政府のデフレ完全克服と日銀の2％物価安定
- 第一ライフ資産運用経済研究所 熊野英生 0.75% 利上げコラム
- JST 資金運用本部 Research Note 42 (2026-01-29) — 中立金利とタームプレミアム
- 日経 2025-12-19 — 日銀 0.75% 利上げ決定 (30 年ぶり水準)

Removed (unverifiable):
- ~~伊藤忠総研 2024-04 コラム「自然利子率r\*に振り回される日米金融市場」数値引用~~
  (-0.386% / G7 比較 数値が本文に不含; 出典無効)
