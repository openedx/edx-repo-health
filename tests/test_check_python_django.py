"""Test to run pyhthon django support in dependencies"""

import os

import pytest

# Because of fixtures: pylint: disable=unused-import
from dependencies_health.check_python_django import check_python_django_support_releases, module_dict_key
from dependencies_health.utils import get_release_tags


def test_check_whitelist_externals():
    repo_path = "path/to/repo"
    release_tags = get_release_tags(repo_path)
    all_results = {module_dict_key:{}}
    check_python_django_support_releases(
        release_tags,
        all_results,
        repo_path
    )
    assert 'python' in list(all_results.keys())