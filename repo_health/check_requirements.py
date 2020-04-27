"""
 Checks whether repo requires some libraries
"""
import re
import glob
import os

import pytest
from repo_health import get_file_lines

from pytest_repo_health import health_metadata

module_dict_key = "requires"


@pytest.fixture
def req_lines(repo_path):
    """
    Fixture containing the text content of req_files
    """
    # TODO(jinder): make below work with inputs with both "/" at end and not
    files = glob.glob(os.path.join(repo_path, "requirements/**/*.in"), recursive=True)
    req_lines = []
    for file_path in files:
        lines = get_file_lines(file_path)
        req_lines.extend(lines)

    return req_lines


@health_metadata(
    [module_dict_key],
    {
        ("django"): "repo requires django",
        ("pytest"): "repo requires pytest",
        ("nose"): "repo requires nose",
    },
)
def check_requires(req_lines, all_results):
    """
    Test to find whether repo requires some key requirements
    """
    important_requirments = ["django", "pytest", "nose"]
    for req in important_requirments:
        all_results[module_dict_key][req] = False
        for line in req_lines:
            if re.search(req, line):
                all_results[module_dict_key][req] = True
