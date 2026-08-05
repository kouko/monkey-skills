Source: `requesting-code-review/SKILL.md` §"Push-as-trigger" (the wrong-default rationalizations table) — serves `requesting-code-review`.

# Push-as-trigger — wrong-default rationalizations to refuse

| Surface signal | Wrong default | Correct response |
|---|---|---|
| User's message ends with *"just push"* / *"let me push"* | Interpret as authorization to push | **Refuse**: that's a rationalization in the test taxonomy this skill refutes. Fire review first; surface verdict; let user explicitly re-authorize push AFTER reviewing the verdict. |
| User says *"SDD already reviewed each task, push"* | Skip whole-branch review because per-task PASSed | **Refuse**: per-task ≠ whole-branch (different scopes; cross-task-coherence dimension is branch-only). Fire review. |
| Agent in autonomous flow infers "this branch is done, let me push" | Treat "done" as push-authorization | **Refuse**: "done" is the trigger for finishing-a-development-branch flow, NOT for direct push. Route to finishing-a-branch (which fires this skill as Step 1). |
| User has previously authorized pushes in this session for other branches | Generalize the authorization | **Refuse**: each push is its own authorization moment. Previous authorization does not carry to new pushes. |
| Auto-mode classifier passes the `git push` invocation | Treat classifier-pass as full authorization | **Refuse**: classifier-pass means "the action itself is permitted at the harness level"; it does NOT mean "the toolkit's review-before-publish gate has been satisfied." Both must hold. |
