# Philosophers Toolkit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

哲學思考框架，引導使用者透過結構化推理進行思考 — 不是講課，而是讓思考更深入的互動式方法。

## Skills

### 西方哲學

#### Socratic Method / ソクラテス式対話 / 蘇格拉底式對話

| | |
|--|--|
| **Origin** | Socrates（公元前 470–399），古希臘 |
| **Core Idea** | 透過有紀律的提問引導使用者自行發現知識，而非直接傳授。「我知道我一無所知。」 |
| **Method** | Dialogue-driven state machine：Topic Discovery → Initial Exploration → Hypothesis Testing (Elenchus) → Aporia → Deepening → Synthesis |
| **Use When** | 使用者希望自己的思考被挑戰，而不是想取得資訊時 |
| **Command** | `/philosophers-toolkit:socratic` |

改編自 [malkreide/socratic-method-skill](https://github.com/malkreide/socratic-method-skill)。

#### Aristotle's Four Causes / アリストテレスの四原因説 / 亞里斯多德四因說

| | |
|--|--|
| **Origin** | Aristotle（公元前 384–322），古希臘。《Physics》與《Metaphysics》 |
| **Core Idea** | 任何事物都可以透過四個提問來理解：它由什麼構成？是什麼讓它成為它自己？是什麼造就了它？它的目的是什麼？ |
| **Method** | Framework-driven：Material Cause → Formal Cause → Efficient Cause → Final Cause → Synthesis |
| **Use When** | 使用者想深入理解某個系統、產品或概念的本質 |
| **Command** | `/philosophers-toolkit:four-causes` |

#### Aristotle's First Principles / アリストテレスの第一原理 / 亞里斯多德第一原理

| | |
|--|--|
| **Origin** | Aristotle（公元前 384–322），古希臘。《Posterior Analytics》 |
| **Core Idea** | 將問題拆解到無法再化約的根本真理，再從零重建。拒絕以類比進行推理。 |
| **Method** | Process-driven：Problem Essence → Challenge Assumptions → Establish Ground Truths → Reason Upward → Validate Reasoning |
| **Use When** | 使用者被「best practices」或慣例所困，想從零重新思考 |
| **Command** | `/philosophers-toolkit:first-principles` |

五階段結構靈感來自 [awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill)（MIT）。

#### Hegelian Dialectics / ヘーゲル弁証法 / 黑格爾辯證法

| | |
|--|--|
| **Origin** | Georg Wilhelm Friedrich Hegel（1770–1831），德國。《Phenomenology of Spirit》 |
| **Core Idea** | 任何立場都包含自我矛盾的種子。將它顯化並深入處理，便能抵達更高層次的理解。Synthesis ≠ 妥協。 |
| **Method** | Phase-driven：Thesis → Antithesis → Synthesis（可選擇迭代：synthesis 變為新的 thesis） |
| **Use When** | 使用者面臨權衡取捨、二選一或對立觀點 |
| **Command** | `/philosophers-toolkit:dialectics` |

#### Popper's Falsifiability / ポパーの反証可能性 / 波普可否證性

| | |
|--|--|
| **Origin** | Karl Popper（1902–1994），奧地利。《The Logic of Scientific Discovery》（1934） |
| **Core Idea** | 一個假設只有在能被證偽時才有意義。設計能推翻自己主張的測試 — 若能存活下來，便暫時被接受。 |
| **Method** | Process-driven：State Hypothesis → Operationalize → Design Falsification Test → Evaluate Evidence → Verdict（falsified / survived / unfalsifiable） |
| **Use When** | 使用者需要測試假設或驗證產品 hypothesis |
| **Command** | `/philosophers-toolkit:falsify` |

#### Descartes' Methodical Doubt / デカルトの方法的懐疑 / 笛卡兒方法性懷疑

| | |
|--|--|
| **Origin** | René Descartes（1596–1650），法國。《Meditations on First Philosophy》（1641） |
| **Core Idea** | 系統性地懷疑一切「能」被懷疑的事，直到抵達「不能」被懷疑的事 — 不可懷疑的基礎。 |
| **Method** | Process-driven：State Belief → Apply Doubt Layers（sensory / reasoning / systemic）→ Identify Survivors → Rebuild from Indubitable |
| **Use When** | 使用者需要稽核基礎假設 — 資安信任模型、資料來源、組織信念 |
| **Command** | `/philosophers-toolkit:doubt` |

### 日本哲學 / 日本哲学 / 日本哲學

#### 守破離 / Shu-Ha-Ri / 守破離

| | |
|--|--|
| **Origin** | 日本武道傳統（合気道、茶道）。由遠藤征四郎正式化 |
| **Core Idea** | 守（嚴格遵守規則）→ 破（理解為何，開始調整）→ 離（超越規則，創造自己的道）。並非線性 — 一個人可在某領域為守，另一領域為離。 |
| **Method** | Framework-driven 診斷：Identify Domain → Diagnose Stage → Stage-Appropriate Guidance → Transition Signals |
| **Use When** | 使用者想評估自己的精通程度，並取得相應的指引 |
| **Command** | `/philosophers-toolkit:shu-ha-ri` |

#### 生き甲斐 / Ikigai / 生之甲斐

| | |
|--|--|
| **Origin** | 日本對人生意義的概念。因沖繩長壽研究而廣為人知 |
| **Core Idea** | 意義存在於四個軸線的交集：你所熱愛的、你所擅長的、世界所需要的、你能藉以獲得報酬的。 |
| **Method** | Framework-driven：分析每一軸、診斷哪一軸缺失或薄弱、找出交集 |
| **Use When** | 使用者想驗證專案目的、product-market fit 或職涯方向 |
| **Command** | `/philosophers-toolkit:ikigai` |

#### 改善 / Kaizen / 改善

| | |
|--|--|
| **Origin** | 戰後日本製造業。於 Toyota Production System 正式化 |
| **Core Idea** | 小而持續的改善勝過大規模的轉型。改變每日習慣，而不是年度策略。 |
| **Method** | Process-driven 循環：現状把握 → 問題発見 → 根本原因 → 改善案 → 実行と検証 → 標準化 |
| **Use When** | 使用者想以漸進方式改善現有流程，而非從零重新設計 |
| **Command** | `/philosophers-toolkit:kaizen` |

#### 反省 / Hansei / 反省

| | |
|--|--|
| **Origin** | 日本自我省察的文化實踐。Toyota Way 與日本教育的核心 |
| **Core Idea** | 事件後不究責的內省。聚焦「我沒看見什麼？」而非「誰搞砸了？」比西方 postmortem 更深 — 個人化且謙卑。 |
| **Method** | Phase-driven：事実確認 → 内省 → 学び → 次の一歩 |
| **Use When** | 使用者想反思已完成的專案、決策或事件，萃取結構性的學習 |
| **Command** | `/philosophers-toolkit:hansei` |

#### 侘寂 / Wabi-Sabi / 侘寂

| | |
|--|--|
| **Origin** | 源於禪宗與茶道（千利休）的日本美學哲學 |
| **Core Idea** | 在不完美、無常與不完整中尋見美。對抗 over-engineering 與完美主義。約束是設計的特徵，不是缺陷。 |
| **Method** | Framework-driven：3 個視角 — 侘（簡素）+ 寂（時間痕跡）+ 不完全の美（不完整之美） |
| **Use When** | 使用者需要判斷「夠好」與更多打磨之間的取捨，或想將約束視為優勢 |
| **Command** | `/philosophers-toolkit:wabi-sabi` |

### 開始使用

#### Using Philosophers Toolkit

不確定要用哪個方法？從這裡開始：

| | |
|--|--|
| **Command** | `/philosophers-toolkit:think` |
| **What it does** | 詢問你想做什麼，再為你路由到最合適的方法 |
| **Categories** | Understand → Decide → Improve → Reflect |
| **Default** | 若不確定，會 fallback 至 Socratic Method |

## 設計原則

- 每一個 skill 都是**互動式流程**，不是講課
- 產出的是「更好的思考」或「更清晰的理解」，不是報告
- agent 透過提問來引導 — 由使用者發現，agent 不開處方
- 在文化上適合的場合採用**起源語言**書寫（日本方法以日文書寫）
- 每個 skill 遵循 [skill structure standard](standards/skill-structure.md)

## Roadmap

請參考 [ROADMAP.md](ROADMAP.md) 了解未來規劃中的 skills。
