# Brief — code-toolkit Continuous Mode (spec-frozen → PR auto-advance)

> Freeze point revised plan→spec during design (see §Design "Why the freeze moved from plan to
> spec"). Earlier "plan-frozen" phrasing below is superseded by spec-frozen throughout.

> Handoff brief (brainstorming-output format). 2026-06-17. Status: awaiting kouko sign-off.
> Upstream evidence: `docs/code-toolkit/research/2026-06-17-plan-frozen-auto-advance-orchestration.md`
> (deep-research, 5/5 claims adversarially verified) + a `dev-workflow:complexity-critique` pass
> (mindset: design-is-taking-apart) verdict **Shape 1 = PROCEED-WITH-CAVEAT, Shape 2 = REJECT**.

## Problem

The code-toolkit pipeline is **human-pumped by design**: the router states it "does not
auto-invoke downstream skills — the harness invokes them when the user's next message …
match." So between every stage (plan → SDD → review → finish) the user must manually say
"go" / "我合併了". kouko wants: once a plan is frozen, run **unattended all the way to a PR**
("凍結後一路無人值守一路實作到完(PR)"), without losing the verification gates.

## Users

- **Primary:** kouko, running code-toolkit on a frozen plan and wanting to step away while the
  implement→review loop runs, getting pulled back only when a decision or a real problem needs him.
- **Implicit:** any future code-toolkit user who opts into continuous mode.

## Smallest end state

A **prose convention** ("Continuous mode") added to `using-code-toolkit`, plus a one-line
amendment to the router's "does not auto-invoke" caveat. **No new skill, no new code, no new
file in the plugin.** Everything load-bearing already exists:

- stop-on-stuck (debug): systematic-debugging's **Anchored-thinking guard** (2 falsified
  hypotheses → mandatory WebSearch → hypothesis #3 → else stuck). Already shipped + empirically
  validated 2026-05-27.
- per-task verdicts (PASS / PASS_WITH_NOTES / NEEDS_REVISION): SDD, already shipped.
- PR-stop + never-auto-merge: `finishing-a-development-branch` (L13/87/150/161). Already shipped.

Continuous mode is the **connective tissue + stop contract** that names "auto-advance unless a
stop condition fires", composed over those existing gates — it adds a STOP rule, not a brain.

## Alternatives considered

- **Shape 2 — a new "orchestrator" skill that sequences the stages.** REJECTED by
  complexity-critique: it would duplicate the stage order the router already owns (a second SoT
  = Shotgun Surgery), is a +150–400-line surface + manifest/marketplace/CI maintenance, and a
  skill is the natural *home for accreting crutch logic* (retry/re-route/re-plan) — exactly the
  Bitter-Lesson failure mode the research warns against.
- **Default-on (no opt-in).** REJECTED: changes a working default for everyone; unproven
  harmless (A/B-baseline lesson). Continuous mode is **opt-in**.
- **Merging the 4 toolkits.** OUT OF SCOPE + declined: auto-advance only needs gates to chain,
  which is orthogonal to packaging (B/D=D "keep modular" holds).
- **A fuzzy "low-confidence" detector.** REJECTED: don't fake an objective confidence score
  (false-positive trap). Operationalized instead as an **honest self-declaration** stop trigger.

## What becomes obsolete

Nothing is deleted (this is purely additive behavior — named as the caveat in the verdict).
The only edit to existing prose: the router's "does not auto-invoke downstream skills" line
gains an explicit **opt-in continuous-mode exception**.

## Design

### Entry (the freeze) — at the SPEC, not the plan

Continuous mode starts only when **both** hold:
1. The user **opts in** explicitly (e.g. "run continuous to PR" / "連續跑到 PR"). Default stays human-pumped.
2. A **human-approved, frozen spec** exists. **Design + spec remain human-gated** (this is where
   the *approach* is locked — via brainstorming's Smallest-End-State / Alternatives axes + spec
   sign-off).

**Why the freeze moved from plan to spec (revised after verifying the plan gate):** the plan is
not a human-judgment artifact — it is the *mechanical sequencing* of an already-decided approach
into atomic tasks + a dependency DAG. And `writing-plans` already dispatches
`plan-document-reviewer` as a **fresh-context evaluator subagent** (a real writer≠judge gate,
PASS / NEEDS_REVISION), plus a structural forcing function (critical-path depth >5 → route back).
So plan *generation* is automatable and already gated; approach-correctness was locked upstream at
brainstorm/spec. The plan therefore becomes one more **auto-advance-with-gate stage**, not a
mandatory human checkpoint.

### Auto-advance behavior

Within continuous mode the orchestrator proceeds stage→stage (**writing-plans → plan gate** →
SDD per-task triad → whole-branch review → verification → finish→PR) **without waiting for a
human "go"**, UNLESS a stop condition fires.

### Stop contract (halt-and-escalate)

| # | Stop trigger | Notes |
|---|---|---|
| 0a | **plan critical-path depth >5** (writing-plans route-back) | scope too deep → escalate: re-cut the spec. Existing forcing function |
| 0b | **plan-document-reviewer = NEEDS_REVISION for 2 rounds** | plan can't be made schema-valid/atomic → escalate. Existing 2-round cap |
| 1 | implementer returns **BLOCKED** | agent self-declares it needs a human; safe direction (Anthropic: Claude over-asks) |
| 2a | **review-revision loop**: 2 reviewer↔implementer round-trips still NEEDS_REVISION (spec/quality gap) | no WebSearch — fix is human clarification, not research |
| 2b | **debug loop**: systematic-debugging exhausts (2 hypotheses → mandatory WebSearch → hypothesis #3 still falsified) | **reuses the existing Anchored-thinking guard; zero new logic** |
| 3 | a **scope / decision the plan did not specify** arises | don't let the agent invent scope unattended (Devin "underspecified ticket" failure) |
| 4 | the agent **self-declares an assumption** outside plan/spec coverage | honest-declaration trigger (ICLR "escalate when unsure", operationalized) |
| 5 | **whole-branch review = NEEDS_REVISION** (cross-task) | direct stop (decision A) — cross-task issues most need human eyes; do NOT auto-remediate |
| 6 | any **PASS_WITH_NOTES** (per-task or whole-branch) | **auto-advance**; accumulate notes, surface them all at the PR |
| 7 | **PR-open reached** | terminal stop; human merges; **never auto-merge** (inherited from finishing) |

**Crutch-vs-verification line (load-bearing):** within a task the agent may re-attempt inside
the existing gate loops up to the bounds above; it may **NOT** re-plan, re-scope, or re-route —
those are stop conditions, not autonomous decisions. WebSearch is allowed only as
systematic-debugging's hypothesis-#3 input, not as a general "research a workaround" escape hatch.

### Escalation surfacing (both, layered)

- **(i) Stop-and-wait (baseline, always):** the run halts and emits a clear **"why I stopped +
  what I need from you"** message + accumulated PASS_WITH_NOTES. Zero infrastructure.
- **(ii) Proactive push (layered, optional):** if the host supports it (PushNotification /
  proactive message), send the stop reason so kouko gets it while away. **Degrades gracefully**
  to (i) if the host lacks the capability — never a hard dependency.

## Exact edit surface

1. **`code-toolkit/skills/using-code-toolkit/SKILL.md`** — new section "Continuous mode
   (opt-in): spec-frozen → PR auto-advance", containing the entry conditions, the stop contract
   table, the crutch-vs-verification line, and the two-layer escalation. Amend the "does not
   auto-invoke downstream skills" caveat (§"What this router does NOT do") with the opt-in
   exception. Est. +35–55 lines prose. Keep SKILL.md body ≤ ~6k tokens (check after).
2. **No edit** to systematic-debugging, SDD, requesting-code-review, finishing — referenced, not
   modified. (Optional: a one-line cross-pointer in finishing noting continuous mode terminates
   at its PR-stop. Decide during implementation; default = no edit, keep it composed.)
3. **Tests:** a grep/structure test asserting the continuous-mode section + stop-contract terms
   exist in the router (mirrors the repo's existing skill-structure test style). TDD: RED first.

## Grounding (from verified research)

- Stop-at-PR, never auto-merge: industry-universal (Spec Kit / OpenSpec / Copilot agent /
  OpenHands / Devin); automated review catches only ~50% of defects → gate = "ready for human".
- Stop-on-stuck is the load-bearing piece: unattended agents fail by NOT stopping (Devin 3/20,
  tunnel-vision / stubborn loops).
- Thin runbook over a new skill: Bitter-Lesson + Cognition "don't build multi-agents" +
  Anthropic "add complexity only when it demonstrably improves outcomes".
- Risk-based checkpoint (stop at irreversible boundary + uncertainty), not per-action approval
  (Anthropic: 93% of prompts rubber-stamped; per-action approval is friction).

## Out of scope (parked)

Toolkit merge; default-on continuous mode; dynamic task-claiming / many-agent load-balancing;
a numeric confidence detector; auto-remediation of whole-branch NEEDS_REVISION; any retry/
re-route logic beyond the named bounds.

## Caveat the user is choosing (from complexity-critique)

~35–55 lines of purely additive prose, no deletion. The value is reliability — making
unattended operation a **named mode with explicit stop conditions** — not new capability. A
capable model could already run stage-to-stage; this makes *when to stop* explicit and safe.
