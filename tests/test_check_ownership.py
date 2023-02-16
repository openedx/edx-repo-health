import csv
import os
from unittest import TestCase, mock

from repo_health.check_ownership import MODULE_DICT_KEY, check_ownership


def mocked_responses(*args, **kwargs):

    current_dir = os.path.dirname(__file__)

    with open(os.path.join(current_dir, 'data/ownership_data.csv'), 'r') as csv_file:
        file_data = csv.reader(csv_file)
        headers = next(file_data)
        return [dict(zip(headers, i)) for i in file_data]


@mock.patch('repo_health.check_ownership.find_worksheet')
@mock.patch.dict(os.environ, {"REPO_HEALTH_GOOGLE_CREDS_FILE": "test", "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL": "test", "REPO_HEALTH_REPOS_WORKSHEET_ID": "23"})
def test_check_ownership(mock_get):
    mock_get.return_value = mocked_responses()

    all_results = {MODULE_DICT_KEY: {}}
    check_ownership(all_results, git_origin_url=f"github.com/edx/ownership_repo1.git")

    assert all_results[MODULE_DICT_KEY]['theme'] == 'openedx'
    assert all_results[MODULE_DICT_KEY]['squad'] == 'arch'
    assert all_results[MODULE_DICT_KEY]['priority'] == 'High'
