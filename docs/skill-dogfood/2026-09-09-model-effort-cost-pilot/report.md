# Main-relative model/effort cost pilot

Date: 2026-09-09

## Result

On this one complex policy-review corpus, `frontier/low` was **not cheaper**
than `standard/medium`. It cost 80.1% more on the two-run mean and 34.1% more
on the cache-warm replicate. It was 30.9% faster on mean wall time and found
substantially more of the nine previously established required changes.

This supports retaining `frontier/low` as comparison and calibration evidence
for complex work. It does not support using that profile as a general
cost-saving substitute for `standard/medium`, nor does it define final routing.

## Frozen method

- Corpus: `../2026-09-09-loom-main-relative-dispatch-plan/claude-review-packet.md`
- Corpus SHA-256:
  `eafe902d69b4ff1c0afe311ea76e065b4a4c6af5787cc9c985856d27d4384de2`
- Prompt SHA-256 for every arm:
  `c15d68169ddf4d140c46e21a1bc79558e662b7a4c8f44667df3a6d0d9e123524`
- Replicates: two independent sessions per profile
- Tools and prior sessions: disabled by prompt and CLI permission controls
- Per-run hard budget: USD 1.00
- Quality oracle: the nine blocking changes in
  `../2026-09-09-loom-main-relative-dispatch-plan/claude-independent-review.md`
- Raw result, stderr, and invocation metadata are retained beside this report.

This is a controlled policy-review pilot, not a formal `SKILL.md` activation
dogfood. No `dogfood-pass` marker is warranted.

## Control-plane verification

| Arm | Requested | Verified canonical model | Verified session effort |
|---|---|---|---|
| S1 | sonnet / medium | claude-sonnet-5 | medium |
| S2 | sonnet / medium | claude-sonnet-5 | medium |
| O1 | opus / low | claude-opus-5 | low |
| O2 | opus / low | claude-opus-5 | low |

The result JSON's `modelUsage.canonicalModel` supplies the model evidence. The
persisted session JSONL matching each recorded session id supplies the effort;
generated answer text was not accepted as configuration evidence. Claude also
used a small Haiku structured-output helper on every arm; its USD 0.00313-ish
cost is included consistently in every total below.

## Cost and latency

| Arm | Cost USD | Wall time | Output tokens | Thinking tokens | Prompt cache |
|---|---:|---:|---:|---:|---|
| S1 | 0.1658040 | 78.733 s | 7,232 | 5,043 | create 22,585 |
| S2 | 0.0997010 | 102.390 s | 9,205 | 6,757 | read 22,585 |
| O1 | 0.3446350 | 59.339 s | 4,293 | 1,381 | create 23,417 |
| O2 | 0.1336735 | 65.757 s | 4,753 | 1,449 | read 23,417 |

| Profile | Two-run total | Mean cost | Mean wall time |
|---|---:|---:|---:|
| standard / medium | 0.2655050 | 0.1327525 | 90.562 s |
| frontier / low | 0.4783085 | 0.2391543 | 62.548 s |

- Total experiment cost: USD 0.7438135.
- Mean cost difference: `frontier/low` +80.1%.
- Cache-warm replicate difference: `frontier/low` +34.1%.
- Mean wall-time difference: `frontier/low` -30.9%.
- The first call per model created a model-specific prompt cache; the second
  read it. Comparing only aggregate token counts would therefore be misleading.

## Known-change recall

The oracle contains these nine required changes: frontier-only high; model
ceiling fall-through to effort; two-redispatch cap; explicit
frontier/medium no-op; unknown capability handling; narrow complex criteria;
repair insufficient packets; model-first mechanical downgrade; and an honest
effort-only dogfood claim.

Credit is given only when the output identifies the underlying defect or asks
for the corresponding repair. Merely discussing the same section is not
credit.

| Oracle item | S1 | S2 | O1 | O2 |
|---|:---:|:---:|:---:|:---:|
| High requires frontier | – | – | – | – |
| Frontier model ceiling falls through to effort | – | – | – | – |
| At most two redispatches | – | – | – | ✓ |
| State frontier/medium complex no-op | ✓ | ✓ | ✓ | ✓ |
| Unknown capabilities are handled before dispatch | ✓ | ✓ | ✓ | ✓ |
| Narrow complex classification | – | – | ✓ | ✓ |
| Repair insufficient packet before routing | – | – | ✓ | ✓ |
| Mechanical downgrade changes model first | – | – | ✓ | ✓ |
| Dogfood claim covers effort only | – | – | ✓ | ✓ |
| **Recall** | **2/9** | **2/9** | **6/9** | **7/9** |

Both profiles reached the correct overall `ACCEPT_WITH_CHANGES` verdict. The
frontier/low runs recovered a much larger portion of the known corrective
set and also found coherent additional state-machine issues. Neither profile
found the frontier-only-high rule or the distinct model-ceiling fall-through
rule, so the stronger profile was not complete.

## Precision cautions

The oracle is not exhaustive, so novel findings were adjudicated for internal
support rather than automatically counted false.

- S1 proposed retaining a supported effort override when the model override is
  rejected. That contradicts the proposal's deliberate atomic-profile rule;
  count it as an unsupported recommendation, not a required fix.
- O1 called the stated "three existing files" count wrong by counting agent
  files that the proposal explicitly says should remain unmodified. That is a
  factual overreach, although the provisional line estimate still deserved
  deletion.
- Several outputs treated the intentionally clamped `frontier/medium` no-op as
  necessarily defective. The real requirement was to make it explicit, not to
  permit initial high. Recall credit above is limited to that clarification.
