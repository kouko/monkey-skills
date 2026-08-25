# Plan: log-ingest pipeline

**Source brief**: none — toy fixture task (mini brief supplied inline, no committed brief file)
Goal: a raw log file can be parsed into structured events and summarized into a per-level count report, with the two commands documented
Stage: planning
**Total tasks**: 3
**Critical-path depth**: 3 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PENDING

## Task-flow diagram

N/A — no flow/state/architecture-shaped content: three tasks form a single linear chain (Task 1 → Task 2 → Task 3), fully stated by the `Dependencies` fields; a paragraph suffices.

## Open Questions

N/A — no unresolved question: mini brief left nothing undecided at plan time.

## Task 1 — Parse raw log lines into events.json

- **Description**: Write `ingest/parse.py` to read `logs/raw.txt` and write `events.json` as a list of `{ts, level, msg}` objects.
  - Parse one line per event; skip/ignore malformed lines rather than crashing.
- **Module**: `ingest/parse.py`
- **Files touched**: `ingest/parse.py`, `tests/test_parse.py`
- **Context paths**:
  - /tmp/none
- **Acceptance**:
  - **RED**: `tests/test_parse.py::test_parse_raw_log_produces_events_json` fails
  - **GREEN**: `events.json` written; content is a JSON list of `{ts, level, msg}` objects matching a fixture `logs/raw.txt`
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: none — toy fixture task
- **Status**: pending
- **Gloss**: Raw log text becomes structured events — the input every later step in the pipeline depends on.

## Task 2 — Summarize events.json into per-level counts

- **Description**: Write `ingest/summarize.py` to read `events.json` and write `summary.md` with a per-level event count.
- **Module**: `ingest/summarize.py`
- **Files touched**: `ingest/summarize.py`, `tests/test_summarize.py`
- **Context paths**:
  - /tmp/none
- **Acceptance**:
  - **RED**: `tests/test_summarize.py::test_summarize_events_json_produces_summary_md` fails
  - **GREEN**: `summary.md` written; contains one count line per distinct `level` value present in a fixture `events.json`
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: `events.json` — list of `{ts, level, msg}` objects; owner: Task 1; probe: `tests/test_summarize.py::test_summarize_events_json_produces_summary_md`
- **Independent**: false
- **Brief item covered**: none — toy fixture task
- **Status**: pending
- **Gloss**: The parsed events turn into a readable count-by-level report — the thing a reader actually wants out of the log.

## Task 3 — Document the two commands in README.md

- **Description**: Add a section to `README.md` documenting how to run `ingest/parse.py` and `ingest/summarize.py`, in order, with their inputs and outputs.
- **Module**: `README.md`
- **Files touched**: `README.md`
- **Context paths**:
  - /tmp/none
- **Acceptance**:
  - **RED**: `tests/test_readme.py::test_readme_documents_both_commands` fails
  - **GREEN**: `README.md` names both commands, their invocation, and the `raw.txt → events.json → summary.md` data flow between them
- **Dependencies**: Tasks 1, 2 complete first
- **Seam**:
  - from Task 1: payload: none
  - from Task 2: payload: none
- **Independent**: false
- **Review-weight**: prose
- **Brief item covered**: none — toy fixture task
- **Status**: pending
- **Gloss**: The two commands become discoverable and runnable by someone who wasn't in this session — the pipeline is only useful once it's documented.
