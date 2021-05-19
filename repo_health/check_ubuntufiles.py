"""
Checks package published name on npm.
"""
import json
import os

import pytest
from pytest_repo_health import health_metadata

from repo_health import read_docker_file, read_docker_parse_string
module_dict_key = "ubuntu_packages"


def get_docker_file_content(repo_path):
    """
   entry point to read parse and read dependencies
   @param repo_path:
   @return: json data.
   """

    # in credentials `Dockerfile-testing` name exists
    for file in ['Dockerfile', 'Dockerfile-testing', 'Dockerfile-3.8']:
        full_path = os.path.join(repo_path, file)
        content = read_docker_file(full_path)
        if content:
            break

    if not content:
        return

    value = []
    for con in content:
        fir,sec = False, False
        if 'RUN apt-get update' in con.original:
            value.append(con.original)
            fir = True
        if 'RUN apt-get install' in con.original:
            value.append(con.original)
            sec = True
        if fir and sec:
            break
    return value


@pytest.fixture(name='content')
def fixture_npm_package(repo_path):
    """Fixture containing the text content of package.json"""
    return get_docker_file_content(repo_path)


@health_metadata(
    [module_dict_key],
    {
        "ubuntu_packages": "package name published on npm."
    })
def check_npm_package(content, all_results):
    """
    verify pattern on npm site where package has prefix @edx/.
    """
    all_results[module_dict_key] = content
