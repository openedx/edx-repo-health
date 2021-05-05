"""
Check some details in the readme file.
"""
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
    Check that the README file has docs build badge.
    """
    if readme is None:
        return

    if re.search(r'image:: *https?://readthedocs\.org/projects', readme):
        all_results[module_dict_key]["build_badge"] = True
    else:
        all_results[module_dict_key]["build_badge"] = False


class ReadTheDocsChecker:
    """
    Handles all the operations related to Read the Docs checks
    """

    def __init__(self, repo_path=None, git_origin_url=None, token=None):
        self._yml_file_name = ".readthedocs.yml"
        self.repo_path = repo_path
        self.git_origin_url = git_origin_url

        self.project_url = 'https://readthedocs.org/api/v3/projects/?limit=100'
        self._token = token
        self._headers = {'Authorization': f'token {self._token}'}
        self._projects = None

        self.build_times = []
        self.build_statuses = []

    def _read_readthedocs_yml_file(self):
        full_path = os.path.join(self.repo_path, ".readthedocs.yml")
        return get_file_content(full_path)

    def _parse_readthedocs_yml_file(self):
        """
            Pareses the .readthdocs.yml file and returns parsed data
        """
        readthedocs_yml = self._read_readthedocs_yml_file()
        try:
            data = yaml.safe_load(readthedocs_yml)
            data = {} if data is None else data
            return data
        except yaml.YAMLError:
            return {}

    def _get_projects(self):
        """
            Lists all the projects related to the provided token
        """
        if self._projects is not None:
            return self._projects
        response = requests.get(self.project_url, headers=self._headers)
        self._projects = response.json()['results']
        return self._projects

    def _get_latest_build(self, slug):
        """
            Returns the latest build details for the project slug prvoided
        """
        build_url = f"https://readthedocs.org/api/v3/projects/{slug}/builds/"
        response = requests.get(build_url, headers=self._headers)
        json = response.json()
        # Getting latest build from results
        return json['results'][0]

    def get_python_version(self):
        """
            Returns the version of python mentioned in .readthedocs.yml
        """
        parsed_data = self._parse_readthedocs_yml_file()
        if "python" in parsed_data.keys():
            if "version" in parsed_data['python'].keys():
                return parsed_data['python']['version']
        return None

    def update_build_details(self):
        """
            Updates the status of latest Read the Docs build and when last built ran
        """

        for item in self._get_projects():
            if item['repository']['url'] == self.git_origin_url:
                build = self._get_latest_build(item['slug'])
                status = 'success' if build['success'] else 'failure'
                self.build_statuses.append({'project': item['name'], 'status': status})
                self.build_times.append({'project': item['name'], 'time': build['created']})


@health_metadata(
    [module_dict_key],
    {
        "python_version": "The version of python mentioned in .readthedocs.yml file"
    }
)
def check_python_version(repo_path, all_results):
    """
    Check that the Python version mentioned in .readthedocs.yml file.
    """
    rtd_checker = ReadTheDocsChecker(repo_path=repo_path)
    all_results[module_dict_key]["python_version"] = rtd_checker.get_python_version()


@health_metadata(
    [module_dict_key],
    {
        "latest_build_status": "The status of latest build ran for Read the Docs",
        "latest_build_ran_at": "The time latest build ran for Read the Docs",
    }
)
def check_readthedocs_build(all_results, git_origin_url):
    """
    Checks Read the Docs build status and when last built ran
    """
    try:
        token = os.environ["READTHEDOCS_API_KEY"]
    except KeyError:
        logger.error("READTHEDOCS_API_KEY is missing in environment variables")
        pytest.skip("READTHEDOCS_API_KEY is missing in environment variables")

    rtd_checker = ReadTheDocsChecker(git_origin_url=git_origin_url, token=token)
    rtd_checker.update_build_details()
    all_results[module_dict_key]["latest_build_status"] = rtd_checker.build_statuses
    all_results[module_dict_key]["latest_build_ran_at"] = rtd_checker.build_times
