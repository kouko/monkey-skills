# Proposal — PiP floating markdown note app (spec-expansion v0.2 dogfood)

> **Seed (verbatim, kouko 2026-06-12):** 一個可以顯示在其他全螢幕 app 上面、類 PiP 介面的簡單筆記軟體；筆記用 markdown（支援表格、codeblock、mermaid）；編輯是硬核的直接文字編輯 markdown，但帶自動完成與即時預覽；資料同步用 iCloud。
> **Coverage statement:** coverage relative to seed + 6 lenses + L2 (cross-object) + L3 (journey-nav); blind spots listed below. NOT complete.

— Phase ① USM backbone —

## USM backbone

Actors: **User** (note-taker) `seeded`; **SyncEngine** (iCloud agent acting on notes asynchronously) `inferred`.

Happy-path spine (forward edges):

| # | Stage | Actor · CTA | Objects co-active |
|---|---|---|---|
| S1 | **Summon PiP** — float the note window over the current fullscreen app | User · invoke/pin | PiPWindow, Note |
| S2 | **Select / create note** | User · open/create | Note (list), PiPWindow |
| S3 | **Edit & preview** (the core loop: type raw markdown → autocomplete → live render) | User · edit/complete/render | Editor, Autocomplete, PreviewPane, RenderedBlock, Note, SyncEngine |
| S4 | **Sync** — iCloud persists/reconciles | SyncEngine · upload/download/reconcile | Note, SyncEngine |
| S5 | **Reposition / dismiss PiP** | User · move/resize/close | PiPWindow, Note |

### Navigation graph (Phase ③c input)

Nodes = S1…S5. Typed edges beyond the forward spine:
- `back`: S3→S2 (return to note list mid-edit), S2→S1
- `skip`: S1→S3 (deep-link / hotkey straight into the last note)
- `abandon`: S3→(exit) (fullscreen app reclaims focus / user closes PiP mid-edit)
- `resume_reenter`: (exit)→S3 (re-summon the PiP later)
- `error_escape`: S3→conflict-view (sync conflict arrives mid-edit), S3→S3 (render error stays in place)
- `retry_self`: S4→S4 (sync upload failed, retry), S3→S3 (mermaid re-render on next keystroke)

— Phase ② OOUX object model —

## OOUX object model

*(Skill prescribes multi-agent fan-out per object; executed inline here — see dogfood note D-2.)*

| Object | Provenance | State machine (states → legal transitions) |
|---|---|---|
| **Note** | `seeded` (lifecycle `inferred`) | `new → editing → dirty → saving → saved → syncing → {synced, sync-conflict}`; `synced → editing`; `* → deleted` |
| **PiPWindow** | `seeded` | `hidden → floating-focused ↔ floating-unfocused`; `floating-* → {dragging, resizing} → floating-*`; `floating-* → pinned-over-fullscreen`; `pinned → occluded (a new fullscreen app covers it) → pinned`; `* → hidden` |
| **Editor** | `seeded` | `idle → typing ↔ selection`; `typing → autocomplete-open → {autocomplete-accepting → typing, dismissed → typing}` |
| **PreviewPane** | `seeded` | `rendered → stale → rendering → {rendered, render-error}`; `render-error → rendering` |
| **Autocomplete** | `seeded` | `closed → open-loading → {open-with-suggestions, open-empty} → {accepted → closed, dismissed → closed}` |
| **SyncEngine (iCloud)** | `seeded` | `up-to-date → uploading → {up-to-date, error}`; `up-to-date → downloading → {up-to-date, conflict}`; `* → offline → (reconnect) → up-to-date`; `error → (retry) → uploading` |
| **RenderedBlock** (table / codeblock / mermaid) | `inferred` | `source → rendering → {rendered, render-error}`; `rendered → source (edited) → rendering` |

— Phase ③ auto-expansion matrix —

## Path × edge matrix

Grid `backbone × object × CTA × state` pruned through the 6 lenses. Surviving high-priority paths/edges (illegal/redundant cells dropped):

