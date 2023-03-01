import os

import pytest

from repo_health.check_requirements import check_requires, fixture_req_lines, module_dict_key


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/fake_repos/{repo_name}"


@pytest.mark.parametrize("repo_path, flag_list", [
    (get_repo_path("django_pytest_requirement"),
    {"django": True, "pytest": True,
    "boto":  False, "nose":  False,}),
    (get_repo_path("django_boto_nose_requirement"),
     {"django": True, "pytest": False,
      "boto": True, "nose": True, })])

def test_check_requires(req_lines, flag_list):
    all_results = {module_dict_key:{}}
    check_requires(req_lines, all_results)
    requirements = ['django', 'pytest', 'nose', 'boto']

    for req in requirements:
        assert all_results[module_dict_key][req] == flag_list[req]
