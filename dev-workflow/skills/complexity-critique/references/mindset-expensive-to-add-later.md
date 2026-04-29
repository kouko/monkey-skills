# Expensive-To-Add-Later Mindset (PAGNI)

A philosophical anchor for design-time decisions: a small set of
things are *Probably Are Gonna Need It* — the cost of retrofitting
later is so disproportionately high that paying the small cost now
is the discipline. PAGNI is the named exception to YAGNI; it is not
a license to over-engineer, and the bar for invoking it is high.

## Primary Sources

- **Willison, S. (2021) "PAGNIs: Probably Are Gonna Need Its"**, simonwillison.net. https://simonwillison.net/2021/Jul/1/pagnis/ — the canonical post coining the PAGNI acronym and listing the most defensible exceptions to YAGNI from a working web-app practitioner's experience.
- **Plant, L. (2021) "YAGNI Exceptions"**, lukeplant.me.uk. https://lukeplant.me.uk/blog/posts/yagni-exceptions/ — a parallel essay arguing that YAGNI as universally applied is wrong, and enumerating the categories where retrofitting is dramatically more expensive.
- **Kaplan-Moss, J. (2021) "Application Security PAGNIs"**, jacobian.org. https://jacobian.org/2021/jul/8/appsec-pagnis/ — applies the PAGNI lens specifically to security infrastructure, where retrofit cost is often catastrophic.
- **Fowler, M. — bliki entry "Yagni"**: https://martinfowler.com/bliki/Yagni.html — Fowler's own framing already concedes that YAGNI applies to *speculative capability*, not to *thinking ahead*; PAGNI sits inside that crack.

This standard is the dual to `pragmatic-principles.md` §YAGNI: YAGNI
is the default, PAGNI is the named exception.

## The Core Insight

**Willison, "PAGNIs" (2021)**:

> *"When should you override YAGNI? When the cost of adding something
> later is so dramatically expensive compared with the cost of adding
> it early on that it's worth taking the risk."*

YAGNI is a sound default. PAGNI identifies the small, specific class
of cases where retrofit is so costly that "add it now" beats "add it
later" — even though you don't yet *need* it.

## Why YAGNI Alone Is Incomplete

Ruthless YAGNI application backfires when:

- **Adding it later requires touching everything** — examples:
  per-row timestamps, audit trails, request IDs in logs. You can't
  retrofit `created_at` for rows that already exist; the gap is
  permanent.
- **You can't add it retroactively at all** — examples: API
  versioning (clients have already pinned v1; introducing v1 vs v2
  *is* a versioning system), mobile-app kill switches (deployed
  binaries can't dial home if dial-home wasn't built in), feature
  flags before you have a feature-flag library (the first one is
  expensive to retrofit).
- **The cost of *not* having it is catastrophic** — security
  fundamentals (vulnerability disclosure path, session
  invalidation), data you threw away (PII you didn't log so you
  can't audit; events you didn't record so you can't reconstruct).

## Common PAGNIs

### Data you can't get back

- `created_at` / `updated_at` timestamps on every persisted row
- Audit logs for state changes (who, what, when)
- Many-to-many tables instead of foreign-key columns when there's
  any signal you'll need >1 — the retrofit is a data migration
- Immutable event logs alongside mutable state (event sourcing
  light) — you can derive snapshots from events, not the reverse

### Infrastructure that's painful to retrofit

- API versioning, even when v1 is the only version (the *mechanism*
  is what's expensive, not the v2)
- Pagination on list endpoints, even when the list is small now
  (clients pin to "no pagination" and break when you add it)
- Automated deploy / CI from day one (manual deploys ossify into
  rituals)
- Structured logging with request/trace IDs (unstructured logs are
  ungreppable when an incident hits)

### Security fundamentals

- A `security@` email and a written vulnerability disclosure policy
- Session / password / token invalidation mechanism (you will need
  to revoke; don't discover at incident time you can't)
- A safe pipeline to extract redacted production data for debugging

## The Test for Invoking PAGNI

Before claiming PAGNI, all three must hold:

1. **Is retrofitting dramatically more expensive?** 10× or more, not
   2×. "It would be a bit annoying later" is YAGNI, not PAGNI.
2. **Is this a known pattern from experience?** Either yours, your
   team's, or a published practitioner's documented incident — not
   speculation.
3. **Is the cost of adding it now actually low?** Minutes to hours,
   not days. If it's a week of work, the PAGNI claim is hiding a
   speculative architectural bet.

If yes to all three: PAGNI applies, build it in.
If any answer is *maybe*: YAGNI still wins.

## How PAGNI Sits Next to YAGNI

YAGNI and PAGNI are not in tension when you respect the asymmetry:

- **Most features**: YAGNI. Don't build speculative capability.
- **Infrastructure and data collection**: probably PAGNI. A small,
  named list of exceptions distilled from painful experience.
- **Architectural flexibility for unknown futures**: YAGNI. PAGNI
  is for *concrete and named* infrastructure, not "we might want
  flexibility".

The discipline is to keep the PAGNI list short, named, and grounded
in your or your sources' real incidents — not to let it expand into
"we might need this someday".

## Practical Application

When evaluating a "should we build this now?" question:

1. **Default to YAGNI** — most asks fail the test
2. **Ask the three PAGNI questions** — retrofit cost / known pattern
   / cheap now
3. **Name the source** — if you can't cite a documented incident or
   primary source, you're speculating. Speculation defaults back to
   YAGNI.
4. **Bound the addition** — if you do invoke PAGNI, build the
   minimal version (a one-column timestamp, a stub `security@` page),
   not the elaborated version. PAGNI buys you the *mechanism*, not
   the full-fledged feature.

## When This Mindset Doesn't Apply

- **One-off scripts and prototypes** — code that won't outlive the
  current sprint doesn't repay PAGNI investments.
- **Throwaway exploration** — research-team explorations and
  spike-then-discard work; you're learning, not shipping.
- **Already-shipped systems with mature infrastructure** — if
  versioning, audit, logging are already in place, the PAGNI bill
  is already paid.

## Cross-References

- `pragmatic-principles.md` — YAGNI primary text (Fowler bliki); this
  mindset is the named dual to that section
- `app-security-standard.md` — the security fundamentals listed
  above (session invalidation, audit) intersect with OWASP ASVS
  controls; PAGNI explains the *timing* discipline, ASVS specifies
  the *content*
- `mindset-simplicity-vs-easy.md` — sibling mindset; PAGNI is the
  rare moment where adding a piece of code is the simple choice

## Anti-Patterns

- ❌ **PAGNI as escape hatch for over-engineering** — invoking PAGNI
  to justify a hexagonal architecture, an event bus, or a
  feature-flag service before there is a concrete documented need
- ❌ **Speculative PAGNI** — "we might need multi-tenancy someday";
  no documented incident, no near-term plan, fails test #2
- ❌ **Expanding the PAGNI list to taste** — every individual's "I
  always wish I had X" added without a primary-source incident to
  ground it; the list bloats into "everything I personally like"
- ❌ **PAGNI without scoping** — building the elaborated version
  ("full event-sourcing CQRS") when the minimal version (one
  append-only events table) was the PAGNI; you've accidentally
  shipped speculative architecture
- ❌ **Treating retrofit cost as binary** — "later is harder" is
  always true; PAGNI requires "later is *dramatically* harder",
  10× or more
