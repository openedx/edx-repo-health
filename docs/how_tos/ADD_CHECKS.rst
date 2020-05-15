========================
Adding Additional Checks
========================

This document explains how to add checks to edx-repo-health.

Steps to adding a check:
------------------------

1. Define what information you are gathering
2. Review existing checks for reuse or extension
3. Write your check(s).
4. Document you check(s).


Writing your check:
-------------------
Some guidelines:
- keep your check function body as small as possible
- as a standard, only add one key per check to all_results dict
- use pytest fixtures to implement lines of code used by multiple Checks
- often, multiple checks need info from same file, so we've implemented file read as a fixture


Documenting Checks:
-------------------

To make it easier to programmatically handle each check/info, we use Decorators to add docs on each key defined by your checks.
    - the decorators are imported from pytest-repo-health
    - if your check adds more than one key to "all_results dictionary"
        - use "@health_metadata" decorator
    - if the function(check) is only adding one key to "all_results" dictionary
        - write your documentation on the key in check doc string
        - declare the key using "@add_key_to_metadata" decorator


Anatomy of a check
------------------

 1. Decorator to add info about check
    - use either "@health_metadata" or "@add_key_to_metadata" decorator
 2. function inputs: pytest fixtures
    - if check is gathering info, it should use "all_results" fixture
 3. function doc string
    - if using "@add_key_to_metadata", this doc string will be treated like the doc for the key
    - otherwise, write something here to help developers in the future
 4. function body
    - code to gather information
    - make sure to add info into "all_results" dict

"all_results" fixture
---------------------

- pytest-repo-health plugin uses a default dict called session_data_holder_dict to hold information for a check run. 
    -  you can add to session_data_holder_dict by using the all_results fixture.

structure of all_results
~~~~~~~~~~~~~~~~~~~~~~~~

- all_results is a dict
- the info in dict is structured by check modules: all_results["module_key"]["info"]...
- the existing modules define a module_dict_key at top of file
    - all_results[module_dict_key] = { dict with all the info in this module}


Available Fixtures:
--------------------

- "all_results" fixture
    - pytest-repo-health plugin uses a default dict called session_data_holder_dict to hold information for a check run. 
        -  you can add to session_data_holder_dict by using the all_results fixture.

- "repo_path" fixture
    - the path to rootdir of the directory on which the checks are being run

Example
-------

In the example below, the decorator add_key_to_metadata assumes the doc string is the info about the key "upgrade"::

    @add_key_to_metadata((module_dict_key, "upgrade"))
    def check_has_upgrade(makefile, all_results):
        """
        upgrade: makefile target that upgrades our dependencies to newer released versions
        """
        code ...
        all_results[module_dict_key]["upgrade"]=True
