# A/B differential dogfood — password reset via emailed link

> **Seed**: "Let a user reset their password via an emailed link."
> **Date**: 2026-06-11
> **Arm A**: spec-toolkit (spec-expansion 3-phase + completeness-critic), blind to Arm B → `proposal.md` + `specs/password-reset/spec.md`
> **Arm B**: baseline — a capable model's unaided one-shot brainstorm, blind to Arm A → `baseline-brainstorm.md`
> **Method**: independent mutually-blind subagents (no cross-contamination); orchestrator diffs. Per `feedback_ab_baseline_reveals_marginal_behavioral_delta`.

## Verdict: **INCONCLUSIVE on omission-recall; the real value is structural.**

On raw omission-finding, the structured scaffold did **NOT decisively beat** a capable model's free brainstorm on this seed. Each arm caught a few things the other missed. **This reproduces the A/B-baseline lesson** (a capable model already does most of the "new" behavior by instinct). spec-toolkit's defensible value turned out to be **not "finds more omissions" but "produces verification-ready, honestly-tagged output"** — which the baseline does not.

## Raw omission diff

### Caught by spec-toolkit (Arm A) but MISSED by baseline (Arm B)
- **MFA-vs-reset interaction** — does reset bypass/override MFA? Baseline never mentioned MFA at all. ← the single clearest genuine win.
- **Token-type granularity on invalidation** — A specifies invalidating remember-me / refresh / API tokens, not just sessions; B said only "session invalidation / log out other devices."
- **Partial-failure atomicity framed as requirements** — A has explicit scenarios for orphan-token-on-email-send-failure and session-invalidation-failure; B listed "email delivery failure" but not the atomicity/orphan framing.
- **Admin/support + email-scanner as first-class actors** — A enumerated overlooked actors; B did not frame actors.

### Caught by baseline (Arm B) but MISSED by spec-toolkit (Arm A)
- **Token-in-URL leakage** (referrer headers, browser history, server logs) — B caught it; A did not list it. ← notable miss by the "thorough" arm.
- **Email normalization** (case / whitespace / Unicode in the address) — B caught; A did not.
- **CAPTCHA** (beyond rate-limiting, for email-bombing) — B caught; A had rate-limiting but not CAPTCHA.
- **Lost-email-access dead-end** (recovery when the user no longer controls the email) — B caught; A did not.

### Caught by BOTH (the large overlap — the point of the experiment)
Enumeration-safety / generic response, constant-time compare, single-use **hashed** high-entropy token, short TTL + expiry-boundary rejection, **email-scanner prefetch burning the token (GET no-consume / POST consume)**, new-request-invalidates-prior-token, password policy + confirm-mismatch + same-as-current, breached-password (HIBP) check, SSO-only / passwordless accounts, disabled/suspended/unverified/deleted account states, concurrent-reset races, clock-skew at boundary, HTTPS-only link, rate-limiting, session invalidation, notify-on-change, audit logging, auto-sign-in-vs-redirect.

**The baseline independently caught the "highest-value" catch spec-toolkit's own run flagged as its star (email-scanner prefetch), plus SSO-only and disabled-account states.** That is the crux of the INCONCLUSIVE verdict.

## What spec-toolkit produced that the baseline structurally did NOT
This is where the delta is real and one-directional:
1. **Testable acceptance criteria.** Arm A emitted 8 requirements / **16 `#### Scenario:` GIVEN/WHEN/THEN** criteria — directly consumable by `code-toolkit:writing-plans` as RED/GREEN. Arm B produced a prose bullet list — **not** acceptance criteria, not TDD-ready.
2. **Enforced, tagged blind spots + provenance.** Arm A's blind spots are a required, non-empty, structured section naming the human/field source per item (product/security/legal/identity-architect/compliance); each spec item is tagged seeded/inferred/critic-found. Arm B's "open questions" overlap in content but are unstructured and untagged.
3. **Auditable structure.** USM backbone → OOUX object model (with state machines) → path×edge matrix makes the coverage inspectable (you can see which `object × CTA × state` cells were considered). The baseline is an unordered list — thorough here, but no structure to audit *what wasn't* considered.

## Honest read for the bet (build-to-learn outcome)
- The original bet was "the critic finds real omissions a well-prompted model misses." **On this seed, that bet is INCONCLUSIVE** — the marginal omission delta (≈1 clear win: MFA) is offset by ≈4 baseline-only catches A missed. A capable model brainstorming freely is a *strong* baseline.
- **The bet should be re-framed**, not abandoned: spec-toolkit's durable value is **structure + verification-readiness + enforced honesty (blind spots/provenance)**, not raw recall superiority. Those are real and the baseline does not provide them — but they are a *different* value proposition than "catches what you'd miss."
- **Caveats on this single run** (do not over-generalize from n=1): (a) password-reset is a security-canonical domain where a strong model has dense priors — a *less* canonical / more bespoke-business-logic seed might show a wider recall gap (the lenses may matter more where the model's priors are thin); (b) the matrix lens visibly helped state/transition coverage but did not beat the baseline on the breadth axes (URL leakage, normalization) — suggesting the lens set has gaps of its own; (c) one seed is not a measurement.

## Recommended next step (decision for kouko)
- **Do not expand to the full 5-skill pipeline on the strength of recall alone** — the recall case is not proven.
- **If continuing**, run 2–3 more A/B seeds in *less canonical* domains (bespoke business logic, not security-textbook) to test caveat (a) — that is where the scaffold should win if it wins anywhere.
- **Or re-position** spec-toolkit explicitly as "verification-ready structured spec output + enforced blind-spots" (a real, defensible value the baseline lacks) rather than "finds more omissions."
