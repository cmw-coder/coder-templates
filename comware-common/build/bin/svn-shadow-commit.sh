#!/bin/bash

# SVN Shadow Branch Commit Script
# This script commits uncommitted changes to a shadow branch

# Configuration variables
SHADOW_BRANCH_SUFFIX="_shadow"
PATCH_FILE="/tmp/svn_with_auth-changes-$(date +%s).patch"
ORIGINAL_DIR=$(pwd)

# Display usage instructions
show_usage() {
    echo "Usage: $0 [options] [filepath]"
    echo "Options:"
    echo "  -s, --shadow PATH       Custom shadow branch path"
    echo "  -u, --username USER     SVN username"
    echo "  -p, --password PASS     SVN password"
    echo "  -h, --help              Display help information"
    echo ""
    echo "If filepath is provided, script will use it to find SVN working copy root"
    exit 1
}

svn_with_auth() {
    local cmd=$1
    shift
    
    # For info and diff commands, we need the output and they don't support -q
    if [ "$cmd" = "info" ] || [ "$cmd" = "diff" ]; then
        if [ -n "$PARAM_SVN_USERNAME" ] && [ -n "$PARAM_SVN_PASSWORD" ]; then
            svn "$cmd" "$@" --non-interactive --username "$PARAM_SVN_USERNAME" --password "$PARAM_SVN_PASSWORD"
        else
            svn "$cmd" "$@" --non-interactive
        fi
    else
        # For other commands, use quiet mode
        if [ -n "$PARAM_SVN_USERNAME" ] && [ -n "$PARAM_SVN_PASSWORD" ]; then
            svn "$cmd" "$@" -q --non-interactive --username "$PARAM_SVN_USERNAME" --password "$PARAM_SVN_PASSWORD"
        else
            svn "$cmd" "$@" -q --non-interactive
        fi
    fi
}

# Parse command line arguments
CUSTOM_SHADOW_PATH=""
FILE_PATH=""
PARAM_SVN_USERNAME=""
PARAM_SVN_PASSWORD=""

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -s|--shadow)
        CUSTOM_SHADOW_PATH="$2"
        shift
        shift
        ;;
        -u|--username)
        PARAM_SVN_USERNAME="$2"
        shift
        shift
        ;;
        -p|--password)
        PARAM_SVN_PASSWORD="$2"
        shift
        shift
        ;;
        -h|--help)
        show_usage
        ;;
        -*)
        echo "Unknown option: $1"
        show_usage
        ;;
        *)
        FILE_PATH="$1"
        shift
        ;;
    esac
done

# Handle file path argument
if [ -n "$FILE_PATH" ]; then
    if [ ! -e "$FILE_PATH" ]; then
        echo "Error: File '$FILE_PATH' does not exist."
        exit 1
    fi
    
    # Get SVN info for the file - don't redirect stderr to preserve error messages
    SVN_INFO=$(svn_with_auth info "$FILE_PATH")
    if [ $? -ne 0 ] || [ -z "$SVN_INFO" ]; then
        echo "Error: '$FILE_PATH' is not under SVN version control or cannot access SVN info."
        exit 1
    fi
    
    echo "SVN info retrieved successfully."
    
    # Extract Working Copy Root Path
    WORKING_ROOT=$(echo "$SVN_INFO" | grep "^Working Copy Root Path:" | awk '{print $5}')
    
    if [ -z "$WORKING_ROOT" ]; then
        echo "Error: Could not determine SVN working copy root path from info:"
        echo "$SVN_INFO"
        exit 1
    fi
    
    echo "Found SVN working copy root: $WORKING_ROOT"
    cd "$WORKING_ROOT" || exit 1
