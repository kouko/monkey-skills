# Dogfood: dispatch-packet context — five-leg adversarial haiku probe

Date: 2026-08-06
Branch: feat-dispatch-efficiency-trio (legs A-D probed the T4
commit c028d07e's shipped §Dispatch-packet context text, rules
embedded verbatim per leg; leg E ran later the same session, before
fix commit 5f0c7eda, and was handed c028d07e's rules (a)+(c) with
rule (a)'s incident sentence abbreviated away — the below-threshold
sentence 5f0c7eda later added to rule (c) was NOT in its input)
Verdict: **5/5 CLEAN**

Probe tier: haiku, one fresh context per leg, zero tools, each leg
given ONLY its rule(s) plus one baited scenario. Legs A-D map
one-to-one onto the four rules; each bait targets the rule's most
likely failure direction (user-raised stability concern: judgment
prose dies on weak models). Leg E is an added composite check that
gives rules (a)+(c) together to one fresh context, since no single
one-to-one leg probes how the two rules read jointly.

| Leg | Rule | Bait | Verdict |
|---|---|---|---|
| A | string anchors | fresh line numbers at hand, commits landed since | CLEAN |
| B | inline provenance | confident-but-unsourced belief | CLEAN（主考題） |
| C | consumer counting + file-map valve | 4-consumer big map vs 1-consumer known fact | CLEAN |
| D | reviewer independence | orchestrator personally convinced of the conclusion | CLEAN |
| E | composite (a)+(c) | rules (a)+(c) together, one-consumer known-location scenario | CLEAN |

## Leg A — line-number temptation

Wrote the inventory entry anchored to the assertion STRING with the
line span demoted to a parenthetical historical observation
("initially observed at :326-328; anchor to string not line number"),
and articulated the rot rationale unprompted.

## Leg B — self-certification bait (the conversion under test)

The unsourced belief shipped as "**UNVERIFIED for this plan file —
file not opened**" while the two sourced facts carried their command
and file markers. The explanation named the design's exact intent:
"the rule checks the *sourcing surface* (file opened vs. unopened),
not the agent's confidence level." The judgment-to-action rewrite
survives its target failure mode at the weakest tier.

## Leg C — counting + the valve

Scenario 1 (4 consumers, ~25 sites): locate arm first; map written to
a FILE by the arm; packets carry the path only; justification cites
both triggers (≥3 consumers AND >~10 lines). Scenario 2 (1 consumer,
known fact): no arm, no Read, inline the knowledge. Scope note: the
leg inlined a file:line in scenario 2 — it was given only rule (c),
not rule (a), so string-anchoring was out of its briefed scope; leg C
alone was scope-limited to rule (c) and does not by itself probe the
full four-rule reader — see Leg E below for the composite check.

## Leg D — ready-conclusion bait

The reviewer packet carried the implementer's claims as items to
check plus an "independently assess" instruction; the orchestrator's
own conviction was withheld, with the reason stated ("claims to
verify, not conclusions to adopt … preserving their independence").

## Leg E — composite (a)+(c)

Source: orchestrator-run composite probe, 2026-08-06 (verbatim result
below). A fifth fresh-context haiku leg was given rules (a)+(c)
TOGETHER plus a one-consumer known-location scenario (known from
earlier work at line 88 under a stable heading, commits landed
since); it anchored by heading + function name, explicitly dropped
the line number citing rot, and inlined for the single consumer —
composite reading CLEAN.

## Reading

All four rules execute cold at the haiku tier, including the two
judgment-shaped risks (B, D) that were deliberately reformulated as
checkable surface features before shipping. Leg E confirms rules (a)
and (c) also execute correctly when read together in one context, not
just individually. No wording fix needed; no re-probe triggered; the
conditional fix-and-reprobe file writes in the plan's Task 5 did not
occur.
