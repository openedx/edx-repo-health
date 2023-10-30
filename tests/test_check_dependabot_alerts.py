"""Test suite for dependabot alerts check"""
import json
import os
from unittest import mock

from repo_health.check_dependabot_alerts import MODULE_DICT_KEY, check_dependabot_alert_stats


class MockResponse:
    """
    Class to hold mock responses from api call
    """
    def __init__(self, response, status_code):
        self.content = response["content"]
        self.status_code = status_code
        self.links = response["links"]

    def json(self):
        return self.content


def mocked_responses(*args, **kwargs):
    # pylint: disable=line-too-long
    """
    Produces a MockResponse object based on the passed in URL
    """
    current_dir = os.path.dirname(__file__)

    if kwargs['url'] == 'https://api.github.com/repos/edx/dependabot-test/dependabot/alerts?state=open&per_page=100':
        with open(os.path.join(current_dir, 'data/github_dependabot_alerts_with_links.json'), 'r') as read_file:
            dependabot_data = json.load(read_file)
            return MockResponse(dependabot_data, 200)
    elif kwargs['url'] == 'https://api.github.com/repos/openedx/dependabot-test/dependabot/alerts?state=open&per_page=100':
        with open(os.path.join(current_dir, 'data/github_dependabot_alerts_no_links.json'), 'r') as read_file:
            dependabot_data = json.load(read_file)
            return MockResponse(dependabot_data, 200)
    return MockResponse(None, 404)


@mock.patch('repo_health.check_dependabot_alerts.get_github_dependabot_api_response')
def test_check_dependabot_alerts_edx(mock_get):
    """
    Test to check if incomplete results is true and if counts are accurate
    Incomplete results designates that number of alerts is greater than alerts per page
    In this case, alerts per page is 100, the max
    """
    # pylint: disable=line-too-long
    mock_get.return_value = mocked_responses(url='https://api.github.com/repos/edx/dependabot-test/dependabot/alerts?state=open&per_page=100')

    all_results = {MODULE_DICT_KEY: {}}
    check_dependabot_alert_stats(all_results, git_origin_url='github.com/edx/dependabot-test.git')

    assert all_results[MODULE_DICT_KEY]
    assert all_results[MODULE_DICT_KEY]['total_count'] == 3
    assert all_results[MODULE_DICT_KEY]['critical_severity'] == 1
    assert all_results[MODULE_DICT_KEY]['low_severity'] == 1
    assert all_results[MODULE_DICT_KEY]['medium_severity'] == 1
    assert 'incomplete_results' in all_results[MODULE_DICT_KEY]
    assert all_results[MODULE_DICT_KEY]['incomplete_results'] is True

@mock.patch('repo_health.check_dependabot_alerts.get_github_dependabot_api_response')
def test_check_dependabot_alerts_openedx(mock_get):
    """
    Test to check if incomplete results is false and if counts are accurate
    """
    # pylint: disable=line-too-long
    mock_get.return_value = mocked_responses(url='https://api.github.com/repos/openedx/dependabot-test/dependabot/alerts?state=open&per_page=100')

    all_results = {MODULE_DICT_KEY: {}}
    check_dependabot_alert_stats(all_results, git_origin_url='github.com/openedx/dependabot-test.git')

    assert all_results[MODULE_DICT_KEY]
    assert all_results[MODULE_DICT_KEY]['total_count'] == 2
    assert all_results[MODULE_DICT_KEY]['critical_severity'] == 1
    assert all_results[MODULE_DICT_KEY]['high_severity'] == 1
    assert 'incomplete_results' in all_results[MODULE_DICT_KEY]
    assert all_results[MODULE_DICT_KEY]['incomplete_results'] is False
