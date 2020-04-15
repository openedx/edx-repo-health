# the first argument for script is the location of edx-repo-health checks
repo_names=(
'edx-analytics-data-api'
'pytest-repo-health'
'edx-platform'
'warehouse-transforms'
'edx-val'
'edx-internal'
'course-discovery'
'terraform'
'edx-analytics-dashboard'
'edx-platform-private'
'sphinxcontrib-openapi'
'api-manager'
'RateXBlock'
'py-opt-cli'
'stylelint-config-edx'
'frontend-config-edx'
'asym-crypto-yaml'
'edx-user-state-client'
'edx-postman-config'
'journals-frontend'
)
touch tmp.txt
for t in ${repo_names[@]}; do
    git_url="git@github.com:edx/${t}.git"
    git clone $git_url
    pytest --repo-health --repo-health-path $1 --repo-path $t --output-path ${t}_repo_health.yaml --noconftest -v -c tmp.txt
    rm -rf $t
done