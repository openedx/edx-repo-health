"""
Checks to collect useful information from the GitHub API about the target repository.
"""
import functools
import json
import logging
import operator
import os
import re
import statistics
import subprocess
import time
from datetime import datetime, timedelta, timezone

import pytest
import requests
from pytest_repo_health import add_key_to_metadata, health_metadata

from .queries import FETCH_BUILD_CHECK_RUNS
from .utils import github_org_repo, parse_build_duration_response

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "github"

FETCH_REPOSITORY_LANGUAGES = """
query fetch_repository_languages ($repository_id: ID!, $cursor: String=null) {
  node (id: $repository_id) {
    ... on Repository {
      languages (first: 10, after: $cursor) {
        edges {
          node {
            __typename
            color
            id
            name
          }
          size
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
  }
}
"""

LANGUAGES = [
    "css",
    "dockerfile",
    "html",
    "javascript",
    "makefile",
    "python",
    "shell",
]


async def fetch_languages(repo):
    """
    Fetch the number of bytes of each language in the target repo from the GitHub API.
    This should ideally be part of github.py, but it hasn't been implemented there yet.
    """
    client = repo.http
    kwargs = {"repository_id": repo.id}
    edges = []

    cursor = None
    has_next_page = True

    while has_next_page:
        _json = {
            "query": FETCH_REPOSITORY_LANGUAGES,
            "variables": kwargs.update(cursor=cursor) or kwargs,
        }

        data = await client.request(json=_json)
        data = functools.reduce(operator.getitem, ["node", "languages"], data)

        edges.extend(data["edges"])

        cursor = data["pageInfo"]["endCursor"]
        has_next_page = data["pageInfo"]["hasNextPage"]

    result = {}
    for edge in edges:
        name = edge["node"]["name"]
        result[name.lower()] = edge["size"]
    return result


@add_key_to_metadata((MODULE_DICT_KEY, "build_details"))
@pytest.mark.asyncio
@pytest.mark.edx_health
async def check_build_duration(all_results, github_repo):
    """
    Fetches the builds details from Github and calculates the duration of each build
    """
    github_repo = await github_repo
    repo = github_repo.object
    client = repo.http
    kwargs = {"repository_id": repo.id}

    _json = {
        "query": FETCH_BUILD_CHECK_RUNS,
        "variables": kwargs,
    }

    data = await client.request(json=_json)
    parsed = parse_build_duration_response(data)
    if parsed is None:  # uninitialized repo
        return
    total_duration, checks_list = parsed

    all_results[MODULE_DICT_KEY]['build_details'] = json.dumps({
        'total_duration': total_duration,
        'checks': checks_list
    })

