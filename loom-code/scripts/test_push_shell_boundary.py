"""Executable shell-boundary regressions for branch-end finding 05.

Every shell command targets temporary local bare remotes. Legacy forms expose
the original holes; canonical forms prevent a future flag-only fix masking
the same shell syntax. No production function is replaced in shell replays.
"""
from __future__ import annotations

import io
import os
from pathlib import Path
import shlex
import shutil
import subprocess

import pytest

import loom_checker
import test_loom_checker_push as fixture
import test_single_owner_push_gate as previous

GIT = str(Path(shutil.which("git")).resolve())
BASH = shutil.which("bash")
ZSH = shutil.which("zsh")
FIXED = "--no-follow-tags --recurse-submodules=no -u"
COUNTER = "from pathlib import Path\np=Path('.git/suite-count'); p.write_text(p.read_text()+'run\\n' if p.exists() else 'run\\n')\n"


def scene(tmp_path):
    """Use a repo-neutral fixture whose absolute checkout path contains spaces."""
    base = tmp_path / "selected repo's spaces"
    base.mkdir()
    repo, _, _ = previous.repository(base, package="python3 evidence/package.py", scripts={"evidence/package.py": COUNTER})
    remote = tmp_path / "remote.git"
    subprocess.run([GIT, "init", "--bare", "-q", str(remote)], check=True)
    fixture.git(repo, "remote", "add", "origin", str(remote))
    head = fixture.git(repo, "rev-parse", "HEAD")
    extra = fixture.git(repo, "commit-tree", f"{head}^{{tree}}", "-p", head, "-m", "unreviewed extra")
    fixture.git(repo, "update-ref", "refs/heads/extra", extra)
    return repo, remote, head, extra


def refs(remote):
    """Read every published ref instead of checking only the expected branch."""
    result = fixture.git(remote, "for-each-ref", "--format=%(refname) %(objectname)")
    return dict(line.split(" ", 1) for line in result.splitlines())


def suites(repo):
    """Count actual complete command executions outside porcelain-visible data."""
    marker = repo / ".git/suite-count"
    return len(marker.read_text().splitlines()) if marker.exists() else 0


def quote_all(token):
    """Quote every token, including safe-looking ones that zsh aliases can match."""
    return "'" + token.replace("'", "'\"'\"'") + "'"


def render(tokens):
    """The canonical spelling is one space between single-quoted argv tokens."""
    return " ".join(quote_all(token) for token in tokens)


def canonical_tokens(repo, head, *, external=False, remote="origin"):
    """Keep the executable, flags, literal remote, and pinned refspec explicit."""
    return [GIT, *(["-C", str(repo)] if external else []), "push", *FIXED.split(), remote, f"{head}:refs/heads/work"]


def exact_shell_replay(repo, remote, command, *, environment=None, shell=BASH, preamble=None):
    """Execute precisely the intercepted bytes only when the real hook releases."""
    checked = previous.hook_command(repo, command)
    executed = None
    if checked.returncode == 0:
        env = dict(os.environ)
        shell_home = repo / ".git/shell-home"
        shell_home.mkdir(exist_ok=True)
        env["HOME"] = str(shell_home)
        env.pop("BASH_ENV", None)
        env.pop("ENV", None)
        env.update(environment or {})
        shell_args = [shell, "-f", "-c", command] if shell == ZSH else [shell, "--noprofile", "--norc", "-c", command]
        if preamble is None:
            executed = subprocess.run(shell_args, cwd=repo, env=env,
                                      capture_output=True, text=True, timeout=15)
        else:
            # Model an already configured shell: it reads setup as a separate
            # command, then the exact intercepted command bytes from stdin.
            executed = subprocess.run([shell, "-f"], input=preamble + "\n" + command + "\n",
                                      cwd=repo, env=env, capture_output=True, text=True, timeout=15)
    return {
        "hook_rc": checked.returncode, "suites": suites(repo), "refs": refs(remote),
        "shell_rc": executed.returncode if executed else None,
        "stderr": checked.stderr, "shell_stderr": executed.stderr if executed else "",
    }


def rejected(result):
    """A rejected command must execute neither the suite nor a network push."""
    assert result["hook_rc"] == 2 and result["suites"] == 0 and result["refs"] == {}, repr(result)


