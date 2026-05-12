# Loop Classification Protocol — S/O Signing + R/B Diagnosis + Mermaid Annotation

The operational reference loaded by `cld-craft` Step 11 (fully-annotated
Mermaid emission). Encodes the link-signing primitives (S vs O), the
loop-type primitives (R vs B via even-O / odd-O), the regime-dependence
hand-off back into Rule 7's split-fuzzy-variable trick, and the
per-loop `%%` annotation format that downstream skills consume.

Two operational layers, inseparable in practice: **Layer 1** signs every
arrow; **Layer 2** counts O-links around closed loops. Skip Layer 1 and
Layer 2 is arithmetic nonsense; skip Layer 2 and Layer 1 is bookkeeping
with no dynamic payoff. Run both, in order, on every loop in the CLD
before emitting Mermaid.

> Adapted from Sherwood, *Seeing the Forest for the Trees* (Nicholas
> Brealey, 2002), Chapters 4-6. Previously a standalone skill
> (`loop-and-link-primitives`); absorbed into `cld-craft` in v0.4 because
> the two are operationally one workflow — you cannot draw a CLD without
> signing links and you cannot finish one without classifying loops.

## Layer 1 — Link signing (S vs O)

Every causal arrow carries a sign: **S** when cause and effect move in
the same direction (cause up → effect up; cause down → effect down);
**O** when they move in opposite directions (cause up → effect down;
cause down → effect up). Assignment proceeds in two tiers.

### Tier 1 — Reversibility shortcut

Ask the link two questions in order:

1. "If the cause increases, does the effect increase?"
2. "If the cause decreases, does the effect decrease?"

If both answers point the same way → **S**. If both point opposite →
**O**. Record the label in pen as you draw — Rule 8 forbids labeling as
a cleanup pass.

The shortcut **fails** when answers are asymmetric (cause up moves
effect, cause down does not, or vice versa). Common failure cases:

- **Uniflow** — birth rates, inflows, outflows; the cause is physically
  one-way. You cannot have negative births; population doesn't drop when
  births drop, it merely stops growing.
- **Stock-and-flow connection** — any inflow → stock or outflow → stock
  edge. The flow is a one-way pipe by physical construction.
- **Threshold or saturation** — small changes have no effect until a
  threshold is crossed, after which they do.

When Tier 1 fails, escalate to Tier 2.

### Tier 2 — Sterman's ultimate test (fallback)

Re-phrase the link using the counterfactual form:

> "Holding all else equal, when the cause is **above what it would
> otherwise have been**, is the effect **above what it would otherwise
> have been**?"

Same direction → **S**; opposite → **O**.

This form survives:

- **Irreversible flows** (pouring-in vs pouring-out; you can pour more
  in, you can't pour negative).
- **One-way physical processes** (BIRTHS → POPULATION; you can't have
  negative births).
- **Stock-and-flow connections** where Tier 1 returns nonsense (e.g.
  Lake Chad: INFLOW → LAKE VOLUME is S; OUTFLOW → LAKE VOLUME is O).

The Sterman form is **mandatory** for any link representing an inflow
or outflow on a stock-and-flow diagram. When you commit a label via
Tier 2 on a uniflow, document "uniflow" alongside the label in the
audit metadata (downstream consumers may need to know the link was
signed under Sterman discipline rather than reversibility).

### Tier 1 → Tier 2 escalation rule

For every link in the CLD, run Tier 1 first. The moment an answer is
asymmetric, or the link involves an inflow / outflow / one-way process,
**stop Tier 1 and run Tier 2**. Do not pick a label by gut. Do not
average the answers. Do not skip the test "because the sign is
obvious" — the obvious answer is often wrong on uniflows (ce09 coffee
example: reversibility says "less coffee in lowers the level," which is
true but causally backwards — there's no causal mechanism by which
"pouring less" *reduces* the level; the level merely fails to rise).

## Sign-flip / regime-dependent link detection

Before committing any S or O label, ask one more question:

> "Is there a value of the cause variable at which the sign of the
> effect would flip?"

Common patterns triggering yes:

- **Saturation** — first units of input deliver high return; later units
  deliver near-zero (advertising → sales above a spend threshold).
