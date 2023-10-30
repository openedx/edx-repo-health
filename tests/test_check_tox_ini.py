"""Test checks on tox config."""

import os

import pytest

# Because of fixtures: pylint: disable=unused-import
from repo_health.check_tox_ini import check_has_sections, check_whitelist_externals, fixture_tox_ini, module_dict_key


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/fake_repos/{repo_name}"


@pytest.mark.parametrize("repo_path, result", [
    (get_repo_path('tox_repo1'),True),
    (get_repo_path('tox_repo2'),False)
])

def test_check_whitelist_externals(tox_ini, result):
    all_results = {module_dict_key:{}}
    check_whitelist_externals(tox_ini, all_results)

    assert all_results[module_dict_key]['uses_whitelist_externals'] == result


@pytest.mark.parametrize("repo_path, result_list", [
    (get_repo_path('tox_repo1'),{
        "tox":True,
        "testenv":True,
        "testenv:quality":False,
    }),
    (get_repo_path('tox_repo2'),{
        "tox":True,
        "testenv":True,
        "testenv:quality":True,
    })
])

def test_check_has_sections(tox_ini, result_list):
    all_results = {module_dict_key:{}}
    check_has_sections(tox_ini, all_results)

    for key, value in result_list.items():
        assert all_results[module_dict_key]['has_section'][key] == value
