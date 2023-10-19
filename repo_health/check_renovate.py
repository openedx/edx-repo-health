"""
Checks for renovate configuration
"""
import json
import os

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

TOTAL_PR_QUERY = """
query searchRepos($filter: String!) {
  search(query: $filter, type: ISSUE, first: 100) {
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
    repo = github_repo.object
    client = repo.http
    kwargs_edx = {
        "filter": f"repo:edx/{repo.name} type:pr author:app/renovate"
    }
    kwargs_open_edx = {
        "filter": f"repo:openedx/{repo.name} type:pr author:app/renovate"
    }

    _json = {
        "query": LAST_PR_QUERY,
        "variables": kwargs_edx,
    }
    data = await client.request(json=_json)

    if not data['search']['nodes']:
      data = await client.request(json={
        "query": LAST_PR_QUERY,
        "variables": kwargs_open_edx
      })

    if len(data['search']['nodes']):
        return data['search']['nodes'][0]['createdAt'][:10]

async def get_total_and_oldest_renovate_pull_requests(github_repo):
    """
    Fetches the total number of pull requests and creation date of oldest still-open PR made by Renovate.
    """
    repo = github_repo.object
    client = repo.http
    kwargs_edx = {
        "filter": f"repo:edx/{repo.name} type:pr author:app/renovate is:open"
    }
    kwargs_open_edx = {
        "filter": f"repo:openedx/{repo.name} type:pr author:app/renovate is:open"
    }

    _json = {
        "query": TOTAL_PR_QUERY,
        "variables": kwargs_open_edx,
    }

    try:
        data = await client.request(json=_json)

        if not data['search']['nodes']:
          data = await client.request(json={
            "query": TOTAL_PR_QUERY,
            "variables": kwargs_edx
          })

        total_open_prs = len(data['search']['nodes'])
        oldest_pr_date = None

        if total_open_prs > 0:
          oldest_pr_data = len(data['search']['nodes']) - 1
          oldest_pr_date = data['search']['nodes'][oldest_pr_data]['createdAt'][:10]

        return total_open_prs, oldest_pr_date
    except (KeyError, TypeError):
        return 0, None


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "configured": "Flag for existence of renovate configuration",
        "last_pr": "Date of last Pull Request made by renovate",
        "total_open_prs": "Number of total open Pull Requests made by renovate",
        "oldest_open_pr_date": "Creation date of oldest still-open renovate PR",
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

    github_repo = await github_repo

    if config_exists:
      total_open_prs, oldest_pr_date = await get_total_and_oldest_renovate_pull_requests(github_repo)

    all_results[MODULE_DICT_KEY] = {
        'configured': config_exists,
        'last_pr': await get_last_pull_date(github_repo) if config_exists else None,
        'total_open_prs': total_open_prs if config_exists else None,
        'oldest_open_pr_date': oldest_pr_date if config_exists else None,
    }
