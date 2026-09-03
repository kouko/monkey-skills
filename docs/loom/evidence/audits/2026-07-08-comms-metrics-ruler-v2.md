# Comms metrics — ruler v2 (harness-injection filter + CJK floor)

Date: 2026-07-08. Supersedes the NUMBERS in
`2026-07-07-comms-metrics-recipe.md` (method and rerun command
unchanged); loom-pipeline 0.6.1.

## Why the ruler changed

Post-merge live probing found `conversation_language()` returning None
on the overhaul session itself: Claude Code writes machine payloads
into the transcript as USER-role turns, flooding the rolling language
window. Three shapes identified and now filtered (`lang_detect.py`
`_HARNESS_INJECTION_*`):

1. `Base directory for this skill:` — every Skill invocation echoes the
   full (English) SKILL.md body as a user turn;
2. `[Request interrupted` — harness marker;
3. `^Run the "<name>" workflow\.` — Workflow/skill invocation echo.

Additionally the 20-visible-char detectability floor discarded
short-but-unambiguous CJK turns (「修」-style confirmations are this
operator's dominant real style); floor is now `visible ≥ 20 OR
CJK chars ≥ 8`, and undetectable turns no longer dilute the majority
vote (last-n DETECTABLE turns are sampled).

Deliberately NOT filtered: English wakeup/continuation prompts written
by the orchestrator via ScheduleWakeup — they are indistinguishable
from genuinely typed user turns. Behavioral rule instead: the
orchestrator writes wakeup prompts in the conversation language.

Effect on the hooks: with ruler v1 the language anchor NEVER fired in
skill-heavy sessions (detection None → fail-open no-op) — the exact
sessions it was built for. Verified fixed: the overhaul session now
detects `zh` (frozen fixture: `fixtures/fixture_session_tail.jsonl`).

## Numbers (same 11 baseline sessions, same command as the recipe doc)

| Metric | ruler v1 (2026-07-07) | ruler v2 | Why it moved |
|---|---|---|---|
| wrong-language ratio | 96/216 = 44.4% | 244/487 = 50.1% | Injection filter gives more sessions a detected conversation language and the CJK floor doubles eligible turns — English narration previously hidden by None-detection is now counted |
| visual-at-fork rate | 23/65 = 35.4% | 23/65 = 35.4% | Visual detection untouched by the ruler change |
| confusion signals | 4 | 2 | Two prior hits lived inside now-filtered machine-payload turns (they were echo text, not the user speaking) |

Pre-effect snapshot (8 sessions, 2026-07-06→08, fixes not yet active):
wrong-language 65/186 = 35.0%, visual-at-fork 0/4, confusion 0.

## Post-ship acceptance (restated against ruler v2)

After ~10 real sessions with loom-pipeline ≥0.6.1 + loom-code ≥0.27.0
active, rerun the recipe-doc command. Targets (brief §Acceptance 5):
wrong-language <10% (v2 baseline 50.1%), visual-at-fork ≥50% where ≥2
options compared (35.4%), zero undefined internal terms at sign-offs.
Compare ONLY v2-to-v2 — v1 numbers are ruler artifacts.

## How to rerun

Identical command as `2026-07-07-comms-metrics-recipe.md` §How to
rerun (the 11-session invocation with `--json`), on loom-pipeline
≥0.6.1.
