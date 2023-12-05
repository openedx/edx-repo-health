#!/bin/bash
set -e -v

# Click requires this to work cause it interfaces weirdly with python 3 ASCII default
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

WORKSPACE=$PWD

# If the REPORT_DATE variable is set and not an empty string parse the date to standardize it.
if [[ -n $REPORT_DATE ]]; then 
    REPORT_DATE=$(date '+%Y-%m-%d' -d "$REPORT_DATE")
fi

###############################################################
# Get list of dependencies repos from the dependencies_urls.csv
###############################################################

cd "$WORKSPACE"
touch "repositories.txt"
# Extract source column (assuming CSV is comma-separated)
source_column=$(tail -n +3 "${WORKSPACE}/dashboards/dependencies_urls.csv" | cut -d ',' -f 2)

# Filter out non-HTTP and non-HTTPS URLs using grep
filtered_urls=$(echo "$source_column" | grep -E '^(http|https)://')

# Save the filtered URLs to repo_urls.txt
echo "$filtered_urls" > "repositories.txt"

#########################################
# Run dependencies checks on repositories
#########################################

# Install checks and dashboarding script, this should also install pytest-repo-health
pip-sync -q edx-repo-health/requirements/base.txt
pip install -q -e edx-repo-health

# data destination folder setup

METADATA_FILE_DIST="docs/checks_metadata.yaml"

failed_repos=()

OUTPUT_FILE_POSTFIX="_dependency_health.yaml"

# Git clone each dependency repo and run checks on it
input="repositories.txt"
while IFS= read -r line; do
    cd "$WORKSPACE"
    if [[ "${line}" =~ ^(git@github\.com:|https://github\.com/)([a-zA-Z0-9_.-]+?)/([a-zA-Z0-9_.-]+?)\.git$ ]]; then
        ORG_NAME="${BASH_REMATCH[2]}"
        REPO_NAME="${BASH_REMATCH[3]}"
        FULL_NAME="${ORG_NAME}/${REPO_NAME}"
    else
        echo "Skipping <${line}>: Could not recognize as a GitHub URL in order to extract org and repo name."
        continue
    fi

    if [[ "${REPO_NAME}" = "edx-repo-health" ]]; then
        echo "Skipping <${line}>: edx-repo-health"
        continue
    fi

    if [[ -n "${ONLY_CHECK_THIS_REPOSITORY}" && "${FULL_NAME}" != "${ONLY_CHECK_THIS_REPOSITORY}" ]]; then
        echo "Skipping <${line}>: ONLY_CHECK_THIS_REPOSITORY was set, and does not match"
        continue
    fi

    echo "Processing repo: ${FULL_NAME}"

    rm -rf target-repo
    if ! git clone -- "${line/https:\/\//https:\/\/$GITHUB_TOKEN@}" target-repo; then
        failed_repos+=("$FULL_NAME")
        continue
    fi

    echo "Cloned repo: ${FULL_NAME}"
    cd target-repo
    echo "Stepping into target-repo"
    # If the REPORT_DATE variable is set and not an empty string.
    if [[ -n $REPORT_DATE ]]; then
        # If a specific date is given for report
        FIRST_COMMIT=$(git log --reverse --format="format:%ci" | sed -n 1p)
        if [[ $REPORT_DATE > ${FIRST_COMMIT:0:10} ]]; then
            git checkout "$(git rev-list -n 1 --before="${REPORT_DATE} 00:00" master)"
        else
            echo "${REPO_NAME} doesn't have any commits prior to ${REPORT_DATE}"
            failed_repos+=("$FULL_NAME")
            continue
        fi
    fi

    cd "$WORKSPACE"
    DEPENDENCIES_DATA_DIR="dependencies_health_data"
    # make sure destination folder exists
    mkdir -p "$DEPENDENCIES_DATA_DIR"

    OUTPUT_FILE_NAME="${REPO_NAME}${OUTPUT_FILE_POSTFIX}"

    DEPENDENCIES_HEALTH_COMMAND() {
        pytest --dependencies-health \
            --repo-health-path "edx-repo-health/dependencies_health" \
            --repo-path "target-repo" \
            --repo-health-metadata "${METADATA_FILE_DIST}" \
            --output-path "${DEPENDENCIES_DATA_DIR}/${OUTPUT_FILE_NAME}" \
            -o log_cli=true --exitfirst --noconftest -v -c /dev/null
    }
    
    if DEPENDENCIES_HEALTH_COMMAND; then
        true
    elif DEPENDENCIES_HEALTH_COMMAND; then
        # rerun the same command if it fails once
        true
    else
        failed_repos+=("$FULL_NAME")
        continue
    fi

done < "$input"

##############################
# Recalculate aggregated data.
##############################

# Go into data repo, recalculate aggregate data, and push a PR
IFS=,
failed_repo_names=$(echo "${failed_repos[*]}")

echo "Pushing data"
cd "${WORKSPACE}/dependencies_health_data"
repo_health_dashboard --data-dir . --configuration "${WORKSPACE}/edx-repo-health/repo_health_dashboard/dependencies_configuration.yaml" \
    --output-csv "${WORKSPACE}/dashboards/dependencies_dashboard" --dashboard-name "dependencies_health"

cd "${WORKSPACE}"
# Only commit the data if running with master and no REPORT_DATE is set.
if [[ ${EDX_REPO_HEALTH_BRANCH} == 'master' && -z ${REPORT_DATE} ]]; then
    ###########################################
    # Commit files and push to repo-health-data
    ###########################################
    echo "Commit new files and push to master..."

    commit_message="chore: Update repo health data files"

    cd "${WORKSPACE}"

    if [[ ${#failed_repos[@]} -ne 0 ]]; then
        commit_message+="\nFollowing repos failed repo health checks\n ${failed_repo_names}"

        for full_name in "${failed_repos[@]}"; do
            OUTPUT_FILE_NAME="${full_name}${OUTPUT_FILE_POSTFIX}"
            echo "reverting repo health data for ${OUTPUT_FILE_NAME}"
            git checkout -- "${WORKSPACE}/dependencies_health_data/${OUTPUT_FILE_NAME}"
        done
    fi

    git checkout master
    if git diff-index --quiet HEAD; then
        # No changes found in the working directory
        echo "No changes to commit"
    else
        # Changes found in the working directory
        git add dashboards
        git add dependencies_health_data
        git config --global user.name "Repo Health Bot"
        git config --global user.email "${GITHUB_USER_EMAIL}"
        git commit -m "${commit_message}"
        git push origin master
    fi
fi

if [[ ${#failed_repos[@]} -ne 0 ]]; then
    echo
    echo
    echo "TLDR Runbook(More detailed runbook: https://openedx.atlassian.net/wiki/spaces/AT/pages/3229057351/Repo+Health+Runbook ):"
    echo "  To resolve, search the console output for 'ERRORS' (without the quotes), or search for any"
    echo "  of the failed repo names listed below."
    echo "The following repositories failed while executing pytest dependencies-health scripts causing the job to fail:"
    echo
    echo "    ${failed_repos[*]}"
    echo
    echo
    exit 1
fi
