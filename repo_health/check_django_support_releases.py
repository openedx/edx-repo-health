"""
Contains the check to check the Django support releases
"""
import pytest
from pytest_repo_health import health_metadata

from .utils import find_django_version_in_setup_py_classifier, get_default_branch, get_release_tags, is_django_package

MODULE_DICT_KEY = "django"


@pytest.fixture(name='repo_release_tags')
def fixture_repo_release_tags(repo_path):
    """Fixture containing the repo release tags"""
    return get_release_tags(repo_path)


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "has_django": "Flag that tells if its Django package",
        "4.0": "Which release added support for Django 4.0",
        "4.1": "Which release added support for Django 4.1",
        "4.2": "Which release added support for Django 4.2",
    },
)
@pytest.mark.py_dependency_health
def check_django_support_releases(repo_release_tags, all_results, repo_path):
    """
    Check to check the django versions in the releases
    """
    if not repo_release_tags:
        all_results[MODULE_DICT_KEY] = {}
        print("There is not tag found")
        return
    django_versions = ['4.0', '4.1', '4.2']
    all_results[MODULE_DICT_KEY] = {}
    desc_tags_list = list(reversed(repo_release_tags))
    if not is_django_package(repo_path):
        all_results[MODULE_DICT_KEY]['has_django'] = False
        return
    # otherwise look for django version releases
    all_results[MODULE_DICT_KEY]['has_django'] = True
    for version in django_versions:
        latest_tag_having_django_support = None
        for tag in desc_tags_list:
            if not find_django_version_in_setup_py_classifier(repo_path, tag, version):
                if tag == desc_tags_list[0]: # try with default branch if the latest tag
                    default_branch = get_default_branch(repo_path)
                    if find_django_version_in_setup_py_classifier(repo_path, default_branch, version):
                        all_results[MODULE_DICT_KEY][version] = default_branch
                    else:
                        all_results[MODULE_DICT_KEY][version] = None
                else:
                    all_results[MODULE_DICT_KEY][version] = latest_tag_having_django_support
                break
            # if django version found in config files then set it as lastest tag having django support
            latest_tag_having_django_support = tag
