# Plan: loom direction layer — DIRECTION.md convention + commitment loop

Source brief: docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md
Goal: loom gains a portable direction layer — a per-repo DIRECTION.md (generated Now / human-only Next+Later, no dates) with its write loop (betting at close when the queue is empty) and read loop (Axis 0) wired conditionally into the stations, five frozen ROADMAPs tombstoned, loom-code shipping 0.69.0 — monkey-skills seeded as first consumer.
Stage: finishing
Total tasks: 10
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-07, round 3)

Steps:
  1. 機制核心：generator/validator＋DIRECTION.md 首例（五座墓碑平行）
  2. 三個教學面接線（charter／Axis 0／下注時刻）
  3. 版本 bump 0.69.0＋CHANGELOG

## Task 1 — --direction-write/--direction-check pair + DIRECTION.md first instance
- Description: Extend scripts/backlog_index.py with the flag pair `--direction-write <path>` / `--direction-check <path>` (mirroring the existing --write/--check semantics; arc-3 precedent: extend the owning script, no second script): `--direction-write` regenerates the `## Now` section of the given DIRECTION.md from COMMITTED-NEXT entry files (one line per entry: name + description, file-date order; empty queue renders exactly `_(queue empty — bet at the next close-out)_`), refusing loudly when the file lacks a `## Now` heading or an entry has malformed frontmatter; `--direction-check` re-runs the generator and diffs (self-confirmation — name it that in --help, per the arc-3 "--check is the generator confirming itself" lesson); the FLAGLESS validate mode gains independent DIRECTION.md checks ONLY when the file exists (absent file = silently valid — the mechanism is opt-in per repo): `## Now` content matches entries, `## Next`/`## Later` headings present, and NO date-like token (regex `20\d\d[-/年.]` plus `Q[1-4]`) anywhere in the body — the charter's no-dates rule as a checked invariant. Then create docs/loom/DIRECTION.md (monkey-skills' first instance): a ≤18-line charter header stating the update rules — `## Now` is generated (never hand-edit) and is a PARALLEL ACTIVE SET, not a serial queue (one entry typically maps to one worktree/lane; the ≤5 cap is parallel-steering capacity); `## Next`/`## Later` are human-written themes only, and a Next line MAY point at a roadmap entry in docs/loom/backlog/ by filename; no dates anywhere; betting promotes backlog entries to COMMITTED-NEXT, user-only; on `## Now` merge conflict, take either side wholesale and regenerate via `--direction-write`, never hand-merge. Then the three sections with the kickoff-decided seed content (verbatim from ## Notes `Kickoff decision:` lines): `## Now` = the empty-queue line (queue is empty today); `## Next` = the two Next themes; `## Later` = the three Later themes. New tests in scripts/test_backlog_index.py: generation from a fixture store with COMMITTED-NEXT entries; empty-queue rendering; refusal on missing `## Now`; date-token detection (mutation-pinned: a fixture with `2026-09` in ## Later must fail validate); absent-DIRECTION.md = validate silent-pass.
- Module: backlog store tooling (script + its test file + the store-adjacent DIRECTION.md instance — one ownership unit)
- Files touched: scripts/backlog_index.py, scripts/test_backlog_index.py, docs/loom/DIRECTION.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 1-2, 8 + §Addendum 3, 5, 7)
  - scripts/check_loom_memory_integrity.py (the --write/--check/flagless trio shape to mirror)
- Acceptance:
  - RED: `python3 scripts/backlog_index.py --direction-write docs/loom/DIRECTION.md` exits nonzero with an unrecognized-argument error (verified: exits 2 today).
  - GREEN: both new flags work against the live store (empty-queue line rendered); flagless `python3 scripts/backlog_index.py` exit 0 with DIRECTION.md present; all new tests green RED-first per file convention; full suite `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` green.
- External surfaces: none — stdlib + pytest.
- Dependencies: none
- Independent: true
- Brief item covered: "`docs/loom/DIRECTION.md` — one file, three sections + charter header" (item 1) + "Generation + validation: backlog_index.py grows a --direction write/check pair" (item 2) + "Portability requirements … absent file = opt-in" (item 8) + "Initial content ride-along (first-consumer dogfood): seed monkey-skills' DIRECTION.md" (item 9, themes per §Addendum 7)
- Status: done(e1dfbd3b)
- Gloss: 生成器＋驗證器＋第一份 DIRECTION.md——Now 段機器寫、日期禁令變成可檢查的不變式、種子主題實內容出貨
- Review-hint: mutation probes must cover the date-ban regex and the empty-queue rendering.

