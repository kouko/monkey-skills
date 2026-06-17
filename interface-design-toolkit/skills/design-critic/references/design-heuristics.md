# Design-critic heuristics — Nielsen × the 7 UX dimensions

The design-critic's lenses are **grounded in canon, not invented**. Each lens is
an intersection of **Nielsen & Molich's 10 usability heuristics** (the canonical
heuristic-evaluation set — Nielsen, J., & Molich, R. (1990) *Heuristic evaluation
of user interfaces*, CHI '90; refined as Nielsen's 10 heuristics, 1994/updated
2024) with the **7 UX generation dimensions** this toolkit's `interaction-flows`
skill already produces (`interaction-flows/references/ux-flow-checklist.md`).

Do **not** author a fresh "design completeness" checklist — that reinvents
Nielsen. Cite the heuristic each finding maps to.

## The 7 UX dimensions (from `interaction-flows`)

The dimensions `ui-flows.md` is generated across (canonical source:
`interaction-flows/references/ux-flow-checklist.md`), enumerated here so this
reference is self-contained:

1. Screen / panel / command **inventory** (+ render-variant flags)
2. **User flows** (mermaid)
3. **UI structure** (ASCII layout)
4. **Transitions** (instant / guided / deliberate)
5. **Entry points** (how the user arrives)
6. **Exit points** (kill dead-ends)
7. **Information density** + modality flow

## Nielsen's 10 heuristics (the canon)

1. Visibility of system status
2. Match between system and the real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognize, diagnose, and recover from errors
10. Help and documentation

## The 5 load-bearing lenses (Nielsen × 7-dim)

| Lens | Nielsen heuristic(s) | UX dimension(s) | The omission it hunts |
|---|---|---|---|
| **1. Render-state completeness** | H1 visibility of system status | dim 1 inventory + render-variant flags | Is every surface's **empty / loading / error / success** variant designed? A surface with only the populated/happy variant is incomplete. |
| **2. Dead-end & exit / user control** | H3 user control & freedom | dim 6 exit points (kill dead-ends) | Does every surface offer a way **forward / back / out**? Are destructive actions **reversible (undo)** or gated by a confirm? Any dead-end = a finding. |
| **3. Navigation reachability & entry** | H2 match real world · H6 recognition not recall · H7 flexibility | dim 2 user flows + dim 5 entry points | Is **every screen reachable** from some flow (no orphans)? Are **all entry points** (deep link, notification, cold start, resume) enumerated? |
| **4. Error prevention & recovery** | H5 error prevention · H9 recover from errors | dim 1 error variant + dim 4 transitions | Are **error screens** designed (not just happy path)? Do irreversible actions have **confirms**? Is there a **recovery path** from every error state? |
| **5. Modality fit & accessibility** | H4 consistency & standards · H8 aesthetic/minimalist | dim 7 density + modality | Are the **render variants for the target modality** flagged (GUI responsive/narrow; TUI narrow-terminal; CLI non-TTY-piped)? Are **a11y** omissions (focus order, labels, contrast intent) surfaced? |

## Boundary

These lenses hunt **surface/usability omissions** on `DESIGN.md` / `ui-flows.md`
— *is the state/exit/screen designed?* They do **NOT** hunt the **behavioral**
omissions of the spec (state-machine transitions, edge-case fan-out, acceptance
scenarios) — that is `spec-toolkit:completeness-critic`'s job, one stage later.
**Flag the surface gap here; fan out the behavior there.**

**Worked surface-vs-behavior pairs** (the lenses — especially error-prevention and
principles — drift toward behavior; hold the line with these):

| Behavior (NOT yours — spec critic) | Surface (YOURS — design critic) |
|---|---|
| "the undo window is N seconds; expiry makes send final" (a rule) | "is an **undo toast** drawn after Send? where?" (a surface) |
| "delete is soft vs hard; what cascades" (a transition) | "is a **delete-confirm dialog** drawn? is the delete entry point on a screen?" |
| "validation: amount must be > 0, reject negatives" (a rule) | "is the **inline error state** of the amount field drawn?" |
| "overdue = derived vs persisted; recompute on what event" (logic) | "is the **overdue badge/state** shown on the list row + detail?" |

If your finding is a *rule / transition / computation*, it belongs to the spec
critic — drop it. If it is a *screen / state / dialog / toast / affordance that is
not drawn*, it is yours.

## Deletability (Bitter Lesson)

The **panel** (writer ≠ judge — an external check on the design) is
verification-class: keep it regardless of model strength. Each **individual
lens** is closer to a crutch — a stronger model may derive its coverage unaided.
So each lens is **designed deletable**: the panel mechanics do not depend on the
specific lens set. **Re-baseline periodically** (bare-model-vs-panel) and prune
any lens the current model has subsumed.
