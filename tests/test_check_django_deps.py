import os
import pytest
from pathlib import Path
from unittest import mock

from repo_health.check_django_dependencies_compatibility import (
    MODULE_DICT_KEY,
    check_django_dependencies_status,
)


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/fake_repos/{repo_name}"


@mock.patch('repo_health.check_django_dependencies_compatibility.get_edx_ida_list',
            return_value=['django_pytest_requirement'])
@mock.patch('repo_health.check_django_dependencies_compatibility.get_django_dependency_sheet',
            return_value=os.path.join(os.path.dirname(__file__), 'data/mock_django_dependencies_sheet.csv'))
@pytest.mark.parametrize("repo_path", [
    get_repo_path("django_pytest_requirement")])
def test_django_deps_upgrade(mock_ida_list, mock_get_sheet, repo_path):
    all_results = {MODULE_DICT_KEY: {}}
    check_django_dependencies_status(repo_path, all_results)

    assert all_results[MODULE_DICT_KEY]
    assert all_results[MODULE_DICT_KEY]['total_count'] == 2
    assert all_results[MODULE_DICT_KEY]['support_django_32'] == 1
