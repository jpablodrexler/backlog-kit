#!/usr/bin/env python3
"""
Read-only facts for the `gitflow` skill's actions — what is on the branch, what would be
committed, what a PR would contain, which branches look finished. It never writes anything:
the skill itself performs (and asks permission for) every commit, push, PR and branch delete.

Usage:
    python3 flow_plan.py <repo-root> --action sync|commit|finish|cleanup [--fetch]

Prints JSON. Common fields: current_branch, base_branch, base_ref, on_base, branch_type
(feature|fix|other), branch_name, remote_branch_exists, ahead_of_remote, behind_remote,
`blockers` (reasons the action cannot proceed) and `warnings`. Per action:

  sync     behind_base: commits on base_ref that the branch lacks
  commit   files: every changed path (untracked included) with {kind: code|kit, suspicious},
           diff_stat, backlog_closed (rows this change adds to features-implemented / bugs-fixed)
  finish   commits (base_ref..HEAD), diff_stat, files, reports, backlog_closed, pushed, title
  cleanup  candidates: topic branches that are not current/base, with merged_into_base,
           just_started (the branch sits on the base tip: it has not diverged, so it is NOT
           reported as merged), upstream_gone, ahead_of_base and last_author. A squash-merged
           branch shows merged_into_base=false: confirm it through the PR before deleting it.
           Also `protected_branches`, which are never candidates.
"""
import argparse
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk
import gitread
import branch_state as bs

SUSPICIOUS = re.compile(
    r"(^|/)(\.env(\.[\w.-]+)?|id_(rsa|dsa|ecdsa|ed25519)|\.npmrc|\.pypirc|\.netrc|credentials(\.[\w.-]+)?"
    r"|[\w.-]*secret[\w.-]*|[\w.-]*\.(pem|key|p12|pfx|jks|keystore)|[\w.-]*e2e-credentials[\w.-]*)$", re.I)
SAFE_SUFFIX = re.compile(r"\.(example|sample|template|dist)$", re.I)


def topic(branch, cfg):
    g = cfg["git"]
    for kind, prefix in (("feature", g["feature_prefix"]), ("fix", g["fix_prefix"])):
        if prefix and branch.startswith(prefix):
            return kind, branch[len(prefix):]
    return "other", branch


def same_commit(root, a, b):
    ra = gitread.git(root, "rev-parse", "--verify", "--quiet", a, check=False).strip()
    rb = gitread.git(root, "rev-parse", "--verify", "--quiet", b, check=False).strip()
    return bool(ra) and ra == rb


def last_author(root, ref):
    return gitread.git(root, "log", "-1", "--format=%an", ref, check=False).strip()


def untracked(root):
    return lines(root, "ls-files", "--others", "--exclude-standard")


def line_count(path):
    try:
        if Path(path).stat().st_size > 1_000_000:
            return None
        return len(Path(path).read_text(encoding="utf-8").splitlines())
    except (UnicodeDecodeError, OSError):
        return None


def lines(root, *args):
    return [ln for ln in gitread.git(root, *args, check=False).splitlines() if ln.strip()]


def rows_added(diff_text, cfg):
    """Backlog rows a diff adds to features-implemented.md / bugs-fixed.md."""
    out = []
    prefix = re.escape(cfg["bugs"]["id_prefix"])
    for ln in diff_text.splitlines():
        if not ln.startswith("+|") or ln.startswith("+| -") or ln.startswith("+| #") or ln.startswith("+| Bug ID"):
            continue
        cells = bk.split_row(ln[1:])
        if not cells:
            continue
        m = re.match(rf"\[?({prefix}-\d+)", cells[0])
        if m:
            out.append({"kind": "bug", "id": m.group(1), "summary": cells[-1] if len(cells) > 5 else ""})
        elif cells[0].isdigit() and len(cells) > 1:
            out.append({"kind": "feature", "number": cells[0], "name": bk.strip_backticks(cells[1])})
    return out


