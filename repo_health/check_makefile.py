"""
Checks to see if Makefile follows standards
"""
import re
import os

import pytest
from repo_health import get_file_content


module_dict_key = "makefile"

@pytest.fixture
def makefile(repo_path):
    """Fixture containing the text content of Makefile"""
    full_path = os.path.join(repo_path, 'Makefile')
    return get_file_content(full_path)


def check_makefile_exists(makefile, all_results):
    """
    Test to check if repo has Makefile
    """
    all_results[module_dict_key]['exists'] = bool(makefile)

def check_has_upgrade(makefile, all_results):
    """
    Test to check if makefile has an upgrade target
    """
    regex_pattern = "upgrade:"
    match = re.search(regex_pattern, makefile)
    all_results[module_dict_key]['has_upgrade_target'] = False
    if match is not None:
        all_results[module_dict_key]['has_upgrade_target'] = True
