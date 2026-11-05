# Defuddle skill refresh — plan
intent: 2026-11-05-defuddle-skill-refresh@de9c5bc4
charter: 1.1

## Current State Evidence
- Forward: `obsidian/skills/defuddle/SKILL.md` Usage describes Markdown extraction for web URLs.
- Reverse: `obsidian/skills/defuddle/SKILL.md` description directs `.md` URLs to WebFetch.
- Error: `obsidian/skills/defuddle/SKILL.md` has no extraction failure or missing transcript guidance.
- Data: `obsidian/skills/defuddle/SKILL.md` Output formats lists JSON and top-level properties.
- Boundary: `obsidian/README.md` Cowork compatibility records sandbox restrictions for URL fetches.

## Task DAG

**W1-01 Refresh extraction guidance and verify examples** after: none acceptance: 1, 2, 3, 4, 5
- Files: obsidian/skills/defuddle/SKILL.md, obsidian/README.md, obsidian/README.ja.md, obsidian/README.zh-TW.md, obsidian/skills/using-obsidian/SKILL.md
- Test: A1 positive: article-and-video; negative: unrelated-request. A2 positive: article-markdown; boundary: unavailable-option. A3 positive: requested-track; boundary: absent-or-different-track. A4 positive: verified-cases; boundary: missing-transcript. A5 positive: existing-structure; boundary: unnecessary-files.
- Risk: agent-decided — retain one skill file; update existing inventories only where descriptions become inaccurate. Verify CLI behavior and language independently; `-p transcript` fails in 0.19.6.

## Simplicity check
- Reuse representative cases across acceptance lines — taken
- Add a dedicated permanent test framework — declined: existing cases and focused checks suffice

## Questions asked
① — what — 你要的方向是否是：**保留原本網頁擷取能力，補上影片逐字稿、語言核對和失敗處理，並用實際案例驗證？**

## Risks
1. Public video captions and network access change; preserve test fixtures and report live checks separately from deterministic cases.
2. Version 0.19.6 returns English when the Japanese preference has no matching track; report actual language without promising translation or availability.
3. User authorized implementation on 2026-11-05 by saying “繼續吧”; publication and merge remain outside the authorization.
4. On 2026-11-05 the user confirmed narrower acceptance: verify the documented commands and representative outputs; exclude gate registration, full agent traces and trigger-rate testing. Prior review and failed evidence remain in Git and acceptance evidence.
