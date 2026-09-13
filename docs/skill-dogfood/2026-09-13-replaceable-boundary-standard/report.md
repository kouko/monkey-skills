# Boundary decision evidence — needs reshape

## Metadata

| Field | Value |
|---|---|
| Date | 2026-09-13 |
| Baseline | e42482b1fb89f55c4f666921f7757ea3b0fd8f53 |
| Candidate | ff4f58844002095ea04b6cf2b4cc9f0596c2604d |
| Runner and auditor model | gpt-6-astra, medium (host identifier; no dated weight revision exposed) |
| Scope | Matched cold-read station decisions E/C/S |
| Activation | Not applicable: description and routing unchanged |
| End-to-end execution | Not run; no whole-skill dogfood verdict |
| Status | NEEDS_RESHAPE — the frozen improvement bar was not met |

The dogfood executor/blind-auditor method is used for a bounded decision
comparison. The complete real resolver is the source fixture; the requested
changes are hypothetical scenarios. Runners produce concrete interface/test
proposals, not executed feature implementations. Thus this measures decision
quality only, not realized dependency reduction, runtime correctness, or agent
token savings. Probe A and full Probe C are outside this scoped experiment.

The report-template request for raw trajectories is narrowed by the approved
plan's privacy constraint. Complete normalized final artifacts and observable
action summaries are retained below; raw tool/system streams remain private.
Normalization changes only neutral arm labels and omits operational metadata;
it must preserve decisions, evidence, limitations, and proposed tests.

## Fixed identities (SHA-256)

| Resource | Baseline | Candidate |
|---|---|---|
| Source fixture | 07b6d78efeb76c7d027433515926e50acbe65ce4355231584ae1f93fe34b3dd1 | same |
| write-plan contract | e4c249bae4a5badbd15c258fbfe6d4d2d920e9eba58329fa2ee05bfe573c0da4 | 63f95cacfc443b5cf93c1f541298a3cd0d034ad7b8d419a80e8b8f307b37ac50 |
| implementer contract | 156d2be59413777f65c369025d1bea19c81e6b9304881bef11a99f8dd4b81691 | 32f2aa34948ef1a32fc731583eca7bac73391918b70bd02272ca5c42a19606ff |
| review lenses | b2423a59a8e38d6c840a85ec0af9e8de3fb3de2a9c06deced1a1dfb8a9c779b4 | 183c935f3873665aacc7c6b17449a957b1ed6b86ae2dee4eaf6b431e44da6573 |

Frozen cases SHA-256: cad5a71af9844296d55d9dd473e502376908c2834801ee8834be7c5b62dc87db.

## Mechanical and test evidence

- Initial RED: focused probe test reported 6 passed, 1 failed because this
  behavioral report did not exist yet.
- Final focused replay: 6 passed, 1 failed because both auditors found the
  baseline correct too. GREEN was not achieved; the assertion was not weakened.
- Mechanism check against the fixed baseline: 119 to 119, delta 0, exit 0.
- Complete package suite: deferred to Closing Review, not run here.

## Outcome and severity summary

Both independent auditors scored both arms correct in all three cases. Arm X
is the baseline; arm Y is the candidate. E changed the proposed file layout,
but the baseline's existing pure API is also sound. S has no new correct
finding absent from the baseline. C has no new false positive. The admission
bar is unmet; this is not evidence that modularity is harmful or that the
candidate can never help another repository.

No implementation defects were established by these bounded proposals:
Critical 0, High 0, Medium 0, Low 0. The failed improvement requirement is
an experiment outcome rather than an invented skill defect. Static prose
pins cannot establish that added instructions earn their prompt cost.
Suggested direction: reshape the claimed benefit and carrier using evidence
of an actual missed boundary; do not relabel this tie as success or rerun
until a favorable sample appears. No contract edits were made by this probe.

One fresh runner per arm and two fresh auditors used the same host model
identifier and effort. No repetitions were made: both auditors agree on the
substantive tie, and this report makes no stability or statistical claim.
Auditors saw only neutral arm artifacts, the case/rubric section, and the
fixed source. Their individual judgments were hidden from each other.

