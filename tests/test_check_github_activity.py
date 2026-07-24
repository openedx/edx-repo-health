"""Tests for the activity-signal checks in check_github."""

import subprocess
from datetime import datetime, timezone

from repo_health.check_github import (MODULE_DICT_KEY, _distinct_authors_since, _releases_last_12mo,
                                      check_activity_signals, parse_pr_activity)

REFERENCE = datetime(2026, 6, 1, tzinfo=timezone.utc)


def _pr(created, state, author, events):
    """Build a PR node. events: list of (created, login) for comments+reviews."""
    nodes = [{"createdAt": ts, "author": {"login": login}} for ts, login in events]
    return {
        "createdAt": created,
        "state": state,
        "author": {"login": author},
        "comments": {"nodes": nodes},
        "reviews": {"nodes": []},
    }


def test_parse_pr_activity_closure_ratio_and_median():
    nodes = [
        # opened in window, merged, first response 1 day after creation by a reviewer
        _pr("2026-05-20T00:00:00Z", "MERGED", "author1",
            [("2026-05-21T00:00:00Z", "reviewer")]),
        # opened in window, still open, first response 2 days later (bot ignored)
        _pr("2026-05-10T00:00:00Z", "OPEN", "author2",
            [("2026-05-10T01:00:00Z", "dependabot[bot]"), ("2026-05-12T00:00:00Z", "reviewer")]),
        # opened before the 90-day window — excluded entirely
        _pr("2026-01-01T00:00:00Z", "MERGED", "author3",
            [("2026-01-02T00:00:00Z", "reviewer")]),
    ]
    opened, closure_ratio, median_response = parse_pr_activity(nodes, REFERENCE)

    assert opened == 2                       # third PR excluded (out of window)
    assert closure_ratio == 0.5              # 1 of 2 in-window PRs closed/merged
    assert median_response == int((86400 + 172800) / 2)  # median of 1d and 2d


def test_parse_pr_activity_ignores_author_and_bot_responses():
    nodes = [
        _pr("2026-05-20T00:00:00Z", "OPEN", "me",
            [("2026-05-20T01:00:00Z", "me"), ("2026-05-20T02:00:00Z", "ci[bot]")]),
    ]
    opened, closure_ratio, median_response = parse_pr_activity(nodes, REFERENCE)
    assert opened == 1
    assert closure_ratio == 0.0
    assert median_response is None  # only self + bot responses → no measurable response


def test_parse_pr_activity_empty():
    assert parse_pr_activity([], REFERENCE) == (0, None, None)


def _init_repo(path):
    """Create a tiny git repo with one commit and a tag; return a git() runner."""
    def git(*args):
        subprocess.run(["git", "-C", str(path), *args], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    git("init")
    git("config", "user.email", "alice@example.com")
    git("config", "user.name", "Alice")
    (path / "f.txt").write_text("1")
    git("add", ".")
    git("commit", "-m", "one")
    git("tag", "v1.0.0")
    return git


def test_distinct_authors_and_releases_from_local_git(tmp_path):
    git = _init_repo(tmp_path)
    # second author, second tag
    git("config", "user.email", "bob@example.com")
    (tmp_path / "f.txt").write_text("2")
    git("commit", "-am", "two")
    git("tag", "v1.1.0")

    assert _distinct_authors_since(str(tmp_path), 90) == 2
    assert _releases_last_12mo(str(tmp_path)) == 2

    all_results = {MODULE_DICT_KEY: {}}
    check_activity_signals(all_results, repo_path=str(tmp_path))
    assert all_results[MODULE_DICT_KEY]["contributor_count_90d"] == 2
    assert all_results[MODULE_DICT_KEY]["release_count_12mo"] == 2


def test_local_git_helpers_are_resilient_to_bad_path(tmp_path):
    bad = tmp_path / "not-a-repo"
    bad.mkdir()
    assert _distinct_authors_since(str(bad), 90) is None
    assert _releases_last_12mo(str(bad)) is None
