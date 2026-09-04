---
name: a-backticked-token-with-a-slash-is-a-repo-path-to-the-citation-check
description: CI's doc-citation check (`loom-code/scripts/check_doc_citations.py`, run over `docs/loom/*.md`, every intent, and the loom skill/agent/reference trees) treats ANY backticked token containing a `/` as an explicit repo-path citation and fails when no such file exists — so a machine-local path like `~/.codex/config.toml` or `/usr/bin/env` written in backticks inside an intent turns the whole PR red; write non-repo paths in prose, keep backticks for paths that resolve in the tree
type: gotcha
origin: branch positioning-paragraph-cap-redesign (2026-09-04) — PR #789's first CI run failed on a parked intent (codex-hook-trust) that cited `~/.codex/config.toml` in backticks; the fix was two words of prose and cost an extra review round because it landed after the branch-end pass
---

`check_doc_citations.py` extracts citations with a regex over backticks
(`` `([^`\s:]+)(?::(\d+)(?:-(\d+))?)?` ``) and then asks `_looks_like_citation`
whether the token is path-shaped — a `/` is enough. It resolves the path
against `git ls-files` at the reviewed sha; a miss is a finding, and the
CI step runs it over every intent file, not only the change's own.

**Why:** the check exists so that `file:line` anchors in plans and reviews
cannot rot; it has no way to tell "a path on the user's machine" from "a
path that used to exist in the repo", and it should not guess.

**How to apply:** in intents, plans and memory entries, write machine-local
paths without backticks ("使用者家目錄下 Codex 的 config.toml", "the
user's shell profile"); reserve backticks for repo files, commands, and
identifiers without a slash. Run the same command CI runs before pushing
when an intent mentions a path outside the tree:

```
git ls-files '*.md' | grep -E '^(docs/loom/[^/]+\.md|docs/loom/intent/|loom-(code|design|workflow)/(skills|agents|references|contract)/)' | xargs python3 loom-code/scripts/check_doc_citations.py
```
