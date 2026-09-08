# loom contract package

The versioned contract loom-design and loom-workflow depend on (concept-model §1).
Only loom-code writes here; the other plugins read.

| file | role |
|---|---|
| `manifest.yaml` | machine-readable declaration: 7 stations, 10 tools (+2 standalone, uncounted), actions, artifact schemas, standing docs, KICKOFF-DEFAULTS keys, artifact-type mapping. `artifacts.<name>.charter` is the single copy of what each artifact answers, must/must-not carry, its sign-off station and what edits it after — `loom_checker.py charter` renders it as a table. One of the five recomputable surfaces of `docs/loom/evidence/mechanisms.yaml`. |
| `templates/intent.md` | intent schema (§2b) |
| `templates/spec-minimal.md` | spec schema (§2c); write-plan uses it to auto-generate a minimal spec when loom-design is not installed |
| `templates/plan.md` | plan shape (§2d) |
| `templates/review.json` | compatibility input used only by risk-triggered pre-build spec review |
| `templates/attestation.json` | generated closing-review evidence bound to the functional-content digest |
| `templates/PRINCIPLES-interview.md` | the product-principles interview run inside decision point ① when a product intent meets a repo without a ratified PRINCIPLES.md |
| `templates/KICKOFF-DEFAULTS.md`, `templates/memory-README.md`, `templates/PURPOSE.md` | scaffolds for an adopting repo's `docs/loom/` |

The checker that enforces the schemas is `loom-code/scripts/loom_checker.py` (`--list-rules` prints every rule id).
