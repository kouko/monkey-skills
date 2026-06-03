/* ---
title:   區域 B 每日指標值（雙來源合併）
summary: 來源 A（本地）+ 來源 B（forecast）合併後的每日指標值，來源 B 優先 / 來源 A fallback
grain:   一列 = 一個 (metric_date, entity_id)
purpose: 區域 B 每日指標值的日/月趨勢、entity 別分析；每日營運報表的指標來源
keys:
  primary: [metric_date, entity_id]
  join:    [metric_date, entity_id]
related:
  - { table: int_dim__entity_dimension, join_on: entity_id, adds: entity 基本資料 / 地區 / 分類 }
  - { table: int_metric__daily_dimension, join_on: [metric_date, entity_id], adds: 其他每日指標 }
sources: [int_metric__daily_value__region_b__source_a, int_metric__daily_value__region_b__source_b__by_sub]
refresh: 日更 T+1（依上游 FDW 延遲）
---

來源 B-only 的 row 沒對到來源 A 是正常現象（來源 A 只攤本地）。
分析總值時用 daily_value（已 merge），勿用 from_source_a / from_source_b 的透明欄位相加。
*/


/* 重要業務規則 / 過濾邏輯（人讀，不進 table comment）
   * 來源 B 優先、來源 A fallback，單一單位為 canonical
   * source flag: 'source_b' | 'source_a'
   * 透明欄位 from_source_a / from_source_b 僅供對帳，勿相加
*/

{% if target.type=='redshift' %}
{{ config(
    materialized = 'table',
    sort = ['metric_date', 'entity_id'],
    tags = ['daily_value']
) }}
{% endif %}


/* == 取得來源 A 本地攤提（per (metric_date, entity_id)）======================= */
WITH SOURCE_A AS (
    SELECT *
    FROM {{ ref('int_metric__daily_value__region_b__source_a') }}
),


/* == 取得來源 B forecast 攤提（per (metric_date, entity_id, sub_id)）========== */
SOURCE_B AS (
    SELECT *
    FROM {{ ref('int_metric__daily_value__region_b__source_b__by_sub') }}
),


/* == 合併：來源 B 優先 / 來源 A fallback（所有業務邏輯都在這層）=============== */
merged AS (
    SELECT metric_date,                                                        -- USING 折成單欄
           entity_id,                                                          -- USING 折成單欄
           SOURCE_B.sub_id,                                                    -- 僅來源 B 有值

           COALESCE(SOURCE_B.daily_value, SOURCE_A.daily_value) AS daily_value,
           CASE WHEN SOURCE_B.metric_date IS NOT NULL
                THEN 'source_b'
                ELSE 'source_a'
           END                                                            AS source,

           SOURCE_A.daily_value AS daily_value__from_source_a,                 -- 對帳透明欄
           SOURCE_B.daily_value AS daily_value__from_source_b                  -- 對帳透明欄
    FROM SOURCE_A
    FULL OUTER JOIN SOURCE_B USING (metric_date, entity_id)
),


/* == 衍生指標月份（單來源 .* 傳遞 + 只加新欄）================================= */
with_month AS (
    SELECT merged.*,
           DATE_TRUNC('month', metric_date)::DATE AS metric_month
    FROM merged
),


/* == 最終輸出（零邏輯，只選欄 + 註解）======================================== */
final AS (
    SELECT -- === 識別欄位 ===
           metric_date,                          -- 指標日期（當地時間）
           entity_id,                            -- entity 識別
           sub_id,                               -- 子識別（僅 source='source_b' 有值）

           -- === 主要輸出 ===
           metric_month,                         -- [OUTPUT] 指標月份（metric_date 所屬月）
           daily_value,                          -- [OUTPUT] 當日值：來源 B 優先，
                                                 -- 無對應來源 B 時以來源 A fallback，
                                                 -- 兩來源皆以單一單位表示（canonical）
           source,                               -- [OUTPUT] 來源旗標 'source_b' | 'source_a'

           -- === 對帳 / 稽核欄位 ===
           daily_value__from_source_a,           -- [AUDIT] 同 row 來源 A 原始攤提（無則 NULL）
           daily_value__from_source_b            -- [AUDIT] 同 row 來源 B 原始攤提（無則 NULL）
    FROM with_month
)


SELECT * FROM final