- **Threshold** — effect kicks in only above a level (regulatory burden,
  network effects, social proof cascades).
- **Inverted-U** — modest input is constructive, excessive input is
  destructive (workload → performance, generosity → productivity,
  pressure → cognitive throughput).
- **Crowding-out** — input helps until a substitution mechanism
  reverses it (financial incentives → intrinsic motivation, monitoring
  → trust).
- **Burnout-by-pressure** — pressure improves output until staff
  burnout, then collapses it.

**Halt condition — if regime-dependence is plausible, do NOT pick a
single S or O label.** Hand off to `cld-craft`'s Rule 7 split-fuzzy-
variable trick: replace the single link with two parallel intermediate
fuzzy variables —

- `EFFECT OF [cause] IN INCREASING [effect]` — S, saturating curve.
- `EFFECT OF [cause] IN DEPLETING [effect]` — O, threshold-triggered
  curve.

Both connect from the cause to the effect; each carries a single clean
S or O. The net behavior emerges from their interaction. This preserves
the even-O / odd-O classification at Layer 2 while admitting the
non-monotonicity. See `cld-craft` Step 5 for the trick's operational
form, and `cases.md` Case 4 (generosity → productivity) for the worked
example.

## Variance convention audit

A subtle, high-cost failure mode (ce27): variance-based links flip sign
when the convention is reversed.

- If variance is defined `TARGET − ACTUAL`: positive variance =
  under-budget = good; the link **variance → action** is signed under
  one direction.
- If variance is defined `ACTUAL − TARGET`: positive variance =
  over-budget = bad; the same link flips three of four labels in a
  variance → action → actual → variance loop.

This is a notation change, not a reality change — the physical system
behaves identically. But the diagram lies if you forget to relabel.
The same loop will be classified R under one convention and B under
the other; predictions will be exactly wrong.

### Audit procedure

When the CLD contains any variance, gap, or signed-difference node:

1. Document the variance direction next to the diagram (e.g.,
   "variance = TARGET − ACTUAL throughout").
2. If the convention changes mid-project, **every S/O label in the
   variance loop must be re-audited**. Do not assume "we just renamed
   it" — three of four labels typically flip.
3. Run Tier 1 / Tier 2 again under the new convention. The R/B
   classification may invert.

See `cases.md` Case 5 for the canonical example (mid-project relabel
that turned a self-stabilizing system into a predicted runaway).

## Layer 2 — Loop classification (R vs B)

Every closed feedback loop falls into exactly one of two types. To
classify, **trace the loop once and tally the O-links**.

| O-count | Loop type | Behavior |
|---|---|---|
| 0 (zero) | Reinforcing (R) | Amplifies in whichever direction it is spinning; exponential |
| 2, 4, 6 (even) | Reinforcing (R) | Same as zero; pairs of O cancel |
| 1, 3, 5 (odd) | Balancing (B) | Seeks a target; under delay, oscillates |

The arithmetic theorem (even-O = R, odd-O = B) **holds only if every
link is a fixed S or O**. If any link is regime-dependent and you
haven't applied the split-trick, the count is meaningless. Run the
Layer-1 regime check on every link before counting.

### R-loop spin-direction protocol

A reinforcing loop's *structure* is identical whether it is currently
a virtuous circle (spinning up) or a vicious circle (spinning down).
They are not opposites; they are the **same loop with opposite spin**,
separable only by the current direction of the variables and the
external trigger that started or could flip it.

For each R-loop in the CLD, run:

1. **Pick one node in the loop.** Ask: "Is this currently rising or
   falling?"
