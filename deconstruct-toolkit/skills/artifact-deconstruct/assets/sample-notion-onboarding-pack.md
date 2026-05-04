# Fixture: Notion onboarding pack (text extract, 2024)

**Source**: https://www.notion.so/templates/getting-started-personal (template gallery + onboarding tour)
**Accessed**: 2026-05-04
**License**: Quoted as fair-use educational analysis of publicly accessible onboarding artifacts. No reproduction of imagery; text content from public template descriptions and onboarding-flow copy.
**Eval target**: artifact-deconstruct must identify ≥6 components, infer probable writing order, identify audience layering, list ≥3 negative-space observations, name ≥1 inherited framework.

---

## The pack contains 6 artifacts (one URL each)

### 1. README.md (root template)

**Title**: "Notion Personal Home — your second brain in 5 minutes"

**Body opening**:
> Welcome. This template is your starting point. Don't worry about getting it perfect — you'll customize it as you learn what works for you.
>
> Below are 4 sections. Start with **Today**, then explore the rest at your pace.

### 2. Today (page)

A daily-note layout with three blocks:
- ☑️ Today's tasks (linked database view)
- 📝 Today's notes (linked database view)
- 📅 Today's calendar (linked database view)

**Helper text at top**: "Edit me. Replace this text with your own focus for today."

### 3. Tasks (database)

Pre-configured database with:
- Property: `Status` (Not started / In progress / Done)
- Property: `Priority` (P1 / P2 / P3)
- Property: `Due` (date)
- Property: `Project` (relation)

Three preset views: **Today** (filtered) / **This week** / **All open**.

### 4. Notes (database)

Pre-configured database with:
- Property: `Type` (Meeting / Idea / Reading / Personal)
- Property: `Tags` (multi-select)
- Property: `Created` (auto-populated)

Two preset views: **Recent** / **By type**.

### 5. Projects (database)

Pre-configured database with:
- Property: `Status` (Active / On hold / Done)
- Property: `Owner` (person)
- Property: `Linked tasks` (relation back to Tasks)

### 6. Quick start tour (in-app overlay)

A 4-step overlay walks the user through:

1. **Step 1**: "This is your home page. Bookmark it."
2. **Step 2**: "Try adding a task in the Today block. Just click and type."
3. **Step 3**: "Now add a note. Same gesture."
4. **Step 4**: "You're set. Customize from here. Browse the template gallery for more."

Each step has a "Next" button. The "Skip tour" link is small grey text top-right.

---

## Annotations for evaluator

The fixture is constructed to contain (so eval can verify):

- **6 components**: README (1) + Today page (2) + 3 databases (3-5) + tour overlay (6)
- **Probable writing order** (inferable):
  - Tasks DB and Notes DB likely written first (most-engineering)
  - Today page assembled from existing DBs
  - README written last (TL;DR / orientation usually last)
  - Tour overlay written last or in parallel with README
- **Audience layering**:
  - First-time user (sees the tour, reads the README)
  - Returning user (skips both, goes straight to Today)
  - Power user (ignores tour, customizes DBs)
- **Inherited framework**:
  - "Second brain" framing — Tiago Forte's *Building a Second Brain* (2022) terminology
  - PARA-adjacent organization (Projects / Areas / Resources / Archive) but simplified to Tasks / Notes / Projects
  - GTD-adjacent task structure (Status / Priority / Due)
- **Negative space** (3+):
  - No "what to do when overwhelmed" / friction-recovery section
  - No habit-formation guidance (template provides scaffolding, no behavioral nudge)
  - No team / collaboration onboarding (this is a personal pack)
  - No risk acknowledgment ("templates can become rigid; here's how to know when to leave")
  - No deletion / cleanup pattern (PARA principle "archive periodically" is absent)

- **Genre**: Personal-productivity onboarding pack. Move analysis (Bhatia-style):
  - ✅ Establishing credentials (implicit via Notion brand)
  - ✅ Introducing the offer (README welcome)
  - ⚠️ Offering incentives (none — assumes user already chose Notion)
  - ✅ Soliciting response (implicit "customize it")
  - ❌ Pressure tactics (absent — appropriate for onboarding genre)
- **Most distinctive feature**: README's *anti-perfectionism* tone ("don't worry about getting it perfect"). This is unusual for product onboarding (which usually sells aspiration); Notion deliberately deflates aspiration to reduce abandonment.
