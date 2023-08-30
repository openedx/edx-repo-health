"""
Applying the following checks:
Does any of the following readthedocs config file exists:
 - readthedocs.yml
 - readthedocs.yaml
 - .readthedocs.yml
 - .readthedocs.yaml
What is the name of file and version
"""
import os
from collections import OrderedDict

import pytest
import yaml
from pytest_repo_health import add_key_to_metadata

from repo_health import get_file_content

module_dict_key = "readthedocs_config"


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
        file_content = get_file_content(os.path.join(repo_path, readthedocs_file))
        if file_content:
            return {
                "file_name": readthedocs_file,
                "file_content": file_content
            }
    return {}


@add_key_to_metadata((module_dict_key, "exists"))
def check_readthedocs_file_exists(readthedocs_config_details, all_results):
    """
    Check to see readthedocs exits
    """
    all_results[module_dict_key]["exists"] = bool(readthedocs_config_details)


@add_key_to_metadata((module_dict_key, "file_name"))
def check_readthedocs_file_name(readthedocs_config_details, all_results):
    """
    Check to set the readthedocs file name
    """
    all_results[module_dict_key]["file_name"] = ""
    if readthedocs_config_details:
        all_results[module_dict_key]["file_name"] = readthedocs_config_details["file_name"]


@add_key_to_metadata((module_dict_key, "version"))
def check_readthedocs_file_version(readthedocs_config_details, all_results):
    """
    Check to set the file version of readthedocs file
    """
    all_results[module_dict_key]["version"] = ""
    if readthedocs_config_details:
        readthedocs_elements = OrderedDict(yaml.safe_load(readthedocs_config_details["file_content"]))
        all_results[module_dict_key]["version"] = readthedocs_elements['version']