# GitHub uses https://licensee.github.io/licensee/ to figure out the license of a git repository.
# Unfortunately, some repositories set their license in a way that does not work with `licensee`.
# repo_license_exemptions is used to fill in license info for these repositories.
# it documents: (repo name, license name, more info (link to license), owner (repo org))
# Since edx/edx-repo-health is a public repository,
# info about private repositories should not be added here without some deliberation
repo_license_exemptions = {
    "gocd-vault-secret-plugin": {
        "license": "Apache License 2.0",
        "more_info": "https://github.com/edx/gocd-vault-secret-plugin/blob/v1.2.0-66-exp/.idea/copyright/Apache_2_0.xml",  # pylint: disable=line-too-long, useless-suppression
        "owner": "edx",
    },
}


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "allows_merge_commit": "Are PRs merged with a merge commit on the repository?",
        "allows_rebase_merge": "Is rebase-merging enabled on the repository?",
        "allows_squash_merge": "Is squash-merging enabled on the repository?",
        "code_of_conduct": "The name of the code of conduct for the repository (if any)",
        "created_at": "The date and time when the repository was created.",
        "default_branch": "The name of the repository's default branch",
        "description": "The description text for the repository (if any)",
        "disk_usage_kb": "The number of kilobytes the repository occupies on disk",
        "fork_count": "How many GitHub forks there are of the repository",
        "has_issues": "Is the repository's the issues feature enabled?",
        "has_wiki": "Is the repository's wiki feature enabled?",
        "is_archived": "Is the repository unmaintained?",
        "is_disabled": "Is the repository disabled?",
        "is_locked": "Has the repository been locked?",
        "is_private": "Is the repository private?",
        "last_push": "When was the repository last pushed to?",
        "license": "The name of the repository's software license",
    },
)
@pytest.mark.asyncio
@pytest.mark.edx_health
async def check_settings(all_results, github_repo):
    """
    Get all the fields of interest from the GitHub repository object itself.
    """
    github_repo = await github_repo
    message = github_repo.message
    github_repo = github_repo.object

    if github_repo is None:
        logger.error(message)
        pytest.skip("There was an error fetching data from GitHub")

    results = all_results[MODULE_DICT_KEY]
    results["allows_merge_commit"] = github_repo.allows_merge_commit
    results["allows_rebase_merge"] = github_repo.allows_rebase_merge
    results["allows_squash_merge"] = github_repo.allows_squash_merge
    coc = github_repo.code_of_conduct
    results["code_of_conduct"] = coc.name if coc else None
    results["created_at"] = github_repo.created_at
    try:
        results["default_branch"] = github_repo.default_branch
    except TypeError:
        results['default_branch'] = None
    results["description"] = github_repo.description
    results["disk_usage_kb"] = github_repo.disk_usage
    results["fork_count"] = github_repo.fork_count
    results["has_issues"] = github_repo.has_issues
    results["has_wiki"] = github_repo.has_wiki
    results["is_archived"] = github_repo.is_archived
    results["is_disabled"] = github_repo.is_disabled
    results["is_fork"] = github_repo.is_fork
    results["is_locked"] = github_repo.is_locked
    results["is_private"] = github_repo.is_private
    results["last_push"] = github_repo.pushed_at
    repo_license = github_repo.license
    if repo_license is None:
        if (
            github_repo.name in repo_license_exemptions
            and github_repo.owner.login == repo_license_exemptions[github_repo.name]["owner"]
        ):
            results["license"] = repo_license_exemptions[github_repo.name]["license"]
        else:
            results["license"] = None
    else:
        results["license"] = repo_license.nickname or repo_license.name


@health_metadata(
    ["language_bytes"],
    {
        "css": "The number of bytes of CSS files in the repository",
        "dockerfile": "The number of bytes of Dockerfiles in the repository",
        "go": "The number of bytes of Go code in the repository",
        "groovy": "The number of bytes of Groovy code in the repository",
        "html": "The number of bytes of HTML files in the repository",
        "java": "The number of bytes of Java code in the repository",
        "javascript": "The number of bytes of JavaScript code in the repository",
        "makefile": "The number of bytes of Makefiles in the repository",
        "objective-c": "The number of bytes of Objective-C code in the repository",
        "php": "The number of bytes of PHP code in the repository",
        "python": "The number of bytes of Python code in the repository",
        "ruby": "The number of bytes of Ruby code in the repository",
        "shell": "The number of bytes of shell scripts in the repository",
    }
)
@pytest.mark.asyncio
@pytest.mark.edx_health
async def check_languages(all_results, github_repo):
    """
    Get the number of bytes of each programming language in the repository.
    """
    github_repo = await github_repo
    message = github_repo.message
    github_repo = github_repo.object
    if github_repo is None:
        logger.error(message)
        pytest.skip("There was an error fetching data from GitHub")

    results = all_results["language_bytes"]
    languages = await fetch_languages(github_repo)
    for language in LANGUAGES:
        if language in languages:
            results[language] = languages[language]
        else:
            results[language] = 0


def get_branch_or_pr_count(org_name, repo_name, pulls_or_branches):
    """
    Get the count for branches or pull requests using Github API and add the count to report
    """
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/{pulls_or_branches}?per_page=1"
    count = 0

    response = requests.get(url=url, headers={'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}'})
    if response.ok and json.loads(response.content):
        count = 1
        if 'last' in response.links:
            last_page = response.links['last']['url']
            count = int(re.findall(r'page=(\d+)', last_page)[1])

    return count


@pytest.mark.py_dependency_health
@pytest.mark.edx_health
def check_branch_and_pr_count(all_results, git_origin_url):
    """
    Checks repository integrated with github actions workflow
    """
    org_name, repo_name = github_org_repo(git_origin_url)
    all_results[MODULE_DICT_KEY]['branch_count'] = get_branch_or_pr_count(org_name, repo_name, 'branches')
    all_results[MODULE_DICT_KEY]['pulls_count'] = get_branch_or_pr_count(org_name, repo_name, 'pulls')


