==============
Check Function
==============

A check function is a python test function with "check_" as a prefix rather than "test_". It is meant to be used by pytest-repo-health plugin to gather info about a repository of code. A check stores its results in "all_results" (more on this below). Documentation of a check is done using one of the decorators: ``@health_metadata`` or ``@add_key_to_metadata``



Anatomy of a check
------------------

1. Decorator to add info about check
 - use either "@health_metadata" or "@add_key_to_metadata" decorator
2. function inputs: pytest fixtures
 - if check is gathering info(which it should), it should use "all_results" fixture
3. function doc string
 - if using "@add_key_to_metadata", this doc string will be treated like the doc for the key
 - otherwise, write something here to help developers in the future
4. function body
 - code to gather information
 - make sure to add info into "all_results" dict

Available Fixtures:
--------------------

- "all_results" fixture
    - pytest-repo-health plugin uses a default dict called session_data_holder_dict to hold information for a check run. 
    - the all_results variable is essentially another named variable to data container session_data_holder_dict
    - Anything you do to all_results variable is done to session_data_holder_dict

- "repo_path" fixture
    - the path to rootdir of the directory on which the checks are being run

How data is structured in "all_results":
----------------------------------------

- all_results is a dict
- the info in dict is structured by check modules: all_results["module_key"]["info"]...
- the existing modules define a module_dict_key at top of file
    - all_results[module_dict_key] = { dict with all the info in this module}

Documenting all_results keys:
-----------------------------
Each key added to all_results should be well documented. Decorators are used to facilitate easy programmatic handling of info on each key.

- the decorators are imported from pytest-repo-health
- there are currently two available decorators
 - "@health_metadata" decorator
  - use if your check adds more than one key to "all_results"
 - "@add_key_to_metadata" decorator
  - if the function(check) is only adding one key to "all_results"
  - this decorator assumes the function doc string is the documentation on the key
