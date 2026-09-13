# Loom description routing corpus

Frozen before router and description edits, 2026-09-13. This corpus tests
selection at the exposed skill boundary; it does not claim a universal
implicit-invocation rate. W2 records the model, prompt, selected skill, and
whether each expected or forbidden route held.

## Runner contract

- Give each request to a fresh context with the candidate Loom skill catalog.
- Record the selected skill name, whether a router was loaded, and the result.
- A direct skill request passes only when its named leaf is selected; it need
  not load a router first.
- `expected: none` passes only when no Loom skill is selected.
- `explicit-only` passes only for the named invocation. Natural-language
  variants must not be reported as evidence that the explicit-only skill
  implicitly triggered.

```json routing-cases
[
  {
    "id": "plugin-umbrella",
    "kind": "positive",
    "request": "Use Loom to help me implement a confirmed engineering change.",
    "expected": "using-loom-code",
    "forbidden": [],
    "invocation": "implicit"
  },
  {
    "id": "direct-leaf",
    "kind": "positive",
    "request": "Use $loom-code:write-plan for the confirmed intent.",
    "expected": "write-plan",
    "forbidden": [],
    "invocation": "explicit"
  },
  {
    "id": "adjacent-skill-collision",
    "kind": "boundary",
    "request": "The intent is already confirmed; make the implementation plan.",
    "expected": "write-plan",
    "forbidden": ["capture-intent", "write-spec"],
    "invocation": "implicit"
  },
  {
    "id": "ordinary-request",
    "kind": "negative",
    "request": "Translate this short sentence into Traditional Chinese.",
    "expected": "none",
    "forbidden": ["using-loom-code", "using-loom-design", "using-loom-workflow"],
    "invocation": "implicit"
  },
  {
    "id": "multilingual-request",
    "kind": "positive",
    "request": "這個已確認 intent 需要設計規格，請先寫 spec。",
    "expected": "write-spec",
    "forbidden": ["write-plan"],
    "invocation": "implicit"
  },
  {
    "id": "explicit-only-goal-create",
    "kind": "boundary",
    "request": "Use $loom-workflow:goal-create to set a stopping condition for this session.",
    "expected": "goal-create",
    "forbidden": [],
    "invocation": "explicit-only"
  }
]
```
