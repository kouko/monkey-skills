# Standard: Goodhart self-check — once stakes are attached, the lead gets gamed

## Statement

Passing the two-axis test (`predictive-and-influenceable.md`) is
**necessary but not sufficient**. The moment visibility, reward, or
career stakes are attached to a lead measure, Goodhart pressure scales
with the stakes — independent of the measure's intrinsic quality. Three
defensive moves are mandatory:

1. **Pair frequency with quality.** Never run two frequency-based leads.
   At least one of the 2-3 leads must be a quality-based check on the
   frequency lead ("called 50 customers" + "followed the script on each
   call"; "wrote 30 min daily" + "produced one named scene beat per
   session").
2. **Re-validate the causal chain on a 4-week cadence.** If leads are
   green but lag is flat for 4+ weeks, the lead is being gamed or was
   wrong. Treat green-lead-flat-lag as a redesign signal, not a "push
   harder" signal. Route to `4dx-sustain-momentum-rescue`.
3. **Keep the falsifiable forecast written down.** D2 protocols all
   produce a written paragraph: "if I/we hit lead targets every week
   for 6 weeks, here's why I/we expect the lag to have moved by [Y]."
   Drift between predicted and observed lag movement is then visible
   instead of rationalized away.

## Source

The book treats measure-gaming as a single boundary case (CE-24, "book
gap" — author warning is one paragraph). The mechanism is older and
better-documented than 4DX itself.

> Any observed statistical regularity will tend to collapse once pressure is placed upon it for control purposes.
>
> — Charles Goodhart, "Problems of Monetary Management: The U.K. Experience" (1975)

> When a measure becomes a target, it ceases to be a good measure.
>
> — Marilyn Strathern, "'Improving ratings': audit in the British University system" (1997, popularized form)

Full citations and verification links in
`../references/industry-grounding.md`.

## Documented industry collapses (case shorthand)

All three lead measures **passed the two-axis test cleanly** at
selection. They collapsed only after stakes were attached. This is the
pattern:

- **Wells Fargo cross-selling, 2011-2016** — "products per household"
  ("Gr-eight": 8 products) lead, tied to branch quotas + termination
  decisions. CFPB Consent Order 2016-09-08 fined $185M total ($100M
  CFPB + $35M OCC + $50M LA City/County). ~3.5M unauthorized accounts.
  CEO Stumpf resigned 2016-10-12.
- **Phoenix VA wait-time, exposed 2014** — 14-day-scheduling lead tied
  to senior-executive bonuses. VA OIG report 14-02603-267 (2014-08-26)
  documented unofficial "secret" wait lists hiding ~115-day real waits.
  3,500+ veterans on unofficial lists; 1,700+ never enrolled at all;
  28 patients negatively impacted (6 deaths) plus 17 more (14 deaths)
  among reviewed cases.
- **Atlanta Public Schools, 2009-2015** — year-over-year CRCT-score
  lead tied to bonuses, public rankings, employment. GBI probe (2011)
  found cheating at 44 of 56 schools, 178 educators implicated. On
  2015-04-01 11 of 12 defendants convicted of racketeering after the
  longest criminal trial in Georgia history (8 months).

The shorthand for 4DX practitioners: "*if your lead measure is the kind
of thing Wells Fargo, Phoenix VA, or Atlanta APS could have selected
under their two-axis test, the gaming risk is built in.*"

## Application across modes

| Mode | Where Goodhart pressure shows up | Mitigation |
|---|---|---|
| **Personal-discover (solo)** | Self-Goodharting when high stakes are attached to self-set leads — speed-reading without comprehension, screen-staring counted as writing, voicemails counted as cold calls. Step 8 of `personal-discover.md` runs the explicit self-check. | Pair frequency + quality; 4-week causal-chain re-check (Step 7's written forecast is the anchor). |
| **Team-facilitate (leader)** | Social rationalization at team scale — teams collectively normalize gamed numbers ("we all know what counts"). Industry cases generalize directly to team scale. Step 8 of `team-facilitate.md` walks the leader through surfacing the gaming risk in the room. | Pair frequency + quality (vetoed by leader if team picks two frequency leads); 4-week causal-chain re-check; honest review of "leads green, lag flat" pattern. |
| **Member-influence (member)** | Once a focus lead is fixed, the same self-Goodhart risks apply at the member's seat. "Made my 3 calls" but didn't follow the script; "logged my 30 min" but stared at the screen. | Step 8 of `member-influence.md` runs the same 4-week re-check; member surfaces the gaming pattern to the leader rather than to themselves alone. |

## When to worry

- **Leads visibly green, lag visibly flat for 4+ weeks.** Single
  highest-confidence Goodhart signal. Redesign, don't push harder.
- **Numbers feel "too clean"** (every week hits target, no variance).
  Real frontline leads vary; suspicious smoothness suggests gaming or
  reporting-side rationalization.
- **Stakes recently attached** (bonus, public rank, performance review
  tied to lead) without paired quality lead — book defaults to
  optimism here; assume gaming will start by week 4.
- **Junior team members start scoring identically to senior members**
  on lead performance — Edmondson safety signal failing into Lencioni
  artificial harmony, gaming covered by face-saving.

For the underlying mechanism literature and primary citations, see
`../references/industry-grounding.md` (Goodhart 1975, Strathern 1997,
CFPB 2016, VA OIG 2014, GBI 2011).