# ---------------------------------------------------------------------------
# Activity signals feeding the dashboard's activity score metrics
# ---------------------------------------------------------------------------

# Recent PRs for closure-ratio and first-response metrics. Capped at 100 PRs
# (one query, no pagination) to stay within the Actions token budget; for very
# active repos this may not cover a full 90-day window — a documented limit.
FETCH_RECENT_PRS = """
query recent_activity ($owner: String!, $name: String!) {
  repository (owner: $owner, name: $name) {
    defaultBranchRef { target { ... on Commit { statusCheckRollup { state } } } }
    openIssues: issues (states: OPEN) { totalCount }
    openPullRequests: pullRequests (states: OPEN) { totalCount }
    oldestOpenPullRequest: pullRequests (states: OPEN, first: 1, orderBy: {field: CREATED_AT, direction: ASC}) {
      nodes { createdAt }
    }
    goodFirstIssue: label (name: "good first issue") { issues (states: OPEN) { totalCount } }
    issues (first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        createdAt
        closedAt
        state
        authorAssociation
        author { __typename login }
        comments (first: 10) { nodes { createdAt author { __typename login } } }
      }
    }
    pullRequests (first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        createdAt
        mergedAt
        state
        authorAssociation
        author { __typename login }
        comments (first: 20) { nodes { createdAt author { __typename login } } }
        reviews (first: 10) { nodes { createdAt author { __typename login } } }
      }
    }
  }
}
"""

NEWCOMER_ASSOCIATIONS = {"FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER"}


def _run_git(repo_path, *args):
    """Run a git command in repo_path, returning stdout (raises on failure)."""
    return subprocess.check_output(
        ["git", "-C", repo_path, *args], text=True, stderr=subprocess.DEVNULL
    )


def _distinct_authors_since(repo_path, days):
    """Count distinct commit-author emails in the last ``days`` days (local git)."""
    try:
        out = _run_git(repo_path, "log", f"--since={days}.days.ago", "--format=%ae")
    except (subprocess.CalledProcessError, OSError):
        return None
    return len({line.strip() for line in out.splitlines() if line.strip()})


def _releases_last_12mo(repo_path, *, now=None):
    """Count git tags created in the last 12 months (local git, no API)."""
    try:
        out = _run_git(repo_path, "for-each-ref", "--format=%(creatordate:unix)", "refs/tags")
    except (subprocess.CalledProcessError, OSError):
        return None
    cutoff = (now if now is not None else time.time()) - 365 * 24 * 3600
    count = 0
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit() and int(line) >= cutoff:
            count += 1
    return count


def _parse_github_dt(value):
    """Parse a GitHub ISO-8601 UTC timestamp; None on failure."""
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


# GitHub Apps come back as __typename Bot; these automation accounts are plain Users.
AUTOMATION_LOGINS = {"web-flow", "openedx-webhooks", "codecov-commenter", "sonarcloud"}


def _is_automation(actor):
    actor = actor or {}
    login = (actor.get("login") or "").lower()
    return (
        not login
        or actor.get("__typename") == "Bot"
        or login.endswith(("[bot]", "-bot"))
        or login in AUTOMATION_LOGINS
    )


def _first_response_seconds(item):
    """Seconds from creation to the first comment/review by someone other than
    the author (bots excluded), or None when nobody else has responded."""
    created = _parse_github_dt(item.get("createdAt"))
    if created is None:
        return None
    author = ((item.get("author") or {}).get("login") or "").lower()
    events = list((item.get("comments") or {}).get("nodes", []))
    events += list((item.get("reviews") or {}).get("nodes", []))
    stamps = []
    for event in events:
        actor = event.get("author") or {}
        if _is_automation(actor) or (actor.get("login") or "").lower() == author:
            continue
        stamp = _parse_github_dt(event.get("createdAt"))
        if stamp is not None:
            stamps.append(stamp)
    return (min(stamps) - created).total_seconds() if stamps else None


def _in_window(item, reference_dt, window_days):
    created = _parse_github_dt(item.get("createdAt"))
    return created is not None and created >= reference_dt - timedelta(days=window_days)


def _median(values):
    return int(statistics.median(values)) if values else None


