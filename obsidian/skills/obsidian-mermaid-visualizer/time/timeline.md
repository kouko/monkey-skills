# Timeline Diagram

Chronology — historical events, version history, project milestones, personal journey.

## When to use

**Best for**:
- Historical timelines (company history, technology evolution)
- Version release history
- Personal / career timelines
- Event sequencing where dependencies don't matter (unlike Gantt)
- Narrative progression with periods and events

**User query 關鍵字**: timeline / chronology / history / 時間軸 / 歷史 / 年表 / version history / career timeline / evolution

**Not for**: project schedules with dependencies (use `time/gantt.md`), process flows (use `flow/flowchart.md`), single-point events (use text).

## Canonical syntax

```mermaid
timeline
    title History of Programming Languages
    section 1950s
        1957 : FORTRAN
        1958 : LISP
        1959 : COBOL
    section 1970s
        1972 : C
        1972 : Smalltalk
        1978 : SQL
    section 1990s
        1991 : Python
        1995 : Java : JavaScript : PHP : Ruby
```

**Minimum required**:
- `timeline` directive
- At least one period or event line

**Syntax**: `period : event1 : event2 : event3` — events separated by colons on same period.

## Configuration options

### Sections

Group periods under thematic headers:

```mermaid
timeline
    title Company Milestones

    section Founding Era
        2015 : Incorporated
        2016 : First hire : Seed round

    section Growth Era
        2017 : Series A
        2018 : 100 customers : Opened SF office

    section Scale Era
        2020 : Series B
        2022 : IPO
```

### Single event per period

```mermaid
timeline
    title Annual events
    2020 : Event A
    2021 : Event B
    2022 : Event C
```

### Multiple events per period (colon-separated)

```mermaid
timeline
    2020 : Hire CEO : Hire CTO : Launch v1
    2021 : Series A : Team of 20 : Open NYC
```

Each colon adds another event to the same period.

### Title

```mermaid
timeline
    title Main Title Here
    ...
```

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — timeline added in v10.9, stable
- **Known quirks**:
  - Very long event text wraps awkwardly — keep events ≤ 40 chars each
  - Too many events per period (>5) gets cramped vertically
  - Sections with many periods create horizontal scrolling in narrow preview panes
  - Non-ASCII characters render fine but may affect alignment
- **Workaround**: none needed for standard use

## Quote rule for Timeline

Mermaid timeline treats title / section / period / event text as free-form tokens delimited by newlines or `:`. Wrapping them in `"..."` causes quote characters to render literally in the output.

**Do NOT quote**:
- Title: `title History of Programming Languages` ✅ (NOT `title "..."`)
- Section: `section 1950s` ✅ (NOT `section "1950s"`)
- Period / events: `1957 : FORTRAN` ✅ (NOT `1957 : "FORTRAN"`)
- Multi-event line: `1995 : Java : JavaScript : PHP : Ruby` ✅ — each event is colon-delimited free-form, unquoted

**For CJK content in Timeline**: CJK usually parses throughout, but this is **not guaranteed** in Obsidian's bundled lexer (mermaid-cli is more lenient than Obsidian — a cli pass does not prove an Obsidian pass). No quoting escape exists (quotes render literally); if a label fails in Obsidian, rephrase / romanize it.

**Colon caveat (scoped)**: only a **space-padded ` : `** starts a new event — that is the separator. A bare colon inside event text is safe and does NOT split: `2023 : 開會 9:00 開始` renders as one event, and `2023 : 發布 http://x` keeps the `://` (verified mermaid-cli 2026-06). So only avoid the literal ` : ` (space-colon-space) sequence inside an event; there is no quoting/escape mechanism, so rephrase if you need that exact sequence.

## Worked examples

### Example 1: Technology era timeline

```mermaid
timeline
    title Evolution of Web Development

    section 1990s
        1991 : WWW born
        1995 : JavaScript : CSS1 : HTML 2.0

    section 2000s
        2004 : Ajax : Gmail
        2006 : jQuery
        2009 : Node.js : Chrome

    section 2010s
        2013 : React
        2014 : Vue
        2016 : Angular 2

    section 2020s
        2020 : Svelte kit rises
        2023 : AI-assisted coding mainstream
        2026 : Post-framework era
```

