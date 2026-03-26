#!/bin/bash

# Pre-fetch complete SVN directory tree for ALL versions and branches.
# Replaces get-svn-map.sh, get-svn-subtree.sh, and get-svn-list.sh.
#
# Input (stdin JSON from Terraform external data source):
#   {
#     "base_url": "http://.../cmwcode-open/",
#     "svn_username": "...",
#     "svn_password": "...",
#     "code_level_markers": "ACCESS,DEV,IP,NETFWD"
#   }
#
# Output (Terraform external data source format):
#   {"data": "<serialized JSON>"}
#
# The serialized JSON has this structure:
#   {
#     "V9R1": {
#       "branches": ["trunk", "branches_bugfix", "tags"],
#       "trunk": {
#         "depth": 0,
#         "folders": ["ACCESS", "DEV", "IP", "NETFWD"]
#       },
#       "branches_bugfix": {
#         "depth": 2,
#         "level_0": ["fix1", "fix2"],
#         "level_1__fix1": ["sub1", "sub2"],
#         "level_1__fix2": ["sub3"],
#         "folders": ["ACCESS", "DEV", "IP", "NETFWD"]
#       }
#     }
#   }
#
# Design notes:
#   - "branches" key: ordered list of branch names for dropdown options
#   - "depth" key: per-branch, 0 = code is directly under branch (e.g., trunk)
#   - "level_N__X__Y" keys: intermediate directory entries for subdir cascading
#   - "folders" key: sampled from the FIRST leaf path of each branch (not per-path)
#     because code-level directories are the same across all paths within a branch
#   - Aggressive parallelism: one background process per version/branch combo

set -euo pipefail

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "BASE_URL=\(.base_url) SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username) CODE_LEVEL_MARKERS=\(.code_level_markers)"')"

SVN_PASSWORD=${SVN_PASSWORD_INPUT:-${SVN_PASSWORD:-""}}
SVN_USERNAME=${SVN_USERNAME_INPUT:-${SVN_USERNAME:-""}}

MAX_DEPTH=6
TMPDIR_BASE=$(mktemp -d)
trap 'rm -rf "$TMPDIR_BASE"' EXIT

# =============================================================================
# Helper functions
# =============================================================================

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
		echo ""
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

# Probe depth for a single branch by sampling the FIRST entry at each level.
# Also outputs the sampled path so we can reuse it for folder listing.
# Returns: "depth first_entry_0/first_entry_1/..."
probe_branch_depth() {
	local url="$1"
	local markers="$2"
	local depth=0
	local probe_url="$url"
	local sampled_path=""

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

		if [ -n "$sampled_path" ]; then
			sampled_path="${sampled_path}/${first_entry}"
		else
			sampled_path="${first_entry}"
		fi
		probe_url="${url}${sampled_path}/"
	done

	echo "${depth} ${sampled_path}"
}