def parse_pr_activity(nodes, reference_dt, window_days=90):
    """Return (opened_count, closure_ratio, median_first_response_seconds).

    - closure_ratio: PRs opened in the window that are now CLOSED/MERGED, over
      all PRs opened in the window (None when none opened).
    - median_first_response_seconds: median seconds from PR creation to the
      first review/comment by someone other than the author, on PRs opened by
      people; automation authors and responders are excluded;
      None when there are no measurable responses.
    """
    recent = [pr for pr in nodes or [] if _in_window(pr, reference_dt, window_days)]
    opened = len(recent)
    closed = sum(pr.get("state") in {"CLOSED", "MERGED"} for pr in recent)
    human_authored = [pr for pr in recent if not _is_automation(pr.get("author"))]
    response_seconds = [seconds for seconds in map(_first_response_seconds, human_authored) if seconds is not None]
    closure_ratio = round(closed / opened, 4) if opened else None
    median_response = int(statistics.median(response_seconds)) if response_seconds else None
    return opened, closure_ratio, median_response


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "contributor_count_90d": "Distinct commit authors in the last 90 days",
        "release_count_12mo": "Number of release tags created in the last 12 months",
    },
)
@pytest.mark.edx_health
def check_activity_signals(all_results, repo_path):
    """
    Local-git activity signals (no GitHub API): recent contributors and releases.
    """
    results = all_results[MODULE_DICT_KEY]
    results["contributor_count_90d"] = _distinct_authors_since(repo_path, 90)
    results["release_count_12mo"] = _releases_last_12mo(repo_path)


def parse_pr_speed(nodes, reference_dt, window_days=90):
    """Median seconds from creation to merge for PRs merged in the window."""
    cutoff = reference_dt - timedelta(days=window_days)
    durations = []
    for pr in nodes or []:
        created = _parse_github_dt(pr.get("createdAt"))
        merged = _parse_github_dt(pr.get("mergedAt"))
        if created and merged and merged >= cutoff:
            durations.append((merged - created).total_seconds())
    return _median(durations)


def parse_newcomers(nodes, reference_dt, window_days=90):
    """(first-timer PRs opened in the window, their median first-response seconds).

    A first-timer is GitHub's FIRST_TIME_CONTRIBUTOR / FIRST_TIMER association on
    the PR, bots excluded. Only these aggregates are emitted, never the authors.
    """
    firsts = [
        pr for pr in nodes or []
        if _in_window(pr, reference_dt, window_days)
        and pr.get("authorAssociation") in NEWCOMER_ASSOCIATIONS
        and not _is_automation(pr.get("author"))
    ]
    responses = [seconds for seconds in map(_first_response_seconds, firsts) if seconds is not None]
    return len(firsts), _median(responses)


def parse_issue_activity(nodes, reference_dt, window_days=90, stale_days=180):
    """(opened in window, closure ratio, median first response seconds, stale open count).

    Counted from the 100 most recent issues, so values saturate on very busy repos.
    """
    issues = [issue for issue in nodes or [] if not _is_automation(issue.get("author"))]
    recent = [issue for issue in issues if _in_window(issue, reference_dt, window_days)]
    closed = sum(issue.get("state") == "CLOSED" for issue in recent)
    closure_ratio = round(closed / len(recent), 4) if recent else None
    responses = [seconds for seconds in map(_first_response_seconds, recent) if seconds is not None]
    stale_cutoff = reference_dt - timedelta(days=stale_days)
    stale = sum(
        issue.get("state") == "OPEN" and (_parse_github_dt(issue.get("createdAt")) or reference_dt) < stale_cutoff
        for issue in issues
    )
    return len(recent), closure_ratio, _median(responses), stale


def _total(repository, field):
    return ((repository.get(field) or {}).get("totalCount"))


def repository_snapshot_results(repository, reference_dt):
    """Point-in-time counts and states from the activity query."""
    results = {}
    target = ((repository.get("defaultBranchRef") or {}).get("target") or {})
    rollup = target.get("statusCheckRollup") or {}
    if rollup.get("state"):
        results["default_branch_ci_state"] = rollup["state"]
    for key, field in (("issues_open", "openIssues"), ("prs_open", "openPullRequests")):
        if _total(repository, field) is not None:
            results[key] = _total(repository, field)
    oldest = ((repository.get("oldestOpenPullRequest") or {}).get("nodes") or [])
    oldest_created = _parse_github_dt(oldest[0].get("createdAt")) if oldest else None
    if oldest_created:
        results["oldest_open_pr_days"] = (reference_dt - oldest_created).days
    label = repository.get("goodFirstIssue")
    results["good_first_issues_open"] = ((label or {}).get("issues") or {}).get("totalCount") or 0
    return results


