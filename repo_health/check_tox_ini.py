"""
Checks tox.ini format
"""
import os
import re

import pytest
from repo_health import get_file_content
from pytest_repo_health import health_metadata
import pdb

module_dict_key = 'tox_ini'


@pytest.fixture
def tox_ini(repo_path):
    """Fixture containing the text content of tox.ini"""
    #TODO(jinder): make below work with inputs with both "/" at end and not
    full_path = os.path.join(repo_path, '/tox.ini')
    return get_file_content(full_path)

@health_metadata([module_dict_key, "has_section"],
    {
    'tox': "TODO(jinder)",
    'testenv': "TODO(jinder)",
    'testenv:quality': "TODO(jinder"
    })
def check_has_sections(tox_ini, all_results):
    """
    Test to check if makefile has an upgrade target
    """
    pdb.set_trace()
    required_sections = [r'tox', r'testenv', r'testenv:quality']
    all_results[module_dict_key]['has_section'] = {}
    for section in required_sections:
        regex_pattern = r"[" + section + r"]"
        match = re.search(regex_pattern, tox_ini)
        all_results[module_dict_key]['has_section'][section] = False
        if match is not None:
             all_results[module_dict_key]['has_section'][section] = True
