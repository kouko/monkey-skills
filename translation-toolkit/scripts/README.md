# translation-toolkit / scripts

Build-time tooling for the **SSOT-and-functional-copy** pattern (TECH-SPEC Decision #14).

## Why this exists

Anthropic's skill spec says each skill folder must be self-contained — a skill can only `Read` files **inside its own directory** at runtime. We have shared knowledge (the 4D loop, glossaries, JLReq summary, NICT corpus notes) that all four active translation skills need verbatim. Two ways to solve that:

1. **Symlink** every skill's `references/foo.md` to a single source. Works on disk but breaks under archive / CI / non-POSIX consumers and silently leaves dangling pointers when the skill is published as an artifact.
2. **Bundle a functional copy in every skill, kept byte-identical to a single source of truth via build tooling.** The pattern used by `dev-workflow:complexity-critique` (memory: SSOT-and-functional-copy v1.5.0).

We use option 2.

## Layout

```
translation-toolkit/
├── scripts/
│   ├── canonical/                     # ← single source of truth (you edit these)
│   │   ├── core-loop.md
│   │   ├── 4d-reflection.md
│   │   ├── 5d-effectiveness.md
│   │   ├── orthogonal-axes.md
│   │   ├── verification-gates.md
│   │   ├── audit-trail-spec.md
│   │   ├── glossary-en-US--ja-JP.md   (Phase B)
│   │   ├── jlreq-summary.md           (Phase B)
│   │   └── nict-en-ja-zh.md           (Phase C)
│   ├── distribute.py                  # canonical → functional copies
│   ├── verify-drift.py                # CI drift detector
│   ├── README.md                      (this file)
│   └── tests/                         # pytest unit tests for both scripts
├── translation-i18n/
│   ├── references/<file>              # ← byte-identical functional copy (DO NOT EDIT)
│   ├── glossary/<file>
│   ├── typography/<file>
│   └── corpus/<file>
├── translation-doc/        (same shape)
├── translation-creative/   (same shape)
└── translation-audit/      (same shape)
```

## Routing rules

`distribute.py` routes by filename:

| Canonical filename pattern             | Target subfolder    |
| -------------------------------------- | ------------------- |
| `core-loop.md`, `4d-reflection.md`, `5d-effectiveness.md`, `orthogonal-axes.md`, `verification-gates.md`, `audit-trail-spec.md` | `references/`       |
| `jlreq-summary.md`, `clreq-summary.md`, `requirements-for-japanese-text-layout-summary.md` | `typography/`       |
| `nict-en-ja-zh.md`, `opus-en-zh-tw.md`, `wmt-*.md` | `corpus/`           |
| `glossary-<srcLocale>--<tgtLocale>.md` | `glossary/`         |
| `manual-entries-<src>--<tgt>.md`       | **NOT distributed** (per-skill authored, not SSOT) |
| anything else                          | warn `WARN unrouted: <name>` (no copies written) |

If you add a new canonical file with a name not yet routed, edit `REFERENCE_FILES` / `TYPOGRAPHY_FILES` / `CORPUS_FILES` / `GLOSSARY_PREFIX` in `distribute.py` to claim the routing — don't silently leak the warning.

## Workflow

```
1. Edit scripts/canonical/<file>.md
2. python3 scripts/distribute.py        # rewrites all functional copies
3. python3 scripts/verify-drift.py      # sanity-check (must print OK)
4. git add scripts/canonical/<file>.md translation-*/
5. git commit                           # canonical + 4 functional copies in one commit
```

**Commit rule**: never commit the canonical edit without the functional-copy refresh — CI will fail. Never edit a functional copy directly under `translation-*/<sub>/<file>.md` — your edit will be wiped on the next `distribute.py` run.

## CI gate

`.github/workflows/translation-toolkit-ci.yml` (or repo-level CI lane) runs:

```bash
python3 translation-toolkit/scripts/verify-drift.py
```

Exit code:
- `0` → all functional copies byte-identical to canonical.
- `1` → at least one drift (file missing or differs); CI blocks merge.

## Required tools

- Python 3.9+ (stdlib only — `shutil`, `filecmp`, `pathlib`)
- `pytest` (for `scripts/tests/`)
- No third-party deps

Tests: `cd translation-toolkit && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts/tests/ -v`

(`PYTHONDONTWRITEBYTECODE=1` avoids `__pycache__/` folders inside skill subtrees, which would trip `validate-skill-folder-structure.sh`.)
