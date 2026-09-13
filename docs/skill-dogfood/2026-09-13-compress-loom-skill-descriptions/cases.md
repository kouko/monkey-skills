# Loom description routing corpus

## Frozen accounting baseline

Source: commit `c9a9b9d9faa75e004e302bee64a61587bbb0ab56` (W0).
Only normalized description scalars are stored, not skill bodies. This snapshot
keeps the historical denominator verifiable in archives and shallow checkouts.

```json description-baseline
{
  "loom-code/skills/build/SKILL.md": "Implements a committed plan with test-first changes, focused verification, and one integration pass before the closing Review. Use when a confirmed intent and plan are ready to build.",
  "loom-code/skills/maintain/SKILL.md": "Routes an incident or regression outside an active unmerged change into an existing or new intent. Use for bug reports, alerts, post-delivery regressions, or dogfood incidents.",
  "loom-code/skills/review/SKILL.md": "Runs the one closing review over completed functional content, executes package and adversarial verification once, and generates a content-bound attestation. Use when Build is complete or a functional change invalidates prior evidence.",
  "loom-code/skills/ship/SKILL.md": "Publishes a reviewed branch by validating its generated content attestation, running fast publication safety checks, opening the pull request, and verifying CI. Use after Review generated a matching attestation.",
  "loom-code/skills/write-plan/SKILL.md": "Turn a confirmed intent into a task plan at docs/loom/<change-id>/plan.md. Use when someone asks to plan, start, or implement a change; when an intent file exists but is not confirmed yet; or when there is no intent yet and the work is about to begin. This is the entry station for engineering changes, and the entry station for every change when loom-design is not installed.",
  "loom-design/skills/capture-intent/SKILL.md": "Interview the user and write a confirmed intent at docs/loom/intent/<change-id>.md. Use when someone describes something they want built or changed — \"I want…\", a feature idea, a bug they keep hitting — and no intent file exists yet. This is the entry station for every change when loom-design is installed.",
  "loom-design/skills/design-system/SKILL.md": "Interview the user and write a ratified DESIGN.md visual design system — colors, typography, layout, component tokens. Use for a product with a UI, before or during write-spec; never required — DESIGN.md never blocks a change. Triggers: 視覺設計系統 / 設計語言 / デザインシステム.",
  "loom-design/skills/product-principles/SKILL.md": "Interview the user and write a ratified PRINCIPLES.md constitution — Who, Non-negotiables, Won't do, Failure we must avoid, Fixed choices. Use when a product change needs principles and the repo has none ratified yet, or when asked what should govern a product/design/engineering trade-off. Triggers: 產品原則 / 設計原則 / 工程原則 / 產品憲章 / プロダクト指針.",
  "loom-design/skills/write-spec/SKILL.md": "Turn a confirmed intent into docs/loom/<change-id>/spec.md, confirm visible product behaviour, declare whether pre-build review is required, and hand high-risk specs to one independent reviewer before planning. Use when an intent says needs-design: yes and no spec exists yet, or when someone asks for a spec or a design of a change.",
  "loom-workflow/skills/cot-explain/SKILL.md": "Explains how something was reasoned — a file the user names, or the work just done here — as a standalone page built around a chain-of-thought diagram, every arrow labeled with why that step follows. Use when the request is about a process: how a conclusion was reached, why a design went one way, what was tried and rejected; or when the user asks for the artifact by name — a CoT diagram, a CoT mermaid chart, a reasoning-chain write-up. A request about a state — what a function does, what a file says — is answered directly without this skill, and a request for a diagram that is not a chain of reasoning belongs to a general Mermaid skill.",
  "loom-workflow/skills/critique/SKILL.md": "Judge a proposal before it is built, through one of two lenses. `mode: proposal` triages a list, plan, or prose recommendation into KEEP / DEFER / DROP by evidence grounding and YAGNI. `mode: complexity` weighs one specific change deletion-first: before/after lines, what it obsoletes, and whether a smaller end state exists. Use for 'critique this', 'over-engineered?', 'can this be simpler?', 'worth the lines?', 'what can we delete?', 'should we build this?', '業界證實', '可以簡化嗎'.",
  "loom-workflow/skills/dbt-model-style/SKILL.md": "Enforces a dbt + Redshift model style & structure contract — CTE roles, zero-logic final CTE, naming, YAML header, comments, syntax. Use when authoring, editing, or reviewing a .sql dbt model, or '符合規範嗎'. Structure only, not logic/layer design.",
  "loom-workflow/skills/decision-map/SKILL.md": "Chart and work through a persistent Outcome Map at docs/loom/maps/<map-id>/ — one long-term outcome-control loop whose fog becomes typed tickets and whose delivery arcs close independently across many sessions. Use for '開地圖' / '開一張決策地圖' / 'chart a decision map' / 'work through the map' / '推進地圖' / 'デシジョンマップを開く' / 'ワークスルー', and to start, resume, claim, re-chart, migrate, retire, or assess a live Map. Not for one self-contained task (use loom-code:write-plan) or one factual question (use research-toolkit).",
  "loom-workflow/skills/distill-sessions/SKILL.md": "Mine past Claude Code and Codex session transcripts + /insights for friction patterns → a per-skill improvement-proposals doc. Use to audit skill-activation telemetry, or gather evidence before a refactor. For creating a skill use skill-creator-advance.",
  "loom-workflow/skills/git-memory/SKILL.md": "Mandatory gate before every git commit / gh pr create / gh pr merge — the skill decides whether memory trailers (Decision/Learning/Gotcha) apply; don't pre-judge a commit 'routine'. Also recalls past decisions: 'why did we…', '為什麼', an old branch.",
  "loom-workflow/skills/goal-create/SKILL.md": "Create a goal condition — SESSION mode validates the four-field goal (Outcome / Constraints / Verification / Stop-when), activates it when the current host accepts it, and gives an honest recovery action otherwise. ARC mode drafts a repository's purpose artifact `Why` / `Done when` for the user to land. Use for 'set a goal', 'give this run a stopping condition', '設一個目標', 'ゴールを立てて'. This skill never fires on its own; it must be invoked by name.",
  "loom-workflow/skills/handoff/SKILL.md": "Save session state to a structured HANDOFF file so a future agent resumes cleanly, or load/verify a prior HANDOFF. Use for 'wrap up', 'save state', 'done for today', or 'pick up where we left off'. For in-session re-orientation use recap-state.",
  "loom-workflow/skills/independent-advisor/SKILL.md": "Get a second opinion on the current plan or decision from a different executor — a stronger model, a higher effort level, or another vendor — instead of a different critique lens. Use for 'second opinion', 'ask a stronger model', '換一個模型看看', 'コードを別のモデルに見せて'. For a same-executor critique use critique (mode: proposal for a list, mode: complexity for one over-engineered change).",
  "loom-workflow/skills/loom-memory/SKILL.md": "Recall, Record, Reconcile, or Retire a durable repository lesson in the OKF v0.2-compatible loom-memory store. Use only when the user explicitly asks to remember, recall, forget, or reconcile repository knowledge (\"記得這個坑\", \"之前是怎麼解的\", \"把這個教訓記下來\", \"這條還準嗎\", \"remember this\", \"what did we learn about X\", \"忘れないで\"), or when you independently judge the current task needs a prior repository lesson. Works standalone or alongside loom-code / loom-design; neither requires it. For commit- or PR-bound decisions, learnings, and gotchas, use loom-workflow's git-memory instead.",
  "loom-workflow/skills/recap-state/SKILL.md": "in-session re-orientation: produce a structured recap ending with a Synthesis-check when the user loses the thread. Use for \"where were we\", \"I'm lost\", \"我們剛剛在幹嘛\", \"剛剛講到哪\", \"我跟丟了\", \"ちょっと振り返って\", \"今どこだっけ\", \"振り返り\", or similar requests. The built-in /recap is an away-summary; for cross-session continuation use handoff."
}
```

