---
name: using-loom-spec
description: |
  Use when starting spec work and unsure which loom-spec skill applies. Family entry router — routes to spec-expansion (draft/expand a spec from a seed) or completeness-critic (critique an existing draft for omissions).
version: 0.1.0
---

# using-loom-spec

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt, **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
**You have loom-spec.** This skill does not draft or critique a spec itself —
it is the thin entry that decides which of loom-spec's two member skills the
work needs, after checking whether spec work is even the right station yet.
</EXTREMELY-IMPORTANT>

## §Intake

All user-facing narration in this router — briefs, critique summaries,
decision asks — follows `loom-pipeline/hooks/family-relay.md §Family relay discipline`
(pointer, never copy).

**Step 1 — 前站檢查 (upstream check).** Check the target repo against the
loom family's on-ramp criteria table (`loom-pipeline/hooks/family-reception.md`
— the reception SSOT; reference it, don't copy its rows here). Two rows are
most relevant to spec work: if the work touches a user-facing surface and no
`DESIGN.md`/`ui-flows.md` exists yet, recommend `using-loom-interface-design`
first — specifying before the surface is designed re-derives it and drifts.
If no `docs/loom/PRINCIPLES.md` exists and the work is product-shaped (a new
product/feature idea, not an increment), recommend `using-loom-product-principles`
first. Recommend **once**, record the user's choice, then proceed either way
— the negative guard still applies (bug fix / refactor / test-covered
increment → do not interrupt).

**Step 2 — 對站檢查 (peer check).** If the ask isn't spec work at all — it's
a UI/UX design ask, a product-constitution ask, or an implementation/code
ask — redirect to the matching family entry (`using-loom-interface-design`,
`using-loom-product-principles`, `using-loom-code`) rather than forcing it
through loom-spec.

**Step 3 — family routing (disambiguation).** Once the ask is confirmed spec
work, route between loom-spec's two members by the specific verb — this
distinction is load-bearing, not cosmetic:

- **draft/expand a spec from a seed** — a few lines of feature intent, or a
  `ui-flows.md`, that needs fan-out into objects/states/paths/edge cases →
  `spec-expansion`.
- **critique/audit an EXISTING draft for omissions** — a spec-expansion
  output already exists and needs a completeness pass before VERIFY →
  `completeness-critic`.

This closes the **#456-documented adjacent mis-route**: a critique-an-existing-
spec ask getting sent to `spec-expansion` (which would silently re-draft
instead of auditing) instead of `completeness-critic`. When in doubt, ask
"does a draft already exist to critique, or am I starting from a seed?" — the
answer picks the member.

## Family

- `spec-expansion` — GENERATE-layer writer. Fans a sparse seed out into a
  high-recall spec draft (OpenSpec change-folder shape).
- `completeness-critic` — GENERATE-layer critic. Adversarially hunts
  omissions in an existing `spec-expansion` draft via a fresh-context lens
  panel; never touches code.

Both stop at GENERATE — `loom-code:writing-plans` reads the emitted
`#### Scenario:` criteria downstream; that is the one-directional spec→code
handoff, not this router's job.

## How to access skills

| Harness | Mechanism |
|---|---|
| Claude Code | Use the `Skill` tool, e.g. `Skill(skill: "spec-expansion")`. |
| Codex CLI | Use the `skill` tool (Codex shape). |

If the user types `/skill-name`, that is an explicit invocation — load it via
the Skill tool. Do not guess names that are not listed above.

## What this router does NOT do

- Does **not** draft a spec itself — that is `spec-expansion`.
- Does **not** critique a spec itself — that is `completeness-critic`.
- Does **not** auto-invoke either member — the harness invokes them when the
  user's next message + this routing decision match.
