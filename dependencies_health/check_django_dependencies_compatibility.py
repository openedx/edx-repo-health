"""
Contains check that reads/parses dependencies of a repo
"""

import logging

from repo_health.check_django_dependencies_compatibility import set_django_packages
from repo_health.fixtures.config_files import django_dependency_sheet_fixture  # pylint: disable=unused-import

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "django_packages"


def check_django_dependencies_status(repo_path, all_results, django_dependency_sheet_fixture):
    """
    Test to find the django dependencies compatibility
    """
    all_results = set_django_packages(
        repo_path,
        all_results,
        django_dependency_sheet_fixture
    )