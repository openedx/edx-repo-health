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
def check_readthedocs_file_exists(readthedocs_yaml, readthedocs_yml, all_results):
    """
    Check to see which file is there .readthedocs.yml or .readthedocs.yaml or Not found
    """
    all_results[module_dict_key]["exists"] = False
    if readthedocs_yaml:
        all_results[module_dict_key]["exists"] = "readthedocs.yaml"
    elif readthedocs_yml:
        all_results[module_dict_key]["exists"] = "readthedocs.yml"
 

@add_key_to_metadata((module_dict_key, "version"))
def check_readthedocs_file_version(readthedocs_yaml, readthedocs_yml, all_results):
    """
    Check to see if any of the readthedocs file exits then
    check its version and save into file
    """
    if readthedocs_yaml or readthedocs_yml:
        content_to_parse = readthedocs_yaml if readthedocs_yaml else readthedocs_yml 
        readthedocs_elements = OrderedDict(yaml.safe_load(content_to_parse))
        all_results[module_dict_key]["version"] = readthedocs_elements['version']
