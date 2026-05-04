# zh-TW 翻譯定譯表

> 鎖定 monkey-skills repo 內 README 翻譯使用的術語對照。
> 研究日期：2026-04-28。
> 研究方法：Anthropic / Obsidian 官方文件 + 台灣業界慣例（iThome 鐵人賽 / HackMD / Medium 台灣 / Taiwan OSS / Taiwan 行銷與投資業界）+ 中國大陸用語排除清單。
> 排除清單：数据→資料、信息→資訊、软件→軟體、视频→影片、程序→程式、数组→陣列、内存→記憶體、质量→品質、用户→使用者、文档→文件、文件→檔案、缺省→預設、菜单→選單、网络→網路、登录→登入、激活→啟用。

---

## 🔒 全域決策（2026-04-28 user override）

**所有英文原文技術名詞 / 專有名詞 / 角色名 / 框架名一律保留英文，不譯。**

此規則覆蓋下方各分類表格內的「主譯」欄位 — 凡標示「保留英文」「副譯保留英文」「混用 OK」者一律採用英文原文；凡標示為中文主譯者**也改為保留英文**（中文翻譯僅作參考、可在第一次出現時加括號補充說明）。

**保留英文範圍**：
- 平台 / 架構：agent、skill、plugin、marketplace、slash command、MCP、router、workflow、pipeline、envelope、worker、evaluator、orchestrator、hook、dispatch
- 品質控管：quality gate、checkpoint、gate verdict、PASS、NEEDS_REVISION、SELF check、MUST、SHOULD、MAY、protocol、standards、checklist、rubric、bounce-back、retry cap、audit trail、primary-source-grounded、canonical、byte-identical、divergence、precondition
- Skill 開發：domain-team、meta-skill、grounding、citation、attribution、ADR、Conventional Commits、semver、CI/CD、monorepo、SSOT
- Obsidian：vault、daily note、canvas、file intel、dashboard、callout、wikilink、frontmatter、properties、embed、base file
- 投資 / 資料：macro regime、nowcast、composite index、proxy、ticker、equity、holdings、portfolio、snapshot、technical indicator、DCF valuation、stock screener、backtest、primary source
- 文案：copywriting、copy、ideation、brief、headline、tagline、voice anchor、voice quadrant、brainstorming、awareness level
- 通用：README、repository、deployment、integration test、regression、refactoring、fixture、dry-run、CLI、API、SDK、commit、PR、branch、merge、log、token、prompt
- 日文 framework：キャッチコピー（保留日文）

**仍會翻譯的部分**：
- 一般敘述句子（連接詞、形容詞、動詞、語氣詞）
- 章節標題的非術語部分（如「安裝」「授權」「貢獻」）
- 表格欄位非術語部分
- 程式碼區塊註解（人類語言部分）

**首次出現可加括號補充**：例如「skill（技能）」「vault（知識庫）」— 但僅限第一次，後續一律保留英文。

下方表格的「主譯」欄為原研究結果；執行翻譯時**一律以本節 override 為準**，副譯欄僅作首次補充說明參考。

---

