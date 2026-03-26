#!/bin/bash

# Get SVN directory map (2-level: version -> branch types) from a specified base URL
# Output format for Terraform external data source: {"data": "<escaped_json_string>"}
#
# Input (stdin JSON): { "base_url": "...", "svn_username": "...", "svn_password": "..." }
# Output: {"data": "{\"V9R1\": [\"trunk\", \"branches_ai\", ...], ...}"}

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "BASE_URL=\(.base_url) SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username)"')"

SVN_PASSWORD=${SVN_PASSWORD_INPUT:-${SVN_PASSWORD:-""}}
SVN_USERNAME=${SVN_USERNAME_INPUT:-${SVN_USERNAME:-""}}

svn_with_auth() {
	if [ -n "$SVN_USERNAME" ] && [ -n "$SVN_PASSWORD" ]; then
		svn "$@" --no-auth-cache --non-interactive --password "$SVN_PASSWORD" --username "$SVN_USERNAME" 2>/dev/null
	else
		svn "$@" --no-auth-cache --non-interactive 2>/dev/null
	fi
}

get_svn_dirs() {
	local url=$1
	local contents
	contents=$(svn_with_auth ls "${url}")
	if [ $? -ne 0 ]; then
		echo "Warning: Unable to fetch contents from ${url}" >&2
		echo ""
		return 1
	fi
	# Filter only directories (entries ending with /) and strip trailing /
	echo "${contents}" | grep '/$' | sed 's/\/$//'
}

# Build JSON map: { version: [branch_types] }
svn_map='{}'

# Level 1: List versions under base URL
mapfile -t versions <<<"$(get_svn_dirs "${BASE_URL}")"

for version in "${versions[@]}"; do
	[ -z "$version" ] && continue

	# Level 2: List branch types under each version
	mapfile -t branches <<<"$(get_svn_dirs "${BASE_URL}${version}/")"
	branch_array='[]'

	for branch in "${branches[@]}"; do
		[ -z "$branch" ] && continue
		branch_array=$(printf '%s\n' "$branch_array" | jq --arg b "$branch" '. + [$b]')
	done

	svn_map=$(printf '%s\n' "$svn_map" | jq --arg ver "$version" --argjson branches "$branch_array" '. + {($ver): $branches}')
done

# Output in Terraform external data source format
jq -n --argjson data "$svn_map" '{"data": ($data | tostring)}'
