"""
Checks The Number of Branches and Pull Requests In Repo
"""
import json
import os
import re

import requests
from pytest_repo_health import add_key_to_metadata

module_dict_key = "branch_and_pulls_stats"

URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"


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


@add_key_to_metadata(module_dict_key)
def check_branch_and_pr_count(all_results, git_origin_url):
    """
    Checks repository integrated with github actions workflow
    """
    match = re.search(URL_PATTERN, git_origin_url)
    repo_name = match.group("repo_name")
    all_results[module_dict_key]['branch_count'] = get_branch_or_pr_count(repo_name, 'branches')
    all_results[module_dict_key]['pulls_count'] = get_branch_or_pr_count(repo_name, 'pulls')
