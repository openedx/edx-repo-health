"""
Checks to fetch repository ownership information from the Google Sheets speadsheet.
"""
import logging
import os

import gspread
import pytest
from pytest_repo_health import health_metadata

from .utils import github_org_repo

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "ownership"

GOOGLE_CREDENTIALS = "REPO_HEALTH_GOOGLE_CREDS_FILE"

REPO_HEALTH_SHEET_URL = "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL"

REPO_HEALTH_WORKSHEET = "REPO_HEALTH_REPOS_WORKSHEET_ID"


class KnownError(Exception):
    """
    Known exception cases where we won't need a stack trace.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def find_worksheet(google_creds_file, spreadsheet_url, worksheet_id):
    """
    Authenticate to Google and return the matching worksheet.
    """
    all_worksheets = gspread.service_account(filename=google_creds_file) \
                            .open_by_url(spreadsheet_url) \
                            .worksheets()
    matching = list(filter(lambda w: w.id == worksheet_id, all_worksheets))
    if not matching:
        raise KnownError(f"Cannot find a worksheet with ID {worksheet_id}")
    worksheet = matching[0]
    expected_headers = ["repo url", "owner.theme", "owner.squad", "owner.priority"]
    return worksheet.get_all_records(expected_headers=expected_headers)


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "theme": "Theme that owns the component",
        "squad": "Squad that owns the component",
        "priority": "How critical is the component to edX?",
        "description": "Description of the what the component is",
        "notes": "Notes maintained by the owner",
    },
)
def check_ownership(all_results, git_origin_url):
    """
    Get all the fields of interest from the tech ownership spreadsheet entry
    for the repository.
    """
    try:
        google_creds_file = os.environ[GOOGLE_CREDENTIALS]
        spreadsheet_url = os.environ[REPO_HEALTH_SHEET_URL]
        worksheet_id = int(os.environ[REPO_HEALTH_WORKSHEET])
    except KeyError:
        logger.error(
            "At least one of the following REPO_HEALTH_* environment variables is missing:\n %s \n %s \n %s",
            GOOGLE_CREDENTIALS, REPO_HEALTH_SHEET_URL, REPO_HEALTH_WORKSHEET
        )
        pytest.skip("At least one of the REPO_HEALTH_* environment variables is missing")

    org_name, repo_name = github_org_repo(git_origin_url)
    repo_url = f"https://github.com/{org_name}/{repo_name}"
    results = all_results[MODULE_DICT_KEY]
    records = find_worksheet(google_creds_file, spreadsheet_url, worksheet_id)
    for row in records:
        if row["repo url"] != repo_url:
            continue
        results["theme"] = row["owner.theme"]
        results["squad"] = row["owner.squad"]
        results["priority"] = row["owner.priority"]