@pytest.mark.parametrize("fixed", [False, True], ids=["legacy-red", "canonical-boundary"])
def test_shell_wordsplit_rejected(tmp_path, fixed):
    """An opaque remote token cannot expand into an extra mutable refspec."""
    repo, remote, head, extra = scene(tmp_path)
    flags = FIXED if fixed else "-u"
    command = (render(["command", GIT, "push", *flags.split()]) + " $R " + quote_all(f"{head}:refs/heads/work")) if fixed else f"{GIT} push {flags} $R {head}:refs/heads/work"
    result = exact_shell_replay(repo, remote, command, environment={"R": "origin extra:refs/heads/extra"})
    if result["hook_rc"] == 0:
        assert result["shell_rc"] == 0, result
        assert result["refs"].get("refs/heads/extra") == extra, "attack failed to publish its extra commit"
    rejected(result)


EXPANSIONS = [
    "$(printf origin)", "`printf origin`", '"$(printf origin)"',
    "<(printf origin)", "orig*", "orig?n", "{origin,origin}", "~",
    '"$R"', "'$R'", r"\$R", "'orig*'", r"orig\*", "'{origin,origin}'",
    '"~"', r"\~", "${R}", "$((1+1))",
]


@pytest.mark.parametrize("remote_token", EXPANSIONS)
@pytest.mark.parametrize("fixed", [False, True], ids=["legacy", "canonical"])
def test_shell_expansion_rejected(tmp_path, remote_token, fixed):
    """Expansion spellings and quoted or escaped decoys are outside the allowlist."""
    repo, remote, head, _ = scene(tmp_path)
    flags = FIXED if fixed else "-u"
    command = (render(["command", GIT, "push", *flags.split()]) + " " + remote_token + " " + quote_all(f"{head}:refs/heads/work")) if fixed else f"{GIT} push {flags} {remote_token} {head}:refs/heads/work"
    rejected(exact_shell_replay(repo, remote, command, environment={"R": "origin"}))


@pytest.mark.parametrize("attack", [
    "path-assignment", "fake-git", "function", "global-alias", "command-wrapper",
    "env-wrapper", "shell-wrapper", "extra-segment", "prefix-segment", "redirect", "comment",
    "bad-quote", "global-option", "push-option", "bare-git",
])
@pytest.mark.parametrize("fixed", [False, True], ids=["legacy", "canonical"])
def test_shell_commandshape_rejected(tmp_path, attack, fixed):
    """The complete command must identify one trusted executable and one push."""
    repo, remote, head, _ = scene(tmp_path)
    flags = FIXED if fixed else "-u"
    tail = f"push {flags} origin {head}:refs/heads/work"
    fake_dir = tmp_path / "fake-bin"
    fake_dir.mkdir()
    fake = fake_dir / "git"
    fake.write_text(f"#!/bin/sh\nexec {shlex.quote(GIT)} push origin extra:refs/heads/extra\n")
    fake.chmod(0o755)
    command = render(["command", *canonical_tokens(repo, head)]) if fixed else f"{GIT} {tail}"
    shell = BASH
    if attack == "path-assignment":
        command = f"PATH={shlex.quote(str(fake_dir))}:$PATH git {tail}"
    elif attack == "fake-git":
        command = render(["command", str(fake), *canonical_tokens(repo, head)[1:]]) if fixed else f"{shlex.quote(str(fake))} {tail}"
    elif attack == "function":
        command = f"git() {{ {GIT} push origin extra:refs/heads/extra; }}; git {tail}"
    elif attack == "global-alias":
        if not ZSH:
            pytest.skip("zsh global aliases are not available on this host")
        shell = ZSH
        command = f"alias -g R='origin extra:refs/heads/extra'\n{GIT} push {flags} R {head}:refs/heads/work"
    elif attack == "command-wrapper":
        command = "command " + command
    elif attack == "env-wrapper":
        command = "env " + command
    elif attack == "shell-wrapper":
        command = f"{shlex.quote(BASH)} -c {shlex.quote(command)}"
    elif attack == "extra-segment":
        command += f"; {GIT} push origin extra:refs/heads/extra"
    elif attack == "prefix-segment":
        command = "true; " + command
    elif attack == "redirect":
        command += " > .git/push-output"
    elif attack == "comment":
        command += " # apparently harmless"
    elif attack == "bad-quote":
        command += " '"
    elif attack == "global-option":
        command = render(["command", GIT, "-c", "push.followTags=true", *canonical_tokens(repo, head)[1:]]) if fixed else f"{GIT} -c push.followTags=true {tail}"
    elif attack == "push-option":
        command = render(["command", GIT, "push", "--force", *canonical_tokens(repo, head)[2:]]) if fixed else f"{GIT} push --force {flags} origin {head}:refs/heads/work"
    elif attack == "bare-git":
        command = render(["command", "git", *canonical_tokens(repo, head)[1:]]) if fixed else f"git {tail}"
    rejected(exact_shell_replay(repo, remote, command, shell=shell))


