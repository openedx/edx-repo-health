"""
Utility Functions
"""
import functools
import operator
from datetime import datetime


GITHUB_DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"


def parse_build_duration_response(json_response):
    """
    This function is responsible for parsing Github GraphQL API response and calculating build duration
    """
    build_checks = list()
    first_started_at = None
    last_completed_at = None
    total_duration = ''

    latest_commit = functools.reduce(
        operator.getitem, ["node", "defaultBranchRef", "target", "history", "edges"], json_response)[0]

    for check_suite in functools.reduce(operator.getitem, ['node', 'checkSuites', 'edges'], latest_commit):

        all_check_runs = check_suite['node']['checkRuns']['edges']
        for check_run in all_check_runs:
            # If check is still in progress, skip it
            if not check_run['node']['completedAt']:
                continue

            name = check_run['node']['name']
            started_at = datetime.strptime(check_run['node']['startedAt'], GITHUB_DATETIME_FMT)
            completed_at = datetime.strptime(check_run['node']['completedAt'], GITHUB_DATETIME_FMT)

            if not first_started_at or started_at < first_started_at:
                first_started_at = started_at
            if not last_completed_at or completed_at > last_completed_at:
                last_completed_at = completed_at

            job_duration = completed_at - started_at
            minutes, remaining_seconds = divmod(job_duration.total_seconds(), 60)

            build_checks.append({
                'name': name,
                'duration': f'{int(minutes)} minutes {int(remaining_seconds)} seconds'
            })

    if build_checks:
        build_duration = last_completed_at - first_started_at
        minutes, remaining_seconds = divmod(build_duration.total_seconds(), 60)

        total_duration = f'{int(minutes)} minutes {int(remaining_seconds)} seconds'

    return total_duration, build_checks