def repository_activity_results(repository, reference_dt):
    """Every result key the activity query feeds; undefined values stay absent."""
    pr_nodes = (repository.get("pullRequests") or {}).get("nodes", [])
    issue_nodes = (repository.get("issues") or {}).get("nodes", [])
    results = pr_activity_results(pr_nodes, reference_dt)
    results.update(repository_snapshot_results(repository, reference_dt))

    time_to_merge = parse_pr_speed(pr_nodes, reference_dt)
    if time_to_merge is not None:
        results["median_pr_time_to_merge_seconds"] = time_to_merge

    first_timer_prs, first_timer_response = parse_newcomers(pr_nodes, reference_dt)
    results["first_timer_prs_90d"] = first_timer_prs
    if first_timer_response is not None:
        results["first_timer_median_first_response_seconds"] = first_timer_response

    opened, closure, response, stale = parse_issue_activity(issue_nodes, reference_dt)
    results["issues_opened_90d"] = opened
    results["issues_stale_open_180d"] = stale
    if closure is not None:
        results["issue_closure_ratio_90d"] = closure
    if response is not None:
        results["median_issue_first_response_seconds"] = response
    return results


def pr_activity_results(nodes, reference_dt):
    """Map fetched PR nodes to the result keys check_pr_activity emits.

    ``pr_opened_90d`` is always present, so a repo with no recent PRs reads 0
    rather than blank. The ratio and median stay absent in that case: they are
    undefined, not zero.
    """
    opened, closure_ratio, median_response = parse_pr_activity(nodes, reference_dt)
    results = {"pr_opened_90d": opened}
    if closure_ratio is not None:
        results["pr_closure_ratio_90d"] = closure_ratio
    if median_response is not None:
        results["median_pr_response_seconds"] = median_response
    return results


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "pr_opened_90d": "PRs opened in the last 90 days (counted from the 100 most recent PRs, so capped at 100)",
        "pr_closure_ratio_90d": "Closed/merged over opened PRs in the last 90 days",
        "median_pr_response_seconds": "Median seconds to first non-author response on recent PRs",
        "median_pr_time_to_merge_seconds": "Median seconds from creation to merge for PRs merged in the last 90 days",
        "prs_open": "Open pull requests",
        "oldest_open_pr_days": "Age in days of the oldest open pull request",
        "default_branch_ci_state": "Combined status of checks on the default branch head "
                                   "(SUCCESS, FAILURE, PENDING, ERROR); absent when the repo has no checks",
        "issues_open": "Open issues",
        "issues_opened_90d": "Issues opened in the last 90 days, bots excluded (from the 100 most recent)",
        "issue_closure_ratio_90d": "Closed over opened issues in the last 90 days",
        "median_issue_first_response_seconds": "Median seconds to first non-author response on issues "
                                               "opened in the last 90 days",
        "issues_stale_open_180d": "Open issues older than 180 days among the 100 most recent issues",
        "first_timer_prs_90d": "PRs opened in the last 90 days by first-time contributors "
                               "(GitHub authorAssociation), bots excluded",
        "first_timer_median_first_response_seconds": "Median seconds to first response on first-time "
                                                     "contributors' PRs in the last 90 days",
        "good_first_issues_open": "Open issues labelled 'good first issue'",
    },
)
@pytest.mark.asyncio
@pytest.mark.edx_health
async def check_pr_activity(all_results, github_repo):
    """
    Activity signals via one GraphQL query: PR and issue flow, backlog, default
    branch CI state and first-time contributor responsiveness.
    """
    github_repo = await github_repo
    repo = github_repo.object
    if repo is None:
        logger.error(github_repo.message)
        pytest.skip("There was an error fetching data from GitHub")

    variables = {"owner": repo.owner.login, "name": repo.name}
    data = await repo.http.request(json={"query": FETCH_RECENT_PRS, "variables": variables})
    repository = (data or {}).get("repository")
    if not repository:
        return

    all_results[MODULE_DICT_KEY].update(repository_activity_results(repository, datetime.now(timezone.utc)))
