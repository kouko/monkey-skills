# Password reset via emailed link — spec-expansion proposal

Seed: *"Let a user reset their password via an emailed link."*

This is a GENERATE-layer spec draft. It is **not** complete — see the coverage
statement at the end and the non-empty Blind spots section. Trust is earned by
execution (loom-code's VERIFY gate), not by a spec that looks finished.

## USM backbone

The happy-path spine of ordered user-journey steps (left-to-right). Each step
tagged seeded / inferred.

| # | Step (who does what) | Provenance |
|---|----------------------|------------|
| 1 | Anonymous user opens the "forgot password" form and submits an identifier (email) | seeded |
| 2 | System looks up the account for that identifier | inferred |
| 3 | System mints a single-use, time-limited reset token bound to the account | seeded ("link") + inferred (single-use/TTL) |
| 4 | System sends an email containing the reset link (token embedded) | seeded |
| 5 | User receives the email and clicks the link | seeded |
| 6 | System validates the token (exists, not expired, not consumed, not invalidated) | inferred |
| 7 | System shows the "set new password" form | inferred |
| 8 | User enters a new password (+ confirmation) | seeded |
| 9 | System validates the new password against policy | inferred |
| 10 | System updates the password and consumes the token | seeded (update) + inferred (consume) |
| 11 | System invalidates existing sessions / other outstanding reset tokens | inferred |
| 12 | System notifies the user the password changed; user can log in with the new password | inferred |

**Actors:** User (seeded); Anonymous/unauthenticated requester (inferred — the
person at the form is by definition not logged in); Email/SMTP system (seeded —
"emailed"); Identity/Auth system (inferred); Clock/Scheduler (inferred — TTL);
Attacker (inferred — adversarial); Email security scanner / link prefetcher
(critic-found); Admin/Support (critic-found — operator-initiated reset).

**Objects:** Reset Request, Reset Token, User Account, Password, Session, Email
Message.

**CTAs:** request-reset, lookup-account, mint-token, send-email, open-link,
validate-token, submit-new-password, validate-policy, update-password,
consume-token, invalidate-sessions, invalidate-other-tokens, notify-user.

## OOUX object model

Object inventory + per-object state machine (states + legal transitions). ORCA
(Objects / Relationships / CTAs / Attributes) folded in per object.

### Reset Token
- **Relationships:** belongs-to 1 User Account; carried-by 1 Email Message.
- **CTAs:** mint, validate, consume, invalidate, expire.
- **Attributes:** opaque high-entropy value (stored hashed), account ref, issued-at, expires-at, status, single-use flag.
- **State machine:**
  - `none → issued` (on request)
  - `issued → validated` (on link open, pre-form)
  - `validated → consumed` (on successful password update)
  - `issued|validated → expired` (clock passes expires-at)
  - `issued|validated → invalidated` (new request mints a fresh token / password changed by another path / admin revoke)
  - terminal: `consumed`, `expired`, `invalidated`
  - **illegal:** `consumed → validated`, `expired → consumed` (replay) — flagged as edges.

### Reset Request
- **Relationships:** made-by 1 requester (possibly anonymous); produces 0..1 Reset Token (0 if account not found / rate-limited).
- **CTAs:** submit, fulfil, abandon, throttle.
- **Attributes:** submitted identifier, source IP, timestamp, count-in-window.
- **State machine:** `none → pending → fulfilled | abandoned | rate-limited`.

### User Account
- **Relationships:** has 1 Password; has 0..N Sessions; targeted-by 0..N Reset Tokens.
- **CTAs:** lookup, reset-password, lock, disable, notify.
- **Attributes:** identifier/email, email-verified flag, status, has-password flag (false for SSO/social-only), MFA-enabled flag.
- **State machine (primary):** `active → reset-in-progress → active(new pw)`.
  - **Orthogonal states:** `enabled ↔ disabled`; `unlocked ↔ locked`; `email-verified ↔ email-unverified`; `has-password ↔ passwordless(SSO/social)`; `exists ↔ nonexistent`.

### Password
- **CTAs:** validate-policy, set, compare-to-old.
- **Attributes:** stored hash, policy params (length/complexity), history.
- **State machine:** `submitted → (policy check) → accepted | rejected-policy | rejected-same-as-old | rejected-breached | rejected-confirm-mismatch`.

### Session
- **Relationships:** belongs-to 1 User Account.
- **CTAs:** create, invalidate.
- **Attributes:** session id, device, issued-at; sibling artefacts: "remember-me" cookies, refresh/API tokens.
- **State machine:** `active → invalidated`. Multiple concurrent instances per account.

### Email Message
- **CTAs:** queue, send, deliver, bounce, fail.
- **Attributes:** to-address, link/token, sent-at.
- **State machine:** `queued → sent → delivered | bounced | send-failed`.

## Path × edge matrix

Cartesian seed = `backbone-step × object × CTA × state`; deliberately
over-generates, then pruned through 7 lenses (state-transition / BVA / CRUD /
permissions / empty-error-loading / NFR / policy-legal). Below = the surviving
paths/edges post-prune. Illegal cells (e.g. consume an already-consumed token)
are kept as **edge cases**, not dropped, because they are the attack surface.

### Surviving HAPPY paths (state-transition legal)
| Path | Object × CTA × state | Provenance |
|------|----------------------|------------|
| P1 | Request × submit × (account exists) → token issued, email sent | seeded |
| P2 | Token × validate × issued → show set-password form | inferred |
| P3 | Password × set × policy-accepted → updated, token consumed | seeded |
| P4 | Session × invalidate × active → all other sessions logged out | inferred |
| P5 | Account × notify × password-changed → confirmation email | inferred (best-practice) |

### Surviving EDGE / error paths (lens-surfaced)
| Edge | Lens | Object × CTA × state | Provenance |
|------|------|----------------------|------------|
| E1 | empty/state | Request × submit × (account NOT found) → respond identically, send nothing (no enumeration) | critic-found |
| E2 | permissions/NFR | Request × submit × (account exists but email-unverified) → policy decision (define) | critic-found |
| E3 | state | Account × reset × (disabled / locked / deleted) → refuse or special-case | critic-found |
| E4 | state | Account × reset × (passwordless SSO/social, has-password=false) → cannot reset; guide to IdP | critic-found |
| E5 | state-transition (illegal) | Token × consume × consumed → reject (replay defence) | inferred |
| E6 | BVA / clock | Token × validate × (now == expires-at, ±1s) → off-by-one expiry boundary | inferred |
| E7 | concurrency | Token × mint × (2nd request while 1st issued) → invalidate prior / which wins | critic-found |
| E8 | concurrency/prefetch | Token × validate × (email-scanner auto-GET) → GET must not consume; consume only on POST | critic-found |
| E9 | partial-failure | Password updated but session-invalidation fails → atomicity / compensation | critic-found |
| E10 | partial-failure | Token minted but email send fails → orphan token; surface failure, allow retry | critic-found |
| E11 | BVA | Password × set × (too short / too long / empty / max-length overflow) | inferred |
| E12 | BVA/policy | Password × set × (same as current) → reject | critic-found |
| E13 | NFR security | Password × set × (known-breached) → reject (policy) | critic-found |
| E14 | input | Password × set × (confirmation mismatch) → reject | inferred |
| E15 | NFR security | Request × submit × (brute-force token guessing) → rate-limit + high token entropy | critic-found |
| E16 | NFR/timing | Request × submit × (timing/response differs by account-existence) → constant-time, no enumeration | critic-found |
| E17 | security | Token transport over plain HTTP → links MUST be HTTPS-only | critic-found |
| E18 | policy/security | Account MFA-enabled × reset → does reset bypass MFA? define policy | critic-found |
| E19 | CRUD | Token read after consume (audit) — read allowed, mutate not | inferred |
| E20 | policy | Reset success × invalidate "remember-me" cookies + refresh/API tokens | critic-found |

### Pruned-away (illegal / out of scope)
- `Token × validate × none` (no token issued) — impossible, dropped.
- `Email × send × (account nonexistent)` — collapses into E1 silent no-op.
- Admin-initiated reset flow — out of seed scope; named as actor, deferred (blind spot).

## Provenance

Every item tagged seeded / inferred / critic-found.

**seeded** (in/entailed by the seed):
- Reset is initiated by a user; delivery is via email; the link carries the reset; the user sets a new password; the password is updated (USM 1,4,5,8,10; P1,P3).

**inferred** (from OOUX/USM/lens priors):
- Account lookup, token mint/validate/consume lifecycle, single-use + TTL semantics, set-password form, password-policy validation, session invalidation, change-notification, off-by-one expiry boundary (E6), replay rejection (E5), confirmation-mismatch (E14), password length BVA (E11), CRUD read-after-consume (E19).

**critic-found** (surfaced by the loop-until-dry critique, re-seeded):
- User-enumeration defence / identical response + constant-time (E1, E16); email-unverified policy (E2); disabled/locked/deleted account (E3); passwordless/SSO accounts (E4); concurrent-request token race (E7); email-scanner prefetch must not consume token — GET vs POST (E8); partial-failure atomicity for session invalidation (E9) and email-send failure orphan token (E10); same-as-current rejection (E12); breached-password check (E13); rate-limiting + token entropy vs brute force (E15); HTTPS-only links (E17); MFA-and-reset interaction (E18); invalidate remember-me / refresh / API tokens (E20); notify-on-change (P5); admin/support actor; email-scanner actor.

## Blind spots — needs human/field input

These are aspects no generator can manufacture — they require real
business/domain/legal/field input. Each names the source that could close it.

- **Token TTL value** — is it 15 min, 1 hour, 24 hours? *Needs: product/security policy owner.*
- **Rate-limit thresholds** — requests per email/IP per window, lockout duration. *Needs: security/abuse-team field data + product policy.*
- **Password policy specifics** — min length, complexity, breach-list source (e.g. HIBP) and whether it is mandatory or advisory. *Needs: security policy owner + compliance.*
- **Email-unverified accounts (E2)** — may an unverified account reset at all, or must it verify first? *Needs: product owner.*
- **Passwordless / SSO-only accounts (E4)** — exact UX: hard-block, or redirect to the IdP? Depends on the actual identity architecture. *Needs: identity/architecture owner.*
- **MFA-and-reset interaction (E18)** — does a password reset bypass, preserve, or require MFA? Security-critical, jurisdiction- and threat-model-dependent. *Needs: security architect.*
- **Session-invalidation scope (E20)** — reset all sessions, or only others; include API tokens / refresh tokens / remember-me? *Needs: product + security policy.*
- **Disabled/locked/deleted account handling (E3)** — refuse silently, refuse with message, or special path. *Needs: product + support-ops.*
- **Notify-on-change channel & content (P5)** — required by which regulation? secondary channel (SMS)? *Needs: compliance / legal.*
- **Data retention of reset audit logs** — how long are reset attempts/IPs kept; GDPR/PII implications. *Needs: legal / data-protection officer + jurisdiction.*
- **Legal jurisdiction** — which privacy/breach-notification regime applies (GDPR / CCPA / APPI / PDPA). *Needs: legal review per deployment region.*
- **a11y / i18n requirements** — WCAG target level; languages the reset email must support. *Needs: design/localization owner + field requirements.*
- **Admin/support-initiated reset** — is operator-triggered reset in scope, and what authorization/audit does it need? *Needs: product + security.*
- **Email deliverability fallback** — what to do when mail bounces / mailbox dead and the account has no other contact. *Needs: product/support-ops.*

---

**Coverage statement:** This draft provides **coverage relative to the seed + 7
expansion lenses (state-transition / BVA / CRUD / permissions /
empty-error-loading / NFR / policy-legal) + 5 critic lenses across a
loop-until-dry critique (terminated after 2 consecutive dry rounds)**. It is
**not complete** — completeness is bounded by the seed ceiling, and the Blind
spots above require human/field input that no generator can supply.
