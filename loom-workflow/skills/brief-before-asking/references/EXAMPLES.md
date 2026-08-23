# Brief Before Asking — Examples

Three side-by-side examples covering: low-complexity fork, medium-complexity fork, and the **Mode C demo** for "long explanation but user can't follow."

## Example 1 — Race Condition (Mode A: Proactive)

### ❌ Bad briefing (typical agent default)

> I noticed `BookingService.confirm()` might have a race condition under high concurrency. Should we add a lock?

**Missing**:
- Which line? How do two threads interleave?
- "Might have" — how likely? Seen in production?
- Lock options (DB-level / app-level / optimistic / serialization)? Each one's throughput impact?
- What if we don't fix it? Data corruption severity?
- Agent's own lean and reasoning?

### ✅ Good briefing (Mode A — Proactive)

> **Mental Model**
>
> This is the "seat reservation" confirmation step in booking flow. When a user clicks "Confirm," we (1) check the seat is available, then (2) write the booking. If two users click at the same time on the same seat, both may see it as available and both bookings get written — meaning two people get the same seat.
>
> **Situation**
> `BookingService.confirm()` lives in `services/booking.ts:88-142`. Flow: SELECT from `seats` (line 92) → INSERT into `bookings` (line 121). No transaction wrapping both. Stress test (50 concurrent requests, same event): reproduced double-booking 3 times.
>
> **Why this is a fork**
> Customer support reported 2 production double-booking cases last week. But the lock choice is non-trivial: app-level locks fail across multi-instance deploys; DB-level locks cost throughput; optimistic locking requires schema change. Picking wrong has real reversal cost.
>
> **Options**
> - **A. DB row-level lock (`SELECT ... FOR UPDATE`)**: ~10 lines change in confirm(). Throughput cost: 50 rps drops to ~35 rps on contested seats. Reversible.
> - **B. Optimistic lock (version column + retry)**: Schema change (add `seats.version` column, ~5 line migration); confirm() change ~25 lines + retry logic. Throughput preserved; retry cost spikes under contention. Schema change is harder to reverse.
> - **C. Redis distributed lock**: New dependency. ~15 lines in confirm() + Redis Sentinel for HA. Works across multi-instance deploys. Adds a failure mode (Redis unavailable).
>
> **My take**
> Lean B (optimistic lock). Reasoning: (1) contention on same seat is rare (only matters during launch of hot events, ~few times per quarter); (2) throughput is critical at our scale (>1k rps baseline); (3) team already uses optimistic locking pattern in InventoryService, low ramp-up. But if you're planning to roll out simultaneous-event flash sales (>100 rps contention per seat), I'd switch to A — retries would thrash under that load.
>
> **Open ends**
> - I don't know: flash-sale roadmap for next 2 quarters
> - Would flip my answer: if booking volume per second per seat exceeds ~20, switch to A
> - Need your call: schema-change tolerance — does the seats table have downstream consumers that would break on version column addition?

User can decide in ~90 seconds.

---

## Example 2 — Database Index (Mode B: Reactive on short question)

### Initial agent question (bad)

> The `getUserOrders` query looks slow. Want me to add an index?

### User reaction

> 什麼意思？

### Agent response (Mode B triggered)

