"""Test checks of Python dependencies."""

import os

from repo_health.check_dependencies import get_dependencies


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


def test_python_js_repo_dependency_check():
    repo_path = get_repo_path('fake_repos/python_js_repo')
    dependencies = get_dependencies(repo_path)

    assert 'fs==2.0.18' in dependencies["pypi_all"]["list"]
    assert "react-redux" in dependencies["js"]["list"]
    assert dependencies["count"] == 347
    assert dependencies["pypi_all"]["count"] == 295
    assert dependencies["github"]["count"] == 15
    assert dependencies["js.all"]["count"] == 10
    assert dependencies["js"]["count"] == 26
    assert dependencies["pypi"]["count"] == 223


def test_js_repo_dependency_check():
    repo_path = get_repo_path('fake_repos/js_repo')
    dependencies = get_dependencies(repo_path)

    assert 'core-js' in dependencies["js"]["list"]
    assert 'jest' in dependencies["js.dev"]["list"]
    assert 'babel' in dependencies["js.all"]["list"]

    assert dependencies["count"] == 37
    assert dependencies["js"]["count"] == 26
    assert dependencies["js.dev"]["count"] == 11
    assert dependencies["pypi_all"]["count"] == 0
    assert dependencies["js.all"]["count"] == 12
    assert dependencies["pypi"]["count"] == 0


def test_python_repo_dependency_check():
    repo_path = get_repo_path('fake_repos/python_repo')
    dependencies = get_dependencies(repo_path)

    assert 'django==2.2.24' in dependencies["pypi_all"]["list"]
    assert 'git+https://github.com/openedx/credentials-themes.git@0.1.62#egg=edx_credentials_themes==0.1.62' \
           in dependencies["github"]["list"]
    assert dependencies["pypi_all"]["count"] == 65
    assert dependencies["github"]["count"] == 1
    assert dependencies["js"]["count"] == 0
    assert dependencies["pypi"]["count"] == 8