def backlog_closed(root, cfg, rng):
    p = bk.Paths(root, cfg)
    out = []
    for path in (p.features_implemented, p.bugs_fixed):
        rel = str(Path(path).relative_to(root)).replace("\\", "/")
        out += rows_added(gitread.git(root, "diff", *rng, "--", rel, check=False), cfg)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--action", required=True, choices=["sync", "commit", "finish", "cleanup"])
    ap.add_argument("--fetch", action="store_true")
    a = ap.parse_args()
    root = a.repo_root
    cfg = bk.load_config(root)
    warnings, blockers = [], []
    if a.fetch:
        try:
            gitread.git(root, "fetch", "--prune")
        except gitread.GitError as e:
            warnings.append(f"git fetch failed ({e}); remote state may be stale")
    cur = bs.current_branch(root)
    base = bs.detect_base(root, cfg["git"]["base_branch"])
    base_ref = f"origin/{base}" if bs.ref_exists(root, f"refs/remotes/origin/{base}") else base
    kind, name = topic(cur, cfg)
    remote = bool(cur) and bs.ref_exists(root, f"refs/remotes/origin/{cur}")
    info = {"action": a.action, "current_branch": cur, "base_branch": base, "base_ref": base_ref,
            "on_base": cur == base, "branch_type": kind, "branch_name": name,
            "remote_branch_exists": remote,
            "ahead_of_remote": bs.count(root, f"origin/{cur}..HEAD") if remote else None,
            "behind_remote": bs.count(root, f"HEAD..origin/{cur}") if remote else None}
    if not cur:
        blockers.append("detached HEAD: switch to a branch first")
    protected = {base, *bs.PROTECTED_FALLBACK}
    changed = gitread.changed_files(root)

    if a.action == "sync":
        if cur in protected:
            blockers.append(f"'{cur}' is a base branch; sync works on a topic branch")
        if changed:
            blockers.append(f"uncommitted changes ({len(changed)}, e.g. {changed[0]}); commit them first")
        info["behind_base"] = bs.count(root, f"HEAD..{base_ref}")

    elif a.action == "commit":
        if cur in protected:
            blockers.append(f"'{cur}' is a base branch; commit on a topic branch (start one first)")
        if not changed:
            blockers.append("nothing to commit")
        globs = bk.kit_globs(cfg)
        info["files"] = [{"path": f, "kind": "kit" if bk.glob_match(f, globs) else "code",
                          "suspicious": bool(SUSPICIOUS.search(f)) and not SAFE_SUFFIX.search(f)} for f in changed]
        new = untracked(root)
        stat = gitread.git(root, "diff", "HEAD", "--stat", check=False).strip()
        new_lines = [f" {f} (new file, {n if n is not None else '?'} lines)" for f in new
                     for n in [line_count(Path(root) / f)]]
        info["untracked_files"] = new
        info["diff_stat"] = "\n".join(x for x in [stat, *new_lines] if x)
        info["backlog_closed"] = backlog_closed(root, cfg, ["HEAD"])
        if any(f["suspicious"] for f in info["files"]):
            warnings.append("some files look like secrets or credentials; never stage them without an explicit yes per file")

    elif a.action == "finish":
        if cur in protected:
            blockers.append(f"'{cur}' is a base branch; finish works on a topic branch")
        if changed:
            blockers.append(f"uncommitted changes ({len(changed)}, e.g. {changed[0]}); commit them first")
        ahead = bs.count(root, f"{base_ref}..HEAD")
        if ahead == 0:
            blockers.append(f"no commits ahead of {base_ref}: nothing to open a PR for")
        rng = [f"{base_ref}...HEAD"]
        files = lines(root, "diff", "--name-only", *rng)
        reports_dir = cfg["paths"]["reports_dir"].rstrip("/") + "/"
        info.update(commits=lines(root, "log", "--format=%h %s", f"{base_ref}..HEAD"), commit_count=ahead,
                    diff_stat=gitread.git(root, "diff", "--stat", *rng, check=False).strip(), files=files,
                    reports=[f for f in files if f.startswith(reports_dir)],
                    backlog_closed=backlog_closed(root, cfg, rng),
                    pushed=remote and info["ahead_of_remote"] == 0,
                    title={"feature": "Feature ", "fix": "Fix "}.get(kind, "") + name)
        if remote and info["behind_remote"]:
            blockers.append(f"origin/{cur} has {info['behind_remote']} commit(s) this branch lacks; reconcile it first")
        behind = bs.count(root, f"HEAD..{base_ref}")
        if behind:
            warnings.append(f"{base_ref} has {behind} commit(s) the branch lacks; consider `sync` before the PR")

    else:  # cleanup
        merged_local = {ln.strip().lstrip("* ") for ln in lines(root, "branch", "--merged", base_ref)}
        merged_remote = {ln.strip().split("origin/", 1)[-1] for ln in lines(root, "branch", "-r", "--merged", base_ref)}
        remote_names = {ln.split("origin/", 1)[-1] for ln in lines(root, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin")}
        cands = []
        for ln in lines(root, "for-each-ref", "--format=%(refname:short)|%(upstream:track)", "refs/heads"):
            br, _, track = ln.partition("|")
            k, _n = topic(br, cfg)
            if br == cur or br in protected or k == "other":
                continue
            ahead = bs.count(root, f"{base_ref}..{br}")
            fresh = same_commit(root, br, base_ref)
            # `git branch --merged` is also true for a branch that has not diverged yet. One that sits on
            # the base tip is a branch somebody just started: report it as such, never as merged.
            cands.append({"branch": br, "local": True, "remote": br in remote_names,
                          "merged_into_base": br in merged_local and not fresh, "just_started": fresh,
                          "upstream_gone": "gone" in track, "ahead_of_base": ahead,
                          "last_author": last_author(root, br)})
        for br in sorted(remote_names):
            k, _n = topic(br, cfg)
            if br not in {c["branch"] for c in cands} and br != cur and br not in protected and k != "other":
                fresh = same_commit(root, f"origin/{br}", base_ref)
                cands.append({"branch": br, "local": False, "remote": True,
                              "merged_into_base": br in merged_remote and not fresh, "just_started": fresh,
                              "upstream_gone": False, "ahead_of_base": bs.count(root, f"{base_ref}..origin/{br}"),
                              "last_author": last_author(root, f"origin/{br}")})
        info["candidates"] = cands
        info["protected_branches"] = sorted(protected)

    info.update(blockers=blockers, warnings=warnings)
    bk.emit(info)


if __name__ == "__main__":
    main()
