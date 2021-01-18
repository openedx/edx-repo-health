"""
Checks to collect useful information from the GitHub API about the target repository.
"""
import functools
import json
import logging
import operator
import os
import re

import pytest
import requests
from pytest_repo_health import health_metadata

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "github"
URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"

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
    edges = list()

    cursor = None
    has_next_page = True

    while has_next_page:
        json = {
            "query": FETCH_REPOSITORY_LANGUAGES,
            "variables": kwargs.update(cursor=cursor) or kwargs,
        }

        data = await client.request(json=json)
        data = functools.reduce(operator.getitem, ["node", "languages"], data)

        edges.extend(data["edges"])

        cursor = data["pageInfo"]["endCursor"]
        has_next_page = data["pageInfo"]["hasNextPage"]

    result = {}
    for edge in edges:
        name = edge["node"]["name"]
        result[name.lower()] = edge["size"]
    return result


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
async def check_settings(all_results, github_repo):
    """
    Get all the fields of interest from the GitHub repository object itself.
    """
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
async def check_languages(all_results, github_repo):
    """
    Get the number of bytes of each programming language in the repository.
    """
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


def check_branch_and_pr_count(all_results, git_origin_url):
    """
    Checks repository integrated with github actions workflow
    """
    match = re.search(URL_PATTERN, git_origin_url)
    repo_name = match.group("repo_name")
    all_results[MODULE_DICT_KEY]['branch_count'] = get_branch_or_pr_count(repo_name, 'branches')
    all_results[MODULE_DICT_KEY]['pulls_count'] = get_branch_or_pr_count(repo_name, 'pulls')


def get_branch_or_pr_count(repo_name, pulls_or_branches):
    """
    Get the count for branches or pull requests using Github API and add the count to report
    """
    url = f"https://api.github.com/repos/edx/{repo_name}/{pulls_or_branches}?per_page=1"
    count = 0

    response = requests.get(url=url, headers={'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}'})
    if response.ok and json.loads(response.content):
        count = 1
        if 'last' in response.links:
            last_page = response.links['last']['url']
            count = int(re.findall(r'page=(\d+)', last_page)[1])

    return count
