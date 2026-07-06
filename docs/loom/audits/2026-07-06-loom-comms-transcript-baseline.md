# loom-* 溝通品質實證 — 跨專案 transcript 稽核

Date: 2026-07-06. Method: grep `"skill":"loom-` across
`/Users/kouko/.claude/projects/*/*.jsonl` (214 files hit; after excluding
firing-A/B harness dirs and subagent scratchpad dirs → 37 real-session
files across 17 project dirs). 11 sessions from 8 distinct project dirs
examined in depth (main-chain turns only, `isSidechain` excluded).
Line numbers = jsonl line numbers in the cited file.

Sessions examined:

| # | Project dir | Session | Date | Work |
|---|---|---|---|---|
| S1 | -Users-kouko-XcodeProjects-komado-Viewfinder | 06647157-1b71-4d2b-ad44-289cdb3c3d93.jsonl | 07-03 | A/V pipeline audit → full loom pipeline (brainstorm→plan→SDD) |
| S2 | -Users-kouko-XcodeProjects-komado-Viewfinder | f0789a4c-067d-433e-a52a-f788db68b9cf.jsonl | 07-06 | tracking-items P1–P3 fixes |
| S3 | -Users-kouko-XcodeProjects-komado-Refs | 225fa464-e04e-4ede-b76b-a502d207d51e.jsonl | 07-04 | ⌘N clipboard bug → TDD fix + smoke |
| S4 | -Users-kouko-XcodeProjects-komado-Refs | 1f54c98d-69da-430b-83a5-e9a878170078.jsonl | 06-23 | loom-docs backfill + timer-mode perf brainstorm |
| S5 | -Users-kouko-GitHub-youtube-summarize-scraper | 867713a8-b307-40be-ac65-3fdb3d3cf5e0.jsonl | 07-04 | LM Studio multi-instance HA planning |
| S6 | -Users-kouko-GitHub-reading-list-summarize-scraper | 978c9592-ff49-4524-a708-0ad46d943bd4.jsonl | 07-04 | port openai-compat HA (TDD) |
| S7 | -Users-kouko--supacode-repos-monkey-skills-loom-dogfood | c73e92db-7b4e-454f-958a-b75f6a60cf73.jsonl | 06-24 | living-spec slice-2 brainstorm |
| S8 | -Users-kouko--supacode-repos-monkey-skills-loom-dogfood | 198f5d1e-f354-4dc1-b024-cf6b9aedbdaf.jsonl | 06-23 | living-spec design decisions + adversarial review |
| S9 | -Users-kouko--supacode-repos-monkey-skills-loom-s2 | a74d08ae-be41-4a5a-a27f-b3ce993ba0ab.jsonl | 06-22 | loom-code router refactor + verification |
| S10 | -Users-kouko-GitHub-monkey-skills | ff13f714-94eb-43a6-825f-66df5598420c.jsonl | 07-03 | loom audit close-out + "merge plugins?" consult |
| S11 | -Users-kouko--supacode-repos-monkey-skills-obsidian-skill-r1 | 6e739422-d65e-4158-832f-c39c88684c69.jsonl | 07-04 | arc-tracking skill rewrite |

---

## A. 使用者親口的溝通回饋（step-6 sweep — 逐字命中）

Search: 看不懂/講人話/白話/太複雜/什麼意思/簡單/視覺化/圖/中文 etc. in
user-role main-chain turns of loom sessions. **7 real hits** (plus the
meta-complaints), listed with file:line:

1. **S7:219** — user: 「我還是不知道你要我決定的東西的意義與影響」
   (after two rounds of diagram already delivered — comprehension of the
   DECISION itself still zero). Assistant's reply S7:222 admits:
   「抱歉,我把這題包在術語裡了。退一步用白話講…」 then gives the
   smoke-detector (煙霧偵測器) metaphor + a plain 2-column table — proving
   the plain version existed all along and was withheld until round 3.
2. **S7:184** — user: 「用 ascii graph 說明」 (visual never offered; user
   had to request it at a checkpoint sign-off).
3. **S7:191** — user: 「圖可以用中文嗎」 — the diagram delivered at S7:187
   had ALL-ENGLISH labels (`SOURCE TREE / SPECS TREE / extract_tags(text)
   / load_namespace(dir)`) in a 繁中 conversation.
4. **S8:1294** — user: 「一個一個來 請先用視覺化說明」 — after S8:1290
   dumped a whole review verdict at once: "**HAS-CONTRADICTIONS** … 8 個
   裡的 1 個 … 2 個 BLOCKER … 🔴 B1 — #5 其實閃避了原始 Gap".
