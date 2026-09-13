# Loom description compression evidence

Date: 2026-09-13. Scope: the 20 existing Loom leaf descriptions and three
new router descriptions. Skill bodies, names, host wrappers, unrelated
plugins, model replies, and execution-time router loading are outside the
initial-description metric.

## Reproducible accounting

Baseline: W0 commit `c9a9b9d9faa75e004e302bee64a61587bbb0ab56`.
The complete normalized description snapshot is in `cases.md`; the test pins
its SHA-256, total, word count, and path population. Tests do not require Git
history and never compare shortened candidate leaves to the old total.

| Population | Descriptions | Characters | Whitespace words | o200k_base tokens |
|---|---:|---:|---:|---:|
| Frozen baseline | 20 | 6,746 | 1,052 | 1,632 |
| Candidate, including routers | 23 | 2,884 | 460 | 654 |

Character reduction is **57.25%**; token reduction is **59.93%**. Candidate
leaves contribute 2,482 characters and routers contribute 402. The enforced
character ceiling is 4,047, corresponding to at least 40% reduction.
Words are reported separately and are not tokens.

| Plugin | Baseline characters | Candidate characters | Baseline tokens | Candidate tokens |
|---|---:|---:|---:|---:|
| loom-code | 1,181 | 733 | 229 | 135 |
| loom-design | 1,239 | 615 | 303 | 137 |
| loom-workflow | 4,326 | 1,536 | 1,100 | 382 |

Tokenizer: `tiktoken==0.14.0`, encoding `o200k_base`. Each normalized
description is encoded separately and token counts are summed. This is an
explicit tokenizer measurement, not a claim about the host's complete prompt
or GPT-6 billing. The isolated command adds no repository dependency:

```sh
uv run --isolated --with tiktoken==0.14.0 python - <<'PY'
import runpy
import tiktoken

m = runpy.run_path("scripts/test_loom_skill_description_catalog.py")
enc = tiktoken.get_encoding("o200k_base")
baseline = list(m["_baseline"]().values())
candidate = [
    m["_description"](path)
    for skills in m["_skills"]().values()
    for path in skills.values()
]
for label, descriptions in (("baseline", baseline), ("candidate", candidate)):
    print(label, {
        "descriptions": len(descriptions),
        "characters": sum(map(len, descriptions)),
        "words": sum(len(text.split()) for text in descriptions),
        "tokens": sum(len(enc.encode(text)) for text in descriptions),
    })
PY
```

## Deterministic verification

`python3 -m pytest scripts/test_loom_skill_description_catalog.py -q`:
**6 passed**. Re-running the same file from `/tmp` with the same verified
Python interpreter also produced **6 passed**. `git diff --check` passed.
The initial focused run reproduced the W0 defect: 2,482 candidate leaf
characters were incorrectly compared with the 6,746 historical baseline.

The tests verify the frozen denominator, unchanged leaf population, all
three routers and their local leaf links, router-inclusive budget, body and
other-metadata exclusion, required corpus categories, and the explicit-only
goal-create boundary. These are deterministic contract checks; they do not
simulate a model's semantic skill selection.

## Blind routing observations

Requested/effective model: **gpt-6-astra**, reasoning effort **medium**,
as recorded by successful host dispatch. Each of the eleven requests ran in
its own collaboration context with `fork_turns: none`. The evaluator was
allowed only current exposed skill names/frontmatter and the selected router
body. It was forbidden to read this dogfood directory, intent, plan, tests,
Git history, or expected answers. The orchestrator supplied the observations
below; this report's author did not act as those evaluators.

Task method: select the matching skill from the exposed metadata; read its
router table only when selecting a router; return selected skill, whether
the router was loaded, and any resulting leaf selection. Actual leaf
workflows were not executed. The exact per-case requests are reproduced here
and in `cases.md`.

| Case | Exact request | Selected skill | Router loaded | Resulting leaf | Assessment |
|---|---|---|---|---|---|
| plugin-umbrella | Use Loom to help me implement a confirmed engineering change. | using-loom-code | Yes | write-plan | PASS |
| direct-leaf | Use $loom-code:write-plan for the confirmed intent. | write-plan | No | write-plan | PASS |
| adjacent-skill-collision | The intent is already confirmed; make the implementation plan. | write-plan | No | write-plan | PASS |
| ordinary-request | Translate this short sentence into Traditional Chinese. | none | No | none | PASS |
| multilingual-request | 這個已確認 intent 需要設計規格，請先寫 spec。 | write-spec | No | write-spec | PASS |
| explicit-only-goal-create | Use $loom-workflow:goal-create to set a stopping condition for this session. | goal-create | No | goal-create | PASS |
| held-out-design-specific | Use Loom to define our product: we need colors, typography, and component tokens. | design-system | No | design-system | Initial router expectation FAIL; corrected direct-leaf contract PASS |
| held-out-workflow-specific | Use the Loom workflow toolbox: assess whether this proposal has too many moving parts. | critique | No | critique | Initial router expectation FAIL; corrected direct-leaf contract PASS |
| held-out-unnamed-goal | Set a stopping condition for this session. | none | No | none | PASS |
| held-out-design-umbrella | Use Loom to help define a product change; I am not sure whether I need an intent, spec, principles, or a visual system. | using-loom-design | Yes | Undetermined: missing artifact state and specific need | PASS for entry selection only |
| held-out-workflow-umbrella | Use Loom's workflow tools to help me, but I am not sure which workflow skill applies. | using-loom-workflow | Yes | Undetermined: no concrete task | PASS for entry selection only |

The six frozen W0 cases passed without answer changes, including all forbidden
routes. Five W2 prompts were held out from description editing. The first two
specific W2 requests initially expected a router; the blind evaluators selected
the correct direct leaves instead. Those answer keys were amended explicitly
because routers are optional for clear leaf requests. They do not count as
pre-frozen router passes. Two subsequently authored ambiguous requests provide
the observed design/workflow router selections; neither settles leaf routing
without more user context. No description was changed in response to this run.

A supplementary implementer judgment selected routes before seeing W0 answer
fields. It agrees with the frozen results but expected routers on the two
specific W2 requests. That judgment shared one context across requests and
accidentally saw portions of leaf bodies during extraction, so it is excluded
from the blind evidence population above.

## Limits

These are blind metadata-selection observations from one model and one run per
request, not host automatic-activation telemetry, a universal trigger rate, or
an end-to-end workflow test. The edited descriptions retain direct leaf access
and representative positive/negative boundaries in this corpus. Router table
loading adds execution-time context not included in the initial-description
saving. Standalone installation, unchanged workflow bodies, package integration,
and closing review remain separate validation obligations owned by the main
change; this report does not claim they were proved by eleven selections.
