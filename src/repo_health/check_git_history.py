"""
Checks that read the local clone's git history: commit volume, how concentrated
authorship is, and how recently dependencies were refreshed. No API calls.
"""
import subprocess
import time
from collections import Counter

import pytest
from pytest_repo_health import health_metadata

MODULE_DICT_KEY = "git"

LOCKFILE_PATHSPECS = (
    ("uv.lock",),
    (":(glob)requirements/**/*.txt",),
    ("package-lock.json",),
)

AUTOMATION_AUTHOR_MARKERS = ("[bot]", "-bot", "github-actions")


def _run_git(repo_path, *args):
    return subprocess.check_output(["git", "-C", repo_path, *args], text=True, stderr=subprocess.DEVNULL)


def _is_automation_author(name, email):
    identity = f"{name} {email}".lower()
    return any(marker in identity for marker in AUTOMATION_AUTHOR_MARKERS)


def human_commit_authors(repo_path, days):
    """Author email of every non-merge commit by a person in the last ``days`` days."""
    out = _run_git(repo_path, "log", "--no-merges", f"--since={days}.days.ago", "--format=%aN%x09%aE")
    authors = []
    for line in out.splitlines():
        name, _, email = line.partition("\t")
        if email and not _is_automation_author(name, email):
            authors.append(email.lower())
    return authors


def absence_factor(authors):
    """Smallest number of authors who together made at least half the commits.

    This is the CHAOSS Contributor Absence Factor (often called bus factor);
    None when there are no commits to measure.
    """
    if not authors:
        return None
    covered = 0
    for rank, (_, commits) in enumerate(Counter(authors).most_common(), start=1):
        covered += commits
        if covered * 2 >= len(authors):
            return rank
    return None


def lockfile_age_days(repo_path, now=None):
    """Days since the first lockfile kind present was last committed, or None."""
    now = now if now is not None else time.time()
    for pathspec in LOCKFILE_PATHSPECS:
        if not _run_git(repo_path, "ls-files", "--", *pathspec).strip():
            continue
        stamp = _run_git(repo_path, "log", "-1", "--format=%ct", "--", *pathspec).strip()
        if stamp.isdigit():
            return int((now - int(stamp)) // 86400)
    return None


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "commits_365d": "Non-merge commits by people in the last 365 days (automation excluded)",
        "absence_factor_365d": "Fewest people who made at least half of the last 365 days of commits "
                               "(CHAOSS Contributor Absence Factor); absent without commits",
        "lockfile_age_days": "Days since uv.lock, else requirements/*.txt, else package-lock.json "
                             "was last committed; absent when the repo has none",
    },
)
@pytest.mark.edx_health
def check_git_history(all_results, repo_path):
    """
    Commit volume, authorship concentration and dependency refresh age from local git.
    """
    try:
        authors = human_commit_authors(repo_path, 365)
        lockfile_age = lockfile_age_days(repo_path)
    except (subprocess.CalledProcessError, OSError):
        return
    results = all_results[MODULE_DICT_KEY]
    results["commits_365d"] = len(authors)
    factor = absence_factor(authors)
    if factor is not None:
        results["absence_factor_365d"] = factor
    if lockfile_age is not None:
        results["lockfile_age_days"] = lockfile_age
