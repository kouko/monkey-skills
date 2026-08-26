---
name: business-value
description: Adversarial worth-it check before betting real time on a product-shaped idea. Use for worth it? / should I build this / weighing ideas against one time budget. Market sizing → domain-teams:planning-team. 值不值得做 / ビジネスバリュー / 時間の使い方.
version: 0.1.0
---

# business-value

Decide whether this product-shaped idea deserves the user's fixed time budget
over its alternatives. Produce a short, git-diffable `business-value.md` whose
reasoning remains useful later.

## Register and executor

This is Shape Up betting: a bounded, reversible appetite decision about *worth
my time budget*. It is **not Cagan business viability**. Do not size markets,
model revenue, or create GTM strategy here.

Keep the frame personal and comparative: ask whether this idea earns a fixed
appetite over everything else that appetite could buy. Do not turn the exercise
into a forecast of market size or company success. The output records a choice,
its evidence, and its displaced alternative so a later reader can understand
the bet without reconstructing the conversation.

**You (the agent running this skill) are the executor.** Interrogate the user,
challenge hand-waving, weigh answers, propose the verdict, and author the
artifact. There is no separate runtime or API. Start from
`assets/business-value-template.md`.

## Fire or skip

This optional check uses explicit guards so weak models need no judgment.

**Fire when ANY of:**

- **(a)** the outcome is **for others**: it will be published or maintained;
  team-internal tools count;
- **(b)** multiple ideas compete for the same time budget; or
- **(c)** it requires meaningful resource spend: non-trivial time, money, or
  continuing upkeep.

**Skip silently when:**

- it is a personal tool for the user alone: private, throwaway, unpublished; OR
- a GO is already decided by the user. An incremental feature on an
  already-shipped product is a decided GO unless that increment independently
  meets (b) or (c).

Silent skip means no interrogation and **no artifact**. Downstream progress is
the implicit GO; never create an empty `business-value.md`. A brief note that
work is proceeding is allowed.

## Re-entrant interrogation

This is a **re-entrant checkpoint, not a one-way gate**. It may run on rough
evidence, then be revisited and overwrite the artifact after research. A
`NEEDS-MORE-RESEARCH` verdict explicitly invites that return.

Ask the user **one question at a time**. Let each answer determine the next
question, reject aspirations presented as evidence, and cover all three axes:

1. **Why now?** Why now rather than later or never? What changes if they wait?
2. **Why me?** Why this user rather than another person, an existing tool, or
   nobody? What advantage or specific itch do they have?
3. **Opportunity cost.** What concrete alternative loses this time? If nothing
   is displaced, the appetite claim is hollow.

Ask only value-judgment questions. Feasibility, need mapping, and implementation
are outside this skill.

Concrete answers name an observable change, a specific advantage, or an actual
competing commitment. When an answer stays abstract, ask for an example rather
than accepting confidence as evidence. Do not batch the remaining axes into the
same turn: preserving one-question-at-a-time pacing is part of the method, not
merely a presentation preference.

## Jurisdiction and authority

Market sizing, GTM, and revenue modeling go to
`domain-teams:planning-team`: pass relevant paths plus structured seed context,
give it authority to run its analysis and gates, and use only its returned
verdict. **Never inline** that work or its reasoning into `business-value.md`.

Need mapping belongs to `user-insights`. Business-value agents **may not map
user needs**, job stories, or opportunity spaces, and the skills share neither
artifact nor agent. Unknown users or needs therefore produce
`NEEDS-MORE-RESEARCH` and a `user-insights` handoff.

The agent renders and recommends the worth-it verdict; ratification remains the
user's call to ratify. The agent never commits the user's time unilaterally.
If the user rejects the recommendation, record the user's ratified verdict and
the disagreement plainly; do not disguise the proposal as the final authority.

## Verdict

Every non-skipped run ends with exactly one recommendation and a one-paragraph
rationale:

- **GO** — worth the time budget; continue downstream.
- **NO-GO** — not worth it now; preserve why to avoid blind re-litigation.
- **NEEDS-MORE-RESEARCH** — current evidence cannot support the call; route to
  `user-insights`, or planning-team for market economics, then revisit.

One weak axis alongside two concrete axes may still produce GO, but name that
weak axis. Two or more weak axes require NEEDS-MORE-RESEARCH, never hopeful GO.

## Procedure

1. Apply the fire/skip guards. On skip, stop this check silently with implicit
   GO and no file.
2. Read `assets/business-value-template.md` before writing so its shape and
   verdict enum control the artifact.
3. Interrogate one question at a time across Why now, Why me, and Opportunity
   cost. If present, consult
   `docs/loom/discovery/<date>-<slug>/user-insights.md`. Verify and cite a
   factual claim when one web search can check it.
4. Delegate market/GTM/revenue questions to `domain-teams:planning-team` using
   paths and seed context. Invocation forms are in
   `../using-loom-design/references/discovery-claude-code-tools.md` and the
   adjacent `discovery-codex-tools.md`.
5. Following the template, write
   `docs/loom/discovery/<date>-<slug>/business-value.md`, where the date is
   today (`YYYY-MM-DD`) and the topic slug is kebab-case. Reuse an existing
   folder for the same topic.
6. From the consumer project root, resolve the validator to an absolute path
   and pass this argv directly to process execution; never through a shell:

   ```text
   argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/discovery/validate_discovery_artifacts.py", "<discovery-folder>"]
   ```

   Fix reported issues and retry, bounded at 2 attempts. After the second
   failure, stop and surface the remaining problems to the user. The validator
   accepts the greenfield first run containing only `business-value.md` before
   `user-insights.md` exists.
7. For NEEDS-MORE-RESEARCH, hand off to `user-insights` and revisit when evidence
   improves.

## Boundary

Stop at the worth-it one-pager. Do not map needs, analyze market economics,
design, spec, or build. Those downstream stations read this verdict.
