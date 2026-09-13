# Loom

Three independently installable plugins share this repository:

| Plugin | Version | Skills | Agents | Purpose |
| --- | --- | --- | --- | --- |
| [`loom-code`](loom-code/) | 3.1.4 | 6 | 0 | Planning, implementation, review and publication. |
| [`loom-design`](loom-design/) | 2.1.5 | 5 | 0 | Intent, specification, product principles and visual design. |
| [`loom-workflow`](loom-workflow/) | 4.3.4 | 12 | 4 | Supporting workflow and repository memory tools, including `independent-advisor`. |

Each plugin retains its own manifest, version, tests and changelog. Read the
README inside each plugin for its capabilities and usage.

## Development

From the repository root, run the complete existing package inventory in an
isolated environment:

```sh
uv run --isolated --with-requirements requirements-package-tests.lock python scripts/run_package_tests.py --loom-family -q
```

CI selects the code, design, workflow-python and workflow-shell groups from
that same inventory. The shared manifest check is scoped to these three plugins:

```sh
python3 scripts/sync_codex_manifests.py --check --all
python3 scripts/check_plugin_boundaries.py loom-code
python3 scripts/check_plugin_boundaries.py loom-design
python3 loom-code/scripts/check-skill-crossrefs.py
```

The local marketplace at `.claude-plugin/marketplace.json` contains only these
three plugin roots. Existing upstream URLs inside plugin manifests remain
provenance links until publication and installation cutover are authorized.

## Migration provenance

This is a local candidate extracted from a fixed `monkey-skills` commit.
`docs/migration/extraction.json` records that commit, the reviewed path boundary
and verification counts. `docs/migration/commit-map.tsv` maps every original
commit reachable from that source to its rewritten commit, or a zero SHA when
the commit did not touch a retained path. The original filter-repo map is also
preserved as `docs/migration/filter-repo-commit-map.tsv`.

Currently committed tests also cite four development commits outside main's
ancestry, and the measurement gate cites one otherwise empty snapshot boundary
within main's ancestry. `docs/migration/auxiliary-history.json` enumerates those exact tips and
their retained citation paths. Their required ancestry is filtered under local
`refs/archive/loom-evidence/<original-sha>` refs and included in the complete
map. This preserves main history plus currently referenced Loom development
evidence; it does not import every abandoned branch.

Historical predecessor plugin directories remain in Git history. Current
development uses only the three plugin directories above. Rewriting changes
commit IDs and invalidates historical signatures; author and committer identity,
dates, messages and retained file trees are verified against the original.

The extraction does not configure a publishing remote. Repository publication,
marketplace cutover and removal of the original files are separate decisions.
