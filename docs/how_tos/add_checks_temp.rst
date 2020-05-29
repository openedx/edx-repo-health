========================
Adding Additional Checks
========================

This document explains how to add checks to edx-repo-health.

To get a better understanding of a check function, read `check_function`_ doc

.. _check_function: https://github.com/edx/edx-repo-health/blob/master/docs/check_function.rst

Steps to adding a check:
------------------------

1. Define what information you are gathering
2. Review existing checks for reuse or extension
3. Write your check(s).
4. Document you check(s).


Writing your check:
-------------------
1. write code to get your info
2. Add info to all_results dictionary
3. Document the key(s) added to all_results dictionary

Some guidelines:

- keep your check function body as small as possible
- as a standard, only add one key per check to all_results dict
- use pytest fixtures to implement lines of code used by multiple checks
    - often, multiple checks need info from same file, so we've implemented file read as a fixture


How to Add Data to "all_results":
--------------------------------
- if you are creating a new module for your checks
 - define a module_dict_key at top of file
 - add info to "all_results" by::
    all_results[module_dict_key]["info_key"]=key
- if you are creating a new check in existing module::
    all_results[module_dict_key]["info_key"]=key


Documenting Checks:
-------------------
To make it easier to programmatically handle each check/info, we use Decorators to add docs on each key defined by your checks:

- the decorators are imported from pytest-repo-health
- if your check adds more than one key to "all_results dictionary"
 - use "@health_metadata" decorator
- if the function(check) is only adding one key to "all_results" dictionary
 - write your documentation on the key in check doc string
 - declare the key using "@add_key_to_metadata" decorator

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
