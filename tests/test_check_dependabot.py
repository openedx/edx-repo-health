"""Test suite for dependabot check"""

import os

import pytest

from repo_health import get_file_content
from repo_health.check_dependabot import check_dependabot_exists, check_has_ecosystems, module_dict_key

dependabot_exists_path = "tests/fake_repos/dependabot_exists_repo/.github/dependabot.yml"
dependabot_doesnot_exists_path = "tests/fake_repos/not_python/.github/dependabot.yml"



@pytest.fixture(name="dependabot_yml_exists")
def fixture_dependabot_yml_exists(repo_path):
    """Fixture containing the text content of dependabot.yml"""
    full_path = os.path.join(repo_path, dependabot_exists_path)
    return get_file_content(full_path)


@pytest.fixture(name="dependabot_yml_doesnot_exist")
def fixture_dependabot_yml(repo_path):
    """Fixture fetching non-existing dependabot.yml"""
    full_path = os.path.join(repo_path, dependabot_doesnot_exists_path)
    return get_file_content(full_path)


def test_check_dependabot_exists(dependabot_yml_exists):
    """
    Test to check if dependabot file exists
    """
    all_results = {module_dict_key: {}}
    check_dependabot_exists(dependabot_yml_exists, all_results)

    assert all_results[module_dict_key]['exists'] is True


def test_check_dependabot_doesnot_exist(dependabot_yml_doesnot_exist):
    """
    Test to check if dependabot file not exist
    """
    all_results = {module_dict_key: {}}
    check_dependabot_exists(dependabot_yml_doesnot_exist, all_results)

    assert all_results[module_dict_key]['exists'] is False


def test_check_has_ecosystems(dependabot_yml_exists):
    """
    Test to check if covered ecosystems are in dependabot
    """
    all_results = {module_dict_key: {}}
    check_has_ecosystems(dependabot_yml_exists, all_results)

    assert all_results[module_dict_key]["has_ecosystem"]["pip"] is True
    assert all_results[module_dict_key]["has_ecosystem"]["github-actions"] is True
    assert all_results[module_dict_key]["has_ecosystem"]["npm"] is False
