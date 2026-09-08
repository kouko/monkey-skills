# Simplify Loom publication — spec
intent: 2026-09-08-simplify-loom-publication@efc84ee28
pre-build-review: required — this change adds a public publication command and moves the Git and GitHub trust boundary from hook-parsed shell text into executable code

## Requirements
REQ-1 — Validate the merge result, not disposable commits
  WHEN a pull request is opened, synchronized, reopened, or edited, the unchanged `Conventional Commits` required-check name shall validate only `github.event.pull_request.title` against the repository's existing type, scope, subject, and no-trailing-period convention; an invalid title shall fail with the rejected title, expected shape, and reason, while intermediate commit subjects shall not affect the result → Acceptance #1, #2

REQ-2 — One command owns publication
  WHEN an authorized agent invokes `loom_checker.py publish --confirm-authorized` from a selected repository with a PR title and absolute body-file path, the command shall validate the matching content attestation, derive the base from the origin repository's current default branch, push exactly the current immutable HEAD without force to `refs/heads/<current-branch>` on literal `origin`, and create at most one pull request from that branch to that base without asking the caller to construct a Git or GitHub shell command → Acceptance #3

REQ-3 — Publication remains metadata-only
  WHILE `publish` validates and publishes a reviewed branch, it shall not execute the package-test command, adversarial programs, or any other functional verification recorded by the attestation → Acceptance #4

REQ-4 — Reject unsafe publication before its affected network action
  IF authorization confirmation is absent, the body file is not absolute and readable, an unsupported argument or targeting override is supplied, or an ambient Git or GitHub redirection variable is present, THEN `publish` shall reject the invocation as a usage error with exit 2 before any network action; IF the selected path is not the repository root, HEAD is detached or moves, the branch or origin cannot be represented safely, the origin host cannot answer the authenticated GitHub CLI repository query, the origin default branch is absent or equals the head branch, the remote head exists but is not an ancestor of the selected HEAD, the trusted Git or GitHub CLI executable is unavailable, or the attestation does not match the selected HEAD, THEN `publish` shall fail under `push.attestation` with exit 1 before the affected mutating network action → Acceptance #5

REQ-5 — Retry without duplicate pull requests
  IF the exact branch HEAD is already published and an open pull request for that head already exists in the origin repository, THEN `publish` shall return that pull request's URL without creating another; IF the push succeeds but PR creation fails, a retry shall reuse the published branch and still create at most one pull request → Acceptance #3, #5

REQ-6 — Ship invokes the wrapper
  WHEN the Ship station publishes a reviewed branch, its operative instructions shall require one `loom_checker.py publish --confirm-authorized` invocation after decision point ③ and shall no longer instruct the agent to run a separate attestation preflight, construct a canonical Git push, or construct a GitHub PR-create command → Acceptance #3

## Design decision
- agent-decided — Add `publish` to the installed `loom_checker.py` CLI. The checker already owns attestation validation, repository discovery, trusted executable resolution, origin identity, branch identity, and exact-HEAD rules, so keeping orchestration there removes shell-string reconstruction without adding another trust authority.
- agent-decided — Execute Git and GitHub CLI operations as argument arrays with an explicit repository working directory and origin-derived GitHub repository identity. Recompute HEAD immediately before each network action and verify the remote branch after push; never evaluate caller-provided shell text.
- agent-decided — Accept only `--confirm-authorized --title <text> --body-file <absolute-path>`. The flag is a fail-closed acknowledgement for the Ship station after decision point ③, not a claim that code can authenticate the conversation. Do not accept `--repo`, `--base`, `--head`, `--remote`, `--hostname`, force, or raw-refspec overrides. The selected repository is the exact root containing the caller's working directory; the head destination comes from literal `origin` plus the current symbolic branch, and the PR base comes from the authenticated origin repository's default-branch query.
- agent-decided — Query for an existing open PR for the origin-derived repository and current head before creating one. A unique match is success; multiple matches fail closed; no match permits exactly one `gh pr create` attempt.
- agent-decided — Keep the installed `PreToolUse` hook for direct raw `git push` and `gh pr create` commands. `publish` is trusted plugin code and performs the same checks internally; the hook need not parse its internal subprocesses.
- agent-decided — Use a non-forced push only. A read-only remote-head lookup precedes the push: an equal SHA is idempotent, an ancestor may fast-forward, and an unknown or divergent remote SHA fails before push with fetch/reconcile guidance.
- agent-decided — Reject the invocation when ambient Git repository/config redirection variables or GitHub host/repository overrides are present, then also remove them from the subprocess environment as defence in depth and set `GH_REPO` from literal origin. Preserve authentication inputs but prove the origin host and repository by a successful authenticated `gh` query before mutation.
- agent-decided — Treat the local user's authentication configuration, credential helpers, askpass programs, SSH agent, and credentials as trusted host state. Publication constrains destination-changing repository and transport settings; it does not attempt to sandbox a locally compromised Git configuration, because partial executable filtering would break legitimate authentication without establishing a complete security boundary.
- agent-decided — Move the Conventional Commits job into a small independent workflow with one environment-bound PR-title check triggered by `opened`, `synchronize`, `reopened`, and `edited`. This prevents title edits from rerunning unrelated CI, while passing the title through an environment variable keeps untrusted PR text out of workflow shell source.
- agent-decided — Keep publication failures under the existing `push.attestation` rule instead of adding bookkeeping-only rule ids; add `publish` to the checker CLI contract and preserve exit 2 for usage/local-input errors versus exit 1 for decided safety failures.

