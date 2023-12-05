"""
Contains fixture for the python config files
"""

import os
import re
import tempfile

import pytest
import requests

from repo_health import get_file_content

DJANGO_DEPS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/19-BzpcX3XvqlazHcLhn1ZifBMVNund15EwY3QQM390M/export?format=csv"
)


@pytest.fixture(scope="session")
def fixture_setup_py(repo_path):
    """Fixture containing the text content of setup.py"""
    full_path = os.path.join(repo_path, "setup.py")
    return get_file_content(full_path)


@pytest.fixture(scope="session")
def fixture_setup_cfg(repo_path):
    """Fixture containing the text content of setup.cfg"""
    full_path = os.path.join(repo_path, "setup.cfg")
    return get_file_content(full_path)


@pytest.fixture(scope="session")
def fixture_python_version(fixture_setup_py):
    """
    The list of python versions in setup.py classifiers
    """
    regex_pattern = r"Programming Language :: Python :: ([\d\.]+)"
    python_classifiers = re.findall(regex_pattern, fixture_setup_py, re.MULTILINE)
    return python_classifiers


@pytest.fixture(scope="session")  # pragma: no cover
def django_dependency_sheet_fixture():
    """
    Returns the path for csv file which contains django dependencies status.
    Also, makes a request for latest sheet & dumps response into the csv file if request was successful.
    """
    tmpdir = tempfile.mkdtemp()
    csv_filepath = os.path.join(tmpdir, "django_dependencies_sheet.csv")

    res = requests.get(DJANGO_DEPS_SHEET_URL)
    if res.status_code == 200:
        with open(csv_filepath, 'w', encoding="utf8") as fp:
            fp.write(res.text)

    return csv_filepath
