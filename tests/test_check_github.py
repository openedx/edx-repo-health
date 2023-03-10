"""Testing functions in repo_health/check_github.py"""

from unittest.mock import AsyncMock

import pytest

from repo_health.check_github import MODULE_DICT_KEY, check_settings, repo_license_exemptions


@pytest.mark.asyncio
async def test_check_settings_license_exemption_present():
    """
    Test to make sure having an exemption in repo_license_exemptions results in change of license in all_results dict
    """
    all_results = {MODULE_DICT_KEY: {}}
    github_repo_mock = AsyncMock()
    test_repo = "test_repo"
    test_org = "test_org"
    test_license = "test_license"
    repo_license_exemptions[test_repo] = {
        "license": test_license,
        "owner": test_org,
        "more_info": "Bah",
    }

    github_repo_mock.return_value.object.name = test_repo
    github_repo_mock.return_value.object.owner.login = test_org
    github_repo_mock.return_value.object.license = None

    await check_settings(all_results, github_repo_mock())

    # clean up changes made to repo_license_exemption
    del repo_license_exemptions[test_repo]
    assert "license" in all_results["github"]
    assert all_results["github"]["license"] == test_license


@pytest.mark.asyncio
async def test_check_settings_no_license_exemption_present():
    """
    Test to make sure exemptions code does not make any changes when no exemption is present.
    """
    all_results = {MODULE_DICT_KEY: {}}
    github_repo_mock = AsyncMock()
    test_repo = "test_repo"

    # make sure test_repo is not in repo_license_exemption,
    # if it is, you might want to change name of test_repo
    assert test_repo not in repo_license_exemptions

    github_repo_mock.return_value.object.license = None

    await check_settings(all_results, github_repo_mock())

    assert "license" in all_results["github"]
    assert all_results["github"]["license"] is None
