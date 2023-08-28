"""
Applying the following checks:
- Does .readthedocs.yaml exists?
- Does .readthedocs.yml exists?
- Does version 2 exists in .readthedocs.yaml?
- Does version 2 exists in .readthedocs.yml?
"""
import os
from collections import OrderedDict

import pytest
import yaml
from pytest_repo_health import add_key_to_metadata

from repo_health import get_file_content

module_dict_key = "readthedocs"
readthedocs_yml_path=".readthedocs.yml"
readthedocs_yaml_path=".readthedocs.yaml"


@pytest.fixture(name="readthedocs_yml")
def fixture_readthedocs_yml(repo_path):
    """Fixture containing the text content of .readthedocs.yml"""
    full_path = os.path.join(repo_path, readthedocs_yml_path)
    return get_file_content(full_path)


@pytest.fixture(name="readthedocs_yaml")
def fixture_readthedocs_yaml(repo_path):
    """Fixture containing the text content of .readthedocs.yaml"""
    full_path = os.path.join(repo_path, readthedocs_yaml_path)
    return get_file_content(full_path)


@add_key_to_metadata((module_dict_key, "exists"))
def check_readthedocs_yml_exists(readthedocs_yaml, all_results):
    """
    Is .readthedocs.yml file exists
    """
    all_results[module_dict_key]["readthedocs_yml"] = {}
    all_results[module_dict_key]["readthedocs_yml"]["exists"] = bool(readthedocs_yaml)


@add_key_to_metadata((module_dict_key, "exists"))
def check_readthedocs_yaml_exists(readthedocs_yaml, all_results):
    """
    Is .readthedocs.yaml file exists
    """
    all_results[module_dict_key]["readthedocs_yaml"] = {}
    all_results[module_dict_key]["readthedocs_yaml"]["exists"] = bool(readthedocs_yaml)


@add_key_to_metadata((module_dict_key, "readthedocs_yaml_version"))
def check_readthedocs_yaml_version(readthedocs_yaml, all_results):
    """
    Is .readthedocs.yaml has version v2 or v1
    """
    if readthedocs_yaml:
        all_results[module_dict_key]["readthedocs_yaml"] = {}
        readthedocs_yaml_elements = OrderedDict(yaml.safe_load(readthedocs_yaml))
        if readthedocs_yaml_elements['version'] == 1:
            all_results[module_dict_key]["readthedocs_yaml"]["version"] = "V1"
        elif readthedocs_yaml_elements['version'] == 2:
            all_results[module_dict_key]["readthedocs_yaml"]["version"] = "V2"


@add_key_to_metadata((module_dict_key, "readthedocs_yml_version"))
def check_readthedocs_yml_version(readthedocs_yml, all_results):
    """
    Is .readthedocs.yml has version v2 or v1
    """
    if readthedocs_yml:
        all_results[module_dict_key]["readthedocs_yml"] = {}
        readthedocs_yml_elements = OrderedDict(yaml.safe_load(readthedocs_yml))
        if readthedocs_yml_elements['version'] == 1:
            all_results[module_dict_key]["readthedocs_yml"]["version"] = "V1"
        elif readthedocs_yml_elements['version'] == 2:
            all_results[module_dict_key]["readthedocs_yml"]["version"] = "V2"
