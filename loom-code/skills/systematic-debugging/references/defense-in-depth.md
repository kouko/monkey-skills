# Defense-in-depth — Phase 4 post-VERIFY layering

> Companion to [`../SKILL.md`](../SKILL.md). Decides where to add defensive layers AFTER the bug is root-caused — proportional to blast radius, not paranoia.

## The principle

After Phase 4 confirms the hypothesis and you apply the fix, ask: *"What's the blast radius if this same class of bug surfaces from a different angle?"* The answer determines what extra layers earn their cost.

**Defense-in-depth is not "add asserts everywhere."** Each layer has a cost (read time, maintenance, sometimes runtime). Layers are warranted when their cost is less than the expected damage of the next instance of the same bug class.

## The layer ladder

Pick the cheapest layer that catches the bug class. Skip layers above your blast-radius threshold; stack layers when blast radius is high.

| Layer | Cost | Catches what | Add when |
|---|---|---|---|
| 1. **Regression test** | One test file | This exact bug | **Always.** Phase 4's repro becomes a permanent test. Non-negotiable. |
| 2. **Input validation** | Few lines at boundary | Bad inputs of the same shape | Boundary is a user-input / external-API / file-format edge. Use allow-list (see `code-team` security checklist). |
| 3. **Invariant assertion** | One assert in production code | State violations of the invariant in any path | Bug was a violated invariant (e.g. *"this list must be non-empty at this point"*). Cheap when the invariant is local. |
| 4. **Type-system constraint** | Type definition change | Whole class of bug, compile-time | Bug was preventable by a stricter type (e.g. NonEmptyList instead of List; branded type instead of raw string). Highest leverage when the language supports it; expensive when the change ripples. |
| 5. **Monitoring / alerting** | Dashboard + alert config | Production reoccurrence | Blast radius is "users notice" or "data integrity." Add observability that fires BEFORE users complain. |
| 6. **Architectural refactor** | Substantial code change | Whole module class of bug | Bug is the third instance of the same class in this module — Rule of Three. Refactor to make the bug class structurally impossible. |

## Worked examples

### Example 1: typo in config (low blast)

Bug: `config.toml` had `retires` instead of `retries`, silently used default value of 3 instead of intended 5.

- ✅ **Regression test** (layer 1): assert config loader rejects unknown keys.
- ❌ Skip layers 2-6: blast radius is "one config file"; cost of monitoring + types disproportionate.

### Example 2: SQL injection (high blast)

Bug: a user-input string was interpolated into a SQL query unparameterized.

- ✅ **Regression test** (layer 1): test that quotes / semicolons / SQL keywords in input do not escape.
- ✅ **Input validation** (layer 2): allow-list at the API boundary; reject anything not matching expected schema.
- ✅ **Type-system constraint** (layer 4): the query function takes `ParameterizedQuery` not `string`; raw-string SQL doesn't compile.
- ✅ **Monitoring** (layer 5): alert on slow queries / queries returning anomalous row counts; both are SQLi smell.
- ❌ Skip layer 6: refactoring the whole ORM is disproportionate to one bug — UNLESS this is the third SQLi in this codebase (Rule of Three).

### Example 3: race condition in webhook handler (medium blast)

Bug: two simultaneous webhook deliveries for the same event ID processed twice, charged customer twice.

- ✅ **Regression test** (layer 1): concurrent-test that fires two simultaneous requests with same idempotency key; asserts one charge.
- ✅ **Invariant assertion** (layer 3): assert *"only one charge per idempotency key"* before commit.
- ✅ **Input validation** (layer 2): require idempotency key on all charge endpoints.
- ✅ **Architectural** (layer 6, only if this is third race): unique constraint on `(event_id, status='processed')`.
- ❌ Type-system (layer 4): no idiomatic way to express "this transaction is serializable" in most type systems.

## Anti-patterns

- ❌ **"Add asserts everywhere."** Each assert is read + maintained. An assert that fires once in 6 months earns its cost; an assert that no human ever reads costs more than it saves.
- ❌ **try/except around the fix.** This is masking, not defense. The fix should resolve the exception's cause; the exception was the bug telling you what's wrong (Red Flag in `../SKILL.md`).
- ❌ **Defense without root-cause understanding.** Adding a guard without knowing what it's guarding against just shifts the failure mode. Phase 3-4 must confirm the cause first.
- ❌ **Same layer multiple times.** Two regression tests for the same bug is not more defense — it's two tests to maintain. One sharp test > two soft tests.
- ❌ **Layer above blast radius.** Monitoring + alerting for a one-off typo in a personal-project config is overkill. Match cost to consequence.

## The proportionality rule

```
Blast radius:        Layers warranted:
  one config         1 (regression test)
  one module         1-3 (regression + validation / assertion)
  customer data      1-5 (regression + validation + assertion + types + monitoring)
  security           1-6 (all layers; the cost of the next instance is unbounded)
```

If you find yourself unsure where to stop, ask: *"Would I be comfortable if this bug class re-emerged in 6 months?"* The first layer that makes the answer *"yes, the new instance would be caught fast"* is where you stop.

## See also

- [`../SKILL.md`](../SKILL.md) — Phase 4 VERIFY produces the bug class; this file decides what defenses follow.
- [`root-cause-tracing.md`](root-cause-tracing.md) — must complete before defense layering (no defense without understanding).
- [`../../subagent-driven-development/checklists/security-checklist.md`](../../subagent-driven-development/checklists/security-checklist.md) — security-grounded version of the input validation / allow-list discipline.
- `dev-workflow:complexity-critique` — for layer 6 (architectural refactor) decisions, especially the Rule-of-Three trigger.
