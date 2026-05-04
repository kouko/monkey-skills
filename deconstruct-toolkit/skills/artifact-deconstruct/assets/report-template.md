# Deconstruction Report Template

Copy this template, fill in each section, deliver to user.

---

# Deconstruction Report: <artifact name>

**Artifact type**: <copy / playbook / UI / argument / etc>
**Lenses applied**: <comma-separated list>
**Date analyzed**: YYYY-MM-DD

---

## 1. Surface observations (what you see)

What is visible on first read:

- Structure / length / visual features
- One-glance design choices

3–5 bullets, no analysis yet.

## 2. Design decisions (what was decided)

### Audience modeling

- **Primary reader**:
- **Default situation**:
- **Excluded readers**:

### Creation sequence (inferred)

- Reading order vs writing order:
- Evidence supporting the inference:

### Rhetorical structure

- Opening move:
- Climax / strongest claim:
- Closing move (CTA / synthesis):

## 3. Borrowed frameworks (what was inherited)

Source genealogy table:

| Borrowed from | How it appears | Acknowledged? |
|---|---|---|
| ... | ... | ... |

## 4. Rhetorical mechanisms (what it does to you)

### Persuasion analysis (if `lens-persuasion` applied)

| Cialdini principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity | ... | ... | 🟢/🟡/🔴/⚫ |
| Commitment | ... | ... | ... |
| Social proof | ... | ... | ... |
| Authority | ... | ... | ... |
| Liking | ... | ... | ... |
| Scarcity | ... | ... | ... |
| Unity | ... | ... | ... |

### Argument analysis (if `lens-rhetoric` applied)

| Toulmin component | Content |
|---|---|
| Claim | ... |
| Grounds | ... |
| Hidden warrant | ... |
| Backing | ... |
| Rebuttal acknowledged? | yes/no |
| Qualifier present? | yes/no |

### Frame analysis (if `lens-frame` applied)

- Primary framework (Goffman): ...
- Conceptual metaphor (Lakoff): <source domain> → <target domain>
- Power relations embedded: ...

### UX analysis (if `lens-ux` applied)

| Nielsen heuristic | Status | Evidence |
|---|---|---|
| 1. Visibility of status | ... | ... |
| 5. Error prevention | ... | ... |
| ... | ... | ... |

### Genre analysis (if `lens-genre` applied)

- Genre identified:
- Move map:

| Section | Move | Strength |
|---|---|---|
| ... | ... | ... |

### Semiotic analysis (if `lens-semiotic` applied)

| Code | Detected? | Detail |
|---|---|---|
| HER | ... | ... |
| PRO | ... | ... |
| SEM | ... | ... |
| SYM | ... | ... |
| REF | ... | ... |

## 5. Replicable lessons (what you can copy)

Five concrete takeaways, each transferable to the reader's own work:

1. <lesson 1, with the design pattern named>
2. <lesson 2>
3. <lesson 3>
4. <lesson 4>
5. <lesson 5>

## 6. Weaknesses / warnings (what's weak)

### Missing genre moves
- ...

### Suspicious warrants (hidden assumptions)
- ...

### Dark-pattern risk
- 🟢/🟡/🔴/⚫ <description>

### Cultural / contextual bias
- ...

### Negative space (mandatory: 3+)

| What's missing | Significance |
|---|---|
| ... | ... |
| ... | ... |
| ... | ... |

---

## Bottom line

<One sentence verdict that captures the artifact's design essence.>

Example: "The artifact is a **🟢 transparent rollout doc** with all 6
canonical moves present and an unusually strong risk section; its
distinctive design choice is **segmented action by role** within a
single document."
