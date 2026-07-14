---
name: deploy-surface-ab-legs-run-post-merge
description: A/B legs that probe DEPLOYED surfaces (skill frontmatter descriptions, hooks, preload cards) via headless `claude -p` read the installed plugin cache, and the monkey-skills marketplace source is github:kouko/monkey-skills — `plugin update` pulls GitHub main, so a feature branch's B-leg pre-merge silently re-probes the OLD cache and reports a false no-regression; author such gates as explicit post-merge steps with review-side static diffs as the pre-merge guard
type: process
origin: feat/description-token-economy Task 8 relocation (2026-07-14), plan amendment in docs/loom/plans/2026-07-14-description-token-economy.md
---

The description-sweep plan authored its A/B regression gate (Task 8) as a
pre-merge step, assuming the firing harness saw the working tree. At
dispatch time this was refuted: `loom_firing_harness.py` shells bare
`claude -p` sessions whose skill descriptions come from the installed
plugin cache, and the marketplace updater resolves github main — a
feature branch cannot reach the cache without uninstall/reinstall
surgery. Running the B leg pre-merge would have compared old cache vs
old cache and passed vacuously.

**Why:** a vacuous no-regression pass is worse than no gate — it stamps
false confidence on exactly the change the gate exists to catch. The
failure is silent: the harness reports normally either way.

**How to apply:** when a plan's acceptance leg probes any deployed
surface (frontmatter description, hooks.json, SessionStart cards),
write it as an explicit POST-MERGE step: merge → device `plugin
update` → run the identical pinned method → regression = follow-up PR
reverting that one surface. Pre-merge safety comes from review-side
static checks instead (per-record corpus-intent diff, old-vs-new
trigger-set inventory). Same shape as the ascii-graph post-ship
telemetry pattern.
