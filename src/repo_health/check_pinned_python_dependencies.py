"""
Counts the python dependencies which are pinned
"""
import os

import pytest

from repo_health import get_file_content

module_dict_key = "pinned_python_dependencies"


def get_dependencies_count(repo_path, file_name):
    """
   entry point to read requirements from constraints and common-constraints
   @param repo_path:
   @param file_name:
   @return: number.
   """
    full_path = os.path.join(repo_path, "requirements/{0}".format(file_name))
    content = get_file_content(full_path)
    lines = content.split('\n')
    dependency_count = 0
    pinned_dependencies_marker = ['==', '>', '<']
    for line in lines:
        if line.startswith('#'):
            continue
        if any(marker in line for marker in pinned_dependencies_marker):
            dependency_count += 1
        else:
            continue
    return dependency_count


@pytest.mark.edx_health
def check_pinned_python_dependencies(repo_path, all_results):
    """
    We shall read constraints file
    """
    constraints_count = get_dependencies_count(repo_path, 'common_constraints.txt')
    common_constraints_count = get_dependencies_count(repo_path, 'constraints.txt')
    all_results[module_dict_key] = constraints_count + common_constraints_count