2. **Trace forward through the labels.** Apply each S/O to the
   trajectory. An R-loop in virtuous spin pushes every node up; in
   vicious spin, every node down. (If trajectories are inconsistent,
   you've mis-signed a link or mis-traced — recheck.)
3. **Tag every node with its current trajectory** (↑ or ↓) on the
   diagram.
4. **Name a plausible flip-trigger.** Look at the input dangles
   (external drivers spinning the loop) and the fuzzy thresholds within
   it. What single event could reverse the spin?
   - Ratner-style (`cases.md` Case 3): a single utterance / signal.
   - Hatfield-style (`cases.md` Case 2): a single external shock event.
   - Saturation-style: the engine hits a constraint (input dangle dries
     up, fuzzy threshold flips a downstream link).

**Output**: each R-loop should have (a) every node tagged with current
trajectory, (b) at least one named, plausible flip-trigger documented
in the audit metadata. The diagnostic question is never "is this loop
good or bad" but "which way is it spinning and what could flip it."

Slow drift is the early-phase signature of an exponential — not noise,
not a lagging indicator. The "frogs and lily-pad" intuition (Sherwood
Ch 5) is the calibration: at day 49 the pond is still half-empty, and
the visible drift looks tame.

### B-loop target + delay protocol

A balancing loop seeks a target and, under delay, oscillates around it.
For each B-loop, run:

1. **Identify the target dangle.** Where does the loop "want" to go?
   The target is usually external to the loop (a set-point, a budget,
   a regulatory threshold) — drawn as a `target dangle` (hexagon
   `{{...}}`) per Rule 1.
2. **Identify the delay magnitude.** How long between action and
   effect? Categories — `short` (sub-quarter), `medium` (quarters /
   years), `long` (years / decade-plus). If the delay is non-trivial,
   **expect oscillation** as the default behavior; do not interpret
   oscillation as a failure of the system.
3. **Estimate amplitude.** Rough qualitative scale ("small / moderate /
   large oscillation around target"). Amplitude grows with delay
   length and with the gain (sensitivity of action to variance).

**Output**: each B-loop should have (a) named target dangle, (b)
qualitative delay magnitude, (c) qualitative amplitude expectation in
the audit metadata.

See `variance-target-action-template` for the generic B-loop template
once you've classified the loop here.

### Dynamic prediction statement

After classifying every loop, write one sentence per loop:

- For R-loops: "This is an R-loop currently spinning [virtuous /
  vicious]; barring trigger [X] it will continue to compound at roughly
  [Y]% per period."
- For B-loops: "This is a B-loop seeking target [T] with delay [D];
  expect oscillation of amplitude [A]."

This statement is the **dynamic prediction caption** appended below the
Mermaid block in Step 11.

## Vicious = virtuous: the structural-identity insight

A reinforcing loop diagnosis must always be paired with **trigger
identification**, not just structural classification. The canonical
proofs are in `cases.md`:

- **UK back-office (c01)** — same R-loop spun vicious because workload
  was overwhelming; would have spun virtuous if WORKLOAD were relieved
  via the EFFECTIVE IT SYSTEMS input dangle.
- **Hatfield Rail (c05)** — Railtrack's reputation R-loop spun virtuous
  for years; one derailment flipped it, and the same loop drove the
  bust at the same pace it had driven the boom. ~12 months to
  bankruptcy.
- **Ratner Jewelry (c06)** — single sentence at the 1991 Institute of
  Directors speech flipped a reputation R-loop. Customer base
  evaporated within weeks. Same loop, opposite spin, same compounding
  speed.

The structural classification (R) tells you the *kind* of dynamic;
the trigger identification tells you which way it's running and what
could flip it. Both halves are mandatory output.

## Per-loop Mermaid `%%` annotation format

After all loops are classified per Layer 1 + Layer 2, annotate the
Mermaid block. Per `cld-mermaid-emit.md`, every closed loop gets one
`%%` comment line directly below the edge declarations of that loop:

### R-loop annotation

```
%% R-loop (<spin>): <node1> → <node2> → ... → <node1> — O-count = <N> → reinforcing
```

Concrete example:

```
%% R-loop (virtuous): Customer Trust → Repeat Orders → Revenue → Marketing → Brand Reach → Trust — O-count = 0 → reinforcing
```

Required fields:

1. **`R-loop`** prefix.
2. **`(<spin>)`** — `virtuous` or `vicious` if known from prose; omit
   parenthetical if unknown.
3. **Traversal path** — nodes in order, separated by `→`, returning to
   the starting node.
4. **O-count** — integer (0, 2, 4, ...) justifying the R classification.

### B-loop annotation

```
%% B-loop: <node1> → <node2> → ... → <node1> — O-count = <N> → balancing; Target is <target dangle>
```

Concrete example:

```
%% B-loop: Variance → Action → Actual → Variance — O-count = 1 → balancing; Target is Target Stock Level (target dangle)
```

Required fields:

1. **`B-loop`** prefix.
2. **Traversal path** — nodes in order, returning to start.
3. **O-count** — odd integer (1, 3, 5, ...) justifying the B
   classification.
4. **Target dangle** — name and dangle-type designation.

### Loop coupling annotation

When two loops share a node and form a recognizable archetype (most
commonly limits-to-growth: an R-loop braked by a B-loop), add a third
`%%` line:

```
%% Loop coupling: limits-to-growth archetype — R-loop spinning <spin> is braked by B-loop on <braking node>
```

See `cld-mermaid-emit.md` "Worked example" section for a full
prose-to-Mermaid demonstration including loop coupling.

### Markdown caption (post-block, mandatory)

Some Mermaid renderers strip `%%` comments. To guarantee downstream
parsers (and human readers) see the classification, **append a Markdown
caption directly below the Mermaid block**:

```
**Loop diagnosis:**
- R-loop (virtuous spin): Trust → Referrals → Revenue → Support → Quality → Trust (O-count = 0, reinforcing). Flip-trigger candidates: support team overload, single PR crisis.
- B-loop: Trust → Volume → Quality → Trust (O-count = 1, balancing). Target = quality threshold; delay = weeks.
- Dynamic prediction: limits-to-growth archetype — virtuous R-loop will plateau as B-loop bites.
```

This caption MUST repeat the per-loop dynamic prediction sentences from
the Layer-2 protocol, so even renderers that strip comments preserve
the diagnosis.

## Halt conditions for Layer 1 + Layer 2

Stop the protocol and either escalate, redraw, or reject the diagram if:

- **Tier 2 also returns asymmetric / nonsense answers.** The "link" may
  not be causal — re-examine whether you've drawn a definitional
  identity (revenue − costs = profit) rather than a behavioral causal
  link. Definitional identities are not CLD edges; remove them.
- **Regime-dependence and the split-trick has not been applied.** The
  classification is meaningless without honest single-sign labels on
  every edge. Apply the split-trick (Rule 7 in `cld-craft`) before
  counting Os.
- **No closed loop traces.** A pure tree of dangles isn't a system —
  R/B is undefined. Either the CLD is incomplete (missing return arc),
  or it's actually a chain / sequence (use a different diagram form).
- **Statistical correlation only, no causation claimed.** CLD edges
  encode causal claims; correlation alone is not a link. Remove the
  edge or re-justify it causally.
- **Stochastic-noise input mis-labeled as loop member.** Weather,
  exogenous shocks, regulatory events are dangles, not loop members.
  Promote to a dangle (input or cloud).

## Audit metadata to record per loop

When emitting Step 11 output, record in the post-block caption:

- Loop ID (R1, R2, B1, ...) — useful when multiple loops share nodes
- Type (R / B)
- O-count (integer)
- Traversal path
- For R: current spin (↑↓), flip-trigger candidates
- For B: target dangle, delay magnitude, amplitude
- Uniflow flags on any edge where Tier 2 was used
- Convention notes on any variance-direction definitions

This metadata is the input contract for downstream skills
(`limits-to-growth-take-the-brakes-off`, `variance-target-action-template`,
`stakeholder-and-team-thinking`). Keep it self-contained in the caption
so a downstream consumer can parse the Mermaid block + caption alone
without re-running this protocol.

## Source provenance

This protocol is distilled from:

- Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002),
  Chapter 4 (S/O signing, reversibility test, generosity split-trick),
  Chapter 5 (R/B classification, even-O/odd-O rule, vicious=virtuous
  structural identity, frogs and lily-pad calibration), Chapter 6
  (variance convention audit ce27), Chapter 12 (Sterman ultimate test,
  uniflow discipline, Lake Chad).
- Originally distilled as standalone skill `loop-and-link-primitives`
  (sk01 + sk02 merge per Profile B); absorbed into `cld-craft` in v0.4
  to consolidate the draw-and-classify workflow into a single
  invocation.

See `cases.md` (Cases 4-9 originally from sk01+sk02) for the worked
examples this protocol calibrates against.