```json evidence
{
  "auditors": ["audit-one", "audit-two"],
  "cases": {
    "E": {"baseline": ["correct", "correct"], "candidate": ["correct", "correct"]},
    "C": {"baseline": ["correct", "correct"], "candidate": ["correct", "correct"]},
    "S": {"baseline": ["correct", "correct"], "candidate": ["correct", "correct"]}
  },
  "existing_flow": true,
  "mechanism_delta": 0
}
```

Normalized output SHA-256, including each arm heading and following blank
line up to (excluding) the next arm/section heading:

- X: c9969b14dfa2e4602a2d93405bcf111a17e4598cdeebfd21c51004018b23acaf
- Y: 727864a6fc9d491808a5a460189de93d3c4cac35e056feec091ac815737ce9a7

Final artifacts below retain complete runner/auditor answers. Normalization
changed heading levels, removed markdown emphasis from table severity labels,
and replaced revision values in runner action summaries with assigned/fixed
revision labels. No substantive output was removed or revised. Scores above
are copied from the two auditors, not self-assigned by the executors.

## Normalized executor artifacts

### Arm X

#### E — Add a second input transport

**Decision:** Keep `dispatch_profile.py` as one file. Preserve `resolve(packet)` as the public policy boundary; add JSON-lines handling only in `main()`. The existing function boundary already lets an in-process caller bypass streams.

**Interface sketch**

```python
def resolve(packet: dict[str, Any]) -> dict[str, Any]:
    """Return one decision; raise InputError for malformed input."""

def main() -> int:
    """Select single-JSON or JSON-lines transport, decode, resolve, encode."""
```

A proposed `--jsonl` option selects the batch transport; invoking the existing command without that option retains single-packet behavior. Both paths call `resolve` once per decoded packet. No batch-policy class, registry, or extracted initial/retry modules are needed.

**Task boundary:** One transport task touching `loom-code/scripts/dispatch_profile.py` and a focused transport test file. Preserve the policy implementation. The task owns the single assertion that transport selection changes framing without changing packet decisions; positive and boundary tests support that assertion. Future in-process integration is a separate consumer task when that caller exists.

**Evidence**

- `main()` currently owns `json.load`, `json.dump`, stream access, diagnostics, and exit status.
- `resolve()` explicitly promises “without I/O or persistent state”; it accepts a decoded packet and returns a dictionary.
- `_initial` and `_after_execution` receive capabilities, inheritance, and redispatch count explicitly. Neither needs transport context.
- The case identifies a new batch caller and a future direct caller, but neither requires separate policy files to use this existing interface.

**Focused tests, proposed rather than executed**

- `test_jsonl_decisions_match_direct_resolve`: two valid lines produce two decision objects, in input order, each equal to a direct `resolve(packet)` result.
- `test_single_packet_cli_compatibility`: the original invocation retains compact sorted JSON, a trailing newline, exit code 0, and existing malformed-input behavior.
- `test_direct_resolve_has_no_stream_dependency`: use stdin/stdout objects that fail on access; direct resolution still returns the expected decision.
- `test_resolve_packets_do_not_share_capabilities`: resolve packets A, B, A with differing capabilities and verify both A results match.

The case does not specify malformed-line continuation, blank-line handling, or whether partial output is acceptable before an error. Those batch behavior choices need specification before implementation; they do not prevent choosing the policy/transport boundary.

#### C — Add one routing failure category

**Decision:** Add `"provider-busy"` to `NON_ROUTING_FAILURES` in the existing file. Splitting the resolver does not help this change.

**Task boundary:** One failure-classification task touching `loom-code/scripts/dispatch_profile.py` and its focused resolver tests. Keep the public interface `resolve(packet) -> dict` unchanged.

**Evidence**

- `FAILURE_KINDS` derives its accepted categories from `NON_ROUTING_FAILURES`, so adding the category once also admits it during validation.
- `_after_execution` already handles members of that set in both the conforming and nonconforming failure paths.
- The incomplete-attempt and redispatch-limit checks precede those branches. Matching `timeout` means preserving that precedence too.
- The stated explicit inputs, lack of shared mutable state, and direct test access provide no change-specific reason to extract several modules. File length alone does not identify a useful boundary.

