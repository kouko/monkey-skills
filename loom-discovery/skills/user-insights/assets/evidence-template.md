# Evidence — <date>-<slug>

> Claims-to-evidence registry for this discovery. **Evidence outlives any
> single report** (ResearchOps atomic-research model): `research/` reports and
> `user-insights.md` insights both cite rows here by claim id. When a report is
> re-run or discarded, its underlying facts stay recorded in this table.
>
> Fill one row per atomic claim. A claim with no evidence is an **open
> question**, not a fact — move it to `user-insights.md` §Risks & open
> questions, do not assert it.

| Claim id | Claim | Evidence (link / quote) | Source | Date | Confidence |
|---|---|---|---|---|---|
| C1 | <one falsifiable statement> | <URL, quote, or `research/<file>` §> | <who / where; EN or JA labelled> | <YYYY-MM-DD> | high / med / low |
| C2 |  |  |  |  |  |

## Confidence rubric

- **high** — multiple independent sources agree, or direct primary observation.
- **med** — single credible source, or cross-language agreement not yet checked.
- **low** — anecdote, single blog, or inference; flag downstream as provisional.

## Notes

- Label each source by language (EN / JA / ZH) so coverage is auditable at a glance.
- Prefer primary sources; when citing a secondary source, name what it cites.
- Never fabricate a citation. No source → mark the claim "insufficient data".
