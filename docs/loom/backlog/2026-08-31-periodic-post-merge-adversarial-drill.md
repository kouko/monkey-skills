---
name: 2026-08-31-periodic-post-merge-adversarial-drill
description: A scheduled GameDay-style adversarial run of the audit packet against main, complementing the pre-merge-only adversarial-audit-station
status: open
origin: 2026-08-31 — adversarial-audit-station arc (docs/loom/specs/2026-08-31-adversarial-audit-station.md `## Out of Scope`), deferred from BI-11's scope
start: event — a finding is reproduced against `main` outside any plan-triggered Step 3.5 run (i.e. a hole shipped through a change that never tripped the `safety-bearing`/guarded-path signal), showing the pre-merge-only trigger has a coverage gap a periodic drill would catch
---

`loom-code:adversarial-audit-station` (Step 3.5 of
`finishing-a-development-branch`) is trigger-gated and pre-merge only: it
runs when a plan carries `safety-bearing: yes` or touches a guarded path,
and it runs against the branch under review, never against `main` on a
schedule. That leaves two gaps the station does not cover by design: a
change that should have tripped the trigger but didn't (a misjudged
`safety-bearing` flag, or an untouched-but-vulnerable guarded path), and
drift — a combination of several individually-reviewed merges that
together open a hole none of them showed alone.

A periodic post-merge drill (GameDay-style: same attack-packet shape,
run against `main` on a schedule rather than against a branch on a
trigger) is the industry-standard complement to pre-merge gating — see
PCI-DSS 4.0's "annually and after significant change" cadence
(https://www.sherlockforensics.com/blog/pci-dss-4-pentest-requirements.html)
and chaos-engineering GameDay practice. It was considered and rejected
for this arc (`2026-08-31-adversarial-audit-station.md`, Alternative
(b)) specifically as the *primary* mechanism — post-merge is after
publication for a marketplace plugin — but nothing in that decision rules
out running it *in addition* to the pre-merge station, as a periodic
backstop against the two gaps above.

Next step: decide cadence and ownership (who dispatches it, on what
schedule, against which repos) before scoping a brief; this entry only
records that the gap exists and that no mechanism currently fills it.
