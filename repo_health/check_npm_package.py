"""
Checks package published name on npm.
"""
import json
import os

import pytest
from pytest_repo_health import add_key_to_metadata, health_metadata

from repo_health import get_file_content

module_dict_key = "npm_package"


@pytest.fixture(name='npm_package')
def fixture_npm_package(repo_path):
    """Fixture containing the text content of package.json"""
    full_path = os.path.join(repo_path, "package.json")
    content = get_file_content(full_path)
    if content:
        return json.loads(get_file_content(full_path))

    return {}


@health_metadata(
    [module_dict_key],
    {
        "npm_package": "package name published on npm."
    })
def check_npm_package(npm_package, all_results):
    """
    verify pattern on npm site where package has prefix @edx/.
    """
    if 'name' in npm_package:
        all_results[module_dict_key] = npm_package['name'] if '@edx/' in npm_package['name'] else ''
    else:
        all_results[module_dict_key] = ''