## Task 2 — charter: Bet verb + roadmap-entry pattern + Now-mirror sentences
- Description: In docs/loom/backlog/README.md: (1) §Verbs gains the fourth flow after the existing three (Ready :119 / Close :125 / Kickoff :132): **Bet (promote)** — user-only; triggered by finishing's close-out when COMMITTED-NEXT is empty and the repo has docs/loom/DIRECTION.md, or manually anytime; candidates = the active roadmap entries' next arcs (same-lane first — when an arc of theme X just closed, theme X's next arc leads the list) then `--ready` output; promotion = the user edits the entry's `status:` to COMMITTED-NEXT (then `--write` + `--direction-write` regenerate); agents never promote. (2) A new short section **Roadmap entries** (a named PATTERN, not a new file type): an ordinary entry whose body is an ordered arc list with dependency notes, serving one DIRECTION theme; DIRECTION `## Next` lines may point at it by filename; the shipped-arc evidence lines accumulate in the body; precedent citation: 2026-08-07-execute-complexity-audit-keep-lanes. (3) The COMMITTED-NEXT tier description (:90-91) gains two sentences: the queue is mirrored into DIRECTION.md's generated `## Now` when that file exists; and the queue is a PARALLEL ACTIVE SET (one entry typically ↔ one worktree/lane; ≤5 = parallel-steering capacity), not a serial order. Before editing, grep BOTH scripts/test_backlog_index.py AND scripts/backlog_index.py's own asserts for pinned charter phrases that these edits would break; adjust windows only, never pinned phrases; report which (if any).
- Module: docs/loom/backlog/README.md (charter)
- Files touched: docs/loom/backlog/README.md, scripts/test_backlog_index.py
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 3, 5 + §Addendum 1-4)
- Acceptance:
  - RED: `grep -c "Bet (promote)" docs/loom/backlog/README.md` returns 0 today (longer anchor per the grep-pin store lesson; re-verify live before editing).
  - GREEN: §Verbs carries the Bet flow (user-only + empty-queue trigger + same-lane-first candidates + agents-never-promote all present); Roadmap-entries section present with the precedent citation; tier description carries mirror + parallel-set sentences; full suite green.
- External surfaces: none.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Charter sync: backlog README §Verbs gains the fourth flow (Bet/promote — user-only)" (item 5) + §Addendum 1 (roadmap-entry pattern) + §Addendum 3-4 (parallel set, same-lane ordering)
- Status: done(987039b8)
- Gloss: 章程補齊：第四動詞、roadmap 條目具名、Now＝並行集合入法
- Review-hint: none.

## Task 3 — brainstorming Axis 0 reads DIRECTION.md
- Description: In loom-code/skills/brainstorming/SKILL.md's Backlog ready check block (:73-80), add one conditional sentence: when the target repo also has docs/loom/DIRECTION.md, read it and surface `## Now` + `## Next` alongside the ready queue (no file → skip silently, same posture as the no-store case; the queue informs, never hijacks — the existing sentence already carries that rule for both). Add a pin for the new sentence in loom-code/scripts/test_brainstorming_backlog_read.py following that file's existing pin convention, RED-first against a probe copy missing the sentence.
- Module: loom-code/skills/brainstorming
- Files touched: loom-code/skills/brainstorming/SKILL.md, loom-code/scripts/test_brainstorming_backlog_read.py
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 4, 8)
- Acceptance:
  - RED: `grep -c "DIRECTION.md" loom-code/skills/brainstorming/SKILL.md` returns 0 today (verified).
  - GREEN: the sentence present inside the Backlog ready check block (not elsewhere); grep returns ≥1; new pin test green with RED probe shown; full suite green.
- External surfaces: none.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Kickoff read: brainstorming Axis 0's ready check extends one line" (item 4) + "every station edit fires CONDITIONALLY … silent skip" (item 8)
- Status: done(fc27fad8)
- Gloss: 開工必經站順讀方向檔——讀取迴路接上
- Review-hint: cold-reader must not misread the conditional as mandatory for repos without the file.

