# Change-folder binding & lifecycle marking — industry research

> **Type**: research note (web-grounded, EN+JA per round; no EN/JA
> disagreements found in any round)
> **Date**: 2026-07-10
> **Consumer**: `docs/loom/specs/2026-07-10-designer-pm-loop-implementation.md`
> (brief) — resolves its Open Questions 1 & 2; also grounds the detection
> cascade in the writing-plans must-consume design.
> **Method**: three research rounds by parallel agents: (1) spec-driven
> tools' spec→implementation binding; (2) branch↔work-item binding at
> scale; (3) proposal lifecycle marking in long-running OSS institutions.

## Round 1 — how shipped SDD tools bind specs to implementation

| Tool | Active-spec detection | Stale handling |
|---|---|---|
| GitHub spec-kit | git branch name IS the key into `specs/<slug>/`; env-var fallback | none — folders sit inert |
| OpenSpec CLI | named arg; else list non-archived, ask on tie (recommended default = most recent) | `openspec archive` moves folder to `changes/archive/YYYY-MM-DD-name/` |
| AWS Kiro | user picks per turn via `#spec` context | permanent living documents |
| Tessl | per-file backlink comment to its 1:1 `.spec.md` | spec-as-source, regenerate |

Finding: **nobody solves staleness by smarter matching — every shipped
answer shrinks the candidate pool (archival) or makes state itself the
binding (branch).** Content-similarity guessing is shipped by no one.

## Round 2 — branch↔work-item binding precedents

- **Jira smart commits / GitHub issue-branches / GitLab `{id}-slug`**
  (Atlassian docs EN/JA; GitHub/GitLab docs): binding is exact-format
  match only; **absence = silent no-op, never an error**. Proven at the
  largest scale precisely because it is opportunistic/additive.
- **spec-kit as cautionary tale** (issues #333/#407/#521/#733/#1110):
  branch-name as SOLE source of truth → rename the branch and the tool
  "behaves erratically", silently recreates "missing" folders; one user
  lost 4 hours (#733); Jira-style branch names trigger wrong-match
  behavior (#1110).
- **Trunk-based development** (trunkbaseddevelopment.com, Atlassian
  EN/JA): branches are hours-lived and disposable; TBD carries work-item
  context in commit messages/PR association, never branch identity.
- Misc failure mode: branch-name regex mis-extraction (GitVersion #4154).

**Conclusion**: the safety axis is *opportunistic vs sole-truth*, not
*branch vs no-branch*. Keep the branch layer only as: deterministic exact
slug match; miss → silent fall-through; when it decides, SAY SO
("bound to `<change-id>` via branch name"); any ambiguity → fall to the
ask layer, never pick.

## Round 3 — lifecycle marking in long-running proposal systems

| System | Mechanism | Files move? | Transition enforced by |
|---|---|---|---|
| Python PEPs | `Status:` header in-file | never | PEP editor PR; index built by parsing headers |
| Rust RFCs | merge-into-tree = accepted; later status NOT in file | merge is the move | none — documented rot: "impossible to tell if implemented/superseded" |
| Kubernetes KEPs | `kep.yaml` `status:` + `superseded-by` | never | PR review + field lint; dashboards purpose-built to read the field |
| ADR (Nygard/MADR) | `Status:` line; supersede = new file | never | human convention only |
| TC39 | stage field + hand-curated list; finished → separate `finished-proposals.md` | list-move | editors |
| Ember RFCs | RFC 0617 moved FROM folder-move (`active/`/`complete/`) TO front-matter `stage` | no (post-0617) | bot + editors |
| OpenSpec | `archive` command merges deltas then MOVES folder | yes | single deterministic CLI command (its own bug class: path bugs, issue #412) |

**Conclusion**: metadata-in-place works ONLY where consuming tooling has a
purpose-built read-the-field contract (PEP index builder, KEP dashboards);
without it, metadata rots (Rust's own postmortem). Our consumer is an
agent globbing `docs/loom/*/` — a naive-reader contract → **physical move
is correct-by-construction**. The one shape-identical system (OpenSpec,
folder-per-change) moves. Ember's counter-motion applies to flat
tracking-doc repos, not folder-per-change shapes.

## Resolved decisions (adopted into the brief)

1. **Branch layer: keep, opportunistic-only.** Exact `docs/loom/<change-id>`
   slug match against the current branch name; no fuzzy matching; miss →
   silent fall-through to the count layer; when the branch layer is the
   deciding signal, surface the binding explicitly; ambiguous → ask layer.
   Reversal trigger: one real wrong-bind incident → downgrade to
   confirm-before-use (cost-per-incident is hours, asymmetric).
2. **Lifecycle: folder-move + lightweight in-place status (hybrid).**
   Archive = deterministic script step inside
   finishing-a-development-branch (single-command semantics à la
   `openspec archive`; script, not manual `mv` — OpenSpec's #412 shows
   path-handling is the move approach's real risk, so it gets tests).
   Destination `docs/loom/archive/<date>-<change-id>/`. A small
   status/frontmatter field rides in the change-folder for the
   pre-archive window and in-archive provenance — the glob never depends
   on it. If path references to archived folders break in practice, leave
   a one-line tombstone stub at the old path (do not revert to
   metadata-only).
