# Fixture: TW 立法院質詢答詢 / 縣市長施政演說 (synthetic-representative)

**Source**: synthetic-representative (composed by maintainer for evaluation purposes; modeled on TW 立法院質詢答詢 / 縣市長 施政總質詢答詢 register conventions, ca. 2024)
**Accessed**: 2026-05-05 (composed)
**Capture method**: synthetic representative — not a real artifact
**License**: maintainer-authored, freely usable for plugin evaluation
**Honesty flag**: This is NOT a real fetched artifact. It is a maintainer-composed text built to exhibit lens features cleanly (面子 + 關係 + 陰陽 dialectical framing + 道 / 氣 metaphors + 圈子 in-group). Real-world TW 政治演說 vary; eval results from this fixture are a smoke-test of `lens-frame-zh` application, not a benchmark of real-text deconstruction quality.
**Eval target**: `artifact-deconstruct` must identify Goffman primary frame (議會答詢 / 施政演說), surface 面子 + 臉 invocations with whose-face mapping, identify 自己人/熟人/外人 圈子 boundary, detect 陰陽 dialectical synthesis (vs Anglo binary), name ≥2 ZH conceptual metaphors (道 / 氣 / 緣 / 心 / 圈子 / 根), and explicitly attribute analysis to `lens-frame-zh`.

---

## 縣長施政總質詢　答詢發言

  主席、各位議員先進、現場與螢幕前關心市政的鄉親朋友：

  各位好。首先，要感謝張議員剛才的指教，讓本縣同仁能夠再一次省思——
我們究竟把人民放在哪裡？這個問題，我這個做縣長的，每天起床都在問
自己。

  剛才議員提到地方產業的轉型。本縣這幾年的努力，相信議員都看在
眼裡。我們秉持「兼顧發展與環境」的施政理念，既要產業升級，也要
山林永續；既要招商引資，也要照顧在地小農。這不是兩條並行的路，而
如陰陽相生——根紮得深，枝葉才能長得遠。

  講到「在地」，本縣的施政有一個堅持：自己人的事，沒有外人。從
返鄉青年的創業補助，到老農阿伯的契作保證；從南管社的文化扎根，到
媽祖繞境的物資後勤——每一項，本府同仁都當作自己家的事在辦。我們
這個團隊，從基層走出來，深深知道地方的「氣」，是怎麼養起來的。

  張議員方才提到的那位陳先生，我們已經請社會處的同仁親自登門
拜訪。陳先生的處境，本縣同仁都很心疼，也都記在心裡。古人說「民為
邦本，本固邦寧」，這句話，是本縣團隊每天提醒自己的話。

  我也要藉這個機會，向中央主管機關致上最深的敬意。這幾年中央和
地方的合作，雖偶有不同意見，但都是為了把事情辦好。給彼此留個
空間，給人民一個交代——這是政治人物的本分，也是這份工作的「道」。

  最後，請容我向議員、向鄉親朋友，鄭重承諾：本府團隊會繼續用心、
用力，把每一分資源，都用在最需要的地方。謝謝各位。

  （鞠躬，掌聲——）

---

## Annotations for evaluator

The fixture exhibits canonical TW 縣市長 議會答詢 / 施政演說 frame architecture: 面子/臉 dual-face management, 自己人/外人 圈子 framing, 陰陽 dialectical metaphor, and 道/氣/根 ZH conceptual metaphors. Evaluator should attribute analysis explicitly to `lens-frame-zh` and identify register variant as zh-TW.

### lens-frame-zh: Goffman frame baseline (ZH adjusted)

- **Primary framework**: 議會答詢 / 施政演說 — political-accountability frame in TW representative-democratic register; assumes 行政—立法 監督關係 + 公務員倫理 + 為民服務 triad
- **Keying**: opens with 「主席、各位議員先進、鄉親朋友」 — formal-respectful keying with 先進 (尊長 register); shifts to 「我這個做縣長的」 — humility-keying signaling 平易近人 register; closes with 「鞠躬」 physical 禮儀
- **Fabrication detected?**: borderline — surface frame "我們同仁都當作自己家的事在辦" / "每天起床都在問自己" performs 同理 (empathy-frame); actual frame may be standard 公務員 routine. Anglo Goffman would call this fabrication; ZH register treats it as 套話 (stock-phrase) deployment that both sides understand as performative
- **Frame break**: not detected — speaker maintains frame throughout; the 鞠躬 closes the frame ritually

### lens-frame-zh: 面子/臉 face-frame analysis

| Term | Surface signal | Whose face | Ledger move |
|---|---|---|---|
| **面子** (status) | 「感謝張議員剛才的指教」「議員都看在眼裡」「向中央主管機關致上最深的敬意」「給彼此留個空間」 | (1) 議員's face given via 指教 framing; (2) 中央主管機關's face given via 敬意; (3) "彼此面子" via 留個空間 | **給面子** (giving face) — building public-credit ledger; future 人情 reciprocity expected |
| **臉** (integrity) | 「民為邦本，本固邦寧」「政治人物的本分」「鄭重承諾」「用心、用力」 | speaker's own 臉 (moral-character credit) | **臉-staking** — speaker stakes moral integrity on follow-through; if broken, structural face-loss not just awkwardness |

