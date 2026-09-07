# Branch-end fix round 6 — immutable push source RED

Target HEAD: `f50691d90407b0ab8fdcd630abd3d9222446d37d`.
Findings encoded: `branch-end-01`, `branch-end-04`.

The permanent regression is in
`loom-code/scripts/test_single_owner_push_gate.py`; the change-specific
`test_branch_end_attack_catalogue.py` invokes the same real replay. Production
checker code and station instructions remain untouched by this test commit.

## Targeted RED command

```sh
uv run --isolated --with pytest --with pyyaml python -m pytest loom-code/scripts/test_single_owner_push_gate.py docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_branch_end_attack_catalogue.py -q --tb=short -k 'refspec or network or concurrent or immutable'
```

Observed: **16 failed, 4 passed, 26 deselected in 54.04s**, exit **1**.
The two existing hook-boundary cases whose commands now use immutable
refspecs were checked separately with `-k 'selectedrepomutation or crossrepo'`:
**2 passed, 44 deselected in 6.07s**, exit **0**.

- Fourteen invalid refspec cases fail because the hook returns 0 and executes
  the package command. They cover missing source, branch/HEAD sources,
  abbreviated or non-current object IDs, abbreviated/wrong/tag destinations,
  deletion, all/mirror/tags modes, and a second mutable refspec.
- The permanent mutable-source replay and its change-specific counterpart
  fail because the actual remote receives the delayed, unvalidated commit.
- Two exact immutable-refspec hook cases pass (selected cwd and absolute
  `git -C`), observing the package command exactly once.
- Both actual immutable-source local bare-remote replays pass: HEAD moves
  after validation, but the published object stays the validated object.

## Exact RED excerpts

```text
E   AssertionError: unsafe refspec 'HEAD:refs/heads/work': hook rc=0
E     package-tests `python3 -c pass`: observed exit code 0 (recorded result: 'pass')
E   assert 0 == 2

E   AssertionError: mutable source published after hook return: {'hook_rc': 0, 'before': 'fea31f0a87fe53f882a9e4548c5b9eb3614129fa', 'after': '2cb0c409ccc74ed56e04f24e0c7f27a5bd4b838d', 'published': '2cb0c409ccc74ed56e04f24e0c7f27a5bd4b838d'}
E   assert (0 == 2)

E   AssertionError: {'hook_rc': 0, 'before': 'b0d55e74bd418429d2fb49173f318aeaa1d5f595', 'after': '3eaf84eb0354a9e60aed01d593497703381b57e8', 'published': '3eaf84eb0354a9e60aed01d593497703381b57e8'}
E   assert (0 == 2)

16 failed, 4 passed, 26 deselected in 54.04s
```

The object IDs above belong only to synthetic temporary fixture repositories.
The child announces readiness and waits for a release marker under `.git`.
The harness supplies that marker only after observing hook success, unchanged
HEAD, and clean porcelain. The child then commits and announces completion;
only then does the harness execute the exact intercepted refspec with real
`git push` to its temporary local bare remote and read back the remote ref.
Timeouts bound the handshake but do not determine the mutation order.

Expected implementation behavior: reject mutable, missing, and wrong refspecs
before any executable probes; accept the full current HEAD object ID paired
with the explicit current `refs/heads/<branch>` destination. The immutable
replay deliberately permits local HEAD to move after hook return while
requiring the published object to remain the validated object. It does not
claim process containment or prevention of all post-hook filesystem writes.

The old success-on-unsafe-mutation assertion has been replaced by required
hook rejection and absence of publication. No whole-package run is claimed;
this is the fix-round's targeted pre-implementation RED run.

Commit carrier privacy: deterministic scan exit 0 (`[]`); fresh-context judge
returned `verdict: PASS` and `findings: []` over the exact final carrier.