## 平台 / 架構

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| agent | agent（保留英文） | 代理（不推薦） | Anthropic 官方文件 zh-TW 與台灣 AI 社群（iThome 鐵人賽 2024-2026）皆保留 "agent"；如「AI Agent」「Agent Workflow」。`代理人 / 代理` 在中文 NLP 圈使用率低且易混淆 proxy。來源：[iThome 鐵人賽 - AI Agent 與 Agent Workflow 設計](https://ithelp.ithome.com.tw/articles/10376247)、[HackMD - Claude Code 術語大全](https://hackmd.io/@BASHCAT/Hk5IjaLdbg) |
| skill | skill（保留英文） | 技能（少數使用） | Anthropic 官方產品名為 "Agent Skills"，繁中翻譯文章亦保留 "Skills"。本 repo 名稱即 monkey-**skills**。來源：[anduril.tw - Claude Code Skills 翻譯](https://www.anduril.tw/claude-code-skills-guide/)、[Claude Code in Action 中文版](https://tenten.co/claude-code/) |
| plugin | plugin（保留英文） | 外掛 / 插件 | Claude Code 場景下繁中文章普遍寫 "Claude Code plugin / 插件"；Obsidian 場景台灣使用者慣用「外掛」。本 repo 為 Claude Code plugin marketplace，主譯**保留英文**較精確。來源：[GitHub - claude-plugin-marketplace](https://github.com/DennisLiuCk/claude-plugin-marketplace)、[Medium - Obsidian 入坑指南](https://medium.com/notability-center/obsidian-%E5%85%A5%E5%9D%91%E6%8C%87%E5%8D%97-2-%E8%AA%8D%E8%AD%98-vault-%E8%B7%A8%E8%A3%9D%E7%BD%AE%E5%90%8C%E6%AD%A5-08e78adda906) |
| marketplace | marketplace（保留英文） | 市集 | Claude Code / VS Code / GitHub 場景下台灣開發者多保留英文。第一次出現可標註「市集（marketplace）」。來源：[claude-plugin-marketplace](https://github.com/DennisLiuCk/claude-plugin-marketplace) |
| slash command | slash command（保留英文） | 斜線指令 | Claude Code 官方 zh-TW 文件保留 "slash command"；HackMD 繁中教學亦保留。`斜線指令` 為輔助說明用。來源：[Claude Code Docs zh-TW - Hooks](https://code.claude.com/docs/zh-TW/hooks)、[HackMD - Claude Code 術語大全](https://hackmd.io/@BASHCAT/Hk5IjaLdbg) |
| MCP | MCP（保留英文） | — | Model Context Protocol 簡稱，繁中業界一律保留英文縮寫。來源：[HackMD - Claude Code 術語大全](https://hackmd.io/@BASHCAT/Hk5IjaLdbg) |
| MCP server | MCP server（保留英文） | MCP 伺服器（混用 OK） | 台灣慣用「伺服器」（**非**「服务器」）。混用：「MCP server」或「MCP 伺服器」皆可。 |
| router | router skill / 路由 skill | 路由器（不推薦在 skill 場景） | 網路設備譯「路由器」，但 skill 場景下混用「router skill」更貼近原意。"dispatch / route" 動詞譯「路由 / 派送」。 |
| workflow | 工作流程 / workflow | — | iThome 鐵人賽繁中文章混用「Agent Workflow」與「工作流程」。建議第一次寫「工作流程（workflow）」，後續可保留英文。來源：[iThome - Agent Workflow](https://ithelp.ithome.com.tw/articles/10376247) |
| pipeline | pipeline（保留英文） | 流水線（中國大陸用語，避免）／管線 | CI/CD 場景台灣慣用「pipeline」保留英文，或譯「管線」。**避免**「流水線」。 |
| envelope (envelope contract / handoff envelope) | envelope（保留英文） | 信封 / 封包契約 | 本 repo 自創概念，主譯保留英文以保留語意。第一次出現標註「封包（envelope）」。需 user review。 |
| worker | worker agent（保留英文） | 工作 agent | 本 repo 行為角色用語，建議保留 "worker agent"。 |
| evaluator | evaluator agent（保留英文） | 評估者 agent | 本 repo 行為角色用語，建議保留 "evaluator agent"；副譯「評估者 agent」。 |
| orchestrator | orchestrator（保留英文） | 編排器 / 協調器 | 容器/Agent 場景台灣多保留英文；副譯「編排器」。 |
| hook | hook（保留英文） | 掛鉤 / 鉤子（少用） | Claude Code 官方 zh-TW 文件即保留 "Hooks"。React / Git hooks 亦慣保留英文。來源：[Claude Code Docs zh-TW - Hooks](https://code.claude.com/docs/zh-TW/hooks) |
| dispatch | 派送 / 路由 | dispatch（保留英文） | 動詞用「派送」（task dispatch）或「路由」（route）。 |

---

## 品質控管

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| quality gate | 品質門檻 | quality gate（混用 OK） | SonarQube 繁中社群與台灣 DevOps 文章慣譯「品質門檻」。**避免**「质量门」。來源：[SonarQube 繁中文檔 - Quality Gates](https://monkenwu.github.io/SonarQubeChineseDoc8.1/user-guide/quality-gates/)、[SonarQube 入門 - 改善程式碼品質](https://www.gss.com.tw/blog/improve-code-quality-with-sonarqube) |
| checkpoint | 檢查點 / checkpoint | — | 通用譯「檢查點」；CI/CD 與 ML 場景常保留英文。混用 OK。 |
| gate verdict | 閘門裁決 / gate verdict | 通過判定 | 「verdict」字面為「裁決 / 判決」，本 repo 指 PASS / NEEDS_REVISION 結果。建議「閘門裁決」或保留英文。需 user review。 |
| PASS / NEEDS_REVISION | 通過 / 待修正 | PASS / NEEDS_REVISION（保留英文） | code 中保留英文常數；散文敘述用「通過 / 待修正」。 |
| PASS_WITH_NOTES | 通過附註 | PASS_WITH_NOTES（保留英文） | 同上，code 保留英文。 |
| SELF check | SELF 自檢 | 自我檢查 | 保留 "SELF" 縮寫 + 中文補充「自檢」。 |
| MUST / SHOULD / MAY | 必須 / 應該 / 可以 | MUST / SHOULD / MAY（保留英文） | RFC 2119 等級術語業界保留英文；可加註「必須 / 應該 / 可以」。 |
| protocol | 協定 | protocol（保留英文） | 台灣慣譯「協定」（**非**「協議」，後者偏中國大陸用語）。skill 場景下保留英文亦常見。 |
| standards | 標準 | standards（保留英文） | 通用譯「標準」。 |
| checklist | 檢查清單 | checklist（保留英文） | 通用譯「檢查清單」。 |
| rubric | 評分量表 / rubric | 評分標準 | 教育/評估領域台灣譯「評分量表」；技術文件可保留 "rubric"。 |
| bounce-back | 退回重做 / bounce-back | 反彈 | 本 repo 流程用語，建議「退回重做」描述行為。 |
| retry cap | 重試上限 | — | 通用直譯。 |
| audit trail | 稽核軌跡 | 稽核紀錄 / audit trail | 金融與資安場景台灣慣譯「稽核軌跡」。 |
| primary-source-grounded | 一手來源錨定 | 原始來源錨定 / 根植於一手來源 | 學術譯「一手資料 / 原始資料」；本 repo 強調 "grounded on primary source"，建議「一手來源錨定」。需 user review。來源：[Linguee - source 譯法](https://cn.linguee.com/%E8%8B%B1%E8%AF%AD-%E4%B8%AD%E6%96%87/%E7%BF%BB%E8%AD%AF/single+source+of+truth.html) |
| canonical | 正典 / 標準形式 | canonical（保留英文） | 數學/CS 譯「正規形式 / 標準形式」；framework 名單上下文可譯「正典」（如「PASONA 正典」）。 |
| byte-identical | 位元組完全相同 | byte-identical（保留英文） | 直譯。台灣用「位元組」（**非**「字节」）。 |
| divergence | 偏離 / 分歧 | divergence（保留英文） | 通用譯「偏離 / 分歧」。 |
| precondition | 前置條件 | precondition（保留英文） | 軟體工程台灣慣譯「前置條件」。 |

---

## Skill 開發

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| domain-team | domain-team（保留英文） | 領域團隊 | 本 repo 自創專有名詞，建議保留英文。第一次標註「領域團隊（domain-team）」。 |
| meta-skill | meta-skill（保留英文） | 元技能 | 「meta-」前綴台灣常保留英文（如 metadata、meta-programming）。 |
| grounding | grounding / 接地 | 一手來源支持 | LLM 場景台灣繁中多保留 "grounding"；學術可譯「接地 / 紮根」。需 user review。 |
| citation | 引用 | citation（保留英文） | 通用譯「引用」；學術文件可譯「引註」。 |
| attribution | 出處標註 / 歸屬 | attribution（保留英文） | 「歸屬 / 出處標註」皆通用。 |
| ADR (Architecture Decision Record) | ADR（架構決策紀錄） | — | 業界保留 "ADR" 縮寫，第一次標註「架構決策紀錄」。 |
| Conventional Commits | Conventional Commits（保留英文） | 慣例式提交 / 規範性提交 | 台灣繁中文章混用「慣例式提交」「規範性提交」與保留英文。產品名建議保留英文。來源：[HackMD - Conventional Commits 規範性提交](https://hackmd.io/@ohQEG7SsQoeXVwVP2-v06A/rkhtpmyXa)、[史戴拉 - 搞懂慣例式提交](https://estellacoding.github.io/blog/conventional-commit-type/) |
| semver / Semantic Versioning | 語意化版本 | semver（保留英文） | 台灣繁中標準譯「語意化版本」。來源：[fingergame.com.tw - Conventional Commits、SemVer 與 Changelog](https://fingergame.com.tw/conventional-commits/) |
| CI/CD | CI/CD（保留英文） | — | 業界一律保留英文縮寫。 |
| monorepo | monorepo（保留英文） | 單一儲存庫 | 業界保留英文；副譯「單一儲存庫」較少用。 |
| SSOT (single source of truth) | 單一事實來源 | 單一資訊來源 / SSOT | 台灣繁中譯「單一事實來源」最貼近原意；中國大陸常譯「單一數據源」（避免）。來源：[Tecky - Programming 原則](https://tecky.io/en/blog/%E5%B9%B3%E5%B8%B8%E4%BA%BA%E9%83%BD%E8%83%BD%E6%8E%8C%E6%8F%A1%E7%9A%84Programming%20%E5%8E%9F%E5%89%87/)、[Medium - Ray Shih SSOT](https://medium.com/@rayshih771012/mvc-%E6%9E%B6%E6%A7%8B%E6%BC%94%E9%80%B2-single-source-of-truth-2720f5a5facd) |
| source of truth | 事實來源 | 真實來源 | 同上。 |

---

## Obsidian 域

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| vault | vault（保留英文） | 保管庫 / 知識庫 | 台灣 Obsidian 社群（吳明倫等）慣用保留英文 "vault"；中國大陸論壇譯「保管庫」。建議第一次標註「vault（知識庫）」。來源：[Medium - Obsidian 入坑指南 #2 認識 Vault](https://medium.com/notability-center/obsidian-%E5%85%A5%E5%9D%91%E6%8C%87%E5%8D%97-2-%E8%AA%8D%E8%AD%98-vault-%E8%B7%A8%E8%A3%9D%E7%BD%AE%E5%90%8C%E6%AD%A5-08e78adda906) |
| daily note | daily note（保留英文） | 每日筆記 | Obsidian 繁中社群混用；台灣偏好保留英文。混用 OK。 |
| canvas | Canvas（保留英文） | — | Obsidian Canvas 為產品名，保留英文。 |
| file intel | file intel（保留英文） | 檔案情報 | 本 repo 自創 skill 名，保留英文。 |
| dashboard | 儀表板 / dashboard | 控制台（不推薦） | 台灣繁中標準譯「儀表板」。**避免**「仪表盘」。 |
| callout | callout（保留英文） | 標註方塊 | Obsidian 官方繁中保留 "callout"；繁中文章亦慣保留。需要時可說明「標註方塊（callout）」。來源：[Obsidian 中文幫助](https://obsidian.md/zh/help/) |
| wikilink | wikilink / 雙向連結 | 內部連結 | Obsidian 場景常稱「雙向連結」描述功能，產品語法名保留 "wikilink"。 |
| frontmatter | frontmatter（保留英文） | 前置資料 | Obsidian / Jekyll 場景慣保留 "frontmatter"。 |
| properties | properties（保留英文） | 屬性 | Obsidian 1.4+ 將 frontmatter 顯示為 Properties UI；繁中譯「屬性」。 |
| embed | 嵌入 | embed（保留英文） | 動詞「嵌入」；名詞混用 OK。 |
| base file | Base 檔（.base 檔） | base file（保留英文） | Obsidian Bases 為產品名，保留英文；副檔名直稱「.base 檔」。 |

---

## 投資 / 資料域

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| macro regime | 總經狀態 / 總經 regime | 宏觀體制（中國大陸用語） | 台灣金融業慣用「總經（總體經濟）」；regime 譯「狀態 / 階段」。**避免**「宏觀」。 |
| nowcast | 即時推估 / nowcast | 即時預測 | 央行報告慣用「即時推估」；FRED / Atlanta Fed 場景保留 "nowcast"。 |
| composite index | 綜合指標 / 綜合指數 | — | 台灣國發會景氣指標慣用「景氣綜合指標」。 |
| proxy | proxy（保留英文） | 代理變數 | 統計/計量場景譯「代理變數」；網路場景保留 "proxy"。 |
| ticker | ticker（保留英文） | 股票代號 / 代碼 | 台灣財經慣用「股票代號」描述功能；保留 "ticker" 亦廣用。 |
| equity | 股權 / 個股 | equity（保留英文） | 上下文決定：「個股」（個別股票）、「股權」（公司持份）、「股票型」（資產類別）。 |
| holdings | 持股 / 持倉 | holdings（保留英文） | 台灣金融業慣用「持股」「持倉」。 |
| portfolio | 投資組合 | portfolio（保留英文） | 台灣金融業標準譯「投資組合」。來源：[元大 ETF 投資組合計算器](https://www.yuanta-etfadvisor.com/introduction/c0330274-d3fe-4543-ab36-b09d72c93449)、[阿爾發 投資組合分析](https://blog.roboadvisor.com.tw/?p=5291) |
| snapshot | snapshot（保留英文） | 快照 | 通用譯「快照」；技術文件混用 OK。 |
| technical indicator | 技術指標 | — | 台灣財經標準譯「技術指標」。來源：[鉅亨網 - 技術指標](https://www.cnyes.com/twstock/a_technical9.aspx) |
| DCF valuation | DCF 估值 / 現金流折現估值 | — | 台灣金融業慣用「DCF」保留英文；展開為「現金流折現法」或「股息折現估值」（依模型）。 |
| stock screener | 選股器 / 選股工具 | screener（保留英文） | 台灣財經慣用「選股」「選股器」。來源：[FinLab - 簡單選股和回測](https://www.finlab.tw/python-%E7%B0%A1%E5%96%AE%E9%81%B8%E8%82%A1%E5%92%8C%E5%9B%9E%E6%B8%AC/) |
| backtest | 回測 | backtest（保留英文） | 台灣量化投資標準譯「回測」。來源：[Mr.Market - 投資組合](https://rich01.com/how-set-portfolio/)、[Portfolio Visualizer 回測教學](https://xuanstyl.com/backtest-portfolio-visualizer/) |
| primary source | 一手來源 / 原始來源 | primary source（保留英文） | 學術譯「一手資料」「原始資料」；技術文件中本 repo 強調「primary-source data fetcher」，建議「一手來源」。 |

---

## 文案域

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| copywriting | 文案撰寫 / 文案 | copywriting（保留英文） | 台灣行銷業標準譯「文案撰寫」「廣告文案」。來源：[數位馬克町 - 廣告文案範例](https://digimkt.com.tw/marketing_plan/%E6%96%87%E6%A1%88%E7%AF%84%E4%BE%8B-%E5%BB%A3%E5%91%8A%E6%96%87%E6%A1%88/) |
| copy | 文案 | — | 同上，「copy」單獨出現亦譯「文案」。 |
| ideation | 創意發想 / 點子發想 | ideation（保留英文） | 設計/行銷業繁中慣譯「創意發想」「發想」。 |
| brief | 需求簡報 / brief | 創意簡報 | 廣告/設計業混用「brief」與「需求簡報」「創意簡報」。產品語境建議保留英文。 |
| headline | 標題 / 主標 | headline（保留英文） | 台灣廣告業慣用「主標」「標題」。來源：[昇華行銷 - 創意標語 5 大技巧](https://shenghua.tw/%E5%89%B5%E6%84%8F%E6%A8%99%E8%AA%9E/) |
| キャッチコピー | キャッチコピー（保留日文） | catch / 主標 / 廣告金句 | 台灣廣告業圈內保留日文「キャッチコピー」（受日本廣告業影響深）；對外可譯「廣告金句」「主標」。本 repo 為日文導向 framework（神田 / 谷山），建議**保留日文**。來源：[動腦 - 廣告金句](https://www.brain.com.tw/news/articlecontent?ID=17006) |
| tagline | 品牌標語 / tagline | slogan | 台灣品牌行銷慣用「品牌標語」。來源：[晨意品牌設計 - 品牌標語大全](https://mmdesign.tw/975/brand-marketing/30slogan/) |
| voice anchor | 語調錨點 / voice anchor | 聲音錨點 | 本 repo 自創概念，建議「語調錨點」（voice = 語調）。需 user review。 |
| voice quadrant | 語調象限 / voice quadrant | — | 同上，象限為標準翻譯。 |
| brainstorming | 腦力激盪 | ブレスト（日文圈混用） / brainstorming（保留英文） | 台灣標準譯「腦力激盪」；日文業界混用「ブレスト」（brainstorming 縮寫）。 |
| awareness level (Schwartz) | 意識層級（Schwartz） | 認知層級 | 廣告心理學譯「意識層級」較貼近 Schwartz 原意（unaware → most aware）。 |

---

## 文物解構域

deconstruct-toolkit 專用術語。本 plugin 對外部「精緻文物」（文案 / UI / 文件包 / 論證 / 產品 / 組織）做逆向分析，理論底座結合 Derrida（哲學）、Barthes（符號學）、Toulmin（論證）、Lakoff（框架）、Goffman（社會框架）、Cialdini（說服）、Bhatia（體裁）、Nielsen-Norman（UX）。

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| deconstruct (verb) | 解構 / 逆向解構 | 拆解（口語）/ deconstruct（保留英文） | 中文哲學界與設計批評界一致譯「解構」（Derrida 系譜）。維基百科「解構主義」獨立詞條。BCG 商業語境引日文「脱構築」進中文亦譯「解構」。 |
| deconstruction (noun) | 解構 | 解構主義（哲學語境）| 同上。 |
| artifact | 文物 | 制作物 / artifact（保留英文）| 本 plugin 採「文物」承襲中文「文化文物」「設計文物」用法。**避免**「人工製品」（過於工程化）/「製作物」（日文式）/「成品」（過於通俗）。 |
| lens (analytical) | lens（保留英文） | 透鏡（不推薦：光學歧義）| 批評理論社群（critical theory / theoretical lens / framework analysis）已將 `lens` 確立為方法論術語。中文「透鏡」99% 用於光學（凸透鏡 / 凹透鏡 / 廣角透鏡），無「分析框架」引申義。本 plugin 全 body 保留英文。 |
| frame (analytical) | 框架 | フレーム（日文混用）| Goffman / Lakoff frame analysis 中文標準譯「框架」。同 cognitive frame / discourse frame。注意與「邊框」「畫面」區分。 |
| reframe | 重塑框架 / 換框 | reframing（保留英文）| Lakoff 政治語言學圈譯「換框」；認知治療圈譯「重塑框架」。本 plugin 偏前者語境。 |
| warrant (Toulmin) | warrant（保留英文）| 論證根據 / 論據 | Toulmin 中文譯界三派並立（論據 / 根據 / 保證），無一統。本 repo 取保留英文路線；中文補充說明用「論證根據」。 |
| claim (Toulmin) | 主張 / claim | 論點 | 哲學論證界譯「主張」；商業論證界用「論點」。本 plugin 取「主張」（更接近 Toulmin 原意）。 |
| grounds (Toulmin) | 證據 / 依據 | grounds（保留英文）| 中文邏輯學界譯「證據」「依據」。 |
| rebuttal (Toulmin) | 反駁 / rebuttal | 反證 | 法學中文譯「反駁」（更貼近 Toulmin 原意）。 |
| qualifier (Toulmin) | 限定詞 / qualifier | 條件限定 | 邏輯學中文譯「限定詞」。 |
| dark pattern | 黑暗模式 / dark pattern | 暗黑模式（中國大陸用法，**避免**）/ 欺騙性設計 | UX 中文圈普及譯「黑暗模式」（Brignull 原文 dark pattern）；Brignull 2024 改稱 deceptive pattern，副譯「欺騙性設計」。 |
| binary opposition | 二元對立 | 二項對立（日文式，避免）| Derrida / 結構主義中文標準譯「二元對立」。 |
| affordance | affordance（保留英文）| 行動可能性 / 可供性 / 示能性 | 中文無確立譯名（三派並立）；HCI / UX 業界保留英文。Norman 中譯本《設計的心理學》亦保留英文。 |
| signifier | 指示物 / signifier | 能指（中國大陸用法，**避免**）| Norman 設計論譯「指示物」；Saussure 符號學中國大陸譯「能指」（台灣使用率低）。 |
| genre move | 體裁 move / 體裁步驟 | move（保留英文）| Swales/Bhatia genre analysis 中文無統一譯名；學術寫作圈混用「移動」「步驟」「move」。本 plugin 保留英文。 |
| pentad (Burke) | 五元 / pentad | 五大要素 | Burke dramatistic pentad 中文譯界用「五元」（act / scene / agent / agency / purpose）。 |
| dramatism (Burke) | 戲劇主義 | — | Burke 修辭學中文標準譯。 |
| heuristic (Nielsen) | 啟發法 / heuristic | 經驗法則 | Nielsen 10 heuristics 中文 UX 圈譯「啟發法」/「經驗法則」混用。 |
| teardown | teardown（保留英文）| 拆解（不推薦：與 deconstruct 同字混淆）| 業界用語，與 deconstruct 區分（teardown = 拆解策略；deconstruct = 揭露隱性結構）。本 plugin **不**用 teardown。 |
| reverse engineering | 逆向工程 | reverse engineering | 工程語境用「逆向工程」（軟體 / 硬體拆解複製）；本 plugin 不屬此語意（已在 §2.2 邊界 fence 排除）。 |
| primary source | 原始文獻 / primary source | 一手資料 | 學術中文譯「原始文獻」；研究方法圈混用「一手資料」。本 repo 取保留英文路線。 |
| symptomatic reading | 症狀式閱讀 / symptomatic reading | — | Althusser 譯介文獻譯「症狀式閱讀」（讀文本中「不在場」之物）。 |

---

## 通用

| EN term | zh-TW（主譯） | 副譯 / 備用 | 決策依據 / 來源 |
|---|---|---|---|
| README | README（保留英文） | 說明文件 | 一律保留英文檔名 README；副譯「說明文件」描述用途。 |
| repository | 儲存庫 / repo | — | 台灣慣用「儲存庫」（**非**「仓库」）；口語「repo」混用 OK。 |
| deployment | 部署 | deployment（保留英文） | 通用譯「部署」。 |
| integration test | 整合測試 | — | 台灣軟體業標準譯「整合測試」。**避免**「集成測試」（中國大陸用語）。 |
| regression | 回歸 / 迴歸 | regression（保留英文） | 「回歸測試」「迴歸測試」皆通用；統計上下文用「迴歸（分析）」。 |
| refactoring | 重構 | refactoring（保留英文） | 通用譯「重構」。 |
| fixture | fixture（保留英文） | 測試樣本 / 測試資料 | 測試框架（pytest 等）慣保留英文；副譯「測試樣本」說明用途。 |
| dry-run | dry-run（保留英文） | 試跑 / 演練 | 業界慣保留英文；副譯「試跑」描述行為。 |
| CLI | CLI（保留英文） | 命令列介面 | 業界保留英文縮寫。 |
| API | API（保留英文） | 應用程式介面 | 業界保留英文縮寫。 |
| SDK | SDK（保留英文） | — | 業界保留英文縮寫。 |
| commit | commit（保留英文） | 提交 | Git 場景台灣繁中慣用「commit」保留英文；副譯「提交」描述動作。 |
| pull request / PR | PR / pull request（保留英文） | — | 業界保留英文。 |
| branch | 分支 / branch | — | Git 場景台灣慣譯「分支」，混用 OK。 |
| merge | 合併 / merge | — | Git 場景台灣慣譯「合併」，混用 OK。 |
| log | 日誌 / log | — | 通用譯「日誌」（**非**「日志」）。 |
| token | token（保留英文） | 詞元 / 權杖 | LLM 場景保留英文最常見；NLP 學術譯「詞元」；認證場景譯「權杖」。 |
| prompt | prompt（保留英文） | 提示詞 | LLM 場景台灣繁中混用「prompt」保留英文與「提示詞」「提示語」。 |

---

## 翻譯通用守則

1. **程式碼區塊內的英文不譯**：command、檔名、URL、路徑（如 `domain-teams/skills/code-team/`）保持原文。
2. **註解（comments）**：若是人類語言則譯，若是程式語法（如 `// TODO`）保留原文。
3. **第一次出現的術語**可加括號標註原文：「外掛（plugin）」、「一手來源錨定（primary-source-grounded）」。
4. **標題層級**（# / ## / ###）保持與原文一致；不額外增減層級。
5. **Markdown 表格**欄位數保持一致；對齊符號（`---`、`:---`）保持原文。
6. **連結 `[text](url)`** 中 text 譯，url 不動。
7. **保留英文清單**（一律不譯）：CLI、API、SDK、MCP、CI/CD、DCF、PR、URL、JSON、YAML、ADR、SSOT、PASONA、QUEST、PASTOR、BEAF、PREP、CREMA、AIDMA、SOLID、TDD、KPI、ETF。
8. **產品/工具名**保留原文：Claude Code、Obsidian、SonarQube、yfinance、FRED、TWSE、EDINET、SEC EDGAR、ECOS、akshare 等。
9. **日文 framework 用語**（神田 PASONA、谷山、糸井、龔大中、許舜英、Ogilvy）保留原作者名與框架名不譯。
10. **混用 OK 的詞**：在同一份文件內可交替使用主譯與英文，但同一上下文段落內保持一致。
11. **避免中國大陸用語**（核心排除清單）：
    - 数据 → 資料
    - 信息 → 資訊
    - 软件 → 軟體
    - 视频 → 影片
    - 程序 → 程式（程序 = procedure 流程）
    - 数组 → 陣列
    - 内存 → 記憶體
    - 质量 → 品質
    - 用户 → 使用者
    - 文件（檔案語境）→ 檔案；文件（文檔語境）→ 文件
    - 缺省 → 預設
    - 菜单 → 選單
    - 网络 → 網路
    - 登录 → 登入
    - 激活 → 啟用
    - 服务器 → 伺服器
    - 仓库 → 儲存庫
    - 集成 → 整合
    - 兼容 → 相容
    - 优化 → 最佳化 / 優化
    - 调试 → 除錯 / 偵錯
    - 部署 → 部署（兩岸通用）
    - 高级 → 進階
    - 默认 → 預設
12. **「需 user review」標記**：以下術語決策不確定，建議翻譯時 highlight 並請使用者最終確認：
    - envelope (envelope contract / handoff envelope)
    - gate verdict
    - primary-source-grounded
    - grounding
    - voice anchor / voice quadrant

---

## 來源彙整

1. [Anthropic Claude Code Skills 翻譯指南（anduril.tw）](https://www.anduril.tw/claude-code-skills-guide/)
2. [Claude Code Docs zh-TW - Hooks 參考](https://code.claude.com/docs/zh-TW/hooks)
3. [HackMD - Claude Code 術語大全](https://hackmd.io/@BASHCAT/Hk5IjaLdbg)
4. [iThome 鐵人賽 - AI Agent 與 Agent Workflow 設計](https://ithelp.ithome.com.tw/articles/10376247)
5. [Medium - Obsidian 入坑指南 #2：認識 Vault](https://medium.com/notability-center/obsidian-%E5%85%A5%E5%9D%91%E6%8C%87%E5%8D%97-2-%E8%AA%8D%E8%AD%98-vault-%E8%B7%A8%E8%A3%9D%E7%BD%AE%E5%90%8C%E6%AD%A5-08e78adda906)
6. [SonarQube 繁中文檔 - Quality Gates](https://monkenwu.github.io/SonarQubeChineseDoc8.1/user-guide/quality-gates/)
7. [HackMD - Conventional Commits 規範性提交](https://hackmd.io/@ohQEG7SsQoeXVwVP2-v06A/rkhtpmyXa)
8. [Tecky - 平常人都能掌握的 Programming 原則（SSOT）](https://tecky.io/en/blog/%E5%B9%B3%E5%B8%B8%E4%BA%BA%E9%83%BD%E8%83%BD%E6%8E%8C%E6%8F%A1%E7%9A%84Programming%20%E5%8E%9F%E5%89%87/)
9. [元大 ETF - 投資組合計算器](https://www.yuanta-etfadvisor.com/introduction/c0330274-d3fe-4543-ab36-b09d72c93449)
10. [FinLab - Python 股票選股與回測](https://www.finlab.tw/python-%E7%B0%A1%E5%96%AE%E9%81%B8%E8%82%A1%E5%92%8C%E5%9B%9E%E6%B8%AC/)
11. [數位馬克町 - 經典廣告文案範例](https://digimkt.com.tw/marketing_plan/%E6%96%87%E6%A1%88%E7%AF%84%E4%BE%8B-%E5%BB%A3%E5%91%8A%E6%96%87%E6%A1%88/)
12. [動腦 Brain.com.tw - 廣告金句](https://www.brain.com.tw/news/articlecontent?ID=17006)
