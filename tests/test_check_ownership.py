"""Test checks for ownership info."""

import csv
import inspect
import os
from pathlib import Path
from unittest import mock

from repo_health.check_ownership import MODULE_DICT_KEY, check_ownership


def mocked_responses(*args, **kwargs):
    """Get mock ownership CSV data."""

    current_dir = os.path.dirname(__file__)

    with open(os.path.join(current_dir, 'data/ownership_data.csv'), 'r') as csv_file:
        file_data = csv.reader(csv_file)
        headers = next(file_data)
        return [dict(zip(headers, i)) for i in file_data]


@mock.patch('repo_health.check_ownership.find_worksheet')
@mock.patch.dict(os.environ, {
    "REPO_HEALTH_GOOGLE_CREDS_FILE": "test",
    "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL": "test",
    "REPO_HEALTH_REPOS_WORKSHEET_ID": "23"
})
def test_check_ownership(mock_get):
    mock_get.return_value = mocked_responses()

    all_results = {MODULE_DICT_KEY: {}}
    check_ownership(all_results, git_origin_url="github.com/edx/ownership_repo1.git", repo_path="")

    assert all_results[MODULE_DICT_KEY]['theme'] == 'openedx'
    assert all_results[MODULE_DICT_KEY]['squad'] == 'arch'
    assert all_results[MODULE_DICT_KEY]['priority'] == 'High'


@mock.patch('repo_health.check_ownership.find_worksheet_with_actions')
@mock.patch.dict(os.environ, {
    "REPO_HEALTH_GOOGLE_CREDS_FILE": '{"type": "test", "project_id": "test", "private_key_id": "test"}',
    "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL": "test",
    "REPO_HEALTH_REPOS_WORKSHEET_ID": "23"
})
def test_check_ownership_with_actions(mock_get):
    mock_get.return_value = mocked_responses()

    all_results = {MODULE_DICT_KEY: {}}
    check_ownership(all_results, git_origin_url="github.com/edx/ownership_repo1.git", repo_path="")

    assert all_results[MODULE_DICT_KEY]['theme'] == 'openedx'
    assert all_results[MODULE_DICT_KEY]['squad'] == 'arch'
    assert all_results[MODULE_DICT_KEY]['priority'] == 'High'


def test_check_ownership_uses_catalog_info_without_sheet_env(tmp_path):
    catalog = Path(tmp_path) / "catalog-info.yaml"
    catalog.write_text("spec:\n  owner: user:alice\n", encoding="utf-8")

    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        check_ownership(
            all_results,
            git_origin_url="github.com/edx/ownership_repo1.git",
            repo_path=str(tmp_path),
        )

    assert all_results[MODULE_DICT_KEY]["owner"] == "user:alice"
    assert all_results[MODULE_DICT_KEY]["owner_kind"] == "user"
    assert all_results[MODULE_DICT_KEY]["owner_name"] == "alice"


def test_check_ownership_strips_backstage_namespace(tmp_path):
    """A namespaced Backstage owner ref yields the bare team name."""
    catalog = Path(tmp_path) / "catalog-info.yaml"
    catalog.write_text("spec:\n  owner: group:default/team-x\n", encoding="utf-8")

    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        check_ownership(all_results, git_origin_url="github.com/openedx/repo.git", repo_path=str(tmp_path))

    assert all_results[MODULE_DICT_KEY]["owner"] == "group:default/team-x"
    assert all_results[MODULE_DICT_KEY]["owner_kind"] == "group"
    assert all_results[MODULE_DICT_KEY]["owner_name"] == "team-x"


def test_check_ownership_emits_empty_owner_keys_when_no_catalog(tmp_path):
    """Owner keys are always present (empty) so the CSV column exists."""
    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        check_ownership(all_results, git_origin_url="github.com/openedx/repo.git", repo_path=str(tmp_path))

    assert all_results[MODULE_DICT_KEY]["owner"] == ""
    assert all_results[MODULE_DICT_KEY]["owner_name"] == ""


