# NBS New SPA API — Indicator Catalog

**Purpose**: Dev-facing reference for the reverse-engineered `data.stats.gov.cn`
new-version SPA API (`/dg/website/publicrelease/web/external/*`). Separate
from the user-facing `indicators-*.md` files which describe our 28 curated
china-macro presets.

This catalog exists so that future work (e.g. a supplementary `nbs_client.py`
to supersede stale akshare mirrors) can proceed without re-running tree
discovery against the NBS WAF.

**Discovery date**: 2026-04-18
**Client IP observed**: Chunghwa Telecom HiNet (Taiwan). All endpoints below
reachable from TW IP.

---

## 1. API endpoints

All under `https://data.stats.gov.cn/dg/website/publicrelease/web/external/`.

| Method | Path | Purpose |
|---|---|---|
| GET | `../page.html` (root homepage) | Establishes `JSESSIONID` cookie (required) |
| GET | `queryAllPblIbs?type={month,session,year}` | 33 "快速查询专题报表" quick-access items |
| GET | `new/queryIndexTreeAsync?pid=<uuid>&code={1,2,3}` | Walk indicator tree (1=月度, 2=季度, 3=年度) |
| GET | `new/queryIndicatorsByCid?cid=<uuid>&dt=&name=` | List indicator IDs for a leaf table |
| POST | `getEsDataByCidAndDt` | Fetch actual numeric values |

### Session setup

```bash
curl -c jar.txt "https://data.stats.gov.cn/dg/website/page.html" -H 'User-Agent: Mozilla/5.0 Chrome/147'
# Sets JSESSIONID. Reuse `-b jar.txt` on all subsequent API calls.
```

### queryIndexTreeAsync (tree walker)

```bash
curl -b jar.txt "https://data.stats.gov.cn/dg/website/publicrelease/web/external/new/queryIndexTreeAsync?pid=&code=1" \
  -H 'Accept: application/json' -H 'User-Agent: Mozilla/5.0 Chrome/147'
# pid="" returns the root singleton for that frequency (code=1|2|3).
# Recurse with pid=<_id from response> to walk down.
# Stop when isLeaf=true.
```

### queryAllPblIbs (quick-access reports — NOT full catalog)

```bash
curl -b jar.txt "https://data.stats.gov.cn/dg/website/publicrelease/web/external/queryAllPblIbs?type=month"
# Returns 11 curated monthly reports (industrial, retail, FAI, real estate...).
# type=session → 11 quarterly. type=year → 11 yearly.
# Total 33 items; superset is queryIndexTreeAsync.
```

### getEsDataByCidAndDt (fetch values)

```bash
curl -b jar.txt -X POST "https://data.stats.gov.cn/dg/website/publicrelease/web/external/getEsDataByCidAndDt" \
  -H 'Content-Type: application/json;charset=UTF-8' \
  -d '{
    "cid": "5c7452825c7c4dcba391db5ca7f335c5",
    "indicatorIds": ["53180dfb9c14411ba4b762307c85920c"],
    "daCatalogId": "",
    "das": [{"text":"全国","value":"000000000000"}],
    "showType": "1",
    "dts": ["202401MM-202603MM"],
    "rootId": "fc982599aa684be7969d7b90b1bd0e84"
  }'
```

Payload fields:
- **cid**: leaf-table catalog ID (from `queryIndexTreeAsync` isLeaf=true entries)
- **indicatorIds**: list of indicator UUIDs within the cid (from `queryIndicatorsByCid`)
- **das**: region selector; `[{"text":"全国","value":"000000000000"}]` = national
- **showType**: "1" for normal numeric values
- **dts**: array of date-range strings. Period suffix: `MM` monthly, `SS` quarterly, `YY` yearly.
  See §1a below for the full accepted syntax and the web UI shortcuts that do NOT transit to the API.
- **rootId**: root of the frequency tree (see §2)

Response `data[].values[].value` is the numeric value (string, e.g. `"101.0"`).
`data[].code` is the period code (e.g. `"202603MM"`).

