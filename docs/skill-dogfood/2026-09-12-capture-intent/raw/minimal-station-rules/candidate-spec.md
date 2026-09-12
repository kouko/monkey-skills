## Requirements

REQ-1 — Mute project activity emails  
  WHEN a user mutes one project, the system shall stop activity emails for that project → Acceptance #1

REQ-2 — Preserve other notifications and settings  
  WHILE a project is muted, the system shall leave in-app notifications and global settings unchanged → Acceptance #2

## Out of scope

This change does not design, implement, or verify unmuting a project.

## UI flows

### Project notifications

mutes one project → activity emails for that project stop; in-app notifications and global settings remain unchanged

## User confirmation

You mute one project and its activity emails stop, while in-app notifications and global settings remain unchanged. Is that right?
