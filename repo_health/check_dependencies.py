"""
 contains check that reads/parses dependencies of a repo
"""


from pytest_repo_health import health_metadata
from .utils import set_repo_dependencies


module_dict_key = "dependencies"


@health_metadata(
    [module_dict_key],
    {
        "count": "count of total dependencies",
        "pypi_all.count": "count of PyPI packages",
        "pypi_all.list": "list of PyPI packages with required versions of all files",
        "pypi.count": "count of PyPI packages only production files.",
        "pypi.list": "list of PyPI packages with required versions only production files.",
        "github.count": "count of GitHub packages",
        "github.list": "list of GitHub packages",
        "js.count": "count of javascript dependencies",
        "js.list": "list of javascript dependencies",
        "js.dev": "list of javascript development dependencies"
    },
)
def check_dependencies(repo_path, all_results):
    """
    Test to find the dependencies of the repo
    """
    all_results = set_repo_dependencies(
        all_results,
        repo_path,
        module_dict_key
    )
