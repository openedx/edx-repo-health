"""
Checks for renovate configuration
"""
import json
import os

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


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "configured": "Flag for existence of renovate configuration",
        "last_pr": "Date of last Pull Request made by renovate",
    }
)
async def check_renovate(all_results, repo_path, github_repo):
    """
    Checks whether repository contains configuration for renovate and is making PR
    """
    1/0
    config_exists = any(file_exists(repo_path, path) for path in POSSIBLE_CONFIG_PATHS)
    if not config_exists and file_exists(repo_path, 'package.json'):
        content = get_file_content(os.path.join(repo_path, 'package.json'))
        config_exists = 'renovate' in json.loads(content)

    all_results[MODULE_DICT_KEY] = {
        'configured': config_exists,
        'last_pr': await get_last_pull_date(github_repo) if config_exists else None
    }
