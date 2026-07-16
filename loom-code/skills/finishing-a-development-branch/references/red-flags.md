# Red Flags — refuse these rationalizations

Load when an agent (or the user) is pushing to skip a close-out gate. Each row: the rationalization → why it is one → the correct response. Default posture: refuse the shortcut, dispatch the gate it tries to bypass.

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Skip review, just push."* | Review-skip rationalization — same shape as `requesting-code-review`'s. | Refuse; dispatch requesting-code-review (Phase 1). If reviewer PASSes in 30 seconds, you lose 30 seconds; if NEEDS_REVISION, you gain a fix-before-prod. |
| *"Tests passed locally yesterday, skip the verification step."* | Code may have changed since yesterday. Test results have a half-life of "current uncommitted state". | Re-run verification-before-completion. |
| *"Don't bother with git-memory, message is obvious."* | P3-D MANDATORY — git-memory itself decides whether memory trailers are warranted. *"Message is obvious"* may be true (git-memory returns "no trailers needed for this routine commit"); the determination is the skill's job, not the user's pre-decision. | Invoke git-memory anyway. The skill outputs an empty trailer set for routine commits; the invocation itself is the discipline (audit trail of "we considered memory and decided no"). See git-memory §Invocation policy. |
| *"Auto-merge after push."* | Merge into main is a visible action with consequences for teammates. Always user-decision. | Push only; report PR URL if created. Let user merge via UI / explicit command. |
| *"Force-push to clean up history."* | Force-push to shared branches is destructive. Force-push to your own feature branch may be appropriate but always requires explicit user authorization. | Refuse unless user explicitly authorizes; warn about implications for any teammates with the branch checked out. |
| *"Just amend the last commit."* | Amend loses the previous commit's SHA → loses any in-flight reviews referencing that SHA. Per CLAUDE.md commit policy: *"Always create NEW commits rather than amending."* | Refuse; create new commit. |
| *"I already have a commit message from SDD."* | Per-task SDD commits cover per-task work. The close-out commit captures the full branch; its Decision/Learning/Gotcha trailers require a fresh git-memory call over the whole diff. | Invoke `dev-workflow:git-memory` (Skill call, not an orchestrator-composed message). Even if it returns no trailers ("routine commit"), the invocation is the audit trail. |
| 「review skip / 跳過審查」 | Same rationalization, localized. | Same refusal — dispatch requesting-code-review (Phase 1). |