def test_check_ownership_survives_non_git_origin(tmp_path):
    """A non-.git origin URL must not crash the check (falls back to catalog-info)."""
    catalog = Path(tmp_path) / "catalog-info.yaml"
    catalog.write_text("spec:\n  owner: user:bob\n", encoding="utf-8")

    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        # No trailing ".git" — previously raised AssertionError in github_org_repo.
        check_ownership(all_results, git_origin_url="https://github.com/openedx/repo", repo_path=str(tmp_path))

    assert all_results[MODULE_DICT_KEY]["owner_name"] == "bob"


@mock.patch.dict(os.environ, {
    "REPO_HEALTH_GOOGLE_CREDS_FILE": "test",
    "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL": "test",
    "REPO_HEALTH_REPOS_WORKSHEET_ID": "not-an-int",
})
def test_check_ownership_survives_non_integer_worksheet_id(tmp_path):
    """A non-integer worksheet id must not crash the check."""
    catalog = Path(tmp_path) / "catalog-info.yaml"
    catalog.write_text("spec:\n  owner: user:carol\n", encoding="utf-8")

    all_results = {MODULE_DICT_KEY: {}}
    check_ownership(all_results, git_origin_url="github.com/openedx/repo.git", repo_path=str(tmp_path))

    assert all_results[MODULE_DICT_KEY]["owner_name"] == "carol"


def test_check_ownership_requires_repo_path_fixture():
    """pytest only injects fixtures into parameters without defaults."""
    repo_path = inspect.signature(check_ownership).parameters["repo_path"]
    assert repo_path.default is inspect.Parameter.empty


def test_check_ownership_emits_lifecycle_type_and_release(tmp_path):
    """Catalog lifecycle, type and the openedx.org/release annotation are emitted."""
    catalog = Path(tmp_path) / "catalog-info.yaml"
    catalog.write_text(
        "metadata:\n"
        "  annotations:\n"
        "    openedx.org/release: \"master\"\n"
        "spec:\n"
        "  owner: group:openedx-unmaintained\n"
        "  type: 'xblock'\n"
        "  lifecycle: 'production'\n",
        encoding="utf-8",
    )

    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        check_ownership(all_results, git_origin_url="github.com/openedx/repo.git", repo_path=str(tmp_path))

    assert all_results[MODULE_DICT_KEY]["lifecycle"] == "production"
    assert all_results[MODULE_DICT_KEY]["component_type"] == "xblock"
    assert all_results[MODULE_DICT_KEY]["release"] == "master"


def test_check_ownership_null_release_annotation_is_empty(tmp_path):
    """`openedx.org/release: null` means not in releases, emitted as empty."""
    catalog = Path(tmp_path) / "catalog-info.yaml"
    catalog.write_text(
        "metadata:\n  annotations:\n    openedx.org/release: null\nspec:\n  owner: user:dave\n",
        encoding="utf-8",
    )

    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        check_ownership(all_results, git_origin_url="github.com/openedx/repo.git", repo_path=str(tmp_path))

    assert all_results[MODULE_DICT_KEY]["release"] == ""
    assert all_results[MODULE_DICT_KEY]["lifecycle"] == ""
    assert all_results[MODULE_DICT_KEY]["owner_name"] == "dave"


def test_check_ownership_emits_empty_catalog_details_when_no_catalog(tmp_path):
    """Detail keys are always present (empty) so the CSV columns exist."""
    all_results = {MODULE_DICT_KEY: {}}
    with mock.patch.dict(os.environ, {}, clear=True):
        check_ownership(all_results, git_origin_url="github.com/openedx/repo.git", repo_path=str(tmp_path))

    for key in ("lifecycle", "component_type", "release"):
        assert all_results[MODULE_DICT_KEY][key] == ""
