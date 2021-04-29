"""
 contains check that reads/parses dependencies of a repo
"""
import copy
import json
import logging
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path

from pytest_repo_health import health_metadata

from repo_health import get_file_lines

logger = logging.getLogger(__name__)

module_dict_key = "dependencies"

default_output = {
    "pypi": {
        "count": 0,
        "list": ""
    },
    "github": {
        "count": 0,
        "list": ""
    },
    "js": {
        "count": 0,
        "list": "",
        "dev.List": ""
    },
    "js.dev": {
        "count": 0,
        "list": ""
    }
}


class DependencyReader(ABC):
    """
    class containing the read/parse logic for dependencies
    """

    def __init__(self, repo_path):
        self._repo_path = repo_path

    @abstractmethod
    def read(self) -> dict:
        """
        entry point method of the class
        """
        raise NotImplementedError


class JavascriptDependencyReader(DependencyReader):
    """
    Javascript dependency reader class
    """

    def __init__(self, repo_path):
        super().__init__(repo_path)
        self.js_dependencies = None
        self.js_dev_dependencies = None
        self.js_dependencies_count = 0
        self.js_dev_dependencies_count = 0

    def _is_js_repo(self) -> bool:
        return os.path.exists(os.path.join(self._repo_path, "package.json"))

    def _read_dependencies(self) -> dict:
        """
        method processing javascript dependencies file
        """
        package_json_content = open(os.path.join(self._repo_path, "package.json"), 'r').read()
        package_json_data = json.loads(package_json_content)

        self.js_dependencies = package_json_data.get('dependencies', {})
        self.js_dev_dependencies = package_json_data.get('devDependencies', {})
        self.js_dependencies_count = len(self.js_dependencies)
        self.js_dev_dependencies_count = len(self.js_dev_dependencies)

        return {
            "count": self.js_dependencies_count + self.js_dev_dependencies_count,
            "js": {
                "count": self.js_dependencies_count,
                "list": self.js_dependencies,
            },
            "js.dev": {
                "count": self.js_dev_dependencies_count,
                "list": self.js_dev_dependencies
            }
        }

    def read(self) -> dict:
        if not self._is_js_repo():
            return {}
        return self._read_dependencies()


class PythonDependencyReader(DependencyReader):
    """
    Python dependency reader class
    """

    def __init__(self, repo_path):
        super().__init__(repo_path)
        self.github_dependencies = None
        self.pypi_dependencies = None

    def _is_python_repo(self) -> bool:
        return os.path.exists(os.path.join(self._repo_path, "requirements"))

    def _read_dependencies(self) -> dict:
        """
        method processing python requirements files
        """
        pypi_packages = []
        github_packages = []
        files = [str(file) for file in Path(os.path.join(self._repo_path, "requirements")).rglob('*.txt')]

        # services have production.txt and base.txt but packages have only base.txt
        # so if both appeared only pick production
        requirement_files = [file for file in files if file.endswith("production.txt")]

        if not requirement_files:
            requirement_files = [file for file in files if file.endswith("base.txt")]

        if not requirement_files:
            logger.error("No production.txt or base.txt files found for this repo %s", self._repo_path)

        for file_path in requirement_files:
            lines = get_file_lines(file_path)
            stripped_lines = [re.sub(r' +#.*', "", line).replace('-e ', "")
                              for line in lines if line and not line.startswith("#")]
            github_packages.extend([line for line in stripped_lines if re.match(r'^git\+.*', line)])
            pypi_packages.extend([line for line in stripped_lines if line not in github_packages and "==" in line])

        self.github_dependencies = list(set(github_packages))
        self.pypi_dependencies = list(set(pypi_packages))

        return {
            "pypi": {
                "count": len(set(self.pypi_dependencies)),
                "list": self.pypi_dependencies,
            },
            "github": {
                "count": len(set(self.github_dependencies)),
                "list": list(set(github_packages)),
            },
            "count": len(set(self.pypi_dependencies)) + len(set(self.github_dependencies)),
        }

    def read(self) -> dict:
        if not self._is_python_repo():
            return {}
        return self._read_dependencies()


def get_dependencies(repo_path) -> dict:
    """
    entry point to read parse and read dependencies
    @param repo_path:
    @return: dependencies_output
    """
    dependencies_count = 0
    dependencies_output = copy.deepcopy(default_output)
    for reader in DependencyReader.__subclasses__():
        reader_instance = reader(repo_path)
        result = reader_instance.read()
        if not result:
            continue

        dependencies_count += result.get('count', 0)
        dependencies_output.update(result)
        dependencies_output.update({"count": dependencies_count})

    return dependencies_output


@health_metadata(
    [module_dict_key],
    {
        "dependencies": "all production dependencies"
    }
)
def check_dependencies(repo_path, all_results):
    """
    Test to find the dependencies of the repo
    """
    all_results[module_dict_key] = json.dumps(get_dependencies(repo_path))
