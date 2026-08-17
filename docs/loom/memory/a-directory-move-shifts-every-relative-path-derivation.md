---
name: a-directory-move-shifts-every-relative-path-derivation
description: Moving files one directory deeper silently breaks every `Path(__file__).parents[N]` chain in them — the derivation still resolves, just to the wrong directory, so no import fails and no grep for the old name matches; the 6→2 plugin merge hit this three separate times and only pytest ever surfaced it
type: gotcha
origin: loom-design-merge (6 plugins → 2 consolidation, parts 1-3, 2026-08-16/17)
---

The merge moved each retired plugin's scripts one level deeper:

```
OLD  loom-spec/scripts/validate_spec_output.py
NEW  loom-design/scripts/spec/validate_spec_output.py
```

Every path derivation inside those files was written against the OLD depth.
`SCRIPTS_DIR.parent` used to mean the plugin root; after the move it means
`loom-design/scripts/`. The correct depths for a file at
`loom-design/scripts/<subdir>/`:

| Expression | Resolves to |
|---|---|
| `parents[0]` | `loom-design/scripts/<subdir>/` |
| `parents[1]` | `loom-design/scripts/` |
| `parents[2]` | `loom-design/` — the PLUGIN root |
| `parents[3]` | the REPO root |

**Why it hides.** The derivation does not raise. It yields a path that is
merely wrong, and the failure surfaces far downstream as a
`FileNotFoundError` on a plausible-looking path, or as an `is_file()`
assertion that reads like a missing artifact rather than a bad derivation.
The tell is a path with a doubled segment — `loom-design/scripts/skills/...`
where `loom-design/skills/...` was meant. Worse, a build script's default
output path silently wrote the regenerated asset into a directory that did
not exist before the run created it.

**Why the migration greps missed it.** Every sweep in this arc searched for
retired plugin NAMES. A path-depth bug contains no name — it is arithmetic
over `__file__`. Three separate rounds of name-greps came back clean while
~40 derivations were still wrong.

**What actually found it.** Running the test suites. It hit three times:
`build_driver.py`'s `DEFAULT_OUT`, the drift test's `ASSET_PATH`, and the
build test's `REPO_ROOT` (that one needed three levels, not two — it reaches
the repo root, not the plugin root). Then ~40 more across the moved script
directories.

**Do this on any move that changes directory depth**: after the `git mv`,
grep the moved tree for `parents[` and `.parent` and re-derive each one from
what the variable is USED for, not from the number that was there — a
`REPO_ROOT` that is then joined with `"skills"` actually wants the plugin
root. Then run every affected suite; a name-grep cannot see this class at
all. Related: [[a-branch-suite-must-cover-every-touched-plugin-scripts-dir]].
