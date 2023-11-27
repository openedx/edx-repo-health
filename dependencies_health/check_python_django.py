"""
Check some details
"""

import os

import pytest
from pytest_repo_health import add_key_to_metadata, health_metadata
from dependencies_health.utils import find_django_version_in_setup_py_classifier, find_python_version_in_config_files, get_default_branch, get_release_tags, is_django_package

module_dict_key = "python"


@pytest.fixture(name='repo_release_tags')
def fixture_repo_release_tags(repo_path):
    """Fixture containing the repo release tags"""
    return get_release_tags(repo_path)


def check_python_django_support_releases(repo_release_tags, all_results, repo_path):
    if not repo_release_tags:
        all_results[module_dict_key] = {}
        print(f"There is not tag found")
        return
    latest_tag_having_django_support = None
    latest_tag_having_python_support = None
    django_versions = ['4.0', '4.1', '4.2']
    python_versions = ['3.11']
    all_results[module_dict_key] = {'django': {}}
    desc_tags_list = list(reversed(repo_release_tags))
    if is_django_package(repo_path):
        all_results[module_dict_key]['has_django'] = True
        for version in django_versions:
            for tag in desc_tags_list:
                if not find_django_version_in_setup_py_classifier(repo_path, tag, version):
                    if tag == desc_tags_list[0]: # if the tag is latest the try with default latest/default branch as well
                        default_branch = get_default_branch(repo_path)
                        if find_django_version_in_setup_py_classifier(repo_path, default_branch, version):
                            all_results[module_dict_key]['django'][version] = default_branch
                        else:
                            all_results[module_dict_key]['django'][version] = None
                        break
                    all_results[module_dict_key]['django'][version] = latest_tag_having_django_support
                    break
                else:
                    latest_tag_having_django_support = tag
    else:
        all_results[module_dict_key]['has_django'] = False

    for version in python_versions:
        for tag in desc_tags_list:
            if not find_python_version_in_config_files(repo_path, tag, version):
                if tag == desc_tags_list[0]: # if the tag is latest the try with default latest/default branch as well
                    default_branch = get_default_branch(repo_path)
                    if find_python_version_in_config_files(repo_path, default_branch, version):
                        all_results[module_dict_key][version] = default_branch
                    else:
                        all_results[module_dict_key][version] = None
                    break

                all_results[module_dict_key][version] = latest_tag_having_python_support
                break
            else:
                latest_tag_having_python_support = tag
        