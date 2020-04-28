==================
edx-repo-health
==================


edx-repo-health contains static checks on repo structures.
The checks are meant to work in conjunction with `pytest-repo-health`_ plugin.

The checks see if a given repository follows minimum standards.
Each check is meant to be minimum and only check for simple specific things. This is to make it easier to debug changes.
No asserts should be placed inside of the checks.
All necessary data about compliance and deviations should be placed in all_results dictionary.
(implemented though pytest fixture)

Check `pytest-repo-health`_ for more info on check design.


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
.. _`file an issue`: https://github.com/edx/edx-repo-health/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
