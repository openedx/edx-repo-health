from pathlib import Path

import pytest

from repo_health import get_file_content
from repo_health.check_setup_py import check_pypi_name, module_dict_key

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
