#!/bin/bash

# Get Press JSON data from a specified URL
# Output format for Terraform external data source: {"data": "<escaped_json_string>"}

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username)"')"

# Get configuration from environment variables, use defaults as fallback
PRESS_SVN_URL=${PRESS_SVN_URL:-"http://10.153.3.214/comware-test-script/50.多环境移植/1/AIGC/INFO/"}
SVN_PASSWORD=${SVN_PASSWORD_INPUT:-${SVN_PASSWORD:-"Zpr758258%"}}
SVN_USERNAME=${SVN_USERNAME_INPUT:-${SVN_USERNAME:-"z11187"}}

svn_with_auth() {
    if [ -n "$SVN_USERNAME" ] && [ -n "$SVN_PASSWORD" ]; then
        svn "$@" --no-auth-cache --non-interactive --password "$SVN_PASSWORD" --username "$SVN_USERNAME"
    else
        svn "$@" --no-auth-cache --non-interactive
    fi
}

svn_s() {
    local cmd=$1
    shift

    # For some commands, we need the output and they don't support -q
    if [ "$cmd" = "cat" ] || [ "$cmd" = "diff" ] || [ "$cmd" = "info" ] || [ "$cmd" = "update" ]; then
        svn_with_auth "$cmd" "$@"
    else
        # For other commands, use quiet mode
        svn_with_auth "$cmd" "$@" -q
    fi
}

get_svn_folder_contents() {
    local url=$1
    contents=$(svn_with_auth ls "${url}")
    if [ $? -ne 0 ]; then
        echo "Error: Unable to fetch contents from ${url}" >&2
        exit 1
    fi
    echo "${contents}"
}

urldecode() {
  local url_encoded="${1//+/ }"
  printf '%b' "${url_encoded//%/\\x}"
}

# Build JSON structure using arrays to avoid subshell issues
declare -A json_data

# Build JSON string
json_output="{"
first_version=true

# Top-level: press_versions
press_versions=$(get_svn_folder_contents "${PRESS_SVN_URL}")

while IFS= read -r press_version; do
    [ -z "$press_version" ] && continue

    press_version_clean="${press_version%/}"

    if [ "$first_version" = true ]; then
        first_version=false
    else
        json_output+="," 
    fi

    json_output+="\"${press_version_clean}\": {"

    # Second-level: press_categories
    press_categories=$(get_svn_folder_contents "${PRESS_SVN_URL}${press_version}")
    first_category=true

    while IFS= read -r press_category; do
        [ -z "$press_category" ] && continue

        press_category_clean="${press_category%/}"

        if [ "$first_category" = true ]; then
            first_category=false
        else
            json_output+=", "
        fi

        json_output+="\"${press_category_clean}\": ["

        # Third-level: items under each category
        sub_folders=$(get_svn_folder_contents "${PRESS_SVN_URL}${press_version}${press_category}")
        first_sub=true

        while IFS= read -r sub_dir; do
            [ -z "$sub_dir" ] && continue

            sub_dir_clean="${sub_dir%/}"

            if [ "$first_sub" = true ]; then
                first_sub=false
            else
                json_output+=", "
            fi

            json_output+="\"${sub_dir_clean}\""
        done <<< "$sub_folders"

        json_output+="]"
    done <<< "$press_categories"

    json_output+="}"
done <<< "$press_versions"

json_output+="}"

# Output in Terraform external data source format
jq -n --arg data "$json_output" '{"data": $data}'

