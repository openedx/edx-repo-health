import os
import pytest
from unittest import mock

from repo_health.check_django_dependencies_compatibility import (
    MODULE_DICT_KEY,
    check_django_dependencies_status,
)


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/fake_repos/{repo_name}"


@mock.patch('repo_health.check_django_dependencies_compatibility.get_django_dependency_sheet',
            return_value=os.path.join(os.path.dirname(__file__), 'data/mock_django_dependencies_sheet.csv'))
@pytest.mark.parametrize("repo_path", [
    get_repo_path("python_repo")])
def test_django_deps_upgrade(mock_get_sheet, repo_path):
    all_results = {MODULE_DICT_KEY: {}}
    check_django_dependencies_status(repo_path, all_results)

    assert all_results[MODULE_DICT_KEY]
    assert all_results[MODULE_DICT_KEY]['total_dependencies']['count'] == 3
    assert all_results[MODULE_DICT_KEY]['support_django_32']['count'] == 2

    assert 'django-waffle' in all_results[MODULE_DICT_KEY]['total_dependencies']['list']
    assert 'django-waffle' not in all_results[MODULE_DICT_KEY]['support_django_32']['list']

    assert 'edx-django-utils' in all_results[MODULE_DICT_KEY]['support_django_32']['list']