@pytest.mark.parametrize("external", [False, True])
def test_shell_literal_publishesonlypinned(tmp_path, external):
    """Canonical literal commands suppress configured implicit tag publication."""
    repo, remote, head, _ = scene(tmp_path)
    fixture.git(repo, "config", "push.followTags", "true")
    fixture.git(repo, "tag", "-am", "private local tag", "local-only", head)
    command = render(["command", *canonical_tokens(repo, head, external=external)])
    result = exact_shell_replay(repo, remote, command)
    assert result["hook_rc"] == 0 and result["shell_rc"] == 0 and result["suites"] == 1, result
    assert result["refs"] == {"refs/heads/work": head}, result


def test_shell_implicitfollowtags_rejected(tmp_path):
    """A literal immutable source still leaks reachable tags without the fixed flag."""
    repo, remote, head, _ = scene(tmp_path)
    fixture.git(repo, "config", "push.followTags", "true")
    fixture.git(repo, "tag", "-am", "local tag", "local-only", head)
    command = f"{GIT} push -u origin {head}:refs/heads/work"
    result = exact_shell_replay(repo, remote, command)
    if result["hook_rc"] == 0:
        assert "refs/tags/local-only" in result["refs"], result
    rejected(result)


@pytest.mark.parametrize("fixed", [False, True], ids=["legacy-red", "canonical-boundary"])
def test_shell_inheritedalias_rejected(tmp_path, fixed):
    """A pre-existing global alias can expand a seemingly literal remote token."""
    if not ZSH:
        pytest.skip("zsh global aliases are not available on this host")
    repo, remote, head, extra = scene(tmp_path)
    flags = FIXED if fixed else "-u"
    command = f"{GIT} push {flags} origin {head}:refs/heads/work"
    result = exact_shell_replay(repo, remote, command, shell=ZSH,
                               preamble="alias -g origin='origin extra:refs/heads/extra'")
    if result["hook_rc"] == 0:
        assert result["refs"].get("refs/heads/extra") == extra, repr(result)
    rejected(result)


def test_shell_quotedalias_publishesonlypinned(tmp_path):
    """Quote-all survives inherited aliases targeting the executable and arguments."""
    if not ZSH:
        pytest.skip("zsh global aliases are not available on this host")
    repo, remote, head, _ = scene(tmp_path)
    command = render(["command", *canonical_tokens(repo, head, external=True)])
    setup = "\n".join([
        "alias -g origin='origin extra:refs/heads/extra'",
        f"alias {shlex.quote(GIT)}='false'",
        "alias -g push='push --follow-tags'",
    ])
    result = exact_shell_replay(repo, remote, command, shell=ZSH, preamble=setup)
    assert result["hook_rc"] == 0 and result["shell_rc"] == 0 and result["suites"] == 1, repr(result)
    assert result["refs"] == {"refs/heads/work": head}, repr(result)


def absolute_function_setup():
    """Model an inherited function without replacing the trusted command builtin."""
    return (f"function {GIT}() {{ command {quote_all(GIT)} "
            '"$@" ' + quote_all("extra:refs/heads/extra") + "; }")


@pytest.mark.parametrize("shell", [BASH, ZSH], ids=["bash", "zsh"])
def test_shell_absolutefunction_rejected(tmp_path, shell):
    """Quoting an absolute executable does not suppress a same-named function."""
    if shell is None:
        pytest.skip("the requested shell is unavailable")
    repo, remote, head, extra = scene(tmp_path)
    command = render(canonical_tokens(repo, head))
    result = exact_shell_replay(repo, remote, command, shell=shell,
                               preamble=absolute_function_setup())
    if result["hook_rc"] == 0:
        assert result["suites"] == 1 and result["shell_rc"] == 0, repr(result)
        assert result["refs"] == {"refs/heads/work": head, "refs/heads/extra": extra}, repr(result)
    rejected(result)


