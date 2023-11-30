"""
Checks to see if setup.py follows minimum standards
And gathers info
"""

from pytest_repo_health import add_key_to_metadata

from repo_health.utils import set_project_urls, set_pypi_name, set_repo_url

module_dict_key = "setup_py"


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
    all_results = set_pypi_name(
        all_results,
        setup_py,
        setup_cfg,
        module_dict_key
    )


@add_key_to_metadata((module_dict_key, "repo_url"))
def check_repo_url(setup_py, setup_cfg, all_results):
    """
    Get the repo URL.
    """
    all_results = set_repo_url(
        all_results,
        setup_py,
        setup_cfg,
        module_dict_key
    )


@add_key_to_metadata((module_dict_key, "project_urls"))
def check_project_urls(setup_py, setup_cfg, all_results):
    """
    Get the additional project URLs.
    TODO: This captures the multi-line junk without parsing them out individually.
    """
    all_results = set_project_urls(
        all_results,
        setup_py,
        setup_cfg,
        module_dict_key
    )

