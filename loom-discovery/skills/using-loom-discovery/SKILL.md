---
name: using-loom-discovery
# firing-evidence: 2026-07-14 baseline 3/3 EXACT (docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md)
description: Family entry router for loom-discovery, the loom problem-space station. Use when unsure which discovery skill applies, or when a product idea's target users are still unclear (說不清是給誰用的 / not sure who this is for / 誰のためかまだ不明) — comes BEFORE product-principles. Routes worth-doing asks (值不值得做 / worth my time budget) to business-value, and user-needs asks (需求研究 / user research / ユーザーインサイト) to user-insights. Non-discovery asks redirect to their family entries. Members share no artifact and no agent.
version: 0.1.0
---

# using-loom-discovery

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt, **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
**You have loom-discovery.** This skill does not map needs, assess worth,
or write any artifact itself — it is the thin entry that decides which of
loom-discovery's two member skills the work needs, after checking whether
discovery is even the right station yet.
</EXTREMELY-IMPORTANT>

## §Intake

All user-facing narration in this router — briefs, routing decisions,
recommendation asks — follows `loom-pipeline/hooks/family-relay.md
§Family relay discipline` (pointer, never copy).

**Step 1 — 前站檢查 (upstream check).** Discovery sits upstream of
principles/design/spec/code — it is normally the FIRST station a
product-shaped idea reaches, not a station something else feeds into.
Still, check the target repo against the loom family's on-ramp criteria
table (`loom-pipeline/hooks/family-reception.md` — the reception SSOT;
reference it, don't copy its rows here) for the negative guard: a bug
fix, a refactor, or a test-covered increment skips discovery entirely and
proceeds straight to whichever downstream station applies. When both a
discovery row and another row fire on the same ask, the precedence note
recorded in `family-reception.md` governs — don't re-derive it here.

**Step 2 — 對站檢查 (peer check).** If the ask isn't discovery work at
all — it's a product-constitution ask, a UI/UX design ask, a spec
fan-out ask, or an implementation/code ask — redirect to the matching
family entry (`using-loom-product-principles`, `using-loom-interface-design`,
`using-loom-spec`, `using-loom-code`) rather than forcing it through
loom-discovery.

**Step 3 — family routing (disambiguation).** Once the ask is confirmed
discovery work, route between loom-discovery's two members by the
specific verb:

- **"worth doing?" / is this worth my time or resources** — an
  adversarial worth-it check, a GO / NO-GO / NEEDS-MORE-RESEARCH call →
  `business-value`.
- **"what do users need?" / what problem exists, for whom** — evidence-
  linked opportunity mapping, or committing to which needs to serve →
  `user-insights`.

When in doubt, ask "are we deciding whether it's worth doing, or are we
figuring out what the problem/users actually are?" — the answer picks the
member.

## Family

- `business-value` — adversarial worth-it check (Shape Up betting
  register, not a Cagan business-viability study). Optional: fires only
  under its own named trigger conditions (see its SKILL.md), silently
  skipped for personal tools or an already-decided GO. Produces
  `business-value.md`.
- `user-insights` — the core research verb. Maps the opportunity space
  (evidence-linked needs) and then proposes a value commitment the user
  must ratify. Produces `user-insights.md`, `evidence.md`, `research/`.

**Typical sequence: `user-insights` ↔ `business-value`.** Most discovery
work starts with `user-insights` — map the opportunity space with
evidence before anyone can judge whether it's worth doing. `business-value`
(the "assess" step) is **skippable** — it only fires under its own
trigger conditions — and **re-entrant**: it can run again after
`user-insights` surfaces more research, and `user-insights` can loop back
after a NEEDS-MORE-RESEARCH verdict. Neither member is a required gate on
the other; call the one the ask actually names.

**Professional isolation is contract-level.** The two skills share no
artifact and no agent: `business-value`'s agents may not map needs;
`user-insights`'s agents may not render investment verdicts. Do not blend
their outputs into one file or one dispatch.

## How to access skills

| Harness | Mechanism |
|---|---|
| Claude Code | Use the `Skill` tool, e.g. `Skill(skill: "business-value")` or `Skill(skill: "user-insights")`. |
| Codex CLI | Use the `skill` tool (Codex shape). |

If the user types `/business-value` or `/user-insights`, that is an
explicit invocation — load it via the Skill tool directly. Do not guess
names that are not listed above.

## What this router does NOT do

- Does **not** assess worth-doing itself — that is `business-value`.
- Does **not** map needs or research evidence itself — that is
  `user-insights`.
- Does **not** auto-invoke either member — the harness invokes them when
  the user's next message + this routing decision match.
