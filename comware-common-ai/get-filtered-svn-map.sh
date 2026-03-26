#!/bin/bash

# Filtered SVN directory map builder for Coder Dynamic Parameters.
# Queries only a curated set of versions/branches instead of scanning the full SVN tree.
# Output format: {"data": "<escaped_json_string>"} for Terraform external data source.
#
# Input (Terraform query JSON on stdin):
#   repo_type    - "platform" or "public"
#   svn_username - SVN username (optional, falls back to default)
#   svn_password - SVN password (optional, falls back to default)
#
# Output JSON structure (inside "data"):
# {
#   "V9R1": {
#     "trunk": ["FOLDER1", "FOLDER2", ...],
#     "branches_bugfix": {
#       "SUBDIR1": ["FOLDER1", "FOLDER2", ...],
#       "SUBDIR2": ["FOLDER1", "FOLDER2", ...],
#       ...
#     }
#   },
#   "V7R1_SPRINGB64": { ... },
#   "V7R1_SPRINGB75": { ... }
# }

set -euo pipefail

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "REPO_TYPE=\(.repo_type) SVN_USERNAME_INPUT=\(.svn_username) SVN_PASSWORD_INPUT=\(.svn_password)"')"

# Configuration
SVN_USERNAME="${SVN_USERNAME_INPUT:-z11187}"
SVN_PASSWORD="${SVN_PASSWORD_INPUT:-Zpr758258%}"

VERSIONS=("V9R1" "V7R1_SPRINGB64" "V7R1_SPRINGB75")
BRANCHES=("trunk" "branches_bugfix")
MAX_BUGFIX_SUBDIRS=20

case "${REPO_TYPE}" in
platform) SVN_BASE="http://10.153.120.80/cmwcode-open" ;;
public) SVN_BASE="http://10.153.120.104/cmwcode-public" ;;
*)
	echo "Error: repo_type must be 'platform' or 'public', got '${REPO_TYPE}'" >&2
	exit 1
	;;
esac

# SVN helper: run svn with auth, suppressing interactive prompts
svn_ls() {
	svn ls "$1" \
		--no-auth-cache \
		--non-interactive \
		--username "${SVN_USERNAME}" \
		--password "${SVN_PASSWORD}" \
		2>/dev/null
}

# List directories (entries ending with /) and strip trailing slash
list_dirs() {
	svn_ls "$1" | grep '/$' | sed 's|/$||'
}

# List all entries (files and dirs) and strip trailing slash
list_all() {
	svn_ls "$1" | sed 's|/$||'
}

# Build the JSON map
result_json='{}'

for version in "${VERSIONS[@]}"; do
	version_json='{}'

	for branch in "${BRANCHES[@]}"; do
		branch_url="${SVN_BASE}/${version}/${branch}"

		if [ "${branch}" = "trunk" ]; then
			# trunk: directly list folders at trunk level
			folders_raw=$(list_all "${branch_url}/" 2>/dev/null || true)
			if [ -n "${folders_raw}" ]; then
				folders_json=$(printf '%s\n' "${folders_raw}" | jq -R . | jq -s .)
			else
				folders_json='[]'
			fi
			version_json=$(printf '%s\n' "${version_json}" | jq \
				--arg branch "${branch}" \
				--argjson folders "${folders_json}" \
				'. + {($branch): $folders}')

		elif [ "${branch}" = "branches_bugfix" ]; then
			# branches_bugfix: list subdirectories, keep latest 20, then list folders in each
			subdirs_raw=$(list_dirs "${branch_url}/" 2>/dev/null || true)
			if [ -z "${subdirs_raw}" ]; then
				version_json=$(printf '%s\n' "${version_json}" | jq \
					--arg branch "${branch}" \
					'. + {($branch): {}}')
				continue
			fi

			# Sort subdirectories in reverse order (newest first) and take top N
			# SVN ls returns entries in alphabetical order; for bugfix branches
			# the names typically sort chronologically (e.g., TB202501071176)
			subdirs_latest=$(printf '%s\n' "${subdirs_raw}" | sort -r | head -n "${MAX_BUGFIX_SUBDIRS}")

			branch_json='{}'
			while IFS= read -r subdir; do
				[ -z "${subdir}" ] && continue
				subdir_url="${branch_url}/${subdir}"
				sub_folders_raw=$(list_all "${subdir_url}/" 2>/dev/null || true)
				if [ -n "${sub_folders_raw}" ]; then
					sub_folders_json=$(printf '%s\n' "${sub_folders_raw}" | jq -R . | jq -s .)
				else
					sub_folders_json='[]'
				fi
				branch_json=$(printf '%s\n' "${branch_json}" | jq \
					--arg subdir "${subdir}" \
					--argjson folders "${sub_folders_json}" \
					'. + {($subdir): $folders}')
			done <<<"${subdirs_latest}"

			version_json=$(printf '%s\n' "${version_json}" | jq \
				--arg branch "${branch}" \
				--argjson data "${branch_json}" \
				'. + {($branch): $data}')
		fi
	done

	result_json=$(printf '%s\n' "${result_json}" | jq \
		--arg version "${version}" \
		--argjson data "${version_json}" \
		'. + {($version): $data}')
done

# Output in Terraform external data source format
jq -n --argjson data "${result_json}" '{"data": ($data | tostring)}'
