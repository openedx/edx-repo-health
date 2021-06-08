#!/usr/bin/env python3

import pytest
import asyncio

from repo_health.check_github import (
    check_settings,
    MODULE_DICT_KEY,
    repo_license_exemptions,
)
from unittest.mock import Mock


def test_check_settings_license_exemption_present():
    """Test to make sure having an exemption in repo_license_exemptions results in change of license in all_results dict"""
    all_results = {MODULE_DICT_KEY: {}}
    github_repo_mock = Mock()
    test_repo = "test_repo"
    test_org = "test_org"
    test_license = "test_license"
    repo_license_exemptions[test_repo] = {
        "license": test_license,
        "owner": test_org,
        "more_info": "Bah",
    }

    github_repo_mock.object.name = test_repo
    github_repo_mock.object.owner.login = test_org
    github_repo_mock.object.license = None
    asyncio.run(check_settings(all_results, github_repo_mock))

    # clean up changes made to repo_license_exemption
    del repo_license_exemptions[test_repo]
    assert "license" in all_results["github"]
    assert all_results["github"]["license"] == test_license


def test_check_settings_no_license_exemption_present():
    """Test to make sure exemptions code does not make any changes when no exemption is present."""
    all_results = {MODULE_DICT_KEY: {}}
    github_repo_mock = Mock()
    test_repo = "test_repo"
    test_org = "test_org"
    test_license = "test_license"

    # make sure test_repo is not in repo_license_exemption,
    # if it is, you might want to change name of test_repo
    assert test_repo not in repo_license_exemptions

    github_repo_mock.object.license = None
    asyncio.run(check_settings(all_results, github_repo_mock))

    assert "license" in all_results["github"]
    assert all_results["github"]["license"] == None
