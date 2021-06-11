import os
import pdb
from repo_health.check_github_integration import check_github_actions_integration, module_dict_key, GitHubIntegrationHandler
from unittest import mock, TestCase


def mocked_responses(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

        def json(self):
            return self.content

    current_dir = os.path.dirname(__file__)

    if kwargs['url'] == 'https://api.github.com/repos/edx/integrated/actions/workflows':
        workflows_data = open(os.path.join(current_dir, 'data/github_integrated.json'), 'r')
        return MockResponse(workflows_data.read(), 200)
    elif kwargs['url'] == 'https://api.github.com/repos/edx/not_integrated/actions/workflows':
        workflows_data = open(os.path.join(current_dir, 'data/github_not_integrated.json'), 'r')
        return MockResponse(workflows_data.read(), 200)

    return MockResponse(None, 404)


class GithubIntegrationTest(TestCase):

    @mock.patch('requests.get', side_effect=mocked_responses)
    def test_check_github_integration_true(self, mock_get):
        all_results = {module_dict_key: {}}
        check_github_actions_integration(all_results, git_origin_url=f"github.com/edx/integrated.git")

        assert all_results[module_dict_key] == True
        assert all_results["org_name"] == 'edx'

    @mock.patch('requests.get', side_effect=mocked_responses)
    def test_check_github_integration_false(self, mock_get):
        all_results = {module_dict_key: {}}
        check_github_actions_integration(all_results, git_origin_url=f"github.com/edx/not_integrated.git")

        assert all_results[module_dict_key] == False
        assert all_results["org_name"] == 'edx'
