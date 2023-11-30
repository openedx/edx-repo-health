"""
Utility Functions
"""
import functools
import requests
import json
import operator
import os
import re
from datetime import datetime

GITHUB_DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"


def file_exists(repo_path, file_name):
    full_path = os.path.join(repo_path, file_name)
    return os.path.isfile(full_path)


def dir_exists(repo_path, dir_name):
    full_path = os.path.join(repo_path, dir_name)
    return os.path.isdir(full_path)


def parse_build_duration_response(json_response):
    """
    This function is responsible for parsing Github GraphQL API response and calculating build duration.

    Returns None when repo is uninitialized.
    """
    build_checks = []
    first_started_at = None
    last_completed_at = None
    total_duration = ''

    # Handle uninitialized repos (missing default branch, or no commits on branch)
    try:
        latest_commits = functools.reduce(
            operator.getitem, ["node", "defaultBranchRef", "target", "history", "edges"], json_response)
    except TypeError:
        return None

    if not latest_commits:
        return None
    else:
        latest_commit = latest_commits[0]

    for check_suite in functools.reduce(operator.getitem, ['node', 'checkSuites', 'edges'], latest_commit):

        all_check_runs = check_suite['node']['checkRuns']['edges']
        for check_run in all_check_runs:
            # If check is still in progress, skip it
            if not check_run['node']['completedAt']:
                continue

            name = check_run['node']['name']
            started_at = datetime.strptime(check_run['node']['startedAt'], GITHUB_DATETIME_FMT)
            completed_at = datetime.strptime(check_run['node']['completedAt'], GITHUB_DATETIME_FMT)

            if not first_started_at or started_at < first_started_at:
                first_started_at = started_at
            if not last_completed_at or completed_at > last_completed_at:
                last_completed_at = completed_at

            job_duration = completed_at - started_at
            total_seconds = job_duration.total_seconds()
            minutes, remaining_seconds = divmod(total_seconds, 60)

            build_checks.append({
                'name': name,
                'duration': f'{int(minutes)} minutes {int(remaining_seconds)} seconds',
                'seconds': total_seconds
            })

    if build_checks:
        # sorting checks into descending order of duration to get slowest check on top
        build_checks = sorted(build_checks, key=lambda k: k['seconds'], reverse=True)
        for check in build_checks:
            del check['seconds']

        build_duration = last_completed_at - first_started_at
        minutes, remaining_seconds = divmod(build_duration.total_seconds(), 60)

        total_duration = f'{int(minutes)} minutes {int(remaining_seconds)} seconds'

    return total_duration, build_checks


URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"

def github_org_repo(git_origin_url):
    """Return the org and repo from a GitHub URL."""
    match = re.search(URL_PATTERN, git_origin_url)
    assert match is not None
    return match.groups()


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


def set_branch_and_pr_count(all_results, git_origin_url, module_dict_key):
    """
    Takes all_results dict and update branch and pr counts using git_origin_url
    """
    org_name, repo_name = github_org_repo(git_origin_url)
    all_results[module_dict_key]['branch_count'] = get_branch_or_pr_count(org_name, repo_name, 'branches')
    all_results[module_dict_key]['pulls_count'] = get_branch_or_pr_count(org_name, repo_name, 'pulls')
    return all_results


def set_pypi_name(all_results, setup_py, setup_cfg, module_dict_key):
    # Look in setup.py for:     name="package",
    py_names = re.findall(r"""(?m)^\s+name\s?=\s?['"]([\w-]+)['"],""", setup_py)
    # Look in setup.cfg for:    name=package
    cfg_names = re.findall(r"""(?m)^name\s?=\s?([\w-]+)""", setup_cfg)

    names = py_names + cfg_names
    # If the name doesn't match the expected format, don't fill it into the results.
    if names and len(names) == 1:
        all_results[module_dict_key]["pypi_name"] = names[0]
    return all_results


def set_repo_url(all_results, setup_py, setup_cfg, module_dict_key):
    py_urls = re.findall(r"""(?m)^\s*url\s*=\s*['"]([^'"]+)['"]""", setup_py)
    cfg_urls = re.findall(r"""(?m)^url\s*=\s*(\S+)""", setup_cfg)
    urls = py_urls + cfg_urls
    if urls:
        assert len(urls) == 1
        all_results[module_dict_key]["repo_url"] = urls[0]
    return all_results


def set_project_urls(all_results, setup_py, setup_cfg, module_dict_key):
    py_urls = re.findall(r"""(?ms)^\s*project_urls\s*=\s*({[^}]+})""", setup_py)
    cfg_urls = re.findall(r"""(?ms)^project_urls\s*=\s*(.*?)(?:^\S|^$)""", setup_cfg)
    urls = py_urls + cfg_urls
    if urls:
        assert len(urls) == 1
        all_results[module_dict_key]["project_urls"] = urls[0]
    return all_results
