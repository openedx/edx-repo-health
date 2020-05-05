========================
Adding Additional Checks
========================

Steps to adding a check:
========================

 1. Define what information you are gathering
 2. Look inside repo_health directory and figure out if that info is related to any checks modules already implemented

    - if not, create a new python module(file) and put your checks in that
 3. write your checks. Each check function should be small and ideally gathers one piece of information

    - consider using fixtures for info that is shared between multiple checks
 4. Add docs explaining info gathered in this check

    - use "@add_key_to_metadata" decorator if your check only adds one key
    - use "@health_metadata" decorator if your check adds mroe than one key



Anatomy of a check:
===================

 1. Decorator to add info about check

    - use "@health_metadata" or "@add_key_to_metadata" decorators to add docs about the information you gather in this check
 2. function inputs: pytest fixtures

    - if you would like to add additional info to output yaml file, use the fixture "all_results"
        - all_results is a dictionary -> guide to adding info to it are below
 3. function doc string

    - if the function(check) is only adding one key to "all_results" dictionary, you
        can add info about it in the doc. The plugin will assume the doc string for function is the doc string for added key
    - if function(check) adds more than one key
        - use doc string to document the whole check and use "@health_metadata" decorator to add docs on individual keys
 4. function body

    - code that gathers the info you need and figures out what to add to "all_results" dict
    - this should be as small as possible
    - if there is any processing happening that might also be useful to another check, consider implementing it as a seperate fixture
    - for now, we've chosen not to add any asserts in the check functions
