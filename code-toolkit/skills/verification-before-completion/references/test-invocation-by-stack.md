# Test invocation by stack — canonical commands

> Companion to [`../SKILL.md`](../SKILL.md). The canonical package-level test command per language / build tool, plus detection signals so the agent picks the right command without asking.

## Priority 0 — consult the project-declared surface first

Before falling back to signal detection, consult the project-declared surface first: check the `AGENTS.md` commands section, `make`/`just` `test` recipes, and README commands. Prefer a declared **granular `test` verb** over a bundled `check` that mixes lint and tests.

**Trust earned by execution, not granted by source.** A declared verb outranks detection only if it runs and emits a test count (`N passed`, N>0) **on a clean, test-only signal**. A verb whose output **interleaves other tooling with the test run** — a bundled `check`/`test` recipe that runs lint+typecheck+tests together — is **signal-opaque**: a count appearing *somewhere* in the mixed output does NOT qualify it, because the interleaving defeats vbc's "0 tests ran / N passed" defense. When the declared verb is signal-opaque, prefer the **granular `test` verb**; if a granular runner is independently detectable (e.g. `pytest` via `pyproject.toml`), run it directly rather than the bundled recipe. Fall back to the signal-detection table only when no granular verb resolves at all, or the declared verb fails to run. Never hard-fail on a broken declaration; never use a signal-opaque bundled `check` as the gate — granular `test` only.

Resolution order:

1. **Consult declared surface** — `AGENTS.md` commands section, `make`/`just` `test` recipe, README. Pick the most granular `test` verb available.
2. **Earn trust by execution** — the declared verb wins only if it runs and emits a test count (N > 0) from clean, test-only output. If it errors, produces no parseable count, **or interleaves lint/typecheck with the test run (signal-opaque)**, prefer a granular `test` verb (run an independently-detectable runner like `pytest` directly), else proceed to step 3.
3. **Fall back to detection** — apply the signal → command table below as the fallback, not the default.

> **Note on `Makefile`/`justfile` `test` recipes**: the "Generic" rows at the bottom of the table (`make test`, `just test`) are also valid *declared-surface* entries at priority 0 — not only lowest-priority fallbacks. If a `Makefile` or `justfile` `test` recipe is present and runs successfully, treat it as a priority-0 declared verb, subject to the same execution-earns-trust rule above.

## Detection signals → command table

If no declared surface resolves (priority 0 above), detect by signal files at project root. If multiple signals match (monorepo / polyglot repo), the user must specify which package to verify; the skill cannot guess.

| Signal file | Language / runtime | Canonical command | Notes |
|---|---|---|---|
| `package.json` with `scripts.test` | JS / TS (Node) | `npm test` / `pnpm test` / `yarn test` (per lockfile present) | Lockfile tells you the package manager — `package-lock.json` → npm; `pnpm-lock.yaml` → pnpm; `yarn.lock` → yarn |
| `package.json` no `scripts.test` but has dev-dep `vitest` | JS / TS (Vitest) | `npx vitest run` | `run` (not watch mode) for CI-equivalent invocation |
| `package.json` no `scripts.test` but has dev-dep `jest` | JS / TS (Jest) | `npx jest` | Default config picks up `*.test.ts` etc |
| `pyproject.toml` with `[tool.pytest.ini_options]` OR `pytest.ini` OR `conftest.py` | Python (pytest) | `pytest` | Run from project root; pytest auto-discovers |
| `pyproject.toml` with `[tool.poetry]` and pytest dev-dep | Python (Poetry + pytest) | `poetry run pytest` | |
| `pyproject.toml` with hatch / pdm | Python | `hatch run test` / `pdm run pytest` | |
| `tox.ini` | Python multi-env | `tox` | Runs all configured envs; for one env: `tox -e py311` |
| `setup.py` no pyproject.toml | Python (legacy) | `python -m pytest` or `python setup.py test` | `setup.py test` is deprecated; prefer pytest |
| `go.mod` | Go | `go test ./...` | `./...` runs all packages recursively; without it, only current dir |
| `Cargo.toml` | Rust | `cargo test` | Includes unit + integration + doc tests |
| `Gemfile` + `spec/` dir | Ruby (RSpec) | `bundle exec rspec` | |
| `Gemfile` + `test/` dir | Ruby (Minitest) | `bundle exec rake test` | |
| `pom.xml` | Java (Maven) | `mvn test` | |
| `build.gradle` / `build.gradle.kts` | Java / Kotlin (Gradle) | `./gradlew test` | Gradle wrapper preferred over global `gradle` |
| `*.csproj` / `*.sln` | C# / .NET | `dotnet test` | |
| `mix.exs` | Elixir | `mix test` | |
| `composer.json` with phpunit | PHP | `vendor/bin/phpunit` OR `composer test` (if script defined) | |
| `Package.swift` | Swift | `swift test` | |
| `dub.json` / `dub.sdl` | D | `dub test` | |
| `pubspec.yaml` | Dart / Flutter | `flutter test` (Flutter) or `dart test` (pure Dart) | |
| `BUILD.bazel` / `WORKSPACE` | Bazel (any language) | `bazel test //...` | |
| `Makefile` with `test:` target | Generic | `make test` | Convention; verify the target actually runs tests not just lint |
| `justfile` with `test:` recipe | Generic | `just test` | |

