"""
Checks to see if Makefile follows standards
"""
import re
import os

import pytest
from pytest_repo_health import add_key_to_metadata
from repo_health import get_file_content


module_dict_key = "makefile"

@pytest.fixture
def makefile(repo_path):
    """Fixture containing the text content of Makefile"""
    full_path = os.path.join(repo_path, 'Makefile')
    return get_file_content(full_path)


@add_key_to_metadata((module_dict_key, "upgrade"))
def check_has_upgrade(makefile, all_results):
    """
    upgrade: makefile target that upgrades our dependencies to newer released versions
    """
    regex_pattern = "upgrade:"
    match = re.search(regex_pattern, makefile)
    all_results[module_dict_key]['upgrade'] = False
    if match is not None:
        all_results[module_dict_key]['upgrade'] = True
