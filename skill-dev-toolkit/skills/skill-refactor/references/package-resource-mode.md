# Package-Resource Mode

Use this protocol only when the candidate changes a bundled resource as well
as, or instead of, `SKILL.md`. It keeps the entrypoint-mode Q2 threshold out
of package accounting: package mode measures the target file and the whole
package, so extracted prose is not counted as a saving.

## Package Q2 — whole-package reduction

Q2 uses **whole-package words** from `account`, not a target-file count.

| Whole-package word reduction | Overall Q2 result |
|---|---|
| ≥10% | **PROCEED** when the other gates pass |
| 5–10% | **RESHAPE** only when the other gates pass; the user decides whether to keep the weak win |
| <5% or increase | **REJECT** |

Bytes are report-only: retain them for diagnosis, but do not use them for the
Q2 threshold. The reducer judges only **layered behavioral evidence**; it does
not decide Q2. The overall skill verdict consumes Q2 and the reducer verdict,
together with the normal Q1 and Q3 results, before it applies an
isolated candidate.

## Locate the bundled gate

Resolve `scripts/package_gate.py` relative to the loaded `skill-refactor` skill
directory into an absolute `<package-gate>` path before running this protocol.
Never derive this path from the target repository or current working directory,
and use no Claude-only environment variable or runtime dependency.

## Safe candidate sequence

1. Before any candidate edit, export the Git-pinned baseline:

   ```sh
   python3 "<package-gate>" export --repo <repo> --workspace <workspace> --skill-path <skill-path> --revision <revision>
   ```

   Retain both returned values: the JSON `manifest` path and the external
   manifest digest (`manifest_sha256`). Keep that digest outside the baseline
   directory as part of the immutable orchestration packet. Never recompute it
   from the manifest after export. Treat the returned path as the canonical
   manifest path; do not copy it, symlink it, or substitute an alias. Keep the
   original Git repository and pinned commit available through final
   verification. `verify` first checks the external manifest digest, then
   re-resolves the Git tree, so changing or repointing the exported files and
   their colocated manifest together cannot manufacture a passing baseline.
2. Create an **isolated candidate** by copying the exported baseline into a
   separate workspace. Edit only that copy; do not edit the user's worktree.
3. Verify the frozen baseline before comparing it:

   ```sh
   python3 "<package-gate>" verify --manifest <manifest> --manifest-sha256 <manifest-sha256>
   ```

4. Account for the candidate's target and full package:

   ```sh
   python3 "<package-gate>" account --manifest <manifest> --manifest-sha256 <manifest-sha256> --candidate-root <candidate-root> --target-file <target-file>
   ```

   Accounting consumes the verified snapshot captured during that same
   operation; it must not reread mutable baseline files after verification.

5. Run resource, owning-skill, then package evidence in that order. Submit
   the normalized evidence JSON to the reducer; add `--dual-host` when the
   package gate requires Claude and Codex replays:

   ```sh
   python3 "<package-gate>" reduce [--dual-host] < evidence.json
   ```

   The CLI returns JSON and preserves the closed verdict vocabulary:
   `PASS`, `FAIL`, or `UNGRADABLE`. A host error is `UNGRADABLE`, never
   `PASS`.
6. Combine the reducer result with Q1, whole-package Q2, and Q3. Apply the
   isolated candidate only after the overall `PROCEED` verdict. A `RESHAPE`
   remains isolated unless the user explicitly accepts the marginal reduction;
   record that acceptance as `PROCEED` before applying it. On `FAIL`,
   `UNGRADABLE`, or `REJECT`, discard the isolated candidate. Discarding that
   copy is the rollback; do not use `git revert` as package-mode evidence.

The `export`, `verify`, `account`, and `reduce` commands are stdlib-only
adapters over the tested package-gate APIs. They do not run paid host replays;
the caller supplies normalized host evidence to `reduce`.
