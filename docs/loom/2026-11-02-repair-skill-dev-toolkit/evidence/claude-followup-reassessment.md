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

No confirmed requirement, paid service, existing-data operation or intended outcome changes. Wave 6 repairs the same command reliability, stable blind selection, consistent policy and executable-evidence obligations. The interactive recovery design makes the existing same-round map lifetime explicit; a separate invocation is a new comparison. Previous evidence remains historical and only unchanged conditions may be carried forward with reasons. Review round and task retry continuity are retained; this request does not reset them.

The outside review did not execute tests. Its findings and the parent reproductions are not a passing review of later corrections. No repeat outside run is authorized. A packet scan found no matches; that check covered only the dispatch packet, not all material reachable by CLI startup or tools. No completeness, confidentiality or zero-defect guarantee is made.