## Alternatives considered
- Keep the manual canonical commands and improve their documentation — rejected because quoting, executable paths, environment bindings, refspecs, and ordering remain caller-owned and continue to create bookkeeping retries.
- Add a GitHub CLI alias — rejected because aliases are user-local shell expansion and reintroduce quoting plus configuration drift outside the plugin.
- Add a GitHub CLI extension — rejected because it creates a separately installed and updated executable surface while still duplicating Loom's attestation authority.
- Make CI validate the squash commit after merge — rejected because it gives no pre-merge feedback and cannot block a malformed PR title before publication.
- Remove the Conventional Commits job entirely — rejected because the final PR title becomes the squash commit subject and remains a useful repository boundary.
- Combine `finalize-review` with publication — deferred by intent; this change first removes the two observed publication costs without changing functional verification ownership.

## Current state evidence
- Forward: `.github/workflows/skill-structure.yml` job `conventional-commits` checks out full history and walks every subject in `BASE_SHA..HEAD_SHA`, so disposable intermediate subjects can block a valid squash title.
- Reverse: `loom-code/skills/ship/SKILL.md` tells the agent to push the exact selected HEAD and open one PR but exposes no command that performs both operations.
- Trust boundary: `loom-code/scripts/loom_checker.py` functions `canonical_git_push` and `is_canonical_pr_create_command` validate caller-rendered shell bytes, trusted executable paths, origin identity, branch, and refspec independently.
- Functional boundary: `loom-code/scripts/loom_checker.py` function `_cmd_push` validates the generated attestation without executing the commands recorded in it; `loom-code/scripts/test_loom_attestation.py` pins that property.
- Hook boundary: `loom-code/hooks/hooks.json` sends Bash tool calls to `loom_checker.py push --hook`; the hook blocks non-canonical raw publication commands and remains the fallback for callers that bypass `publish`.

## UI flows
- Success: after decision point ③, from any directory inside the selected repository, the agent invokes `python3 <installed-loom-code>/scripts/loom_checker.py publish --confirm-authorized --title <title> --body-file <absolute-file>`; the command identifies the exact repository root, reports attestation validation, derives and reports the base branch, pushes the immutable HEAD without force, creates one PR, prints its URL, and exits zero.
- Existing PR: the same invocation validates current state, confirms the remote branch points at current HEAD, finds one open PR for the current head, prints its URL with an already-exists status, and exits zero without creating another.
- Validation error: a decided publication-safety failure prints `BLOCK push.attestation: <reason>` to stderr and exits one; malformed arguments or unreadable local inputs print a usage error and exit two. Both name a corrective action where one is safe and do not run a later mutating network action.
- Partial retry: after a successful push and failed PR creation, rerunning the same command treats the exact remote HEAD as already published, checks for an existing PR, and creates one only when none exists.
- CI success: the Conventional Commits job prints the accepted PR title and exits zero regardless of intermediate commit subjects.
- CI error: the job prints the rejected PR title, the `<type>(<scope>): <subject>` shape, and the specific mismatch or trailing-period reason, then exits one.
- Piped output: status and the final PR URL are line-oriented plain text; diagnostics go to stderr and success output goes to stdout.

principles lens: conforming — the wrapper preserves machine-owned quality, explicit user publication authorization, recomputed gates, no net mechanism increase, and no mutation of user data.