## Task 4 — finishing: betting duty in the Backlog-close cell
- Description: In loom-code/skills/finishing-a-development-branch/SKILL.md's Step-8 close-out table, extend the **Backlog-close check row's cells** (NOT a new row — the row-order pin test_finishing_backlog_close.py:77-78 stays untouched): the Action cell gains the betting duty — after flipping statuses and regenerating, when the repo also has docs/loom/DIRECTION.md: run `--direction-write` and stage the refreshed file; then if COMMITTED-NEXT is EMPTY, surface the betting prompt to the user — candidates listed same-lane first (the just-closed arc's theme, via its roadmap entry when one exists), then `--ready`; the USER promotes or declines; agents never auto-promote — promotion is never a silent default. The On-failure/N/A cell gains the absent-artifact fallback: no DIRECTION.md → skip the betting duty silently (opt-in mechanism); backlog_index.py absent → extend the existing script-absent wording to name the direction refresh too. Adjust test_finishing_backlog_close.py: new pins for the agents-never-auto-promote wording and the empty-queue trigger condition, window-scoped to the row, RED-first per file convention; existing pins untouched.
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_backlog_close.py
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 3, 8 + §Addendum 4)
- Acceptance:
  - RED: `grep -c "DIRECTION.md" loom-code/skills/finishing-a-development-branch/SKILL.md` returns 0 today (verified).
  - GREEN: betting duty present inside the Backlog-close row only; row-order pin (:77-78 semantics) still green untouched; new pins green with RED probes; full suite green.
- External surfaces: none.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Betting moment (the missing write loop)" + Decision "betting = event-driven at close (queue EMPTY → prompt)" (item 3) + "conditional + fallback wording like the backlog-close row" (item 8) + §Addendum 4 (same-lane first)
- Status: done(f9079211)
- Gloss: 收線站得到下注時刻——寫入迴路接上、同線優先，機制閉環
- Review-hint: the cell is already the table's longest neighbor class — reviewer checks the extended cell still reads unambiguously (arc-4b's known long-row debt is precedent, not a blocker).

## Task 5 — tombstone header: loom-code/ROADMAP.md
- Description: Insert, as line 2 of the file (immediately after the `# ...` title line), this exact line: `> **Historical design record — superseded.** Forward direction lives in `docs/loom/DIRECTION.md` (see its charter header); this file is kept as a design-era artifact and is no longer maintained.` No other line changes.
- Module: loom-code/ROADMAP.md
- Files touched: loom-code/ROADMAP.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 6)
- Acceptance:
  - RED: `grep -c "Historical design record — superseded" loom-code/ROADMAP.md` returns 0 today.
  - GREEN: exactly the literal line present at line 2; `git diff --stat` for this task's commit shows this file only, +1 line; full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Review-weight: mechanical
- Brief item covered: "Five ROADMAP.md tombstones: one header line each" (item 6)
- Status: done(7d01fd23)
- Gloss: 墓碑一：loom-code 的設計期 roadmap 蓋章
- Review-hint: none (mechanical self-check path).

## Task 6 — tombstone header: investing-toolkit/ROADMAP.md
- Description: Same literal line as Task 5, inserted as line 2 of investing-toolkit/ROADMAP.md (after the `# ...` title line). No other line changes.
- Module: investing-toolkit/ROADMAP.md
- Files touched: investing-toolkit/ROADMAP.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 6)
- Acceptance:
  - RED: `grep -c "Historical design record — superseded" investing-toolkit/ROADMAP.md` returns 0 today.
  - GREEN: the literal line at line 2; this file only, +1 line; full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Review-weight: mechanical
- Brief item covered: "Five ROADMAP.md tombstones: one header line each" (item 6)
- Status: done(917c11e4)
- Gloss: 墓碑二：investing-toolkit
- Review-hint: none (mechanical self-check path).

## Task 7 — tombstone header: legal-toolkit/ROADMAP.md
- Description: Same literal line as Task 5, inserted as line 2 of legal-toolkit/ROADMAP.md (after the `# ...` title line). No other line changes.
- Module: legal-toolkit/ROADMAP.md
- Files touched: legal-toolkit/ROADMAP.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 6)
- Acceptance:
  - RED: `grep -c "Historical design record — superseded" legal-toolkit/ROADMAP.md` returns 0 today.
  - GREEN: the literal line at line 2; this file only, +1 line; full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Review-weight: mechanical
- Brief item covered: "Five ROADMAP.md tombstones: one header line each" (item 6)
- Status: done(6be322cf)
- Gloss: 墓碑三：legal-toolkit
- Review-hint: none (mechanical self-check path).

## Task 8 — tombstone header: philosophers-toolkit/ROADMAP.md
- Description: Same literal line as Task 5, inserted as line 2 of philosophers-toolkit/ROADMAP.md (after the `# ...` title line). No other line changes.
- Module: philosophers-toolkit/ROADMAP.md
- Files touched: philosophers-toolkit/ROADMAP.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 6)
- Acceptance:
  - RED: `grep -c "Historical design record — superseded" philosophers-toolkit/ROADMAP.md` returns 0 today.
  - GREEN: the literal line at line 2; this file only, +1 line; full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Review-weight: mechanical