**Focused test:** `test_provider_busy_matches_timeout`, parameterized over completed/incomplete attempts, conforming/nonconforming output, and redispatch counts 0–2. For otherwise identical failed-attempt packets, assert exact result equality when substituting `"provider-busy"` for `"timeout"`. Include a normal completed, conforming case that explicitly asserts `execution-failed`, `non-routing-failure`, no overrides, and no `next_redispatch`. Retain an unknown-category rejection case.

Write that test first: the current fixture rejects `"provider-busy"` as unknown.

#### S — Review the proposed split

**Decision:** Request revision. The proposed extraction introduces shared state and circular dependencies while distributing one policy across more files. The smaller corrective shape is to retain the original pure helpers and explicit arguments.

| Finding | Case anchor and consequence | Focused regression test |
|---|---|---|
| Fatal — loss of independent resolution | “`resolve` overwrites [the global] on every call” and “both extracted modules read it.” A call can observe another call’s capabilities during interleaving. This breaks the original per-packet, no-persistent-state guarantee. | `test_interleaved_resolutions_keep_own_capabilities`: deterministically pause A after its capabilities are established, run B with incompatible capabilities, resume A, and compare both results with isolated resolution. Use synchronization, not timing sleeps. |
| Important — dependencies point in both directions | Both extracted modules import `dispatch_profile`, while that module imports them at module import time. The purported policy modules depend on their caller for constants, exceptions, and decision construction; they cannot be initialized or replaced independently without considering the cycle. An actual import-time crash is possible but not established by the case alone. | `test_policy_modules_import_in_any_order`: start fresh interpreters and import each module first, then exercise a representative initial and retry decision. This detects order-sensitive initialization failures; passing it would not remove the dependency cycle. |
| Important — one effort change requires three coordinated edits | “Adding a supported effort now requires editing checks in all three files.” The extraction duplicates ownership of supported-effort rules, making inconsistent admission or routing more likely. | `test_effort_support_is_consistent_across_events`: parameterize the authoritative supported efforts and verify initial and after-execution paths honor the same capability support contract, including an unsupported-effort boundary. |
| Test coverage concern — setup hides state dependence | “Tests initialize that global through `resolve` before calling either extracted helper.” Those tests exercise a prepared process rather than independent policy calls; they cannot establish the original explicit-input guarantee. | `test_policy_helpers_need_no_prior_resolve`: call each helper with its complete explicit arguments in a fresh process, without priming state, and assert its expected decision. |

**Concrete correction:** Remove `CURRENT_CAPABILITIES`; retain capabilities as an argument to `_initial`, `_after_execution`, and `_decision`. Keep the helpers and shared policy definitions together in `dispatch_profile.py`. This removes the cycle and the three-file edit requirement without inventing a fourth shared-utilities module.

The findings apply the assigned architecture, correctness, tests, refactoring, and deletion-first lenses. They concern the proposed change, not unrelated existing function lengths.

#### Observable action summary

Read the permitted Runner prompt section of `cases.md` and the complete following files at the assigned revision using `git show`:

- `loom-code/scripts/dispatch_profile.py`
- `loom-code/skills/write-plan/SKILL.md`
- `loom-code/agents/implementer.md`
- `loom-code/skills/review/references/lenses.md`

Re-read the planning contract separately after the combined tool output was truncated. Checked call boundaries, parameter/state flow, error handling, and failure-category branch precedence by source inspection. No existing test files were inspected and no tests were executed. All tests above are proposals. No edits, commits, delegation, other revisions, frozen rubric, or surrounding delivery workflow were used.

### Arm Y

#### E — Add a second input transport

Decision: separate the pure resolver from transport handling, keeping the policy helpers together.

Proposed files and interfaces:

- `loom-code/scripts/dispatch_policy.py`: owns constants, `InputError`, policy helpers, and `resolve(packet: dict[str, Any]) -> dict[str, Any]`.
- `loom-code/scripts/dispatch_profile.py`: retains the executable entry point and exposes the imported `resolve` and `InputError` for compatibility. `main() -> int` owns argument selection, JSON decoding, output encoding, and error reporting.
- Proposed focused tests: `loom-code/scripts/test_dispatch_policy.py` and `loom-code/scripts/test_dispatch_profile_cli.py`; these paths are proposals, not inspected existing files.

