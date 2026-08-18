---
name: a-skill-that-takes-a-folder-must-say-it-owns-intake-or-the-router-explores-the-folder-first
description: When a user request names a folder ("think about X, sources in ./y"), the router's first move is to inspect the folder and ask, not to load the skill — unless the skill's description says explicitly that it owns intake and must be invoked before any folder is inspected; the same shape hides a second gap: a verb skill that presumes existing project state (break-assumption) never fires standalone unless the entry skill lists its phrases as its own triggers and hands off
type: practice
origin: think-orbit dogfood 2026-08-18 — Probe A (27 queries × 2, real harness): every folder-mentioning query 0/14, assumption-broke queries 0/8, precision perfect; after adding "invoke first — before inspecting any folder — it owns intake" and the assumption-broke phrases to the router description (0.1.2), the same queries went 1/26 → 22/26 with 0 over-triggers
---

A router deciding between "run a tool on this folder" and "load a skill"
picks the folder when the request names one, because inspecting a path is
the cheapest first move and nothing in the description told it the skill
would do that itself. Verb skills that only make sense over an existing
project (mark an assumption broken) look inapplicable when no project
state is visible, so the phrase that should trigger them gets answered as
"no context".

**Why:** trigger phrases alone describe *what* a skill is for; the router
also weighs *what to do first*. If the description is silent on intake
ownership, the model's own default (look at the folder) wins, and the
skill is never consulted.

**How to apply:** for any skill whose requests can carry a path, put an
ownership sentence in the description ("invoke before inspecting any
folder the user names — this skill owns intake"); for verb skills that
presume state, list their phrases in the entry skill's description too and
let the entry skill hand off. Measure with the dogfood activation probe
(≥2 runs per query, folder-mentioning and stateless-verb queries included)
— static description review cannot see the router's first move.
