# OKF-compatible loom-memory
originator: kouko
kind: engineering
needs-design: yes — the memory lifecycle spans multiple operations and plugin installation states, and no current spec covers the independent OKF-compatible behavior
status: confirmed 2026-09-10

## Problem
`loom-memory` is useful to both `loom-code` and `loom-design`, but the current design ties memory recording to fixed Loom stages and keeps the store format inside `loom-code`. That makes an optional capability affect the core workflow, while the existing repository memory format has not been checked against the emerging Open Knowledge Format.

## Proposed outcome
Define `loom-memory` as an independently installable, passively triggered skill with a repository-owned memory store that follows an explicit OKF v0.2-compatible Loom profile. Both `loom-code` and `loom-design` can use it when installed, and continue normally when it is absent.

## Acceptance
1. A clean installation can verify whether a Loom memory store conforms to the declared OKF v0.2-compatible profile without requiring another Loom plugin.
2. An agent can discover relevant repository lessons through a small generated index and load only the selected entries.
3. An agent or user can recall, record, reconcile, and retire lessons without making memory a required Build, Review, or Ship stage.
4. `loom-code` and `loom-design` continue their normal work when `loom-memory` is not installed, the store is absent, or recall returns no match.
5. Existing repository memory entries can be migrated without losing their lesson, origin, index description, or Git history.
6. Structural corruption fails clearly inside an explicit memory operation while unrelated Loom work remains unblocked.

## Constraints
- Compatibility target is the published OKF v0.2 conformance contract, with Loom-specific fields and body sections added as permitted extensions.
- Keep the store as plain Markdown plus YAML frontmatter in Git; no hosted memory service, vector database, proprietary account, or required SDK.
- `index.md` provides progressive disclosure; `log.md` is omitted because Git history remains the update record.
- Memory activation is passive: explicit user requests, agent relevance judgment, or an optional memory-owned hook. No fixed-stage mandatory invocation.
- Hooks may remind or validate but must not autonomously author lessons or block unrelated Loom operations.
- The specification must preserve plugin filesystem boundaries and must not create a mandatory sibling-plugin dependency.
- Implementation, repository data migration, and publication up to an opened pull request with all required CI checks green are authorized (kouko, 2026-09-10, superseding the earlier intent-and-specification-only limit); merging the pull request remains outside this change.

## Out of scope
- Conversation-level personal memory or user-profile storage.
- Vertex AI Memory Bank or another managed retrieval service.
- Semantic embeddings, vector search, or a new runtime protocol.
- Full adoption of every optional OKF provenance, trust, lifecycle, or attestation field.
- Changing `git-memory` commit and pull-request trailer responsibilities.

## Open questions
- none
