"""
Checks to see if Makefile follows standards
"""
import re
import os

import pytest
from pytest_repo_health import health_metadata
from repo_health import get_file_content


module_dict_key = "makefile"


@pytest.fixture(name='makefile')
def fixture_makefile(repo_path):
    """Fixture containing the text content of Makefile"""
    full_path = os.path.join(repo_path, "Makefile")
    return get_file_content(full_path)


@health_metadata(
    [module_dict_key, "has_target"],
    {
        "upgrade": "target that upgrades our dependencies to newer released versions",
        "test": "target that runs tests",
        "quality": "target that runs code quality checks",
        "test-js": "target that runs javascript unit tests",
        "quality-js": "target that runs javascript code quality checks",
        "test-python": "target that runs python unit tests",
        "quality-python": "target that runs python code quality checks",
    },
)
def check_has_make_target(makefile, all_results):
    """
    Checks make file has provided targets
    """
    targets = ["upgrade", "test", "quality", "test-js", "quality-js", "test-python", "quality-python"]
    for target in targets:
        all_results[module_dict_key][target] = False
        regex_pattern = "".join(["^", target, ":"])
        match = re.search(regex_pattern, makefile, re.MULTILINE)
        if match:
            all_results[module_dict_key][target] = True