- Brief item covered: "Five ROADMAP.md tombstones: one header line each" (item 6)
- Status: done(53fec8d3)
- Gloss: 墓碑四：philosophers-toolkit
- Review-hint: none (mechanical self-check path).

## Task 9 — tombstone header: systems-thinking-toolkit/ROADMAP.md
- Description: Same literal line as Task 5, inserted as line 2 of systems-thinking-toolkit/ROADMAP.md (after the `# ...` title line). No other line changes.
- Module: systems-thinking-toolkit/ROADMAP.md
- Files touched: systems-thinking-toolkit/ROADMAP.md
- Context paths:
  - docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md (§Smallest End State 6)
- Acceptance:
  - RED: `grep -c "Historical design record — superseded" systems-thinking-toolkit/ROADMAP.md` returns 0 today.
  - GREEN: the literal line at line 2; this file only, +1 line; full suite green.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Review-weight: mechanical
- Brief item covered: "Five ROADMAP.md tombstones: one header line each" (item 6)
- Status: done(ee6a676f)
- Gloss: 墓碑五：systems-thinking-toolkit
- Review-hint: none (mechanical self-check path).

## Task 10 — loom-code 0.69.0 + CHANGELOG + version pin
- Description: Bump loom-code 0.68.0 → 0.69.0 via `python3 scripts/sync_codex_manifests.py loom-code` (--check exit 0); CHANGELOG 0.69.0 entry (house style: the DIRECTION.md convention — what the two station edits teach, conditional/portable posture, the betting loop with same-lane-first ordering, the roadmap-entry charter pattern, the tombstones; cite that Now is generated, a parallel active set, and dates are validator-banned); version-pin test rewrite in loom-code/scripts/test_docs_review_blocking_class.py `_0_68_0` → `_0_69_0` RED-first (flip pin, show missing heading, write entry, GREEN).
- Module: loom-code release unit (manifest pair + CHANGELOG + version pin, one version)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (0.68.0 entry shape)
- Acceptance:
  - RED: version-pin test fails on missing `## [0.69.0]` heading after the flip (shown pre-entry).
  - GREEN: both manifests 0.69.0 in sync; CHANGELOG entry present; zero 0.68.0/0_68_0 residue in the pin test; full suite green.
- External surfaces: marketplace versioning (bump-or-silent-no-op).
- Dependencies: Tasks 3, 4 complete first
- Independent: false
- Brief item covered: "Pin-test migration + loom-code minor bump (brainstorming + finishing SKILL.md change) + CHANGELOG" (item 7)
- Status: done(e77ca3c6)
- Gloss: 0.69.0——方向層機制隨 minor 版出貨
- Review-hint: none.

## Decision Log

- 2026-08-08 (wave 2, T3 fix round 1): spec-over-plan wording — plan
  Task 3's verbatim phrase "when the target repo also has
  docs/loom/DIRECTION.md" reads conjunctive with the block's
  backlog-store condition; spec §Smallest End State 8 deliberately
  contrasts Axis 0 (DIRECTION.md-present ONLY, single condition)
  against finishing (both artifacts). Artifact reworded to make the
  read independent of the store; quality-reviewer finding, spec is the
  portability SSOT. Below briefing threshold (reversible, spec-backed).
- 2026-08-08 (wave 2, T2 fix round 1): precedent-claim correction —
  charter's "evidence lines accumulating arc by arc across five PRs"
  was contradicted by the cited entry's own git history (single
  final-commit write; arcs 2-3 never touched the file). Claim shrunk
  to what the source supports; the accumulation practice stays as
  prescription, not as precedent. Plan/spec-inherited wording, fixed
  at artifact level. Tier sentences kept (plan requires both facts)
  but aligned verbatim to DIRECTION.md phrasing + SSOT pointer added.
- 2026-08-08 (wave 2, T4): PASS_WITH_NOTES 🟡 fixed immediately
  instead of carried as PR debt — promote-then-stale-Now gap (row
  never re-runs --direction-write after a user promote) is a real
  drift generator in the mechanism this arc ships; one-clause fix +
  two pins, cheap-hardening rule applied; re-verified by the
  whole-branch review arms.

