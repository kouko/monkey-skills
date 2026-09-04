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

## 3. Read `--trusted`, then probe

`.codex/hooks.json` carries more than one hook definition — loom's own
`PreToolUse` checker plus whatever `PostToolUse` hooks this repo ships. Each
is trusted independently, so check all of them, not one:

```
python3 <loom-code>/scripts/codex_scaffold.py --trusted
```

This reads the firing ledger the shims leave behind and prints one line per
definition: `<event> <matcher> <command>: fired|never|ambiguous`. Exit 0
means every definition has fired at least once — continue to step 1 of the
station. A non-zero exit prints a `BLOCK: <n> of <m> Codex hook definitions
have never fired in <absolute repo path>` header followed by the `never`
lines. A `never` line is only "no evidence of a firing yet", never proof of
distrust — the ledger cannot tell a never-approved hook from an approved one
Codex simply hasn't triggered.

To turn a `never` line into a real answer, issue the loom checker's own
probe yourself, as an ordinary tool call, not through the scaffold:

```
git push loom-trust-probe HEAD
```

`loom-trust-probe` is not a remote and never will be, so the command cannot
succeed. Read the first line of the output:

- It starts with `BLOCK push.` — the loom hook answered before git was
  reached. The hook is trusted and live.
- Anything else — git answered (`'loom-trust-probe' does not appear to be a
  git repository`, or another git error). The hook did not run: Codex is
  skipping it because it is not trusted. Print the words below, naming this
  repo's folder, and **stop**. Do not retry and write no artifact: there is
  no gate.

> 我已幫 `<absolute repo path>` 這個資料夾裝好 loom 的檢查；請在 Codex 裡
> 對這個資料夾輸入 `/hooks` 按一次授權，我才會繼續。
>
> (I have installed loom's checks for `<absolute repo path>`; please type
> `/hooks` in Codex **for this folder** and approve them once, then I will
> carry on.)

After the user approves, run `--trusted` again; every definition reading
`fired` means you can continue.

## 4. What trust is bound to

Codex binds an approval to one `(hooks.json path, event, index)` triple —
the definition — not to the script file it points at. Editing a hook
script's contents needs no re-approval; editing the `command` string for a
definition in `hooks.json` does, because that changes which definition
Codex is being asked to trust. The approval key also carries the repo's
absolute path, so it is scoped per clone: a fresh `git clone`, or a second
worktree of the same repo, is a different key and starts at `never` again —
this is not a bug to route around, it is the same "one binary, many
folders" boundary `/hooks` already draws.

## 5. Your own hooks

A repo that ships its own Codex hooks (not loom's) should have each one
record its own firing rather than staying invisible to `--trusted`. The
shape is a three-line thin shim in front of the repo's existing hook:

```bash
INPUT=$(cat)
printf '%s' "$INPUT" | python3 .codex/hooks/loom_record_fire.py "$0" 2>/dev/null || true
printf '%s' "$INPUT" | exec .claude/hooks/<same name>
```

Read stdin once, hand it to the shared recorder (best-effort — a failure
there must never block the hook it is wrapping), then hand the same stdin
on to the real hook by `exec`.
