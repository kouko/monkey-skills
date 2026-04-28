# Philosophers Toolkit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

哲学的思考の framework 集。ユーザーを構造化された推論へ導く — 講義ではなく、より深く考えるためのインタラクティブな方法。

## Skills

### 西洋哲学

#### Socratic Method / ソクラテス式対話 / 蘇格拉底式對話

| | |
|--|--|
| **Origin** | Socrates（紀元前 470–399）、古代ギリシャ |
| **Core Idea** | 直接教えるのではなく、規律ある問いかけによってユーザー自身に知識を発見させる。「無知の知」。 |
| **Method** | Dialogue-driven state machine：Topic Discovery → Initial Exploration → Hypothesis Testing (Elenchus) → Aporia → Deepening → Synthesis |
| **Use When** | ユーザーが情報ではなく、自分の思考を挑まれたいとき |
| **Command** | `/philosophers-toolkit:socratic` |

[malkreide/socratic-method-skill](https://github.com/malkreide/socratic-method-skill) より翻案。

#### Aristotle's Four Causes / アリストテレスの四原因説 / 亞里斯多德四因說

| | |
|--|--|
| **Origin** | Aristotle（紀元前 384–322）、古代ギリシャ。『Physics』および『Metaphysics』 |
| **Core Idea** | あらゆるものは 4 つの問いで理解できる：何でできているか？何がそれをそれたらしめているか？何が生み出したか？何のためにあるか？ |
| **Method** | Framework-driven：Material Cause → Formal Cause → Efficient Cause → Final Cause → Synthesis |
| **Use When** | ユーザーがあるシステム、製品、または概念の本質を深く理解したいとき |
| **Command** | `/philosophers-toolkit:four-causes` |

#### Aristotle's First Principles / アリストテレスの第一原理 / 亞里斯多德第一原理

| | |
|--|--|
| **Origin** | Aristotle（紀元前 384–322）、古代ギリシャ。『Posterior Analytics』 |
| **Core Idea** | これ以上分解できない根本的な真理まで問題を分解し、ゼロから再構築する。類推による推論を拒否する。 |
| **Method** | Process-driven：Problem Essence → Challenge Assumptions → Establish Ground Truths → Reason Upward → Validate Reasoning |
| **Use When** | ユーザーが「best practices」や慣習に縛られ、ゼロから考え直したいとき |
| **Command** | `/philosophers-toolkit:first-principles` |

5 phase 構成は [awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill)（MIT）から着想を得た。

#### Hegelian Dialectics / ヘーゲル弁証法 / 黑格爾辯證法

| | |
|--|--|
| **Origin** | Georg Wilhelm Friedrich Hegel（1770–1831）、ドイツ。『Phenomenology of Spirit』 |
| **Core Idea** | あらゆる立場には自己矛盾の種が含まれている。それを顕在化し向き合うことで、より高次の理解に至る。Synthesis ≠ 妥協。 |
| **Method** | Phase-driven：Thesis → Antithesis → Synthesis（任意の反復：synthesis が新しい thesis になる） |
| **Use When** | ユーザーが trade-off、二者択一、または対立する見解に直面しているとき |
| **Command** | `/philosophers-toolkit:dialectics` |

#### Popper's Falsifiability / ポパーの反証可能性 / 波普可否證性

| | |
|--|--|
| **Origin** | Karl Popper（1902–1994）、オーストリア。『The Logic of Scientific Discovery』（1934） |
| **Core Idea** | 仮説は誤りであることを証明できる場合にのみ意味を持つ。自分の主張を反証しうる test を設計する — 生き残れば暫定的に受け入れられる。 |
| **Method** | Process-driven：State Hypothesis → Operationalize → Design Falsification Test → Evaluate Evidence → Verdict（falsified / survived / unfalsifiable） |
| **Use When** | ユーザーが前提を test したい、または製品の hypothesis を検証したいとき |
| **Command** | `/philosophers-toolkit:falsify` |

#### Descartes' Methodical Doubt / デカルトの方法的懐疑 / 笛卡兒方法性懷疑

| | |
|--|--|
| **Origin** | René Descartes（1596–1650）、フランス。『Meditations on First Philosophy』（1641） |
| **Core Idea** | 疑える限りすべてを体系的に疑い、疑うことのできない地点 — 疑い得ない基盤 — に到達する。 |
| **Method** | Process-driven：State Belief → Apply Doubt Layers（sensory / reasoning / systemic）→ Identify Survivors → Rebuild from Indubitable |
| **Use When** | ユーザーが基礎的な前提を監査したいとき — security の信頼モデル、データソース、組織の信念 |
| **Command** | `/philosophers-toolkit:doubt` |

### 日本哲学 / 日本哲学 / 日本哲學

#### 守破離 / Shu-Ha-Ri / 守破離

| | |
|--|--|
| **Origin** | 日本武道の伝統（合気道、茶道）。遠藤征四郎により定式化 |
| **Core Idea** | 守（規則を厳格に守る）→ 破（理由を理解し、適応し始める）→ 離（規則を超越し、自分の道を創る）。線形ではない — ある領域で守、別の領域で離ということもある。 |
| **Method** | Framework-driven 診断：Identify Domain → Diagnose Stage → Stage-Appropriate Guidance → Transition Signals |
| **Use When** | ユーザーが自分の習熟段階を評価し、適切な指導を得たいとき |
| **Command** | `/philosophers-toolkit:shu-ha-ri` |

#### 生き甲斐 / Ikigai / 生之甲斐

| | |
|--|--|
| **Origin** | 人生の目的についての日本の概念。沖縄の長寿研究で国際的に注目された |
| **Core Idea** | 目的は 4 つの軸の交点に存在する：好きなこと、得意なこと、世界が求めること、報酬を得られること。 |
| **Method** | Framework-driven：各軸を分析、欠けている / 弱い軸を診断、交点を見つける |
| **Use When** | ユーザーがプロジェクトの目的、product-market fit、またはキャリアの方向性を検証したいとき |
| **Command** | `/philosophers-toolkit:ikigai` |

#### 改善 / Kaizen / 改善

| | |
|--|--|
| **Origin** | 戦後日本の製造業。Toyota Production System で定式化 |
| **Core Idea** | 小さく継続的な改善は大規模な変革に勝る。年次戦略ではなく、日々の習慣を変える。 |
| **Method** | Process-driven cycle：現状把握 → 問題発見 → 根本原因 → 改善案 → 実行と検証 → 標準化 |
| **Use When** | ユーザーがゼロから再設計するのではなく、既存プロセスを段階的に改善したいとき |
| **Command** | `/philosophers-toolkit:kaizen` |

#### 反省 / Hansei / 反省

| | |
|--|--|
| **Origin** | 日本の自己省察の文化的実践。Toyota Way と日本の教育の核心 |
| **Core Idea** | 出来事の後の責めのない内省。「誰がしくじったか」ではなく「自分は何が見えていなかったか」に焦点を当てる。西洋の postmortem より深い — 個人的で謙虚。 |
| **Method** | Phase-driven：事実確認 → 内省 → 学び → 次の一歩 |
| **Use When** | ユーザーが完了したプロジェクト、決定、出来事を振り返り、構造的な教訓を抽出したいとき |
| **Command** | `/philosophers-toolkit:hansei` |

#### 侘寂 / Wabi-Sabi / 侘寂

| | |
|--|--|
| **Origin** | 禅仏教と茶道（千利休）に根ざす日本の美学哲学 |
| **Core Idea** | 不完全さ、無常、未完成のうちに美を見出す。over-engineering と完璧主義に対抗する。制約は設計の特長であり、欠陥ではない。 |
| **Method** | Framework-driven：3 つのレンズ — 侘（簡素）+ 寂（時間の痕跡）+ 不完全の美 |
| **Use When** | ユーザーが「これで十分」とさらなる磨き込みを判断する必要があるとき、または制約を強みとして受け入れたいとき |
| **Command** | `/philosophers-toolkit:wabi-sabi` |

### はじめに

#### Using Philosophers Toolkit

どの方法を使えばよいか分からない？ここから始めよう：

| | |
|--|--|
| **Command** | `/philosophers-toolkit:think` |
| **What it does** | あなたが何をしようとしているかを尋ね、最適な方法に振り分ける |
| **Categories** | Understand → Decide → Improve → Reflect |
| **Default** | 不明な場合は Socratic Method に fallback |

## 設計原則

- すべての skill は**インタラクティブなプロセス**であり、講義ではない
- 出力は「より良い思考」「より明確な理解」であり、レポートではない
- agent は問いかけによって導く — ユーザーが発見し、agent は処方しない
- 文化的に適切な場面では**起源の言語**で記述（日本の方法は日本語で）
- 各 skill は [skill structure standard](standards/skill-structure.md) に準拠

## Roadmap

将来の skill 計画は [ROADMAP.md](ROADMAP.md) を参照。
