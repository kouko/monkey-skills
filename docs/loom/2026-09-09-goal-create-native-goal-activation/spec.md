# goal-create native Goal activation — spec
intent: 2026-09-09-goal-create-native-goal-activation@a1b7e31be6739ca92cc7307b577cdc5457e30321
confirmed-behavior: 2026-09-09 @9295bc8
pre-build-review: required — conditional Claude Code capability plus Codex activation creates a cross-host public behavior contract

## Requirements
REQ-1 — Activate a Codex Goal
  WHEN a user explicitly invokes SESSION mode with sufficient input in Codex and the draft passes lint, the skill shall show the complete four-field condition and activate the current task's native Goal → Acceptance #1

REQ-2 — Activate or propose a Claude Code Goal
  WHEN a user explicitly invokes SESSION mode with sufficient input in an interactive Claude Code session that exposes Goal proposal capability, the skill shall show the complete four-field condition, derive a proposal of at most 500 characters that preserves its Outcome, Verification, and Stop-when bound, and invoke that capability, setting directly only when the user's own words already state the exact outcome and otherwise leaving activation pending explicit confirmation → Acceptance #2

REQ-3 — Fall back without false activation
  IF the current Claude Code session does not expose Goal proposal capability THEN the skill shall state that activation is pending and emit one copyable `/goal <condition>` command without launching another process → Acceptance #3

REQ-4 — Report only observed activation state
  WHEN host activation succeeds, fails, is declined, or remains pending, the skill shall report the matching state and shall call a Goal active only after host-provided success evidence → Acceptance #4

REQ-5 — Preserve the existing contract
  WHILE host activation is added, the skill shall preserve the four-field shape, input-floor refusal, lint behavior, 4,000-character portable ceiling, and ARC mode behavior while emitting the smallest complete condition permitted by the available durable source material → Acceptance #5

## Design decision
Keep the existing host-neutral drafting and linting path, then make one capability check and one native tool call directly in the skill instructions; this is agent-decided because it prevents version or host-name guesses without adding an adapter abstraction or persistent status model.

In Codex, call the public `create_goal` host tool with the complete validated condition; do not add a second representation because the existing four fields already meet the host's objective input.

In Claude Code, prefer the session's `ProposeGoal` tool when it is actually present. Its proposal input has a separate 500-character limit, so derive a compact activation condition from the full condition already shown in the conversation while preserving the Outcome, named Verification check, and Stop-when bound. Set `ask_user: false` only when the user's own words explicitly requested that exact outcome; otherwise use the host's confirmation path. Treat the kickoff or successful tool result, rather than the attempted call, as activation evidence. Any non-success result remains not active, keeps the host's reason visible, and uses the same recovery path; do not create separate handling mechanisms for declined, failed, pending, or already-active results.

When native activation is unavailable or returns a non-success result, print exactly one paste-ready `/goal` command containing the complete condition and label the Goal not active. A proposal awaiting the user's confirmation is the sole exception: label it pending and let the host finish that interaction. Do not invoke `claude -p`, inject keystrokes, or install a custom Stop hook because each would change the session or substitute a different mechanism.

Treat Goal length as an information-design constraint, not a platform-specific writing style. This is agent-decided because OpenAI recommends one objective, one stopping condition, pointers to plans or issues, and the evidence that proves progress; Anthropic recommends the smallest high-signal context that still fully specifies expected behavior. Neither source establishes a universal quality threshold in characters.

Use one advisory content target for the complete four-field Goal: aim for 1,500 Unicode characters whether or not a durable repository artifact is available. Cite an exact path plus heading or stable identifier whenever that artifact can carry detailed scope or verification more clearly. The target may be exceeded whenever further compression would reduce clarity or remove a behavior-changing constraint, decisive verification condition, or bounded stop rule; only the portable 4,000-character ceiling is mandatory for the complete Goal.

Count Unicode characters after removing the `/goal ` prefix and presentation fences. Length includes all four labels and inline source references. This is agent-decided because the host contracts are expressed in characters and the same measurement must behave predictably for Chinese, Japanese, and English text.

Keep only the single outcome, costly-to-violate constraints, the smallest decisive verification surface, and success plus genuine-blocker stop conditions inline. Move task lists, implementation order, repeated project rules, exhaustive test commands, provenance explanations, and speculative edge cases to the cited artifact. Never shorten by replacing a measurable end state with a vague summary or by hiding a destructive or externally visible side effect behind a reference.

When a complete draft exceeds the 1,500-character advisory target, make one compression pass that removes duplication and moves eligible detail to a durable source. If no sufficient source exists, keep the self-contained content instead of inventing a weak citation. Remaining above 1,500 characters is not an error and requires no warning label; exceeding 4,000 remains a lint failure.

