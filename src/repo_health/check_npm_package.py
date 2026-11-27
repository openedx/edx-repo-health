"""
Checks package published name on npm.
"""
import json
import os

import pytest
from pytest_repo_health import health_metadata

from repo_health import get_file_content

module_dict_key = "npm_package"


def get_dependencies(repo_path):
    """
   entry point to read parse and read dependencies
   @param repo_path:
   @return: json data.
   """
    full_path = os.path.join(repo_path, "package.json")
    content = get_file_content(full_path)
    if content:
        return json.loads(get_file_content(full_path))

    return {}


@pytest.fixture(name='content')
def fixture_npm_package(repo_path):
    """Fixture containing the text content of package.json"""
    return get_dependencies(repo_path)


@health_metadata(
    [module_dict_key],
    {
        "npm_package": "package name published on npm."
    })
@pytest.mark.edx_health
def check_npm_package(content, all_results):
    """
    verify pattern on npm site where package has prefix @edx/.
    """
    if 'name' in content:
        all_results[module_dict_key] = content['name'] if '@edx/' in content['name'] else ''
    else:
        all_results[module_dict_key] = ''
