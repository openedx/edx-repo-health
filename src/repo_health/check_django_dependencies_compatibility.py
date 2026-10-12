"""
 contains check that reads/parses dependencies of a repo
"""

import csv
import json
import logging
import os
import re
import tempfile
from pathlib import Path

import pytest
import requests
from packaging.version import InvalidVersion, parse
from pytest_repo_health import health_metadata

from repo_health import get_file_lines

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "django_packages"

GITHUB_URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).*#egg=(?P<package>[^\/]+).*"
PYPI_PACKAGE_PATTERN = r"(?P<package_name>[^\/]+)==(?P<version>[^\/]+)"
DJANGO_DEPS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1UKHpv0IGcsTyAB2DbpxluRJujjhRrhVd9-y-qdMIoqw/export?format=csv"
)

# Target Django version for the current upgrade campaign.
# Set TARGET_DJANGO_VERSION env var (e.g. "4.2" or "5.2") to track a different release.
TARGET_DJANGO_VERSION = os.environ.get("TARGET_DJANGO_VERSION", "4.2")
TARGET_DJANGO_COLUMN = f"Django {TARGET_DJANGO_VERSION}"
TARGET_DJANGO_KEY = f"django_{TARGET_DJANGO_VERSION.replace('.', '')}"


@pytest.fixture(name="django_deps_sheet", scope="session")  # pragma: no cover
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


class DjangoDependencyReader:
    """
    Django dependency reader class
    """

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.dependencies = {}

    def _is_python_repo(self) -> bool:
        return os.path.exists(os.path.join(self.repo_path, "requirements"))

    def _read_dependencies(self):
        """
        Method processing python requirements files
        """

        requirement_files = [str(file) for file
                             in Path(os.path.join(self.repo_path, "requirements")).rglob('*.txt')
                             if 'constraints' not in str(file)]

        for file_path in requirement_files:
            lines = get_file_lines(file_path)

            for line in lines:
                stripped_line = self.strip_requirement(line)
                if not stripped_line:
                    continue

                if 'git+http' in stripped_line:
                    name, version = self.extract_from_github_link(stripped_line)
                else:
                    name, version = self.extract_from_pypi_package(stripped_line)

                self.dependencies[name] = version

    @staticmethod
    def strip_requirement(line):
        """
        Finds if the requirement line is actually a requirement & not a reference to other files
        """
        if line and not re.search('^[#-]', line):
            return re.sub(r' +[;#].*', "", line).replace('-e ', "")

        return None

    @staticmethod
    def extract_from_github_link(github_dep) -> tuple:
        """
        Extracts the package name from Github URL
        """
        match = re.search(GITHUB_URL_PATTERN, github_dep)

        if match:
            return match.group("package"), ''

        return '', ''

    @staticmethod
    def extract_from_pypi_package(pypi_dependency) -> tuple:
        """
        Sanitizes the package name from any version constraint and extra spaces
        """
        pypi_dependency = "".join(pypi_dependency.split())
        match = re.match(PYPI_PACKAGE_PATTERN, pypi_dependency)

        if match:
            return match.group('package_name'), match.group('version')

        return '', ''

    def read(self) -> dict:
        """
        Entry method for reading data
        """
        if not self._is_python_repo():
            return {}
        self._read_dependencies()

        return self.dependencies


def get_upgraded_dependencies_count(repo_path, django_deps_sheet) -> tuple:
    """
    Entry point to read, parse and calculate django dependencies
    @param repo_path: path for repo which we are calculating django deps
    @param django_dependency_sheet: csv which contains latest status of django deps
    @return: count for all + upgraded django deps in repo
    """
    reader_instance = DjangoDependencyReader(repo_path)
    deps = reader_instance.read()
    django_deps = []
    deps_support_target = []
    upgraded_in_repo = []

    csv_path = django_deps_sheet
    with open(csv_path, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for line in csv_reader:
            package_name = line["Django Package Name"]
            if package_name in deps.keys():  # pylint: disable=consider-iterating-dictionary
                django_deps.append(package_name)

                sheet_version = line.get(TARGET_DJANGO_COLUMN, "")
                if sheet_version and sheet_version != '-':
                    deps_support_target.append(package_name)

                    try:
                        if parse(deps[package_name]) >= parse(sheet_version):
                            upgraded_in_repo.append(package_name)
                    except InvalidVersion:
                        logger.warning(
                            "Skipping version comparison for '%s': invalid version string "
                            "(repo version=%r, sheet version=%r)",
                            package_name, deps[package_name], sheet_version,
                        )

    django_deps = list(set(django_deps))
    deps_support_target = list(set(deps_support_target))
    upgraded_in_repo = list(set(upgraded_in_repo))

    return django_deps, deps_support_target, upgraded_in_repo


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "total": "Dependencies that depend on Django",
        TARGET_DJANGO_KEY: f"Dependencies that support Django {TARGET_DJANGO_VERSION}",
        "upgraded": f"Dependencies that are upgraded to support Django {TARGET_DJANGO_VERSION}",
    },
)
@pytest.mark.py_dependency_health
@pytest.mark.edx_health
def check_django_dependencies_status(repo_path, all_results, django_deps_sheet):
    """
    Test to find the django dependencies compatibility
    """
    django_deps, support_target_deps, upgraded_in_repo = get_upgraded_dependencies_count(
        repo_path, django_deps_sheet)

    all_results[MODULE_DICT_KEY] = {
        'total': {
            'count': len(django_deps),
            'list': json.dumps(django_deps),
        },
        TARGET_DJANGO_KEY: {
            'count': len(support_target_deps),
            'list': json.dumps(support_target_deps)
        },
        'upgraded': {
            'count': len(upgraded_in_repo),
            'list': json.dumps(upgraded_in_repo)
        }
    }
