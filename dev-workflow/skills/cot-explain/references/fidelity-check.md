# The fidelity check

Step 6 of `SKILL.md`. Run this before a page goes to anyone who was not
there. Steps 4 and 5 prove the page is well-formed; they prove nothing
about whether it represents the source honestly, and **no mechanical
check can** — a diagram whose every node is well-shaped and whose every
edge is labeled can still hand the reader a conclusion the source
refutes.

The method is a **simulatability-style round-trip**: forward simulation
(Doshi-Velez & Kim 2017), refined as Leakage-Adjusted Simulatability
(Hase et al. 2020), plus a hallucination pass borrowed from QA-based
faithfulness evaluation.

**Round 1 — blind reconstruction.** Dispatch a fresh agent that may read
**only the generated HTML**. Forbid it from opening the source, the
repo, or anything else, and require it to say so if it learns anything
from outside — a contaminated reconstruction silently passes a test it
should fail. Ask it for: the reasoning in its own words; the causal
claims it would now repeat; what it feels is asserted but unexplained;
what questions it is left with.

**Round 2 — comparison.** Dispatch a second agent that reads **the
source and round 1's reconstruction, but never the page**. Seeing the
page makes it grade prose instead of effect. Ask for: misunderstandings
(with damage rating), omissions that change a conclusion, unearned
confidence where the source hedges, and — the most useful question —
for each thing round 1 flagged as unexplained, whether the source
supplies the missing justification (the summary dropped it) or is
equally silent (the summary faithfully reproduced a real gap).

**Round 3 — hallucination.** List every node and edge in the diagram and
check each against the source. Round 1 and 2 measure what was lost; only
this measures what was invented. Anything with no basis in the source is
a defect regardless of how plausible it reads.

**Leakage caveat.** A page that restates its conclusion verbatim scores
well on naive reconstruction without being faithful — the reader is
copying. When round 1 comes back suspiciously aligned, check whether the
page gave the answer away.

### Recording the verdict

Write the outcome to `<name>.fidelity.md` beside the page, opening with:

```
verdict: PASS
reviewed_md_sha256: <output of verify_cot_html.py --sha <file>.html>
```

The hash is what makes the verdict about *this* page. Without it
`--stamp` records nothing; if the markdown changes afterwards it refuses
again and tells you to re-run. A verdict that outlives the thing it
judged is the same failure as a stale render.

Then run the two commands that carry the verdict onto the page — the
verdict file alone changes nothing a reader sees:

```
python3 scripts/verify_cot_html.py --render --stamp <file>.html
python3 scripts/render_cot_html.py <file>.md
```

**Keep `--render`.** The outcome written into `verified:` is computed
from *this* invocation's flags, not carried over from Step 5, so stamping
without it rewrites `pass --render` down to `pass` — silently discarding
the record that the mermaid parser actually validated the diagram, when
nothing about that validation has changed.

The first reads the verdict file and writes `fidelity_checked:` into the
markdown; the second rebuilds the HTML from it. Stop after the first and
the page still reads 忠實度檢查：未執行 — the check ran, and the page
says it did not, which is the same class of lie in the other direction.
`--stamp` prints exactly what it wrote; if it says the markdown has no
`fidelity_checked:` line, the verdict was **not** recorded.

### What gates

Not every finding blocks. The split follows what the reader would *do*
with the belief, and it is the same shape as `docs-review`'s
instruction/evidence classes:

| Finding | Gates? |
|---|---|
| A statement the reader believes that the source contradicts | **Yes** |
| A hallucination — anything with no basis in the source | **Yes** |
| A dropped clause that changes what gets built | **Yes** |
| A dropped *reason* — the instruction survives, the justification does not | No — recorded |
| Compression, emphasis, ordering | No — recorded |

The line is whether the reader ends up **wrong** or merely **short**. A
gap sends them back to the source; a false belief does not, because they
have no reason to look. That asymmetry is why the first three gate and
the rest do not — and why a run producing many recorded findings can
still be safer than one producing a single confident error.

A finding whose class is unclear gates. Fail closed.

### The fix cycle, and where it stops

Adapted from `loom-code:requesting-docs-review`, which faced the same
problem: prose has no test to terminate on.

- **Rounds 1–3 are the only full check.** No round cap, no re-sampling.
  Nothing gating → done.
- **On a gating finding: fix the `.md`** — never the HTML — then re-run
  Step 5's three commands, then confirm:
  - dispatch a **fresh** blind reconstructor. This one cannot be
    delta-scoped: an agent that has read the page is no longer blind, and
    blindness is the instrument.
  - `SendMessage` the **same** comparator from round 2, handing it the
    new reconstruction and the findings that gated, **scoped to those** —
    never a fresh whole-source re-read. It answers `CONFIRMED_RESOLVED`
    or `STILL_BLOCKING` + reason.
- **`STILL_BLOCKING` after that one cycle → STOP.** Surface the finding
  and the comparator's reason to the user. No second cycle, and no
  fallback to a fresh full check, without their explicit say-so.
- **If the session dies before the confirmation lands**, do not resume
  it: run one fresh full check instead.
- **The terminal state is "no gating findings", never "faithful".** Six
  measured rounds never reached zero findings; a round that raises
  nothing is evidence about that sampling, not about the page.

Fixing is allowed here, unlike in docs-review, because the page is
generated rather than authored. The obligation that survives is
disclosure: **report what the check found even when you fixed it.**

