# Write Tutorial Protocol (Diátaxis: Tutorial Quadrant)

Write a **learning-oriented** document. Hand-holding. Guaranteed success.
The reader is a beginner who follows every step and ends with a concrete
achievement.

**Vocabulary reference**: `standards/diataxis-taxonomy.md` §Tutorial
**Style reference**: `standards/style-conventions.md`
**Pre-writing reference**: `standards/pre-writing-checklist.md` — apply before Phase 0

## Tutorial vs Other Modes

| This mode | NOT this mode |
|-----------|---------------|
| Teach by doing | Teach by lecturing (→ Explanation) |
| Sequential, no branching | Recipe for a specific problem (→ How-to) |
| Guaranteed success path | Exhaustive coverage (→ Reference) |
| Beginner-friendly | Expert reference (→ Reference) |

## Phase 0: Context Discovery

Before writing:

1. **Confirm the starting state** — what does the reader have when they begin?
   (fresh install, empty project, specific version installed, prior tutorial completed)
2. **Confirm the target state** — what concrete achievement should the reader
   reach? ("You have a running hello-world app", not "You understand the API")
3. **Budget the path length** — a good tutorial takes 15-60 minutes. If it's
   longer, split into a tutorial series.
4. **Verify executability** — can a real beginner complete every step in the
   stated time on a real machine? If not, the tutorial is broken.

## Phase 1: Design the Minimum Success Path

1. List every step from starting state to target state
2. **Cut every step that is not strictly necessary** — tutorials are ruthlessly
   minimal. If a step is "good to know" or "in case you want to", cut it.
3. Verify each step **only has one correct outcome** — no branches, no "if you
   see X do Y, if you see Z do W". Branches go in How-to guides.
4. Verify the starting state is **exactly reproducible** — pinned versions,
   explicit prerequisites, no "install the usual tools".

## Phase 2: Write Steps

For each step:

1. **Tell the reader what they will do** (one sentence)
2. **Show them the command or action** (code block or screenshot)
3. **Tell them what to expect** (the observable output)
4. **Mark the checkpoint** — "You have now..."

Use second person, imperative, present tense (per `standards/style-conventions.md`).

Example step:

```markdown
### Step 3: Create your first config file

Create a file called `config.yaml` in the project root:

​```yaml
name: my-project
version: 1.0.0
​```

You should see the file appear in your project root. You have now
initialized the project configuration.
```

## Phase 3: Success Checkpoints

A tutorial should include a success checkpoint roughly every 5-10 minutes of
reading or ~3-5 steps. Each checkpoint:

- Confirms what the reader has accomplished in plain language
- Verifies observable state ("Run `ls` and you should see...")
- Gives the reader a moment of pride before the next challenge

## Phase 4: The Conclusion

End with:

1. **What you did** — recap the concrete achievement
2. **What you learned** — 2-3 high-level takeaways
3. **Where to go next** — link to one How-to guide OR one Explanation, not both

Do not end with "here are 10 things you could explore next." Tutorials are
focused; exploration belongs in How-to and Reference.

## Rules

- **No branching.** One path, one success.
- **No "advanced" sections.** If a topic is advanced, it's a different tutorial.
- **No "alternatively, you could".** If there's a choice, the tutorial writer
  makes it for the reader.
- **No "for more detail, see...".** Tutorials stand alone until the conclusion.
- **Every code block must run.** Copy-paste the full tutorial from the doc to
  a clean environment and verify it works end-to-end before publishing.
- **No theory.** If you catch yourself explaining why something works, move
  that explanation to an Explanation doc and link from the conclusion.

## Output Structure

```markdown
---
title: {Tutorial title — "Your first <thing>"}
last_reviewed: {YYYY-MM-DD}
applies_to: {version}
owner: {team}
mode: tutorial
---

# Your first {thing}

{1-2 sentence hook: what you'll achieve}

## Before you begin

{Prerequisites — pinned versions, required accounts, required knowledge}

## Step 1: {Action}
## Step 2: {Action}
...

## What you accomplished

{Plain-language recap}

## What's next

{One link — either to the next tutorial, or to the how-to section for real use}
```

## Example

```markdown
---
title: Your first Taskflow board
last_reviewed: 2026-04-29
applies_to: v2.x
owner: docs-team
mode: tutorial
---

# Your first Taskflow board

In this tutorial you will create a Taskflow board, add three cards, and
move one card across columns. By the end you will see Taskflow's core
loop in action.

Time required: ~15 minutes.

## Before you begin

- Taskflow running locally (see Quickstart in README)
- Logged in as `admin@example.com`

## Step 1: Create a new board

Click **New Board** in the sidebar. Name it `My First Board`. Click
**Create**.

You should see an empty board with three columns: To Do, Doing, Done.

## Step 2: Add three cards

In the **To Do** column, click **+ Add Card**. Type `Try Taskflow` and
press Enter. Repeat for `Read the docs` and `Invite a teammate`.

You now have three cards in the To Do column.

## Step 3: Move a card to Doing

Drag `Try Taskflow` from To Do to Doing.

The card animates across, and the board's last-updated timestamp refreshes.

## What you accomplished

You created your first board, added cards, and moved one across columns.
This is Taskflow's core flow.

## What's next

Read the [Boards reference](../reference/boards.md) for the full list of
board options, or follow the [Invite a teammate](../how-to/invite-teammate.md)
how-to guide.
```

**Why this works**: One success path, no branching. Each step has a
verifiable observable outcome. Conclusion links to exactly one follow-up
per Diátaxis quadrant. Frontmatter declares `mode: tutorial` so the gate
can verify per-section mode clarity.

## Rules Summary

This tutorial passes the Diátaxis Mode Clarity gate if:

- It contains only one continuous success path
- No "why" explanations beyond 1-2 sentences per step
- No reference tables of options
- Every code block is runnable as shown
- The conclusion links to exactly one follow-up resource
