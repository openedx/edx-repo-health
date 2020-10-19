"""
Checks tox.ini format
"""
import os

import pytest
from pytest_repo_health import add_key_to_metadata, health_metadata
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
    Test to check if tox.ini has all the standard sections
    """
    required_sections = ["tox", "testenv", "testenv:quality"]
    all_results[module_dict_key]["has_section"] = {}
    for section in required_sections:
        section_head = "[" + section + "]"
        all_results[module_dict_key]["has_section"][section] = section_head in tox_ini


@add_key_to_metadata((module_dict_key, "uses_whitelist_externals"))
def check_whitelist_externals(tox_ini, all_results):
    """
    Does tox.ini still use the deprecated "whitelist_externals" setting
    (should be replaced with "allowlist_externals")
    """
    all_results[module_dict_key]["uses_whitelist_externals"] = "whitelist_externals" in tox_ini
