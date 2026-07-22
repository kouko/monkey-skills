---
name: construction-guaranteed-invariant-proves-nothing
description: An invariant that holds BY CONSTRUCTION (both sides derived from the same operation) validates nothing about whether that operation was semantically right — `text[start:end] == token` held on every one of six fabricated numbers; when the trust rail is construction-guaranteed, the real risk is upstream of it.
type: practice
origin: branch feat-prose-kpi-part-2 (2026-07-20) — six instances of one class across three whole-branch review rounds, each found by a reviewer executing an exploit string by hand
---

The 8-K prose KPI chain's load-bearing anti-fabrication rail is
`canonical_text[start:end] == matched_token`. It is guaranteed **by
construction**: both the token and the span come from the same regex
match, so it cannot fail. That made it feel like protection. It is not.

Six separate defects shipped a *fabricated* number wearing a perfectly
valid anchor:

| input | token | committed value |
|---|---|---|
| `Fiscal 2026<nbsp>250,000 units` | `2026,250,000` | 2.0e9 (3 orders off) |
| `fiscal 2026 billion-dollar program` | `2026 billion` | 2.026e12 |
| `1,428<nbsp>500-mile trucks` | `1,428,500` | fused two figures |
| `<li>45,000</li><li>Million Air…` | `45,000\nMillion` | 4.5e10 |
| `…45,000</p><table>…</table><p>million…` | fused across an **excised table** | 4.5e10 |
| `<pre>45,000\nMillion Air…</pre>` | `45,000 Million` | 4.5e10 |

Every one satisfies the gate. The anchor is real; the *phrase it anchors
to* is one nobody wrote.

**Why:** a construction-guaranteed invariant answers "did I record where I
found this?" — never "was this the right thing to find". Reviewers (and
authors) read the green gate as coverage and stop looking upstream, which
is exactly where the whole risk lives. The recurring root cause here was
narrower still: the surface's real invariant (*a newline means a block
boundary, and every rendered break becomes a newline*) lived only in
**prose comments**, never as an executable check — and two of the six
defects were caused by a comment overstating its guard's coverage, then
being believed.

**How to apply:**

1. For any invariant, ask **"can this ever fail?"** If the answer is no
   because both sides derive from one operation, it is a *bookkeeping*
   check, not a *correctness* check. Say so in its docstring so the next
   reader does not bank on it.
2. Put the correctness risk where it actually is — in whether the match
   is semantically right — and test THAT with adversarial inputs, not
   with the invariant.
3. When an invariant is stated as a biconditional in a comment, treat the
   **converse** as untested until something executes it. Five of the six
   instances came from the converse silently failing.
4. Six hand-found instances of one class is the signal to stop
   point-fixing and build the structural check. Related:
   [[assertion-must-encode-the-property-it-claims]] (a guard whose
   predicate cannot encode its claim) — same family, different failure:
   there the assertion is unrelated to the claim, here the assertion is
   *true but empty*.

**The class recurs beyond string anchors — binary float is the same shape.**
The follow-on slice (branch feat-kpi-obs-history, 2026-07-22) compared KPI
values across filings by `value × scale`. Written in binary float,
`1.005 × 1e9 == 1004999999.9999999`, so two records of the *same* figure
(one lane storing `1005000000`, another `1.005` at scale `1e9`) compared
UNEQUAL — a fabricated "restatement" flag on data that never changed,
hitting 1.4–5.1% of realistic two-decimal cells. The multiply "cannot be
wrong" arithmetically, yet it manufactured the exact false signal the
feature existed to avoid. The same module family had **already** closed
this once (`_normalize_value` uses `Decimal` with a docstring naming the
hazard) — the defect reopened at *compare* time after being fixed at
*fold* time. And only an adversarial decimal exposes it: `301.63 × 1e6` is
float-exact and passes while the code is wrong; `1.005 × 1e9` is not. So:
**any cross-layer arithmetic on money/count values goes through `Decimal`,
never binary float** — and a test value must be chosen to be
float-*hostile* (a non-terminating binary fraction), or a green suite
proves nothing.

Related: [[changing-what-a-token-is-defeats-downstream-guards]] (the
mechanism by which most of the six string-anchor instances were
introduced); [[retiring-a-mechanism-must-move-its-tests]] (removing the
read-time scaler dropped its adversarial word-boundary test).