Dependency direction: CLI → policy. The policy imports no CLI module and accesses neither standard streams nor mutable process state. The in-process caller uses `dispatch_policy.resolve(packet)` directly. No resolver class, provider abstraction, or separate initial/retry modules are needed.

Two sequential task boundaries:

1. Extract the existing pure policy unchanged and retain compatibility exports. Own the policy boundary and equivalence tests.
2. Add opt-in `--jsonl` handling inside `main()`, depending on task 1. Own transport behavior and subprocess tests.

Evidence: the fixture’s `main()` already performs `json.load`, calls `resolve`, catches decoding/validation failures, and serializes the result. `resolve` already promises “without I/O or persistent state”; `_initial` and `_after_execution` receive capabilities explicitly. Moving that complete responsibility preserves this useful boundary while letting stream handling change without exposing parsing details to the in-process caller. Splitting the policy further would add navigation without reducing dependencies.

Focused tests:

- Direct calls cover initial routing, after-execution routing, host rejection, and invalid packets; assert complete result dictionaries and `InputError` behavior match the frozen fixture. Replace standard streams with objects that fail on access to verify independence.
- Existing invocation still accepts a formatted, multiline single JSON object, emits the same compact sorted JSON plus newline, and preserves exit code 2 and the error prefix for invalid input.
- `--jsonl` processes two packets with different capabilities in order; each output equals its standalone `resolve(packet)` result.
- Empty batch emits nothing successfully.
- Proposed batch error behavior: stop at the first invalid line, exit 2, report its line number on stderr, and retain already emitted decisions. Test an invalid second line and ensure the third is not processed. This behavior needs an explicit batch contract; it is a proposal, not an existing guarantee.

#### C — Add one routing failure category

Decision: one task changes `NON_ROUTING_FAILURES` in `dispatch_profile.py` and adds a focused regression test. Do not split the file.

Public interface remains `resolve(packet) -> dict`; add `"provider-busy"` to the existing set. `FAILURE_KINDS` already incorporates that set, so no separate validation list change is necessary.

Evidence: `_after_execution` checks membership in `NON_ROUTING_FAILURES` in both conforming and nonconforming failure paths. Both produce the same non-routing outcome used by `timeout`. The resolver is one policy, capabilities are explicit inputs, and direct testing already has the `resolve` entry point. File length supplies no change-specific benefit for extraction.

Focused test: `test_provider_busy_matches_timeout`, parameterized over conforming/nonconforming attempts, completion status, and redispatch counts 0, 1, and 2. For otherwise identical valid packets, assert full result equality after changing only `failure_kind`. For completed attempts below the limit, assert `execution-failed`, `non-routing-failure`, no overrides, no `next_redispatch`, and unchanged count. Incomplete or exhausted attempts must preserve existing `no-legal-redispatch` precedence. Retain an unknown-category rejection test.

#### S — Review the proposed split

Decision: request revision; restore the cohesive policy and explicit capability arguments.

1. **Shared mutable capabilities break independent calls.**
   Anchor: `resolve` overwrites `CURRENT_CAPABILITIES`, and both extracted helpers read it. The fixture instead creates call-local capabilities and passes them explicitly. An interleaved second call can overwrite capabilities before the first helper reads them, producing the wrong support decision. Tests that first initialize the global through `resolve` also hide the helpers’ setup dependency. This loses the existing stateless guarantee.

   Focused regression: use a controlled barrier to pause call A before its helper reads capabilities, execute call B with conflicting capabilities, then resume A. Both results must equal their isolated results. Also call each helper with explicit capabilities without prior initialization.

2. **The extraction retains bidirectional dependencies.**
   Anchor: the original module imports both extracted modules at import time; each extracted module imports the original for constants, exceptions, and shared helpers. Understanding or replacing either extracted responsibility still requires the original module. Circular imports may additionally cause initialization failures depending on import order; that runtime failure is not established from the case description alone.

   Focused regression: import each module first in a fresh interpreter and exercise its entry point. Successful imports would address initialization risk, but would not establish a useful dependency boundary.

