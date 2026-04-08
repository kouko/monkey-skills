# Philosophers Toolkit — Skill Structure Standard

Every skill in this plugin should contain the following sections in order.
The format within each section is flexible — adapt to the method's nature.

## Required Sections (in order)

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

### 5. Response Format
Define the structure of each agent response during the method.
How should the agent format its output per turn?

### 6. Critical Constraints
Never / Always rules specific to this method.
What must the agent avoid? What must it always do?

### 7. Safety Measures
- Psychological safety (frustration handling, mode switching)
- Ethical boundaries (no manipulation, no ideological steering)
- When to break the method and give direct help

### 8. Examples
At least one complete interaction transcript showing the method in action.
Use realistic scenarios, not textbook cases.
Reference files go after examples: "For more, see `references/X.md`."

### 9. Implementation Checklist
Per-response verification items.
What should the agent check before every response?

## Optional Sections (place after Method, before Critical Constraints)

- **Operating Modes** — if the method has distinct application contexts
- **Taxonomy / Toolkit** — if the method has categorized tools (e.g., question types)
- **Domain Adaptations** — if the method works differently across domains
- **Tone Management** — if tone is critical to the method's effectiveness
