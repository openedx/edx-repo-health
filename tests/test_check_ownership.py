"""Test checks for ownership info."""

import csv
import os
from pathlib import Path
from unittest import mock

from repo_health.check_ownership import MODULE_DICT_KEY, check_ownership


def mocked_responses(*args, **kwargs):
    """Get mock ownership CSV data."""

    current_dir = os.path.dirname(__file__)

    with open(os.path.join(current_dir, 'data/ownership_data.csv'), 'r') as csv_file:
        file_data = csv.reader(csv_file)
        headers = next(file_data)
        return [dict(zip(headers, i)) for i in file_data]


@mock.patch('repo_health.check_ownership.find_worksheet')
@mock.patch.dict(os.environ, {
    "REPO_HEALTH_GOOGLE_CREDS_FILE": "test",
    "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL": "test",
    "REPO_HEALTH_REPOS_WORKSHEET_ID": "23"
})
def test_check_ownership(mock_get):
    mock_get.return_value = mocked_responses()

    all_results = {MODULE_DICT_KEY: {}}
    check_ownership(all_results, git_origin_url="github.com/edx/ownership_repo1.git", repo_path="")

    assert all_results[MODULE_DICT_KEY]['theme'] == 'openedx'
    assert all_results[MODULE_DICT_KEY]['squad'] == 'arch'
    assert all_results[MODULE_DICT_KEY]['priority'] == 'High'


@mock.patch('repo_health.check_ownership.find_worksheet_with_actions')
@mock.patch.dict(os.environ, {
    "REPO_HEALTH_GOOGLE_CREDS_FILE": '{"type": "test", "project_id": "test", "private_key_id": "test"}',
    "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL": "test",
    "REPO_HEALTH_REPOS_WORKSHEET_ID": "23"
})
def test_check_ownership_with_actions(mock_get):
    mock_get.return_value = mocked_responses()

    all_results = {MODULE_DICT_KEY: {}}
    check_ownership(all_results, git_origin_url="github.com/edx/ownership_repo1.git", repo_path="")

    assert all_results[MODULE_DICT_KEY]['theme'] == 'openedx'
    assert all_results[MODULE_DICT_KEY]['squad'] == 'arch'
    assert all_results[MODULE_DICT_KEY]['priority'] == 'High'


def test_check_ownership_uses_catalog_info_without_sheet_env(tmp_path):
    catalog = Path(tmp_path) / "catalog-info.yaml"
    catalog.write_text("spec:\n  owner: user:alice\n", encoding="utf-8")

    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        check_ownership(
            all_results,
            git_origin_url="github.com/edx/ownership_repo1.git",
            repo_path=str(tmp_path),
        )

    assert all_results[MODULE_DICT_KEY]["owner"] == "user:alice"
    assert all_results[MODULE_DICT_KEY]["owner_kind"] == "user"
    assert all_results[MODULE_DICT_KEY]["owner_name"] == "alice"
