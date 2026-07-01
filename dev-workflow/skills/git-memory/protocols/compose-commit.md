# Protocol: Composing a commit message with memory

When you are about to create a commit, follow this flow.

## Step 1 — Decide if this commit is memory-worthy

Ask yourself three filter questions. **Memory-worthy = any "yes".**

1. **Decision filter** — did this change make a non-obvious choice where
   the alternative was a real contender? (Not "add function X" — that's
   trivial. "Chose approach A over B because of Y" is.)
2. **Learning filter** — did the work reveal something a future reader
   would want to know? (Undocumented API behavior, surprising constraint,
   non-obvious interaction.)
3. **Gotcha filter** — is there a specific trap future self or others
   should avoid? (A failure mode we hit, an edge case, a policy limit.)

If all three answers are "no" → write a normal commit, no memory
trailers. This is the common case (roughly 70–80% of commits).

## Step 2 — Draft the body first (the WHY)

Write the body in prose, focused on **why**, not **what**. The diff
shows what. 72-char wrap. One paragraph is often enough; bullet lists
are fine for multi-aspect changes.

Anti-patterns to avoid in the body:

- Restating the diff ("added function foo to file bar")
- Listing files changed ("25 files, +2189 / −1775")
- Restating the subject in longer form

## Step 3 — Add trailers for the memory-worthy bits

Pick from the three trailer types. Use the minimum that captures the
signal; do not force all three.

### `Decision:`

One or two sentences answering: **why this approach, not the obvious
alternative?** Reference the alternative inline if it tightens the
reasoning.

```
Decision: Chose git-trailer-based memory over a separate MEMORY.md
  file because trailers survive squash-merge and are readable by
  any tool that understands git.
```

### `Learning:`

A surprise, constraint, or insight. Prefer concrete specifics over
general statements.

```
Learning: Google Auth Platform Console (2025-01 UI refresh) localizes
  to ブランディング / 対象 / クライアント in JP — keep untranslated
  in walkthroughs so users see the same strings.
```

### `Gotcha:`

A specific trap with enough context to recognize it. Include the
misleading surface feature, not just the correct answer.

```
Gotcha: gws flag `-s` is a service filter, not a scope specifier;
  use `--scopes=<URL>,<URL>` for scope elevation.
```

### `Related:`

Link to an earlier PR when the current commit builds on its context.

```
Related: PR #135
```

### `Supersedes:`

Use when this commit **reverses or replaces** a decision recorded
earlier. Because commit messages are immutable, the pointer lives on the
*new* commit and points backward; retrieval computes liveness from it
(`memory-grep.sh` hides superseded decisions unless `--history`).

```
Decision: switch to a single-pass parser after the two-pass approach
  blew the latency budget under load.
Supersedes: PR #135
```

- Prefer `PR #<N>`; a SHA works but gets rewritten by rebase/squash.
- **Validate before committing**: confirm the referenced PR/SHA exists
  and actually carries a `Decision:`/`Learning:`/`Gotcha:`. A pointer to
  nothing is a silently broken chain — the top failure mode of immutable
  decision logs. `memory-grep.sh --verify <ref>` is a quick
  existence-and-memory check, but it needs a **git-resolvable ref** — it
  cannot resolve `PR #135`, so resolve the PR to its merge/squash commit
  SHA first (e.g. `gh pr view 135 --json mergeCommit`) and verify that.

## Step 4 — Diagram, if change is architectural

If the change alters architecture, data flow, or state transitions,
consider adding an ASCII diagram to the commit body. Use ASCII, not
Mermaid, for commit messages (see `standards/memory-conventions.md`
§Diagram venue).

Skip the diagram for trivial changes.

```
       before                          after
     ┌───────────┐                   ┌───────────┐
     │ technical │──CJK mixed──────▶ │ technical │  EN-native
     └───────────┘                   └───────────┘
     ┌───────────┐                   ┌───────────┐
     │  design   │──ZH only────────▶ │  design   │  EN/JP/ZH anchors
     └───────────┘                   └───────────┘
```

## Step 5 — Confirm with user before finalizing

If you proposed adding memory trailers, briefly tell the user what you
are about to add and give them a chance to edit or veto:

> "I'm going to add `Decision:` + `Gotcha:` trailers about the gws
> scope-flag issue. OK to commit?"

If the user has been consistently writing memory trailers throughout
the conversation, you may commit without asking each time — but
surface any non-obvious memory judgments (e.g. classifying something
as a Decision vs a Learning).

## Quick reference — minimum viable memory commit

```
<type>(<scope>): <subject, imperative, ≤72 chars>

<one or two paragraphs of WHY, 72-char wrap>

Decision: <one or two sentences>
Learning: <one sentence>
Gotcha: <one sentence>
Related: PR #<N>
Co-Authored-By: Claude <version> <noreply@anthropic.com>
```

Omit any trailer that doesn't earn its line. A commit with only
`Decision:` + `Co-Authored-By:` is a valid memory-worthy commit.

## Anti-patterns

- **Filling all three trailers to look thorough** — each trailer must
  carry real signal; empty ritualism dilutes the grep output later
- **Restating the diff in a trailer** — if it's visible in the diff,
  it does not need a trailer
- **Vague trailers** — `Gotcha: Be careful with scopes.` is noise;
  specify the actual trap
- **Trailer chains referencing SHAs** — SHAs get rewritten by rebase;
  always use `Related: PR #N`, never `Related: abc1234`

## Escalation

If the change is so large that a single commit can't capture the
memory cleanly, that's a signal to split the commit. One decision per
commit scales better than one commit with five decisions crammed into
one `Decision:` trailer.
