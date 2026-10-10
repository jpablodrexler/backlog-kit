#!/usr/bin/env python3
"""
The only place in backlog-kit that talks to git, and it is deliberately
read-mostly: an allowlist of subcommands, none of which can create a commit,
move a ref to new content, or publish anything.

    status rev-parse branch rev-list symbolic-ref for-each-ref diff ls-files log   (read)
    fetch                                                      (updates remote-tracking refs only)

`branch` is further limited to listing/showing; the destructive and renaming
flags are refused. The kit's public promise — Claude never commits, pushes or
opens a PR on the user's behalf — is enforced here in code, and by
tests/test_skills.py, which fails if any other script imports subprocess.
Branch creation/switching is done by the work skills' subagents and is
documented there; it is not routed through this module.
"""
import subprocess

READ_ONLY = {"status", "rev-parse", "branch", "rev-list", "symbolic-ref",
             "for-each-ref", "diff", "ls-files", "log"}
ALLOWED = READ_ONLY | {"fetch"}
BRANCH_REFUSED = {"-d", "-D", "-m", "-M", "-c", "-C", "-f", "-u", "--delete", "--move",
                  "--copy", "--force", "--set-upstream-to", "--unset-upstream", "--edit-description"}
FETCH_REFUSED = {"--update-head-ok", "--force", "-f"}


class GitError(RuntimeError):
    pass


def _run(root, *args):
    if not args or args[0] not in ALLOWED:
        raise GitError(f"git {args[0] if args else ''} is not allowed from backlog-kit scripts")
    if args[0] == "branch" and BRANCH_REFUSED & set(args[1:]):
        raise GitError("git branch is limited to listing / showing the current branch")
    if args[0] == "fetch" and FETCH_REFUSED & set(args[1:]):
        raise GitError("git fetch flag not allowed")
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def git(root, *args, check=True):
    """Run an allowlisted git subcommand in `root`; return stdout (text)."""
    proc = _run(root, *args)
    if check and proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {args[0]} failed")
    return proc.stdout


def ok(root, *args):
    """True if the allowlisted git command exits 0 (never raises on a non-zero exit)."""
    return _run(root, *args).returncode == 0


def changed_files(root):
    """Every path with working-tree or index changes, untracked files included.

    Uses `status --porcelain=v1 -z -uall` — the reliable way to see new files too
    (`git diff --name-only HEAD` misses untracked ones, and a branch-to-branch diff
    shows nothing when nothing is committed). Renames report the new path.
    """
    out = git(root, "status", "--porcelain=v1", "-z", "-uall")
    files, parts, i = [], out.split("\0"), 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if len(entry) < 4:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            i += 1  # skip the "from" path that follows a rename/copy entry
        files.append(path)
    return sorted(set(files))