> Going back to my earlier "add index" question, here's the full picture:
>
> **Mental Model**
>
> Whenever a user opens their "My Orders" page in the app, the backend runs a query to fetch that user's order history. Right now, when this user has many orders, the query is slow enough to hit our latency budget alert. The question is what technical move to make to speed it up.
>
> **Situation**
> Query is `getUserOrders` in `src/services/order/queries.ts:42-58`. LEFT JOINs `orders` (3.2M rows) / `shipments` (4.1M rows) / `users` (180K rows). EXPLAIN ANALYZE: full table scan on `orders.user_id`, cost 32k. Measured P95 ~850ms. Called from `/api/users/:id/orders` at ~120 rps.
>
> **Why this is a fork**
> Last week P99 climbed from 1.2s to 2.4s, tripping SLO alert. Need to fix this sprint. But we already have 47 indexes on `orders` — adding another isn't free (slower writes, more storage). "What index" matters, not just "do we add one."
>
> **Options**
> - **A. Single-column `idx_orders_user_id`**: ~180MB storage. INSERT cost +20% (2ms → 2.4ms). P95 850ms → ~80ms. Low risk, reversible.
> - **B. Composite covering `idx_orders_user_id_created_at`**: ~320MB storage. INSERT cost +40% (2ms → 2.8ms). P95 850ms → ~25ms (avoids heap fetch). If query pattern shifts later, may become dead index.
> - **C. Materialized view + scheduled refresh**: P95 ~10ms (pure read). Data staleness 5-10 min. Adds operational complexity (refresh scheduler, stale-view monitoring).
>
> **My take**
> Lean B (composite covering). Reasoning: (1) all callers already sort by `created_at` (verified in code), so covering pays off; (2) write rate on `orders` is ~50 rps, well within +40% headroom; (3) reversible (drop index) with no schema change. But if you're about to run a big historical-data import, switch to A to minimize write cost during import.
>
> **Open ends**
> - I don't know: any planned changes to read pattern over next 6 months
> - Would flip: if `created_at` ordering becomes optional (covering becomes wasted)
> - Need your value call: have you had bad experience with materialized views before? (affects whether C is on the table at all)
>
> ---
> **Restating my ask**: pick A, B, or C — or do you want me to spec out the materialized view path before deciding?

---

## Example 3 — Saga + Outbox (Mode C: Reactive on long explanation)

### Initial agent explanation (over-jargoned)

> We're using the saga pattern with eventual consistency via the outbox pattern. OrderService publishes domain events to Kafka, and InventoryService consumes via a consumer group with manual offset commits. We're seeing duplicate messages because the consumer crashes between processing and commit. The question is: do we add idempotency keys at the consumer level, or push them down to the domain aggregate?

### User reaction

> 太多術語，我跟不上

### Agent response (Mode C triggered — partial output, then pause)

> Let me step back and build the mental model first.
>
> **Mental Model**
>
> This is the "decrement inventory after order placed" async flow. After an order is written, we send a message to InventoryService telling it to decrement stock for the items ordered. Recently we found: the same message sometimes gets processed twice, so the same order decrements stock twice — meaning we sell items we don't have (oversells).
>
> If any of these terms in my previous turn were unfamiliar, ask and I'll expand:
>
> - **saga pattern**: a way to coordinate "multi-step transactions" that span across services
> - **outbox pattern**: a way to guarantee "writing to database" and "publishing a message" never end up with one succeeding and the other failing
> - **offset commit**: a "bookmark" in the message queue marking how far we've processed
> - **consumer group**: a way for multiple machines to share consumption of one message queue
>
> ---
>
> Does this mental model match what you understand? If yes, where would you like to drill in next:
> - **A. Why duplicate processing happens** (technical detail)
> - **B. Available solutions + my recommendation** (Options + My take)
> - **C. Expand one of the terms above**

### Why this works

- Agent did NOT dump the full 6-block briefing. The user already drowned in jargon once; dumping all 6 blocks would drown them again, even reordered.
- Agent surfaced **only the Mental Model + jargon dictionary** for terms already used.
- Agent **paused and asked the user to choose direction**. The user is now in control of how to drill.
- The 4 expanded glossary definitions are 1-sentence plain-language descriptions — each addresses "what does this term let me do" rather than "how does this term work."

This is the structurally different shape of Mode C.

---

## Real-World Cases (mined from actual sessions)

These four are real cases pulled from session logs — unedited except for trimming. Cases 1-3 are before/after recovery pairs covering Modes B, C, and D across three domains (UX, research pipeline, data/SQL); Case 4 has a different shape — a guard *miss* narrative whose fix shipped with the version that added it. Real cases beat synthetic ones: the recovery turns show what *landing the briefing* actually looks like in messy, domain-specific reality.

### Real Case 1 — Eval design (Mode C: lost in jargon)

