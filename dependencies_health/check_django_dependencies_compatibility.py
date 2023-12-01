"""
 contains check that reads/parses dependencies of a repo
"""

import logging

from repo_health.utils import set_django_packages

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "django_packages"


def check_django_dependencies_status(repo_path, all_results, django_deps_sheet):
    """
    Test to find the django dependencies compatibility
    """
    all_results = set_django_packages(
        repo_path,
        all_results,
        django_deps_sheet,
        MODULE_DICT_KEY
    )
