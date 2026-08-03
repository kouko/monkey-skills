## ADDED Requirements

### Requirement: Float above fullscreen apps without stealing focus
The system MUST display the note window above an active fullscreen application without taking keyboard focus from it until the user interacts with the note.

#### Scenario: Summon over a fullscreen app
- GIVEN another app is in fullscreen and focused
- WHEN the user invokes the PiP note window
- THEN the note floats above the fullscreen app AND the fullscreen app keeps focus until the user clicks into the note

#### Scenario: A new fullscreen app occludes the float
- GIVEN the note is pinned over a fullscreen app and the note is dirty
- WHEN a different app enters fullscreen and covers the note
- THEN the system re-asserts the window level to stay above, or if the OS forbids it, badges "hidden behind <app>" and offers a re-summon hotkey — the dirty note is never silently lost

### Requirement: Editing never blocks on preview or sync
The system MUST keep the raw-markdown editor responsive while preview rendering and iCloud sync proceed in the background.

#### Scenario: Mermaid render error while offline
- GIVEN the user is typing and iCloud is offline
- WHEN the markdown contains an invalid mermaid block
- THEN the editor stays fully editable AND the render error is shown inline in the preview only (not a modal) AND the edit is queued locally for later sync

#### Scenario: Live preview defers under autocomplete
- GIVEN the autocomplete popover is open
- WHEN the preview would re-render from the in-progress edit
- THEN the live re-render is deferred until autocomplete is accepted or dismissed, so the layout does not reflow under the popover

### Requirement: No unsaved edit is lost on navigation or dismissal
The system MUST persist the in-progress buffer before any back-navigation, abandonment, or PiP teardown.

#### Scenario: Close PiP mid-edit
- GIVEN the note is dirty and unsaved
- WHEN the user closes the PiP or the fullscreen app reclaims focus
- THEN the dirty buffer is autosaved before teardown AND sync finishes in the background

#### Scenario: Re-summon restores context
- GIVEN the user previously closed the PiP while editing a note
- WHEN the user re-summons the PiP
- THEN the last note, cursor position, and scroll offset are restored AND if a remote change landed while away it is surfaced before the user types over it

### Requirement: Remote sync conflicts never clobber the live buffer
The system MUST treat the local in-progress edit as authoritative when a remote iCloud conflict arrives, and reconcile only on a deliberate user action.

#### Scenario: Conflict arrives while typing
- GIVEN the user is actively typing in a note
- WHEN iCloud reports a remote version conflict for that note
- THEN the local keystrokes are preserved AND a non-destructive "remote version differs" affordance is shown AND no automatic overwrite occurs