- O1 and O2 surfaced useful additional type/state concerns, especially mixing
  routing outcomes with station outcomes and failing to represent the
  unobservable-main path. Those are plausible new findings, not part of the
  nine-item oracle.

## Decision for the dispatch design

Keep the planned ordering, with a tighter economic interpretation:

1. Ordinary tasks remain at the main agent's profile.
2. Mechanical tasks lower the model one tier and preserve effort initially.
3. A checkably complex task may move `standard/medium` to `frontier/medium`,
   or `standard/low` to `frontier/low`, because the upgrade buys review recall
   and latency here — **not because it saves money**.
4. Do not automatically replace `standard/medium` with `frontier/low` merely
   to reduce reasoning effort; this pilot measured the opposite cost result.
5. Preserve the initial-high clamp and require observed failure evidence before
   entering high.

## Limits

- One 1,174-word policy-review corpus, two replicates per arm. This does not
  estimate coding, search, mechanical-edit, or long-context performance.
- Alias mapping is time-sensitive: this run resolved to Claude Sonnet 5 and
  Claude Opus 5. Future aliases require re-verification.
- Prompt-cache creation differed between first and second runs, so both cold
  and warm comparisons are reported; neither is a universal workload mix.
- The nine-item oracle came from a prior Opus/medium review and may favor the
  kinds of issue Opus tends to express. It is independently useful because the
  changes were incorporated into the revised policy, but it is not a neutral
  human benchmark.
- Structured JSON output invoked a small Haiku helper equally in all arms.
  These measurements describe the actual Claude Code execution path, not only
  the primary model API call.

## Stage 1 extension: effort marginal cost

After the initial interpretation, the pre-registered staged extension added
two independent `standard/high` runs and two independent `frontier/medium`
runs. Corpus, prompt hash, schema, isolation, and oracle remained identical.

### Verified execution and measurements

| Arm | Verified profile | Cost-equivalent USD | Wall time | Output tokens | Thinking tokens |
|---|---|---:|---:|---:|---:|
| SH1 | claude-sonnet-5 / high | 0.2088740 | 121.267 s | 11,540 | 8,650 |
| SH2 | claude-sonnet-5 / high | 0.1289510 | 123.315 s | 12,129 | 9,653 |
| OM1 | claude-opus-5 / medium | 0.5681085 | 131.384 s | 10,138 | 3,638 |
| OM2 | claude-opus-5 / medium | 0.3385870 | 126.202 s | 9,776 | 3,652 |

The Claude Code sessions were authenticated through the user's Claude Max
subscription. These USD values are API-list-price equivalents reported by the
CLI, not incremental charges.

| Profile | Mean equivalent cost | Mean wall time | Oracle recall per run |
|---|---:|---:|---|
| standard / medium | 0.1327525 | 90.561 s | 2/9, 2/9 |
| standard / high | 0.1689125 | 122.291 s | 2/9, 2/9 |
| frontier / low | 0.2391543 | 62.548 s | 6/9, 7/9 |
| frontier / medium | 0.4533477 | 128.793 s | 5/9, 6/9 |

Relative to the same-model lower-effort profile:

- Sonnet high versus medium: mean equivalent cost +27.2%, wall time +35.0%,
  no known-change recall gain.
- Opus medium versus low: mean equivalent cost +89.6%, wall time +105.9%,
  no known-change recall gain; recall was lower in this small sample.
- Eight accepted runs together reported USD 1.988334 of API-price-equivalent
  usage under the subscription.

### Interpretation

On this corpus, increasing effort expanded the amount and scope of analysis but
did not improve recovery of the established required-change set. It also added
unsupported or policy-opposed recommendations, notably partial override
fallback and treating the intentional initial-high clamp as a reason to permit
high. More text and more reasoning tokens were not a quality proxy.

The following sparse ladder records the historical experiment design used to
choose useful comparison cells; it is not the final routing policy:

```text
standard/medium --complex capability upgrade--> frontier/low
frontier/low --observed depth failure----------> frontier/medium
frontier/medium --strict high trigger----------> frontier/high
```

`standard/high` is dominated for this task by `frontier/low`: the latter had
higher oracle recall and much lower latency, while the cost-equivalent gap was
far smaller than the quality gap. In this historical experiment design,
`frontier/medium` was reserved for an observed reasoning-depth failure. This
stage supplies no reason to add `standard/high` or `frontier/high` to the
initial-routing menu; the final policy below separately governs initial routes.

The final routing contract supersedes that experimental ladder: a complex
initial route preserves effort, so `standard/medium` → `frontier/medium`.
`frontier/low` remains comparison and calibration evidence, and is also the
effort-preserving result when the observable main profile is `standard/low`;
it is not an automatic effort downgrade from `standard/medium`.

Stage 1 still has only one corpus and two samples per cell. The result is strong
enough to avoid eager high-effort routing, not to claim that high never helps.

## Reduced follow-up scope after external review

The next Claude matrix stage was stopped after one unreplicated `sonnet/low`
run. Its raw evidence is retained but is not used for a comparative conclusion.
Published experiments already cover the generic effort curve more broadly and
with stronger replication than this local pilot can economically reproduce.

Remaining Loom-owned evidence is limited to:

- three two-arm, two-replicate Codex calibrations: mechanical model downgrade,
  implementation low-versus-medium effort, and complex-review cross-upgrade;
- deterministic exhaustive tests for routing arithmetic and fallback states;
- one live adapter success and one forced unsupported-override fallback probe
  on each host.

The reduction removes further Claude matrix cells, initial high/xhigh/max
profiles, and repeated provider-wide benchmark duplication. It preserves the
three uncertainties public studies cannot settle for Loom: its task classifier,
its host tier mapping, and its automatic fallback behavior.