5. **S9:1189** — user quotes the assistant's own jargon sentence back
   («Continuous-mode 的「載入 reference」是 prose 指示、不是 harness 機械
   強制…prose-trust 模型…auto-merge 不變式留在 body、freeze 有硬閘») and
   appends: 「←可以視覺化解釋嗎」.
6. **S9:1200** — user: 「prose-trust 的意思是？」 — term had been used
   twice without first-use definition (violates plain-language-first).
7. **S9:1205→1212** — follow-up 「現在是怎樣做到 hard gate 的啊？」 forces
   the assistant to re-check the repo and confess (S9:1212): 「我前面那張
   表把 validate_spec_output 標成 🔒 是過度簡化」 — the visual it produced
   under pressure was **factually wrong**.

The user's own summary statement (to Gemini, pasted at **S10:1193**):
> 「我目前就在用這套 loom-* skill 開發 但我覺得目前還是有很多需要人工介入
> 的部分，尤其是介面測試與一些**我其實看不太懂的技術選擇**。」

And today's framing (monkey-skills/1ca8bd0d-…jsonl:12): 「我一直想要改善
loom-* …用更簡單易懂的方式溝通說明複雜的程式實作選擇，甚至是善用各種視覺
化方法（表格 ASCII Graph…）但是好像都不是很有效」.

Institutionalized workaround evidence: the user's own handoff prompts now
carry a standing language directive — komado-Viewfinder
814cc765:11 and 44fb6175:11 open with 「請以繁體中文（zh-Hant）回覆本
session（subagent/工具輸出維持原語言，surfacing 前在地化）」; S2:11 pins
`conversation_language(繁體中文)` from handoff frontmatter. Users don't
write standing reminders for failures that don't recur.

Related-but-different hit: S11:433 「為何關鍵字還是用中文啊？」 is about
artifact keyword language policy, not conversation comms — excluded.

---

## B. 主導性 failure patterns（transcript-grounded）

### B1. TDD/execution 階段整段滑成英文（loom-code SKILL.md 的語言外洩）
Once `tdd-iron-law` / `writing-plans` (English skill bodies) load, the
assistant's user-visible narration flips to English for dozens of turns,
in conversations the user runs in 繁中.

