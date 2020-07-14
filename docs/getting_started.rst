Getting Started
===============

If you have not already done so, create or activate a `virtualenv`_. Unless otherwise stated, assume all terminal code
below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/


Install dependencies
--------------------
Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements


To use dashboard script:

.. code-block:: bash

    $ pip install -e .


Documentation
-------------

Read `check_function`_ to get an understanding of the implementation details behind check functions


To add new checks, read `add_checks`_.

To get an understanding of how the dashboard csv is made, read `dashboard`_.


.. _check_function: https://github.com/edx/edx-repo-health/blob/master/docs/check_function.rst
.. _add_checks: https://github.com/edx/edx-repo-health/blob/master/docs/how_tos/add_checks.rst
.. _dashboard: https://github.com/edx/edx-repo-health/blob/master/docs/csv_dashboard.rst