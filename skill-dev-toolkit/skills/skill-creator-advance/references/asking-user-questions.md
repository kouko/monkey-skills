# Asking User Questions

Guidelines for asking users questions during skill creation and iteration.

## Empty-Prompt Onboarding
When the user provides an empty or vague prompt, use a structured
question sequence to clarify intent, scope, and success criteria.

**Surface Orientation Pattern:**
1. **What** — What specific task or output does the user want? (concrete, not abstract)
2. **Why** — What problem does this solve? What happens without it?
3. **How** — What does success look like? What would a "good enough" result be?
4. **Constraints** — Any tools, formats, or existing patterns to follow/avoid?

This pattern closes three failure modes:
- **Scope drift** — User keeps adding requirements mid-task
- **Vague acceptance** — "Make it better" with no measurable criteria
- **Tool mismatch** — Using the wrong tool for the job

## Hardened Pattern
Use AskUserQuestion with specific, checkable answer formats to collect
user input efficiently. Avoid open-ended questions that invite
narrative responses.

**Mandatory-Gate Template (copy-paste ready):**
```python
AskUserQuestion({
    "questions": [{
        "question": "What specific outcome should this skill produce?",
        "header": "Outcome",
        "options": [
            {"label": "Option A", "description": "Description of what Option A produces"},
            {"label": "Option B", "description": "Description of what Option B produces"},
        ],
        "multiSelect": false
    }],
    "answers": {},
    "annotations": {},
    "metadata": {"source": "skill-creator-advance:onboarding"}
})
```

**Answer Format Guidelines:**
- Use `multiSelect: true` only when options are truly independent
- Each option must be mutually exclusive and collectively exhaustive where possible
- `header` ≤ 12 chars for UI chips
- `description` explains trade-offs, not just restates label
- Include `preview` for concrete artifacts (code snippets, mockups, diagrams)

**Failure Modes Addressed:**
1. **Open-ended fatigue** — User writes paragraphs instead of choosing
2. **False consensus** — Multiple options selected that conflict
3. **Ambiguous criteria** — Options without clear success definitions

**When to Use Which Pattern:**
- **Empty-Prompt Onboarding** — First interaction, no context
- **Hardened Pattern** — Decision points during iteration, gate enforcement
- **Both** — Complex skills needing both orientation and gate checks