| Lens (dominant) | KEEP (path) | FLAG (edge) | provenance |
|---|---|---|---|
| empty/error/loading | Preview renders table/codeblock/mermaid | **mermaid/markdown syntax error → inline render-error, editor stays editable** | `inferred` |
| empty/error/loading | Autocomplete shows suggestions | **autocomplete open-empty (no match) → dismiss quietly, no blocking popover** | `inferred` |
| empty/error/loading | Sync uploads on save | **sync offline → queue edit locally, badge "pending"; sync error → retry path** | `seeded` |
| state-transition | Note new→editing→saved→synced | **edit a note still `syncing` (in-flight) → defer/merge, don't drop keystrokes** | `inferred` |
| state-transition | — | **`deleted → editing` illegal → block; resurrect-or-discard prompt** | `inferred` |
| BVA | a nominal note renders | **empty note (0 bytes); very large note / huge mermaid block → render latency cap, async render** | `inferred` |
| permissions | signed-in iCloud syncs | **iCloud account signed-out / unavailable → degrade to local-only, surface "not syncing"** | `inferred` |
| NFR | PiP floats above normal windows | **PiP must stay above a *fullscreen* app (window level / Spaces / `canJoinAllSpaces`) — the core technical obligation; FLAG: unquantified, needs platform input** | `seeded` |
| NFR | live preview updates | **preview render must not block typing (debounce / background render); latency budget unquantified** | `seeded` |
| CRUD | create/open/edit/delete note | **no explicit delete-undo path in seed → FLAG coverage gap** | `inferred` |

— Phase ③b cross-object combinations —

## Cross-object combinations

**Interaction-density gate applied.** Stages judged:
- **S1 Summon** (PiPWindow × Note × Sync): interaction-dense → enumerate (3 objects, in-prompt).
- **S3 Edit & preview** (Editor × Autocomplete × PreviewPane × RenderedBlock × SyncEngine × Note): interaction-dense AND **wide (≥4 objects)** → reduce via `scripts/pairwise.py`.
- **S2 Select** (Note-list × PiPWindow): separable (list selection ≠ joint-dependent) → **skipped**, deferred to grid + critic.
- **S4 Sync** (Note × SyncEngine): 2-object but the reaction *is* joint (conflict) → enumerate.
- **S5 Reposition** (PiPWindow × Note): separable (window geometry independent of note state) → **skipped**.

### S3 Edit & preview — pairwise-reduced (wide stage)

Ran the 5 co-active objects' notable states through `scripts/pairwise.py`; the combinations whose **joint reaction ≠ union of individual reactions** (the ones that matter):

