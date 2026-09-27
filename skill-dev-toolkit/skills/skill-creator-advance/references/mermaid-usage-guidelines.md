# Mermaid Usage Guidelines

Guidelines for when and how to use Mermaid diagrams in skill authoring.

## When to Use
- **State machines / flows** — multi-step processes with branching
- **Architecture / data flow** — components and their connections
- **Sequence diagrams** — agent interactions, API calls, user journeys
- **Class / entity relationships** — when static structure matters

## Guidelines
1. **Prefer prose for simple cases** — A 3-step linear flow is clearer as a numbered list
2. **Use Mermaid for complexity** — Branching, loops, parallel paths, or ≥4 components
3. **Syntax conventions**:
   - Use `graph TD` for top-down flows
   - Use `sequenceDiagram` for interactions over time
   - Use `classDiagram` for type relationships
   - Label edges with verbs, not nouns
4. **Cost-benefit framework**:
   - **Cost**: Rendering time, token overhead, maintenance burden
   - **Benefit**: Clarity for complex relationships, visual debugging
   - **Threshold**: Use Mermaid only when prose would take ≥2× the space or fail to show the relationship
5. **Maintenance**: Diagrams must be regenerated when the described system changes — include a comment with the source file that generates the diagram if applicable

## Quick Reference
| Diagram Type | Use Case | Syntax Start |
|---|---|---|
| Flow | Linear or branching processes | `graph TD` |
| Sequence | Agent/API/user interactions | `sequenceDiagram` |
| Class | Type hierarchies, data models | `classDiagram` |
| State | State machines | `stateDiagram-v2` |
| Gantt | Timelines, schedules | `gantt` |
| Pie | Proportions | `pie` |