"""Tests for the activity-signal checks in check_github."""

import subprocess
from datetime import datetime, timezone

from repo_health.check_github import (MODULE_DICT_KEY, _distinct_authors_since, _releases_last_12mo,
                                      check_activity_signals, parse_issue_activity, parse_newcomers, parse_pr_activity,
                                      parse_pr_speed, pr_activity_results, repository_activity_results)

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


def test_pr_activity_results_reports_zero_opened_for_dormant_repo():
    """No PRs in the window: the count is an explicit 0 and the ratios stay absent."""
    nodes = [_pr("2026-01-01T00:00:00Z", "MERGED", "author", [("2026-01-02T00:00:00Z", "reviewer")])]

    assert pr_activity_results(nodes, REFERENCE) == {"pr_opened_90d": 0}


def test_pr_activity_results_includes_all_keys_when_measurable():
    nodes = [_pr("2026-05-20T00:00:00Z", "MERGED", "author", [("2026-05-21T00:00:00Z", "reviewer")])]

    assert pr_activity_results(nodes, REFERENCE) == {
        "pr_opened_90d": 1,
        "pr_closure_ratio_90d": 1.0,
        "median_pr_response_seconds": 86400,
    }


def test_pr_activity_results_omits_median_without_responses():
    nodes = [_pr("2026-05-20T00:00:00Z", "OPEN", "me", [("2026-05-20T01:00:00Z", "me")])]

    assert pr_activity_results(nodes, REFERENCE) == {"pr_opened_90d": 1, "pr_closure_ratio_90d": 0.0}


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


def _node(created, *, state="OPEN", merged=None, closed=None, association="MEMBER", author="author", events=()):
    return {
        "createdAt": created,
        "mergedAt": merged,
        "closedAt": closed,
        "state": state,
        "authorAssociation": association,
        "author": {"login": author},
        "comments": {"nodes": [{"createdAt": ts, "author": {"login": login}} for ts, login in events]},
        "reviews": {"nodes": []},
    }


def test_parse_pr_speed_uses_prs_merged_in_the_window():
    nodes = [
        _node("2026-05-01T00:00:00Z", state="MERGED", merged="2026-05-03T00:00:00Z"),
        _node("2026-05-10T00:00:00Z", state="MERGED", merged="2026-05-11T00:00:00Z"),
        _node("2025-12-01T00:00:00Z", state="MERGED", merged="2025-12-02T00:00:00Z"),
        _node("2026-05-20T00:00:00Z"),
    ]

    assert parse_pr_speed(nodes, REFERENCE) == int((2 * 86400 + 86400) / 2)


def test_parse_pr_speed_none_without_merges():
    assert parse_pr_speed([_node("2026-05-20T00:00:00Z")], REFERENCE) is None


def test_parse_newcomers_counts_first_time_contributors_and_skips_bots():
    nodes = [
        _node("2026-05-20T00:00:00Z", association="FIRST_TIME_CONTRIBUTOR", author="new1",
              events=[("2026-05-21T00:00:00Z", "maintainer")]),
        _node("2026-05-18T00:00:00Z", association="FIRST_TIMER", author="new2"),
        _node("2026-05-19T00:00:00Z", association="FIRST_TIME_CONTRIBUTOR", author="helper[bot]"),
        _node("2026-05-19T00:00:00Z", association="CONTRIBUTOR", author="regular"),
        _node("2026-01-01T00:00:00Z", association="FIRST_TIME_CONTRIBUTOR", author="old"),
    ]

    assert parse_newcomers(nodes, REFERENCE) == (2, 86400)


def test_parse_issue_activity_counts_flow_and_stale_backlog():
    nodes = [
        _node("2026-05-20T00:00:00Z", state="CLOSED", closed="2026-05-22T00:00:00Z", author="u1",
              events=[("2026-05-20T12:00:00Z", "maintainer")]),
        _node("2026-05-25T00:00:00Z", author="u2"),
        _node("2025-10-01T00:00:00Z", author="u3"),
        _node("2026-05-26T00:00:00Z", author="renovate[bot]"),
    ]

    assert parse_issue_activity(nodes, REFERENCE) == (2, 0.5, 43200, 1)


