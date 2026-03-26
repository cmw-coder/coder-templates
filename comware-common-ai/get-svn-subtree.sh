#!/bin/bash

# Explore SVN subtree under a branch directory, detect depth dynamically,
# and collect entries at each level in a flattened format.
#
# Output format for Terraform external data source: {"data": "<escaped_json_string>"}
#
# Input (stdin JSON):
#   {
#     "base_url": "http://.../V9R1/branches_bugfix/",
#     "svn_username": "...",
#     "svn_password": "...",
#     "code_level_markers": "ACCESS,DEV,IP,NETFWD"   (comma-separated marker directory names)
#   }
#
# Output (flattened level structure):
#   {"data": "{\"depth\": 2, \"level_0\": [\"TAG_A\", ...], \"level_1__TAG_A\": [\"ISSUE_1\", ...], ...}"}
#
# Depth detection: At each level, check if svn ls results contain any of the
# code_level_markers directories. If found, this is the code level (stop).
# Otherwise, it is an intermediate level (continue deeper).

# Read input from Terraform (stdin)
eval "$(jq -r '@sh "BASE_URL=\(.base_url) SVN_PASSWORD_INPUT=\(.svn_password) SVN_USERNAME_INPUT=\(.svn_username) CODE_LEVEL_MARKERS=\(.code_level_markers)"')"

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
	# Filter only directories and strip trailing /
	echo "${contents}" | grep '/$' | sed 's/\/$//'
}

# Check if the given svn ls output contains any code-level marker directories
is_code_level() {
	local entries="$1"
	local markers="$2"

	IFS=',' read -ra marker_array <<<"$markers"
	for marker in "${marker_array[@]}"; do
		# Trim whitespace
		marker=$(echo "$marker" | xargs)
		[ -z "$marker" ] && continue
		# Check if this marker appears as a directory entry
		if echo "$entries" | grep -qx "$marker"; then
			return 0 # Found marker -> code level
		fi
	done
	return 1 # No marker found -> intermediate level
}

MAX_DEPTH=6
result='{}'
depth=0

# Probe depth by sampling the first entry at each level
probe_url="${BASE_URL}"
probe_depth=0

while [ "$probe_depth" -lt "$MAX_DEPTH" ]; do
	probe_entries=$(get_svn_dirs "${probe_url}")
	[ -z "$probe_entries" ] && break

	# Check if this level is the code level
	if is_code_level "$probe_entries" "$CODE_LEVEL_MARKERS"; then
		break # Reached code level, stop
	fi

	probe_depth=$((probe_depth + 1))

	# Use the first entry to probe the next level
	first_entry=$(echo "$probe_entries" | head -1)
	[ -z "$first_entry" ] && break
	probe_url="${probe_url}${first_entry}/"
done

depth=$probe_depth
result=$(printf '%s\n' "$result" | jq --argjson d "$depth" '. + {"depth": $d}')

# If depth is 0, no intermediate levels to collect
if [ "$depth" -eq 0 ]; then
	jq -n --argjson data "$result" '{"data": ($data | tostring)}'
	exit 0
fi

# Collect entries at each level using BFS-like traversal
# We store (level_index, key_path, url) tuples and process them

# Level 0: entries directly under BASE_URL
level_0_entries=$(get_svn_dirs "${BASE_URL}")
level_0_json=$(printf '%s\n' "$level_0_entries" | grep -v '^$' | jq -R . | jq -s .)
result=$(printf '%s\n' "$result" | jq --argjson entries "$level_0_json" '. + {"level_0": $entries}')

# For deeper levels, iterate through parent entries and collect children
# We use arrays to track parent paths for key construction
if [ "$depth" -ge 2 ]; then
	# Collect level 1 entries for each level 0 entry
	while IFS= read -r l0_entry; do
		[ -z "$l0_entry" ] && continue

		l1_entries=$(get_svn_dirs "${BASE_URL}${l0_entry}/")
		l1_json=$(printf '%s\n' "$l1_entries" | grep -v '^$' | jq -R . | jq -s .)

		# Key: "level_1__<l0_entry>"
		key="level_1__${l0_entry}"
		result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$l1_json" '. + {($k): $entries}')

		# Collect deeper levels if needed
		if [ "$depth" -ge 3 ]; then
			while IFS= read -r l1_entry; do
				[ -z "$l1_entry" ] && continue

				l2_entries=$(get_svn_dirs "${BASE_URL}${l0_entry}/${l1_entry}/")
				l2_json=$(printf '%s\n' "$l2_entries" | grep -v '^$' | jq -R . | jq -s .)
				key="level_2__${l0_entry}__${l1_entry}"
				result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$l2_json" '. + {($k): $entries}')

				if [ "$depth" -ge 4 ]; then
					while IFS= read -r l2_entry; do
						[ -z "$l2_entry" ] && continue

						l3_entries=$(get_svn_dirs "${BASE_URL}${l0_entry}/${l1_entry}/${l2_entry}/")
						l3_json=$(printf '%s\n' "$l3_entries" | grep -v '^$' | jq -R . | jq -s .)
						key="level_3__${l0_entry}__${l1_entry}__${l2_entry}"
						result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$l3_json" '. + {($k): $entries}')

						if [ "$depth" -ge 5 ]; then
							while IFS= read -r l3_entry; do
								[ -z "$l3_entry" ] && continue

								l4_entries=$(get_svn_dirs "${BASE_URL}${l0_entry}/${l1_entry}/${l2_entry}/${l3_entry}/")
								l4_json=$(printf '%s\n' "$l4_entries" | grep -v '^$' | jq -R . | jq -s .)
								key="level_4__${l0_entry}__${l1_entry}__${l2_entry}__${l3_entry}"
								result=$(printf '%s\n' "$result" | jq --arg k "$key" --argjson entries "$l4_json" '. + {($k): $entries}')
							done <<<"$l3_entries"
						fi
					done <<<"$l2_entries"
				fi
			done <<<"$l1_entries"
		fi
	done <<<"$level_0_entries"
elif [ "$depth" -eq 1 ]; then
	# depth == 1: only level_0 needed (already collected above)
	true
fi

# Output in Terraform external data source format
jq -n --argjson data "$result" '{"data": ($data | tostring)}'
