# Evaluation Case Design Reference

Purpose: Create unambiguous, measurable tasks that reveal skill gaps before writing documentation.

## Structure

Each evaluation case should contain:

### Task Description
- Concrete, specific request a real user would make
- Should be complex enough that Claude would benefit from a skill
- Must have objectively verifiable outcome

### Files Needed (if any)
- List of input files with descriptions
- Should be realistic examples from actual work

### Success Criteria (Expected Behavior)
- 3-5 specific, observable outcomes that indicate success
- Each criterion should be checkable via automated means
- Avoid subjective preferences unless paired with deterministic checks

### Failure Modes to Document
- What happens when Claude attempts this without the skill?
- Common mistakes, incomplete outputs, wrong approaches
- These become the baseline for measuring skill lift

## Validation Checklist

- [ ] Task description is concrete and specific (not abstract)
- [ ] Success criteria are objectively verifiable
- [ ] Based on real user-reported issues or observed gaps
- [ ] Can be completed in <5 minutes by skilled human
- [ ] Includes file paths if file operations are needed

## Example (matching schemas.md evals.json structure)

```json
{
  "skill_name": "excel-analysis",
  "evals": [
    {
      "id": 1,
      "prompt": "My boss just sent me this xlsx file... add a column that shows profit margin as percentage",
      "expected_output": "Excel file with new profit margin percentage column added",
      "files": ["test-files/sales_data.xlsx"],
      "expectations": [
        "Reads the Excel file using a library (not hand-rolled CSV parsing)",
        "Correctly calculates profit margin from columns C and D",
        "Adds new column E with the calculated values",
        "Saves the file with the new column included"
      ]
    }
  ]
}
```

**Note**: `failure_modes_without_skill` is documented separately in the design phase (see §Failure Modes to Document above) but is not part of the evals.json schema — it becomes the baseline for measuring skill lift.
```

## When to Use Eval-First

Evaluation-first is recommended when:
- Creating a skill for a new domain or workflow
- The skill has multiple distinct behaviors (needs to verify each)
- The user reports vague "it doesn't work" feedback
- Multiple developers will use the same skill

Evaluation-first is NOT needed when:
- Skill does one very simple thing (e.g., format conversion)
- User already has clear success criteria documented
- Skill is being used as a one-off prototype

## Integration with Iteration Loop

After Step 0, evaluation cases become the regression test suite for future iterations:
- Each improvement cycle re-runs all eval cases
- Baseline is the previous iteration's output (or original without-skill output)
- Pass rate must improve or stay flat; regressions are flagged immediately
- New edge cases discovered during iteration are added to the eval set
