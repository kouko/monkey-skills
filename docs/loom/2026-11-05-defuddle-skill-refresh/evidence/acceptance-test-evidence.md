# Defuddle skill refresh — acceptance test evidence

## Re-run on 2026-11-05, at e6a9235fdbaba36185879f10513dfb0f0f05447c

- Setup: cloned the repository with `git clone --no-local --no-checkout`, checked out the exact commit detached, and read the plugin README and skill. The README instructs plugin installation and `npm install -g defuddle`; neither was repeated because changing the existing host installation is outside scope. The existing executable returned `0.19.6` from `defuddle --version`. Agent discovery/loading and the installation command were not exercised.
- 1: re-tested — the skill description explicitly names web pages and YouTube transcripts. Automatic selection was excluded by the user and not tested.
- 2: re-tested — the skill documents installation, web Markdown, output file, property extraction, frontmatter, stdin, video Markdown, JSON and language preference. The commands below exercised the available 0.19.6 executable; installing it was not repeated.
- 3: re-tested — the skill requires checking transcript text and reporting a missing transcript, different language, unknown language or command failure. `defuddle parse 'https://www.youtube.com/watch?v=PO15YVVp5Mg' --json --lang ja` exited 0 outside the sandbox: top-level `language` was `en`, and `variables.transcript` contained 4,057 characters starting `Good morning. It's Yusuke. This is near Chiba Station.` This example returned English despite the Japanese preference. A real captionless video and an agent response were not tested.
- 4: re-tested — the initial sandbox command `defuddle parse 'https://example.com/' --md --frontmatter` exited 1 with `Error: fetch failed`. Retrying outside the sandbox exited 0 and returned `title: "Example Domain"`, `language: "en"`, and the readable page paragraph. `defuddle parse 'https://example.com/' -p title` returned `Example Domain`; `defuddle parse 'https://example.com/' --md -o /private/tmp/defuddle-acceptance-e6a9235-output.md` wrote the readable paragraph. Piping a local HTML article to `defuddle parse - --md` returned `Readable sample content.` The same video with `--md` returned a `## Transcript` followed by timestamped English speech. The JSON language-preference command and its output are recorded in 3. The real captionless case and installation were not exercised.
- 5: re-tested — the skill remains a single `SKILL.md`, with existing English, Japanese and Traditional Chinese README entries and router entry. The fix diff from `5f7fd271` changes the Defuddle guidance, so all rows were re-tested. No criterion-specific automated Defuddle test was found by `rg -n -i 'defuddle' obsidian --glob '*test*'`; the full package suite is reserved for finalization, where it runs before acceptance and blocks it on failure. No suite result is claimed here.

## User-confirmed narrower acceptance — 2026-11-05

The user confirmed that gate registration, complete agent execution traces, and trigger-rate testing are not acceptance conditions. Earlier partial results and sandbox failures below remain part of the record. The skill content tested is commit `5f7fd271`; the later commits before this section changed evidence only.

1. The skill description names web pages and YouTube transcripts. This verifies the wording, not automatic skill selection.
2. The skill documents the installation command, Markdown extraction, YouTube JSON and the language preference. The installed executable reports `0.19.6`; installation was not repeated.
3. The skill states that the language is a preference and that the top-level language can reflect page metadata; it requires checking transcript text and reporting errors or absence. For `PO15YVVp5Mg`, `--json --lang ja` exited 0 and returned an English transcript (4,057 characters) and top-level language `en`.
4. `defuddle parse 'https://example.com/' --md --frontmatter` exited 0 with the page body and frontmatter. `defuddle parse 'https://www.youtube.com/watch?v=jNQXAC9IVRw' --md` exited 0 with a timestamped transcript. The preceding Japanese-preference case also succeeded. A real video with no captions was not tested; synthetic absence and earlier sandbox errors are recorded below.
5. The skill remains one `SKILL.md`; existing English, Japanese and Traditional Chinese README entries and the router entry were updated. No new skill runtime or test framework was added.

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

## Re-run on 2026-11-05, at 5f7fd271
- Fix diff `9f379140..5f7fd271` changes the tested-options claim and transcript language guidance. A fresh clone checked out the full commit; no host installation or agent auto-trigger test was performed.
- 1: re-tested — read the changed skill and ran the live page and video requests below; the description covers both, but these CLI requests cannot prove automatic agent selection.
- 2: re-tested — `defuddle parse 'https://www.youtube.com/watch?v=PO15YVVp5Mg' --json --lang ja` with network access exited 0; top-level `language` was `en` and `variables.transcript` began with English speech: `Good morning. It's Yusuke. This is near Chiba Station.` A synthetic HTML document with `lang="ja"` and description only was piped to `defuddle parse - --json`; exit 0, `language: ja`, `variables: None`, `content: Description only`. This demonstrates the distinction between page language and a missing transcript for a synthetic input, not a real captionless video or an agent response. The earlier sandbox fetch error remains recorded above.
- 3: re-tested — `defuddle parse 'https://example.com' --md --frontmatter` with network access exited 0, returning frontmatter with `title: "Example Domain"`, `language: "en"`, and the readable paragraph. The standard-input local HTML test again exited 0 with `Readable sample content.` Video JSON is recorded in 2. Other options and agent behavior were not individually verified.
- 4: re-tested — the above live and synthetic outputs were obtained; no criterion-specific automated test was found or run. The full package suite is reserved for the later acceptance gate. Neither automatic triggering nor a real captionless video was tested.

### Additional explicit-skill cases
- Reviewed `/private/tmp/defuddle-behavior-evidence/youtube.json`, `youtube.stdout`, `youtube.stderr`, and `youtube.response.md`. The recorded request explicitly names `obsidian/skills/defuddle/SKILL.md`; automatic triggering was not tested. Recorded command: `defuddle parse 'https://www.youtube.com/watch?v=PO15YVVp5Mg' --json --lang ja`; exit 0, empty stderr, top-level `language: en`, and nonempty English `variables.transcript`. The saved response says Japanese was requested but English was obtained, and that this does not establish whether Japanese captions exist.
- Reviewed `synthetic.json`, `synthetic.stdout`, `synthetic.stderr`, `synthetic.response.md`, and `description-only.html` in the same directory. Recorded command: `defuddle parse /private/tmp/defuddle-behavior-evidence/description-only.html --json`; exit 0, empty stderr, `language: ja`, and no `variables` field. The saved response says parsing succeeded without a transcript and page language does not establish transcript language. This is synthetic local HTML, not a real captionless video.
- Provenance limit: `run_cases.py` shows that the command output and metadata files were produced by a Python subprocess harness. The response files contain the reported agent answers, but the available files do not contain a host execution trace proving how those answers were generated or linking them to an agent session. They support inspection of the saved answers and CLI results, not independent proof of skill invocation or automatic selection.
