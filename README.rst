==================
edx-repo-health
==================


edx-repo-health contains static checks on repo structures.

The checks are meant to work in conjunction with `pytest-repo-health`_ plugin.

- The checks gather information about a given repository.
- Each check is meant to be minimum and only check for simple specific things. This is to make it easier to debug changes.
- No asserts should be placed inside of the checks.
- All necessary data about compliance and deviations should be placed in all_results dictionary (implemented through pytest fixture.)

Design
------

``edx-repo-health`` is part of a set of tools that together collect results of checks against multiple repositories. Then, taking the individual results as input, it can output the data in different formats including aggregated views of the data.

The `org-repo-health-report`_ jenkins job collects a list of all repos in the edx org and runs the ``repo_health`` tests defined in this repo against them.  The jenkins job first produces a yaml file per repository with the results of all run checks.  The output YAML is stored in the `repo-health-data`_ repository.

Next the jenkins job uses the `repo_health_dashboard`_ script along with the stored YAML files as input to produce CSV reports from the data.  The latest CSV reports are also stored in the `repo-health-data`_ repository. The tooling in the `repo_health_dashboard`_ module is what allows us to generate custom outputs for different use-cases where we need different data.

Some example use cases are:

#. Tech dashboard - What's wrong with my repo(s)?
#. Tech ownership - What do I own?
#. Tech ownership - Who owns this and how do I contact them?
#. Debt Management - Which repos are using version X of library Y?

Along with the output data from the jenkins job, the `repo-health-data`_ repo currently contains scripts that will publish the data from CSVs into specific google sheets. The long term vision is that `repo_health_data`_ will manage publishing to whatever UI we want to have on top of the data to make it easier to consume.

.. _org-repo-health-report: https://github.com/edx/jenkins-job-dsl-internal/blob/master/jobs/tools-edx-jenkins.edx.org/createRepoHealthJobs.groovy
.. _repo_health_dashboard: https://github.com/edx/edx-repo-health/blob/master/repo_health_dashboard/repo_health_dashboard.py
.. _repo-health-data: https://github.com/edx/repo-health-data


Adding Checks
-------------
For more info on adding new checks, please See `how_tos`_.

Checks Enchancement path
------------------------
- Documenting standard reqs/checks in each check better
- create tests for the checks and make sure they behave correctly to diff dir/file structure.


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

The code in this repository is licensed under the Apache Software License 2.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.


Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.


Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help
.. _pytest-repo-health: https://github.com/edx/pytest-repo-health
.. _how_tos: https://github.com/edx/edx-repo-health/blob/msingh/docs/docs/how_tos/ADD_CHECKS.rst
.. _`file an issue`: https://github.com/edx/edx-repo-health/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
