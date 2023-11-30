import pytest
from dependencies_health.utils import (
    find_python_version_in_config_files,
    get_default_branch,
    get_release_tags
)

module_dict_key = "python"


@pytest.fixture(name='repo_release_tags')
def fixture_repo_release_tags(repo_path):
    """Fixture containing the repo release tags"""
    return get_release_tags(repo_path)


def check_python_support_releases(repo_release_tags, all_results, repo_path):
    if not repo_release_tags:
        all_results[module_dict_key] = {}
        print(f"There is not tag found")
        return
    latest_tag_having_python_support = None
    python_versions = ['3.8', '3.9', '3.10', '3.11']
    all_results[module_dict_key] = {}
    desc_tags_list = list(reversed(repo_release_tags))
    
    for version in python_versions:
        for tag in desc_tags_list:
            if not find_python_version_in_config_files(repo_path, tag, version):
                if tag == desc_tags_list[0]:  # if the tag is the latest, then try with the default latest/default branch as well
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