Frozen before router and description edits, 2026-09-13. This corpus tests
selection at the exposed skill boundary; it does not claim a universal
implicit-invocation rate. W2 records the model, prompt, selected skill, and
whether each expected or forbidden route held.

## Runner contract

- Give each request to a fresh context with the candidate Loom skill catalog.
- Record the selected skill name, whether a router was loaded, and the result.
- A direct skill request passes only when its named leaf is selected; it need
  not load a router first.
- `expected: none` passes only when no Loom skill is selected.
- `explicit-only` passes only for the named invocation. Natural-language
  variants must not be reported as evidence that the explicit-only skill
  implicitly triggered.

The first six requests below are the original W0 corpus. Subsequent requests
are W2 additions held out from description editing. The two specific design
and workflow requests permit direct leaf selection: their initial W2 router
expectation was corrected after observing the blind result, because routers
are optional when the leaf is clear. These are not pre-frozen router passes;
see the report for the unchanged observation and assessment history.

```json routing-cases
[
  {
    "id": "plugin-umbrella",
    "kind": "positive",
    "request": "Use Loom to help me implement a confirmed engineering change.",
    "expected": "using-loom-code",
    "forbidden": [],
    "invocation": "implicit"
  },
  {
    "id": "direct-leaf",
    "kind": "positive",
    "request": "Use $loom-code:write-plan for the confirmed intent.",
    "expected": "write-plan",
    "forbidden": [],
    "invocation": "explicit"
  },
  {
    "id": "adjacent-skill-collision",
    "kind": "boundary",
    "request": "The intent is already confirmed; make the implementation plan.",
    "expected": "write-plan",
    "forbidden": ["capture-intent", "write-spec"],
    "invocation": "implicit"
  },
  {
    "id": "ordinary-request",
    "kind": "negative",
    "request": "Translate this short sentence into Traditional Chinese.",
    "expected": "none",
    "forbidden": ["using-loom-code", "using-loom-design", "using-loom-workflow"],
    "invocation": "implicit"
  },
  {
    "id": "multilingual-request",
    "kind": "positive",
    "request": "這個已確認 intent 需要設計規格，請先寫 spec。",
    "expected": "write-spec",
    "forbidden": ["write-plan"],
    "invocation": "implicit"
  },
  {
    "id": "explicit-only-goal-create",
    "kind": "boundary",
    "request": "Use $loom-workflow:goal-create to set a stopping condition for this session.",
    "expected": "goal-create",
    "forbidden": [],
    "invocation": "explicit-only"
  },
  {
    "id": "held-out-design-specific",
    "kind": "positive",
    "request": "Use Loom to define our product: we need colors, typography, and component tokens.",
    "expected": "design-system",
    "forbidden": ["using-loom-code"],
    "invocation": "implicit"
  },
  {
    "id": "held-out-workflow-specific",
    "kind": "positive",
    "request": "Use the Loom workflow toolbox: assess whether this proposal has too many moving parts.",
    "expected": "critique",
    "forbidden": ["independent-advisor"],
    "invocation": "implicit"
  },
  {
    "id": "held-out-unnamed-goal",
    "kind": "negative",
    "request": "Set a stopping condition for this session.",
    "expected": "none",
    "forbidden": ["goal-create"],
    "invocation": "implicit"
  },
  {
    "id": "held-out-design-umbrella",
    "kind": "positive",
    "request": "Use Loom to help define a product change; I am not sure whether I need an intent, spec, principles, or a visual system.",
    "expected": "using-loom-design",
    "forbidden": ["using-loom-code"],
    "invocation": "implicit"
  },
  {
    "id": "held-out-workflow-umbrella",
    "kind": "positive",
    "request": "Use Loom's workflow tools to help me, but I am not sure which workflow skill applies.",
    "expected": "using-loom-workflow",
    "forbidden": ["using-loom-code", "goal-create"],
    "invocation": "implicit"
  }
]
```
