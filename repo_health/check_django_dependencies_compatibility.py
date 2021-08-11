"""
 contains check that reads/parses dependencies of a repo
"""
import csv
import logging
import os
import re
from pathlib import Path

from pytest_repo_health import health_metadata

from repo_health_dashboard.utils.utils import get_edx_ida_list, get_django_dependency_sheet
from repo_health import get_file_lines

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "django_related_dependencies"
URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).*#egg=(?P<package>[^\/]+).*"


class DjangoDependencyReader:
    """
    Django dependency reader class
    """

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.dependencies = None

    def _is_python_repo(self) -> bool:
        return os.path.exists(os.path.join(self.repo_path, "requirements"))

    def _read_dependencies(self):
        """
        Method processing python requirements files
        """
        dependencies = []

        requirement_files = [str(file) for file in Path(os.path.join(self.repo_path, "requirements")).rglob('*.in')]

        for file_path in requirement_files:
            lines = get_file_lines(file_path)
            stripped_lines = [re.sub(r' +#.*', "", line).replace('-e ', "") for line in lines if line
                              and not any(line.startswith(start) for start in ['#', '-c', '-r'])]
            github_deps = [self.clean(self.extract(line)) for line in stripped_lines if 'git+http' in line]
            pypi_deps = [self.clean(line.strip()) for line in stripped_lines if line not in github_deps]

            dependencies.extend(github_deps+pypi_deps)

        self.dependencies = dependencies

    @staticmethod
    def extract(github_dep):
        """
        Extracts the package name from Github URL
        """
        match = re.search(URL_PATTERN, github_dep)

        return match.group("package") if match else ''

    @staticmethod
    def clean(pypi_dependency):
        """
        Sanitizes the package name from any version constraint and extra spaces
        """
        splitter = [symbol for symbol in [' ', '>', '<', '=='] if symbol in pypi_dependency]
        if splitter:
            return pypi_dependency.split(splitter[0])[0].strip()

        return pypi_dependency

    def read(self) -> dict:
        """
        Entry method for reading data
        """
        if not self._is_python_repo():
            return {}
        self._read_dependencies()

        return self.dependencies


def get_upgraded_dependencies_count(repo_path) -> tuple:
    """
    entry point to read parse and read dependencies
    @param repo_path:
    @return: dependencies_output
    """

    reader_instance = DjangoDependencyReader(repo_path)
    deps = reader_instance.read()
    total_django_deps = 0
    total_django32_deps = 0

    csv_path = get_django_dependency_sheet()
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

        for line in csv_reader:
            if line[1] in deps:
                total_django_deps += 1
                if line[6] and line[6] != '-':
                    total_django32_deps += 1

    return total_django_deps, total_django32_deps


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "total_count": "Count for total dependencies that depend on django",
        "support_django_32": "Count for total dependencies that support django 3.2",
    },
)
def check_django_dependencies_status(repo_path, all_results):
    """
    Test to find the django dependencies compatibility
    """
    repo_name = repo_path.split('/')[-1]
    if repo_name in get_edx_ida_list():
        total_django_deps, total_django32_deps = get_upgraded_dependencies_count(repo_path)
        upgrade_status = f"{total_django32_deps}/{total_django_deps} Upgraded"
        all_results[MODULE_DICT_KEY] = {
            'total_count': total_django_deps,
            'support_django_32': total_django32_deps,
            'status': upgrade_status
        }
