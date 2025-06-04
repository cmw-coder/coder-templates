#!/bin/bash

# SVN Shadow Branch Commit Script
# This script commits uncommitted changes to a shadow branch

# Configuration variables
SHADOW_BRANCH_SUFFIX="_shadow"
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
    if [ "$cmd" = "diff" ] || [ "$cmd" = "info" ] || [ "$cmd" = "update" ]; then
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
    -s | --shadow)
        CUSTOM_SHADOW_PATH="$2"
        shift
        shift
        ;;
    -u | --username)
        PARAM_SVN_USERNAME="$2"
        shift
        shift
        ;;
    -p | --password)
        PARAM_SVN_PASSWORD="$2"
        shift
        shift
        ;;
    -h | --help)
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
    if [ ! -d ".svn" ]; then
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
LAST_CHANGED_REVISION=$(echo "$SVN_INFO" | grep "^Last Changed Rev:" | awk '{print $4}')
CURRENT_PATH=${CURRENT_URL#"$REPO_ROOT"}

# Debugging output
echo "Current URL: $CURRENT_URL"
echo "Repository Root: $REPO_ROOT"
echo "Last Changed Revision: $LAST_CHANGED_REVISION"
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

# Track added/deleted/unknown files
MODIFIED_FILES=$(svn_with_auth status | grep -E "^M|^MM" | awk '{print $2}')
ADDED_FILES=$(svn_with_auth status | grep "^A" | awk '{print $2}')
DELETED_FILES=$(svn_with_auth status | grep "^D" | awk '{print $2}')

# Check if shadow branch exists, create if it doesn't
if ! svn_with_auth info "$SHADOW_BRANCH_URL" >/dev/null 2>&1; then
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
        if ! svn_with_auth info "$REPO_ROOT" >/dev/null 2>&1; then
            echo "ERROR: Could not access repository root. Check SVN server connection."
        fi

        cd "$ORIGINAL_DIR" || exit 1
        exit 1
    fi
    echo "Shadow branch created: $SHADOW_BRANCH_URL"

    # Verify the branch was created (with retry)
    echo "Verifying shadow branch creation..."
    for i in {1..3}; do
        if svn_with_auth info "$SHADOW_BRANCH_URL" >/dev/null 2>&1; then
            echo "Shadow branch verified successfully."
            break
        else
            if [ "$i" -eq 3 ]; then
                echo "ERROR: Failed to verify shadow branch creation after $i attempts."
                cd "$ORIGINAL_DIR" || exit 1
                exit 1
            fi
            echo "Waiting for SVN server to process the creation (attempt $i)..."
            sleep 2
        fi
    done
else
    # Shadow branch already exists, sync it with main branch first
    echo "Shadow branch exists. Syncing with main branch..."

    # Get main branch revision to sync with
    MAIN_LAST_CHANGED_REV=$LAST_CHANGED_REVISION
    echo "Main branch last changed revision: $MAIN_LAST_CHANGED_REV"

    # Delete shadow branch and recreate it to ensure it's in sync
    if svn_with_auth delete -m "Resetting shadow branch to sync with main" "$SHADOW_BRANCH_URL" >/dev/null; then
        echo "Deleted old shadow branch"

        # Recreate shadow branch from main branch
        if svn_with_auth copy -r "$MAIN_LAST_CHANGED_REV" "$CURRENT_URL" "$SHADOW_BRANCH_URL" -m "Resetting shadow branch to main r$MAIN_LAST_CHANGED_REV"; then
            echo "Shadow branch reset to match main branch revision $MAIN_LAST_CHANGED_REV"
        else
            echo "Failed to recreate shadow branch"
            cd "$ORIGINAL_DIR" || exit 1
            exit 1
        fi
    else
        echo "Warning: Could not reset shadow branch, continuing with existing branch"
    fi
fi

# Instead of handling individual files separately, check out the entire shadow branch
# and apply all changes in one commit
# Use sparse checkout to handle large repositories efficiently
process_files_in_single_commit() {
    local temp_dir
    temp_dir="/tmp/svn-shadow-$(date +%s)"
    local changed=false

    echo "Creating sparse checkout..."
    mkdir -p "$temp_dir"
    
    # Initialize empty checkout
    if ! svn_with_auth checkout --depth=empty "$SHADOW_BRANCH_URL" "$temp_dir" > /dev/null; then
        echo "Failed to initialize checkout"
        rm -rf "$temp_dir"
        return 1
    fi
    cd "$temp_dir" || return 1
    
    # Modify process_file to handle conflicts
    process_file() {
        local action="$1"
        local relative_path="$2"
        
        # Update the parent directory to ensure it exists
        svn_with_auth update --parents --set-depth empty "$relative_path" >/dev/null 2>&1
        
        case "$action" in
            add)                
                # Copy new content from working root
                cp -f "$WORKING_ROOT/$relative_path" "$relative_path"
                
                # Add to version control with force
                svn_with_auth add --force "$relative_path" > /dev/null 2>&1
                
                # Check status to see if we have conflicts
                if svn_with_auth status "$relative_path" | grep -q "^C"; then
                    echo "- Resolving conflict with local version"
                    svn_with_auth resolve --accept working "$relative_path" > /dev/null 2>&1
                fi
                ;;
            update)                
                # Copy new content from working root
                cp -f "$WORKING_ROOT/$relative_path" "$relative_path"
                
                # Check status to see if we have conflicts
                if svn_with_auth status "$relative_path" | grep -q "^C"; then
                    echo "- Resolving conflict with local version"
                    svn_with_auth resolve --accept working "$relative_path" > /dev/null 2>&1
                fi
                ;;
            delete)
                [ -e "$relative_path" ] && svn_with_auth delete "$relative_path" > /dev/null 2>&1
                ;;
        esac
        echo "OK $action: $relative_path"
        changed=true
    }

    # Process each file type
    echo "Processing modified files..."
    for relative_path in $MODIFIED_FILES; do
        [ -f "$WORKING_ROOT/$relative_path" ] && process_file "update" "$relative_path"
    done
    
    echo "Processing added files..."
    for relative_path in $ADDED_FILES; do
        [ -f "$WORKING_ROOT/$relative_path" ] && process_file "add" "$relative_path"
    done
    
    echo "Processing deleted files..."
    for relative_path in $DELETED_FILES; do
        process_file "delete" "$relative_path"
    done

    # Commit all changes
    if [ "$changed" = true ]; then
        echo "Committing all changes..."
        if svn_with_auth commit -m "[Auto Sync] Commit for CodeX - $(date '+%Y-%m-%d %H:%M:%S')"; then
            echo "✓ Successfully committed all changes"
        else
            echo "✗ Commit failed"
            cd ..
            rm -rf "$temp_dir"
            return 1
        fi
    else
        echo "No changes to commit"
    fi

    cd ..
    rm -rf "$temp_dir"
    return 0
}

# Apply changes directly to shadow branch
echo "Applying changes to shadow branch..."

# Process all changes in single commit instead of individual operations
if ! process_files_in_single_commit; then
    echo "Error applying changes to shadow branch."
    cd "$ORIGINAL_DIR" || exit 1
    exit 1
fi

# Final summary
echo ""
echo "Changes applied to shadow branch: $SHADOW_BRANCH_URL"
echo "SVN revision: $(svn_with_auth info "$SHADOW_BRANCH_URL" | grep "^Last Changed Rev:" | awk '{print $4}')"

# Clean up
# Remove unused patch file cleanup
# Return to original directory
cd "$ORIGINAL_DIR" || exit 1