| # | Joint state | Required reaction (≠ union) | provenance |
|---|---|---|---|
| C1 | Editor=typing ∧ PreviewPane=render-error(bad mermaid) ∧ Sync=offline | Keep typing uninterrupted; show the render error **inline in preview only** (never a modal — a modal would break the PiP focus model); queue the edit for sync. The error must NOT block edit, and offline must NOT lose the buffer. | `inferred` |
| C2 | Editor=autocomplete-open ∧ PreviewPane=stale ∧ Sync=uploading | **Defer the live re-render while autocomplete is open** (don't reflow under the popover); resume render on accept/dismiss. Sync upload proceeds in background, no UI steal. | `inferred` |
| C3 | Note=sync-conflict ∧ Editor=typing | The hard one: remote conflict arrives **while the user is typing**. Do NOT overwrite the live buffer; keep local keystrokes authoritative, surface a non-destructive "remote version differs" affordance, reconcile on a deliberate user action — never auto-clobber. | `inferred` |
| C4 | Editor=typing ∧ RenderedBlock(mermaid)=rendering(slow) ∧ PreviewPane=stale | Large mermaid mid-render must not freeze the editor; render off the main thread, show a per-block "rendering…" placeholder, keep typing at 60fps. | `inferred` |

### S1 Summon — in-prompt (3 objects)

| # | Joint state | Required reaction | provenance |
|---|---|---|---|
| C5 | PiPWindow=pinned-over-fullscreen ∧ Sync=downloading ∧ Note=syncing | Show the note in a loading state **inside** the PiP **without stealing focus** from the underlying fullscreen app (the float appears, content fills in async). | `inferred` |
| C6 | PiPWindow=occluded (new fullscreen app covered it) ∧ Note=dirty | Re-assert window level to stay above the new fullscreen Space; if the OS forbids, badge "hidden behind <app>" and offer a re-summon hotkey — never silently lose the float. | `inferred` |

### S4 Sync — in-prompt (2 objects, joint)

| # | Joint state | Required reaction | provenance |
|---|---|---|---|
| C7 | Note=dirty ∧ SyncEngine=conflict | Conflict reconciliation: present both versions (local-dirty vs remote), default to non-destructive keep-both, never silently pick a winner. | `inferred` |

**Residue blind-spotted (not padded):** pairwise on S3 covers all *pairs* of co-active states but not every higher-order triple; a genuine 3-way interaction beyond C1–C4 (e.g. autocomplete-open ∧ conflict-arrives ∧ mermaid-rendering simultaneously) is **listed as a blind spot**, not fabricated.

— Phase ③c journey navigation —

## Journey navigation

0-switch coverage of the navigation graph — every typed edge walked once, reaction specified:

| Edge | Transition | Required reaction | provenance |
|---|---|---|---|
| `forward` | S1→S2→S3→S4→S5 | Standard advance; PiP summoned → note chosen → edited → synced → repositioned. | `seeded` |
| `back` | S3→S2 | Return to note list mid-edit: **autosave the dirty buffer first** (the edit must survive the navigation), then show the list; selecting back into the note restores cursor. | `inferred` |
| `skip` | S1→S3 | Hotkey/deep-link straight into the last-open note, bypassing the list; if no last note, fall through to S2 (don't open a blank broken editor). | `inferred` |
| `abandon` | S3→(exit) | User closes PiP / fullscreen app reclaims focus mid-edit: **autosave the dirty note** (never lose unsaved markdown), tear down the float cleanly, leave sync to finish in background. | `inferred` |
| `resume_reenter` | (exit)→S3 | Re-summon the PiP later: **restore the last note + cursor position + scroll offset**, re-check sync state on return (if a remote change landed while away, surface it before the user types over it). | `inferred` |
| `error_escape` | S3→conflict-view | A sync conflict arrives mid-edit: escape into a conflict-resolution view **without losing the live buffer**; resolving returns to S3 at the same cursor. | `inferred` |
| `error_escape` | S3→S3 (in place) | A render error (bad mermaid/markdown) does NOT escape the editor — stay in S3, show the error inline, keep editing. | `inferred` |
| `retry_self` | S4→S4 | Sync upload failed → retry in place with backoff; badge state, never block editing on it. | `inferred` |

**Critic deep-complement (handed to completeness-critic):** the exact *landing* of `resume_reenter` (cursor byte-offset vs logical position after a remote edit shifted the text) and *what* to restore on `back` (scroll vs selection vs fold state) are nuanced per-case judgments — flagged for the critic, not resolved here.

## Provenance

- `seeded`: PiP-over-fullscreen requirement, markdown (table/codeblock/mermaid), raw-edit + autocomplete + live-preview, iCloud sync, the 5-stage spine.
- `inferred`: all object state machines, the lifecycle of Note, every L2 joint combination (C1–C7), every L3 non-forward edge reaction, the lens FLAGs.
- `critic-found`: (none yet — completeness-critic has not run on this draft.)

## Blind spots — needs human/field input

1. **Platform feasibility of "above a fullscreen app"** — macOS fullscreen Spaces are hostile to floating windows; whether a non-Accessibility-API approach can keep the PiP above an *arbitrary* fullscreen app is an unresolved platform constraint, NOT specifiable here. (Highest-risk unknown.)
2. **iCloud conflict-resolution policy** — keep-both vs last-writer-wins vs field-merge is a product decision, not derivable from the seed.
3. **Higher-order (≥3-way) S3 interactions** beyond the pairwise-covered C1–C4 (residue from the pairwise reduction).
4. **`resume_reenter` cursor landing** after a remote edit shifted the buffer (deep per-case judgment).
5. **Autocomplete corpus** — what is completed (markdown syntax? note-link targets? snippet library?) is unstated in the seed.
6. **Mermaid/codeblock render engine** choice + its failure surface (sandboxing, perf cap) — unquantified NFR.
