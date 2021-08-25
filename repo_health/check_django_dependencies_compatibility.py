"""
 contains check that reads/parses dependencies of a repo
"""
import csv
import json
import logging
import os
import re
from pathlib import Path

from pytest_repo_health import health_metadata

from repo_health_dashboard.utils.utils import get_django_dependency_sheet
from repo_health import get_file_lines, GITHUB_URL_PATTERN

logger = logging.getLogger(__name__)

MODULE_DICT_KEY = "django_related_dependencies"


class DjangoDependencyReader:
    """
    Django dependency reader class
    """

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.dependencies = set()

    def _is_python_repo(self) -> bool:
        return os.path.exists(os.path.join(self.repo_path, "requirements"))

    def _read_dependencies(self):
        """
        Method processing python requirements files
        """
        dependencies = []

        requirement_files = [str(file) for file in Path(os.path.join(self.repo_path, "requirements")).rglob('*.txt')]

        for file_path in requirement_files:
            lines = get_file_lines(file_path)
            stripped_lines = [re.sub(r' +#.*', "", line).replace('-e ', "") for line in lines if line
                              and not any(line.startswith(start) for start in ['#', '-c', '-r'])]
            github_deps = [self.clean(self.extract(line)) for line in stripped_lines if 'git+http' in line]
            pypi_deps = [self.clean(line.strip()) for line in stripped_lines if line not in github_deps]

            dependencies.extend(github_deps+pypi_deps)

        self.dependencies = set(dependencies)

    @staticmethod
    def extract(github_dep):
        """
        Extracts the package name from Github URL
        """
        match = re.search(GITHUB_URL_PATTERN, github_dep)

        return match.group("package") if match else ''

    @staticmethod
    def clean(pypi_dependency):
        """
        Sanitizes the package name from any version constraint and extra spaces
        """
        pypi_dependency = "".join(pypi_dependency.split())
        splitter = [symbol for symbol in ['>', '<', '=='] if symbol in pypi_dependency]
        if splitter:
            return pypi_dependency.split(splitter[0], maxsplit=1)[0]

        return pypi_dependency

    def read(self) -> set:
        """
        Entry method for reading data
        """
        if not self._is_python_repo():
            return set()
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
    django_deps = []
    deps_support_django32 = []

    csv_path = get_django_dependency_sheet()
    with open(csv_path, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for line in csv_reader:
            if line["Django Package Name"] in deps:
                django_deps.append(line["Django Package Name"])
                if line["Django 3.2"] and line["Django 3.2"] != '-':
                    deps_support_django32.append(line["Django Package Name"])

    django_deps = list(set(django_deps))
    deps_support_django32 = list(set(deps_support_django32))

    return django_deps, deps_support_django32


@health_metadata(
    [MODULE_DICT_KEY],
    {
        "total_dependencies": "Dependencies that depend on Django",
        "support_django_32": "Dependencies that support Django 3.2",
    },
)
def check_django_dependencies_status(repo_path, all_results):
    """
    Test to find the django dependencies compatibility
    """
    django_deps, support_django32_deps = get_upgraded_dependencies_count(repo_path)
    all_results[MODULE_DICT_KEY] = {
        'total_dependencies': {
            'count': len(django_deps),
            'list': json.dumps(django_deps),
        },
        'support_django_32': {
            'count': len(support_django32_deps),
            'list': json.dumps(support_django32_deps)
        }
    }