# Process a single branch: detect depth, collect intermediate dirs, sample folders.
# Writes result JSON to $TMPDIR_BASE/branch_<version>_<branch>
process_branch() {
	local version="$1"
	local branch="$2"
	local branch_url="$3"
	local markers="$4"
	local outfile="$TMPDIR_BASE/branch_${version}_${branch}"

	# Step 1: Probe depth and get sampled path
	local probe_result
	probe_result=$(probe_branch_depth "$branch_url" "$markers")
	local depth sampled_path
	depth=$(echo "$probe_result" | cut -d' ' -f1)
	sampled_path=$(echo "$probe_result" | cut -d' ' -f2-)

	# Initialize result with depth
	local result
	result=$(jq -n --argjson d "$depth" '{"depth": $d}')

	# Step 2: Collect intermediate-level entries (only if depth > 0)
	if [ "$depth" -gt 0 ]; then
		# Level 0: entries directly under the branch
		local level_0_entries
		level_0_entries=$(get_svn_dirs "$branch_url")
		local level_0_json
		level_0_json=$(list_to_json_array "$level_0_entries")
		result=$(printf '%s\n' "$result" | jq --argjson entries "$level_0_json" '. + {"level_0": $entries}')

		# Level 1+: nested entries (parallelized within branch for level 1)
		if [ "$depth" -ge 2 ]; then
			local l1_tmpdir="$TMPDIR_BASE/l1_${version}_${branch}"
			mkdir -p "$l1_tmpdir"

			while IFS= read -r l0_entry; do
				[ -z "$l0_entry" ] && continue
				(
					l1_entries=$(get_svn_dirs "${branch_url}${l0_entry}/")
					l1_json=$(list_to_json_array "$l1_entries")
					# Write json to temp file (filename encodes the key)
					printf '%s\n' "$l1_json" >"$l1_tmpdir/${l0_entry}"

					# Level 2 (if depth >= 3)
					if [ "$depth" -ge 3 ] && [ -n "$l1_entries" ]; then
						while IFS= read -r l1_entry; do
							[ -z "$l1_entry" ] && continue
							l2_entries=$(get_svn_dirs "${branch_url}${l0_entry}/${l1_entry}/")
							l2_json=$(list_to_json_array "$l2_entries")
							printf '%s\n' "$l2_json" >"$l1_tmpdir/${l0_entry}__${l1_entry}"

							# Level 3 (if depth >= 4)
							if [ "$depth" -ge 4 ] && [ -n "$l2_entries" ]; then
								while IFS= read -r l2_entry; do
									[ -z "$l2_entry" ] && continue
									l3_entries=$(get_svn_dirs "${branch_url}${l0_entry}/${l1_entry}/${l2_entry}/")
									l3_json=$(list_to_json_array "$l3_entries")
									printf '%s\n' "$l3_json" >"$l1_tmpdir/${l0_entry}__${l1_entry}__${l2_entry}"
								done <<<"$l2_entries"
							fi
						done <<<"$l1_entries"
					fi
				) &
			done <<<"$level_0_entries"

			wait || true

			# Collect level 1+ results from temp files
			for tmpfile in "$l1_tmpdir"/*; do
				[ -f "$tmpfile" ] || continue
				local basename
				basename=$(basename "$tmpfile")
				local json_val
				json_val=$(cat "$tmpfile")

				# Determine the key based on the number of __ separators
				local num_separators
				num_separators=$(echo "$basename" | grep -o '__' | wc -l)

				local key
				if [ "$num_separators" -eq 0 ]; then
					key="level_1__${basename}"
				elif [ "$num_separators" -eq 1 ]; then
					key="level_2__${basename}"
				elif [ "$num_separators" -eq 2 ]; then
					key="level_3__${basename}"
				else
					key="level_$((num_separators + 1))__${basename}"
				fi

				result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$json_val" '. + {($k): $entries}')
			done
		fi
	fi

	# Step 3: Sample folders from the code level
	# Use the sampled path from depth probing to reach the code level
	local folder_url
	if [ -n "$sampled_path" ]; then
		folder_url="${branch_url}${sampled_path}/"
	else
		folder_url="$branch_url"
	fi

	local folder_entries
	folder_entries=$(get_svn_dirs "$folder_url")
	local folder_json
	folder_json=$(list_to_json_array "$folder_entries")
	result=$(printf '%s\n' "$result" | jq --argjson folders "$folder_json" '. + {"folders": $folders}')

	echo "$result" >"$outfile"
}

# =============================================================================
# Main execution
# =============================================================================

# Phase 1: List all versions
versions=$(get_svn_dirs "$BASE_URL")

if [ -z "$versions" ]; then
	jq -n '{"data": "{}"}'
	exit 0
fi

# Phase 2: For each version, list branches and process each branch in parallel
final_json='{}'

while IFS= read -r version; do
	[ -z "$version" ] && continue
	version_url="${BASE_URL}${version}/"

	# List branches for this version
	branches=$(get_svn_dirs "$version_url")
	[ -z "$branches" ] && continue

	# Build branch list JSON
	branch_list_json=$(list_to_json_array "$branches")

	# Launch parallel processing for each branch
	while IFS= read -r branch; do
		[ -z "$branch" ] && continue
		branch_url="${version_url}${branch}/"

		if [ "$branch" = "trunk" ]; then
			# trunk is always depth 0, just sample folders directly
			(
				folder_entries=$(get_svn_dirs "$branch_url")
				folder_json=$(list_to_json_array "$folder_entries")
				jq -n --argjson folders "$folder_json" '{"depth": 0, "folders": $folders}' \
					>"$TMPDIR_BASE/branch_${version}_${branch}"
			) &
		else
			process_branch "$version" "$branch" "$branch_url" "$CODE_LEVEL_MARKERS" &
		fi
	done <<<"$branches"

	# Wait for all branches of this version to complete
	wait || true

	# Assemble version JSON
	version_json=$(jq -n --argjson branches "$branch_list_json" '{"branches": $branches}')

	while IFS= read -r branch; do
		[ -z "$branch" ] && continue
		outfile="$TMPDIR_BASE/branch_${version}_${branch}"
		if [ -f "$outfile" ]; then
			branch_json=$(cat "$outfile")
			version_json=$(printf '%s\n' "$version_json" | jq --arg k "$branch" --argjson v "$branch_json" '. + {($k): $v}')
		else
			# Fallback: branch with depth 0 and empty folders
			version_json=$(printf '%s\n' "$version_json" | jq --arg k "$branch" '. + {($k): {"depth": 0, "folders": []}}')
		fi
	done <<<"$branches"

	final_json=$(printf '%s\n' "$final_json" | jq --arg k "$version" --argjson v "$version_json" '. + {($k): $v}')
done <<<"$versions"

# Output in Terraform external data source format
jq -n --argjson data "$final_json" '{"data": ($data | tostring)}'
