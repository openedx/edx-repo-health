"""Test suite for dependabot check"""

import os

import pytest

from repo_health import get_file_content
from repo_health.check_readthedocs_config import (
    check_readthedocs_file_exists,
    check_readthedocs_file_version,
    check_readthedocs_file_name,
    module_dict_key
)


@pytest.fixture(name="readthedocs_config_details")
def fixture_readthedocs_config_details(repo_path):
    """Fixture returns the name and the content of readthedocs file"""
    files_to_check = [
        "readthedocs.yml",
        "readthedocs.yaml",
        ".readthedocs.yml",
        ".readthedocs.yaml"
    ]
    for readthedocs_file in files_to_check:
        file_content = get_file_content(os.path.join(repo_path, f"tests/fake_repos/readthedocs_samples/{readthedocs_file}"))
        if file_content:
            return {
                "file_name": readthedocs_file,
                "file_content": file_content
            }
    return {}


def test_check_readthedocs_yml_exists(readthedocs_config_details):
    """
    Test to check if readthedocs.yml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True


def test_check_readthedocs_yaml_exists(readthedocs_config_details):
    """
    Test to check if readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True

def test_check_readthedocs_dot_yml_exists(readthedocs_config_details):
    """
    Test to check if .readthedocs.yml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True


def test_check_readthedocs_dot_yaml_exists(readthedocs_config_details):
    """
    Test to check if .readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True


def test_check_readthedocs_yml_exists(readthedocs_config_details):
    """
    Test to check if readthedocs.yml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == "readthedocs.yml"


def test_check_readthedocs_yaml_exists(readthedocs_config_details):
    """
    Test to check if readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == "readthedocs.yaml"


def test_check_dot_readthedocs_yml_exists(readthedocs_config_details):
    """
    Test to check if .readthedocs.yml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == ".readthedocs.yml"


def test_check_dot_readthedocs_yaml_exists(readthedocs_config_details):
    """
    Test to check if .readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        readthedocs_config_details,
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == ".readthedocs.yaml"


def test_check_readthedocs_version_is_1_or_2(readthedocs_config_details):
    """
    Test to check if the file content has version 1 or 2
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_version(readthedocs_config_details, all_results)

    assert all_results[module_dict_key]['version'] in [1,2]
