---
title: OOUI and Object Modeling
tier: 2
---

# OOUI and Object Modeling

Canonical anchor for Object-Oriented UI design and the OOUX / ORCA
framework. Tier 2: cold-query LLMs routinely conflate the 2015 *A List
Apart* article with the full ORCA 4-step process, and rarely surface
the co-canonical JP synthesis 上野 2020. The body spells out ORCA and
flags the source split.

## Primary Sources

- 上野学・ソシオメディア・藤井幸多 (2020) 『オブジェクト指向 UI デザイン—使いやすいソフトウェアの原理』. 技術評論社. JP-original canonical synthesis; 18 workouts + theory chapters.
- Sophia V. Prater (2015-10-20) "Object-Oriented UX". *A List Apart*. https://alistapart.com/article/object-oriented-ux/. Origin article; introduces OOUX philosophy and the 4-step object-extraction workflow. Does **not** contain ORCA.
- Sophia V. Prater (2016-04-19) "OOUX: A Foundation for Interaction Design". *A List Apart*. https://alistapart.com/article/ooux-a-foundation-for-interaction-design/. Adds CTA Inventory but still not full ORCA.
- Sophia V. Prater "What is OOUX? The ORCA Process". https://ooux.com/what-is-ooux. Canonical source for the full ORCA 4-step framework (Objects / Relationships / CTAs / Attributes) — the 2015 and 2016 ALA articles are not sufficient for ORCA.

## Philosophy: Noun-First, Verb-Second

OOUI designs the interface around **objects** (nouns the user cares
about) first, then exposes **actions** (verbs) as operations on those
objects. 名詞を先に、動詞を後に. A task-based UI asks "what flow is
the user in?"; an object-based UI asks "what object is the user
looking at, and what can they do to it right now?".

This inversion matters because task-based UIs tend to silo state per
flow ("book a flight" flow does not share context with "check status"
flow), while OOUIs let users pivot freely between related objects
because the system is modelled as a graph of objects, not a tree of
tasks.

## Object Views Lifecycle

An object's journey through the UI follows a consistent pattern:

1. **Collection view** — a list or grid of objects of a single class
   (e.g., an Inbox, a search-results page, a product catalogue).
2. **Single Object view** — the full representation of one specific
   object with all its attributes and primary actions.
3. **Detail / nested object view** — a related object drilled into
   from the Single Object view (e.g., a comment on an article, a line
   item on an order).

Navigation is object-to-object, not task-to-task: from a Single
Object view, users can pivot to related objects by following
relationships, not by dropping back into a separate task flow.

## Object Relationships

Model relationships between object classes explicitly. Short example:

- `Author has-many Article`
- `Article has-many Comment`
- `Comment belongs-to Author` (commenter)
- `Comment belongs-to Article`

OOUI surfaces these relationships as **navigable links** — an Article
view includes a link to its Author, a Comment view includes a link to
the commenter and to the parent Article. Do not hide relationships
behind separate task flows; they are part of the object model.

## The ORCA 4-Step Framework (load-bearing spell-out)

ORCA is Prater's mature process on ooux.com; it is NOT fully present
in the 2015 or 2016 ALA articles, which is why cold-query recall often
gets the step list wrong.

1. **Objects** — enumerate the nouns the user cares about. Extract
   from user goals, not from existing screens. Ask: "what are the
   things in this world?"
2. **Relationships** — map how objects connect. Enumerate has-many,
   belongs-to, and references relationships between object classes.
   The output is an object-relationship diagram.
3. **CTAs (Calls-to-Action)** — list the verbs users perform on each
   object. CTAs are object-scoped (verbs attached to a specific
   object class), not flow-scoped.
4. **Attributes** — enumerate the data each object carries. Separate
   **display attributes** (what the user sees) from **structural
   attributes** (what the system needs for relationships, sorting,
   filtering).

ORCA is iterative: new objects surface during the Relationships step;
missing CTAs surface during the Attributes step. Do not treat ORCA as
a one-pass waterfall.

## OOUI vs Task-Based UI — Contrast

| Dimension | Task-based UI | OOUI |
|---|---|---|
| Organizing principle | Flows ("book a flight", "check status") | Objects (Flight, Booking, Traveler) |
| Navigation | Task entry points | Object pivots |
| State scope | Per-flow silo | Shared object graph |
| Verbs | Flow-specific | Object-contextual |
| New feature cost | New flow + new entry point | New verb on existing object |

Task-based UI is still appropriate for **one-shot, rarely-revisited
operations** (set up a new device, run a background migration) where
there is no meaningful object the user returns to. Mixed products use
both — task flows as discrete wizards, object views for everything
else.

## Co-Canonical Note

上野 2020 is the JP-original synthesis and is **co-canonical** with
Prater 2015 / 2016 — it is NOT a Japanese translation of Prater.
Both traditions should be cited together when OOUI / OOUX is invoked
as a design-team standard.