- 2026-08-08 (review round 1, USER-RATIFIED): 🔴 filename-pointer vs
  date-ban self-contradiction — user chose validator exemption: date
  tokens inside a backlog-entry filename reference
  (`YYYY-MM-DD-slug.md`) are exempt from the DIRECTION.md no-dates
  scan (identifiers, not schedule promises); wording aligned across
  DIRECTION.md charter / backlog README / CHANGELOG. Alternatives
  (dateless-slug pointers; dropping the permission) declined.
- 2026-08-08 (review round 1, USER-RATIFIED): remediation scope — all
  four findings fixed (validator exemption, heading-predicate
  alignment in _direction_now_bounds, main() extraction below the
  100-line ceiling, Bet-trigger entry-flip precondition), then one
  delta-scoped round-2 re-review before PR-open.

## Notes

- Endpoint: user said 「開工吧」 after the brief checkpoint, with the
  arc's terminal repeatedly stated as PR-open for user merge — endpoint
  named: yes → continuous; PR-open terminal; never auto-merge.
- Kickoff decision: seed themes user-confirmed (brief §Addendum 7),
  verbatim content for T1's DIRECTION.md — `## Next`: ①
  investing-toolkit 三大表＋管理層 KPI 完整歷史入 kpi_store ②
  loom-code replay matrix——skill 文本改動的客觀迴歸量測; `## Later`:
  ① 投資線營運指標敘事層（非金錢 KPI）② loom 機制 Codex 移植線 ③
  obsidian wiki 知識線深化.
- Kickoff decision: `## Now` name retained (Task rejected —
  term-collision); Now = parallel active set (brief §Addendum 3);
  roadmap-entry pattern = named backlog-entry pattern, no new file
  type (§Addendum 1); betting candidates same-lane first (§Addendum 4);
  DIRECTION header carries the merge-conflict regenerate line
  (§Addendum 5).
- Review plan: whole-branch review = code + docs arms, plus a HAIKU
  COLD-READ probe leg on the two station edits (T3/T4): blind scenario
  execution must reach the conditional posture correctly (repo WITHOUT
  DIRECTION.md → silent skip; WITH → read/bet) — the portability
  contract is exactly what a weak model must not misread.
- Wave discipline: Wave 1 = T1 + T5-T9 (all disjoint); Wave 2 =
  T3 + T4 in parallel (disjoint, both depend on T1) with T2 running
  sequentially in the same window (Independent: false — it shares
  scripts/test_backlog_index.py with T1, so it never co-dispatches
  with any task touching that file; T1 is already done by wave 2);
  Wave 3 = T10. One commit per Bash block while agents live
  (parallel-wave-commit-discipline).
- Change-folder binding: Layer 0 explicit handoff — input is the brief;
  non-archived investing change-folders remain unrelated, NOT bound
  (stated loudly).
- Kickoff briefing: zero one-way-door decisions (all edits reversible
  from git history; the convention is opt-in per repo). The seed-theme
  ask was the only user input — collected (see Kickoff decision above).
- RESUME NOTE (2026-08-08, session handoff): wave 1 fully done and
  reviewed (T1 spec PASS + quality PASS_WITH_NOTES; five tombstones
  mechanical-self-check clean; suite 1185). Wave-2 claims were reset to
  pending — their implementers were never spawned (session subagent
  budget exhausted at 200/200; user chose pause-and-new-session).
  Carried 🟡 debt for the PR body: build_direction_now is the third
  near-copy of the entry-iteration loop in scripts/backlog_index.py
  (prescribed fix: extract a shared _iter_entries_validated iterator —
  reviewer finding, Rule of Three). Carried 🟢: charter/enforcement
  wording gap on the Now-body date exemption (DIRECTION.md:12-13 vs
  script docstring); date-regex boundary behavior is plan-pinned
  (bare years pass, TW tickers like 2049.TW false-positive) — upstream
  debt, not implementer error; Violation.kind vocabulary comment not
  extended; main() length pre-existing. T1's three adjudicated
  deviations (Now-body date exemption / flagless-defaults-to-validate /
  <store>/../DIRECTION.md resolution) are all ACCEPTED and documented.
  Next session: dispatch T2+T3+T4 (pairwise disjoint; T1 done so T2's
  Independent:false constraint is satisfied), then T10, then
  whole-branch review (code + docs + haiku cold-read on T3/T4's
  conditional posture), then finishing to PR-open.
- T2's RED grep caveat: anchor is the longer "Bet (promote)" token —
  the implementer re-anchors if the live grep collides (store lesson:
  docs/loom/memory/a-red-grep-pinned-to-prose-must-anchor-a-phrase-that-exists-on-one-line.md).
