# Brief: make a stale adjudication render impossible to mistake for a good one

Date: 2026-08-18
Stage: brainstorming output → writing-plans input
Design-side on-ramp: no criteria row fired (repair of a shipped loom mechanism;
no UI surface, no new multi-state behavior) — no detour offered.
Axis 0 queue check: `docs/loom/DIRECTION.md` `## Now` is empty; no OPEN backlog
entry covers this defect (nearest neighbours —
`2026-08-12-protocol-files-carry-no-size-ceiling` touches the same protocol
file but is a size concern, not a correctness one). This arc is unqueued and
user-initiated.
Recall: `docs/loom/memory/a-mechanical-check-can-go-green-by-skipping.md` and
`a-mutation-test-must-run-the-production-assertion.md` both bind here — the
guard this brief adds is exactly the shape that historically went green by
not running.

## Problem

`adjudication_render.py` converts a unit's `rendition` markdown to HTML. When
the copy of the script that actually executes predates the markdown-it
conversion (`adjudication_render.py:40,89-133`), it writes a well-formed HTML
page in which the markdown was never converted — literal `**bold**`, literal
`|` table rows, literal ` ```mermaid ` fences. The run exits 0, prints no
warning, and writes a file of plausible size. **The failure is byte-for-byte
indistinguishable from success at the command line.**

This is not hypothetical and not one incident. Five renditions delivered to the
adjudicator between 2026-08-14 and 2026-08-18 were unconverted, verified by
opening each file:

| Date | Project | Copy that ran | Unconverted markers in the delivered page |
|---|---|---|---|
| 08-14 | monkey-skills | repo-local copy, pre-fix | 186 raw `**` |
| 08-14 | kumiko-zaiku-app-icons | plugin cache `0.80.0/` | 244 raw `**`, 2 raw mermaid fences |
| 08-17 | loom-doc-container | working tree mid-recovery | 255 raw `**` |
| 08-18 05:54 | strage-dag-skill | that worktree's own checkout | 353 raw `**`, 6 raw mermaid fences |
| 08-18 06:09+ | monkey-skills | plugin cache `0.84.0/` (hardcoded path) | 45 raw `**` |

Three distinct staleness sources appear: the plugin cache retains **every**
released version as its own directory tree (0.17.0 → 0.86.0 all present on
disk today), un-rebased git worktrees carry their own older checkout
(`strage-dag-skill/loom-code/scripts/adjudication_render.py` has no
`markdown_it` import as of this writing, and its
`loom-code/.claude-plugin/plugin.json` reads `0.83.0`), and a working tree can
sit mid-fix. One path convention does reach all three — "the copy shipped
beside the protocol being read" — because each of the three sources is a copy
the executor chose over that one; what no path convention can reach is the
fourth case, where the shipped copy is itself old.

The job to be done: **an adjudicator opening the page, and an orchestrator
about to hand it over, must be able to tell at a glance which version produced
it** — so a stale render announces itself instead of being read as the
artifact's actual content. Note the corollary that reframes the obvious fix: a
self-check written inside the renderer cannot catch its own staleness, because
the stale copy does not contain the self-check either. Only an artifact the
current code emits — and a stale copy therefore cannot emit — carries the
signal.

Two independent review agents in this investigation judged a stale render
"correct" from its exit code alone; opening the file refuted both. The same
mistake is available to every future agent and to the user.

## Users

- **kouko as adjudicator** — the sole reader of the document view. Reads the
  page in Traditional Chinese to sign off a brief or plan; has no cue today
  that the page in front of them came from a five-versions-old script. This
  user's whole relationship to the artifact is visual, so a signal they can
  see beats any signal only an agent can query.
- **The orchestrator that renders and delivers** — runs the three-script
  pipeline from `protocols/adjudication-view.md:190-205`, then hands the file
  over (`SendUserFile`). Today it has no postcondition to check and, per the
  incidents above, no reason to suspect one is needed.
- **Reviewers / future agents auditing past renders** — need the produced file
  to be self-describing, because the transcript's record of the run (exit 0)
  is affirmatively misleading.

Job story: *When I open a rendered adjudication view, I want to see which
renderer version produced it, so I can tell a real rendition from a stale
one before I read it as the artifact's content.*

## Smallest End State

Two changes to one script, plus two rules in the invocation contract:

1. `adjudication_render.py` stamps every HTML page it emits with the version of
   the plugin copy that ran — machine-readable (`<meta name="generator">`) and
   visible to the reader (a small page footer). The version is read from the
   `.claude-plugin/plugin.json` that ships beside the running copy, so the
   stamp travels with the copy rather than with the invocation.
2. `adjudication_render.py` fails loud (non-zero exit, no output file written)
   when a rendered `rendition` still contains unconverted markdown markers.
3. `protocols/adjudication-view.md` gains one sentence in the invocation
   contract: before delivering the page, confirm it carries the stamp and the
   stamp's version matches the pipeline being run; a page with no stamp came
   from a pre-stamp copy and must not be delivered.
4. The same invocation contract pins WHICH copy runs, as a self-locating rule:
   the script to execute is the one shipped beside the protocol file the
   executor is reading — three levels up from that file's own absolute path,
   `../../../scripts/adjudication_render.py`. Carve out the case where the
   session is developing these scripts themselves (then the working tree's
   copy is the point).

Deliberately NOT in the smallest end state: any cleanup of the plugin cache,
any second script, any move of the scripts out of the plugin root.

## Current State Evidence

- **Forward (entry → output)**: `main()` at `adjudication_render.py:546-579`
  parses args, resolves the language profile (`:566`, the one existing
  fail-loud), loads units JSON (`:569`), dispatches to `render_doc` (`:575`) →
  `_build_unit_html` per unit (`:435-451`) → `_render_markdown` (`:89-133`) →
  `_render_page` (`:343-372`), then writes the file (`:578`) and
  `return 0` (`:579`) unconditionally.
- **Reverse (SSOT ownership)**: `scripts/distribute.py` contains no
  `adjudication` reference — this script is NOT part of the
  domain-teams functional-copy sync, so `loom-code/scripts/adjudication_render.py`
  is its own single source. The multiplicity is purely deployment-side
  (per-version plugin cache dirs + worktrees), which is why the fix must be
  detectable at the artifact rather than enforced at the source.
- **Error (how failure surfaces today)**: exactly two failure paths exist —
  unknown `--lang` tag (`:566`, deliberate) and JSON parse failure (`:569`).
  There is no postcondition on the rendered output. Contrast the sibling
  script's exit-code convention at `adjudication_lint.py:283`: `WARNING `-prefixed
  lines exit 0, everything else exits 1 — a precedent for a
  two-tier severity signal that this brief does NOT need (a stale render is
  never a warning).
- **Data (what carries markdown)**: per `protocols/adjudication-view.md:161-176`,
  only `rendition` is markdown-bearing and it alone is injected unescaped
  (`:449`). `source_text` is `html.escape`'d into the `原文` `<details><pre>`
  block (`:439`) **by design** — raw `**` inside that collapsible is correct
  output, not a defect. Any leftover-markdown check MUST therefore scope
  itself to the rendition region, or it will condemn every correct page.
- **Boundary (where a version lives)**: `loom-code/.claude-plugin/plugin.json:3`
  carries `"version"`, and one such file ships inside every deployed copy —
  verified across three: the 0.86.0 plugin cache tree, this repo (0.86.0), and
  the stale `strage-dag-skill` worktree (0.83.0). This is what makes the stamp
  discriminating: the stale copy stamps its own older number, and a pre-stamp
  copy stamps nothing at all.

Evidence paths:
- `loom-code/scripts/adjudication_render.py`
- `loom-code/scripts/adjudication_lint.py`
- `loom-code/scripts/distribute.py`
- `loom-code/skills/using-loom-code/protocols/adjudication-view.md`
- `loom-code/.claude-plugin/plugin.json`
- `/Users/kouko/.supacode/repos/monkey-skills/strage-dag-skill/loom-code/` (stale-worktree control case)

## Alternatives Considered

Researched via WebSearch, EN + JA, 2026-08-18.

**My take: pin the invocation, stamp the page, and fail loud — in that order
of load-bearing-ness.** Path pinning PREVENTS 4 of the 5 incidents (see the
revised row below); the stamp DETECTS the residual case pinning cannot reach
(the installed plugin is itself old); the postcondition catches a future
conversion regression rather than staleness. **Conditional reversal**: if the
postcondition's rendition-scoped regex proves to false-positive on legitimate
content, drop leg 2 and keep the other two — a live probe on this brief's own
view already produced one such false positive (` ``**bold**`` ` inside a code
span, quoted as an example), so the regex MUST exclude `<code>` spans.

**Correction to an earlier reading in this same brief's drafting**: path
pinning was first rejected on the grounds that it "cannot help a stale
worktree". That is backwards — the worktree incidents happened *because* the
repo-relative copy ran; pinning to the shipped-beside-the-protocol copy is
exactly what stops them. What pinning cannot reach is only the case where the
installed plugin itself predates the fix.

| Approach | Who ships it | Source (lang) | Catches THIS bug? | Cost |
|---|---|---|---|---|
| **Version/commit stamp in the artifact** (chosen) | Go ecosystem (`-ldflags -X main.version=$(git rev-parse HEAD)`); Unreal Engine BuildID, which exists precisely to catch stale binaries | [Zenn 埋め込み](https://zenn.dev/teasy/articles/embed-git-hash-to-binary) (JA), [Unreal BuildID](https://dev.epicgames.com/documentation/en-us/unreal-engine/how-to-version-binaries-in-unreal-engine) (EN) | **Yes** — the only one that does | ~10 lines + template slot |
| **Fail-loud postcondition on output** (chosen, secondary) | Defensive-programming doctrine — Sutter GotW #97 on postconditions; "fail fast and loud" | [herbsutter.com GotW #97](https://herbsutter.com/2021/01/01/gotw-97-contracts-part-1-assertions-and-postconditions/) (EN) | No (stale copy lacks the check) — catches future conversion regressions | ~10 lines, needs a rendition-scoped regex |
| **Canonical-path enforcement** (chosen, primary) | mise / asdf ship `not_found_system_fallback=false` explicitly so a shim fails loudly instead of silently resolving elsewhere | [mise shims](https://mise.jdx.dev/dev-tools/shims.html) (EN), [classmethod](https://dev.classmethod.jp/articles/mise-tool-version-management-20260418/) (JA) | **4 of 5** — the hardcoded-cache-dir, stale-worktree, mid-fix-tree and old-cache-version incidents all resolve to the shipped-beside-the-protocol copy; only "the installed plugin is itself old" survives | One paragraph in the protocol's invocation contract |
| **Golden/approval test** | ApprovalTests.Python; TensorFlow Federated `golden_tests` | [ApprovalTests.Python](https://github.com/approvals/ApprovalTests.Python) (EN) | No — dev-time only; the stale copy on disk never runs CI | CI-side; the existing 33 render tests already cover this ground |

**EN/JA disagreement, recorded rather than smoothed**: JA general-practice
writing on silent failures leans toward degrade-and-continue (wrap, log,
「プログラム自体は止まらずに次の処理に進む」 —
[note.com](https://note.com/masa_sys/n/nf51b3c046648)), while the EN sources
argue fail-loud on a violated postcondition. For this artifact the EN posture
wins on its own terms: degrade-and-continue is precisely the behavior that
produced all five incidents.

## Decision

Add a deployment-version stamp to every HTML page `adjudication_render.py`
emits — `<meta name="generator" content="loom-code-adjudication-render/<version>">`
plus a visible page footer carrying the same version — read from the
`.claude-plugin/plugin.json` that ships beside the running script, falling back
to a literal `unknown` when that file is unreadable (a copy that cannot name
itself is as suspect as an old one, and must still be visibly marked). Add a
postcondition over the rendered rendition region only: if unconverted markdown
markers survive there, exit non-zero and write no output file. Add one sentence
to the invocation contract in `protocols/adjudication-view.md` making the
pre-delivery stamp check the executor's duty.

Pin the invocation in the same contract, as a **self-locating** rule — "the
script shipped beside the protocol file you are reading" — rather than via
`${CLAUDE_PLUGIN_ROOT}`. Two findings force that wording. Anthropic's docs
state the substitution happens in exactly two places, "the skill's markdown
content, and Bash rules in the `allowed-tools` frontmatter"
([skills docs](https://code.claude.com/docs/en/skills.md)); a protocol file
opened with the Read tool is neither, and the on-disk file keeps the literal
token (verified: `brainstorming/SKILL.md:79` carries `${CLAUDE_PLUGIN_ROOT}`
on disk while this session's loaded body carried the resolved absolute path).
A literal token reaching Bash expands to empty — a new trap. The self-locating
rule also carries to Codex, which has no such placeholder at all.

**Correction, 2026-08-18, after this brief's first draft**: an earlier version
of this paragraph claimed Codex "installs by git clone (no per-version cache
tier, so only the stale-clone class of this bug exists there)". That is false,
and the repo's own `docs/loom/codex-verification.md:50` already said so — the
`codex plugin add` marketplace path installs into
`~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/`, a per-version tree
structurally identical to staleness source #1 above. The manual `git clone`
shape in `.codex/INSTALL.md:9-29` is a *second*, different install path, and
the two were conflated. Confirmed live on this machine: the Codex cache holds
`monkey-skills/loom-code/0.83.0` — a pre-markdown-it copy — so a Codex-rendered
adjudication view today reproduces the original bug. At least two of the three
staleness classes therefore exist under Codex. What remains un-probed is
whether an executor under Codex resolves the self-locating rule correctly, NOT
whether Codex can go stale; the backlog entry carries that scope.

We will NOT touch the plugin cache and will NOT add a second script: both trade
the problem for device hygiene the repo cannot enforce. We will NOT move these
scripts into a skill directory: the official plugin reference sanctions a
plugin-root `scripts/` for "shared utility scripts", the skills docs name
`${CLAUDE_PLUGIN_ROOT}` as the way to reach "resources shared between the
plugin's skills", and this renderer is shared by four skills — while a move
would break the CI paths, 117 sibling test files, and four agent definitions
that cite `loom-code/scripts/`.

Both legs need mutation coverage that runs the **production** call site, per
`docs/loom/memory/a-mutation-test-must-run-the-production-assertion.md` — a test
that only proves the helper works would leave exactly the hole this brief
exists to close. The postcondition additionally needs a probe proving it cannot
go green by skipping (the `原文` block must stay excluded WITHOUT the check
silently matching nothing), per
`docs/loom/memory/a-mechanical-check-can-go-green-by-skipping.md`.

## Out of Scope

- Deleting or pruning old versions from `~/.claude/plugins/cache/` — device
  hygiene, not repo behavior, and destructive.
- Rebasing the stale `strage-dag-skill` worktree — that branch's own business.
- Any change to `adjudication_split.py` or `adjudication_lint.py`.
- Verdict-mode markdown output (no HTML page, no place for a stamp); verdict
  mode's `--html` page is in scope only because it shares `_render_page`.
- Retro-flagging the five already-delivered stale pages.
- A repo-wide convention for stamping other generated artifacts.

## What Becomes Obsolete

Nothing is deleted by this change — flagged honestly, since a purely additive
change is a YAGNI smell by Axis 5's own rule. What it retires is an unstated
assumption rather than code: the invocation contract at
`protocols/adjudication-view.md:190-205` currently treats a zero exit as
sufficient evidence that the pipeline ran, and the added sentence removes that
reading. The ~20 lines of added production code are justified by five
confirmed user-visible failures, not by anticipation.

## Open Questions

0. Should a live Codex probe of the self-locating rule gate this arc?
   Recommended no — the rule's portability is structural (it uses no
   harness-specific primitive), so the probe is worth a backlog entry rather
   than a blocking task. Recorded here because "portable by construction" is
   an argument, not a measurement.
1. Should the visible footer name only the version, or also the render
   timestamp? (Timestamp helps date a page found later; adds nondeterminism to
   the golden-ish render tests. Leaning version-only.)
2. Does the postcondition treat a leftover ` ```mermaid ` fence and a leftover
   `**` as one severity? (Leaning yes — both mean the same thing.)

## Diagrams

Declared N/A. The pipeline is linear (split → translate → lint → render) and
the branching that matters — which copy on disk executed — is enumeration, not
flow; the incident table above carries it without a diagram.
