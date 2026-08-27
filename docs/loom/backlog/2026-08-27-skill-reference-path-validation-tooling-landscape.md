---
name: 2026-08-27-skill-reference-path-validation-tooling-landscape
description: Nothing validates the plain-text file paths loom skills tell agents to open, and the surveyed ecosystem does not yet supply one worth adopting — the official reference validator declines the job, general link checkers deliberately skip inline code, and the one third-party linter that does it is a solo project; revisit when skill-lint gains adoption or the agentskills resolution proposals land
status: open
origin: 2026-08-27 fix/conditional-ops-path — three dangling path literals shipped in conditional-operations.md because check-skill-crossrefs.py checks inline markdown links only; a survey of the tooling landscape was run before deciding whether to build a checker, and the answer was to wait
start: whichever comes first — skill-lint (or an equivalent) shows real adoption beyond its author, agentskills discussion #210 or a successor reaches an adopted spec (#178 is already closed and is not a live trigger), or a third dangling-path defect ships from this repo
---

- Start: whichever comes first — skill-lint (or an equivalent) shows real adoption
  beyond its author, agentskills discussion #210 or a successor reaches an
  adopted spec (#178 is already closed and is not a live trigger), or a
  third dangling-path defect ships from this repo
- Origin: 2026-08-27 fix/conditional-ops-path — three dangling path literals shipped
  in conditional-operations.md because check-skill-crossrefs.py checks
  inline markdown links only; a survey of the tooling landscape was run
  before deciding whether to build a checker, and the answer was to wait
- What: this repo has no check on the plain-text file paths its skills tell
  agents to open. `loom-code/scripts/check-skill-crossrefs.py` states its own
  bound in its docstring — "only INLINE links `](target)` are checked" — so a
  backtick-quoted path is unchecked at any depth. Three such paths dangled in
  one reference file for a full release cycle while the checker reported clean.

### Why this is parked rather than built

A survey (2026-08-27) found the ecosystem is early, and the parts that exist
either decline the job or are too thin to adopt:

- **The official reference validator declines it.** `skills-ref`, shipped with
  the agentskills specification, checks "that your SKILL.md frontmatter is
  valid and follows all naming conventions" — frontmatter and naming only, no
  file-reference validation. https://agentskills.io/specification
- **The specification's own examples sit in the blind spot.** It writes bundled
  resources as plain-text paths (`scripts/extract.py`), which is precisely the
  form no general checker reads. The encouraged style is the unchecked style.
- **General link checkers skip inline code on purpose.** lychee and
  remark-validate-links both parse `](target)` only, and the convention of
  ignoring backticked text is deliberate — code samples carry placeholder URLs
  that would false-positive. https://github.com/lycheeverse/lychee ·
  https://github.com/remarkjs/remark-validate-links
- **One third-party linter does target this exactly**: `skill-lint` checks
  "Markdown links, plus plain-text paths such as `scripts/extract.py`" against
  the filesystem. It is a solo project with no visible adoption.
  https://github.com/himself65/skill-lint
- **The defect class is not local to this repo.** A published full-corpus
  analysis using `skill-validator` reports broken links as the single most
  common error, 85 instances of which 33 were missing internal files.
  https://dacharycarey.com/2026/02/13/agent-skill-analysis/
- **The structural fix is proposed but unspecified.** Replacing path literals
  with resolvable names is on the table upstream and has not landed. Discussion
  #210 — a skill package manifest keying dependencies by git URL — is open with
  no adopted standard. Issue #178, the AgentFile proposal for declarative
  composition and filesystem-native delivery, was **closed as completed on
  2026-02-22** without producing a spec this repo could adopt; treat its closure
  as the proposal being taken off the table in that form, not as the trigger
  below having fired.
  https://github.com/agentskills/agentskills/discussions/210 ·
  https://github.com/agentskills/agentskills/issues/178

### If it is built here anyway

The hard part is not detection, which is a dozen lines. It is the false-positive
rate: a naive sweep of this repo's skill trees returned 234 unresolvable path
literals, and sampling showed the overwhelming majority are legitimate —
adopting-repo protocol paths (`docs/loom/PRINCIPLES.md`), grammar placeholders
(`<change-id>`, `YYYY-MM-DD`), cross-plugin named references
(`domain-teams:code-team/...`), and descriptive mentions ("that rule lives in
X") as opposed to imperatives ("read X"). The first three are rule-excludable;
the fourth needs judgment. Before writing one, read how `skill-lint` handles
that split — it is the only prior art that has faced it.

### Related

- `docs/loom/memory/a-path-literal-does-not-survive-being-copied-one-level-deeper.md`
  records the defect class and how #740's own reviewer reached the checker's
  blind spot by the checker's own reasoning.
