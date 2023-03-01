"""
Check some details of Read The Docs integration.
"""
import json
import logging
import os.path
import re

import pytest
import requests
import yaml
from pytest_repo_health import health_metadata

from repo_health import fixture_readme, get_file_content  # pylint: disable=unused-import

logger = logging.getLogger(__name__)

module_dict_key = "docs"


@health_metadata(
    [module_dict_key],
    {
        "build_badge": "Check that the README file has docs build badge"
    }
)
def check_build_bagde(readme, all_results):
    """
    Check that the README file has a docs build badge.
    """
    if readme is None:
        return

    if re.search(r'image:: *https?://readthedocs\.org/projects', readme):
        all_results[module_dict_key]["build_badge"] = True
    else:
        all_results[module_dict_key]["build_badge"] = False


class ReadTheDocsChecker:
    """
    Handles all the operations related to Read the Docs checks.
    """

    PROJECTS_URL = 'https://readthedocs.org/api/v3/projects/?limit=100'
    _projects = None

    def __init__(self, repo_path=None, git_origin_url=None, token=None):
        self._yml_file_name = ".readthedocs.yml"
        self.repo_path = repo_path
        self.git_origin_url = git_origin_url

        self._token = token
        self._headers = {'Authorization': f'token {self._token}'}

        self.build_details = []

    def _read_readthedocs_yml_file(self):
        full_path = os.path.join(self.repo_path, ".readthedocs.yml")
        return get_file_content(full_path)

    def _parse_readthedocs_yml_file(self):
        """
        Parses the .readthdocs.yml file and returns parsed data.
        """
        readthedocs_yml = self._read_readthedocs_yml_file()
        try:
            data = yaml.safe_load(readthedocs_yml)
            data = {} if data is None else data
            return data
        except yaml.YAMLError:
            return {}

    @classmethod
    def _get_projects(cls, headers):
        """
        Lists all the projects related to the provided token.
        """
        if cls._projects is not None:
            return cls._projects
        response = requests.get(cls.PROJECTS_URL, headers=headers)
        response.raise_for_status()
        cls._projects = response.json()['results']
        return cls._projects

    def _get_all_builds(self, slug):
        """
        Returns all build details for the project whose slug is provided.
        """
        build_url = f"https://readthedocs.org/api/v3/projects/{slug}/builds/"
        response = requests.get(build_url, headers=self._headers)
        response.raise_for_status()
        _json = response.json()
        return _json['results']

    def get_python_version(self):
        """
        Returns the version of Python mentioned in .readthedocs.yml file.
        """
        parsed_data = self._parse_readthedocs_yml_file()
        if "python" in parsed_data.keys():
            if "version" in parsed_data['python'].keys():
                return parsed_data['python']['version']
        return None

    def update_build_details(self):
        """
        Updates the status of latest Read the Docs build and when last build ran.
        """
        self.build_details = []

        for item in self._get_projects(self._headers):      # pylint: disable=not-an-iterable
            if item['repository']['url'] == self.git_origin_url:
                all_builds = self._get_all_builds(item['slug'])
                last_build = all_builds[0]
                last_successful_build = next((build for build in all_builds if build['success']), None)
                self.build_details.append({
                    'project': item['name'],
                    'last_build_status': 'success' if last_build['success'] else 'failure',
                    'last_build_time': last_build['created'],
                    'last_good_build_time': last_successful_build['created'] if last_successful_build else None
                })


@health_metadata(
    [module_dict_key],
    {
        "python_version": "The version of Python mentioned in .readthedocs.yml file"
    }
)
def check_python_version(repo_path, all_results):
    """
    Check the Python version mentioned in .readthedocs.yml file.
    """
    rtd_checker = ReadTheDocsChecker(repo_path=repo_path)
    all_results[module_dict_key]["python_version"] = rtd_checker.get_python_version()


@health_metadata(
    [module_dict_key],
    {
        "build_details": "This contains the build details of all Read the Docs projects connected with the repo",
    }
)
def check_readthedocs_build(all_results, git_origin_url):
    """
    Checks the Read the Docs build status and when last build ran.
    """
    try:
        token = os.environ["READTHEDOCS_API_KEY"]
    except KeyError:
        logger.error("READTHEDOCS_API_KEY is missing in environment variables")
        pytest.skip("READTHEDOCS_API_KEY is missing in environment variables")

    rtd_checker = ReadTheDocsChecker(git_origin_url=git_origin_url, token=token)
    rtd_checker.update_build_details()
    all_results[module_dict_key]["build_details"] = json.dumps(rtd_checker.build_details)
