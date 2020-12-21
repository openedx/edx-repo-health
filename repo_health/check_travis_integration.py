"""
Checks repository is on travis.org or .com
"""
import json
import logging
import re

import pytest
import requests
from pytest_repo_health import add_key_to_metadata

from repo_health_dashboard.utils.utils import squash_dict

logger = logging.getLogger(__name__)

module_dict_key = "travis_ci"

TRAVIS_API_URL = "https://api.travis-ci.com/repo/edx%2F"

URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"


def log_travis_api_failure(response):
    logger.error("An error occurred while fetching integration information from Travis. Details: %s", response.content)
    pytest.skip("Skipped due to an error with Travis API")


def get_travis_api_response(repo_name):
    return requests.get(url=f'{TRAVIS_API_URL}{repo_name}',
                        headers={'Travis-API-Version': '3', "User-Agent": "API Explorer"})


class TravisIntegrationHandler:
    """
    sets up the operations and required travis CI integration information on instance
    """

    def __init__(self, repo_name):
        self.active_on_com = False
        self.active_on_org = False
        self.active = False
        self.repo_name = repo_name
        self.travis_api_data = None
        self._set_travis_integration_data()

    def _set_travis_integration_data(self):
        self.travis_api_response = get_travis_api_response(self.repo_name)

    def _set_active_on_com(self):
        self.active_on_com = (self.travis_api_data['migration_status'] is None or
                              self.travis_api_data['migration_status'] == 'migrated') and \
                             (self.travis_api_data['active_on_org'] is False)

    def _set_active_on_org(self):
        self.active_on_org = self.travis_api_data['migration_status'] is None and \
                             self.travis_api_data['active_on_org'] is True

    def _set_active(self):
        self.active = True

    def handle(self):
        """
        initiates the process to fetch travis CI integration information
        """

        if self.travis_api_response.status_code == 404:
            return
        elif self.travis_api_response.status_code != 404 and not self.travis_api_response.ok:
            log_travis_api_failure(self.travis_api_response)
            return

        self.travis_api_data = json.loads(self.travis_api_response.content)
        self._set_active()
        self._set_active_on_com()
        self._set_active_on_org()


@add_key_to_metadata(module_dict_key)
def check_travis_integration(all_results, git_origin_url):
    """
    Checks repository integrated with travis-ci.org or travis-ci.com
    """

    if squash_dict(all_results)['exists..travis.yml']:
        match = re.search(URL_PATTERN, git_origin_url)
        repo_name = match.group("repo_name")
        travis_integration_handler = TravisIntegrationHandler(repo_name)
        travis_integration_handler.handle()

        all_results[module_dict_key]['active_on_com'] = travis_integration_handler.active_on_com
        all_results[module_dict_key]['active_on_org'] = travis_integration_handler.active_on_org
        all_results[module_dict_key]['active'] = travis_integration_handler.active

    else:
        all_results[module_dict_key]['active_on_com'] = False
        all_results[module_dict_key]['active_on_org'] = False
        all_results[module_dict_key]['active'] = False
