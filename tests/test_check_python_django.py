"""Test to run python django support in dependencies"""

import os

import pytest

# Because of fixtures: pylint: disable=unused-import
from dependencies_health.check_django import check_django_support_releases
from dependencies_health.check_python import check_python_support_releases
from dependencies_health.utils import get_release_tags


def test_check_python():
    repo_path = "path/to/repo"
    release_tags = get_release_tags(repo_path)
    all_results = {}
    check_python_support_releases(
        release_tags,
        all_results,
        repo_path
    )
    assert 'python' in list(all_results.keys())

def test_check_django():
    repo_path = "path/to/repo"
    release_tags = get_release_tags(repo_path)
    all_results = {}
    check_django_support_releases(
        release_tags,
        all_results,
        repo_path
    )
    assert 'django' in list(all_results.keys())
