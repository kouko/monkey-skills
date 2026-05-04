# Lens: Genre Analysis (Japanese register — 甲田/木下 academic + 拝啓-formula business letter)

> **Sources**:
> - John M. Swales, *Genre Analysis: English in Academic and Research Settings* (Cambridge University Press, 1990). 260 pages. CARS (Create A Research Space) move-step methodology — used here as **methodological scaffolding** only; the canonical move sets below are JP-specific, not Swales's English-academic moves.
> - Vijay K. Bhatia, *Analysing Genre: Language Use in Professional Settings* (Longman, 1993). 246 pages. Move-step analysis methodology extended to professional genres — again used as scaffolding; the JP business-letter formula below is the JP-specific canonical genre, not Bhatia's 7-move sales letter.
> - John Hinds, "Reader versus Writer Responsibility: A New Typology" — in U. Connor & R. B. Kaplan, eds., *Writing Across Languages: Analysis of L2 Text* (Addison-Wesley, 1987), pp. 141-152. Source for the reader-responsibility claim that JP genre moves can be implicit and still recognized.
> - 甲田直美 (Kōda Naomi), 『文章を科学する』 (ひつじ書房) and related Japanese academic-writing handbooks anchoring 序論-本論-結論 + the sub-move conventions used in modern 大学 アカデミック・ライティング instruction. (Specific edition / pages: see Phase A grounding-v0.2.0.md.)
> - 木下是雄 (Kinoshita Koreo), 『理科系の作文技術』 中公新書 624 (中央公論新社, 1981). Canonical Japanese reference for technical / scientific writing; argues against literary 起承転結 in academic register, in favor of 序論→本論→結論 with explicit thesis-up-front. Co-anchors §"Part 1" below alongside 甲田.
> - JP business-letter handbooks (e.g. NHK 放送文化研究所 / 文化庁 文化審議会 国語分科会 reports on 公用文 + commercial 慣用 references) for the 拝啓 / 時候の挨拶 / 主文 / 末文 / 敬具 formula. (Specific handbook citations: see grounding-v0.2.0.md.)

> **Synthesis note**: This file uses Swales's CARS scaffolding (1990) and Bhatia's move-step methodology (1993) as a **method**, but the **canonical move sets are different**. Anglo CARS + sales-letter 7-move do not capture JP academic 序論-本論-結論 nor JP business 拝啓-formula. Per [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md), this variant grounds in 甲田 / 木下 / Hinds and treats Swales/Bhatia as foreign methodologists whose **method** transfers but whose **content** does not.

> **Cultural-register statement**: This variant grounds in **Japanese** academic, business-correspondence, and modern email registers. Compared to the Anglo variant: JP genres are **more formula-locked**, especially business letters — `拝啓 / 時候の挨拶` openings are non-negotiable, and their absence is itself a strong genre signal. Per Hinds (1987), JP is **reader-responsible**: moves can be implicit and still functionally present, so a missing-move finding requires more care than in the Anglo variant.

Genre analysis recovers the **conventional move structure** of any
recognizable Japanese document type — and identifies when moves are
**missing**, **weak**, or **deliberately abbreviated** (especially in
modern メール).

## When to apply this lens

- Japanese 学術論文 / academic papers (especially 序論 + 抄録)
- Japanese ビジネス文書 / formal business letters (`拝啓`-formula register)
- Japanese ビジネスメール (modern abbreviated register)
- Japanese 大学 syllabus / シラバス
- Japanese 起業家 pitch deck / 事業計画書
- Japanese 報告書 / 議事録 / 提案書 (internal business genres)
- Japanese op-ed / コラム — but cross-reference [`lens-rhetoric-ja.md`](lens-rhetoric-ja.md) for 起承転結

## When NOT to apply

- JP poetry / 短歌 / 俳句 — formal-form analysis, not genre analysis
- JP literary fiction — narrative structure, not move structure
- Documents that have been translated INTO Japanese from English source — register may be English-origin even though surface is JP; flag and apply -anglo
- Mixed JP/EN code-switched documents where the JP portion is ornamental — apply -anglo to the EN body

