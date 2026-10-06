# Canvas skill layout templates + output validator — acceptance test evidence

Tried on 2026-10-05, in a clean copy of the project at `644c60d43`.

Setup: `git worktree add /private/var/folders/m5/4cb4p8h938qc4qcpdykwz2480000gn/T/opencode/acc-test-canvas HEAD` (detached HEAD at `644c60d43`). All runs below are inside that worktree unless noted.

## 1. Four new layout patterns each documented (node composition, grouping, connections, color semantics) + one template each

How I tried it:
- Read `obsidian/skills/obsidian-canvas-creator/references/layout-patterns.md`.
- Read each of the four new templates under `obsidian/skills/obsidian-canvas-creator/assets/`.
- Ran the validator on all six bundled templates (the four new + the two pre-existing).
- Parsed and checked the four JSON examples embedded in the docs.

What came back:
- `references/layout-patterns.md` has, for each of the four patterns, the four required sections: Kanban at lines 23–60 (Node Composition 25, Grouping 35, Connections 45, Color Semantics 52), Dashboard / Home Page at 81–118 (83/92/101/108), Research Map at 135–172 (137/144/152/162), Moodboard at 192–220 (194/201/210/214).
- Four templates exist and match the documented rules: `template-kanban.canvas` (three columns x=0/340/680, colors 6/2/4, one `blocked by` edge), `template-dashboard.canvas` (title + 3 sections x=0/500/1000, no edges), `template-research-map.canvas` (root + 3 Theme groups, `explores`/`extends`/`contradicts` edges), `template-moodboard.canvas` (3 groups, file/link nodes, no edges).
- The two pre-existing templates changed only in commit `21f64afe2` ("conform bundled template ids to the validator"): `template-mindmap-simple.canvas` and `template-freeform-grouped.canvas` had their ids rewritten from short ids (`root001`, `e1`, …) to 16-char lowercase hex; every coordinate, size, color, label and edge pair is identical to the pre-change version (`git diff 2068db1c2..HEAD` shows only id/fromNode/toNode rewrites).

Validator on the six bundled templates (from the skill directory):

```
$ python3 obsidian/skills/obsidian-canvas-creator/scripts/validate_canvas.py \
    obsidian/skills/obsidian-canvas-creator/assets/*.canvas
(no output)
$ echo $?
0
```

Doc examples parse and conform:

```
$ python3 - <<'EOF'
... (parse the 4 ```json blocks in layout-patterns.md) ...
example 1: JSON parses=True, ids 16-hex-unique=True, edge refs resolve=True
example 2: JSON parses=True, ids 16-hex-unique=True, edge refs resolve=True
example 3: JSON parses=True, ids 16-hex-unique=True, edge refs resolve=True
example 4: JSON parses=True, ids 16-hex-unique=True, edge refs resolve=True
EOF
```

Evidence: `obsidian/skills/obsidian-canvas-creator/references/layout-patterns.md:23-234`; `assets/template-kanban.canvas`, `assets/template-dashboard.canvas`, `assets/template-research-map.canvas`, `assets/template-moodboard.canvas`; validator exit code 0 on all six templates.

## 2. Asking the skill for any of the four patterns produces structure conforming to that pattern's rules

How I tried it (exercising the routing, not just reading):
- Read `SKILL.md` step 2 (lines 42–53): "Community Layout Patterns (Kanban, Dashboard / Home Page, Research Map, Moodboard)" routes to `references/layout-patterns.md` and to the matching template under `assets/` (table at SKILL.md:48-53).
- Acted as the skill instructs: for each of the four patterns I read the pattern's rules in `references/layout-patterns.md`, started from the matching template, and generated a *fresh* canvas with different subject matter (blog-launch kanban, home dashboard, attention-in-LLMs research map, cabin moodboard) at `/private/var/folders/m5/4cb4p8h938qc4qcpdykwz2480000gn/T/opencode/acc-probes/skill-output/`.
- Ran the bundled validator on all four generated files.
- Ran a 44-point mechanical conformance check (`conformance_check.py`) asserting the documented rules: column/gap geometry (40px), group-first ordering, cards fully inside their groups, color semantics per pattern, edge labels/colors (`blocked by` red, `explores`, `extends` orange, `contradicts` red), no edges where the pattern forbids them, title/root placement.

What came back:

```
$ python3 <skill>/scripts/validate_canvas.py skill-output/kanban-blog.canvas      → exit 0
$ python3 <skill>/scripts/validate_canvas.py skill-output/dashboard-home.canvas   → exit 0
$ python3 <skill>/scripts/validate_canvas.py skill-output/research-attention.canvas → exit 0
$ python3 <skill>/scripts/validate_canvas.py skill-output/moodboard-cabin.canvas  → exit 0
(no output; each EXIT=0)
```

```
$ python3 conformance_check.py
44/44 conformance checks passed
(EXIT=0; one FAIL during development was a bug in my checker — the dashboard title intentionally
 sits above the sections — fixed the checker, then 44/44.)
