#!/bin/bash

# Get a single-level SVN directory listing as a JSON array
# Output format for Terraform external data source: {"data": "[\"dir1\", \"dir2\", ...]"}
#
# Input (stdin JSON): { "url": "...", "svn_username": "...", "svn_password": "..." }
# Output: {"data": "[\"dir1\", \"dir2\", ...]"}
# On error: {"data": "[]"}

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "URL=\(.url) SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username)"')"

SVN_PASSWORD=${SVN_PASSWORD_INPUT:-${SVN_PASSWORD:-""}}
SVN_USERNAME=${SVN_USERNAME_INPUT:-${SVN_USERNAME:-""}}

svn_with_auth() {
	if [ -n "$SVN_USERNAME" ] && [ -n "$SVN_PASSWORD" ]; then
		svn "$@" --no-auth-cache --non-interactive --password "$SVN_PASSWORD" --username "$SVN_USERNAME" 2>/dev/null
	else
		svn "$@" --no-auth-cache --non-interactive 2>/dev/null
	fi
}

# Fetch directory listing
contents=$(svn_with_auth ls "${URL}")
if [ $? -ne 0 ]; then
	# Return empty array on error
	echo '{"data": "[]"}'
	exit 0
fi

# Filter only directories, strip trailing /, build JSON array
dir_list=$(echo "${contents}" | grep '/$' | sed 's/\/$//' | grep -v '^$' | jq -R . | jq -s .)

# If no directories found, return empty array
if [ -z "$dir_list" ] || [ "$dir_list" = "null" ]; then
	dir_list='[]'
fi

# Output in Terraform external data source format
jq -n --argjson data "$dir_list" '{"data": ($data | tostring)}'
