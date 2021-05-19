# the first argument for script is the location of edx-repo-health checks
repo_names=(
'configuration'
)
mkdir temp_data
cd temp_data
for t in "${repo_names[@]}"; do
    git_url="git@github.com:edx/${t}.git"
    git clone $git_url
    pytest --repo-health --repo-health-path $1 --repo-path $t --output-path "${t}_repo_health.yaml" --noconftest -v -c /dev/null
done
