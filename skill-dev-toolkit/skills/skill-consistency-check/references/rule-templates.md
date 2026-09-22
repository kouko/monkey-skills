# Rule Extraction Templates

This file contains templates for extracting structured rules from natural language text in skill files.
Each template defines a pattern to match, the rule type it produces, and the propositions to extract.

## Rule Types

| Type | Keywords | Semantics |
|------|----------|-----------|
| `must` | MUST, ALWAYS, REQUIRED, SHALL | Hard requirement: proposition MUST be true |
| `never` | NEVER, MUST NOT, PROHIBITED, FORBIDDEN | Hard prohibition: proposition MUST be false |
| `should` | SHOULD, RECOMMENDED, ADVISED | Soft requirement: proposition SHOULD be true |
| `should_not` | SHOULD NOT, NOT RECOMMENDED | Soft prohibition: proposition SHOULD be false |
| `optional` | MAY, OPTIONAL, CAN | No constraint |
| `conditional` | IF ... THEN, WHEN ... THEN | Conditional constraint |

## Extraction Templates

### Template 1: Explicit Imperative Rules
**Pattern**: `(MUST|NEVER|ALWAYS|SHOULD|SHOULD NOT|MUST NOT)\s+(.+)`
**Rule Type**: Based on keyword (must/never/should/should_not)
**Propositions**: Extract action and object from text

```yaml
- pattern: "(?i)(MUST|MUST NOT|NEVER|ALWAYS|SHOULD|SHOULD NOT)\s+(.+)"
  type_map:
    "MUST": "must"
    "ALWAYS": "must"
    "MUST NOT": "never"
    "NEVER": "never"
    "SHOULD": "should"
    "SHOULD NOT": "should_not"
  proposition_extractor: "extract_action_object"
```

### Template 2: Passive Voice Requirements
**Pattern**: `(required|prohibited|forbidden|mandatory)\s+(?:to\s+)?(.+)`
**Rule Type**: Based on keyword (required/mandatory → must, prohibited/forbidden → never)
**Propositions**: Extract action and object

```yaml
- pattern: "(?i)(required|prohibited|forbidden|mandatory)\s+(?:to\s+)?(.+)"
  type_map:
    "required": "must"
    "mandatory": "must"
    "prohibited": "never"
    "forbidden": "never"
  proposition_extractor: "extract_action_object"
```

### Template 3: Conditional Rules
**Pattern**: `IF\s+(.+?)\s+THEN\s+(.+)`
**Rule Type**: `conditional`
**Propositions**: Extract condition and consequence

```yaml
- pattern: "(?i)IF\s+(.+?)\s+THEN\s+(.+)"
  type: "conditional"
  condition_extractor: "extract_proposition"
  consequence_extractor: "extract_proposition"
```

### Template 4: Sequential Dependencies
**Pattern**: `(before|after|prior to|following|must precede|must follow)\s+(.+)`
**Rule Type**: `dependency`
**Propositions**: Extract ordering constraint

```yaml
- pattern: "(?i)(before|after|prior to|following|must precede|must follow)\s+(.+)"
  type: "dependency"
  direction_map:
    "before": "precedes"
    "prior to": "precedes"
    "after": "follows"
    "following": "follows"
    "must precede": "precedes"
    "must follow": "follows"
  proposition_extractor: "extract_phase_or_action"
```

### Template 5: Scope-Bound Rules
**Pattern**: `(in|during|for)\s+(phase|step|stage)\s+([A-Za-z0-9]+)\s*,?\s*(.+)`
**Rule Type**: Based on embedded imperative
**Propositions**: Extract scope and action

```yaml
- pattern: "(?i)(in|during|for)\s+(phase|step|stage)\s+([A-Za-z0-9]+)\s*,?\s*(.+)"
  type: "scoped"
  scope_extractor: "extract_phase"
  embedded_rule_extractor: "apply_templates_1_2"
```

### Template 6: Agent/Script Invocation Constraints
**Pattern**: `(invoke|call|run|execute)\s+(?:the\s+)?(?:script|agent)\s+([a-z0-9_\-:./]+)`
**Rule Type**: `invocation`
**Propositions**: Extract target and constraints

```yaml
- pattern: "(?i)(invoke|call|run|execute)\s+(?:the\s+)?(?:script|agent)\s+([a-z0-9_\-:./]+)"
  type: "invocation"
  target_extractor: "extract_target"
```

### Template 7: File/Reference Constraints
**Pattern**: `(read|write|load|parse)\s+(?:file\s+)?([a-z0-9_\-./]+)`
**Rule Type**: `file_op`
**Propositions**: Extract operation and file

```yaml
- pattern: "(?i)(read|write|load|parse)\s+(?:file\s+)?([a-z0-9_\-./]+)"
  type: "file_op"
  operation_extractor: "extract_operation"
  file_extractor: "extract_file"
```

## Proposition Extraction Functions

### extract_action_object(text)
```python
def extract_action_object(text: str) -> list[str]:
    """Extract atomic propositions from action-object text."""
    # Normalize
    text = text.lower().strip()
    text = re.sub(r'^(?:do\s+)?', '', text)
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_]', '', text)
    return [text[:64]] if text else []
```

### extract_proposition(text)
```python
def extract_proposition(text: str) -> str:
    """Extract a single proposition from text."""
    text = text.lower().strip()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_]', '', text)
    return text[:64] if text else None
```

### extract_phase_or_action(text)
```python
def extract_phase_or_action(text: str) -> str:
    """Extract phase name or action from dependency text."""
    text = text.lower().strip()
    # Check for phase reference
    phase_match = re.search(r'phase\s+([a-z0-9]+)', text)
    if phase_match:
        return f"phase_{phase_match.group(1)}"
    # Otherwise treat as action
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_]', '', text)
    return text[:64] if text else None
```

### extract_phase(text)
```python
def extract_phase(text: str) -> str:
    """Extract phase identifier from scoped rule."""
    text = text.lower().strip()
    phase_match = re.search(r'([a-z0-9]+)', text)
    return f"phase_{phase_match.group(1)}" if phase_match else None
```

### extract_target(text)
```python
def extract_target(text: str) -> str:
    """Extract script/agent target from invocation text."""
    return text.strip()
```

### extract_operation(text)
```python
def extract_operation(text: str) -> str:
    """Extract file operation from text."""
    return text.lower().strip()
```

### extract_file(text)
```python
def extract_file(text: str) -> str:
    """Extract file path from text."""
    return text.strip()
```

## Usage in SMT Encoding

Each extracted proposition becomes a Z3 Boolean variable.
The rule type determines the constraint:
- `must`: `var == True`
- `never`: `var == False`
- `should`: `(var == True)` as soft constraint
- `should_not`: `(var == False)` as soft constraint
- `conditional`: `Implies(condition_var, consequence_var)`
- `dependency`: `precedes(a, b)` - encoded as ordering constraint
- `invocation`: `invoked(target)` - may have preconditions
- `file_op`: `reads(file)` or `writes(file)` - for resource tracking

## Extending Templates

To add a new template:
1. Define the regex pattern with capture groups
2. Specify the rule type (or map from keywords)
3. Define which extractors to use for each capture group
4. Add to the appropriate extractor functions if needed
5. Test against real skill files

---