"""Test suite for dependabot check"""

import os

import pytest

from repo_health import get_file_content
from repo_health.check_readthedocs import check_readthedocs_file_exists, check_readthedocs_file_version, module_dict_key

readthedocs_yml_path=".readthedocs.yml"
readthedocs_yaml_path=".readthedocs.yaml"

readthedocs_yaml_fake_path = "tests/fake_repos/readthedocs_samples/.readthedocs.yaml"
readthedocs_yml_fake_path = "tests/fake_repos/readthedocs_samples/.readthedocs.yml"



@pytest.fixture(name="readthedocs_yaml_exists")
def fixture_readthedocs_yaml_exists(repo_path):
    """Fixture containing the text content of .readthedocs.yaml"""
    full_path = os.path.join(repo_path, readthedocs_yaml_fake_path)
    return get_file_content(full_path)


@pytest.fixture(name="readthedocs_yml_exists")
def fixture_readthedocs_yml_exists(repo_path):
    """Fixture containing the text content of .readthedocs.yml"""
    full_path = os.path.join(repo_path, readthedocs_yml_fake_path)
    return get_file_content(full_path)


def test_check_readthedocs_yaml_exists(readthedocs_yaml_exists, readthedocs_yml_exists):
    """
    Test to check if .readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        readthedocs_yaml_exists,
        readthedocs_yml_exists,
        all_results
    )

    assert all_results[module_dict_key]['exists'] == "readthedocs.yaml"


def test_check_readthedocs_yml_exists(readthedocs_yaml_exists, readthedocs_yml_exists):
    """
    Test to check if .readthedocs.yml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        readthedocs_yaml_exists,
        readthedocs_yml_exists,
        all_results
    )

    assert all_results[module_dict_key]['exists'] == "readthedocs.yml"


def test_check_readthedocs_version_is_1_or_2(readthedocs_yaml_exists, readthedocs_yml_exists):
    """
    Test to check if the file content has version 1 or 2
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_version(readthedocs_yaml_exists, readthedocs_yml_exists, all_results)

    assert all_results[module_dict_key]['version'] in [1,2]
