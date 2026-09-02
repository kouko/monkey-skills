# Codex only — first contact with this repo

Skip all of this on Claude Code, where the plugin supplies the checker and
nothing is installed into the repo.

On Codex CLI the checker has to live inside the repo and be trusted once.
This runs at most once per repo, not once per change, and the approval it
asks for is an authorisation to run — not a decision about the work, and
therefore not a decision point.

## 1. Write the scaffold

From the loom-code checkout — wherever the user installed it; there is no
plugin root variable on this host:

```
python3 <loom-code>/scripts/codex_scaffold.py --repo .
```

Run it; never predict its answer. It prints one line per file it wrote,
repaired or left alone, then the commit subject to use.

If it says the sandbox protects `.codex/`, Codex' write sandbox refuses the
one directory the scaffold needs. Print this and **stop**:

> Codex 的沙箱保護 `.codex/`：請在 Codex 之外的終端機跑一次
> `python3 <loom-code>/scripts/codex_scaffold.py --repo .`，commit 之後我
> 再繼續。
>
> (Codex' sandbox protects .codex/ — run
> `python3 <loom-code>/scripts/codex_scaffold.py --repo .` once in a
> terminal outside Codex, commit, then continue.)

If it wrote or changed files, commit them with the message
`chore(loom): scaffold hooks <version>`, using the version the script
printed.

## 2. Check the copy runs at all

```
python3 <loom-code>/scripts/codex_scaffold.py --self-test
```

Exit 0 means the copied checker blocks a fake push. It does **not** mean
Codex will ever run it: that command runs the checker itself, so Codex'
trust decision is not in the loop. An untrusted hook is skipped in silence,
so the only way to tell a live gate from a dead one is to make **Codex**
issue the command.

If it reports the shim is not executable, re-run step 1 — the scaffold
repairs the mode — or `chmod +x .codex/hooks/loom-checker`.

## 3. The trust probe

Issue this yourself, as an ordinary tool call, not through the scaffold:

```
git push loom-trust-probe HEAD
```

`loom-trust-probe` is not a remote and never will be, so the command cannot
succeed. Read the first line of the output:

- It starts with `BLOCK push.` — the loom hook answered before git was
  reached. The hook is trusted and live: continue to step 1 of the station.
- Anything else — git answered (`'loom-trust-probe' does not appear to be a
  git repository`, or another git error). The hook did not run: Codex is
  skipping it because it is not trusted. Print the words below and **stop**.
  Do not retry and write no artifact: there is no gate.

> 我已幫這個 repo 裝好 loom 的檢查；請在 Codex 裡輸入 `/hooks` 按一次授
> 權，我才會繼續。
>
> (I have installed loom's checks for this repo; please type `/hooks` in
> Codex and approve them once, then I will carry on.)

After the user approves, run the trust probe again; a `BLOCK push.` answer
means you can continue.

To report whether the hook has ever fired here without issuing a command,
`python3 <loom-code>/scripts/codex_scaffold.py --trusted` reads the marker
the shim leaves behind. The self-test never writes that marker, so it
answers only for Codex' own firings.
