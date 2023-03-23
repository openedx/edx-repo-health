"""
Checks repository open dependabot alert and collects metrics.
"""

import logging
import os

import requests
from pytest_repo_health import health_metadata

from .utils import github_org_repo

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "dependabot_alerts"

def get_github_dependabot_api_response(org_name, repo_name):
    """
    Fetch the repo's list of open Dependabot alerts, as `requests` response object
    """

    response = requests.get(
        url=f'https://api.github.com/repos/{org_name}/{repo_name}/dependabot/alerts?state=open&per_page=100',
        headers={'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}'}
    )

    if response.status_code != 200:
        logger.error(
                "An error occurred while fetching %s. status code %s content info %s.",
                repo_name,
                response.status_code,
                response.content
        )
        return None

    return response

@health_metadata(
    [MODULE_DICT_KEY, "dependabot_alerts"],
    {
        "total_count": "The total number of open Dependabot alerts for this repository",
        "low_severity ": "Open Dependabot alerts with low severity",
        "medium_severity ": "Open Dependabot alerts with medium severity",
        "high_severity ": "Open Dependabot alerts with high severity",
        "critical_severity ": "Open Dependabot alerts with critical severity",
        "incomplete_results": "Indicates if there are additional open alerts beyond the page count limit of 100"
    }
)
def check_dependabot_alert_stats(all_results, git_origin_url):
    """
    Checks repo stats for dependabot alerts
    """
    org_name, repo_name = github_org_repo(git_origin_url)
    stats = compile_dependabot_stats(org_name, repo_name)

    all_results[MODULE_DICT_KEY] = stats

def compile_dependabot_stats(org_name, repo_name):
    """
    Compiles dependabot alert stats for the repo
    """
    response = get_github_dependabot_api_response(org_name, repo_name)
    if response is None:
        return {}
    else:
        stat_dict = {
            "total_count": 0,
            "critical_severity": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
        }
        dependabot_alerts = response.json()
        for dependabot_alert in dependabot_alerts:
            stat_dict["total_count"] += 1

            if dependabot_alert["security_vulnerability"]["severity"] == "low":
                stat_dict["low_severity"] += 1
            elif dependabot_alert["security_vulnerability"]["severity"] == "medium":
                stat_dict["medium_severity"] += 1
            elif dependabot_alert["security_vulnerability"]["severity"] == "high":
                stat_dict["high_severity"] += 1
            elif dependabot_alert["security_vulnerability"]["severity"] == "critical":
                stat_dict["critical_severity"] += 1
        stat_dict['incomplete_results'] = 'next' in response.links
        return stat_dict