@pytest.mark.parametrize("shell", [BASH, ZSH], ids=["bash", "zsh"])
def test_shell_commandbuiltin_publishesonlypinned(tmp_path, shell):
    """The supported shell's standard command builtin bypasses the Git function."""
    if shell is None:
        pytest.skip("the requested shell is unavailable")
    repo, remote, head, _ = scene(tmp_path)
    command = render(["command", *canonical_tokens(repo, head)])
    result = exact_shell_replay(repo, remote, command, shell=shell,
                               preamble=absolute_function_setup())
    assert result["hook_rc"] == 0 and result["suites"] == 1 and result["shell_rc"] == 0, repr(result)
    assert result["refs"] == {"refs/heads/work": head}, repr(result)


def install_extra_ref_pre_push(repo):
    """Install a repository-controlled hook that attempts a second push."""
    hook = repo / ".git/hooks/pre-push"
    hook.write_text(
        "#!/bin/sh\n"
        + quote_all(GIT)
        + " push --no-verify origin extra:refs/heads/extra\n"
    )
    hook.chmod(0o755)


@pytest.mark.parametrize("shell", [BASH, ZSH], ids=["bash", "zsh"])
def test_shell_prepushhook_rejected(tmp_path, shell):
    """A command that permits a post-gate pre-push hook is not canonical."""
    if shell is None:
        pytest.skip("the requested shell is unavailable")
    repo, remote, head, extra = scene(tmp_path)
    install_extra_ref_pre_push(repo)
    command = render(["command", *canonical_tokens(repo, head)])
    result = exact_shell_replay(repo, remote, command, shell=shell)
    if result["hook_rc"] == 0:
        assert result["shell_rc"] == 0 and result["refs"].get("refs/heads/extra") == extra, repr(result)
    rejected(result)


@pytest.mark.parametrize("shell", [BASH, ZSH], ids=["bash", "zsh"])
def test_shell_noverify_publishesonlypinned(tmp_path, shell):
    """The fixed no-verify flag prevents repository hooks from adding refs."""
    if shell is None:
        pytest.skip("the requested shell is unavailable")
    repo, remote, head, _ = scene(tmp_path)
    install_extra_ref_pre_push(repo)
    tokens = canonical_tokens(repo, head)
    tokens.insert(tokens.index("-u") + 1, "--no-verify")
    result = exact_shell_replay(repo, remote, render(["command", *tokens]), shell=shell)
    assert result["hook_rc"] == 0 and result["suites"] == 1 and result["shell_rc"] == 0, repr(result)
    assert result["refs"] == {"refs/heads/work": head}, repr(result)


