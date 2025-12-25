#!/bin/bash

# Get KE JSON data from a specified URL
# Output format for Terraform external data source: {"data": "<escaped_json_string>"}

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username)"')"

# Get configuration from environment variables, use defaults as fallback
KE_SVN_URL=${KE_SVN_URL:-"http://10.153.3.214/comware-test-script/50.多环境移植/1/AIGC/KE_ver2/"}
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

# Build JSON using jq to avoid mangling names (e.g., keep dots intact)
mapfile -t components <<< "$(get_svn_folder_contents "${KE_SVN_URL}/")"

ke_map='{}'

for ke_component in "${components[@]}"; do
  ke_component="${ke_component%/}"
  [ -z "$ke_component" ] && continue

  mapfile -t modules <<< "$(get_svn_folder_contents "${KE_SVN_URL}/${ke_component}/")"
  component_obj='{}'

  for ke_module in "${modules[@]}"; do
    ke_module="${ke_module%/}"
    [ -z "$ke_module" ] && continue

    mapfile -t tags <<< "$(get_svn_folder_contents "${KE_SVN_URL}/${ke_component}/${ke_module}/脚本示例")"
    cleaned_tags=()

    for ke_tag in "${tags[@]}"; do
      ke_tag="${ke_tag%/}"
      [ -z "$ke_tag" ] && continue
      cleaned_tags+=("$ke_tag")
    done

    tags_json=$(printf '%s\n' "${cleaned_tags[@]}" | jq -R . | jq -s .)
    component_obj=$(printf '%s\n' "$component_obj" | jq --arg module "$ke_module" --argjson tags "$tags_json" '. + {($module): $tags}')
  done

  ke_map=$(printf '%s\n' "$ke_map" | jq --arg component "$ke_component" --argjson modules "$component_obj" '. + {($component): $modules}')
done

# Output in Terraform external data source format
# The entire ke_map JSON is stored as a string value in the "data" key
jq -n --argjson data "$ke_map" '{"data": ($data | tostring)}'
