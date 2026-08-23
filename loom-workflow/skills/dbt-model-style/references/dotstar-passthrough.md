# The `.*` passthrough conciseness idiom

Companion reference for `dbt-model-style` SKILL.md §2.

The whole set is **SHOULD / MAY** — **be concise when you can; the moment any step doesn't work, fall back to explicit declaration. Don't force it.** Goal: less typing, less maintenance, and adding an upstream column means changing only one line in `final`.

> **Overriding premise**: `final` zero-logic (SKILL §1.2) is a MUST and outranks every preference here — **never push logic into `final` for the sake of `.*` conciseness.**

## 1. Single-source passthrough (most common, no JOIN)

When an intermediate CTE references **one** upstream, just `SOURCE_CTE.*` it through and add your derived columns. Always valid, most concise:

```sql
daily_with_week AS (
    SELECT DAILY_DIMENSION.*,                                  -- 上游全部欄位帶過
           DATE_TRUNC('week', data_date)::DATE AS week_start_date   -- 只加新衍生欄
    FROM DAILY_DIMENSION
)
```

Add an upstream column → `.*` carries it through here automatically → you only add one declaration line in `final`.

## 2. JOIN passthrough (the key scenario involving USING)

When a CTE **JOINs two sources** and you still want to pass `.*` down, the only obstacle is the **duplicate join-key column**. The preconditions are precise:

- **MUST use the right star**: `JOIN ... USING (key)` + an **unqualified `SELECT *`** → the join key appears **once** (merged column). This is what makes a clean passthrough possible.
- ⚠️ **`a.*, b.*` (qualified stars) do NOT dedupe even with `USING`** — `a.*` and `b.*` each include the key, so it appears twice and a downstream `*` collides. To dedupe via USING you must use an **unqualified `SELECT *`** (or `a.*` + only b's non-key columns).
- Contrast: `JOIN ... ON a.key = b.key` duplicates the key regardless of which star you use.

```sql
-- ✅ USING + 不限定 * → key 只一份，乾淨傳遞
joined AS (
    SELECT *
    FROM ORDERS
    LEFT JOIN CUSTOMERS USING (customer_id)
)

-- ❌ a.*, b.* → 即使 USING，customer_id 仍出現兩次
```

- **MAY — pre-rename so join keys share a name**: if the two sides' keys differ (`cust_id` vs `customer_id`), USING isn't possible; unify the names upstream first so USING becomes usable.

## 3. Renaming a few columns: explicit + `.*` together (MAY)

When you only need to rename a few columns, **don't declare the whole CTE column-by-column** (anti-pattern). Pull out the renamed columns explicitly + `.*` for the rest:

```sql
-- ✅ 偏好：少數 rename 顯式，其餘 .* 帶過
renamed AS (
    SELECT source_cte.amount AS amount_with_tax,   -- 只把要改名的挑出來：帶來源 CTE 限定詞 + AS
           source_cte.*                            -- 其餘全部 .*
    FROM source_cte
)
-- 副作用：amount（原名，來自 .*）與 amount_with_tax 會並存（同資料兩個名）→ 可接受，下游 final 挑正確那欄
-- 換來：宣告更短、更好維護
-- ⚠️ 顯式列的那一欄一定要「改名 (AS)」；若用原名又配 .*，會出現兩個同名欄而撞名

-- ❌ 反模式：為了改一個欄名，把 40 個欄全部顯式列出來
```

## 4. When to fall back to explicit declaration

Enumerate columns explicitly (don't force `.*`) when the conciseness is already gone — typically because **value columns collide or need renaming** (e.g. two sources both expose a `value` / `count` column, so they become `source_a_*` / `source_b_*`), or because **keys are differently named** so `USING` can't fold them. If any link in the chain `pre-rename → USING → unqualified .*` doesn't hold, fall back.

> **FULL OUTER JOIN + USING**: when both sides name the join key identically, `JOIN ... USING (key)` folds it into a single non-null column **even under `FULL OUTER JOIN`** — no manual `COALESCE(a.key, b.key)` needed. Hand-written key `COALESCE` is only for differently-named keys where `USING` is impossible. (Missing-side *value* columns may still need their own `COALESCE` — but that's calculation, out of scope for this style guide.)
