"""
Checks tox.ini format
"""
import os
import re

import pytest
from pytest_repo_health import health_metadata
from repo_health import get_file_content

module_dict_key = "tox_ini"


@pytest.fixture(name='tox_ini')
def fixture_tox_ini(repo_path):
    """Fixture containing the text content of tox.ini"""
    full_path = os.path.join(repo_path, "tox.ini")
    return get_file_content(full_path)


@health_metadata(
    [module_dict_key, "has_section"],
    {
        "tox": "Section to define global settings, these apply to all envs defined in tox.ini",
        "whitelist_externals": "whitelist_externals has been deprecated in favour of allowlist_externals.",
        "testenv": "Settings that apply to all individual testenv:Name envs",
        "testenv:quality": "Env setting used to run quality linting on repo",
    },
)
def check_has_sections(tox_ini, all_results):
    """
    Test to check if makefile has an upgrade target
    """
    required_sections = [r"tox", r"testenv", r"testenv:quality", r"whitelist_externals"]
    all_results[module_dict_key]["has_section"] = {}
    for section in required_sections:
        regex_pattern = r"[" + section + r"]"
        match = re.search(regex_pattern, tox_ini)
        all_results[module_dict_key]["has_section"][section] = False
        if match is not None:
            all_results[module_dict_key]["has_section"][section] = True
