"""
Functions to check the existence of files.
"""
import os

from pytest_repo_health import health_metadata
from repo_health import get_file_content


module_dict_key = "exists"
output_keys = {
    "openedx.yaml": "openedx.yaml contains repository metadata as outlined in OEP-2",
    "Makefile": "Make targets",
    "tox.ini": "Tox configuration",
    ".travis.yml": "Travis configuration",
    "README.rst": "Basic level of documentation in the form of README.rst",
    "CHANGELOG.rst": "Change history",
    "pylintrc": "Pylint configuration",
    "setup.cfg": "Application setup configuration",
    "setup.py": "Application setup",
    ".coveragerc": "Test coverage configuration",
    ".editorconfig": "IDE configuration",
    ".pii_annotations.yml": "PII annotations as outline in OEP-0030",
    ".gitignore": "git ignore configuration",
    "package.json": "packages managed by npm",
    }


def file_exists(repo_path, file_name):
    full_path = os.path.join(repo_path, file_name)
    return bool(get_file_content(full_path))


@health_metadata(
    [module_dict_key],
    output_keys
)
def check_file_existence(repo_path, all_results):
    """
    Checks repository contains file which is not empty at root level
    """
    for file_name, _ in output_keys.items():
        all_results[module_dict_key][file_name] = file_exists(
            repo_path, file_name
        )
