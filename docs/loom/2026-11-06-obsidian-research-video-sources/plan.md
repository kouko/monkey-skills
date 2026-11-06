# Video sources for research — plan
intent: 2026-11-06-obsidian-research-video-sources@6dae13b
charter: 1.1

## Current State Evidence
- Forward: `obsidian/skills/obsidian-research/SKILL.md` Step 3 researches angles and accepts user-provided sources.
- Reverse: `obsidian/skills/obsidian-research/SKILL.md` Step 4 separates factual verification from confirming opinions.
- Error: `obsidian/skills/obsidian-research/SKILL.md` Pre-flight records missing web tools and preserves user-material-only research.
- Data: `obsidian/skills/obsidian-research/SKILL.md` Step 5 requires source URLs, language and access date.
- Boundary: `obsidian/skills/defuddle/SKILL.md` YouTube section already covers optional transcript extraction and language uncertainty.

## Task DAG

**W1-01 Add optional video research guidance** after: none  acceptance: 1, 2, 3, 4
- Files: `obsidian/skills/obsidian-research/SKILL.md`, `obsidian/.claude-plugin/plugin.json`, `obsidian/.codex-plugin/plugin.json`, `obsidian/CHANGELOG.md`
- Test: A1 positive: video-relevant topic; boundary: sufficient text sources. A2 positive: original captions; boundary: unknown language. A3 positive: cited video; negative: unavailable tools. A4 positive: available metrics; boundary: missing metrics.
- Risk: agent-decided — keep guidance in the existing research skill, reuse Defuddle, and make yt-dlp optional; a separate tool package adds maintenance without a demonstrated need.

## Simplicity check
- none found

## Questions asked
① — what — 這就是你要的範圍嗎？

## Risks
1. Tool output and platform availability vary; no particular subtitle, language field, metric, or search benefit is guaranteed.
2. user-decided — Keep tool instructions brief and focus on when video sources add research value; retain existing source-verification practices.
