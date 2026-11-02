# Preference Log Schema

The preference log is the durable record of every A/B decision
made during `skill-tuning` sessions. It serves two purposes:

1. **Decision basis for current iteration** — what variant did the
   user prefer for this prompt?
2. **Future training data** — at ≥1000 usable single-pick records, becomes RLHF-lite
   dataset for self-trained judge (see `self-trained-judge-pipeline.md`)

## Location

```
<target-skill>/preference-log.jsonl
```

Same level as `SKILL.md`. Per-skill (not centralized) so that
preference data is scoped to the skill it was collected for.

JSONL format (one JSON object per line) so:

- Append is cheap (no full-file parse / rewrite)
- Streaming reads work
- Each line is independently valid (corruption of one line doesn't
  invalidate the rest)

## Per-pick entry schema

```json
{
  "schema_version": 1,
  "timestamp": "2026-04-29T14:30:00Z",
  "session_id": "uuid-or-short-id",
  "skill": "<skill-name>",
  "round": 3,
  "test_prompt_id": 2,
  "test_prompt_hash": "sha256-of-prompt-text",
  "variants_shown": [
    {"label": "A", "identity": "baseline", "skill_md_hash": "..."},
    {"label": "B", "identity": "variant_a", "skill_md_hash": "...", "dimension_explored": "shorter sentences"},
    {"label": "C", "identity": "variant_b", "skill_md_hash": "...", "dimension_explored": "list-first structure"}
  ],
  "constitutional_rejected": [
    {"variant_id": "variant_c", "violated_clause": "MUST #3 exact-integer quantities"}
  ],
  "constitution_present": true,
  "constitution_version": "v1",
  "evaluator": "human-1",
  "user_pick": "B",
  "user_pick_identity": "variant_a",
  "user_notes": "B feels warmer without losing density",
  "decision_time_seconds": 45,
  "verdict": "ADOPT"
}
```

## Field semantics

### `schema_version`
Currently `1`. Increment if schema changes.

### `timestamp`
ISO 8601 UTC. When this pick was made.

### `session_id`
Short identifier (UUID or `<skill>-<date>-<seq>`) grouping all
picks within one tuning session. Useful for "all picks in
session X".

### `skill`
Target skill's frontmatter `name`. Sanity check against the
filename location.

### `round` and `test_prompt_id`
Round number within the session (1, 2, 3...). `test_prompt_id`
matches the id in `test-prompts.json`.

### `test_prompt_hash`
SHA-256 of the prompt text. If the test prompt is later edited,
the hash changes — old log entries can be filtered (preferences
were collected against a different prompt).

### `variants_shown`
Array, one entry per variant in the A/B (typically 2-3 entries
plus the baseline = 3-4 entries total).

Each entry:
- `label`: the letter shown to user (A / B / C)
- `identity`: which variant this *actually* was (`baseline`,
  `variant_a`, `variant_b`, etc.) — the part hidden from user
  during display
- `skill_md_hash`: SHA-256 of the SKILL.md as edited by this
  variant (so we can reconstruct exact state)
- `dimension_explored`: human-readable description of what made
  this variant different (only for non-baseline variants)

### `constitutional_rejected`
Array of variants that were rejected by Phase 2 pre-filter and
*not shown to user*. Logged separately from `variants_shown` so
we can analyze which generation patterns produce contract
violations.

### `constitution_present`, `constitution_version`
Whether the target skill had a constitution at log time, and
which version. Lets the trained judge filter on
"constitutionally-grounded picks" vs "pure-taste picks".

### `evaluator`
Who picked. For single-evaluator: `"human-1"` or actual user
identifier. For multi-evaluator setups, each evaluator gets their
own log entry per pick.

### `user_pick`
The label letter the user picked (`"A"`, `"B"`, `"C"`, or
`"multiple"`, `"none"`, `"refine"`).

### `user_pick_identity`
Decoded identity of the picked variant. Computed by joining
`user_pick` against `variants_shown[*].label` to find the matching
identity. For `multiple` / `none` / `refine`, this is the literal
string.

### `user_notes`
Optional free-form rationale from the user. Highly valuable for
later judge training; capture when user offers it.

### `decision_time_seconds`
How long the user took to pick. Useful for fatigue detection
(very fast = guess; very slow = genuinely hard).

### `verdict`
The skill-tuning verdict applied: `ADOPT` / `DROP` / `DEFER` /
`REFINE` / `ESCALATE`.

## Per-session summary entry

After the session, append one summary entry:

```json
{
  "schema_version": 1,
  "type": "session_summary",
  "session_id": "...",
  "skill": "...",
  "rounds": 3,
  "total_picks": 9,
  "verdicts": {"ADOPT": 1, "DROP": 5, "DEFER": 2, "REFINE": 1},
  "constitutional_rejection_rate": 0.11,
  "evaluator_agreement_rate": null,
  "session_duration_seconds": 1200,
  "outcome": "skill updated to variant_a after round 3"
}
```