## Cultural register up front: formula vs Anglo flexibility

JP genres are **systematically more formula-locked** than Anglo
equivalents:

| Phenomenon | Anglo | Japanese |
|---|---|---|
| Business-letter opening | "Dear X," (1 line) | `拝啓` + `時候の挨拶` + `安否の挨拶` (3-4 lines, prescribed wording) |
| Missing the opening formula | Mildly informal | **Strong negative signal** — reads as rude or as deliberate code-switch |
| Move implicitness | Generally explicit (writer-responsible per Hinds 1987) | Often implicit (reader-responsible) — `お世話になっております` carries entire 時候+安否 functions |
| Variant register | Wide latitude | Narrow latitude — the formula IS the genre |

Take this seriously: in JP business correspondence, the formula
elements are **load-bearing**, not decoration. Their absence signals
something specific (haste / informality / deliberate transgression).

## Part 1: JP Academic — 序論-本論-結論 + IMRAD adaptation

Modern Japanese academic writing — per 甲田直美 textbooks and 木下是雄 『理科系の作文技術』 (1981) — uses **序論-本論-結論** (introduction-body-conclusion), **not** 起承転結. This is a Meiji-era + post-WWII Western-influenced convention; literary / op-ed JP still uses 起承転結 (see Part 4).

### Canonical 序論 (introduction) sub-moves

Per 甲田 / standard JP アカデミック・ライティング instruction, the 序論 typically contains:

| Sub-move | JP convention | Function |
|---|---|---|
| テーマ提示 | Topic presentation | "本稿では X について論じる" |
| 背景・先行研究 | Background + literature | Citation of relevant 先行研究 |
| 問題提起 / リサーチクエスチョン | Problem statement | "従来 X は Y とされてきたが、Z については未解明である" |
| 本稿の目的 | Thesis statement | "本稿の目的は ... を明らかにすることである" |
| 構成の予告 | Roadmap | "第2章では ..., 第3章では ..." (more variable; sometimes omitted) |

