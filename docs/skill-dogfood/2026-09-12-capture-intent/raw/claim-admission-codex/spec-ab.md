## B

### Requirements

**REQ-1 — Mute one project**  
WHEN a user mutes one project, the system shall stop that project’s activity emails.

**REQ-2 — Preserve in-app notifications**  
WHEN a user mutes one project, the system shall leave in-app notifications unchanged.

**REQ-3 — Preserve global settings**  
WHEN a user mutes one project, the system shall leave global settings unchanged.

### UI flows

- User mutes one project → activity emails for that project stop.
- After that project is muted → in-app notifications remain unchanged.
- After that project is muted → global settings remain unchanged.

### User confirmation

When you mute one project, activity emails for that project stop, while in-app notifications and global settings remain unchanged. Is that right?

## A

### Requirements

**REQ-1 — Mute one project**  
WHEN a user mutes one project, the system shall stop sending activity emails for that project.

**REQ-2 — Keep in-app notifications active**  
WHILE a project is muted, the system shall continue delivering its in-app notifications.

**REQ-3 — Keep global settings unchanged**  
WHEN a user mutes one project, the system shall not change the user’s global notification settings.

**REQ-4 — No unmute operation**  
WHILE a project is muted, the system shall not offer an operation to unmute it.

### UI flows

- User mutes a project → that project becomes muted and its activity emails stop.
- Muted project has new activity → no activity email is sent, but the in-app notification still appears.
- User checks global notification settings after muting a project → the settings remain as they were.
- User returns to the muted project → it remains muted and no unmute action is available.

### User confirmation

When you mute a project, that project becomes muted and its activity emails stop; its in-app notifications continue, and your global notification settings stay the same. The project remains muted because unmuting is not included. Is that right?