Summary entries have `"type": "session_summary"`; per-pick entries
omit the `type` field (or set `"type": "pick"`).

## Privacy considerations

The preference log captures user preferences. Sensitive
considerations:

| Concern | Mitigation |
|---|---|
| User identity | Use evaluator IDs (`human-1`) not names; per-skill log scoped to project |
| Prompt content | Test prompts may contain sensitive info; consider redaction or hashing in shared logs |
| User notes | Free-form text; users may type sensitive context; gitignore the log if working in shared repo, or sanitize before commit |
| Cross-session correlation | Multiple sessions accumulate user preference patterns; treat the log as user-data-equivalent |

For monkey-skills public-repo case, the log is **per-user** and
typically not committed. If committed (for shared learning), apply
sanitization: strip user names, hash prompts containing PII,
review notes manually.

## Retention

The log grows monotonically. Retention policy:

| Age | Action |
|---|---|
| <1 year | Keep all |
| 1-3 years | Keep but flag `"stale": true` for entries older than 1 year |
| >3 years | Optional archival (move to `<skill>/preference-log-archive-YYYY.jsonl`); don't delete (training data is valuable) |

When the target skill is **rewritten significantly** (via
skill-creator-advance), preference log entries against the old
skill are invalidated for current decisions but retained for
historical analysis. Mark with `"applies_to_skill_version": "v1"`
or similar.

## Lifecycle events

| Event | Log action |
|---|---|
| Skill rewritten | Append `"type": "skill_rewrite"` marker; subsequent entries scope to new version |
| Constitution updated | Append `"type": "constitution_update"` with old/new version |
| Test-prompts.json updated | Append `"type": "test_prompts_update"` |

These markers let later analysis filter "preferences collected
under skill version X" cleanly.

## Querying the log

`scripts/preference_log.py` provides:

- `append(entry)` — atomic JSONL append
- `query(filter_dict)` — filter by skill / session_id / verdict /
  evaluator
- `summarize(skill)` — per-skill aggregate (total picks,
  ADOPT rate, etc.)
- `export_for_training(skill, min_entries=1000)` — exports the
  subset suitable for training; fails below the usable-record threshold

A usable record is an explicit single ADOPT of a non-baseline variant or
DROP selecting `baseline`. Both `user_pick` and `user_pick_identity` must be
nonempty single-choice strings; `none`, `multiple`, and `refine` never
provide a winner, even with an ADOPT/DROP verdict. The chosen identity must
match exactly one object in `variants_shown`, with a nonempty
`skill_md_hash`; `test_prompt_hash` must also be nonempty. Old string-list
variants and records missing the chosen identity or hashes are skipped.

When any shown object supplies a `label` field, the picked label must match
exactly one shown object after trimming whitespace and ignoring letter case,
and that object's identity must equal `user_pick_identity`. Contradictory or
duplicate picked-label mappings, and partial mappings without the picked
label, are skipped. Identity-only compatibility applies only when every
shown object omits `label`; incomplete mappings never fall back to it.

Each usable record yields at least one selected-over-other comparison with
distinct, nonempty skill hashes. Unusable alternatives are omitted, and
duplicate alternative hashes produce one pair. Readiness counts **records**,
not pairs: ≥1000 usable records for this skill, regardless of how many pairs
each produces. `--min-entries` overrides that threshold for local checks.
All other records for the target skill (including summaries) count as skipped;
records from other skills are excluded. Both scripts report usable/skipped
record counts and pair counts. Original JSONL bytes remain untouched.

Format for `export_for_training`:

```json
{
  "skill": "...",
  "n_entries_used": 1234,
  "n_entries_skipped": 10,
  "n_training_pairs": 2468,
  "training_pairs": [
    {"test_prompt_hash": "...", "preferred_skill_md_hash": "...", "rejected_skill_md_hash": "...", "evaluator": "human-1", "constitution_version": "v2"}
  ]
}
```

The example omits remaining pairs. The current `judge_train_stub.py` reads
the original JSONL and shares the exporter's eligibility rule; it preserves
its identity-pair API (`preferred`, `rejected`, `test_prompt_hash`). Future
training may consume the exported hash pairs after resolving artifacts;
this change activates no training.

## Anti-patterns

| Anti-pattern | Why bad |
|---|---|
| Editing log entries after the fact | Defeats the durability purpose; preference log should be append-only |
| Logging only ADOPT verdicts | DROP / DEFER / REFINE are also signal; selective logging biases the dataset |
| Sharing logs across skills | Preferences are skill-specific (taste for status report ≠ taste for inventory snapshot); per-skill scope is essential |
| Logging without `decision_time_seconds` | Loses fatigue / confidence signal for free |
| Not capturing `dimension_explored` | Future analysis can't see *what* was being varied; just sees pick |
| Capturing user identity / PII without consent | Privacy violation; sanitize first |
