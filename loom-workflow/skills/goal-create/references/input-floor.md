# The Input Floor

> **SSOT for the input requirements of `loom-workflow:goal-create`.**
> This file is the authoritative definition of what must hold before a goal
> condition may be written, and what must hold of the condition itself. Other
> files in this skill route here; do not duplicate these definitions
> elsewhere.

---

## 1 — Two input slots

A goal condition is never drafted from nothing. Before drafting may begin at
all, two input slots must be filled — this is the floor, not the source of
every field in the four-field shape (§2 states where the other two fields
come from):

- **Current state** — what is true now, cited to something readable (a file,
  a test run, a log, a message already in the conversation). This is not a
  guess about the present; it is a pointer to evidence of the present.
- **Wanted difference** — what must become true instead. This is the change
  the run exists to produce, not the direction it should move in.

## 2 — Slot-to-field mapping

Each input slot feeds exactly one field of the four-field goal shape:

- **Current state** is what `Verification` is written against — the check
  that will tell the evaluator the wanted difference has actually landed
  starts from what the current state says is true today.
- **Wanted difference** is what `Outcome` states — the one measurable end
  state the run is finished once it reaches.

### The other two fields

`Constraints` and `Stop-when` are not sourced from either input slot. Both
are drafted by the agent from the same evidence and conversation context
that fills the two slots above, and each still carries its own provenance
tag under §5 like every field of the goal. Because they sit outside the
floor, an empty or missing `Constraints` or `Stop-when` does not by itself
trigger the refusal rule in §3 — that rule gates on the two input slots
only.

## 3 — Refusal

When either input slot is empty, the skill names the empty slot and emits no
goal.

Emitting a vague goal is worse than emitting none. A vague condition does
not fail loudly — it is re-evaluated every turn, and a vague condition may
be judged satisfied immediately, which ends a run that has not actually
produced the wanted difference. An empty slot that is named and refused can
be filled by the user on the next turn; a vague goal that is accepted looks
like progress while producing none.

## 4 — The bar

Once both slots are filled, the resulting condition still has to clear a
bar before it is a goal rather than a wish. This bar is stated here as prose
judgment — it is explicitly **not** a mechanical check the skill can run
automatically, and applying it is a call the agent has to make each time,
not a formula:

1. **Decidable** — the condition must be checkable true or false against
   evidence, not against opinion. A condition that cannot be decided either
   way fails this bar exactly the same way a condition that already holds
   does: neither one gives the run something to move toward and confirm.
2. **False when written** — the condition must not already be true at the
   moment it is written. A goal that already holds is not a goal; it is a
   description of the present dressed up as a target.
3. **Free of dependence on a person** — the condition must not depend on a
   person acting or answering. A condition that resolves only when someone
   takes an action or replies to a question is not decidable by the run
   itself; it is decidable by that person, which makes it their goal, not
   the run's. Such a condition never becomes a Stop-when branch — it has
   exactly two legitimate destinations instead. The goal can pre-decide it
   in `Constraints`, fixing the choice before the run starts. Or the goal
   can delegate it to the run itself, under the **Standing decision rule**
   in `goal-shape.md` §2, which lets the run decide, record, and continue
   without stopping to ask. Only an irreversible or outward-facing act
   still sits outside the run, reserved for the user.

## 5 — Provenance tags

Every field of a produced goal carries exactly one provenance tag, naming
where that field's content came from:

- **`user-said`** — the field's content is the user's own words, quoted
  directly.
- **`derived`** — the field's content was inferred, and the tag names the
  anchor (the file, message, or evidence) the inference was drawn from.
- **`proposed`** — the agent supplied the content itself, and the user has
  not yet confirmed it.

## 6 — The citation boundary

A recorded purpose — a `PURPOSE.md`, a brief, a spec, or any similar
standing document — is a source an agent quotes to justify an inference. It
is never authority to settle a choice reserved for the user, such as an
irreversible or outward-facing action, or a fork the user has not decided.
Citing the purpose can explain why a `derived` field was inferred the way it
was; it cannot substitute for the user's own decision on a choice that is
theirs to make.