Apply the 500-character hard limit to Claude Code's `ProposeGoal` input regardless of the displayed tier. When the displayed condition is longer, the proposal shall preserve the Outcome, decisive Verification, and Stop-when bound and refer to the complete condition already surfaced in the current conversation. The manual `/goal` fallback uses the complete displayed condition, not the compact proposal representation.

Update the skill and plugin-facing descriptions in all three maintained languages so discovery promises creation where supported and an honest activation fallback elsewhere.

## Alternatives considered
- Always print `/goal`: rejected because it leaves Codex's public activation tool and Claude Code's conditionally available proposal tool unused.
- Require `ProposeGoal` in every Claude Code session: rejected because a live interactive 2.1.266 session omitted it despite the type being shipped.
- Launch `claude -p "/goal ..."`: rejected because it starts a separate invocation rather than activating the current session.
- Implement a custom Stop hook: rejected because it would be a second Goal engine and is explicitly outside this change.
- Send the complete condition through `ProposeGoal`: rejected because that tool's published SDK input permits at most 500 characters even though Claude Code's typed `/goal` accepts 4,000.
- Use 500 characters as a complete-Goal target or limit: rejected because the existing four-field framework produced no historical sample at or below 500 characters, and necessary clarity, constraints, or verification detail outrank that artificial target.
- Enforce 1,500 characters as a complete-Goal limit: rejected because neither vendor recommends that numeric threshold; it is a compression prompt, not a validity boundary.
- Permit every Goal to grow toward 4,000 characters: rejected because vendor guidance favors outcome-first, minimally sufficient context and external state for long-running work; the technical ceiling is not a quality target.
- Set different writing budgets for Codex and Claude Code: rejected because attention quality depends on the information and surrounding context rather than the host name; only the activation transport has a platform-specific hard limit.
- Add host adapter files, status enums, or per-result handlers: rejected because the skill needs only one capability branch, host success evidence, and one shared non-success recovery path.

## Current state evidence
- Forward: `loom-workflow/skills/goal-create/SKILL.md:14` defines SESSION mode; its current experimental host branch begins at the `After the checker exits 0` anchor.
- Reverse: `loom-workflow/skills/handoff/SKILL.md:89` presents `loom-workflow:goal-create` as the named way to add a session acceptance condition.
- Error: `loom-workflow/skills/goal-create/SKILL.md:54` currently handles only an absent Claude tool and does not specify declined, failed, pending-confirmation, or already-active outcomes.
- Data: `loom-workflow/skills/goal-create/references/goal-shape.md:7` owns the ordered Outcome, Constraints, Verification, and Stop-when condition with a portable 4,000-character budget.
- Boundary: `loom-workflow/skills/goal-create/SKILL.md:62` starts ARC mode, which remains outside the host activation change.

## UI flows
### SESSION mode in Codex
- User invokes `goal-create SESSION` with both required inputs and a sufficient existing plan, specification, or issue → a complete four-field Goal aims to stay within 1,500 characters and points to that source where useful; exceeding the target is allowed, activation succeeds in the current task, and the response says the Goal is active.
- User invokes it without a sufficient durable source → a self-contained four-field Goal follows the same 1,500-character advisory target; exceeding the target is allowed, and it activates after passing the mandatory 4,000-character ceiling.
- Drafting or lint is in progress → normal skill progress is shown; no Goal is described as active yet.
- Input is missing or lint cannot pass → the existing refusal or lint error is shown and no activation is attempted.
- Host activation fails → the failure is reported as not active with the host's recoverable reason; no success wording is shown.

### SESSION mode in Claude Code with Goal proposal capability
- User explicitly invokes `goal-create SESSION` and states the exact wanted outcome → the complete validated four-field Goal is shown, a faithful proposal of at most 500 characters activates the native Goal, and the host kickoff confirms it is active.
- The requested outcome was inferred or changed during drafting → the complete condition is proposed for confirmation and remains pending until the user accepts it.
- Native activation returns any non-success result → the response preserves the host's reason, says the Goal is not active, and provides one paste-ready `/goal` command for recovery; no result-specific state machinery is added.

### SESSION mode in Claude Code without Goal proposal capability
- User invokes `goal-create SESSION` with sufficient input → the complete validated four-field Goal is shown, the response says activation is pending, and one paste-ready `/goal` command containing that same condition is printed.
- User submits that `/goal` command → Claude Code's native Goal behavior takes over; `goal-create` makes no activation claim before this user action.
- Non-interactive, plan, subagent, disabled, or rollout-ineligible context omits the tool → the same pending fallback is used without guessing which eligibility condition caused the omission.

### Preserved paths
- User invokes ARC mode → existing purpose-drafting behavior runs unchanged and no session Goal activation is attempted.
- User invokes SESSION mode without current state or wanted difference → existing refusal behavior runs unchanged and emits neither a Goal nor an activation command.