Compare to Swales CARS Move 1 (territory) + Move 2 (niche) + Move 3 (occupy): the JP convention parallels CARS but is more **explicit** about thesis statement (per 木下 1981's "結論を先に書け" doctrine for 理科系 writing).

### IMRAD adaptation

JP scientific papers (理工系 / 医学系) commonly follow IMRAD (Introduction / Methods / Results / Discussion). 木下 1981 advocates this strongly. Humanities / social-science 論文 vary — many follow 序論-本論-結論 with sub-divided 本論 sections.

### Canonical 結論 (conclusion) sub-moves

| Sub-move | Function |
|---|---|
| 本稿のまとめ | Summary of findings |
| 本研究の意義 | Significance / contribution |
| 限界 / 今後の課題 | Limitations + future work (often softer than Anglo "Limitations" — per 婉曲表現 / Hinds reader-responsibility) |

## Part 2: JP Business Letter — 拝啓-formula moves

The canonical JP business letter (商用文 / ビジネス文書) follows a
prescribed 7-move formula. **All 7 are conventionally required**;
their absence is a strong genre signal.

| # | Move | JP convention | What goes here | Required? |
|---|---|---|---|---|
| 1 | 頭語 (とうご) | `拝啓` (standard) / `謹啓` (more formal) / `前略` (omits 時候の挨拶) | Opening greeting word | **Yes** — the genre marker |
| 2 | 時候の挨拶 (じこうのあいさつ) | Seasonal phrase, e.g. 「新緑の候」「初夏の候」「師走の候」 | Builds 場 (relational scene) before business | **Yes** in 拝啓-register; **omitted** with 前略 |
| 3 | 安否の挨拶 (あんぴのあいさつ) | Wellness inquiry, e.g. 「貴社ますますご清栄のこととお慶び申し上げます」 | Relational opening; acknowledges recipient's status | Often (formal letters); abbreviated in routine correspondence |
| 4 | 主文 (しゅぶん) | Body, opens with `さて、` or `この度は、` | The actual ask / message | **Yes** — the substantive content |
| 5 | 末文 (まつぶん) | Closing relational, e.g. 「今後ともよろしくお願い申し上げます」 「ご検討のほどよろしくお願いいたします」 | Well-wishing + transition to closing | **Yes** |
| 6 | 結語 (けつご) | `敬具` / `謹白` / `草々` (matching #1 頭語) | Closing word; **must match 頭語**: 拝啓→敬具, 謹啓→謹白, 前略→草々 | **Yes** — formula match required |
| 7 | 後付 (あとづけ) | Date / sender / recipient block, formatted right-aligned | Post-block administrative info | **Yes** |

### Pairing rule (load-bearing)

Mismatching 頭語 / 結語 (e.g. opening with `拝啓` but closing with
`草々`) is not just informal — it is a **failed genre move** signaling
the writer is unfamiliar with business-letter conventions. Native JP
readers parse this immediately.

## Part 3: JP メール (modern email) — abbreviated genre

Modern JP business email **collapses** the letter formula but does
**not** delete it. The moves remain — they simply shrink to
formulaic substitutes:

| Letter formula move | Email substitute | Function preserved? |
|---|---|---|
| 頭語 (`拝啓`) | `お世話になっております` / `お疲れ様です` (in-house) | Yes — opening genre marker |
| 時候の挨拶 | (usually absent, OR abbreviated to 「いつも」) | Mostly omitted |
| 安否の挨拶 | Carried inside `いつもお世話になっております` | Yes — folded into headline |
| 主文 | `さて、` may appear; or direct `〜の件でご連絡いたします` | Yes |
| 末文 | `よろしくお願いいたします` (almost universal) | Yes |
| 結語 (`敬具`) | (usually absent) — `よろしくお願いいたします` carries this function | Folded |
| 後付 | Email signature block | Yes |

### Implication for analysis

When analyzing a JP email, do **not** mark moves missing just because
the surface formula is absent. Read for **functional substitutes**:

- Email opening with `お世話になっております` → 頭語 + 安否 both present
- Email opening with `お疲れ様です` only → in-house register signal; no 安否 move (intentional; in-house people don't need wellness inquiry)
- Email with **no** opening greeting → either highly informal (peer-internal) or transgressive (genre violation)

## Part 4: 起承転結 in non-academic JP genres

**Important register split**: 起承転結 (kishōtenketsu) is alive and
canonical in JP **literary / op-ed / personal-essay / journalistic /
entrepreneurial-narrative** registers — but **not** in modern JP
academic / scientific writing (per 木下 1981 and 甲田).

For analysis of those non-academic registers — op-ed, コラム, personal essay, 起業家 founder narrative — apply the kishōtenketsu lens via [`lens-rhetoric-ja.md`](lens-rhetoric-ja.md), which treats 起承転結 as the rhetorical structure rather than a genre move-set. The two lenses are complementary; pick by register:

| Register | Apply this lens (`lens-genre-ja`) for | Apply `lens-rhetoric-ja` for |
|---|---|---|
| Academic 論文 | 序論-本論-結論 move structure | (rarely — academic JP has muted rhetorical structure) |
| Business letter | 拝啓-formula 7 moves | (N/A — formula not rhetorical) |
| Op-ed / コラム | (rarely — op-eds don't have canonical move sets) | 起承転結 narrative arc |
| 起業家 pitch deck | Pitch-deck moves (problem / solution / traction / ask) | 起承転結 (often layered on top of pitch moves) |
| 報告書 | 序論-本論-結論 | (mostly N/A) |

## Step-by-step application

### Step 1: Identify register

Before mapping moves, identify which register the artifact occupies:

- 学術 (academic) — apply Part 1
- ビジネス文書 / 拝啓-letter — apply Part 2
- メール — apply Part 3
- Op-ed / コラム / 起業家 narrative — apply Part 4 (mostly delegate to lens-rhetoric-ja)

A JP artifact mixing registers (e.g. an academic paper with literary 起承転結 in the introduction) is signaling something — note it.

### Step 2: Map artifact's moves to canonical move-set

Same table format as Anglo lens, but use JP move set:

| Artifact section | Canonical move | Strength |
|---|---|---|
| §1 first paragraph | 頭語 + 時候の挨拶 | Strong / weak / **missing** |
| §2 paragraph | 主文 (さて〜) | ... |
| §3 closing | 末文 + 結語 | ... |

### Step 3: Reader-responsibility check (per Hinds 1987)

Before flagging a move as missing, ask: **could a JP reader infer
this move from context?**

In Anglo analysis, a missing transition or thesis is usually a real
gap. In JP — per Hinds — readers are expected to do more work, so
moves can be implicit and still functionally present.

Examples of legitimate implicitness:

- 序論 with no explicit `本稿の目的は〜` thesis — sometimes the title carries it; check before flagging
- ビジネス letter with abbreviated 時候の挨拶 — `お世話になっております` may carry it
- メール with no 頭語 — may signal in-house peer register, not transgression

### Step 4: Identify missing or weak moves

Common patterns specific to JP:

| Pattern | What it means |
|---|---|
| 序論 missing 問題提起 sub-move | Paper feels like report, not research |
| 主文 directly opens letter (no 頭語 / 時候) | Either rushed-business or deliberate-informal — distinguish |
| 結語 mismatched with 頭語 | Genre-illiterate writer (or AI-generated draft) |
| メール with no `よろしくお願いいたします` close | Either highly intimate or aborted draft |
| 結論 with no 限界 / 今後の課題 sub-move | Paper feels overconfident (rare in JP register) |
| 起業家 narrative with rigid 序論-本論-結論 (no 起承転結) | Possibly AI-translated from EN; flag |

### Step 5: Detect genre transgressions

Sometimes the artifact deliberately violates JP genre. Distinguish:

- **Successful subversion**: a 起業家 prospectus that opens 「拝啓」 and uses business-letter formula for personal narrative — high-control register-play, signals craft
- **Failed transgression**: an academic 論文 with 起承転結 instead of 序論-本論-結論 — signals the author isn't fluent in academic register
- **Code-switch signal**: an email opening with `Dear ○○-san` instead of `お世話になっております` — explicit code-switch, often deliberate (cross-cultural register)

## Worked example A: JP business letter snippet (5-7 lines)

> 拝啓
>
> 新緑の候、貴社ますますご清栄のこととお慶び申し上げます。平素は格別のお引き立てを賜り、厚く御礼申し上げます。
>
> さて、先日ご相談いたしました件につきまして、別添の通り企画書を提出させていただきます。ご検討のほどよろしくお願い申し上げます。
>
> 敬具
>
> 2026年5月5日
> 株式会社○○ 営業部 田中

### Move map

| Section | Canonical move | Strength |
|---|---|---|
| `拝啓` | 頭語 | Strong (canonical) |
| 「新緑の候、〜」 | 時候の挨拶 | Strong (季節 matches May) |
| 「貴社ますますご清栄〜」 | 安否の挨拶 | Strong (formal-canonical) |
| 「平素は格別の〜」 | 安否の挨拶 (extended) / relational acknowledgment | Strong |
| 「さて、先日〜」 | 主文 | Adequate (concise; the `さて` transition is canonical) |
| 「ご検討のほど〜」 | 末文 | Strong |
| `敬具` | 結語 | Strong (matches 拝啓) |
| 日付 / 署名 | 後付 | Strong |

### Findings

- All 7 canonical moves present and well-formed
- 頭語 / 結語 pairing correct (拝啓 → 敬具)
- 時候 matches actual season (新緑 = May)
- Main weakness: 主文 is **very brief** — relies on attached document; appropriate for letter-as-cover-note genre but uninformative as standalone

### Verdict

Genre-faithful canonical 拝啓-letter; all formula moves present and matched; this is a cover-letter sub-genre (主文 is intentionally minimal because the substance lives in 別添).

## Worked example B: JP academic introduction snippet

> 1. はじめに
>
> 近年、深層学習を用いた自然言語処理は急速に発展している (Brown et al., 2020)。特に大規模言語モデルは、文書要約・翻訳・質問応答など多くのタスクで高い性能を示している。しかし、日本語ビジネス文書における拝啓-formula の自動生成については、先行研究が限られている。本稿では、拝啓-formula 7 move の自動推論モデルを提案し、商用メール 1,000 件を用いて評価する。

### Move map

| Sentence | 序論 sub-move | Strength |
|---|---|---|
| 「近年、深層学習〜」 | テーマ提示 + 背景 | Strong |
| 「特に大規模言語モデル〜」 | 先行研究の概観 | Adequate (citation-thin) |
| 「しかし、日本語ビジネス文書〜」 | 問題提起 (gap) | Strong (clear `しかし` pivot) |
| 「本稿では、拝啓-formula〜」 | 本稿の目的 + 構成の予告 (folded) | Adequate (no separate roadmap; thesis is clear) |

### Findings

- All 4 core 序論 sub-moves present
- 先行研究 is cited but thinly (only 1 anchor) — could be stronger per 甲田 convention
- No separate `第2章では...` roadmap — common variant; not a flaw at this length
- `しかし` pivot is the canonical JP gap-establishing move — handled correctly

### Verdict

Genre-faithful modern JP academic 序論; thesis is clear (per 木下 1981's prescription); 先行研究 sub-move is the weakest element.

## Output format

```markdown
### Genre identified
<JP register: 学術 / 商用文 / メール / op-ed / その他>, with optional <hybrid notes>

### Move map
| Section | Canonical JP move | Strength | Notes |
|---|---|---|---|
| ... | ... | strong/adequate/weak/missing | ... |

### Missing / unconventional moves
- (note each missing move; flag whether implicit-but-functionally-present per Hinds reader-responsibility)
- (note any 頭語/結語 mismatch, register transgression, code-switch)

### Register signals
- 拝啓-formula formula adherence: strong / partial / abbreviated / absent
- Reader-responsibility load: high (many moves implicit) / medium / low (writer-responsible-leaning)
- Cross-register markers: any 起承転結 leakage into academic / any 序論-本論-結論 forced into op-ed?

### Verdict
<one paragraph stating: genre identified, formula adherence, deliberate-vs-failed transgressions, distinctive feature>
```

End with 1-line synthesis: "The artifact is **genre-X** in **JP-register-Y**;
**N** canonical moves; **M** are missing or implicit; the strongest
deviation is **Z**."

## Pitfalls

- **Treating 拝啓 / 時候 as decoration** — they are **load-bearing genre markers**; their absence is data, not noise. Never report `拝啓-formula letter` analysis without auditing all 7 moves.
- **Forcing JP academic into 起承転結 (or vice versa)** — register matters. 学術 register uses 序論-本論-結論; op-ed / 起業家 narrative uses 起承転結. Apply the wrong one and your analysis will misread the artifact's genre choices.
- **Missing reader-responsibility (Hinds 1987)** — JP readers are expected to infer more than Anglo readers. Before declaring a move "missing," check whether it is **functionally implicit** (e.g. `お世話になっております` collapsing 時候+安否).
- **Applying Anglo IMRAD directly to JP humanities papers** — JP 理工系 / 医学系 follow IMRAD (per 木下 1981); JP 人文・社会系 often follow 序論-本論-結論 with non-IMRAD body structure. Pick by sub-discipline.
- **Mistaking `お世話になっております` for filler** — it is the canonical relational opening move, simultaneously functioning as 頭語 + 安否 in modern email register. Mark it present, not absent.
- **Mismatching 頭語 / 結語 unflagged** — if the artifact opens 拝啓 and closes 草々, this is a **failed move** not a stylistic variant; report it.
- **Anglo-default fallback for JP メール** — modern email differs from canonical letter-formula; apply Part 3, not Part 2 directly.
