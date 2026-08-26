# Package-Resource Mode

Use this protocol only when the candidate changes a bundled resource as well
as, or instead of, `SKILL.md`. It keeps the entrypoint-mode Q2 threshold out
of package accounting: package mode measures the target file and the whole
package, so extracted prose is not counted as a saving.

## Safe candidate sequence

1. Before any candidate edit, export the Git-pinned baseline:

   ```sh
   python3 skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py export --repo <repo> --workspace <workspace> --skill-path <skill-path> --revision <revision>
   ```

   Retain the JSON `manifest` path returned by the command.
2. Create an **isolated candidate** by copying the exported baseline into a
   separate workspace. Edit only that copy; do not edit the user's worktree.
3. Verify the frozen baseline before comparing it:

   ```sh
   python3 skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py verify --manifest <manifest>
   ```

4. Account for the candidate's target and full package:

   ```sh
   python3 skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py account --manifest <manifest> --candidate-root <candidate-root> --target-file <target-file>
   ```

5. Run resource, owning-skill, then package evidence in that order. Submit
   the normalized evidence JSON to the reducer; add `--dual-host` when the
   package gate requires Claude and Codex replays:

   ```sh
   python3 skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py reduce [--dual-host] < evidence.json
   ```

   The CLI returns JSON and preserves the closed verdict vocabulary:
   `PASS`, `FAIL`, or `UNGRADABLE`. A host error is `UNGRADABLE`, never
   `PASS`.
6. Apply the isolated candidate to the user worktree only after a `PASS`.
   On `FAIL` or `UNGRADABLE`, discard the isolated candidate. Discarding that
   copy is the rollback; do not use `git revert` as package-mode evidence.

The `export`, `verify`, `account`, and `reduce` commands are stdlib-only
adapters over the tested package-gate APIs. They do not run paid host replays;
the caller supplies normalized host evidence to `reduce`.
