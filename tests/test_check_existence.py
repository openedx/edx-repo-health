import os
import pytest

from repo_health.check_existence import (
    check_readme_existence,
    check_dir_existence,
    check_file_existence,
    check_path_existence,
    req_dirs,
    req_files,
    req_paths,
    module_dict_key
)


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


@pytest.mark.parametrize("fake_repo, flag_list", [
    ("kodegail", {
        "openedx.yaml": False,
        "Makefile": False,
        "tox.ini": False,
        ".travis.yml": False,
        "README.rst": False,
        "CHANGELOG.rst": False,
        "pylintrc": False,
        "setup.cfg": True,
        "setup.py": True,
        ".coveragerc": False,
        ".editorconfig": False,
        ".pii_annotations.yml": False,
        ".gitignore": False,
        "package.json": False,
        "config": False,
    }),
    ("python_js_repo", {
        "openedx.yaml": False,
        "Makefile": False,
        "tox.ini": False,
        ".travis.yml": False,
        "README.rst": False,
        "CHANGELOG.rst": False,
        "pylintrc": False,
        "setup.cfg": False,
        "setup.py": False,
        ".coveragerc": False,
        ".editorconfig": False,
        ".pii_annotations.yml": False,
        ".gitignore": False,
        "package.json": True,
        "config": True,
    }),
    ("just_setup_py", {
        "openedx.yaml": False,
        "Makefile": False,
        "tox.ini": False,
        ".travis.yml": False,
        "README.rst": False,
        "CHANGELOG.rst": False,
        "pylintrc": False,
        "setup.cfg": False,
        "setup.py": True,
        ".coveragerc": False,
        ".editorconfig": False,
        ".pii_annotations.yml": False,
        ".gitignore": False,
        "package.json": False,
        "config": False,
    })
])
def test_check_file_existence(fake_repo, flag_list):
    repo_path = get_repo_path(f'fake_repos/{fake_repo}')
    all_results = {module_dict_key: {}}
    check_file_existence(repo_path, all_results)

    for file in req_files.keys():
        assert all_results[module_dict_key][file] == flag_list[file]


@pytest.mark.parametrize("fake_repo, flag_list", [
    ("kodegail", {"requirements": False}),
    ("python_js_repo", {"requirements": True}),
])
def test_check_dir_existence(fake_repo, flag_list):
    repo_path = get_repo_path(f'fake_repos/{fake_repo}')
    all_results = {module_dict_key: {}}
    check_dir_existence(repo_path, all_results)

    for dir in req_dirs.keys():
        assert all_results[module_dict_key][dir] == flag_list[dir]


@pytest.mark.parametrize("fake_repo, flag_list", [
    ("just_setup_cfg", {
        "commitlint.yml": False,
    }),
    ("python_repo", {
        "commitlint.yml": True,
    }),
])
def test_check_path_existence(fake_repo, flag_list):
    repo_path = get_repo_path(f'fake_repos/{fake_repo}')
    all_results = {module_dict_key: {}}
    check_path_existence(repo_path, all_results)

    for _, key, _ in req_paths:
        assert all_results[module_dict_key][key] == flag_list[key]


@pytest.mark.parametrize("fake_repo, flag", [
    ("docs_repo", True),
    ("js_repo", True),
    ("just_setup_cfg", False),
])
def test_readme_existence(fake_repo, flag):
    repo_path = get_repo_path(f'fake_repos/{fake_repo}')
    all_results = {module_dict_key: {}}
    check_readme_existence(repo_path, all_results)

    assert all_results[module_dict_key]['README'] == flag
