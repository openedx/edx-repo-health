==================
edx-repo-health
==================

edx-repo-health is a set of checks of the health of repositories.  They are written similar to pytest tests, and run in pytest using a customized pytest plugin (`pytest-repo-health`_).

- Each check gathers information about a given repository.
- Each check is meant to be minimal and only check for simple specific things. This is to make it easier to debug changes.
- Unlike test functions, checks should not use asserts.
- Each check writes its result to a dictionary.
- The completed dictionary is written as a YAML file when all the checks have
  been run.

Design
------

``edx-repo-health`` is part of a set of tools that together collect results of checks against multiple repositories. Then, taking the individual results as input, it can output the data in different formats including aggregated views of the data.

The `org-repo-health-report`_ Jenkins job collects a list of all repos in the edx org and runs the ``repo_health`` tests defined in this repo against them.  The Jenkins job first produces a yaml file per repository with the results of all run checks.  The output YAML is stored in the `repo-health-data`_ repository.

Next the Jenkins job uses the `repo_health_dashboard`_ script along with the stored YAML files as input to produce CSV reports from the data.  The latest CSV reports are also stored in the `repo-health-data`_ repository. The tooling in the `repo_health_dashboard`_ module is what allows us to generate custom outputs for different use-cases where we need different data.

Some example use cases are:

#. Tech dashboard - What's wrong with my repo(s)?
#. Tech ownership - What do I own?
#. Tech ownership - Who owns this and how do I contact them?
#. Debt Management - Which repos are using version X of library Y?

Along with the output data from the Jenkins job, the `repo-health-data`_ repo currently contains scripts that will publish the data from CSVs into specific Google sheets. The long term vision is that `repo_health_data`_ will manage publishing to whatever UI we want to have on top of the data to make it easier to consume.

.. _org-repo-health-report: https://github.com/edx/jenkins-job-dsl-internal/blob/master/jobs/tools-edx-jenkins.edx.org/createRepoHealthJobs.groovy
.. _repo_health_dashboard: https://github.com/edx/edx-repo-health/blob/master/repo_health_dashboard/repo_health_dashboard.py
.. _repo-health-data: https://github.com/edx/repo-health-data


Adding Checks
-------------

For details on adding new checks, please See `how_tos`_.

Future improvements
-------------------

- Documenting standard reqs/checks in each check better.

- Create tests for the checks and make sure they behave correctly for different dir/file structure.


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
.. _how_tos: https://github.com/edx/edx-repo-health/blob/master/docs/how_tos/add_checks.rst
.. _`file an issue`: https://github.com/edx/edx-repo-health/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
