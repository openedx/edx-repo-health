from pathlib import Path

import pytest

from repo_health import get_file_content
from repo_health.check_setup_py import (
    check_project_urls, check_pypi_name, check_repo_url, module_dict_key,
)

FAKE_REPO_ROOT = Path(__file__).parent / "fake_repos"

@pytest.mark.parametrize("fake_repo, pypi_name", [
    ("kodegail", "kodegail"),
    ("just_setup_py", "some_other_pypi_name"),
    ("just_setup_cfg", "setup_cfg_package"),
    ("docs_repo", None),
])
def test_check_pypi_name(fake_repo, pypi_name):
    setup_py = get_file_content(FAKE_REPO_ROOT / fake_repo / "setup.py")
    setup_cfg = get_file_content(FAKE_REPO_ROOT / fake_repo / "setup.cfg")
    all_results = {module_dict_key: {}}
    check_pypi_name(setup_py, setup_cfg, all_results)
    if pypi_name is not None:
        assert all_results[module_dict_key]["pypi_name"] == pypi_name
    else:
        assert "pypi_name" not in all_results[module_dict_key]

@pytest.mark.parametrize("fake_repo, repo_url", [
    ("just_setup_py", "https://github.com/openedx/just_setup_py"),
    ("just_setup_cfg", "https://github.com/openedx/just_setup_cfg"),
    ("docs_repo", None),
])
def test_check_repo_url(fake_repo, repo_url):
    setup_py = get_file_content(FAKE_REPO_ROOT / fake_repo / "setup.py")
    setup_cfg = get_file_content(FAKE_REPO_ROOT / fake_repo / "setup.cfg")
    all_results = {module_dict_key: {}}
    check_repo_url(setup_py, setup_cfg, all_results)
    print(all_results)
    if repo_url is not None:
        assert all_results[module_dict_key]["repo_url"] == repo_url
    else:
        assert "repo_url" not in all_results[module_dict_key]

@pytest.mark.parametrize("fake_repo, project_urls", [
    (
        "just_setup_py",
        '{\n     "Source": "https://github.com/openedx/just_setup_py",\n     "Bugs": "https://somebugs.com",\n }',
    ),
    (
        "just_setup_cfg",
        'Source = https://github.com/openedx/just_setup_py\n    Bugs = https://somebugs.com\n',
    ),
    ("docs_repo", None),
])
def test_check_project_urls(fake_repo, project_urls):
    setup_py = get_file_content(FAKE_REPO_ROOT / fake_repo / "setup.py")
    setup_cfg = get_file_content(FAKE_REPO_ROOT / fake_repo / "setup.cfg")
    all_results = {module_dict_key: {}}
    check_project_urls(setup_py, setup_cfg, all_results)
    if project_urls is not None:
        assert all_results[module_dict_key]["project_urls"] == project_urls
    else:
        assert "project_urls" not in all_results[module_dict_key]