What Goffman / Brown-Levinson would miss: the **multi-year reciprocity ledger** (Hwang 1987) — 給張議員面子 today builds credit for future legislative cooperation; staking 臉 on 「民為邦本」 invocation creates community-wide moral-judgment risk if broken.

### lens-frame-zh: 關係/圈子 in-group frame

- **自己人 framing**: 「自己人的事，沒有外人」「本府同仁都當作自己家的事」「我們這個團隊，從基層走出來」 — explicit 自己人 in-group construction (情感性 ties; need-rule applies)
- **熟人 framing**: 張議員 + 中央主管機關 = 混合性 ties (renqing-rule); "雖偶有不同意見，但都是為了把事情辦好" softens 熟人 conflict via 人情 buffer
- **外人 framing**: NOT explicitly invoked, but implicit (anyone outside 本縣團隊 + 鄉親 + 中央 triangle); 工具性 ties not in scope
- **圈子 nesting (regional)**: 縣團隊 (innermost) → 鄉親朋友 / 在地小農 / 返鄉青年 (中層) → 中央主管機關 (relational) → implicit 外人 (out-of-frame). Note: TW 「我們」 may silently exclude PRC-readers / 外籍人士 — register-sensitive.
- **Reciprocity rule invoked**: 人情法則 (renqing-rule) at multiple points — 「指教」/「致敬」/「留空間」 are 人情 ledger moves

### lens-frame-zh: 陰陽 dialectical metaphor check

- **Binary-vs-complementary register**: **complementary** (陰陽 register, NOT Anglo binary)
- **Dyads in play**:
  - 「兼顧發展與環境」「既要產業升級，也要山林永續」「既要招商引資，也要照顧在地小農」 — explicit 既/也 dialectical complementarity
  - 「不是兩條並行的路，而如陰陽相生——根紮得深，枝葉才能長得遠」 — explicit 陰陽 invocation + 根/枝葉 complementary metaphor
- **If Lakoff binary applied naively**: would mis-flag 「兼顧 A 與 B」 as Anglo equivocation / fence-sitting. In TW political register, this is the position — Peng & Nisbett 1999 dialectical-thinking style. Anglo "must-choose" reading projects non-contradiction logic that doesn't apply.

### lens-frame-zh: ZH conceptual metaphors at work

| Metaphor | Surface signal | Anglo gap |
|---|---|---|
| **道 (dao)** | 「政治人物的本分，也是這份工作的『道』」 | Anglo "way / role" loses normative-cosmic-order content; 道 carries ought-from-is + lifetime-practice |
| **氣 (qi)** | 「地方的『氣』，是怎麼養起來的」 | No direct Anglo equivalent; "atmosphere / spirit" misses agentive-vital-force |
| **根 (gen)** | 「根紮得深，枝葉才能長得遠」 | Anglo "root" is neutral; 根 carries 在地 belonging + legitimacy weight |
| **心 (xin)** | 「同仁都很心疼」「記在心裡」「用心、用力」 | Anglo distinguishes mind/heart; 心 fuses cognition + emotion |
| **圈子 (quanzi)** | 「自己人」「外人」 explicit binary | Anglo "network" lacks tightness/boundary; "clique" pejorative-only |

### Synthesis (1-line)

The text positions the audience as **自己人 inside a 縣團隊 + 鄉親 圈子 anchored by speaker's 臉 (moral-integrity) credit**, uses **陰陽 complementary structure** (「兼顧發展與環境」「根/枝葉」) to make **growth-and-conservation-as-unified** feel natural, and grounds in **道 / 氣 / 根 / 心 metaphors**. The unstated alternative — Anglo binary trade-off framing — is rhetorically excluded by the dialectical register itself.

### Ethical position

🟡 Gray zone — register-appropriate by ZH standards (套話 + 面子-giving + 臉-staking are canonical political-speech moves), but 「我們同仁都當作自己家的事在辦」 is performative 同理-frame deployment that may not match operational reality. Anglo Goffman-only pass would mis-flag "fabrication"; that would over-pathologize register-appropriate ZH political communication. The ⚠️ risk is the 套話 deployment becoming a frame-trap that pre-empts dissent.

### Expected lessons

- 面子 (status) ≠ 臉 (moral integrity) — Hu 1944 distinction; different repair mechanics
- 自己人/熟人/外人 is 3-tier (Hwang 1987 tie-typology), NOT Anglo binary in-group/out-group
- 「兼顧 A 與 B」 is 陰陽 dialectical synthesis, NOT Anglo equivocation
- 道 / 氣 / 根 / 心 carry content that Anglo glosses lose — leave romanized + brief gloss
- 圈子 (TW 我們) may silently exclude PRC-readers / 外籍 — register-sensitive
- Applying `lens-frame-anglo.md` (Goffman/Lakoff alone) would systematically misread all of the above
