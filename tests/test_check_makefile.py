import os
import pytest

from repo_health.check_makefile import (
    module_dict_key,
    check_has_make_target,
    check_upgrade_script,
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


@pytest.mark.parametrize("fake_repo, flag", [
    ("makefile_repo1",
    {"pip-installed": False
    }),
    ("makefile_repo2",
    {"pip-installed": True
    })])
def test_check_upgrade_script(fake_repo, flag):
    repo_path = get_repo_path('fake_repos/' + fake_repo)
    all_results = {module_dict_key: {}}
    file = open(repo_path + '/Makefile', 'r')
    check_upgrade_script(file.read(), all_results)
    assert all_results[module_dict_key]["pip-installed"] == flag["pip-installed"]