**The bad ask** — agent dumped a full eval-design table, then asked to proceed:
> | **Arm A** | sonnet 單趟 synthesis（含可選 meta-mode prepend）|
> | **Arm B** | A 的 synthesis → opus 異質 skeptic pass 對著 confirmed-claims 去 falsify |
> | **反同模型膨脹** | generator=sonnet vs judge=opus … recall 可能略樂觀 |
> … base-rate / recall / precision / materiality / Build 門檻 …
> 要我**就照這個設計跑**嗎？

**User:** 用白話文解釋

**The recovery** — a plain-language restate that is, in fact, a full briefing in disguise:
> 白話版——我要測什麼、為什麼。
> **現在的情況**：研究報告產生器最後一步是「把驗證過的資料整理成一篇報告」… **這一步只做一次，沒人回頭檢查它整理得對不對。**
> 我選的「缺口 1」就是想補一個**回頭挑毛病的人**。
> **但我不急著做，先測一件事**：強的 AI 模型搞不好自己整理就夠好了…那個「挑毛病的人」就是多餘的。
> **實驗怎麼做**：**甲組**（照現在的方式整理）／**乙組**（整理完再請另一個 AI 挑毛病）／**裁判**（第三個 AI，換一個牌子，避免自己幫自己打分）。
> **為什麼要這樣繞**：紀律是「先用證據證明值得做，再動手」… 我不想花力氣做一個 AI 本來就會的東西。

**Why it works:** The recovery is a textbook briefing — Mental Model (一步只做一次、沒人檢查) → why it matters (整理可能藏矛盾／標錯信心) → options in plain words (甲/乙/裁判, not Arm A/B/judge) → My take + stakes (為什麼要這樣繞). Same decision, opposite legibility.

### Real Case 2 — text-to-SQL knowledge layer (Mode D: stakes didn't land)

**The bad ask** — a leverage table of pp-deltas, with no plain definition of the core term:
> | 關係/join-path 圖 | +39〜+51pp（複雜多表）| ✅ 已有、最強資產 |
> | in-domain gold 問題→SQL 範例 | +44.9pp（真實 KaggleDBQA）| ❌ Gap B = 第一優先 |
> **結論**：最高 ROI 不是 profiling，而是把 syntheses/ 演化成「問題→SQL gold 範例庫」…

**User** — understood the words, not the point; supplied the missing definition themselves:
> 我想確定一下 我們現在說的 text to SQL 的 text 是商業邏輯問題 而不是單純的 SQL 統計的白話文 對嗎？

**The recovery** — lead with the distinction that makes the whole thing matter:
> 對，而且這個區分正是**整個設計的存在理由**。
> | | 白話統計（直接對 schema）| 商業邏輯問題（要懂業務）|
> | 例 | 「昨天幾筆訂單」| 「這季 churn 多少」「哪些活躍餐廳貢獻最多 GMV 成長」|
> | 沒知識層時 | 普通模型也能做 | **模型直接失敗**（BIRD「需外部知識」子集，最佳模型僅 40%）|

**Why it works:** The user was lost on *what the choice was even about* (stakes), not on a term's meaning — so a second pp-delta table would not have helped. The two-example contrast (昨天幾筆訂單 vs 這季 churn) made the stakes land in one line. This is Mode D, not C.

### Real Case 3 — keyboard-shortcut design (Mode B: didn't get the question)

**The bad ask** — three quick questions; Q3 was pure jargon with no grounding:
> 3. **Persistence 語意**：per-window-per-archive (跟 flip / rotate 同 L3 lock) vs cross-archive…

**User** — answered Q1/Q2 fine, hit the wall on Q3:
> Ａ。2. 是同一件事 3. 不太懂你的問題

**The recovery** — the agent's own question was malformed; retract, don't re-word:
> Q3 不懂的原因是：A 沒有獨立 state… 所以「persistence」這個問題其實**不適用**於 A — `currentIndex` 已經是唯一狀態。**問錯了、忘掉這條。**

**Why it works:** The fix wasn't to re-phrase the jargon — it was to notice the question was *invalid* (asking persistence of a stateless option). Sometimes "I don't get the question" means the question shouldn't have been asked. Mode B done right can end in retraction, not a glossary.

