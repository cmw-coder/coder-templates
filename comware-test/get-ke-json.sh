#!/bin/bash

# Get KE JSON data from a specified URL
# Output format for Terraform external data source: {"data": "<escaped_json_string>"}

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "KE_SVN_URL_INPUT=\(.ke_svn_url) SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username)"')"

# Get configuration from environment variables, use defaults as fallback
KE_SVN_URL=${KE_SVN_URL_INPUT:-${KE_SVN_URL:-"http://10.153.3.214/comware-test-script/50.多环境移植/1/AIGC/KE/"}}
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

# Get all components
components=$(get_svn_folder_contents "${KE_SVN_URL}脚本样例KE/")

# Build JSON string (store in variable for escaping)
json_output="{"
first_component=true

while IFS= read -r ke_component; do
  [ -z "$ke_component" ] && continue
  
  # Remove trailing slash if present
  ke_component_clean="${ke_component%/}"
  
  # Add comma before component if not first
  if [ "$first_component" = true ]; then
    first_component=false
  else
    json_output+=","
  fi
  
  json_output+="\"${ke_component_clean}\": {"
  
  # Get all modules for this component
  modules=$(get_svn_folder_contents "${KE_SVN_URL}脚本样例KE/${ke_component}")
  
  first_module=true
  
  while IFS= read -r ke_module; do
    [ -z "$ke_module" ] && continue
    
    # Remove trailing slash if present
    ke_module_clean="${ke_module%/}"
    
    # Add comma before module if not first
    if [ "$first_module" = true ]; then
      first_module=false
    else
      json_output+=","
    fi
    
    json_output+="\"${ke_module_clean}\": ["
    
    # Get all tags for this module
    tags=$(get_svn_folder_contents "${KE_SVN_URL}脚本样例KE/${ke_component}${ke_module}")
    
    first_tag=true
    
    while IFS= read -r ke_tag; do
      [ -z "$ke_tag" ] && continue
      
      # Remove trailing slash if present
      ke_tag_clean="${ke_tag%/}"
      
      # Add comma before tag if not first
      if [ "$first_tag" = true ]; then
        first_tag=false
      else
        json_output+=", "
      fi
      
      json_output+="\"${ke_tag_clean}\""
    done <<< "$tags"
    
    json_output+="]"
  done <<< "$modules"
  
  json_output+="}"
done <<< "$components"

json_output+="}"

# Output in Terraform external data source format
# The entire ke_map JSON is stored as a string value in the "data" key
jq -n --arg data "$json_output" '{"data": $data}'
