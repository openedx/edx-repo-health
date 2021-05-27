import os
import pytest

from repo_health.check_makefile import (
    module_dict_key,
    check_has_make_target,
    output_keys,
)


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


@pytest.mark.parametrize("fake_repo, flag_list", [
    ("makefile_repo1",
    {"upgrade": True,
    "quality": True,
    "test":  True,
    "test-js":  False,
    "test-python":  False,
    "quality-js":  False,
    "quality-python":  False
    }),
    ("makefile_repo2",
    {"upgrade": True,
    "quality": True,
    "test":  False,
    "test-js":  False,
    "test-python":  False,
    "quality-js":  True,
    "quality-python":  False
    })])

def test_check_file_existence(fake_repo, flag_list):
    repo_path = get_repo_path('fake_repos/'+ fake_repo)
    all_results = {module_dict_key:{}}
    file = open(repo_path+'/Makefile', 'r')
    check_has_make_target(file.read(), all_results)

    for key, desc in output_keys.items():
        assert all_results[module_dict_key][key] == flag_list[key]
