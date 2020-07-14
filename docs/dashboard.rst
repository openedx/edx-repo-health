=========
Dashboard
=========

The `repo_health_dashboard`_ script is meant to aggregate data from runs of `pytest-repo-health`_ on multiple 
repos. It aggregates the data from yaml outputs, flattens it, and outputs it in csv form.


.. _repo_health_dashboard: https://github.com/edx/edx-repo-health/blob/master/repo_health_dashboard/repo_health_dashboard.py
.. _pytest-repo-health: https://github.com/edx/pytest-repo-health

How to use
----------

.. code-block:: bash

    $ make requirements
    $ pip install -e .
    $ repo_health_dashboard --data-dir "path_to_data" --configuration "configuration.yaml" --output-csv "path_to_output_dir" --data-life-time 10

configuration
~~~~~~~~~~~~~

The contents of output csv can be configured using a yaml file.

Options:
    - output multiple csv files
    - dictate order of check info(order the column header)
    - alias column names
    - output only subset of data

see example: `configuration.yaml`_

.. _configuration.yaml: https://github.com/edx/edx-repo-health/blob/master/repo_health_dashboard/configuration.yaml