- **S6** (reading-list, user turns all 中文: 「好，做 openai-compat 多實
  例 HA」S6:68, 「照抄 ytss 的就好」S6:166): **34 of 48 substantive
  assistant turns (70%) are English**, e.g. S6:235 "RED confirmed
  (compile failure, per Martin's Second Law). Now make it GREEN"; S6:311
  "All GREEN. Now update `config.example.yaml`…". It flips back to 中文
  only at the review report (S6:375).
- **S3** (komado-Refs): 29/147 turns (19%) English mid-session — S3:157
  "Now let me look at `ImageSourceRouter`…", S3:440 "Session attached.
  Screenshot the initial state:".
- **S7:169** "Now I'll write the brief." — single-line English turns
  sprinkled through a 中文 brainstorm.
Mechanism: loom-code skill/agent text is English; its vocabulary and
sentence frames leak straight into the conversation channel, violating
the CLAUDE.md conversation-language contract.

### B2. Skill-internal jargon 未翻譯直通使用者（verdict/工作流術語）
Skill-internal terms reach the user with no plain-language framing:
PASS_WITH_NOTES / NEEDS_REVISION / RED→GREEN / Wave 1 / seam test /
atomic 提交紀律 / writer≠judge / prose-trust / harness / drift gate.

- **S9:1159** status report to user: 「#1 router 瘦身…Continuous-mode 區塊
  下放 references/continuous-mode.md,body 148→112 行 / ~3,500-4,150 →
  ~1,800 token」 + S9:1150 「8 條 STOP row byte-identical 保留、
  never-auto-merge / crutch line / R6 freeze 全在」 — internal invariant
  names dumped raw; two turns later the user asks for a visual (A5) and a
  definition (A6).
- **S1:470** 「T3 判定:spec PASS + 品質 PASS_WITH_NOTES → 任務完成…(平行
  wave 的原子提交紀律)」— verdict algebra, never explained.
- **S7:180** checkpoint sign-off asks the user to approve based on
  「seam test 斷言精確 dict…dangling / malformed tag…@req 綁定」 →
  three turns later A1 (「我還是不知道…」).
- Counter-example proving it's capability, not ability: S1:156 defines
  torn read in one plain clause (「指一條執行緒讀到只寫了一半的多欄位結
  構」); S7:222's 煙霧偵測器 metaphor. Plain mode exists — it fires only
  AFTER user pushback.

### B3. Verdict-dump / mechanism-first briefing at decision points
Decision asks lead with internal mechanism or arrive as an unbriefed
menu; stakes surface only inside the option text, or after interruption.

- **S1:185** AskUserQuestion fires directly after brainstorming loads —
  no chat-visible brief between skill load (S1:181) and the menu. The
  question references 「分 5 批(PR)…第 5 批會改變使用者可感知的同步行為」
  but the 5-batch structure was never enumerated in chat (the research
  report S1:156 lists findings, not batches).
- **S5:101→106**: assistant fires an options menu; user interrupts
  ([Request interrupted] S5:104) — 「請先評估 還不要實作」. The menu came
  before the evaluation the user wanted.
- **S8:1290**: 8 review findings + 2 BLOCKERs in one wall → user must
  impose pacing themselves (「一個一個來 請先用視覺化說明」S8:1294).
- **S2:592/595**: assistant refers to P2/P3 batch labels; user must ask
  「P2/P3 有哪些東西？」 — internal labels outlive the user's memory of
  them (the plain re-explanation at S2:600 is good, but reactive).

### B4. Visuals: promised in the institution, rare at the actual forks
CLAUDE.md promises tables/ASCII 「when it beats prose」; in practice, at
AskUserQuestion decision points across the 9 quantified sessions:
**54 asks, only 21 (39%) had any table/ASCII in the ask turn or the two
assistant turns before it — and in the two real-app komado projects it
is 1 of 11 (9%)** (S1: 0/4, S2: 1/3, S3: 0/2, S4: 0/2). The higher meta-
session rates (S8 6/16, S9 8/11) are inflated by the user explicitly
demanding visuals (A2, A4, A5). Where visuals DID appear unprompted they
were in research REPORTS (S1:156 pipeline ASCII, S1:282 test-coverage
table, S5 config YAML preview) — i.e., visuals decorate conclusions but
skip the fork the user must decide.
Quality failure inside the visuals themselves: English labels (A3),
factually-wrong 🔒 marking (A7), and eyeballed alignment before the
ascii-graph tool was adopted (S7:193 finally routes to width-aware tool
only after the user's 中文-labels request).

### B5. SDD 執行期把使用者當旁觀的 orchestrator console
During S1's SDD run, the visible conversation becomes a stream of
teammate idle_notifications + assistant micro-status in orchestration
dialect: S1:366 「Wave 1 三個 implementer…各自用獨立的 DerivedData 跑測試
避免互撞」, S1:404 「等待中:T1、T4 實作,T3 兩路審查」, S1:486 「T3 已提交
(fcced1e)。T1 的 spec 審查也 PASS…」. No rollup in user terms (「三個資料
競爭修了幾個、還剩什麼要你決定」). The user goes silent for ~200 lines —
the only turns available to them are watching internal traffic.

---

## C. 對照組（做得好的案例 — 失敗不是全面的）

- **S5 (youtube-scraper) 全程優**: plain stakes-first answers
  (S5:241 「純粹是『設定 key 要叫什麼名字』的命名選擇，沒有任何功能差
  異」), tables at 5/10 asks, EN turns 10%.
- **S3 root-cause explanation** (S3:79) is conclusion-first plain 中文
  with code evidence; the same session still leaks English turns (B1).
- **S6:375/390**: review verdict explicitly 「轉成白話回報」 — PASS_WITH_NOTES
  translated into consequences (幽靈預設值 explanation). Recent sessions
  (07-04+) show the review-report seam improved; the execution-narration
  and decision-brief seams did not.

## D. 侷限（誠實聲明）

- 「firing-ab」與 scratchpad dirs (159 of 214 hits) are synthetic A/B
  harness runs — excluded; conclusions rest on the 11 real sessions above.
- Turn-level language stats use a ≥40-char CJK heuristic; short 中文
  confirmations are uncounted (biases EN% down, not up).
- The 3-turn look-back window for "visual before ask" is generous; the
  9% real-app figure is if anything an overcount.
- Zero hits for 講人話/太複雜/看攏無 as literal strings — the user's
  feedback style is polite re-asking (A1, A6) and explicit requests
  (A2, A4, A5), not complaints; absence of「講人話」strings ≠ absence of
  friction.
