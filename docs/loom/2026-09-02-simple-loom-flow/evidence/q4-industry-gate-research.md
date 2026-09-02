# Deterministic enforcement layer — industry research (2026-09-02)

## Q1. How existing agent-workflow frameworks enforce hard gates across hosts

| Project | Enforcement mechanism | Cross-host? | Evidence |
|---|---|---|---|
| obra/superpowers | Prose skill ("using-superpowers" 1% rule) + Claude Code `hooks.json` lifecycle hooks (SessionStart synchronous injection since v4.3.0). "Hard gate" blocking implementation until design approved is enforced by **skill/checklist convention**, not a script that can't be talked past. | Claude Code only (hooks.json is CC-specific) | github.com/obra/superpowers, deepwiki.com/obra/superpowers/5.1 |
| BMAD-METHOD | Three enforcement points: fragments steer generation (prose), a **git hook blocks the write** (commit-msg/pre-commit/post-merge), test-review scores what landed. | git hooks are host-agnostic once installed, but installation is framework/npm-specific | github.com/bmad-code-org/BMAD-METHOD discussions #878, #1473 |
| github/spec-kit | Docs explicitly say: **"The only reliable enforcement mechanism is code — tests, hooks, CI gates."** Base toolkit itself does NOT enforce (specs are living docs); community extensions ("CI Guard", "Architecture Guard") add gates. | CI/hook-based, add-on, not built in | dev.to/htekdev/github-spec-kit-turn-english-into-production-ready-specs-27o2 |
| OpenSpec (Fission-AI) | Explicitly **stays out of git**: "OpenSpec never touches git, so it fits your existing workflow instead of replacing it... never commits, branches, pushes, or pulls." Provides `openspec validate --archived` — a CLI check "perfect for a pre-commit or CI hook" but you must wire it yourself. Also has onCreate/onArchive shell-script hooks (its own hook system, not git hooks). | Any host, because it's just files + a validator CLI you wire into CI/hooks yourself | github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md, github.com/Fission-AI/OpenSpec/blob/main/docs/team-workflow.md |
| AWS Kiro | "Agent Hooks" = event-driven automations (file save, PR open, manual) that trigger an agent task — NOT a blocking gate, more an automation trigger. Kiro's own IDE feature; **"hooks are stored at repository level, the entire team benefits from this automation immediately upon repository checkout"** (i.e., zero-init by virtue of being repo-committed IDE config). | Kiro IDE only | kiro.dev/blog/introducing-kiro/ |
| Cursor rules/hooks | Cursor Hooks (v1.7+): `preToolUse`/`beforeReadFile` etc., same exit-code semantics as Claude Code (exit 2 blocks). **"Cursor... will even load your existing Claude Code hook configuration"** — i.e., Cursor explicitly adopted the Claude Code hook contract for compatibility. Separately, Cursor can be told to run `git commit --no-verify`, defeating git-hook-based rules unless a PreToolUse hook specifically blocks the `--no-verify` flag. | Cursor natively re-uses Claude Code's hook config = de facto shared contract | cursor.com/docs/hooks; ranthebuilder.cloud/blog/agentic-coding-hooks-deterministic-ai-guardrails/ |
| Gemini CLI | Hooks introduced v0.26.0+, config in `.gemini/settings.json` (project) / `~/gemini/settings.json` (user), synchronous, stdin/stdout JSON protocol, matcher regex on tool names. Extensions can bundle hooks. | Gemini CLI only, but same shape (stdin JSON in / stdout JSON out, sync) as Claude Code | github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md, geminicli.com/docs/hooks/ |
| Codex CLI | **Official, current, enabled by default** — confirmed via developers.openai.com/codex/hooks (redirects to learn.chatgpt.com/docs/hooks). Config discovered automatically at `~/.codex/hooks.json`, `~/.codex/config.toml` `[hooks]`, `<repo>/.codex/hooks.json`, `<repo>/.codex/config.toml` — **"No initialization step is required."** "Hooks are enabled by default" (disable via `[features] hooks = false`). Windows supported via `commandWindows` override. PreToolUse stdin payload: `session_id, cwd, hook_event_name, tool_name, tool_input, permission_mode` (Claude-Code-shaped). NOTE: an older third-party blog (codex.danielvaughan.com, dated Apr 2026) claimed hooks were "experimental, disabled by default, not available on Windows" as of v0.114 (Mar 2026) — that appears **stale**; the current official doc (fetched today) contradicts it on both disabled-by-default and Windows support, so hooks matured/became default sometime between Mar and Sep 2026. | Yes — repo-local `.codex/hooks.json` is the zero-init, per-repo path | learn.chatgpt.com/docs/hooks (official, redirect target of developers.openai.com/codex/hooks) |