### 1a. `dts` syntax — what the API actually accepts

Verified empirically on `5c7452825c7c4dcba391db5ca7f335c5` (CPI 2026-) on 2026-04-18.

| Form | Example | Works? | Notes |
|---|---|---|---|
| Single closed range | `"202401MM-202603MM"` | ✅ | Canonical. Every period in the interval is returned (values may be empty if outside the indicator's validity window). |
| Multi-range array | `["202301MM-202312MM","202601MM-202603MM"]` | ✅ | Each element is an independent closed range. Non-contiguous ranges are **fully supported** — one POST can fetch 2023 annual + 2026 Q1 in 15 periods. |
| Quarterly range | `"202301SS-202601SS"` | ✅ | Suffix `SS`. |
| Yearly range | `"2020YY-2025YY"` | ✅ | Suffix `YY`. |
| `"LATEST10"` / `"LAST5"` / `"last99"` | any | ❌ | **UI-only shortcuts.** The web textbox accepts them (the placeholder says `last10`), but the SPA's JS translates them client-side to an explicit range before POSTing. Inherited-looking behaviour from `mbk-dev/nbsc`'s old `easyquery.htm` is gone on the new API. |
| Open-ended range | `"2023-"` / `"-202012MM"` | ❌ | Empty response. API requires both ends. |
| Comma-delimited discrete periods | `"202301MM,202306MM,202312MM"` | ❌ | Parsed as one opaque code, returns one garbage row. The UI textbox hint `201201,201205` is also client-side-only. |

**Replicating `last99` in your own client**:

```python
from datetime import date
from dateutil.relativedelta import relativedelta

# last N monthly periods ending at today's year-month
today = date.today()
start = today - relativedelta(months=N - 1)
dts = [f"{start:%Y%m}MM-{today:%Y%m}MM"]

# last N quarterly periods
q_today = (today.month - 1) // 3 + 1
start_y  = today.year - ((N - q_today) // 4)
start_q  = ((q_today - N) % 4) or 4
dts = [f"{start_y}{start_q:02}SS-{today.year}{q_today:02}SS"]
```

**Time-window "fences" on indicator IDs**:

Each leaf catalog (`cid`) bundles multiple indicator IDs, and a given indicator ID is
only valid for its declared year window. For CPI the four IDs are
`(2026-)`, `(2021-2025)`, `(2016-2020)`, and `(-2015)`. A request with
`dts=["201001MM-202603MM"]` and only the 2026+ indicator ID will return 195
period rows but values for only 3 periods (2026-01/02/03). To stitch full
history, pass all four sibling indicator IDs — the API will populate each
period with whichever ID covers that window.

---

## 2. Root catalog IDs

| Frequency | code | root _id |
|---|---|---|
| Monthly (月度) | 1 | `fc982599aa684be7969d7b90b1bd0e84` |
| Quarterly (季度) | 2 | `a94b8b7365a94874968cabbe392cf679` |
| Yearly (年度) | 3 | `884c062607104a91967b22742537f44f` |

---

## 3. WAF behaviour (critical for client design)

- Low-volume GETs / POSTs (≤ 20 / session) are 200 OK from TW/US IPs.
- Bulk tree walks (≥ 100 sequential requests) trip the **WZWS** JS anti-bot
  challenge. Response body becomes HTML (Javascript obfuscated) instead of
  JSON; `success:true` disappears.
- Observed cooldown: **~10–30 minutes** after a block.
- Only the NEW `/dg/website/...` API is reachable from TW. The legacy
  `/english/easyquery.htm` (the endpoint used by `mbk-dev/nbsc`) is blocked
  at the WAF URL-ACL layer from non-mainland IPs — always 403.

**Client design implications**:
1. Pin `(cid, indicator_id[], root_id)` STATICALLY per preset. Do not
   rediscover the tree at runtime.
2. Throttle requests to ≤ 1 per second.
3. Always prime the session with the homepage GET before any API call.
4. Detect WAF lock by checking response body starts with `<`; back off 30s+ on hit.

---

## 4. Top-level category IDs

### Monthly (code=1)

| Category | _id | Leaves (≤depth 4) |
|---|---|---|
| 价格指数 | `3c9c459384c74f578f3541b2198aac70` | 178 |
| 工业 | `f484811113a5470892cb52b00c2b35c2` | 334 |
| 能源 | `a8ac252ded0b45289261c98468e60234` | 22 |
| 固定资产投资 (不含农户) | `c3079d221d2943888b87d47c28abf64e` | 11 |
| 服务业生产指数 | `f58d0d6448f644ba9ed295b2681e393e` | 1 |
| 城镇调查失业率 | `e69d8b62991649d4b278e0445bcc0cd0` | 1 |
| 房地产 | `a7d36f218969426daaeeddd1c6c5823a` | 14 |
| 国内贸易 | `3913ce1309d04eb1bdf7d7b622b1d07c` | 24 |
| 对外经济 | `73f0f0fafb31475ab48a309cc25dedd9` | 2 |
| 交通运输 | `54a7826037284f8d8905120290b80192` | 7 |
| 邮电通信 | `8ce414a4ef94420db44448e5e3dc4d49` | 5 |
| 采购经理指数 | `8f108f3406d7436b82498390d9e08da7` | 3 |
| 财政 | `3a35da71e2be4af39a8c3acd45f03eb3` | 2 |
| 金融 | `4fb2f4d836a24c1a824a26e2b04b7009` | 1 |
| **Total** | — | **605** |

### Quarterly (code=2)

| Category | _id | Leaves |
|---|---|---|
| 国民经济核算 | `1b1ce0cfd03646dc9e15103ea4c570f6` | 6 |
| 农业 | `21005792d2164ea780549452f3ed7300` | 1 |
| 工业 | `ddc4756a96c04ed78699233fd2ba5a1a` | 80 |
| 建筑业 | `20244d5f11e14fe2a16dd11bece22379` | 10 |
| 人民生活 | `85ee7ccd4212489d9d3b774c8558e274` | 7 |
| 价格指数 | `1da3b0f4028c4a89a73f51a2d038c243` | 5 |
| 国内贸易 | `d9ac9f4f5f834da8ae7cca1c4cac8b1a` | 1 |
| 文化 | `62cb069607b642e6910a4e4230e119fa` | 6 |
| **Total** | — | **116** |

### Yearly (code=3)

| Category | _id | Leaves |
|---|---|---|
| 综合 | `71d41888d5a44bb2a67402ef4e60003e` | 25 |
| 国民经济核算 | `bf4fb427305c4d7ba5a00562c8a4a621` | 53 |
| 人口 | `040faf60f9b64535957e242e62a18a85` | 25 |
| 就业人员和工资 | `103e7c6841bf4176b43bd6d5682badb9` | 29 |
| 固定资产投资和房地产 | `1d83863d4983470f834cb2e569bb2ad1` | 46 |
| 对外经济贸易 | `64784aef51644d03a9224fd35ac9f064` | 101 |
| 能源 | `2dc0c279011e4d2e9f24f7d42f1d4af4` | 37 |
| 财政 | `9637adcedfa846f1b8c3d625331fd274` | 15 |
| 价格指数 | `aefb8690a49146f8b4745a383be5c29a` | 84 |
| 人民生活 | `f7a08c16a68744839aaf863edc80c9b4` | 18 |
| 城市概况 | `cc3c140d012c425eba5c02f9f4bb11a6` | 10 |
| 资源和环境 | `eadfba08f8ec4511bf05d5d88738b26b` | 20 |
| 农业 | `c2f3466f871e400dbf96ee4ce322f236` | 32 |
| 工业 | `d2053699ac254437aa5a6cb802e11c3c` | 747 |
| 建筑业 | `a4b72fb9ab4a4a598d6e539b07298513` | 42 |
| 运输和邮电 | `79c5a96c74a14d7ebd3b17d21639a196` | 57 |
| 社会消费品零售总额 | `d5b51c4a56d646b3b3f00f2c9e31a217` | 0 |
| 批发和零售业 | `abb115f16fde4032aae7e3d160e50290` | 123 |
| 住宿和餐饮业 | `90490a6ff9564fc8affb819d6ad544a0` | 71 |
| 旅游业 | `b7ec837309f34a828e18710e04367da6` | 5 |
| 金融业 | `b85b930279a040688e03158e2ee3d60d` | 19 |
| 教育 | `7d6e10dffddf42a6821120b0b5cb93cd` | 86 |
| 科技 | `506ef89a377e4beb96533b3659955ab5` | 200 |
| 卫生 | `5de9e4e0a1b647d4a83e9070059edeb6` | 37 |
| 社会服务 | `47ef1714b056454a949c9c94f366da84` | 17 |
| 文化 | `7a24131adc1e42be8f28d03b77da2414` | 173 |
| 体育 | `791fa7f2e9a64f1685e2c2c1f3b7b625` | 16 |
| 公共管理、社会保障及其他 | `aff45f94c0b2438c8aba5528e56e9bce` | 99 |
| **Total** | — | **2187** |

**Grand total: ~2,900 leaf indicators (605 monthly + 116 quarterly + 2187 yearly).**

---

## 5. Mapping — current akshare presets ↔ NBS subtrees

Which of our 19 existing `akshare_client.py` presets have a direct NBS path.
(Down from 21 after Caixin PMI presets were removed 2026-04-18 for staleness.)
Stale akshare mirrors are the priority upgrade candidates for any future
`nbs_client.py`.

| akshare preset | NBS path | NBS available | akshare staleness |
|---|---|---|---|
| `cpi-yoy` | 月度→价格指数→居民消费 (上年同月=100) | ✅ | ~47d (fresh) |
| `ppi-yoy` | 月度→价格指数→工业生产者出厂价格分类指数 | ✅ | ~47d (fresh) |
| `gdp-yoy` | 季度→国民经济核算→分季国内生产总值指数 | ✅ | ~106d (fresh) |
| `industrial-yoy` | 月度→工业→工业增加值增速 | ✅ | **~245d (stale)** |
| `retail-yoy` | 月度→国内贸易→社会消费品零售总额 | ✅ | ~47d (fresh) |
| `exports-yoy` | 月度→对外经济→货物进出口总额 | ✅ | **~253d (stale)** |
| `imports-yoy` | (same table, different column) | ✅ | **~253d (stale)** |
| `trade-balance` | (same table, different column) | ✅ | **~253d (stale)** |
| `urban-unemployment` | 月度→城镇调查失业率 | ✅ | ~75d (fresh) |
| `pmi-manufacturing` | 月度→采购经理指数→制造业PMI | ✅ | ~47d (fresh) |
| `pmi-non-manufacturing` | 月度→采购经理指数→非制造业PMI | ✅ | ~47d (fresh) |
| `lpr-1y`, `lpr-5y` | (PBOC — not in NBS monthly) | ❌ | fresh (chinamoney) |
| `rrr-major` | (PBOC — not in NBS) | ❌ | event-driven |
| `shibor-3m` | (SHIBOR — not in NBS) | ❌ | same-day (shibor.org) |
| `m2-yoy`, `m1-yoy` | 月度→金融→货币供应量 | ✅ | ~47d (fresh) |
| `shrzgm` | (PBOC 社融 — not in NBS) | ❌ | ~137d (fresh enough) |
| `new-loans` | (PBOC — not in NBS) | ❌ | ~47d (fresh) |

**Priority upgrade candidates** (NBS has it AND akshare is stale ≥ 200d):
`industrial-yoy`, `exports-yoy`, `imports-yoy`, `trade-balance`.

### New presets NBS makes possible (not in current akshare client)

- **综合PMI产出指数** (Composite PMI Output, 月度→采购经理指数)
- **服务业生产指数** (Services Production Index, 月度→服务业生产指数)
- **限上单位商品零售类值** — 16 detailed retail sub-categories
  (汽车, 家电, 服装, 化妆品, 金银珠宝, 中西药品, 建筑材料 … 月度→国内贸易)
- **房地产销售面积/销售额** — by property type (住宅, 办公, 商业, 月度→房地产, 14 tables)
- **固定资产投资分行业** (11 FAI breakdowns: 增速, 分行业, 民间, 资金来源 …)

---

## 6. CPI worked example (verified 2026-04-18)

Request:
```json
POST /dg/website/publicrelease/web/external/getEsDataByCidAndDt
{
  "cid":"5c7452825c7c4dcba391db5ca7f335c5",
  "indicatorIds":["53180dfb9c14411ba4b762307c85920c"],
  "daCatalogId":"",
  "das":[{"text":"全国","value":"000000000000"}],
  "showType":"1",
  "dts":["202401MM-202603MM"],
  "rootId":"fc982599aa684be7969d7b90b1bd0e84"
}
```

Response (abbreviated — shows 3 periods with values, older periods empty
because indicator ID `53180dfb9c14411ba4b762307c85920c` belongs to the
2026+ series; earlier years have distinct indicator IDs under the same cid):

```json
{
  "data": [
    {"code":"202603MM","values":[{"i_showname":"居民消费价格指数 (上年同月=100)","value":"101.0","du_name":"%"}]},
    {"code":"202602MM","values":[{"value":"101.3"}]},
    {"code":"202601MM","values":[{"value":"100.2"}]},
    {"code":"202512MM","values":[]},
    ...
  ],
  "success": true
}
```

**Series ID segmentation**: Same indicator spans multiple `_id`s across
time windows (observed: `(2026-)`, `(2021-2025)`, `(2016-2020)`, `(-2015)`).
To fetch full history, you must stitch 4 requests. This is analogous to
`mbk-dev/nbsc`'s legacy `A01030101 / A01030201 / A01030G01` pattern.

---

## 7. TODO for future implementation

- [ ] Write `nbs_client.py` covering at least the 4 priority upgrade presets
  (`industrial-yoy`, `exports-yoy`, `imports-yoy`, `trade-balance`).
- [ ] Map the 4 CPI time-window indicator IDs for full history stitching.
- [ ] Decide hybrid vs replace: keep akshare for PBOC/Caixin (no NBS source),
  NBS for the priority 4.
- [ ] Cache indicator IDs statically — do not re-walk at runtime.

---

## 8. Full catalogs (trees + indicators)

### 8a. Tree catalogs (cid only)

- `nbs-tree-monthly.md` (14 categories, 605 leaves)
- `nbs-tree-quarterly.md` (8 categories, 116 leaves)
- `nbs-tree-yearly.md` (28 categories, 2187 leaves)

Each is a nested markdown bullet list. 📁 = folder, 📄 = leaf table;
each node carries its UUID in backticks. Leaf UUID is the `cid` for
`POST getEsDataByCidAndDt`.

### 8b. Indicator catalogs (cid → indicatorIds[])

Captured 2026-04-18 via `queryIndicatorsByCid?cid=<leaf>` against every
leaf in §8a:

- `nbs-indicators-monthly.{json,md}` (605 cids, ~15k indicators)
- `nbs-indicators-quarterly.{json,md}` (116 cids, ~3k indicators)
- `nbs-indicators-yearly.{json,md}` (2187 cids, ~57k indicators)

JSON is machine-readable (`{cid → {path, indicators[], ...}}`); MD is
human-readable with per-category TOC + per-leaf indicator tables.
Together with §8a these give everything a hardcoded
`nbs_client.py` needs.

**Capture stats**: 2908 cids / 75,719 indicators / 0 WAF events (under
NordVPN + 0.5s throttle + exponential backoff).

Generation scripts are in `tools/` — see `tools/README.md` for when
to re-run (typically every ~5 years at NBS base-period revisions).

