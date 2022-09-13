===============
Check Functions
===============

A check function is a Python function that checks some aspect of a repository.  It adds its results to a dictionary called "all_results." It is run by pytest using a customized plugin (`pytest-repo-health`_). This allows every check function to be independent and centrally coordinated, like test functions.


How results are structured
--------------------------

Check functions contribute results to a dictionary called all_results.  The structure of all_results is arbitrarily nested, but usually, it's two-level: the first level is based on the module containing the check function, and the second level is the name of the data result.

For example, in check_existence.py, the check function might write::

    all_results["exists"]["Makefile"] = True
    all_results["exists"]["tox.ini"] = False

Here, "exists" is the module key, and the second key is the name of the file being checked.  (In a real check function, the result value would be determined from the repo contents, rather than constants.)


Anatomy of a check
------------------

#. **Name**: Name your check function with a "check_" prefix, not "test_". The Python file should be named "check_*.py".

#. **Decorator to add metadata:** Use either "@health_metadata" or "@add_key_to_metadata" decorator.  These define the expected structure of the results, and add a descriptive string describing the result. Which you use depends on how many results you will write. See below for details.

#. **Function inputs:** The check function uses pytest fixtures to get the all_results results dictionary and the location of the repo to check.

#. **Function docstring:**  If using "@add_key_to_metadata", this doc string will be treated like the doc for the key.  Otherwise, write something here to help developers in the future.

#. **Function body:**  Use the repo_path pytest fixture to find the local directory containing the repo to check.  Make sure to add info into the "all_results" dict. Don't write asserts.

Metadata decorators:

* "@add_key_to_metadata" is used when your check function produces a single result.  The argument is a tuple, the keys to use in all_results. The function docstring is used as the description of the result::

    @add_key_to_metadata(("exists", "readme"))
    def check_readme(repo_path, all_results):
        """Does the repo have a README?"""
        all_results["exists"]["readme"] = os.path.exists(os.path.join(repo_path, "README"))

* "@health_metadata" is a more general decorator used when your check produces a number of results.  The first argument is a list of keys, the path down to the result leaves in all_results.  The second argument is a dictionary mapping leaf keys to their descriptions::

    @health_metadata(
        ["exists"],
        {
            "README": "Does the repo have a README?",
            "Makefile": "Does the repo have a Makefile?",
            "tox.ini": "Does the repo have a tox.ini?",
        },
    )
    def check_files(repo_path, all_results):
        for fname in ["README", "Makefile", "tox.ini"]:
            all_results["exists"][fname] = os.path.exists(os.path.join(repo_path, fname))


Available Fixtures
------------------

These are the two main fixtures. 

- "all_results" fixture: the dictionary to update with your check's results.

- "repo_path" fixture: a str, the path to the repo directory being checked.

The complete set of fixtures is available in the `pytest-repo-health/fixtures`__ directory.

__ https://github.com/openedx/pytest-repo-health/tree/master/pytest_repo_health/fixtures


Running checks
--------------

Installing this repo (with ``make requirements``) will install the pytest-repo-health tools.  See the `pytest-repo-health`_ repo for details on using pytest to run the checks.

.. _pytest-repo-health: https://github.com/openedx/pytest-repo-health