@pytest.mark.parametrize("shell", [BASH, ZSH], ids=["bash", "zsh"])
def test_shell_builtinoracle_publishesonlypinned(tmp_path, shell):
    """A shell-only local control proves the proposed prefix bypasses the function."""
    if shell is None:
        pytest.skip("the requested shell is unavailable")
    repo, remote, head, _ = scene(tmp_path)
    command = render(["command", *canonical_tokens(repo, head)])
    env = dict(os.environ)
    env.pop("BASH_ENV", None)
    env.pop("ENV", None)
    result = subprocess.run([shell, "-f"], input=absolute_function_setup() + "\n" + command + "\n",
                            cwd=repo, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert refs(remote) == {"refs/heads/work": head}
    assert suites(repo) == 0, "the shell-only oracle must not pretend to run the hook"


@pytest.mark.parametrize("quotation", ["unquoted", "executable-only", "arguments-only", "remote-unquoted", "double-quotes", "tabs"])
def test_shell_partialquotes_rejected(tmp_path, quotation):
    """Only the exact quote-all spelling closes every alias-expansion position."""
    repo, remote, head, _ = scene(tmp_path)
    tokens = ["command", *canonical_tokens(repo, head)]
    if quotation == "unquoted":
        command = " ".join(tokens)
    elif quotation == "executable-only":
        command = quote_all(tokens[0]) + " " + " ".join(tokens[1:])
    elif quotation == "arguments-only":
        command = tokens[0] + " " + render(tokens[1:])
    elif quotation == "remote-unquoted":
        command = render(tokens[:-2]) + " origin " + quote_all(tokens[-1])
    elif quotation == "double-quotes":
        command = " ".join('"' + token + '"' for token in tokens)
    else:
        command = "\t".join(quote_all(token) for token in tokens)
    rejected(exact_shell_replay(repo, remote, command))


@pytest.mark.parametrize("fixed", [False, True], ids=["implicit-rejected", "canonical-no-recursion"])
def test_shell_implicitsubmodule_contained(tmp_path, fixed):
    """Configured on-demand recursion cannot publish a second repository."""
    repo, remote, _, _ = scene(tmp_path)
    child = tmp_path / "child-source"
    child.mkdir()
    fixture.git(child, "init", "-q", "-b", "work")
    fixture.git(child, "config", "user.email", "fixture@example.test")
    fixture.git(child, "config", "user.name", "Fixture")
    (child / "data").write_text("initial\n")
    fixture.git(child, "add", "data")
    fixture.git(child, "commit", "-qm", "initial")
    child_remote = tmp_path / "child-remote.git"
    subprocess.run([GIT, "clone", "--bare", "-q", str(child), str(child_remote)], check=True)
    initial = fixture.git(child_remote, "rev-parse", "refs/heads/work")
    fixture.git(repo, "reset", "--soft", "HEAD^")
    fixture.git(repo, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(child_remote), "dependency")
    dependency = repo / "dependency"
    fixture.git(dependency, "config", "user.email", "fixture@example.test")
    fixture.git(dependency, "config", "user.name", "Fixture")
    fixture.git(dependency, "commit", "--allow-empty", "-qm", "unpublished submodule")
    unpublished = fixture.git(dependency, "rev-parse", "HEAD")
    fixture.git(repo, "add", ".gitmodules", "dependency")
    fixture.git(repo, "commit", "--amend", "--no-edit", "-q")
    reviewed = fixture.git(repo, "rev-parse", "HEAD")
    body = fixture.review_body(reviewed)
    body["probes"][0]["command"] = "python3 evidence/package.py"
    fixture.write_review(repo, body)
    fixture.git(repo, "add", fixture.REVIEW)
    fixture.git(repo, "commit", "-qm", "checkpoint")
    fixture.git(repo, "config", "push.recurseSubmodules", "on-demand")
    head = fixture.git(repo, "rev-parse", "HEAD")
    # Git forwards the parent's refspec into the submodule. A hostile child
    # can provide that hexadecimal branch name, making the forwarded source
    # resolve to its own unpublished commit instead of failing as unknown.
    fixture.git(dependency, "branch", head, unpublished)
    flags = FIXED if fixed else "-u"
    command = render(["command", *canonical_tokens(repo, head)]) if fixed else f"{GIT} push {flags} origin {head}:refs/heads/work"
    result = exact_shell_replay(repo, remote, command)
    child_after = fixture.git(child_remote, "rev-parse", "refs/heads/work")
    result["child_changed"] = child_after != initial
    if fixed:
        assert result["hook_rc"] == 0 and result["shell_rc"] == 0 and result["suites"] == 1, result
        assert result["refs"] == {"refs/heads/work": head} and child_after == initial, result
    else:
        if result["hook_rc"] == 0:
            assert child_after == unpublished, repr(result)
        rejected(result)


@pytest.mark.parametrize("fixed", [False, True], ids=["legacy-red", "canonical-boundary"])
def test_snapshot_validatedhead_rejected(tmp_path, monkeypatch, fixed):
    """An interleaved commit between refspec validation and snapshot cannot be tested."""
    repo, remote, head, _ = scene(tmp_path)
    original = loom_checker._cmd_push
    injected = []
    def move_before_snapshot(args, out, err):
        fixture.git(repo, "commit", "--allow-empty", "-qm", "snapshot-gap commit")
        injected.append(fixture.git(repo, "rev-parse", "HEAD"))
        return original(args, out, err)
    monkeypatch.setattr(loom_checker, "_cmd_push", move_before_snapshot)
    flags = FIXED if fixed else "-u"
    command = render(["command", *canonical_tokens(repo, head)]) if fixed else f"{GIT} push {flags} origin {head}:refs/heads/work"
    monkeypatch.setattr(loom_checker, "read_hook_payload", lambda: {"cwd": str(repo), "tool_input": {"command": command}})
    monkeypatch.chdir(repo)
    output, errors = io.StringIO(), io.StringIO()
    rc = loom_checker.cmd_push(["--hook"], output, errors)
    if injected:
        assert injected[0] != head
    else:
        assert rc == 2, "the scheduling boundary was not exercised"
    assert rc == 2 and suites(repo) == 0 and refs(remote) == {}, {"rc": rc, "suites": suites(repo), "injected": bool(injected), "output": output.getvalue(), "errors": errors.getvalue()}
