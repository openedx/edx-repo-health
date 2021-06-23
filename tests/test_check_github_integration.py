import os

from repo_health.check_github_integration import check_github_actions_integration, module_dict_key, get_githubworkflow_api_response
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


@mock.patch('repo_health.check_github_integration.get_githubworkflow_api_response')
def test_check_github_integration_true(mock_get):
    mock_get.return_value = mocked_responses(url='https://api.github.com/repos/edx/integrated/actions/workflows')

    all_results = {module_dict_key: {}}
    check_github_actions_integration(all_results, git_origin_url=f"github.com/edx/integrated.git")

    assert all_results[module_dict_key] == True
    assert all_results["org_name"] == 'edx'


@mock.patch('repo_health.check_github_integration.get_githubworkflow_api_response')
def test_check_github_integration_false(mock_get):
    mock_get.return_value = mocked_responses(url='https://api.github.com/repos/edx/not_integrated/actions/workflows')

    all_results = {module_dict_key: {}}
    check_github_actions_integration(all_results, git_origin_url=f"github.com/edx/not_integrated.git")

    assert all_results[module_dict_key] == False
    assert all_results["org_name"] == 'edx'
