#!/usr/bin/env python3
"""
Decide what the branch-setup phase should do — read-only.

Inspects the repo (current branch, dirty tree, whether the target branch exists
locally / on origin, how it diverges) and returns ONE recommended action for the
subagent to carry out. The script never changes anything; creating or switching
a branch is done by the subagent with plain `git switch`, and nothing in the
kit ever merges, rebases, commits or pushes.

Actions:
  resume          already on the target branch, nothing to reconcile
  fast-forward    on the target branch, origin has newer commits and local has none
                  of its own  -> `git merge --ff-only origin/<branch>`
  checkout        branch exists locally -> `git switch <branch>`
  checkout-ff     exists locally and origin is ahead (no local-only commits)
                  -> `git switch <branch>` then `git merge --ff-only origin/<branch>`
  track-remote    exists only on origin -> `git switch -c <branch> --track origin/<branch>`
  create          neither exists -> `git switch -c <branch> --no-track <start>`
                  (--no-track: a plain `git push` must never aim at the base branch)
  batch-ok        --batch: caller owns the branch, current one is fine
  blocked         see `reason` (uncommitted work outside backlog-kit's own files, a diverged branch, ...)

Usage:
    python3 branch_state.py <repo-root> --branch <name> [--fetch] [--batch]
"""
import argparse
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk
import gitread

PROTECTED_FALLBACK = ("main", "master", "develop", "trunk")


def current_branch(root):
    return gitread.git(root, "branch", "--show-current").strip()


def ref_exists(root, ref):
    return gitread.ok(root, "rev-parse", "--verify", "--quiet", ref)


def count(root, rng):
    try:
        return int(gitread.git(root, "rev-list", "--count", rng).strip())
    except gitread.GitError:
        return 0


def detect_base(root, configured):
    if configured:
        return configured
    try:
        head = gitread.git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
        return head.split("/", 1)[1] if "/" in head else head
    except gitread.GitError:
        pass
    for cand in PROTECTED_FALLBACK:
        if ref_exists(root, f"refs/heads/{cand}") or ref_exists(root, f"refs/remotes/origin/{cand}"):
            return cand
    return "main"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--branch", required=True)
    ap.add_argument("--fetch", action="store_true", help="run `git fetch --prune` first")
    ap.add_argument("--batch", action="store_true", help="caller owns branch state; only verify it isn't a protected branch")
    args = ap.parse_args()

    root, branch = args.repo_root, args.branch
    cfg = bk.load_config(root)
    warnings = []
    if args.fetch:
        try:
            gitread.git(root, "fetch", "--prune")
        except gitread.GitError as e:
            warnings.append(f"git fetch failed ({e}); remote state may be stale")

    cur = current_branch(root)
    base = detect_base(root, cfg["git"]["base_branch"])
    protected = {base, *PROTECTED_FALLBACK}
    changed = gitread.changed_files(root)
    blocking = [f for f in changed if not bk.glob_match(f, bk.kit_globs(cfg))]
    dirty = bool(blocking)
    local = ref_exists(root, f"refs/heads/{branch}")
    remote = ref_exists(root, f"refs/remotes/origin/{branch}")
    start = f"origin/{base}" if ref_exists(root, f"refs/remotes/origin/{base}") else base

    info = {"branch": branch, "current_branch": cur, "base_branch": base, "start_point": start,
            "dirty": dirty, "dirty_files": blocking[:10], "kit_files_changed": len(changed) - len(blocking),
            "local_exists": local, "remote_exists": remote, "warnings": warnings}

    def done(action, reason=""):
        info.update(action=action, reason=reason)
        bk.emit(info)
        sys.exit(0)

    if args.batch:
        if not cur or cur in protected:
            done("blocked", f"batch mode needs an existing work branch already checked out, not '{cur or 'detached HEAD'}'")
        done("batch-ok", f"working on '{cur}'; branch state is the caller's")

    # Resume check comes BEFORE the dirty check: an interrupted run leaves its
    # in-progress work uncommitted on the right branch, which is expected state.
    if cur == branch:
        if remote:
            behind = count(root, f"HEAD..origin/{branch}")
            ahead = count(root, f"origin/{branch}..HEAD")
            info.update(behind_remote=behind, ahead_of_remote=ahead)
            if behind and ahead:
                done("blocked", f"'{branch}' has diverged from origin ({ahead} local-only, {behind} remote-only commits); reconcile it manually")
            if behind:
                done("fast-forward", f"origin/{branch} has {behind} commit(s) not present locally")
        done("resume")

    if dirty:
        done("blocked", f"uncommitted changes outside backlog-kit's own files ({len(blocking)}, e.g. {blocking[0]}); commit or stash them before switching branches")
    if local:
        if remote:
            behind = count(root, f"{branch}..origin/{branch}")
            ahead = count(root, f"origin/{branch}..{branch}")
            info.update(behind_remote=behind, ahead_of_remote=ahead)
            if behind and ahead:
                done("blocked", f"local '{branch}' has diverged from origin ({ahead} local-only, {behind} remote-only commits); reconcile it manually")
            if behind:
                done("checkout-ff", f"origin/{branch} has {behind} commit(s) not present locally")
        done("checkout")
    if remote:
        done("track-remote", f"'{branch}' exists only on origin (pushed from another machine)")
    if not ref_exists(root, f"refs/heads/{base}") and not ref_exists(root, f"refs/remotes/origin/{base}"):
        done("blocked", f"base branch '{base}' not found; set [git] base_branch in .backlog-kit.toml")
    done("create", f"new branch from {start}")


if __name__ == "__main__":
    main()
