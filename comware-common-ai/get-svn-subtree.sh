#!/bin/bash

# Explore ALL branches under a version directory, detect depth for each branch,
# and collect directory entries at each intermediate level.
#
# This script is designed to be called UNCONDITIONALLY (no count guard) so that
# the Coder UI can dynamically cascade subdirectory selections by looking up
# the pre-computed map with live parameter values.
#
# Input (stdin JSON from Terraform external data source):
#   {
#     "base_url": "http://.../cmwcode-open/V9R1/",
#     "svn_username": "...",
#     "svn_password": "...",
#     "code_level_markers": "ACCESS,DEV,IP,NETFWD"
#   }
#
# Output (Terraform external data source format):
#   {"data": "{\"trunk\": {\"depth\": 0}, \"branches_bugfix\": {\"depth\": 2, \"level_0\": [...], \"level_1__TAG_A\": [...]}, ...}"}
#
# Depth detection heuristic:
#   At each level, check if `svn ls` results contain any code_level_markers.
#   If found -> this is the code level (stop, depth = levels traversed so far).
#   Otherwise -> intermediate level (continue deeper, up to MAX_DEPTH).

set -euo pipefail

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "BASE_URL=\(.base_url) SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username) CODE_LEVEL_MARKERS=\(.code_level_markers)"')"

SVN_PASSWORD=${SVN_PASSWORD_INPUT:-${SVN_PASSWORD:-""}}
SVN_USERNAME=${SVN_USERNAME_INPUT:-${SVN_USERNAME:-""}}

MAX_DEPTH=6
TMPDIR_BASE=$(mktemp -d)
trap 'rm -rf "$TMPDIR_BASE"' EXIT

svn_with_auth() {
	if [ -n "$SVN_USERNAME" ] && [ -n "$SVN_PASSWORD" ]; then
		svn "$@" --no-auth-cache --non-interactive --password "$SVN_PASSWORD" --username "$SVN_USERNAME" 2>/dev/null
	else
		svn "$@" --no-auth-cache --non-interactive 2>/dev/null
	fi
}

# Get directory entries from an SVN URL (directories only, trailing / stripped)
get_svn_dirs() {
	local url=$1
	local contents
	contents=$(svn_with_auth ls "${url}") || {
		echo "" # Return empty on failure
		return 0
	}
	echo "${contents}" | grep '/$' | sed 's/\/$//'
}

# Check if directory listing contains any code-level marker directories
is_code_level() {
	local entries="$1"
	local markers="$2"

	IFS=',' read -ra marker_array <<<"$markers"
	for marker in "${marker_array[@]}"; do
		marker=$(echo "$marker" | xargs)
		[ -z "$marker" ] && continue
		if echo "$entries" | grep -qx "$marker"; then
			return 0
		fi
	done
	return 1
}

# Convert a newline-separated list to a JSON array of strings
list_to_json_array() {
	local input="$1"
	if [ -z "$input" ]; then
		echo "[]"
		return
	fi
	printf '%s\n' "$input" | grep -v '^$' | jq -R . | jq -s .
}

# Probe depth for a single branch by sampling the first entry at each level
probe_branch_depth() {
	local url="$1"
	local markers="$2"
	local depth=0
	local probe_url="$url"

	while [ "$depth" -lt "$MAX_DEPTH" ]; do
		local entries
		entries=$(get_svn_dirs "$probe_url")
		[ -z "$entries" ] && break

		if is_code_level "$entries" "$markers"; then
			break
		fi

		depth=$((depth + 1))
		local first_entry
		first_entry=$(echo "$entries" | head -1)
		[ -z "$first_entry" ] && break
		probe_url="${probe_url}${first_entry}/"
	done

	echo "$depth"
}

