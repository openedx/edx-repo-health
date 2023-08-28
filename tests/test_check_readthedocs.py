"""Test suite for dependabot check"""

import os

import pytest

from repo_health import get_file_content
from repo_health.check_readthedocs import check_readthedocs_yaml_exists, check_readthedocs_yml_exists, check_readthedocs_yaml_version, module_dict_key

readthedocs_yml_path=".readthedocs.yml"
readthedocs_yaml_path=".readthedocs.yaml"

readthedocs_yaml_exists_path = "tests/fake_repos/readthedocs_samples/.readthedocs.yaml"
readthedocs_yml_does_not_exist_path = "tests/fake_repos/readthedocs_samples/.readthedocs.yml"



@pytest.fixture(name="readthedocs_yaml_exists")
def fixture_readthedocs_yaml_exists(repo_path):
    """Fixture containing the text content of .readthedocs.yaml"""
    full_path = os.path.join(repo_path, readthedocs_yaml_exists_path)
    return get_file_content(full_path)


@pytest.fixture(name="readthedocs_yml_doesnot_exist")
def fixture_readthedocs_yml_doesnot_exist(repo_path):
    """Fixture containing the text content of .readthedocs.yml"""
    full_path = os.path.join(repo_path, readthedocs_yml_does_not_exist_path)
    return get_file_content(full_path)


def test_check_readthedocs_yaml_exists(readthedocs_yaml_exists):
    """
    Test to check if .readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_yaml_exists(readthedocs_yaml_exists, all_results)

    assert all_results[module_dict_key]['readthedocs_yaml']['exists'] is True


def test_check_readthedocs_yml_doesnot_exist(readthedocs_yml_doesnot_exist):
    """
    Test to check if .readthedocs.yml file does not exist
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_yml_exists(readthedocs_yml_doesnot_exist, all_results)

    assert all_results[module_dict_key]['readthedocs_yml']['exists'] is False


def test_check_readthedocs_yaml_has_v2(readthedocs_yaml_exists):
    """
    Test to check if version 2 is in .readthedocs.yaml
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_yaml_version(readthedocs_yaml_exists, all_results)

    assert all_results[module_dict_key]["readthedocs_yaml"]["version"] == "V2"