3. **Policy changes remain coupled across three files.**
   Anchor: adding a supported effort requires editing checks in all three files. The split has increased the number of change sites without separating ownership.

   Focused regression: parameterize supported-effort behavior across initial and retry decisions from one authoritative policy definition, including unsupported fallback. Pair this with inspection confirming effort policy has one owner; behavioral tests alone cannot prove edit locality.

The smaller correction is to remove the global and undo the initial/retry extraction, retaining explicit arguments and one policy module. A transport/policy separation remains independently defensible for case E.

Observable actions: read the permitted runner-prompt section, the complete source fixture at its fixed revision, and all three assigned contracts at their assigned revision. Re-read the planning contract after output truncation. Inspected call flow, state ownership, validation, and failure precedence. No tests were executed, files edited, commits created, other revisions inspected, or lifecycle work performed.

## Blind auditor judgments

Both judgments are advisory drafts, not a human acceptance decision.

### Auditor one

Advisory judgment: both arms are correct on E, C, and S. Y proposes a physical transport/policy separation absent from X, but S is a substantive tie. The frozen admission bar is therefore not met.

| Case / arm | Judgment | Anchored output excerpt | Reason |
|---|---|---|---|
| E / X | Correct | “Preserve `resolve(packet)` as the public policy boundary; add JSON-lines handling only in `main()`.” Tests include “direct resolution still returns the expected decision” with streams that fail on access. | The fixture already provides the pure, explicit-input API described. Direct policy tests and CLI compatibility/batch tests are proposed. Keeping the API in the same file is architecturally sound under the rubric, although it does not demonstrate the planned extraction benefit. |
| E / Y | Correct | “CLI → policy”; “The policy imports no CLI module”; “exposes the imported `resolve` and `InputError` for compatibility.” | The extraction keeps the cohesive policy together and gives it a one-way dependency boundary. Independent policy tests compare complete results and exceptions with the fixture; transport tests cover original invocation and batch framing. This proposes an extraction benefit absent from X, without establishing that extraction is necessary. |
| C / X | Correct | “Add `"provider-busy"` to `NON_ROUTING_FAILURES` in the existing file”; “assert exact result equality” against `timeout`. | Source inspection confirms `FAILURE_KINDS` derives from that set, both relevant failure branches use it, and incomplete/exhausted attempts have earlier precedence. The proposed parameterized regression matches those facts and rejects length-only splitting. |
| C / Y | Correct | “Do not split the file”; “Incomplete or exhausted attempts must preserve existing `no-legal-redispatch` precedence.” | Same correct change boundary and relevant regression coverage. The explicit completed/below-limit assertions match failed attempts in the fixture; the proposals must retain `success=False` where needed to avoid the existing early success return. No new C false positive. |
| S / X | Correct | “A call can observe another call’s capabilities during interleaving”; “An actual import-time crash is possible but not established”; “one effort change requires three coordinated edits.” | Identifies all specified substantive coupling problems, including state-primed tests. Deterministic interleaving and fresh-interpreter import tests target real risks; restoring explicit arguments and cohesive helpers is actionable. It correctly avoids treating a cycle as proof of a crash. |
| S / Y | Correct | “An interleaved second call can overwrite capabilities”; “behavioral tests alone cannot prove edit locality.” | Identifies the same state, initialization/dependency, test-setup, and change-site problems as X. Tests and the correction are appropriate. Pairing behavior tests with ownership inspection is precise, but does not supply a correct S finding absent from X. |

| Additional check | Judgment | Evidence and limitation |
|---|---|---|
| Observable actions / X | Correct as reported; execution unverified | Reports source/contract inspection, re-reading truncated material, and “All tests above are proposals.” Nothing in the permitted output contradicts the bounded runner task. Tool history was not supplied, so actual reads cannot be independently certified. |
| Observable actions / Y | Correct as reported; execution unverified | Reports complete permitted reads, source inspection, and “No tests were executed.” Proposed test paths are explicitly distinguished from inspected files. Same verification limitation. |
| Existing flow / X | Correct | No extra mandatory skill or user boundary decision. Noting unspecified batch-error behavior is a product-contract gap, not an explicit new user approval gate. |
| Existing flow / Y | Correct | Two sequential implementation tasks do not create a new mandatory skill or human decision. Proposed batch-error semantics are labeled as proposals requiring a contract, without demanding an additional user approval. |

