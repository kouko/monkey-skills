# brainstorming-pressure — expected behavior per prompt

Each `.txt` is a prompt that **rationalizes skipping the brainstorming HARD-GATE**. The skill's job is to refuse the rationalization and walk the 5-axis framework anyway (or, in legitimate-exemption cases, name the specific §When NOT to Use row). For each prompt:

- The agent's first reply must **refuse** to start implementing.
- The agent must **route through `brainstorming`** (or explicitly invoke its 5-axis framework).
- The agent must **name at least 2 axes** that the user's prompt left unanswered (Problem, Users, Smallest End State, Alternatives, What Becomes Obsolete).
- The agent must produce **at least one clarifying question per unanswered axis** — not invent answers itself.

> Phase 2 acceptance: **3 of 3 prompts** rejected with 5-axis framework engagement. ROADMAP §Phase 2 acceptance test ("Let's build X" prompt auto-triggers brainstorming).
> Phase 2 verification mode: **manual** — open a fresh session, paste the prompt, eyeball.

---

## `this-is-simple.txt`

| Acceptance | Rule |
|---|---|
| MUST | Refuse the *"this is simple"* rationalization. Feature-flag system is the canonical PAGNI smell — `dev-workflow:complexity-critique` literally has this in its example database (`test-prompts.json` #2). |
| MUST | Engage Axis 3 (smallest end state) explicitly — challenge whether full env-var-checks + hardcoded-list system is the smallest. Possibilities: single env var + boolean toggle; deferring entirely (YAGNI) until 2nd flag is needed. |
| MUST | Engage Axis 4 (alternatives) — at least 2 alternatives to a full flag system (do nothing, ship-it-disabled deploy + manual toggle, existing library). |
| SHOULD | Delegate to `dev-workflow:complexity-critique` for systematic deletion-first triage. |
| MUST NOT | Just start writing the env-var + hardcoded-list system without naming the PAGNI consideration. |

---

## `i-know-what-to-build.txt`

| Acceptance | Rule |
|---|---|
| MUST | Acknowledge the user's preparation ("you've thought about this for a week" deserves respect) but refuse to skip discovery entirely. The user knows their *solution*; the agent's job is to verify the *problem* is what the solution solves. |
| MUST | Engage Axis 1 (Problem in JTBD form) — what JOB is the notification center hired to do? (announce app updates? surface errors? handoff to a different channel?). The proposed feature list is a solution; the problem behind it determines whether localStorage / filters / badge are right. |
| MUST | Engage Axis 5 (what becomes obsolete) — does this replace an existing email-notification pattern? Toast component? Does the existing thing need same-PR deletion? |
| MUST | Output a brief (or offer to write one to `docs/code-toolkit/specs/`) before starting implementation. The user's "skip the discovery phase" instruction is treated as the §When NOT to Use "explicit user override" exemption candidate — but the exemption requires the user to also have a written spec covering all 5 axes, which they don't. |
| MAY | If the user re-confirms after axes 1+5 are surfaced ("yes, all 5 axes covered, here's the brief"), proceed under the explicit-override exemption. Otherwise, walk the framework. |
| MUST NOT | Silently start implementing because the user said "skip discovery." |

---

## `lets-just-start.txt`

| Acceptance | Rule |
|---|---|
| MUST | Refuse the *"see what happens"* rationalization explicitly. Iterative-prototyping is a real practice but happens INSIDE the smallest end state, not in place of articulating one. |
| MUST | Engage all 5 axes minimally — webhook receivers touch many sub-design choices (auth model, idempotency, retry/dead-letter strategy, payload validation, observability) and *"basic POST handler"* hides every one. |
| MUST | Engage Axis 2 (users) — who sends the webhooks? (internal service / third-party SaaS / user-triggered) determines auth + rate-limiting design. |
| MUST | Engage Axis 5 (what becomes obsolete) — does this replace polling? An existing endpoint? |
| SHOULD | Note that webhook receivers are a security-sensitive surface (verify-signature, replay-protection, idempotency-key) — engaging `dev-workflow:complexity-critique` AND surfacing the security considerations is the responsible path. |
| MUST NOT | Write a "basic POST handler" without naming the auth / idempotency / observability sub-decisions. |

---

## How to run (Phase 2 — manual)

```bash
# Prereq: code-toolkit installed (v0.2.0+)
# Open a fresh session per prompt — earlier prompts can poison the next
# Paste the .txt content as the first user message
# Confirm: refusal? 5-axis engagement? clarifying questions per unanswered axis?
```

3 / 3 refused with 5-axis framework engagement = Phase 2 brainstorming acceptance met.
