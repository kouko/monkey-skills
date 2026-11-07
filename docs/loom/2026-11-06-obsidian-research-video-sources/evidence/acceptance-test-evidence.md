# Research video sources — acceptance test evidence

Tried on 2026-11-06 in a clean shared clone at c3cbbb7e93ab5ab138f458430854c5fa3aaeecc1, detached; `git status --short` returned no entries. No packages installed and no network escalation requested.

Setup: README.md:25-46 points to host installation, and obsidian/README.md:114-125 requires marketplace installation and optionally a global CLI installation. Neither was performed: network access was unavailable and the test must not install packages or modify the user's host. Therefore host discovery/load was not verified. Existing local `yt-dlp --version` returned `2026.08.19`; `defuddle --version` returned `0.19.6`. `python3 scripts/sync_codex_manifests.py --check obsidian` exited 0, and both plugin manifests reported `3.26.0`. The default Python lacked pytest (`No module named pytest`). No matching criterion-specific tests were found by `rg -n -i 'yt-dlp|video sources|original.language|video research|youtube' obsidian/tests scripts`. The full package suite was not run; it is planned for finalize-review.

## 1. 指引說明何時適合使用影片，包括研究示範、訪談、使用經驗、使用者提供的影片，以及尋找多方觀點。

- How tried: inspected the clean-copy research guidance, especially Step 3.
- Observed: `obsidian/skills/obsidian-research/SKILL.md:53-55` describes the named use cases and optional search. This is static evidence only; no agent-led research was exercised.
- Verdict: not verified.

## 2. 指引提供影片搜尋、資訊與字幕取得所需的基本工具使用及安裝說明，並說明原始語言字幕的優先原則和資訊不足時的處理方式。

- How tried: inspected the clean-copy guidance and ran `yt-dlp --ignore-config --flat-playlist --no-download --print '%(title)s | %(url)s' 'ytsearch1:python tutorial' --socket-timeout 5 --retries 0`.
- Observed: the command exited 1 with `Failed to resolve 'www.youtube.com'` and `Unable to download API page`. `obsidian/skills/obsidian-research/SKILL.md:64-73` lists installation, search, metadata, caption commands and original-language preference. No real metadata or caption retrieval or installation was exercised.
- Verdict: not verified.

## 3. 影片來源能沿用現有研究的引用和查證要求；影片資訊缺漏或工具不可用時不阻止其他研究。

- How tried: inspected the new instructions and existing verification and source-list requirements.
- Observed: `obsidian/skills/obsidian-research/SKILL.md:73-75,77-80,102-106,114-123` directs the researcher to record limitations, continue with other sources and apply source checks. The network failure above did not produce a research run, so continuation and citation behavior remain untested.
- Verdict: not verified.

## 4. 指引說明影片日期、觀看、評價和頻道訂閱數等可用資訊僅供參考，不將受歡迎程度等同於可信度。

- How tried: inspected the clean-copy guidance.
- Observed: `obsidian/skills/obsidian-research/SKILL.md:75` calls for publication date where available, treats views, likes, ratings and subscriber counts as optional time-sensitive context, and says they do not establish credibility. No research output was generated to verify application.
- Verdict: not verified.
