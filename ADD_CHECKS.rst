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
 - as a standard, only add one key to all_results dict
 - 


all_results fixture:
--------------------

Documenting Checks:
-------------------
 To make it easier to programmatically handle each check/info, we use Decorators to add docs on each key defined by your checks.
    - the decorators are imported from pytest-repo-health
    - if your check adss more than one key to "all_results dictionary"
        - use "@health_metadata" decorator
    - if the function(check) is only adding one key to "all_results" dictionary
        - write your documentation on the key in check doc string
        - declare the key using "@add_key_to_metadata" decorator

 3. Write your check(s)

    - Each check function should be small and ideally gathers one piece of information

    - consider using fixtures for info that is shared between multiple checks
 4. Add docs explaining info gathered in this check

    - use "@add_key_to_metadata" decorator if your check only adds one key
    - use "@health_metadata" decorator if your check adds more than one key
    - the decorators are imported from pytest-repo-health



Anatomy of a check:
-------------------

 1. Decorator to add info about check

    - use "@health_metadata" or "@add_key_to_metadata" decorators to add docs about the information you gather in this check
    - the decorators are imported from pytest-repo-health
 2. function inputs: pytest fixtures

    - if you would like to add additional info to output yaml file, use the fixture "all_results"
        - all_results is a dictionary -> guide to adding info to it are below
 3. function doc string

    - if the function(check) is only adding one key to "all_results" dictionary, you can add info about it in the doc. The plugin will assume the doc string for function is the doc string for added key
    - if function(check) adds more than one key
        - use doc string to document the whole check and use "@health_metadata" decorator to add docs on individual keys
 4. function body

    - code that gathers the info you need and figures out what to add to "all_results" dict
    - this should be as small as possible
    - if there is any processing happening that might also be useful to another check, consider implementing it as a seperate fixture
    - for now, we've chosen not to add any asserts in the check functions


Anatomy of a check:
-------------------

 1. Decorator to add info about check
    - see "Documenting Checks" section below
 2. Function inputs: use pytest fixtures
    - To add further information to yaml output, use all_results fixture
 3. Function doc string
    - see "Documenting Checks" section below
 4. Function body