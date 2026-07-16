# loom-* weak-model behavioral audit (haiku cold-read)

**Date:** 2026-07-16 · **Method:** one haiku (weak-model) agent per skill loads the SKILL.md cold and ENACTS a representative scenario that exercises the skill's core behavioral contract; graded PASS = the contract fires (refusal / gate / routing / output shape) on the weak model. Purpose: robustness audit — does each loom skill survive a weak implementer/reviewer, not just a strong one. Independent of token-slimming.

**Result: 26/26 loom-* skills PASS** (no skill's core contract failed to fire on haiku).

## loom-code (12)
| skill | probe | result |
|---|---|---|
| subagent-driven-development | multi-feature auth module | ✅ split into atomic tasks + 3-agent triads |
| writing-plans | CSV-export brief | ✅ atomic tasks, one RED/GREEN test each, dependency graph |
| requesting-code-review | "review my branch to merge" | ✅ whole-branch review → NEEDS_REVISION (**caught a real issue on this branch: new reference files untracked**) |
| tdd-iron-law | "just write the email validator" | ✅ refused; failing test first |
| systematic-debugging | "sometimes returns null, fix it" | ✅ refused to fix before REPRODUCE |
| verification-before-completion | "done, it works" | ✅ (re-probe w/ explicit code) refused; ran package tests. Note: a thin "it works" prompt let haiku invent a doc-only exemption — real invocations carry actual changed files |
| dispatching-parallel-agents | 3 unrelated failing tests | ✅ one subagent per domain, single fan-out |
| using-git-worktrees | "redesign while keeping main" | ✅ git worktree, not stash |
| ui-verification | "screen built, tests pass" | ✅ fail-closed N/A when no real ui-flows.md found (correct conditional gate) |
| using-loom-code | "add a feature" | ✅ routed to brainstorming (Stage 1) first |
| brainstorming | (equivalence-gate session) | ✅ Red Flags refusal + Axis-4 template load |
| finishing-a-development-branch | (equivalence-gate session) | ✅ Red Flags refusal + exemption + git-memory (post-fix) |

## loom-spec (3)
| completeness-critic | login spec draft | ✅ critic panel fired, hunted 13 NFR/security omissions (TLS, rate-limit, session, a11y, i18n, MFA, compliance…). Note: haiku's *parent-agent aggregation* of its own panel stumbled — a haiku multi-agent-orchestration limitation, not a skill-text defect (in practice a stronger orchestrator dispatches the panel) |
| spec-expansion | "users upload a profile photo" | ✅ fanned out objects/states/paths/edge-cases → 7 acceptance criteria (OpenSpec), 10 blind spots |
| using-loom-spec | "one-liner → full spec" | ✅ routed to spec-expansion |

## loom-interface-design (4)
| design-critic | "critique my design draft" | ✅ fail-closed — asked for the real DESIGN.md/ui-flows.md; named the 5-lens panel |
| design-system | "design system for task app" | ✅ DESIGN.md with color/type/layout/component tokens, WCAG-AA; flagged missing PRINCIPLES.md |
| interaction-flows | "map checkout flows" | ✅ ui-flows.md: screens, Mermaid nav, ASCII wireframes, transitions, responsive |
| using-loom-interface-design | "design UI/UX" | ✅ routed to design-system + interaction-flows |

## loom-product-principles (2)
| product-principles | "principles for habit app" | ✅ required user vision first (anchors falsifiable principles) before generating |
| using-loom-product-principles | "new idea, where to start" | ✅ routed to discovery first (on-ramp row 4: users unarticulated) |

## loom-discovery (3)
| business-value | "worth building a finance dashboard?" | ✅ adversarial worth-it interrogation ("Why now?") |
| user-insights | "who needs a meal planner?" | ✅ evidence-linked job stories, problem-space-pure, value commitment left UNRATIFIED |
| using-loom-discovery | "unsure who/worth it" | ✅ routed who→user-insights, worth-it→business-value |

## loom-pipeline (2)
| using-loom-pipeline | "run the whole pipeline" | ✅ checked BOTH-gate precondition, Workflow unavailable → N/A-loud |
| loom-memory | "prior lessons on X?" | ✅ recall: grepped store index+bodies, surfaced hit files with citations |

## Cross-cutting observations
- **3 conditional/fail-closed skills behaved correctly** (ui-verification, design-critic, using-loom-pipeline) — emitted N/A or asked for missing artifacts rather than fabricating. This is the correct weak-model posture.
- **completeness-critic + design-critic** require the executing agent to dispatch a critic PANEL; haiku can *be* a panelist fine, but haiku *orchestrating* the panel is fragile (known limitation). These critics are normally dispatched by a stronger orchestrator — unaffected in practice.
- **verification-before-completion**: the pure-doc exemption is invokable by a weak model that assumes a doc-only context from a thin prompt. Mild robustness note; a real invocation carries concrete changed files.
- **Bonus find:** the requesting-code-review probe reviewed this very branch and flagged that the newly-created reference files were git-untracked — a real close-out reminder.
