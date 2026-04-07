# Philosophers Toolkit — Skill Structure Standard

Every skill in this plugin should contain the following sections.
The format within each section is flexible — adapt to the method's nature.

## Required Sections

### 1. Core Philosophy
One paragraph describing the method's essence and spirit.
What makes this method unique? What mindset should the agent adopt?

### 2. When to Use
Trigger scenarios and negative triggers (when NOT to use).
Keep narrow — avoid over-triggering on generic queries.

### 3. Topic Discovery
Establish what the user wants to explore before applying the method.

Shared pattern:
- If user's input contains a specific topic → proceed to method
- If vague but conversation has context → acknowledge topic, ask thinking
- If no context → ask what to explore

Constraint: acknowledge topic, never acknowledge answer.

### 4. Method
The core procedure. Format depends on the method's nature:
- **Dialogue-driven** (e.g., Socratic) → State Machine
- **Framework-driven** (e.g., Four Causes) → Analysis dimensions
- **Phase-driven** (e.g., Dialectics) → Sequential stages
- **Process-driven** (e.g., Falsifiability) → Step-by-step flow

### 5. Critical Constraints
Never / Always rules specific to this method.
What must the agent avoid? What must it always do?

### 6. Safety Measures
- Psychological safety (frustration handling, mode switching)
- Ethical boundaries (no manipulation, no ideological steering)
- When to break the method and give direct help

### 7. Examples
At least one complete interaction transcript showing the method in action.
Use realistic scenarios, not textbook cases.

## Optional Sections

- **Operating Modes** — if the method has distinct application contexts
- **Taxonomy / Toolkit** — if the method has categorized tools (e.g., question types)
- **Domain Adaptations** — if the method works differently across domains
- **Implementation Checklist** — per-response verification items