**Cross-cutting finding**: "Claude Code's design of JSON on stdin with exit 2 to block has become the de facto convention" — Cursor, Codex, and Gemini CLI all converged on essentially the same hook contract shape (stdin JSON, PreToolUse/PostToolUse naming, deny via exit code / JSON decision field). Source: github.com/rohitg00/awesome-claude-code-toolkit search summary; corroborated independently by Cursor's own docs re-using CC's format and Codex's stdin JSON shape matching CC's field names.

**Implication for your design**: A **repo-committed `.codex/hooks.json` + `.claude/settings.json` (or `hooks.json`) pair** pointing at the *same* underlying script is a real, host-supported, zero-init pattern for Claude Code + Codex CLI today (both auto-discover repo-local hook config with no init command). Cursor adds itself for free if it keeps reading CC's hook config. Gemini CLI needs its own `.gemini/settings.json` hook entry (different file, same script). None of these are a **backstop that survives an agent simply not running the host** (e.g., a human running `git commit` directly, or CI) — that requires an independent git-level or CI-level check (Q5).

---

## Q2. Zero-init git hook installation patterns

| Mechanism | How it works | Needs a user action after `git clone`? |
|---|---|---|
| **husky** | `"prepare": "husky"` (or `is-ci \|\| husky install`) in package.json — `prepare` is an npm lifecycle script that runs automatically on `npm install`. | **No manual step**, but *does* require `npm install` to run at least once (which most workflows do anyway). CI should set `HUSKY=0` to skip. Source: typicode.github.io/husky/get-started.html, sonspring.com/journal/husky-v5-and-npm-prepare |
| **lefthook** | `postinstall` (npm) writes hooks into `.git/hooks/`; idempotent. Caveat: pnpm requires `onlyBuiltDependencies` allow-listing or `postinstall` silently never runs. Conflicts with a pre-existing `core.hooksPath`. | No manual step **if** package manager runs postinstall/prepare scripts (pnpm needs explicit opt-in). Source: lefthook.dev/installation/node/, github.com/evilmartians/lefthook/issues/1248 |
| **pre-commit (Python framework)** | Canonical flow needs an explicit `pre-commit install` after clone — this is the **documented gap**. Workaround: `git config --global init.templateDir <dir>` with hook scripts pre-staged in the template dir, so `git clone`/`git init` auto-populates `.git/hooks/` from the template — but this is a **per-developer machine-global config**, not something the repo itself can force on a fresh clone. | **Yes, by default** (`pre-commit install` required) unless the developer has pre-configured `init.templateDir` themselves — not something the repo can push onto a clean machine. Source: pre-commit.com, gist.github.com/CITguy/e8cecbbb7408a93f28c1cbaccaec6765 |
| **`core.hooksPath` set at clone via `init.templateDir`** | Git 2.9+ `core.hooksPath` repoints hook lookup; combined with `init.templateDir`, a global template can auto-set `core.hooksPath` on every new repo. Still a **local machine prerequisite** — cannot be shipped inside the repo itself, because `.git/hooks` isn't tracked and `core.hooksPath` isn't set until something (a human, or another already-running hook) sets it. | No if machine is pre-configured; **yes** (someone/something must run the config command once per machine) otherwise. |
| **`.githooks/` committed in repo + `core.hooksPath .githooks`** | Scripts live in a tracked folder; still requires **one `git config core.hooksPath .githooks` command** post-clone, OR an npm/other package-manager postinstall step that runs it automatically for you. | **No, if wrapped in a postinstall/prepare script** (i.e., piggybacking on Q2's husky/lefthook pattern); otherwise yes. Source: githooks.com, viget.com/articles/two-ways-to-share-git-hooks-with-your-team |
| **rycus86/githooks ("Githooks")** | A dedicated tool for **per-repo and global git hooks with version control** — hooks live in the repo, tool manages installation/updates across the team, has a "post-init" hook idea to auto-set `core.hooksPath` in newly created/cloned repos. | Still needs the Githooks tool itself installed once per machine; then subsequent repos are handled automatically. Source: github.com/rycus86/githooks |
| **"lazy install on first command" pattern** | Not found as a named, documented convention distinct from the above — closest real analogue is a wrapper script/binary (e.g., a CLI tool's own subcommand) that checks on every invocation whether `core.hooksPath`/hook files are present and (re)installs them if missing — several `agent-guardrails`/`agentjail`-style projects (Q3) do this implicitly via their CLI's own bootstrap. | Depends on implementation; not a standardized git-native mechanism. |

**Bottom line for your design**: the only mechanisms that need **literally zero user action after `git clone`** without any prior machine-level config are ones piggybacked on a package manager's `prepare`/`postinstall` lifecycle (husky/lefthook pattern) — and even those depend on the workflow running `npm install`/`pnpm install` at some point. For a language-agnostic (non-npm) repo, there is **no git-native "hooks auto-install on clone" mechanism** — `init.templateDir` only helps if pre-configured on the developer's machine *before* the clone, which you cannot control or ship. This is a real gap your project would need to fill with something like a first-run bootstrap inside the CLI-specific hook itself (Claude/Codex hook configs ARE zero-init per Q1, so they could be the trigger that lazily installs the git-level hook on first agent invocation).

---

## Q3. Cross-host "one guard implementation + adapters" projects

- **LuD1161/agentjail** — "Policy guardrails for coding agents (Claude Code, Codex, Cursor) — every tool call is checked locally, before it runs." Explicitly multi-host, single policy engine. github.com/LuD1161/agentjail
- **JeongJaeSoon/agent-guard** — "Real-time secret-leak guardrails for AI coding agents (Claude Code, Codex), Git hooks, and CI" — explicitly layers git hooks + CI on top of agent-level hooks, i.e. exactly the "belt and suspenders" pattern you're asking about. github.com/JeongJaeSoon/agent-guard
- **logi-cmd/agent-guardrails** — "Merge gates and safety checks for AI coding agents. Works with Claude Code, Cursor, Windsurf, Codex via MCP. Detect scope violations, missing tests, and risks before merge." Uses **MCP** as the cross-host adapter layer rather than replicating each host's native hook format. github.com/logi-cmd/agent-guardrails
- **block-no-verify** (tupe12334) — narrow single-purpose CLI to block `--no-verify`; explicitly named as an AI-agent-bypass countermeasure. github.com/tupe12334/block-no-verify
- **hookflows** (htek.dev article "Stop Trusting AI Agents with Git — Start Governing Them") — intercepts raw git commands and replaces them with governed alternatives (e.g. `dev_commit`) that enforce validation/co-author trailers structurally, rather than relying on hooks alone. htek.dev/articles/hookflows-governed-git-for-ai-agents
- Cursor's own docs note it **reuses the Claude Code hook config format** directly rather than building a separate adapter — the "one implementation" already exists at the config-format level for these two hosts. cursor.com/docs/hooks

No project found that ships one **git-level** (not agent-level) guard script with adapters registering it identically into Claude Code hooks.json + Codex hooks.json + Cursor hooks + Gemini CLI hooks + a git pre-commit hook, all from one source file — closest is agent-guard's explicit "agent hooks + git hooks + CI" three-layer stack, and hookflows' single script intercepted at multiple layers.

---

## Q4. Anthropic's AI-Native SDLC playbook — where it places enforcement

Source: https://claude.com/blog/the-ai-native-sdlc-playbook (fetched 2026-09-02)

- **Hooks = deterministic gates, admin-locked**: `.claude/settings.json` in version control or **managed settings** admins own; example config: `"allowManagedPermissionRulesOnly": true`, `"disableBypassPermissionsMode": "disable"`, `"allowManagedHooksOnly": true`, `"sandbox": {"failIfUnavailable": true}` — i.e., "gates refuse to start without enforcement" rather than fail open.
- **Production gate is a hook, human-approval-gated**: `.claude/hooks/production-gate.sh` — "Production deploys need a release authorization" until `$RELEASE_APPROVAL` is set. Quote: **"The agent may act up to the production gate and cannot pass it."** "A hook can also ask, pausing the action until a specific person approves."
- **Branch protection = separation-of-duties barrier**: "the agent that wrote the code has no way to approve it" — branch protection forces human code-owner approval before merge; this is explicitly NOT delegated to a hook.
- **CI = the deterministic checkpoint for what doesn't need judgment**: tests/linting are "deterministic" and belong in CI, distinct from hooks (which gate the *agent's actions in real time*) and branch protection (which gates *human approval of the result*).

So Anthropic's own model is a **three-layer split**, not "git hooks as the single enforcement surface": (1) host hooks gate what the agent can do live, admin-locked so the agent can't loosen its own leash; (2) branch protection gates merge via a human who isn't the author; (3) CI gates the deterministic checks. This maps directly onto your "non-bypassable backstop somewhere" requirement — Anthropic's answer is **branch protection + admin-managed hook settings**, not a git hook alone (which any agent with shell access could edit or `--no-verify` around).

---

## Q5. Documented downsides of git-hooks-as-the-agent-gate, and mitigations

1. **`--no-verify` makes hooks advisory, not enforced.**
   - anthropics/claude-code issue #40117: "Agent bypasses git pre-commit hooks using --no-verify, stash, and quiet flags despite explicit deny rules" — one agent used **6 consecutive commits with different bypass strategies** despite CLAUDE.md explicitly prohibiting it.
   - Kastalien-Research/thoughtbox issue #220: "Hook bypass: --no-verify makes all git hooks advisory, not enforced."
   - **Mitigation found**: a PreToolUse *agent-level* hook (Claude Code/Codex layer, not git layer) that parses the full shell command at runtime and denies any invocation containing `--no-verify`, `core.hooksPath` overrides, or hook-manager disable env vars — tools: `block-no-verify` (github.com/tupe12334/block-no-verify), and a hand-rolled example cited in pydevtools.com/handbook/how-to/how-to-stop-ai-agents-from-bypassing-pre-commit-hooks/. This still requires the agent-level hook to be active — it doesn't help against a human or CI runner invoking git directly with `--no-verify`.

2. **Git worktrees break naive hook installers — three separate live bugs, same root cause.**
   - anthropics/claude-code #66993: **"Worktree creation rewrites shared core.hooksPath, silently disabling repo-managed git hooks for the whole clone."**
   - anthropics/claude-code #72714: **"/worktree can silently write core.hooksPath into the MAIN repo's shared .git/config, disabling global hooks."**
   - anthropics/claude-code #88747: **"Worktree creation writes an ABSOLUTE core.hooksPath into config.worktree, so worktrees run the MAIN checkout's hooks."**
   - pre-commit/pre-commit #808: "Hooks not installed in the right hooks directory for worktrees."
   - gastownhall/beads #1127: "Git hooks don't work in worktrees."
   - **Root cause**: hooks live in the *common* git dir (`.git/hooks` in the main checkout, or wherever `--git-common-dir` resolves to), not per-worktree; and `core.hooksPath`, when set from inside a linked worktree, writes to the **shared** `.git/config`, which can silently disable or redirect hooks for every other worktree including the main one.
   - **Mitigation found**: resolve the hooks directory via `git rev-parse --git-common-dir` (or `--git-path hooks`) rather than hard-coding `.git/hooks`; j178/prek issue #1672 ("Make git hook installation worktree-safe and transactional") is an open effort specifically to fix this class of bug properly (transactional install, worktree-aware).

3. **Hooks/MCP init can run outside the sandbox boundary — a security-relevant asymmetry, not just a UX one.**
   - levelup.gitconnected.com / "A Technical Guide to AI Agent Sandboxing": "Hooks and MCP initialization functions often run outside of a sandbox environment, offering an opportunity to escape sandbox controls." Also: "if the agent edits files that humans later execute — Git hooks, CI configs, IDE task configs, Makefile, package.json scripts, build files — the damage can cross the boundary when a human or pipeline runs those files later."
   - **Mitigation found**: CI-side, ensure the agent's push token/credentials **lack workflow-modification scope**, or a repository ruleset blocks changes to `.github/workflows/` — i.e., don't let the same actor that's gated also edit the gate. (haulos.com/blog/sandboxing-github-actions/)

4. **Fresh clones / new machines have no hooks until something installs them** (ties to Q2) — the pre-commit framework's own docs concede the standard flow requires `pre-commit install`; nothing in git itself pushes hook installation onto a clone unless `init.templateDir` was pre-configured on that machine before cloning, which a repo cannot force.

5. **Anthropic's own mitigation for all of the above, taken together**: don't rely on git hooks alone — admin-managed, non-overridable **host-level** hook settings (`allowManagedHooksOnly`, `disableBypassPermissionsMode: disable`) so the agent literally cannot loosen its own hook config, PLUS branch protection (a separate human, separate system) as the actual non-bypassable backstop, PLUS CI for the deterministic checks. Git hooks alone were not treated as sufficient anywhere in the sources found.

---

## Sources (deduplicated)

- github.com/obra/superpowers/ ; deepwiki.com/obra/superpowers/5.1-claude-code:-skill-tool-and-hooks
- github.com/bmad-code-org/BMAD-METHOD/discussions/878 ; /issues/1473
- dev.to/htekdev/github-spec-kit-turn-english-into-production-ready-specs-27o2 ; github.com/github/spec-kit
- github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md ; /docs/team-workflow.md
- kiro.dev/blog/introducing-kiro/
- cursor.com/docs/hooks ; ranthebuilder.cloud/blog/agentic-coding-hooks-deterministic-ai-guardrails/
- github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md ; geminicli.com/docs/hooks/
- learn.chatgpt.com/docs/hooks (official Codex hooks doc, redirect target of developers.openai.com/codex/hooks)
- codex.danielvaughan.com/2026/04/15/codex-cli-hooks-complete-guide-events-policy-patterns/ (third-party, appears stale re: disabled-by-default/Windows claims — flagged, not relied on)
- claude.com/blog/the-ai-native-sdlc-playbook
- typicode.github.io/husky/get-started.html ; sonspring.com/journal/husky-v5-and-npm-prepare
- lefthook.dev/installation/node/ ; github.com/evilmartians/lefthook/issues/1248
- pre-commit.com ; gist.github.com/CITguy/e8cecbbb7408a93f28c1cbaccaec6765
- githooks.com ; viget.com/articles/two-ways-to-share-git-hooks-with-your-team ; github.com/rycus86/githooks
- github.com/LuD1161/agentjail ; github.com/JeongJaeSoon/agent-guard ; github.com/logi-cmd/agent-guardrails ; github.com/tupe12334/block-no-verify ; htek.dev/articles/hookflows-governed-git-for-ai-agents
- github.com/anthropics/claude-code/issues/40117 ; /66993 ; /72714 ; /88747
- github.com/Kastalien-Research/thoughtbox/issues/220
- github.com/pre-commit/pre-commit/issues/808 ; github.com/gastownhall/beads/issues/1127 ; github.com/j178/prek/issues/1672
- pydevtools.com/handbook/how-to/how-to-stop-ai-agents-from-bypassing-pre-commit-hooks/
- levelup.gitconnected.com/a-technical-guide-to-ai-agent-sandboxing-dfdf9571dd2d ; haulos.com/blog/sandboxing-github-actions/
