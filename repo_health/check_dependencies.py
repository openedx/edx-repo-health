"""
 Checks which are the dependencies of the repo
"""
import re
from pathlib import Path
import os

import pytest
from pytest_repo_health import health_metadata
from repo_health import get_file_lines

module_dict_key = "dependencies"


@pytest.fixture(name='dependencies')
def fixture_req_packages(repo_path):
    """
    Fixture containing the text content of req_files
    """
    pypi_packages = []
    github_packages = []
    files = [str(file) for file in Path(os.path.join(repo_path, "requirements")).rglob('*.txt')]
    constraints_files = ("constraints.txt", "pins.txt")
    requirement_files = [file for file in files if not file.endswith(constraints_files)]
    for file_path in requirement_files:
        lines = get_file_lines(file_path)
        stripped_lines = [re.sub(r' +#.*', "", line).replace('-e ', "")
                          for line in lines if line and not line.startswith("#")]
        github_packages.extend([line for line in stripped_lines if re.match(r'^git\+.*', line)])
        pypi_packages.extend([line for line in stripped_lines if line not in github_packages and "==" in line])

    return {
        "pypi": list(set(pypi_packages)),
        "github": list(set(github_packages)),
    }


@health_metadata(
    [module_dict_key],
    {
        "count": "count of total dependencies",
        "pypi.count": "count of PyPI packages",
        "pypi.list": "list of PyPI packages with required versions",
        "github.count": "count of GitHub packages",
        "github.list": "list of GitHub packages",
    },
)
def check_dependencies(dependencies, all_results):
    """
    Test to find the dependencies of the repo
    """
    all_results[module_dict_key] = {
        "count": len(dependencies["pypi"]) + len(dependencies["github"]),
        "pypi": {
            "count": len(dependencies["pypi"]),
            "list": dependencies["pypi"],
        },
        "github": {
            "count": len(dependencies["github"]),
            "list": dependencies["github"],
        },
    }
