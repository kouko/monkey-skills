# Defuddle skill refresh — acceptance test evidence

Tried on 2026-11-05 in a clean clone at 5698f79f53f24ab62cc2749244136479d60cce27. `git worktree add` failed with `Operation not permitted` when creating repository worktree metadata; `git clone --no-local --no-checkout` followed by checkout of the tested commit succeeded. The clone was not installed into the user's host: doing so would change the existing plugin installation. Therefore discovery and loading by an agent were not tested. The README recommends plugin installation and a globally installed Defuddle CLI; the already available CLI reported version `0.19.6`.

## 1. 使用者要求讀取一般網頁或 YouTube 逐字稿時，skill 的描述與指引涵蓋對應用途。
- How I tried it: Read `obsidian/skills/defuddle/SKILL.md` in the clean clone, then attempted actual URL extraction as described in sections 2 and 3.
- What came back: The description names web pages and YouTube transcripts; the usage sections cover both. No isolated agent session was available to test actual selection or execution of the skill.
- Evidence: `obsidian/skills/defuddle/SKILL.md` lines 3–4, 14–18, and 36–46. Reading guidance establishes its content only, not triggering behavior.

## 2. 影片逐字稿的指引能辨識實際回傳的語言、逐字稿缺失及擷取錯誤，不將其他內容當作逐字稿。
- How I tried it: `defuddle parse 'https://www.youtube.com/watch?v=jNQXAC9IVRw' --json --lang ja`.
- What came back: Exit 1, `Error: fetch failed`. No transcript or language was returned. Missing-track, different-language, and agent interpretation behavior could not be exercised. The instruction text describes these cases but was not behaviorally tested.
- Evidence: captured command output above; `obsidian/skills/defuddle/SKILL.md` lines 36–46.

## 3. 現有網頁擷取用途保留，相關指令和新版功能的說明與可驗證行為一致。
- How I tried it: `defuddle parse 'https://example.com' --md`; also supplied a small HTML article via `printf '<html><head><title>Acceptance Article</title></head><body><article><h1>Acceptance Article</h1><p>Readable sample content.</p></article></body></html>' | defuddle parse - --md`.
- What came back: URL: exit 1, `Error: fetch failed`. Standard input: exit 0, `Readable sample content.` Local HTML extraction works; live web and video claims remain unverified in this environment.
- Evidence: captured outputs above. No network availability was established by these failures alone.

## 4. 更新後的 skill 通過適用的檢查，並以代表性請求和輸出驗證上述用途與限制。
- How I tried it: Searched `obsidian/tests` for `defuddle` and tried the representative commands in sections 2 and 3. No criterion-specific Defuddle test was found in that directory. The full package suite is reserved for the later acceptance gate and was not run here.
- What came back: Local HTML succeeded; both public URL requests failed to fetch. No representative agent request or transcript output was obtained; no criterion-specific automated test was run.
- Evidence: `rg -n -i 'defuddle' obsidian --glob '*test*'` returned no matches; outputs in sections 2–3.

## Additional network retry on 2026-11-05 at 5698f79
- The same clean clone and installed CLI were used with network access outside the sandbox. The original sandbox failures above remain part of the record.
- 1: The CLI output below does not establish whether an agent selects or follows the skill.
- 2: `defuddle parse 'https://www.youtube.com/watch?v=jNQXAC9IVRw' --json --lang ja` exited 0. JSON returned `language: "en"` and a nonempty `variables.transcript` containing English speech with timestamps and chapters. Thus this example returned English despite the Japanese preference. The missing-transcript case and agent interpretation were not tested.
- 3: `defuddle parse 'https://example.com' --md` exited 0 and returned the example domain's readable paragraph. This supplements the successful local HTML test; other documented options were not individually tested.
- 4: The live page and video provide representative CLI outputs, not representative agent requests or proof of missing-transcript handling. No criterion-specific automated test was run; the full package suite remains for the later gate.