## Monorepo handling

If multiple signal files exist in subdirectories (`packages/foo/package.json`, `packages/bar/pyproject.toml`):

- **For touched-package verification**: detect which packages contain files in the diff; run each package's command from that package root.
- **For whole-monorepo verification**: use the monorepo runner if one exists (`nx test`, `turbo test`, `bazel test //...`, `lerna run test`); otherwise iterate per-package.

The user must clarify scope if the diff touches multiple packages and no monorepo runner is configured.

## Detecting "0 tests ran" — exit 0 is not enough

Exit code 0 with zero tests is a configuration bug, not a pass. Each runner has its own way to report this:

| Runner | "Tests ran" signal in output |
|---|---|
| npm / pnpm / yarn test (via vitest / jest) | Summary line: `Tests: N passed, N total` — N > 0 required |
| pytest | `===== N passed in T s =====` — N > 0 required |
| go test ./... | `ok <pkg>` for each tested package; if all show `[no test files]`, that's the bug |
| cargo test | `test result: ok. N passed; ...` — N > 0 required |
| rspec | `N examples, 0 failures` — N > 0 required |
| dotnet test | `Passed!  - Failed: 0, Passed: N` — N > 0 required |

If the runner reports 0 tests ran, the verification has not happened. Treat as failure, surface to user.

## Slow-suite handling — IS NOT a reason to skip

If the suite takes >10 minutes, do NOT skip; investigate via [`../../systematic-debugging/references/condition-based-waiting.md`](../../systematic-debugging/references/condition-based-waiting.md) §"Bisecting a heisenbug" + general slow-suite isolation (parallel test runner, find the 80/20 slow tests, fixture caching).

In the meantime, the package-level run is still required. Options:

1. **Run scoped subset locally** as a pre-flight (`pytest tests/touched_module/`), THEN run full suite once at end-of-branch. Don't conflate the scoped run with verification.
2. **Run full suite in background** while doing other work; check exit code before declaring done.

What you do NOT do: skip the full suite and trust the scoped run. The interaction-bug failure mode that this skill catches only shows in the full run.

## Test-runner-specific gotchas

- **vitest / jest**: `--watch` does not exit; use `run` / no-watch for verification.
- **pytest**: `-x` stops at first failure (good for fast feedback during debug; bad for verification — you want to know ALL failures). Use neither for verification.
- **go test**: `-short` flag may skip long-running tests; for verification, run without `-short`.
- **cargo test**: doc tests are slow and sometimes skipped in CI; for verification, do NOT skip (`--doc` runs doc tests; default runs unit + integration; for full coverage run both).
- **gradle / maven**: incremental build caching can mask "tests didn't actually rerun"; for clean verification use `clean test`.

## See also

- [`../SKILL.md`](../SKILL.md) — the HARD-GATE this command table serves.
- [`../../tdd-iron-law/SKILL.md`](../../tdd-iron-law/SKILL.md) — the discipline that creates the tests this command runs.
- [`../../systematic-debugging/references/condition-based-waiting.md`](../../systematic-debugging/references/condition-based-waiting.md) — when the suite is slow-but-not-broken, isolation protocol.
