"""Test checks for Travis integration."""

from unittest.mock import patch

import requests
import responses

from repo_health.check_travis_integration import TRAVIS_API_URL, TravisIntegrationHandler


@responses.activate
def mock_non_existent_repo_response():
    """Mock response for missing repo."""
    url = "{api_url}{repo_name}".format(api_url=TRAVIS_API_URL, repo_name="edx-platform")
    responses.add(responses.GET, url, json={"@type": "error", "error_type": "not_found",
                                            "error_message": "repository not found (or insufficient access)",
                                            "resource_type": "repository"}, status=404)
    return requests.get(url)


@responses.activate
def mock_on_com_repo_response():
    """Mock response for repo on travis.com."""
    url = "{api_url}{repo_name}".format(api_url=TRAVIS_API_URL, repo_name="edx-cookiecutters")
    responses.add(responses.GET, url, json={"active_on_org": False, "migration_status": None}, status=200)
    return requests.get(url)


@responses.activate
def mock_migrated_repo_response():
    """Mock response for migrated repo."""
    url = "{api_url}{repo_name}".format(api_url=TRAVIS_API_URL, repo_name="ecommerce")
    responses.add(responses.GET, url, json={"active_on_org": False, "migration_status": "migrated"}, status=200)
    return requests.get(url)


@patch('repo_health.check_travis_integration.get_travis_api_response', return_value=mock_non_existent_repo_response())
def test_integration_non_existent_repo(_mock_get_response):
    travis_integration_handler = TravisIntegrationHandler("edx-platform")
    travis_integration_handler.handle()

    assert travis_integration_handler.active is False
    assert travis_integration_handler.active_on_org is False
    assert travis_integration_handler.active_on_com is False


@patch('repo_health.check_travis_integration.get_travis_api_response', return_value=mock_on_com_repo_response())
def test_integration_active_on_com_repo(_mock_get_response):
    travis_integration_handler = TravisIntegrationHandler("edx-cookiecutters")
    travis_integration_handler.handle()

    assert travis_integration_handler.active is True
    assert travis_integration_handler.active_on_org is False
    assert travis_integration_handler.active_on_com is True


@patch('repo_health.check_travis_integration.get_travis_api_response', return_value=mock_migrated_repo_response())
def test_integration_migrated_repo(_mock_get_response):
    travis_integration_handler = TravisIntegrationHandler("ecommerce")
    travis_integration_handler.handle()

    assert travis_integration_handler.active is True
    assert travis_integration_handler.active_on_org is False
    assert travis_integration_handler.active_on_com is True