def test_repository_activity_results_combines_every_signal():
    repository = {
        "defaultBranchRef": {"target": {"statusCheckRollup": {"state": "FAILURE"}}},
        "openIssues": {"totalCount": 4},
        "openPullRequests": {"totalCount": 2},
        "oldestOpenPullRequest": {"nodes": [{"createdAt": "2026-05-01T00:00:00Z"}]},
        "goodFirstIssue": {"issues": {"totalCount": 3}},
        "issues": {"nodes": [_node("2026-05-25T00:00:00Z", author="u1")]},
        "pullRequests": {"nodes": [
            _node("2026-05-20T00:00:00Z", state="MERGED", merged="2026-05-21T00:00:00Z",
                  association="FIRST_TIME_CONTRIBUTOR", author="new", events=[("2026-05-20T06:00:00Z", "maintainer")]),
        ]},
    }

    results = repository_activity_results(repository, REFERENCE)

    assert results == {
        "pr_opened_90d": 1,
        "pr_closure_ratio_90d": 1.0,
        "median_pr_response_seconds": 21600,
        "default_branch_ci_state": "FAILURE",
        "issues_open": 4,
        "prs_open": 2,
        "oldest_open_pr_days": 31,
        "good_first_issues_open": 3,
        "median_pr_time_to_merge_seconds": 86400,
        "first_timer_prs_90d": 1,
        "first_timer_median_first_response_seconds": 21600,
        "issues_opened_90d": 1,
        "issues_stale_open_180d": 0,
        "issue_closure_ratio_90d": 0.0,
    }


def test_repository_without_checks_or_label_leaves_ci_absent_and_counts_zero():
    repository = {"defaultBranchRef": {"target": {"statusCheckRollup": None}}, "goodFirstIssue": None,
                  "issues": {"nodes": []}, "pullRequests": {"nodes": []}}

    results = repository_activity_results(repository, REFERENCE)

    assert "default_branch_ci_state" not in results
    assert results["good_first_issues_open"] == 0
    assert results["first_timer_prs_90d"] == 0
    assert results["issues_opened_90d"] == 0
    assert "issue_closure_ratio_90d" not in results


def test_automation_accounts_do_not_count_as_responses():
    nodes = [_node("2026-05-20T00:00:00Z", association="FIRST_TIME_CONTRIBUTOR", author="new",
                   events=[("2026-05-20T00:00:05Z", "openedx-webhooks"),
                           ("2026-05-20T00:01:00Z", "edx-requirements-bot"),
                           ("2026-05-21T00:00:00Z", "maintainer")])]

    assert parse_newcomers(nodes, REFERENCE) == (1, 86400)


def test_github_app_actors_do_not_count_as_responses():
    node = _node("2026-05-20T00:00:00Z", association="FIRST_TIME_CONTRIBUTOR", author="new")
    node["comments"]["nodes"] = [
        {"createdAt": "2026-05-20T00:00:10Z", "author": {"__typename": "Bot", "login": "dependabot"}},
        {"createdAt": "2026-05-22T00:00:00Z", "author": {"__typename": "User", "login": "maintainer"}},
    ]

    assert parse_newcomers([node], REFERENCE) == (1, 172800)


def test_pr_response_ignores_prs_opened_by_automation():
    nodes = [
        _node("2026-05-20T00:00:00Z", author="renovate", events=[("2026-05-20T00:00:30Z", "maintainer")]),
        _node("2026-05-20T00:00:00Z", author="person", events=[("2026-05-21T00:00:00Z", "maintainer")]),
    ]
    nodes[0]["author"]["__typename"] = "Bot"

    assert parse_pr_activity(nodes, REFERENCE) == (2, 0.0, 86400)


def test_parse_newcomers_counts_none_association_seen_by_tokens_without_push_access():
    nodes = [
        _node("2026-05-20T00:00:00Z", association="NONE", author="new1",
              events=[("2026-05-20T12:00:00Z", "maintainer")]),
        _node("2026-05-19T00:00:00Z", association="NONE", author="dependabot"),
        _node("2026-05-18T00:00:00Z", association="CONTRIBUTOR", author="private-member"),
    ]
    nodes[1]["author"]["__typename"] = "Bot"

    assert parse_newcomers(nodes, REFERENCE) == (1, 43200)
