"""
Checks repository is on github actions workflow and tests are enabled.
"""

from repo_health.check_github import set_branch_and_pr_count
from repo_health.utils import github_org_repo

module_dict_key = "github"


def check_github_actions_integration(all_results, git_origin_url):
    """
    Checks repository's org name
    """
    org_name, repo_name = github_org_repo(git_origin_url)
    all_results[module_dict_key]['org_name'] = org_name


def check_branch_and_pr_count(all_results, git_origin_url):
    """
    Checks repository branch and pr count
    """
    all_results = set_branch_and_pr_count(
        all_results,
        git_origin_url,
        module_dict_key
    )
