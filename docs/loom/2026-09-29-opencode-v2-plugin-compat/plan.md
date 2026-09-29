# OpenCode v2 plugin compatibility — plan
intent: 2026-09-29-opencode-v2-plugin-compat@5d3a65208
charter: 1.1

## Current State Evidence
- Forward: `.claude-plugin/marketplace.json` lists 21 plugins; each dir has `.claude-plugin/plugin.json` + flat `skills/*/SKILL.md` (168 files, all with name+description frontmatter) — no plugin dir has package.json/src/.opencode today.
- Reverse: superpowers (obra/superpowers `.opencode/plugins/superpowers.js`) proves the loader pattern: read `skills/*/SKILL.md`, parse frontmatter, register via `ctx.skill.transform()` — verified against our flat layout.
- Error: OpenCode requires `description` for discovery; our 168/168 frontmatter coverage satisfies it — briefing-toolkit uses a 5-line YAML literal description a line-based parser must handle.
- Data: `CLAUDE_SKILL_DIR`/`CLAUDE_PLUGIN_ROOT` appear in SKILL.md bodies of 16 skills across 5 plugins (investing-toolkit, tsundoku, think-orbit, obsidian, salesforce-toolkit) — substitution behavior in OpenCode is the acceptance-4 probe.
- Boundary: CI gates existing manifests via `skill-structure.yml` (structure/marketplace-description-sync/plugin-version-bump) and `.claude/hooks/check-codex-manifest-drift.sh`; additive package.json files must not trip these gates.

## Task DAG

**W1-01** Spike probe + pilot loader packages  after: —  acceptance: 1, 2
- Files: investing-toolkit/package.json, obsidian/package.json, ascii-graph-toolkit/package.json, investing-toolkit/.opencode-plugin/index.js, obsidian/.opencode-plugin/index.js, ascii-graph-toolkit/.opencode-plugin/index.js
- Test: A1 positive: `opencode plugin add github:kouko/monkey-skills#main::path:investing-toolkit` succeeds from a local git clone; negative: malformed package.json → install fails, plugin absent from list. A2 positive: pilot skills advertised with name+description; negative: skill without description not advertised.
- Risk: spike resolves 4 runtime unknowns (registration shape, frontmatter tolerance incl. 5-line literal, token substitution, git-subdir package resolution) before dependent tasks. agent-decided: scratch probes in /tmp, committed artifacts only.

**W1-02** Loader replication to remaining 18 plugins  after: W1-01  acceptance: 3
- Files: <non-pilot dirs>/package.json, <non-pilot dirs>/.opencode-plugin/index.js
- Test: A3 positive: each of the 18 installs and loads one representative skill; negative: repo-wide scan finds no plugin dir missing package.json.
- Risk: Mechanical replication of proven W1-01 loader; agent-decided: scripted generation + per-plugin spot check, not per-plugin hand review.

**W2-01** Placeholder compatibility probe + documented fallback  after: W1-01  acceptance: 4
- Files: docs/opencode.md (new), ascii-graph-toolkit probe notes
- Test: A4 positive: one placeholder-carrying skill (ascii-graph-toolkit or investing-toolkit) produces expected artifact in clean OpenCode session; negative: unresolved token visible in output = probe failed → fallback documented.
- Risk: If OpenCode does not substitute tokens, agent-decided fallback: document per-skill in docs/opencode.md rather than editing skill bodies (constraint: additive only).

**W2-02** Install docs  after: W1-02, W2-01  acceptance: 1
- Files: README.md, README.ja.md, README.zh-TW.md, .opencode/INSTALL.md
- Test: A1 positive: README OpenCode section lists the `opencode plugin add` command for pilots; boundary: docs match the final loader naming (no phantom paths).
- Risk: agent-decided: follow existing README convention (## Install → per-host ### headings); ja/zh-TW siblings updated in same commit.

**W3-01** Full-fleet verification + package suite  after: W1-02, W2-01, W2-02  acceptance: 5
- Files: none (verification only); evidence in acceptance-test-report
- Test: A5 positive: diff vs main shows only new files and the package suite passes; negative: any modified existing file or failing suite fails the task.
- Risk: agent-decided: verification runs against a local git clone install (not npm publish); CI gate conflicts checked via existing skill-structure workflow locally.

## Simplicity check
- Single shared loader file imported by 21 package.json entries — declined: cross-plugin relative import (`../`) breaks under git-subdir install (each subdir is a standalone install root); per-plugin self-contained loader taken instead.
- Reuse superpowers `.opencode/` central dir layout — declined: superpowers is a single plugin; our monorepo installs per-subdir, so the loader must live inside each plugin dir.
- Skip W0-01 spike and design from docs alone — declined: 4 runtime unknowns were identified; a 30-minute local probe is cheaper than a wrong committed design.

## Questions asked
1 — what — OpenCode 用戶想用 monkey-skills 時，無法用 `opencode plugin add` 從你的 repo 安裝；他們要麼放棄、要麼手動複製檔案。
1 — what — 完成後你能做什麼（舉例：plugin add 後 skills 出現在清單並可載入、21 個 plugin 都可用、佔位符 skill 有文件說明）— 使用者回答「你的舉例好像就差不多了」
1 — what — 什麼不能動？什麼明確不做？（舉例：現有 4 host 安裝不壞、不做 marketplace、不重寫 skill 內容、不支援 v1）— 同上，使用者採納舉例
1 — consequence — 確認即授權自動 push + Ready PR（merge 另決）— 使用者回答「對」
4 — what — superpowers 的 OpenCode 相容做法可以參考嗎？— 使用者提問，調查後納入 Current State Evidence（loader 模式被證實）

## Risks
1. OpenCode v2 git-spec install may resolve the package root differently than a local-path install; W0-01 spike must include a git-clone-based install test before W1-01 commits anything.
2. `plugin-version-bump` CI gate may require version bumps for new files; if it fires, agent-decided: bump only plugins whose packaging changes, with reason in PR body.
3. Token substitution in OpenCode is undocumented; if the W2-01 probe fails, the documented-fallback path keeps acceptance 4 satisfiable without touching skill bodies.
4. OpenCode versions move fast (v1 vs v2 plugin APIs differ); loader targets v2 only per intent Constraints, and docs must state the minimum tested version (v2.0.18).
