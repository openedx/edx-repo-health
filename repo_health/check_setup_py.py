"""
Checks to see if setup.py follows minimum standards
And gathers info
"""

import re
import os

import pytest
from pytest_repo_health import add_key_to_metadata
from repo_health import get_file_content

module_dict_key = "setup_py"


@pytest.fixture(name="setup_py")
def fixture_setup_py(repo_path):
    """Fixture containing the text content of setup.py"""
    full_path = os.path.join(repo_path, "setup.py")
    return get_file_content(full_path)


@pytest.fixture(name="python_versions_in_classifiers")
def fixture_python_version(setup_py):
    """
    The list of python versions in setup.py classifiers
    """
    regex_pattern = r"Programming Language ?:: ?Python ?:: ?([\d\.]+)"
    python_classifiers = re.findall(regex_pattern, setup_py, re.MULTILINE)
    return python_classifiers


@add_key_to_metadata((module_dict_key, "py38_classifiers"))
def check_has_python_38_classifiers(python_versions_in_classifiers, all_results):
    """
    Are there classifiers with python 3.8?
    """
    all_results[module_dict_key]["py38_classifiers"] = "3.8" in python_versions_in_classifiers
