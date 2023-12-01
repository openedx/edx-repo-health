"""
 contains check that reads/parses dependencies of a repo
"""

from repo_health.utils import set_repo_dependencies


module_dict_key = "dependencies"


def check_dependencies(repo_path, all_results):
    """
    Test to find the dependencies of the repo
    """
    all_results = set_repo_dependencies(
        all_results,
        repo_path,
        module_dict_key
    )
