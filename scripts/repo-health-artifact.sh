#!/bin/bash
set -e -v

WORKSPACE=$PWD

# Generate sql file from the yaml files
cd "${WORKSPACE}/repo-health-data/individual_repo_data"
repo_health_dashboard --data-dir . --configuration "${WORKSPACE}/edx-repo-health/repo_health_dashboard/configuration.yaml" \
    --output-sqlite "${WORKSPACE}/repo-health-data/dashboards/dashboard"
