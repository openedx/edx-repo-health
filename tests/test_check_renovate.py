"""Tests for Renovate checks."""

import os
from unittest import mock

import pytest

from repo_health.check_renovate import MODULE_DICT_KEY, check_renovate


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/fake_repos/{repo_name}"


async def mocked_responses(*args, **kwargs):
    return  "24-4-2016"


@mock.patch('repo_health.check_renovate.get_last_pull_date')
@mock.patch('repo_health.check_renovate.get_total_pull_requests')
@pytest.mark.asyncio
async def test_check_renovate_true(mock_get):
    mock_get.return_value = await mocked_responses()
    all_results = {MODULE_DICT_KEY: {}}
    await check_renovate(all_results, repo_path=get_repo_path('renovate_repo1'), github_repo=None)

    assert all_results[MODULE_DICT_KEY]['configured'] is True

@mock.patch('repo_health.check_renovate.get_last_pull_date')
@mock.patch('repo_health.check_renovate.get_total_pull_requests')
@pytest.mark.asyncio
async def test_check_renovate_false(mock_get):
    mock_get.return_value = await mocked_responses()
    all_results = {MODULE_DICT_KEY: {}}
    await check_renovate(all_results, repo_path=get_repo_path('js_repo'), github_repo=None)

    assert all_results[MODULE_DICT_KEY]['configured'] is False
