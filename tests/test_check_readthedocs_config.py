"""Test suite for dependabot check"""

from repo_health import get_file_content
from repo_health.check_readthedocs_config import (
    check_readthedocs_file_exists,
    check_readthedocs_file_version,
    check_readthedocs_file_name,
    module_dict_key
)



def test_check_readthedocs_yml_exists():
    """
    Test to check if readthedocs.yml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        {
            "file_name": "readthedocs.yml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/readthedocs.yml")
        },
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True


def test_check_dot_readthedocs_yml_exists():
    """
    Test to check if .readthedocs.yml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        {
            "file_name": ".readthedocs.yml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/.readthedocs.yml")
        },
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True


def test_check_readthedocs_yaml_exists():
    """
    Test to check if readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        {
            "file_name": "readthedocs.yaml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/readthedocs.yaml")
        },
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True


def test_check_dot_readthedocs_yaml_exists():
    """
    Test to check if .readthedocs.yaml file exists
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_exists(
        {
            "file_name": ".readthedocs.yaml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/.readthedocs.yaml")
        },
        all_results
    )

    assert all_results[module_dict_key]['exists'] is True


def test_check_readthedocs_yml_file_name():
    """
    Test to check if readthedocs.yml file name
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        {
            "file_name": "readthedocs.yml"
        },
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == "readthedocs.yml"


def test_check_dot_readthedocs_yml_file_name():
    """
    Test to check if .readthedocs.yml file name
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        {
            "file_name": ".readthedocs.yml"
        },
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == ".readthedocs.yml"


def test_check_readthedocs_yaml_file_name():
    """
    Test to check if readthedocs.yaml file name
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        {
            "file_name": "readthedocs.yaml"
        },
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == "readthedocs.yaml"


def test_check_dot_readthedocs_yaml_file_name():
    """
    Test to check if .readthedocs.yaml file name
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_name(
        {
            "file_name": ".readthedocs.yaml"
        },
        all_results
    )

    assert all_results[module_dict_key]['file_name'] == ".readthedocs.yaml"


def test_check_readthedocs_yml_version_is_1_or_2():
    """
    Test to check if the readthedocs.yml file content has version 1 or 2
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_version(
        {
            "file_name": "readthedocs.yml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/readthedocs.yml")
        },
        all_results
    )

    assert all_results[module_dict_key]['version'] in [1,2]


def test_check_dot_readthedocs_yml_version_is_1_or_2():
    """
    Test to check if the .readthedocs.yml file content has version 1 or 2
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_version(
        {
            "file_name": ".readthedocs.yml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/.readthedocs.yml")
        },
        all_results
    )

    assert all_results[module_dict_key]['version'] in [1,2]


def test_check_readthedocs_yaml_version_is_1_or_2():
    """
    Test to check if the readthedocs.yaml file content has version 1 or 2
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_version(
        {
            "file_name": "readthedocs.yaml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/readthedocs.yaml")
        },
        all_results
    )

    assert all_results[module_dict_key]['version'] in [1,2]


def test_check_dot_readthedocs_yaml_version_is_1_or_2():
    """
    Test to check if the .readthedocs.yaml file content has version 1 or 2
    """
    all_results = {module_dict_key: {}}
    check_readthedocs_file_version(
        {
            "file_name": ".readthedocs.yaml",
            "file_content": get_file_content("tests/fake_repos/readthedocs_samples/.readthedocs.yaml")
        },
        all_results
    )

    assert all_results[module_dict_key]['version'] in [1,2]
