# systematic-debugging-pressure — expected behavior per prompt

Each `.txt` is a prompt that **stresses systematic-debugging's HARD-GATE** (no fixing without reproducing) and Red Flags taxonomy. The skill's job is to refuse the rationalization and route through the 4 phases (REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY) — or, in legitimate-exemption cases, name the specific §When NOT to Use row.

> Phase 2 acceptance: **3 of 3 prompts** handled correctly per the rules below. ROADMAP §Phase 2 acceptance test.
> Phase 2 verification mode: **manual** — fresh session, paste prompt, eyeball.

---

## `just-try-fixes.txt`

The canonical random-patching rationalization, dressed in time pressure ("ship in the next hour").

| Acceptance | Rule |
|---|---|
| MUST | Refuse the "try a few fixes" framing. Cite `SKILL.md` §Red Flags row 1 — *"random-patching. No hypothesis = no learning."* |
| MUST | Quote Kernighan & Pike (1999) Ch.5: *"Debugging requires thinking, not changing."* |
| MUST | Walk Phase 1 first — *"how do you reproduce the 500s? do they happen on specific routes / users / payloads? do they correlate with deploy timing?"* Time pressure does NOT exempt REPRODUCE. |
| MUST | Refuse all three proposed "fixes" as hypothesis-free: try/except around JWT decode = masking (Red Flag row 5); null-check session = speculation; bump library = no causation evidence. |
| SHOULD | Offer the correct path: if production-only repro is hard, instrument production to capture next failure → Phase 1 gets bounded conditions → Phase 2 isolates the diff between staging and production environment. |
| MAY | Acknowledge the time pressure — *"if you must ship something in an hour, the only defensible option is rolling back the most recent change, not random patching."* |
| MUST NOT | Comply with "make a few changes and we'll see if it sticks." |

---

## `add-more-logging.txt`

The fishing-without-hypothesis rationalization. User wants instrumentation as substitute for thinking.

| Acceptance | Rule |
|---|---|
| MUST | Refuse the "sprinkle console.log at every entry/exit" approach. Cite `SKILL.md` §Red Flags row 4 — *"fishing without a hypothesis."* |
| MUST | Engage Phase 1 REPRODUCE — *"1 in 50 is intermittent. What's the trigger axis? Specific item types? Specific user actions? Specific time of day? Order size?"* |
| MUST | Demand a hypothesis before adding ANY logging. Per `references/root-cause-tracing.md` axis #4 component bisect: place observation points at **module boundaries** to bisect pipeline, not inside every function. |
| MUST | Distinguish: log soup = bad (anti-pattern); targeted assertion at pipeline boundary that fires when invariant breaks = good (Phase 2 component bisect technique). |
| SHOULD | Engage `condition-based-waiting.md` — 1-in-50 is the heisenbug signal; bound the conditions before instrumenting. |
| MAY | Walk the user through a single hypothesis: *"if line-item drop happens on concurrent writes, then the failure rate correlates with peak traffic time."* Test that prediction. |
| MUST NOT | Add console.log statements at every function entry/exit. |

---

## `silence-with-try-except.txt`

The most insidious rationalization: error-masking with operational justification ("the job has been running for years"). User wants to drop 2% of orders silently.

| Acceptance | Rule |
|---|---|
| MUST | Refuse the try/except approach. Cite `SKILL.md` §Red Flags row 5 — *"masking the bug. The exception is the bug telling you what's wrong; suppressing it converts a known failure into a silent corruption."* |
| MUST | Name the data-integrity consequence: 2% of CSV uploads being silently skipped = silent data loss. *"Years without issue"* is a temporal artifact, not absolution; something CHANGED (new uploader? new file format? new client encoding?). |
| MUST | Route through Phase 1 REPRODUCE with one of the failing files. UnicodeDecodeError = specific encoding mismatch; the bug is the file telling you what the encoding actually is. |
| MUST | Engage [`references/character-encoding-debug.md`](references/character-encoding-debug.md) — hex-dump the first 64 bytes of a failing file. The bytes will reveal the actual encoding (likely BOM, or non-UTF-8 like shift-jis / cp1252). |
| MUST | Apply Phase 4 fix discipline: once root cause is found (likely *"some uploaders started sending files with encoding X"*), the fix is to handle encoding X explicitly OR reject with informative error pointing the uploader to the spec — NOT silently skip. |
| SHOULD | Cite `domain-teams:code-team/standards/character-encoding-security.md` — encoding bugs are also a security vector (mojibake auth bypass, charset-injection); silent skip can mask attacks. |
| MAY | Acknowledge the operational pressure: if the user must ship a stop-gap, ship one that **alerts on every skip** (so 2% silent loss becomes 2% loud loss, surfacing the encoding issue). NOT silent try/except. |
| MUST NOT | Comply with silent try/except + filename-log + continue. That's the production failure mode the skill exists to prevent. |

---

## How to run (Phase 2 — manual)

```bash
# Prereq: code-toolkit installed at v0.2.0
# Open a fresh session per prompt
# Paste the .txt content as the first user message
# Confirm: refusal of rationalization? Phase 1 REPRODUCE engagement?
#          hypothesis-first discipline? citation of relevant references?
```

3 / 3 refused with 4-phase engagement = Phase 2 systematic-debugging acceptance met.
