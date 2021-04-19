"""
Checks repository is on github actions workflow and tests are enabled.
"""
import json
import logging
import os
import re

import requests
from pytest_repo_health import add_key_to_metadata


logger = logging.getLogger(__name__)

module_dict_key = "github_actions"

URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"


def get_githubworkflow_api_response(repo_name):
    """
    get the workflows information using api.
    """

    # For unauthenticated requests, the rate limit allows for up to 60 requests per hour.
    # https://developer.github.com/v3/#rate-limiting

    return requests.get(
        url=f'https://api.github.com/repos/edx/{repo_name}/actions/workflows',
        headers={'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}'}
    )


class GitHubIntegrationHandler:
    """
    sets up the operations and required  github actions workflow CI integration information on instance
    """

    def __init__(self, repo_name):
        self.repo_name = repo_name
        self.api_data = None
        self.github_actions = False
        self._set_github_actions_integration_data()

    def _set_github_actions_integration_data(self):
        self.api_response = get_githubworkflow_api_response(self.repo_name)

    def handle(self):
        """
        initiates the process to fetch github actions workflow integration information
        """
        if self.api_response.status_code != 200:
            logger.error(
                "An error occurred while fetching %s. status code %s content info %s.",
                self.repo_name,
                self.api_response.status_code,
                self.api_response.content
            )
            return

        self.api_data = json.loads(self.api_response.content)

        if self.api_data and 'workflows' in self.api_data:
            self.github_actions = [
                True for workflow in self.api_data['workflows']

                if workflow['path'] in [
                    '.github/workflows/ci.yml',
                    '.github/workflows/playbook-test.yml',
                    '.github/workflows/syntax-test.yml'
                ] and workflow['state'] == 'active'
            ]


@add_key_to_metadata((module_dict_key,))
def check_githuba_actions_integration(all_results, git_origin_url):
    """
    Checks repository integrated with github actions workflow
    """
    match = re.search(URL_PATTERN, git_origin_url)
    repo_name = match.group("repo_name")
    org_name = match.group("org_name")
    integration_handler = GitHubIntegrationHandler(repo_name)
    integration_handler.handle()
    all_results[module_dict_key] = bool(integration_handler.github_actions)
    all_results['org_name'] = f'{org_name}'