```

Evidence: validator exit 0 for each generated file; `conformance_check.py` output "44/44 conformance checks passed". Skill routing anchors: `SKILL.md:42-53`, `references/layout-patterns.md:14-21` (Pattern Selection).

`conformance_check.py` (run from the probe directory, read-only over the four freshly generated canvases under `skill-output/`) asserted these 44 checks, all PASS. The count is per item: a check repeated once per node is counted once per node.

**Kanban — `kanban-blog.canvas` (14 checks)**
1. three column groups
2. columns in workflow order
3. group color = state (6 To Do / 2 In Progress / 4 Done)
4. 40px column gap
5. full board height columns
6. groups listed first
7–12. each card fully inside its column (6 cards: Write outline, Pick hero images, Draft post, Blog/Draft Notes, Publish, Promote on feed)
13. exactly one urgent (red) card
14. single dependency edge labeled `blocked by`, red

**Dashboard / Home Page — `dashboard-home.canvas` (14 checks)**
15. purple title node on top
16. three section groups
17. 3-section row at x=0/500/1000 (40px gap)
18. title centered above the middle section
19. no edges
20–25. each node fully inside one section (6 nodes: Jot an idea, Morning pages, two file nodes, two link nodes)
26. capture text yellow `3`
27. file nodes yellow/green
28. link nodes cyan `5`

**Research Map — `research-attention.canvas` (9 checks)**
29. root question purple `6`
30. two `Theme` groups
31. group color neutral
32. root above groups
33. theme papers inside groups
34. root `explores` each theme anchor
35. `extends` edge orange `2`
36. `contradicts` edge red `1`
37. paper colors are the reading-status set

**Moodboard — `moodboard-cabin.canvas` (7 checks)**
38. three theme groups
39. group backgrounds neutral
40. 40px group gap
41. no edges
42. at most one purple accent anchor
43. link nodes cyan `5`
44. no text nodes (optional)

The 44 fall into five categories: 40px geometry, group-first ordering, cards fully inside their groups, color semantics, and edge labels/colors. `conformance_check.py` was a one-off acceptance aid and is not committed here.

## 3. Validator checks: JSON parse, unique 16-char lowercase-hex ids, edge fromNode/toNode existence, per-type required fields, no overlap; exit 0 clean / non-zero naming each violation

How I tried it: wrote 12 hand-crafted probe files (`/private/var/folders/m5/4cb4p8h938qc4qcpdykwz2480000gn/T/opencode/acc-probes/`) exercising every check, plus the six bundled templates (clean, see section 1), and ran `python3 obsidian/skills/obsidian-canvas-creator/scripts/validate_canvas.py <file>` on each.

What came back (each probe file, its output, and exit code):

```
=== bad-json.canvas ===                       (malformed JSON)
bad-json.canvas: invalid JSON: Expecting value: line 1 column 14 (char 13)
EXIT=1
=== dupe-id.canvas ===                        (same id twice)
node "aaaaaaaaaaaaaaaa": duplicate id
EXIT=1
=== dangling-edge.canvas ===                  (toNode references no node)
edge "bbbbbbbbbbbbbbbb": toNode "missingnode00000" references missing node
EXIT=1
=== missing-fields.canvas ===                 (text node without text; file node without file)
node "aaaaaaaaaaaaaaaa": missing required field "text" for type "text"
node "cccccccccccccccc": missing required field "file" for type "file"
EXIT=1
=== overlap.canvas ===                        (two overlapping text nodes)
node "aaaaaaaaaaaaaaaa" overlaps node "eeeeeeeeeeeeeeee"
EXIT=1
=== bad-id-format.canvas ===                  (uppercase id; 7-char id)
node "AAAAAAAAAAAAAAAA": invalid id (want 16 lowercase hex chars)
node "shortid": invalid id (want 16 lowercase hex chars)
EXIT=1
=== group-contains-child.canvas ===           (child inside a group — allowed by design)
(no output)
EXIT=0
=== top-level-array.canvas ===                (top level not an object)
top-level-array.canvas: top level is not an object
EXIT=1
=== link-no-url.canvas ===                    (link node without url)
node "dddddddddddddddd": missing required field "url" for type "link"
EXIT=1
=== node-edge-id-collision.canvas ===         (edge id equals a node id)
edge "aaaaaaaaaaaaaaaa": duplicate id
EXIT=1
=== empty-node-missing-id.canvas ===          (node without id)
node #0: id must be a string
EXIT=1
=== /nope/missing.canvas ===                  (unreadable file)
/nope/missing.canvas: cannot read: [Errno 2] No such file or directory: '/nope/missing.canvas'
EXIT=1
```

Each violation is named individually with the node/edge id and reason, and every violating file exits 1 while clean files exit 0. The overlap check is positive-area AABB intersection between non-group nodes only, as the spec's Design decision states (group nodes excluded; siblings inside a group still overlap-checked — `obsidian/tests/test_validate_canvas.py::test_group_overlapping_its_children_is_not_flagged` and the adversarial probe `test_sibling_overlap_inside_group_still_flagged`).

Evidence: probe outputs above; exit codes; `scripts/validate_canvas.py:60-162` (checks), `scripts/validate_canvas.py:31-36` (id regex and per-type field map).

## 4. Validator has automated tests, merged into the repo's pytest suite, all passing

How I tried it:
- Ran the validator's own test file: `cd obsidian && python3 -m pytest tests/test_validate_canvas.py -v`
- Ran the plugin suite: `cd obsidian && python3 -m pytest tests/ -q`
- Ran the committed adversarial probes for the validator: `python3 -m pytest docs/loom/2026-10-05-canvas-layout-templates-validator/evidence/probes/test_canvas_validator_adversarial.py -q`
- Did NOT run the full repo package suite (`python3 -m pytest scripts/ -q` at repo root) — that check runs before the change is accepted and blocks it on failure; this row covers the criterion's own tests.

What came back:

```
$ cd obsidian && python3 -m pytest tests/test_validate_canvas.py -v
tests/test_validate_canvas.py::test_clean_valid_canvas_exits_zero PASSED
tests/test_validate_canvas.py::test_duplicate_id_is_reported PASSED
tests/test_validate_canvas.py::test_dangling_edge_reference_is_reported PASSED
tests/test_validate_canvas.py::test_missing_required_field_is_reported PASSED
tests/test_validate_canvas.py::test_overlapping_non_group_nodes_are_reported PASSED
tests/test_validate_canvas.py::test_group_overlapping_its_children_is_not_flagged PASSED
6 passed in 0.70s

