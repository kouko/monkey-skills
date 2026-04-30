# 4dx-audit (Consultant-mode entry point)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Consultant-mode entry point for the 4DX plugin — synthesize artifacts the user already has into a structured 4DX audit + sequenced next-move roadmap.

## What this skill does

The other 11 skills in this plugin are **coach-mode**: Socratic dialogue, step-by-step, from zero. This skill is **consultant-mode**: the user drops a strategy doc / OKR sheet / KPI dashboard / scoreboard / meeting-notes pile, and the skill reads it all, diagnoses against the 4DX 5-layer framework, and prescribes 3-5 prioritized next moves — each routing to the matching coach-mode D-skill for deep work.

Five steps:

1. **Inventory** — list every artifact provided
2. **Map** — extract content into the 5 layers (L1 WIG / L2 Lead / L3 Scoreboard / L4 Cadence / L5 Substrate)
3. **Diagnose** — label each layer `well-formed` / `malformed` / `absent` / `wrong-shape` against the book's standards
4. **Identify gaps + risks** — sequencing, Goodhart, engagement collapse, capacity collapse, mis-framing
5. **Prescribe** — 3-5 prioritized actions, each routed to a specific coach skill

## When this skill activates

- **EN** — "Here's our strategy doc — help me 4DX it", "Audit our 4DX given this context", "We have WIG + leads + dashboard but cadence broken — diagnose", "Translate this OKR sheet into 4DX terms"
- **JP** —「策略 doc を 4DX 視点で診断して」「うちの OKR を 4DX に整理したい」「資料を渡すから 4DX 視点で見て」「4DX 入れたが何が抜けてる？」
- **zh-TW** —「這是我們的策略 doc，幫看 4DX 怎麼套」「OKR 翻成 4DX」「資料都在這，幫我用 4DX 框架釐清」「我們導入 4DX 但卡住，幫我診斷」

The activation signature is **artifact-rich query + explicit 4DX-framing ask**. Cold-start queries with no artifacts go to `using-four-dx-coach`.

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Cold-start, no artifacts provided | `using-four-dx-coach` (router does scope triage) |
| Single-discipline ask + full context for that one | The matching D-skill directly (e.g. `4dx-d1-wig-formulation`) |
| User wants Socratic step-by-step coaching | Coach-mode D-skills, not audit |
| Non-4DX framework audit (OKR / BSC / agile retro) | Out of scope — `using-four-dx-coach` for handoff |
| Mid-flow inside an active deep-dive coach skill | Don't interrupt with audit reframing |
| Pure venting / no 4DX-framing intent | Router or external support |

## Output format (brief)

```markdown
# 4DX Audit — [context label / date]

## Inventory
- [artifacts read]

## Layer status
| Layer | Status | Finding |
|---|---|---|
| L1 WIG | malformed | [reason + standard cite] |
| ... |

## Gaps + risks
- [cross-layer issues]

## Recommendations (prioritized)
1. **[Action]** — [reason] → run `[skill-slug]`
2. ...

## Suggested next move
[which skill to run first + why]
```

## Source citation

The 4 Disciplines of Execution (2nd ed., 2021) — McChesney / Covey / Huling / Thele / Walker. Cross-cutting (Foreword + Ch 1 framing + Ch 6 selection + Ch 10 sustaining).

Consultant-craft references in [`references/industry-grounding.md`](references/industry-grounding.md): Block (*Flawless Consulting* 3rd ed. 2011), Schein (*Process Consultation* 1969 / *Helping* 2009), Maister-Green-Galford (*The Trusted Advisor* 2000), Adler & Van Doren (*How to Read a Book* rev. 1972).

## See also

- [`SKILL.md`](SKILL.md) — full audit protocol with 5-step procedure + per-layer diagnostic standards
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) — for cold-start / out-of-4DX queries
- 11 coach-mode D-skills — deep-dive targets the audit routes to