### Real Case 4 — check-questions after a completion report (guard miss, 2026-07-22)

**Context:** agent shipped a docs PR (a measurement baseline plus a
ride-along test fix), then reported completion with a mechanism-dense
card. The user sent two consecutive verification questions:

> 所以這只是修測試？

> 但是你沒動 skill 本身對吧

Each was answered **correctly and locally** — proportions clarified,
scope confirmed — but the agent never asked itself why the user needed
two rounds to rebuild the picture. On the next work turn the agent led
with branch-surgery jargon (cherry-pick, gate markers, a pre-existing
red test). Turn 3:

> 我覺得剛剛的溝通就有點讓我搞不清楚狀況了 這時候本來應該要由這個
> skill 來幫我用白話說明才是

**Four stacked misses:**
1. Check-questions were classified as pure factual queries ("When NOT
   to Use → just answer"), so the repeated-confusion guard's counter
   never incremented.
2. The confusion followed a *report*, not an ask — the reactive modes
   were framed around questions/explanations, and report-confusion fell
   into a jurisdiction seam.
3. Per-message-local correctness masked the failed framing: every
   individual answer was right, so nothing felt wrong.
4. The mechanical layer (ask-triage hook) only sees `AskUserQuestion`
   tool calls — prose-only turns are invisible to it.

**The fix shipped with this case:** check-questions now count toward
the repeated-confusion guard (SKILL.md §Mode Detection Heuristics +
the guard block), the guard's scope is explicitly "after ANY agent
output the user is parsing — including a completion report", and the
Pre-send check's two-line test runs before any briefing goes out.

---

## Anti-Patterns Demonstrated

These are concrete examples of common mistakes the skill must reject.

### Anti-Pattern 1 — Skipping Mental Model

```
**Situation**
`BookingService.confirm()` at services/booking.ts:88-142, no transaction
wrap, stress-test shows 3/50 double-booking under concurrent INSERT...
```

❌ User who doesn't already know what BookingService does is lost from sentence one.
Fix: prepend Mental Model.

### Anti-Pattern 2 — Mental Model Containing Jargon

```
**Mental Model**
OrderService has a race condition in the confirmation aggregate
under high contention, breaking idempotency guarantees.
```

❌ Three jargon terms (aggregate / race condition / idempotency) without definition. Mental Model is for plain English.
Fix: rewrite in business language.

### Anti-Pattern 3 — Fake Neutrality in My Take

```
**My take**
Both A and B are reasonable. Up to you which you prefer.
```

❌ Agent already read the code and investigated. Pretending neutrality is dishonest.
Fix: state an explicit lean with reasoning and conditional reversal.

### Anti-Pattern 4 — Unbalanced Options

```
**Options**
- **A. Add Redis cache**: it would simplify caching, improve perf,
  reduce DB load, scale better, and is the modern industry standard
  approach used by most large companies. Quantified: P95 latency
  expected to drop 65%, DB CPU drop ~30%, with new dependency on
  Redis Sentinel for HA, ~25 lines refactor in cache module.
- **B. Status quo**: keep current Caffeine.
```

❌ A is 5 lines of pro-positioning; B is 1 line. Even though both are technically listed, the framing is rigged.
Fix: equal depth — give B the same diff-level treatment.

### Anti-Pattern 5 — Mode C Trigger But Agent Dumps Full Briefing

```
User: 太多術語，我跟不上

Agent: [delivers full 6 blocks: Mental Model + Situation + Why + 
Options + My take + Open ends, all 600 words]
```

❌ User is drowning in jargon. Even a perfectly structured 6-block briefing is still 600 words and contains the same jargon. The user gets re-drowned, just in a tidier sequence.
Fix: Mode C delivers ONLY Mental Model + jargon glossary, then pauses.

### Anti-Pattern 6 — Bundled Forks

```
**Why this is a fork**
Should we (1) add a lock, (2) refactor the service, and (3) migrate
to event sourcing?
```

❌ Three independent forks. User has to disentangle them before answering. Each is a different decision with different stakes.
Fix: one briefing per fork. Sequence them.
