"""
Checks for renovate configuration
"""
import json
import os
import requests
import pytest
from pytest_repo_health import health_metadata
from . import get_file_content
from .utils import file_exists
MODULE_DICT_KEY = "renovate"
LAST_PR_QUERY = """
query searchRepos($filter: String!) {
  search(query: $filter, type: ISSUE, last: 1) {
    nodes {
      ... on PullRequest {
        createdAt
      }
    }
  }
}
"""

OLDEST_RENOVATE_PR_QUERY = """
query searchRepos($filter: String!) {
  search(first: 1, query: $filter, type: ISSUE) {
    nodes {
      ... on PullRequest {
        createdAt
      }
    }
  }
}
"""

POSSIBLE_CONFIG_PATHS = [
    ".github/renovate.json",
    ".github/renovate.json5",
    ".gitlab/renovate.json",
    ".gitlab/renovate.json5",
    ".renovaterc.json",
    "renovate.json",
    "renovate.json5",
    ".renovaterc"
]
async def get_last_pull_date(github_repo):
    """
    Fetches the last pull request made by renovate
    """
    github_repo = await github_repo
    repo = github_repo.object
    client = repo.http
    kwargs = {
        "filter": f"repo:edx/{repo.name} type:pr author:app/renovate"
    }
    _json = {
        "query": LAST_PR_QUERY,
        "variables": kwargs,
    }
    data = await client.request(json=_json)
    if len(data['search']['nodes']):
        return data['search']['nodes'][0]['createdAt'][:10]
async def get_total_renovate_pull_requests(github_repo):
    """
    Fetches the total number of pull requests made by Renovate.
    """
    repo = await github_repo.object
    client = repo.http
    kwargs = {
        "filter": f"repo:edx/{repo.name} type:pr author:app/renovate"
    }
    _json = {
        "query": LAST_PR_QUERY,
        "variables": kwargs,
    }
    try:
        data = await client.request(json=_json)
        return len(data['search']['nodes'])
    except (KeyError, TypeError):
        return 0

async def get_oldest_renovate_pr_creation_date(github_repo):
    """
    Fetches the creation date of the oldest still-open Renovate PR.
    """
    repo = await github_repo.object
    client = repo.http
    kwargs = {
        "filter": f"repo:edx/{repo.name} type:pr author:app/renovate is:open"
    }

    _json = {
        "query": OLDEST_RENOVATE_PR_QUERY,
        "variables": kwargs,
    }

    try:
        data = await client.request(json=_json)
        oldest_pr_date = data['search']['nodes'][0]['createdAt']
        return oldest_pr_date
    except (KeyError, TypeError, IndexError):
        return None


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "configured": "Flag for existence of renovate configuration",
        "last_pr": "Date of last Pull Request made by renovate",
        "total_renovate_prs": "Number of Total Pull Request made by renovate",
        "oldest_renovate_pr_date": "Creation date of oldest renovate PR",
    }
)
@pytest.mark.asyncio
async def check_renovate(all_results, repo_path, github_repo):
    """
    Checks whether repository contains configuration for renovate and is making PR
    """
    config_exists = any(file_exists(repo_path, path) for path in POSSIBLE_CONFIG_PATHS)
    if not config_exists and file_exists(repo_path, 'package.json'):
        content = get_file_content(os.path.join(repo_path, 'package.json'))
        config_exists = 'renovate' in json.loads(content)
    all_results[MODULE_DICT_KEY] = {
        'configured': config_exists,
        'last_pr': await get_last_pull_date(github_repo) if config_exists else None,
        'total_renovate_prs': await get_total_renovate_pull_requests(github_repo) if config_exists else None,
        'oldest_renovate_pr': await get_oldest_renovate_pr_creation_date(github_repo) if config_exists else None
    }