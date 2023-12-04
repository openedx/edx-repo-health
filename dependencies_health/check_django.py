"""
Contains the check to check the Django versions releases
"""
import pytest

from dependencies_health.utils import (find_django_version_in_setup_py_classifier, get_default_branch, get_release_tags,
                                       is_django_package)

module_dict_key = "django"


@pytest.fixture(name='repo_release_tags')
def fixture_repo_release_tags(repo_path):
    """Fixture containing the repo release tags"""
    return get_release_tags(repo_path)


def check_django_support_releases(repo_release_tags, all_results, repo_path):
    """
    Check to check the django versions in the releases
    """
    if not repo_release_tags:
        all_results[module_dict_key] = {}
        print("There is not tag found")
        return
    latest_tag_having_django_support = None
    django_versions = ['4.0', '4.1', '4.2']
    all_results[module_dict_key] = {}
    desc_tags_list = list(reversed(repo_release_tags))

    if is_django_package(repo_path):
        all_results[module_dict_key]['has_django'] = True
        for version in django_versions:
            for tag in desc_tags_list:
                if not find_django_version_in_setup_py_classifier(repo_path, tag, version):
                    if tag == desc_tags_list[0]: # try with default branch if the latest tag
                        default_branch = get_default_branch(repo_path)
                        if find_django_version_in_setup_py_classifier(repo_path, default_branch, version):
                            all_results[module_dict_key][version] = default_branch
                        else:
                            all_results[module_dict_key][version] = None
                        break
                    all_results[module_dict_key][version] = latest_tag_having_django_support
                    break
                else:
                    latest_tag_having_django_support = tag
    else:
        all_results[module_dict_key]['has_django'] = False
