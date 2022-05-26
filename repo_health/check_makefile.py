"""
Checks to see if Makefile follows standards
"""
import re
import os

import pytest
from pytest_repo_health import health_metadata
from repo_health import get_file_content


module_dict_key = "makefile"
output_keys = {
    "upgrade": "target that upgrades our dependencies to newer released versions",
    "test": "target that runs tests",
    "quality": "target that runs code quality checks",
    "test-js": "target that runs javascript unit tests",
    "quality-js": "target that runs javascript code quality checks",
    "test-python": "target that runs python unit tests",
    "quality-python": "target that runs python code quality checks",
}


@pytest.fixture(name='makefile')
def fixture_makefile(repo_path):
    """Fixture containing the text content of Makefile"""
    full_path = os.path.join(repo_path, "Makefile")
    return get_file_content(full_path)


@health_metadata(
    [module_dict_key, "has_target"],
    output_keys
)
def check_has_make_target(makefile, all_results):
    """
    Checks make file has provided targets
    """
    for target, __ in output_keys.items():
        all_results[module_dict_key][target] = False
        regex_pattern = "".join(["^", target, ":"])
        match = re.search(regex_pattern, makefile, re.MULTILINE)
        if match:
            all_results[module_dict_key][target] = True

@health_metadata(
    [module_dict_key],
    {
        "pip-installed": "check if pip.txt was installed immediately after upgrade"
    }
)
def check_upgrade_script(makefile, all_results):
    """
    Checks if pip installed after upgrading pip.txt
    """
    upgrade_targets = re.finditer("^upgrade:", makefile, re.MULTILINE)

    for i in upgrade_targets:
        upgrade_script = makefile[i.end():]
        next_target = re.search("^[a-zA-Z_]+:", upgrade_script, re.MULTILINE)
        if next_target is not None:
            upgrade_script = upgrade_script[:next_target.start()]
        update_commands = (r"(\n\t(\$\(PIP_COMPILE\)|pip-compile)(.*?)((requirements/pip\.txt requirements/pip\.in)"
                           r"|(requirements/pip-tools\.txt requirements/pip-tools\.in))){2}")
        install_commands = r"(\n\t(pip install)(.*?)(requirements/pip.txt|requirements/pip-tools.txt)){2}"
        regex_pattern = "".join([update_commands, install_commands])
        match = re.search(regex_pattern, upgrade_script, re.MULTILINE)
        if match:
            all_results[module_dict_key]["pip-installed"] = True
            return

    all_results[module_dict_key]["pip-installed"] = False
