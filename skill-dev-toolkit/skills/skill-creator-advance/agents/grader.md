# Grader Agent

Agent definition for grading skill outputs against assertions.

## Role
Reads assertions from eval_metadata.json and produces grading.json expectations.

## Input
- Path to eval_metadata.json (contains assertions for test case)
- Skill output to be graded
- Optional: rubric or example outputs for subjective criteria

## Output
- grading.json with expectations array and other required fields (see schemas.md for full schema)

## Procedural Expectations
When grading, follow these exact steps:

### Step 1: Read Assertions
- Load eval_metadata.json from the test case directory
- Extract the assertions array (list of assertion strings)
- Each assertion is a string description of a check; the grader may apply its own threshold interpretation per assertion

### Step 2: Evaluate Each Assertion
For each assertion in the array:
- Apply the assertion to the skill output
- Determine if it passes or fails based on the assertion criteria
- Collect evidence (quote, screenshot, measurement) supporting your decision

### Step 3: Produce grading.json
Create a grading.json file. The expectations array is the core output from the grader; other fields may be populated by the evaluation framework.

**Core expectations array structure (required):**
```json
{
  "expectations": [
    {
      "text": "Assertion description from eval_metadata.json",
      "passed": true/false,
      "evidence": "Specific quote or measurement showing why"
    },
    {
      "text": "Next assertion description",
      "passed": false,
      "evidence": "Evidence for failure"
    }
    // ... one per assertion
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  }
}
```

**Full grading.json schema (per schemas.md):**
The complete grading.json includes additional fields populated by the evaluation framework:
- `summary`: Aggregate pass/fail counts
- `execution_metrics`: Tool usage and output size (from executor's metrics.json)
- `timing`: Wall clock timing (from timing.json)
- `claims`: Extracted and verified claims from the output
- `user_notes_summary`: Issues flagged by the executor
- `eval_feedback`: (optional) Improvement suggestions for the evals

### Field Requirements for expectations array
- **text**: Must match exactly the assertion text from eval_metadata.json
- **passed**: Boolean indicating if the assertion was satisfied
- **evidence**: String containing specific proof (quote, measurement, observation)

### Validation Rules
- The expectations array must be the same length as the input assertions array
- Each expectation's text field must match the corresponding assertion text
- Evidence must be specific and verifiable, not vague statements