# Collect all intermediate-level entries for a branch using BFS traversal.
# Outputs a JSON object: {"depth": N, "level_0": [...], "level_1__X": [...], ...}
collect_branch_tree() {
	local branch_url="$1"
	local markers="$2"
	local depth="$3"

	local result
	result=$(jq -n --argjson d "$depth" '{"depth": $d}')

	if [ "$depth" -eq 0 ]; then
		echo "$result"
		return
	fi

	# Level 0: entries directly under the branch
	local level_0_entries
	level_0_entries=$(get_svn_dirs "$branch_url")
	local level_0_json
	level_0_json=$(list_to_json_array "$level_0_entries")
	result=$(printf '%s\n' "$result" | jq --argjson entries "$level_0_json" '. + {"level_0": $entries}')

	# Deeper levels: iterate through parent entries
	if [ "$depth" -ge 2 ]; then
		while IFS= read -r l0_entry; do
			[ -z "$l0_entry" ] && continue

			local l1_entries
			l1_entries=$(get_svn_dirs "${branch_url}${l0_entry}/")
			local l1_json
			l1_json=$(list_to_json_array "$l1_entries")
			local key="level_1__${l0_entry}"
			result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$l1_json" '. + {($k): $entries}')

			if [ "$depth" -ge 3 ]; then
				while IFS= read -r l1_entry; do
					[ -z "$l1_entry" ] && continue

					local l2_entries
					l2_entries=$(get_svn_dirs "${branch_url}${l0_entry}/${l1_entry}/")
					local l2_json
					l2_json=$(list_to_json_array "$l2_entries")
					key="level_2__${l0_entry}__${l1_entry}"
					result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$l2_json" '. + {($k): $entries}')

					if [ "$depth" -ge 4 ]; then
						while IFS= read -r l2_entry; do
							[ -z "$l2_entry" ] && continue

							local l3_entries
							l3_entries=$(get_svn_dirs "${branch_url}${l0_entry}/${l1_entry}/${l2_entry}/")
							local l3_json
							l3_json=$(list_to_json_array "$l3_entries")
							key="level_3__${l0_entry}__${l1_entry}__${l2_entry}"
							result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$l3_json" '. + {($k): $entries}')
						done <<<"$l2_entries"
					fi
				done <<<"$l1_entries"
			fi
		done <<<"$level_0_entries"
	fi

	echo "$result"
}

# =============================================================================
# Main: Iterate all branches under the version directory
# =============================================================================

# List all branches (top-level directories under version URL)
branches=$(get_svn_dirs "$BASE_URL")

if [ -z "$branches" ]; then
	# No branches found — return empty map
	jq -n '{"data": "{}"}'
	exit 0
fi

# Phase 1: Probe depth for each branch (parallelized)
declare -A branch_depths
while IFS= read -r branch; do
	[ -z "$branch" ] && continue
	branch_url="${BASE_URL}${branch}/"

	if [ "$branch" = "trunk" ]; then
		# trunk is always depth 0 (code is directly here)
		branch_depths["$branch"]=0
	else
		# Probe in background, write result to temp file
		(
			d=$(probe_branch_depth "$branch_url" "$CODE_LEVEL_MARKERS")
			echo "$d" >"$TMPDIR_BASE/depth_${branch}"
		) &
	fi
done <<<"$branches"

# Wait for all depth probes to complete
wait

# Collect depth results
while IFS= read -r branch; do
	[ -z "$branch" ] && continue
	if [ "$branch" != "trunk" ]; then
		if [ -f "$TMPDIR_BASE/depth_${branch}" ]; then
			branch_depths["$branch"]=$(cat "$TMPDIR_BASE/depth_${branch}")
		else
			branch_depths["$branch"]=0
		fi
	fi
done <<<"$branches"

# Phase 2: Collect full tree for each non-trunk branch (parallelized)
while IFS= read -r branch; do
	[ -z "$branch" ] && continue
	branch_url="${BASE_URL}${branch}/"
	depth=${branch_depths["$branch"]:-0}

	(
		tree_json=$(collect_branch_tree "$branch_url" "$CODE_LEVEL_MARKERS" "$depth")
		echo "$tree_json" >"$TMPDIR_BASE/tree_${branch}"
	) &
done <<<"$branches"

# Wait for all tree collections to complete
wait

# Phase 3: Assemble final JSON output
final_json='{}'
while IFS= read -r branch; do
	[ -z "$branch" ] && continue

	if [ "$branch" = "trunk" ]; then
		branch_json='{"depth": 0}'
	elif [ -f "$TMPDIR_BASE/tree_${branch}" ]; then
		branch_json=$(cat "$TMPDIR_BASE/tree_${branch}")
	else
		branch_json='{"depth": 0}'
	fi

	final_json=$(printf '%s\n' "$final_json" | jq --arg k "$branch" --argjson v "$branch_json" '. + {($k): $v}')
done <<<"$branches"

# Output in Terraform external data source format
jq -n --argjson data "$final_json" '{"data": ($data | tostring)}'
