"""
Checks to fetch repository ownership information from the Google Sheets speadsheet.
"""
import json
import logging
import os

import gspread
import pytest
import yaml
from pytest_repo_health import health_metadata

from .utils import github_org_repo

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "ownership"

GOOGLE_CREDENTIALS = "REPO_HEALTH_GOOGLE_CREDS_FILE"

REPO_HEALTH_SHEET_URL = "REPO_HEALTH_OWNERSHIP_SPREADSHEET_URL"

REPO_HEALTH_WORKSHEET = "REPO_HEALTH_REPOS_WORKSHEET_ID"

CATALOG_INFO_FILE = "catalog-info.yaml"


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


def find_worksheet_with_actions(google_creds_file, spreadsheet_url, worksheet_id):
    """
    Authenticate to Google and return the matching worksheet with GitHub Actions
    """
    # Access credentials from GitHub Actions as json
    all_worksheets = gspread.service_account_from_dict(json.loads(google_creds_file)) \
                            .open_by_url(spreadsheet_url) \
                            .worksheets()
    matching = list(filter(lambda w: w.id == worksheet_id, all_worksheets))
    if not matching:
        raise KnownError(f"Cannot find a worksheet with ID {worksheet_id}")
    worksheet = matching[0]
    expected_headers = ["repo url", "owner.theme", "owner.squad", "owner.priority"]
    return worksheet.get_all_records(expected_headers=expected_headers)


def _catalog_owner(repo_path):
    """Return owner metadata from catalog-info.yaml, if available."""
    if not repo_path:
        return None, None, None

    catalog_path = os.path.join(repo_path, CATALOG_INFO_FILE)
    if not os.path.exists(catalog_path):
        return None, None, None

    try:
        with open(catalog_path, encoding="utf-8") as stream:
            data = yaml.safe_load(stream) or {}
    except (OSError, yaml.YAMLError) as exc:
        logger.warning("Could not parse %s: %s", catalog_path, exc)
        return None, None, None

    if not isinstance(data, dict):
        return None, None, None

    spec = data.get("spec") or {}
    if not isinstance(spec, dict):
        return None, None, None

    owner = spec.get("owner")
    if not isinstance(owner, str) or not owner.strip():
        return None, None, None

    owner = owner.strip()
    owner_kind = "unknown"
    owner_name = owner
    if ":" in owner:
        owner_kind, owner_name = owner.split(":", 1)
        owner_kind = owner_kind.strip().lower() or "unknown"
        owner_name = owner_name.strip() or owner

    # Backstage entity refs may carry a namespace (e.g. "group:default/team-x").
    # Strip the "<namespace>/" prefix so owner_name is the bare team/user name.
    if "/" in owner_name:
        owner_name = owner_name.split("/", 1)[1].strip() or owner_name

    return owner, owner_kind, owner_name


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "owner": "Owner from catalog-info.yaml (spec.owner)",
        "owner_kind": "Owner kind from catalog-info.yaml (user/group)",
        "owner_name": "Owner name from catalog-info.yaml",
        "theme": "Theme that owns the component",
        "squad": "Squad that owns the component",
        "priority": "How critical is the component to edX?",
        "description": "Description of the what the component is",
        "notes": "Notes maintained by the owner",
    },
)
@pytest.mark.edx_health
def check_ownership(all_results, git_origin_url, repo_path=None):
    """
    Get all the fields of interest from the tech ownership spreadsheet entry
    for the repository.
    """
    results = all_results[MODULE_DICT_KEY]

    # catalog-info.yaml (OEP-55 spec.owner) is the primary, in-repo ownership
    # source. Always emit the keys (empty when absent) so the aggregated CSV
    # carries the column and coverage math has something to count.
    owner, owner_kind, owner_name = _catalog_owner(repo_path)
    results["owner"] = owner or ""
    results["owner_kind"] = owner_kind or ""
    results["owner_name"] = owner_name or ""

    # The Google Sheet (theme/squad/priority) is a secondary, org-specific
    # source (2U). Everything below is best-effort and must never crash the
    # check: a bad origin URL or misconfigured env falls back to catalog-info.
    try:
        org_name, repo_name = github_org_repo(git_origin_url)
    except (AssertionError, AttributeError, ValueError):
        logger.warning(
            "Could not parse org/repo from %r; using catalog-info.yaml only.",
            git_origin_url,
        )
        return
    repo_url = f"https://github.com/{org_name}/{repo_name}"

    try:
        google_creds_file = os.environ[GOOGLE_CREDENTIALS]
        spreadsheet_url = os.environ[REPO_HEALTH_SHEET_URL]
        worksheet_id_raw = os.environ[REPO_HEALTH_WORKSHEET]
    except KeyError:
        logger.warning(
            "Ownership spreadsheet env vars are not fully configured; using catalog-info.yaml only."
        )
        return

    try:
        worksheet_id = int(worksheet_id_raw)
    except ValueError:
        logger.warning(
            "%s is not an integer (%r); using catalog-info.yaml only.",
            REPO_HEALTH_WORKSHEET,
            worksheet_id_raw,
        )
        return

    if not google_creds_file.strip():
        logger.warning(
            "Environment variable %s is set but empty; using catalog-info.yaml only.",
            GOOGLE_CREDENTIALS,
        )
        return

    try:
        json.loads(google_creds_file)
        # Using Json dict values in case of GitHub Actions
        records = find_worksheet_with_actions(google_creds_file, spreadsheet_url, worksheet_id)
    except ValueError:
        # Using default string representation for Jenkins compatibility
        records = find_worksheet(google_creds_file, spreadsheet_url, worksheet_id)
    except KnownError as exc:
        logger.warning("Ownership worksheet not available: %s", exc.message)
        return

    for row in records:
        if row["repo url"] != repo_url:
            continue
        results["theme"] = row["owner.theme"]
        results["squad"] = row["owner.squad"]
        results["priority"] = row["owner.priority"]
        break
