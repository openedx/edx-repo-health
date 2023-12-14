"""
Checks to see if setup.py follows minimum standards
And gathers info
"""

import os
import re

import pytest
from pytest_repo_health import add_key_to_metadata

from repo_health import get_file_content

module_dict_key = "setup_py"


@pytest.fixture(name="setup_py", scope="session")
def fixture_setup_py(repo_path):
    """Fixture containing the text content of setup.py"""
    full_path = os.path.join(repo_path, "setup.py")
    return get_file_content(full_path)


@pytest.fixture(name="setup_cfg", scope="session")
def fixture_setup_cfg(repo_path):
    """Fixture containing the text content of setup.cfg"""
    full_path = os.path.join(repo_path, "setup.cfg")
    return get_file_content(full_path)


@pytest.fixture(name="python_version", scope="session")
def fixture_python_version(setup_py):
    """
    The list of python versions in setup.py classifiers
    """
    regex_pattern = r"Programming Language :: Python :: ([\d\.]+)"
    python_classifiers = re.findall(regex_pattern, setup_py, re.MULTILINE)
    return python_classifiers


@add_key_to_metadata((module_dict_key, "py38_classifiers"))
@pytest.mark.py_dependency_health
@pytest.mark.edx_health
def check_has_python_38_classifiers(python_version, all_results):
    """
    Are there classifiers with python 3.8?
    """
    all_results[module_dict_key]["py38_classifiers"] = "3.8" in python_version


@add_key_to_metadata((module_dict_key, "python_versions"))
@pytest.mark.py_dependency_health
@pytest.mark.edx_health
def check_travis_python_versions(python_version, all_results):
    """
    Add list of python versions to the results
    """
    all_results[module_dict_key]["python_versions"] = python_version


def set_pypi_name(all_results, setup_py_content, setup_cfg_content):
    """"
    A generic function that is use to set pypi name in the all_results dict
    """
    # Look in setup.py for:     name="package",
    py_names = re.findall(r"""(?m)^\s+name\s?=\s?['"]([\w-]+)['"],""", setup_py_content)
    # Look in setup.cfg for:    name=package
    cfg_names = re.findall(r"""(?m)^name\s?=\s?([\w-]+)""", setup_cfg_content)

    names = py_names + cfg_names
    # If the name doesn't match the expected format, don't fill it into the results.
    if names and len(names) == 1:
        all_results[module_dict_key]["pypi_name"] = names[0]
    return all_results


def set_repo_url(all_results, setup_py_content, setup_cfg_content):
    """
    A generic function that is use to set repo url in the all_results dict
    """
    py_urls = re.findall(r"""(?m)^\s*url\s*=\s*['"]([^'"]+)['"]""", setup_py_content)
    cfg_urls = re.findall(r"""(?m)^url\s*=\s*(\S+)""", setup_cfg_content)
    urls = py_urls + cfg_urls
    if urls:
        assert len(urls) == 1
        all_results[module_dict_key]["repo_url"] = urls[0]
    return all_results


def set_project_urls(all_results, setup_py_content, setup_cfg_content):
    """
    A generic function that is use to set project url in the all_results dict
    """
    py_urls = re.findall(r"""(?ms)^\s*project_urls\s*=\s*({[^}]+})""", setup_py_content)
    cfg_urls = re.findall(r"""(?ms)^project_urls\s*=\s*(.*?)(?:^\S|^$)""", setup_cfg_content)
    urls = py_urls + cfg_urls
    if urls:
        assert len(urls) == 1
        all_results[module_dict_key]["project_urls"] = urls[0]
    return all_results


@add_key_to_metadata((module_dict_key, "pypi_name"))
@pytest.mark.py_dependency_health
@pytest.mark.edx_health
def check_pypi_name(setup_py, setup_cfg, all_results):
    """
    Get the name of the PyPI package for this repo.
    """
    all_results = set_pypi_name(
        all_results,
        setup_py,
        setup_cfg
    )


@add_key_to_metadata((module_dict_key, "repo_url"))
@pytest.mark.py_dependency_health
@pytest.mark.edx_health
def check_repo_url(setup_py, setup_cfg, all_results):
    """
    Get the repo URL.
    """
    all_results = set_repo_url(
        all_results,
        setup_py,
        setup_cfg
    )


@add_key_to_metadata((module_dict_key, "project_urls"))
@pytest.mark.py_dependency_health
@pytest.mark.edx_health
def check_project_urls(setup_py, setup_cfg, all_results):
    """
    Get the additional project URLs.
    TODO: This captures the multi-line junk without parsing them out individually.
    """
    all_results = set_project_urls(
        all_results,
        setup_py,
        setup_cfg
    )