$ cd obsidian && python3 -m pytest tests/ -q
28 passed in 1.14s

$ python3 -m pytest docs/loom/2026-10-05-canvas-layout-templates-validator/evidence/probes/test_canvas_validator_adversarial.py -q
20 passed in 1.21s
```

The validator's tests live in the plugin test directory picked up by the suite (`obsidian/pyproject.toml` `testpaths = ["tests", "scripts", "skills"]`). The 20 adversarial probes cover: non-hex/short/uppercase ids, edge id duplicating a node id, fromNode/toNode referencing missing nodes, missing `nodes`/`edges` keys (clean), non-array nodes, top-level non-objects, unknown node types, overlapping groups not flagged, node inside group not flagged, sibling overlap inside group flagged, empty file, missing file, large clean canvas, late overlap.

Evidence: `obsidian/tests/test_validate_canvas.py` (6 passed); `obsidian/tests/` suite (28 passed); `docs/loom/2026-10-05-canvas-layout-templates-validator/evidence/probes/test_canvas_validator_adversarial.py` (20 passed). Suite command for the full check: `python3 -m pytest scripts/ -q` (repo root).

## 5. Plugin README and skill attribution table match the new capability

How I tried it: read `git diff 2068db1c2..HEAD` for `obsidian/README.md`, `obsidian/README.ja.md`, `obsidian/README.zh-TW.md`, `obsidian/skills/README.md`, the skill READMEs, `obsidian/CHANGELOG.md`, and both `plugin.json` files.

What came back:
- `obsidian/README.md:24` — version 3.22.0, matching `obsidian/.claude-plugin/plugin.json:3` and `obsidian/.codex-plugin/plugin.json:3` (both 3.22.0).
- `obsidian/README.md` skill table row for `obsidian-canvas-creator` now reads: "Create Obsidian Canvas files with MindMap or freeform layouts, plus four community patterns (kanban, dashboard / home page, research map, moodboard) with templates and a `.canvas` output validator. (Combined with json-canvas integration from kepano.)"
- `obsidian/skills/README.md` attribution row for `obsidian-canvas-creator` now appends: "— this repo added layout patterns (kanban, dashboard / home page, research map, moodboard) and a `.canvas` output validator (derivative)" while keeping "MIT (Axton Liu + Steph Ango)".
- `obsidian/README.md` directory tree notes "this repo adds layout patterns + validator" and lists `tests/test_validate_canvas.py`.
- `obsidian/README.ja.md` and `obsidian/README.zh-TW.md` version lines and skill table rows updated (ja line 24/167, zh-TW line 24/165; skill rows list the four patterns and the validator).
- Skill READMEs updated: `obsidian/skills/obsidian-canvas-creator/README.md` (and .ja/.zh-TW) mention the four patterns and the validator; upstream attribution unchanged.
- `obsidian/CHANGELOG.md:7` — `[3.22.0] — 2026-10-05 canvas layout patterns + output validator` describing the four patterns, the validator, and the docs sync.

Evidence: file lines above; `git diff 2068db1c2..HEAD` output.

## Open observations

- `SKILL.md:3` — the frontmatter `description` still reads "Create Obsidian Canvas files with MindMap or freeform layouts…"; it does not name the four new patterns. Routing inside the body is complete (lines 42–53), so once the skill is loaded the patterns are reachable, but a request phrased only as "kanban"/"moodboard" may not select this skill on description alone. Reported as a nit finding.
