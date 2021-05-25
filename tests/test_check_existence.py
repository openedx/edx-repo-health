import os
import pytest

from repo_health.check_existence import (
    check_readme_existence,
    check_dir_existence,
    check_file_existence,
    req_dirs,
    req_files,
    module_dict_key
)


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


@pytest.mark.parametrize("fake_repo, flag_list", [
    ("kodegail",
    {"openedx.yaml": False,
    "Makefile": False,
    "tox.ini":  False,
    ".travis.yml":  False,
    "README.rst":  False,
    "CHANGELOG.rst":  False,
    "pylintrc":  False,
    "setup.cfg":  True,
    "setup.py":  True,
    ".coveragerc":  False,
    ".editorconfig":  False,
    ".pii_annotations.yml":  False,
    ".gitignore":  False,
    "package.json":  False,
    }),
    ("python_js_repo", {"openedx.yaml": False,
    "Makefile": False,
    "tox.ini":  False,
    ".travis.yml":  False,
    "README.rst":  False,
    "CHANGELOG.rst":  False,
    "pylintrc":  False,
    "setup.cfg":  False,
    "setup.py":  False,
    ".coveragerc":  False,
    ".editorconfig":  False,
    ".pii_annotations.yml":  False,
    ".gitignore":  False,
    "package.json":  True,
    }),("just_setup_py",
    {"openedx.yaml": False,
    "Makefile": False,
    "tox.ini":  False,
    ".travis.yml":  False,
    "README.rst":  False,
    "CHANGELOG.rst":  False,
    "pylintrc":  False,
    "setup.cfg":  False,
    "setup.py":  True,
    ".coveragerc":  False,
    ".editorconfig":  False,
    ".pii_annotations.yml":  False,
    ".gitignore":  False,
    "package.json":  False,
    })])

def test_check_file_existence(fake_repo, flag_list):
    repo_path = get_repo_path('fake_repos/'+ fake_repo)
    all_results = {module_dict_key:{}}
    check_file_existence(repo_path, all_results)

    for file, desc in req_files.items():
        assert all_results[module_dict_key][file] == flag_list[file]


@pytest.mark.parametrize("fake_repo, flag_list", [
    ("kodegail",{"requirements": False}),
    ("python_js_repo", {"requirements": True})])

def test_check_dir_existence(fake_repo, flag_list):
    repo_path = get_repo_path('fake_repos/'+ fake_repo)
    all_results = {module_dict_key:{}}
    check_dir_existence(repo_path, all_results)

    for dir, desc in req_dirs.items():
        assert all_results[module_dict_key][dir] == flag_list[dir]


@pytest.mark.parametrize("fake_repo, flag", [
    ("docs_repo", True),
    ("js_repo", True),
    ("just_setup_cfg", False)])
def test_readme_existence(fake_repo, flag):
    repo_path = get_repo_path('fake_repos/' + fake_repo)
    all_results = {module_dict_key: {}}
    check_readme_existence(repo_path, all_results)

    assert all_results[module_dict_key]['README'] == flag
