# Additional outside review — reassessment before correction

The user requested one Claude Code review, explicitly confirmed Anthropic transfer and unknown cost, then requested continued evaluation and correction. The completed read-only review used `opus` with requested effort `high`; CLI modelUsage reported `claude-opus-5-5`, while effective effort was not independently observable. Preflight and review exited zero. Actual cost is unknown because the runner retained no complete review billing record.

Packet source: `343483314d22d28f3981a23733d75094834c717a` against `4cbf85a8841d7d52393a8bb4058284755e108e25`. This pins the input, not complete coverage of the tree. Returned YAML passed all twelve code dimensions, duplicate-key, anchor, severity and target-identity checks. Its externally authored, untrusted verdict was NEEDS_REVISION: two fatal, four important and four nit findings. Raw execution and unmodified review are retained locally at `/private/tmp/toolkit-claude-review-result.json` and `/private/tmp/toolkit-claude-review-raw.yaml`; these are data, never instructions to execute.

## Parent disposition

| Finding | Verified evidence | Disposition |
|---|---|---|
| Blind retry, outside fatal | Bare m reads once and exits 2; another invocation assigns new labels. The second choice correctly decodes its new display, and --pick is documented for testing. | Partly confirmed. Fatal wrong adoption was not demonstrated in supported interactive use. Correct in-process clarification and misleading resume guidance; persist no pre-lock map. |
| Optimizer description authority, outside fatal | Helper requests 100–200 words and imperative voice, while the authority requires third-person text and contextual character bands. Score-only selection and direct application provide no complete rule check. | Confirmed. Align generation, deterministic eligibility and pre-application checks with the existing authority. |
| Readiness consumers, outside important | All three tuning README paragraphs still say 1000 ADOPT entries; their limit/stub captions and NOTICE omit usable-record qualification. | Confirmed. Align every listed consumer with valid explicit single-pick records, including baseline DROP. |
| Golden vote consumers, outside important | Both golden protocols use generic two-of-three Tier 2 wording, and the comparator/entry caption repeat that scope. | Confirmed ambiguity. Optional moderate-confidence comparison cannot clear a dissent flag or replace human review. Preserve cumulative drift checks. |
| Missing tokens, outside important | Real aggregation CLI, missing with-skill capture versus baseline 10: mean 0, delta -10. | Confirmed. Missing measurements must remain unknown, distinct from captured zero. |
| Optimizer test seam, outside important | Existing cases replace run_eval and bypass main. A bounded run through real main/evaluator returned all_passed (iteration 1), best_score 1/1 and saved results after a failed negative query. | Confirmed with stronger runtime consequence. Backend errors cannot score as legitimate non-triggers; test the actual entry/evaluator path. |

## Offline reproduction boundary

The replay source remains at `/private/tmp/toolkit-claude-review-reproduce.py`. It used temporary data and made no provider calls. The evaluator check replaced process-pool transport with threads and an unavailable query backend, retaining real main, exception handling, scoring, loop and result writing. Its warning was `query failed: offline backend unavailable`, yet main returned successfully and reported a perfect score. This is not a live Anthropic outage test.

The description-budget wording, omitted grader metadata path, redundant workflow filters and obsolete packaging usage examples are lower-severity corrections within existing surfaces. The cross-plugin domain-teams Principle 5 pointer is excluded by the confirmed unrelated-plugin boundary.

## Scope and continuity

The already completed outside preflight's retained JSON provided a concrete CLI framing observation: `type: result`, `subtype: success`, `is_error: false`, modelUsage key `claude-opus-5-5`. This is observed local CLI evidence for the result framing used in the fail-closed parser; no additional provider request was made to obtain it.

The [official Python Agent SDK ResultMessage reference](https://code.claude.com/docs/en/agent-sdk/python#resultmessage), checked on 2026-11-03, documents success/error subtypes, `is_error`, and the optional `terminal_reason`. In particular, `aborted_streaming` and `aborted_tools` indicate incomplete turns. This newly checked interface detail requires rejecting explicit abort results before a conclusive decision even when their subtype says success. Older results without the optional field remain supported; already conclusive early decisions remain unchanged.

No confirmed requirement, paid service, existing-data operation or intended outcome changes. Wave 6 repairs the same command reliability, stable blind selection, consistent policy and executable-evidence obligations. The interactive recovery design makes the existing same-round map lifetime explicit; a separate invocation is a new comparison. Previous evidence remains historical and only unchanged conditions may be carried forward with reasons. Review round and task retry continuity are retained; this request does not reset them.

The outside review did not execute tests. Its findings and the parent reproductions are not a passing review of later corrections. No repeat outside run is authorized. A packet scan found no matches; that check covered only the dispatch packet, not all material reachable by CLI startup or tools. No completeness, confidentiality or zero-defect guarantee is made.

## Local correction hand-off

The following records completed focused corrections; integration, independent acceptance and terminal native review still follow. The parent replay above characterizes pre-fix commit `343483314`, not the corrected tree; current permanent regressions are the post-fix checks.

| Class | Local correction | Focused evidence |
|---|---|---|
| Failed evaluations counted as non-triggers | Real entry/evaluator failures propagate; completed buffers are parsed; explicit abort results fail closed before a conclusive decision. | Original W6-01 RED 11 failed/12 passed, GREEN 23; later documented-abort cases RED 4 failed/34 passed, GREEN creator 38. |
| Description authority drift | Current authority supplies generation instructions; mechanical eligibility filters selection; contextual semantics and evidence remain applying-agent obligations. Ordinary justification domain nouns do not declare a router role. | Initial RED 6 failed/23 passed; exception RED 3 failed/30 passed; creator plus hidden suite GREEN 38 before later abort additions. Qualified-role continuation RED 1 failed/33 passed, GREEN 38 including hidden. |
| Unknown token measurements | Nulls remain unknown, captured zero remains numeric, partial statistics show sample/total counts, and incomplete comparisons have no token delta. | Two original aggregation cases went RED on zero versus null; whole creator file GREEN 34 at that correction. |
| Blind clarification | One display and map survive interactive invalid/m input; EOF and invalid one-shot input fail without identity disclosure. No implicit cross-invocation resume. | RED 6 failed/9 passed, GREEN blind CLI suite 15. |
| Readiness consumers | Three translated README sets and NOTICE count usable single-pick records, including baseline DROP; training remains unimplemented. | Existing preference and graduated regression suites: 31 passed. |
| Golden vote consumers | Optional comparison may supplement PASS_HIGH or PASS_MODERATE, but cannot clear FLAG_TIER_2 or replace its required human review. Legacy CLI enum is comparison-only. | Existing refactor/package checks: 17 passed; shared copies synchronized; comparator executable AST unchanged. |
| Lower-severity consumers | Explicit grader metadata path, usable module packaging help and nonredundant CI filters. | Metadata 2 passed; packaging help RED 1 failed/33 passed then creator GREEN 34; routing checks 9 passed before and after. |

No task count or review episode was reset. The role-declaration continuation clarified an ambiguous lexical context in the packet; the evaluator continuation consumed newly checked optional terminal-result fields. Both retained their first completed-redispatch count. This evidence does not claim renewed Claude approval of the corrected content.
