"""
Contains the checks to check the python versions releases
"""
import pytest

from dependencies_health.utils import find_python_version_in_config_files, get_default_branch, get_release_tags

module_dict_key = "python"


@pytest.fixture(name='repo_release_tags')
def fixture_repo_release_tags(repo_path):
    """Fixture containing the repo release tags"""
    return get_release_tags(repo_path)


def check_python_support_releases(repo_release_tags, all_results, repo_path):
    """
    Check to see the python version releases for 3.8, 3.9, 3.10, 3.11
    """
    if not repo_release_tags:
        all_results[module_dict_key] = {}
        print("There is not tag found")
        return
    python_versions = ['3.8', '3.9', '3.10', '3.11']
    all_results[module_dict_key] = {}
    desc_tags_list = list(reversed(repo_release_tags))
    for version in python_versions:
        latest_tag_having_python_support = None
        for tag in desc_tags_list:
            if not find_python_version_in_config_files(repo_path, tag, version):
                # try with the default latest/default branch if it is latest tag
                # because support sometimes added in master or default branch and not released
                if tag == desc_tags_list[0]:
                    default_branch = get_default_branch(repo_path)
                    if find_python_version_in_config_files(repo_path, default_branch, version):
                        all_results[module_dict_key][version] = default_branch
                    else:
                        all_results[module_dict_key][version] = None
                else:
                    all_results[module_dict_key][version] = latest_tag_having_python_support
                break
            # if python version found in config files then set it as lastest tag having python support
            latest_tag_having_python_support = tag
