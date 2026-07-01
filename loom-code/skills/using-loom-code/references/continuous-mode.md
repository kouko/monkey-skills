# Continuous mode (opt-in): spec-frozen → PR auto-advance

> Loaded on demand by the `using-loom-code` router when the user opts into
> continuous mode. The router body carries only a stub; this file holds the
> full doctrine. **Read it IN FULL before auto-advancing — do not act on the
> stub alone.** Every STOP row, the never-auto-merge terminal, and the
> crutch-vs-verification line below are load-bearing and must not be weakened.

By default the pipeline is **human-pumped**: between every stage the user says
"go". **Continuous mode** is an **opt-in** convention that lets the
orchestrator run stage→stage unattended — from a frozen spec all the way to a
PR — **without losing the verification gates**. It adds a STOP rule, not a
brain.

## Entry — at the SPEC, not the plan

Continuous mode starts only when **both** hold:

1. The user **opts in** explicitly (e.g. "run continuous to PR" / "連續跑到
   PR"). The default stays human-pumped.
2. A **human-approved, frozen spec** exists. Two entry artifacts are accepted
   (the user picks one — see freeze discrimination below):
   - **(a) the `brainstorming` hand-off brief** (`docs/loom/specs/<topic>.md`),
     the per-feature artifact that locks the *approach*; or
   - **(b) a human-approved loom-spec change-folder** (`docs/loom/<change-id>/`)
     as an **alternative** entry artifact alongside the brief — the upstream
     loom-spec output the user has signed off on.

   Either way this is **not** the repo-level PRODUCT-SPEC / TECH-SPEC.
   **Design + spec stay human-gated** (sign-off locks the *approach* via
   `brainstorming`'s Smallest-End-State / Alternatives axes, or via the user's
   approval of the change-folder). The plan is **not** a human checkpoint: it
   is the mechanical sequencing of an already-decided approach, so it is
   **auto-generated** by `writing-plans` and **gated** by the
   `plan-document-reviewer` evaluator subagent (a real writer≠judge **plan
   gate**, PASS / NEEDS_REVISION). The plan becomes one more
   auto-advance-with-gate stage.

## Freeze discrimination — declared, NOT content-shape sniffed (R6)

The freeze does **not** classify the entry artifact by sniffing its content
shape. Instead, the **user declares** which artifact to run on (the brief, or
a change-folder at a named path), and only then does the freeze act. A brief
takes no further machine check; a change-folder is **confirmed** by two
checkable signals — never a fuzzy content-shape classifier:

- **(a) named-artifact presence** — `specs/<capability>/spec.md` exists at the
  declared change-folder path; and
- **(b) validator exit 0** — `loom-spec/scripts/validate_spec_output.py
  <change-folder>` returns **exit 0** (the cross-plugin gate; loom-spec owns
  the format, loom-code reuses it — no new validator). A non-zero exit HALTS
  the freeze and escalates (the artifact is not validate-clean).

There is **no shape-sniffing on either side** — the user's declaration
discriminates, and the validator confirms.

**The brief↔change-folder asymmetry is INTENTIONAL.** The brief (entry a) has
**no structural gate** — it is accepted on the user's declaration alone — *by
design*: the brief is a **human-authored, human-approved** artifact, so the
**human sign-off IS its gate** (per the upstream-human-gate doctrine) and it
needs no machine validation. Its canonical path `docs/loom/specs/<topic>.md`
is a **convention/hint**, not the gate — an off-path brief still enters; the
human approval, not the path, is what locks it. The change-folder (entry b),
by contrast, is **machine-generated**, so it is **machine-validated**
(presence + validator exit 0). This is *why* R6's no-content-shape-sniffing
rule binds only the change-folder: the brief is gated by human approval, not
by shape, so there is nothing to sniff.

This follows the declaration-gate learning: don't fake a fuzzy objective
detector — make the agent declare it, and gate the consequence on a checkable
signal. Upstream stays human-gated; the STOP contract + never-auto-merge
terminal below are **unchanged**.

## Auto-advance behavior

Within continuous mode the orchestrator proceeds `writing-plans → plan gate →
SDD per-task triad → whole-branch review → verification → finish→PR` without
waiting for a human "go", **unless a stop condition fires**.

## Stop contract (halt-and-escalate)

The run halts and escalates when any row fires:

| # | Stop trigger | Notes |
|---|---|---|
| 0a | **plan critical-path depth >5** (`writing-plans` route-back) | scope too deep → escalate: **re-cut** the spec. Existing forcing function |
| 0b | **`plan-document-reviewer` = NEEDS_REVISION for 2 rounds** | plan can't be made schema-valid / atomic → escalate. Existing 2-round cap |
| 1 | implementer returns **BLOCKED** | agent self-declares it needs a human; safe direction |
| 2a | **review-revision loop**: 2 reviewer↔implementer round-trips still NEEDS_REVISION | spec/quality gap; no WebSearch — fix is human clarification, not research |
| 2b | **debug loop**: `systematic-debugging` exhausts (2 hypotheses → mandatory WebSearch → hypothesis #3 still falsified) | reuses the existing **anchored-thinking** guard; zero new logic |
| 3 | a **scope / decision the plan did not specify** arises (not in the spec) | don't let the agent invent scope unattended |
| 4 | the agent **self-declares an assumption** outside plan/spec coverage | honest self-declaration trigger, not a fuzzy confidence detector |
| 5 | **whole-branch review = NEEDS_REVISION** (cross-task) | direct stop; cross-task issues most need human eyes — do NOT auto-remediate |
| 6 | any **PASS_WITH_NOTES** (per-task or whole-branch) | **auto-advance**; accumulate the notes, surface them all at the PR |
| 7 | **PR-open reached** | terminal stop; human merges; **never auto-merge** (inherited from `finishing-a-development-branch`) |

## Crutch-vs-verification line (load-bearing)

Within a task the agent may re-attempt **inside the existing gate loops** up to
the bounds above (retry-within-bounds = verification). It may **NOT re-plan,
re-scope, or re-route** — those HALT and escalate, they are not autonomous
decisions. WebSearch is allowed only as `systematic-debugging`'s
hypothesis-#3 input, never as a general "research a workaround" escape hatch.

## Escalation surfacing (two-layer)

- **(i) Stop-and-wait (baseline, always):** the run **halts** and emits a clear
  **"why I stopped + what I need from you"** message plus the accumulated
  PASS_WITH_NOTES. Zero infrastructure.
- **(ii) Proactive notification (layered, optional):** if the host supports it
  (push notification / proactive message), send the stop reason so the user
  gets it while away. **Degrades gracefully** to (i) when the host lacks the
  capability — never a hard dependency.

This mode is **composed over existing gates** — it references, and does not
duplicate, `systematic-debugging` (the anchored-thinking / WebSearch guard for
row 2b), `subagent-driven-development` (the per-task verdicts), and
`finishing-a-development-branch` (the PR-stop / never-auto-merge terminal).
