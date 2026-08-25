=== PACKET A ===

### Task
Write fetcher.py that downloads station data and writes stations.json with a `station` key per record.
Files touched: pipeline/fetcher.py

### Context
- /tmp/none

### Resource Paths
- protocol: loom-code/skills/tdd-iron-law/SKILL.md
- standards: load on cite, not upfront. The `rule-sheet-v1` block in `loom-code/agents/implementer.md` embeds the cite-on-fire discipline and the dimension → standard mapping that tells you which of the 9 standards files under `loom-code/skills/subagent-driven-development/standards/` to load when a specific concern fires.
- repo: /tmp/toy-repo
- branch: feat/pipeline
- Resolved test command: python3 -m pytest -q

### Seam contracts
- from Task 1: payload: stations.json records; owner: Task 1; probe: `python3 -m pytest tests/test_renderer.py`
  - owner parser/schema: pipeline/stations_schema.py — you are the owner; this is the ONLY legal writer for this payload's shape. Do not hand-roll a second writer/reader for stations.json elsewhere.

=== PACKET B ===

### Task
Write renderer.py that reads stations.json and renders a report table.
Files touched: pipeline/renderer.py

### Context
- /tmp/none

### Resource Paths
- protocol: loom-code/skills/tdd-iron-law/SKILL.md
- standards: load on cite, not upfront. The `rule-sheet-v1` block in `loom-code/agents/implementer.md` embeds the cite-on-fire discipline and the dimension → standard mapping that tells you which of the 9 standards files under `loom-code/skills/subagent-driven-development/standards/` to load when a specific concern fires.
- repo: /tmp/toy-repo
- branch: feat/pipeline
- Resolved test command: python3 -m pytest -q

### Seam contracts
- from Task 1: payload: stations.json records; owner: Task 1; probe: `python3 -m pytest tests/test_renderer.py`
  - owner parser/schema: pipeline/stations_schema.py — this is the ONLY legal reader for stations.json; import it, never hand-roll a second reader.
- from Task 2: payload: rendered report table string; owner: Task 2; probe: `python3 -m pytest tests/test_cli.py`
  - you are the owner of this payload-bearing seam; no owner parser/schema path was supplied for the report-table string in the plan/assumptions — none to cite.
