"""
Checks to see if setup.py follows minimum standards
And gathers info
"""

import re

from repo_health.check_setup_py import (
    set_pypi_name,
    set_repo_url,
    fixture_python_version,
    fixture_setup_cfg,
    fixture_setup_py
)

module_dict_key = "setup_py"


def check_pypi_name(fixture_setup_py, fixture_setup_cfg, all_results):
    """
    Get the name of the PyPI package for this repo.
    """
    all_results = set_pypi_name(
        all_results,
        fixture_setup_py,
        fixture_setup_cfg,
        module_dict_key
    )


def check_has_python_38_classifiers(fixture_python_version, all_results):
    """
    Are there classifiers with python 3.8?
    """
    all_results[module_dict_key]["py38_classifiers"] = "3.8" in fixture_python_version


def check_travis_python_versions(fixture_python_version, all_results):
    """
    Add list of python versions to the results
    """
    all_results[module_dict_key]["python_versions"] = fixture_python_version


def check_repo_url(fixture_setup_py, fixture_setup_cfg, all_results):
    """
    Get the repo URL.
    """
    all_results = set_repo_url(
        all_results,
        fixture_setup_py,
        fixture_setup_cfg,
        module_dict_key
    )


def check_project_urls(fixture_setup_py, fixture_setup_cfg, all_results):
    """
    Get the additional project URLs.
    TODO: This captures the multi-line junk without parsing them out individually.
    """
    py_urls = re.findall(r"""(?ms)^\s*project_urls\s*=\s*({[^}]+})""", fixture_setup_py)
    cfg_urls = re.findall(r"""(?ms)^project_urls\s*=\s*(.*?)(?:^\S|^$)""", fixture_setup_cfg)
    urls = py_urls + cfg_urls
    if urls:
        assert len(urls) == 1
        all_results[module_dict_key]["project_urls"] = urls[0]
