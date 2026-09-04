# Product principles interview (runs inside decision point ①; no separate stop)

Opening line (translate into the user's language; the meaning is fixed, the words are not): "Before building a product feature, this repo needs a set of product principles first. I'll ask you a few questions to produce it (about ten minutes), then confirm it together with the intent."

Keep asking until it's clear; each question stays in plain language, with no mechanism jargon.
1. Who is this product for? How do they solve this today?
2. What's the one thing about the experience that can't be compromised (fast, accurate, cheap, private, offline, good-looking)? Rank them.
3. Is there anything explicitly "won't do"?
4. What's the worst outcome if this goes wrong? Who gets hurt?
5. Is there anything already decided that can't change (platform, language, paid service, data format)?

Produce `PRINCIPLES.md`:
```
# Product principles
ratified-by: <name> <date>      # written by the agent after the user confirms
## Who
## Non-negotiables (ordered)
## Won't do
## Failure we must avoid
## Fixed choices
```
Recap it together with the intent for the user; when the user says "yes" — write `ratified-by`.