Limitations: I inspected only the permitted case/rubric section, normalized artifacts, and fixed source fixture. No tests were executed, no implementation was available, and reported runner actions were not independently verified. Helper-independence tests describe the corrected explicit-argument interface; they are not immediately executable against an unspecified global-reading signature.

No disagreement with the frozen rubric’s correctness categories. Its admission condition is stricter than architectural correctness: E permits a sound same-file API, and neither soundness nor an additional extraction proposal establishes improvement in both E and S. These artifacts provide no basis for general efficiency or cost claims.

### Auditor two

Advisory judgment: both arms are architecturally correct in all three cases. Y proposes a separate policy module in E, but S is a substantive tie; the frozen admission bar is therefore not met.

| Case / arm | Judgment | Anchored output excerpt | Reason and test assessment |
|---|---|---|---|
| E / X | Correct | “Preserve `resolve(packet)` as the public policy boundary; add JSON-lines handling only in `main()`.” | The fixture already exposes a pure, explicit-input API. Keeping it in the same file meets the transport independence requirement. Direct-call stream traps and capability-isolation tests provide independent policy checks; JSON-lines equivalence and original-command compatibility checks address transport. This is domain-correct but does not demonstrate a separate-module extraction benefit. |
| E / Y | Correct | “CLI → policy. The policy imports no CLI module” and “exposes the imported `resolve` and `InputError` for compatibility.” | Extracts the complete cohesive policy with a one-way dependency while preserving existing entry points. Proposed direct-policy equivalence and subprocess transport tests fit the boundary. Empty-batch and partial-output behavior are explicitly proposals, not invented existing guarantees. Extraction creates a separately importable module, although reduced maintenance burden is not demonstrated by this planning exercise. |
| C / X | Correct | “Add `"provider-busy"` to `NON_ROUTING_FAILURES` in the existing file.” | Source inspection confirms that `FAILURE_KINDS` incorporates this set and both relevant failure paths use it. The proposed timeout-equivalence matrix covers completion, conformance, and redispatch precedence; the explicit normal-case expectation prevents equality alone from hiding an unintended outcome. Rejects length-only splitting. |
| C / Y | Correct | “one task changes `NON_ROUTING_FAILURES` … Do not split the file.” | Same correct minimal boundary. Proposed completed-attempt results and incomplete/exhausted precedence match the fixture for failed attempts. Full-result timeout equivalence plus unknown-category rejection is appropriate. |
| S / X | Correct | “A call can observe another call’s capabilities during interleaving”; “dependencies point in both directions”; “three coordinated edits.” | Identifies the stated global-state, circular-dependency, test-priming, and change-locality problems. Controlled interleaving and fresh-process tests address observable failures. Correctly qualifies import-time crashes as possible rather than established. Restoring explicit arguments and cohesive helpers is actionable. |
| S / Y | Correct | “Tests that first initialize the global … hide the helpers’ setup dependency”; “behavioral tests alone cannot prove edit locality.” | Identifies the same substantive issues with case-anchored evidence and appropriate tests/corrections. Its explicit distinction between behavioral verification and ownership inspection is useful, but X already identifies the underlying coupling and an actionable correction. No correct S improvement absent from X is established. |

Both action summaries describe only the permitted reads and source inspection, clearly labeling tests as proposed and unexecuted. Their source claims match the fixture I inspected. Actual runner read histories cannot be independently verified from these normalized outputs.

Neither arm adds a mandatory skill invocation or user boundary decision. Statements that batch error behavior needs specification do not explicitly impose a new user approval checkpoint.

Limitations: this assesses proposals, not executable implementations or test results. I read only the authorized case section, normalized artifacts, and fixed source fixture. I have no arm mapping or other auditor judgment. I find no disagreement with the frozen rubric as written; its separate admission requirement must not turn X’s valid same-file API into an architectural failure.

## Post-probe disposition

The candidate contract additions were removed after this result. The branch
retains this corpus, the normalized outputs, and the executable non-admission
check, but it does not carry prompt text that the matched comparison failed to
justify. No Closing Review or publication was started.
