# Plan: station report pipeline

**Source brief**: docs/loom/specs/2026-08-25-station-report.md
Goal: fetcher writes stations.json, renderer reads it, CLI wires both.
**Total tasks**: 3
**Critical-path depth**: 3 (≤5)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PENDING

## Task-flow diagram

N/A — no flow/state/architecture-shaped content: three-task chain stated in Goal.

## Open Questions

N/A — no unresolved question: toy fixture.

## Task 1 — fetcher

- **Description**: Write fetcher.py that downloads station data and writes stations.json with a `station` key per record.
- **Module**: pipeline
- **Files touched**: pipeline/fetcher.py
- **Context paths**:
  - /tmp/none
- **Acceptance**:
  - **RED**: `python3 -m pytest tests/test_fetcher.py` fails (module absent).
  - **GREEN**: test passes; stations.json written with `station` keys.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: none — toy fixture task
- **Status**: pending

## Task 2 — renderer

- **Description**: Write renderer.py that reads stations.json and renders a report table.
- **Module**: pipeline
- **Files touched**: pipeline/renderer.py
- **Context paths**:
  - /tmp/none
- **Acceptance**:
  - **RED**: `python3 -m pytest tests/test_renderer.py` fails (module absent).
  - **GREEN**: test passes; report lists every station.
- **Seam**:
  - from Task 1: payload: stations.json records; owner: Task 1; probe: `python3 -m pytest tests/test_pipeline_end_to_end.py`
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: none — toy fixture task
- **Status**: pending

## Task 3 — CLI wiring

- **Description**: Write cli.py wiring fetcher and renderer behind one command.
- **Module**: pipeline
- **Files touched**: pipeline/cli.py
- **Context paths**:
  - /tmp/none
- **Acceptance**:
  - **RED**: `python3 -m pytest tests/test_cli.py` fails (module absent).
  - **GREEN**: test passes; `pipeline report` prints the table.
- **Seam**:
  - from Task 1: payload: none
  - from Task 1: payload: none
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false
- **Brief item covered**: none — toy fixture task
- **Status**: pending