### Example 2: Personal career timeline

```mermaid
timeline
    title My Career Journey

    section Junior
        2018 : Graduated
        2018 : Joined StartupCo : Entry-level Dev
        2019 : Promoted to Mid-level

    section Senior
        2021 : Joined BigTechCo : Senior Engineer
        2022 : Tech lead for payments team
        2023 : Promoted to Staff Engineer

    section Leadership
        2024 : Engineering Manager : 6 reports
        2025 : Director of Engineering
```

### Example 3: Product release history

```mermaid
timeline
    title Product Release History

    section v1.x (2023)
        Jan 2023 : v1.0 launched : MVP with 5 features
        Mar 2023 : v1.1 : Added auth
        Jun 2023 : v1.2 : Performance improvements
        Oct 2023 : v1.3 : Mobile support

    section v2.x (2024)
        Feb 2024 : v2.0 : Major redesign
        Jul 2024 : v2.1 : API v2
        Nov 2024 : v2.2 : Enterprise features

    section v3.x (2025-)
        Jun 2025 : v3.0 : AI features
        Jan 2026 : v3.1 : Collaboration
```

### Example 4: Historical events (world history)

```mermaid
timeline
    title 20th Century Major Events

    section Pre-WWII
        1914 : WWI begins
        1918 : WWI ends
        1929 : Great Depression starts
        1939 : WWII begins

    section WWII Era
        1941 : Pearl Harbor
        1945 : WWII ends : Atomic bombs

    section Cold War
        1957 : Sputnik launched
        1969 : Moon landing
        1989 : Berlin Wall falls
        1991 : USSR dissolves
```

### Example 5: Without sections (simple linear)

```mermaid
timeline
    title Quick Decision Timeline
    Jan : Started planning
    Feb : Got approval
    Mar : Hired team
    Apr : Kicked off build
    May : First demo
    Jun : Launched
```

Sections are optional — simple linear timelines work without them.

### Example 6: CJK content (台灣網路業發展簡史 — demonstrates CJK tolerance without quoting)

```mermaid
timeline
    title 台灣網路業發展簡史

    section 萌芽期 1990s
        1991 : 中研院連上 NSFNET
        1996 : 蕃薯藤成立 : PC home 上線
        1998 : Hinet ADSL 服務

    section 爆發期 2000s
        2000 : 無名小站上線
        2003 : PChome 購物
        2006 : Facebook 進入台灣

    section 行動時代 2010s
        2011 : LINE 登陸台灣
        2014 : Uber 進入台灣
        2018 : 電支法上路

    section 新世代 2020s
        2020 : 疫情加速數位轉型
        2023 : 生成式 AI 創業潮
        2026 : AI 應用普及
```

**Important note**: Timeline does NOT support quoting — title, section names, periods, and event text are all free-form tokens delimited by newlines or `:`. CJK works directly without `"..."`. Wrapping CJK in quotes like `section "萌芽期"` would make the quote characters render literally. Avoid colons `:` inside CJK event text since colons are the event separator (use dashes or rephrase if needed).

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| Using `:` without period label: `: event` | `2023 : event` (always have period label first) | Every event line needs a period marker |
| Events with colons in text: `2023 : http://url` | Escape or rephrase to avoid nested colons | Colons are event separators |
| Too many events per period (>5) | Split into multiple periods or use section | Visual clutter |
| Commas instead of colons: `2023 , eventA , eventB` | `2023 : eventA : eventB` | Separator is `:`, not `,` |
| Section header with no events | Add at least one period under each section | Empty sections confuse layout |

### Pre-save validation

- [ ] `timeline` declared on line 1
- [ ] Title optional but recommended
- [ ] Each event line format: `period : event1 : event2 : ...`
- [ ] Events separated by ` : ` (with spaces for readability)
- [ ] ≤ 5 events per period for readability
- [ ] Sections used to group if >8 periods
- [ ] Period labels consistent format (all years OR all months OR all quarters)

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal rules.
