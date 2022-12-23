"""
Checks to see if setup.py follows minimum standards
And gathers info
"""

import re
import os

import pytest
from pytest_repo_health import add_key_to_metadata
from repo_health import get_file_content

module_dict_key = "setup_py"


@pytest.fixture(name="setup_py")
def fixture_setup_py(repo_path):
    """Fixture containing the text content of setup.py"""
    full_path = os.path.join(repo_path, "setup.py")
    return get_file_content(full_path)


@pytest.fixture(name="setup_cfg")
def fixture_setup_cfg(repo_path):
    """Fixture containing the text content of setup.cfg"""
    full_path = os.path.join(repo_path, "setup.cfg")
    return get_file_content(full_path)


@pytest.fixture(name="python_versions_in_classifiers")
def fixture_python_version(setup_py):
    """
    The list of python versions in setup.py classifiers
    """
    regex_pattern = r"Programming Language :: Python :: ([\d\.]+)"
    python_classifiers = re.findall(regex_pattern, setup_py, re.MULTILINE)
    return python_classifiers


@add_key_to_metadata((module_dict_key, "py38_classifiers"))
def check_has_python_38_classifiers(python_versions_in_classifiers, all_results):
    """
    Are there classifiers with python 3.8?
    """
    all_results[module_dict_key]["py38_classifiers"] = "3.8" in python_versions_in_classifiers


@add_key_to_metadata((module_dict_key, "python_versions"))
def check_travis_python_versions(python_versions_in_classifiers, all_results):
    """
    Add list of python versions to the results
    """
    all_results[module_dict_key]["python_versions"] = python_versions_in_classifiers


@add_key_to_metadata((module_dict_key, "pypi_name"))
def check_pypi_name(setup_py, setup_cfg, all_results):
    """
    Get the name of the PyPI package for this repo.
    """
    # Look in setup.py for:     name="package",
    py_names = re.findall(r"""(?m)^\s+name\s?=\s?['"]([\w-]+)['"],""", setup_py)
    # Look in setup.cfg for:    name=package
    cfg_names = re.findall(r"""(?m)^name\s?=\s?([\w-]+)""", setup_cfg)

    names = py_names + cfg_names
    if names:
        assert len(names) == 1
        all_results[module_dict_key]["pypi_name"] = names[0]


@add_key_to_metadata((module_dict_key, "repo_url"))
def check_repo_url(setup_py, setup_cfg, all_results):
    """
    Get the repo URL.
    """
    py_urls = re.findall(r"""(?m)^\s*url\s*=\s*['"]([^'"]+)['"]""", setup_py)
    cfg_urls = re.findall(r"""(?m)^url\s*=\s*(\S+)""", setup_cfg)
    urls = py_urls + cfg_urls
    if urls:
        assert len(urls) == 1
        all_results[module_dict_key]["repo_url"] = urls[0]


@add_key_to_metadata((module_dict_key, "project_urls"))
def check_project_urls(setup_py, setup_cfg, all_results):
    """
    Get the additional project URLs.
    TODO: This captures the multi-line junk without parsing them out individually.
    """
    py_urls = re.findall(r"""(?ms)^\s*project_urls\s*=\s*({[^}]+})""", setup_py)
    cfg_urls = re.findall(r"""(?ms)^project_urls\s*=\s*(.*?)(?:^\S|^$)""", setup_cfg)
    urls = py_urls + cfg_urls
    if urls:
        assert len(urls) == 1
        all_results[module_dict_key]["project_urls"] = urls[0]