else
    # Check if current directory is an SVN working copy
    if [ ! -d ".svn_with_auth" ]; then
        echo "Error: Current directory is not an SVN working copy."
        exit 1
    fi
    
    # Get SVN info for current directory
    SVN_INFO=$(svn_with_auth info)
    WORKING_ROOT=$(echo "$SVN_INFO" | grep "^Working Copy Root Path:" | awk '{print $5}')
    
    # If working root path is different from current directory, change to it
    if [ -n "$WORKING_ROOT" ] && [ "$WORKING_ROOT" != "$(pwd)" ]; then
        echo "Changing to SVN working copy root: $WORKING_ROOT"
        cd "$WORKING_ROOT" || exit 1
    fi
fi

# Get SVN information from working copy root
SVN_INFO=$(svn_with_auth info)
CURRENT_URL=$(echo "$SVN_INFO" | grep "^URL:" | awk '{print $2}')
REPO_ROOT=$(echo "$SVN_INFO" | grep "^Repository Root:" | awk '{print $3}')
CURRENT_REVISION=$(echo "$SVN_INFO" | grep "^Revision:" | awk '{print $2}')
CURRENT_PATH=${CURRENT_URL#$REPO_ROOT}

# Debugging output
echo "Current URL: $CURRENT_URL"
echo "Repository Root: $REPO_ROOT"
echo "Current Revision: $CURRENT_REVISION"
echo "Current Path: $CURRENT_PATH"

# Build shadow branch URL
if [ -n "$CUSTOM_SHADOW_PATH" ]; then
    SHADOW_BRANCH_URL="${REPO_ROOT}/${CUSTOM_SHADOW_PATH}"
else
    SHADOW_BRANCH_URL="${REPO_ROOT}${CURRENT_PATH}${SHADOW_BRANCH_SUFFIX}"
fi

echo "Shadow branch URL: $SHADOW_BRANCH_URL"

# Check for uncommitted changes
SVN_STATUS=$(svn_with_auth status)
if [ -z "$SVN_STATUS" ]; then
    echo "No uncommitted changes found. No need to commit to shadow branch."
    cd "$ORIGINAL_DIR" || exit 1
    exit 0
fi

echo "Uncommitted changes found. Preparing to commit to shadow branch..."

# Create diff patch file
svn_with_auth diff > "$PATCH_FILE"

# Track added/deleted/unknown files
ADDED_FILES=$(svn_with_auth status | grep "^A" | awk '{print $2}')
DELETED_FILES=$(svn_with_auth status | grep "^D" | awk '{print $2}')
UNKNOWN_FILES=$(svn_with_auth status | grep "^?" | awk '{print $2}')

# Check if shadow branch exists, create if it doesn't
if ! svn_with_auth info "$SHADOW_BRANCH_URL" > /dev/null 2>&1; then
    echo "Shadow branch does not exist. Creating..."
    
    # Try to create the parent directory structure first if needed
    PARENT_PATH=$(dirname "$SHADOW_BRANCH_URL")
    echo "Checking parent path: $PARENT_PATH"
    
    # Create shadow branch
    echo "Running: svn copy \"$CURRENT_URL\" \"$SHADOW_BRANCH_URL\" -m \"Creating shadow branch for $CURRENT_PATH\""
    if ! svn_with_auth copy --parents "$CURRENT_URL" "$SHADOW_BRANCH_URL" -m "Creating shadow branch for $CURRENT_PATH"; then
        echo "Failed to create shadow branch."
        echo "Command failed: svn copy --parents \"$CURRENT_URL\" \"$SHADOW_BRANCH_URL\""
        
        # Check if repository exists
        echo "Verifying repository root..."
        if ! svn_with_auth info "$REPO_ROOT" > /dev/null 2>&1; then
            echo "ERROR: Could not access repository root. Check SVN server connection."
        fi
        
        rm -f "$PATCH_FILE"
        cd "$ORIGINAL_DIR" || exit 1
        exit 1
    fi
    echo "Shadow branch created: $SHADOW_BRANCH_URL"
    
    # Verify the branch was created (with retry)
    echo "Verifying shadow branch creation..."
    for i in {1..3}; do
        if svn_with_auth info "$SHADOW_BRANCH_URL" > /dev/null 2>&1; then
            echo "Shadow branch verified successfully."
            break
        else
            if [ $i -eq 3 ]; then
                echo "ERROR: Failed to verify shadow branch creation after $i attempts."
                rm -f "$PATCH_FILE"
                cd "$ORIGINAL_DIR" || exit 1
                exit 1
            fi
            echo "Waiting for SVN server to process the creation (attempt $i)..."
            sleep 2
        fi
    done
fi

# Instead of checking out the entire shadow branch, we'll use direct server-side operations
echo "Preparing to apply changes directly to shadow branch..."

# Create a modified files list from status
MODIFIED_FILES=$(svn_with_auth status | grep -E "^M" | awk '{print $2}')

# Handle modifications directly
if [ -n "$MODIFIED_FILES" ]; then
    echo "Processing modified files directly..."
    for file in $MODIFIED_FILES; do
        rel_path="${file}"
        shadow_file_url="$SHADOW_BRANCH_URL/$rel_path"
        
        echo "Updating file: $rel_path"
        # Create temporary file with modifications
        tmp_file="/tmp/svn-shadow-$(basename "$file")-$(date +%s)"
        cat "$file" > "$tmp_file"
        
        # Put the modified file directly to shadow branch
        if ! svn_with_auth import -m "Shadow update for $rel_path" "$tmp_file" "$shadow_file_url"; then
            echo "Warning: Failed to update $shadow_file_url"
        fi
        rm -f "$tmp_file"
    done
fi

# Handle added files directly
if [ -n "$ADDED_FILES" ]; then
    echo "Processing added files directly..."
    for file in $ADDED_FILES; do
        rel_path="${file}"
        shadow_file_url="$SHADOW_BRANCH_URL/$rel_path"
        
        echo "Adding file: $rel_path"
        # Create parent directories if needed
        parent_dir=$(dirname "$shadow_file_url")
        svn_with_auth mkdir --parents -m "Creating parent directories for $rel_path" "$parent_dir" 2>/dev/null || true
        
        # Import the file
        if ! svn_with_auth import -m "Shadow add for $rel_path" "$file" "$shadow_file_url"; then
            echo "Warning: Failed to add $shadow_file_url"
        fi
    done
fi

# Handle deleted files directly
if [ -n "$DELETED_FILES" ]; then
    echo "Processing deleted files directly..."
    for file in $DELETED_FILES; do
        rel_path="${file}"
        shadow_file_url="$SHADOW_BRANCH_URL/$rel_path"
        
        echo "Deleting file: $rel_path"
        if ! svn_with_auth delete -m "Shadow delete for $rel_path" "$shadow_file_url"; then
            echo "Warning: Failed to delete $shadow_file_url"
        fi
    done
fi

# Handle unknown files (not under version control)
if [ -n "$UNKNOWN_FILES" ]; then
    echo "Processing unversioned files directly..."
    for file in $UNKNOWN_FILES; do
        rel_path="${file}"
        shadow_file_url="$SHADOW_BRANCH_URL/$rel_path"
        
        echo "Adding unversioned file: $rel_path"
        # Create parent directories if needed
        parent_dir=$(dirname "$shadow_file_url")
        svn_with_auth mkdir --parents -m "Creating parent directories for $rel_path" "$parent_dir" 2>/dev/null || true
        
        # Import the file
        if ! svn_with_auth import -m "Shadow add for unversioned $rel_path" "$file" "$shadow_file_url"; then
            echo "Warning: Failed to add unversioned $shadow_file_url"
        fi
    done
fi

# Final commit message to shadow branch
echo "Changes applied directly to shadow branch: $SHADOW_BRANCH_URL"
echo "SVN revision: $(svn_with_auth info "$SHADOW_BRANCH_URL" | grep "^Revision:" | awk '{print $2}')"

# Clean up
rm -f "$PATCH_FILE"

# Return to original directory
cd "$ORIGINAL_DIR" || exit 1
