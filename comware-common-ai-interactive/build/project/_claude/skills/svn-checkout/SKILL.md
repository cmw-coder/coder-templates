---
name: svn-checkout
description: Interactive SVN project checkout skill. Guides users through branch selection, folder picking, and credential setup via natural language conversation. Manages the full lifecycle from initial checkout to subsequent updates.
---

# SVN Project Checkout Skill

## Overview

This skill handles interactive SVN project configuration and checkout for Comware workspaces. Instead of requiring users to fill in Terraform UI parameters, it collects SVN configuration through natural language conversation, persists the configuration, and executes checkout operations.

## Workspace Script Locations

All utility scripts are installed in `/usr/local/bin/` and available in `$PATH`. You can `source` or execute them **by name only** — do NOT use absolute paths or try to find them under the home directory.

| Script | Type | Usage |
|---|---|---|
| `svn-utils` | Source library | `source svn-utils` — provides `svn_with_auth`, `svn_s`, `svn_remove_branch` |
| `checkout-list` | Executable | `checkout-list platform` or `checkout-list public` |
| `project-env` | Source library | `source project-env` — loads `~/.svn_project_env` (auto-sourced by other scripts) |
| `abuild` | Executable | `abuild -e 64sim9cen` |
| `build-job` | Executable | `build-job --type abuild -e 64sim9cen` |
| `shadow-branch` | Executable | `shadow-branch "$PROJECT_PLATFORM_PATH"` |

**CRITICAL:** When you need to use `svn_with_auth`, just run:

```bash
source svn-utils
svn_with_auth list "http://..."
```

Do NOT try to find `svn-utils` with `find` or `locate`. Do NOT use paths like `~/project/.tools/svn-utils` or `/home/user/project/.tools/svn-utils`. The scripts are in `/usr/local/bin/` which is already in `$PATH`.

## Configuration File

All parameters are persisted to `~/.svn_project_env` in shell-sourceable format. This file is automatically loaded by all workspace scripts (`checkout-list`, `abuild`, `build-job`, `svn-utils`, etc.) via the `project-env` utility.

**File format:**

```bash
export SVN_USERNAME="<username>"
export SVN_PASSWORD_B64="<base64-encoded-password>"
export PROJECT_PLATFORM_SVN="http://10.153.120.80/cmwcode-open/<branch_path>"
export PROJECT_PLATFORM_FOLDER_LIST='["folder1","folder2"]'
export PROJECT_PLATFORM_PATH="$HOME/project/platform"
export PROJECT_PUBLIC_SVN="http://10.153.120.104/cmwcode-public/<branch_path>"
export PROJECT_PUBLIC_FOLDER_LIST='["PUBLIC/include"]'
export PROJECT_PUBLIC_PATH="$HOME/project/public"
```

**IMPORTANT:** After writing the file, always run `chmod 600 ~/.svn_project_env` to protect credentials.

## Decision Flow

### Step 1: Detect Current State

Before asking any questions, check the workspace state:

```bash
# Check if config already exists
[ -f ~/.svn_project_env ] && echo "CONFIG_EXISTS" || echo "NO_CONFIG"

# Check if platform checkout exists
[ -d ~/project/platform/.svn ] && echo "PLATFORM_CHECKED_OUT" || echo "NO_PLATFORM"

# Check if public checkout exists
[ -d ~/project/public/.svn ] && echo "PUBLIC_CHECKED_OUT" || echo "NO_PUBLIC"
```

**Decision matrix:**

| Config exists | Checkout exists | Action |
|---|---|---|
| No | No | → **First-time setup flow** (Step 2) |
| Yes | No | → Load config, confirm with user, execute checkout |
| Yes | Yes | → **Maintenance flow** (Step 8) |
| No | Yes | → Recover config from `svn info`, ask for missing credentials |

### Step 2: Collect SVN Credentials (MUST be first)

Credentials are needed before any `svn list` operations for directory browsing.

**SVN username:**
- Default: `$CODER_WORKSPACE_OWNER` or `$USER` environment variable
- Say to user: "SVN username will default to `<default_value>`, press enter to confirm or provide a different one."

**SVN password:**
- Required, no default value
- Say to user: "Please provide your SVN password. It will be stored as base64-encoded text in `~/.svn_project_env`."

After collecting credentials, write them to the config file IMMEDIATELY so that `svn-utils` (and all other scripts) can find them automatically. Then source and validate:

```bash
# Write credentials to config file first (even before branch selection)
# This ensures svn-utils can authenticate for subsequent svn list operations
cat > ~/.svn_project_env << 'ENVEOF'
export SVN_USERNAME="<collected_username>"
export SVN_PASSWORD_B64="<base64_password>"
ENVEOF
chmod 600 ~/.svn_project_env

# Now source svn-utils (it auto-loads project-env which reads ~/.svn_project_env)
source svn-utils
# Test authentication works
svn_with_auth list "http://10.153.120.80/cmwcode-open/" | head -10
```

**IMPORTANT:** After branch and folder selection is complete (Step 7), the config file will be overwritten with the full configuration including all parameters. This initial write is just to enable `svn list` operations during the selection process.

### Step 3: Select Branch Path

The user provides the SVN branch path which is appended to fixed prefixes:
- **Platform prefix:** `http://10.153.120.80/cmwcode-open`
- **Public prefix:** `http://10.153.120.104/cmwcode-public`

Support three input modes:

#### Mode A: Direct path

User provides a complete path like `V9R1/trunk` or `V7R1_SPRINGB75/branches_bugfix/COMWAREV700R001B75D071SP0010/H20250101-012345`.

**Validation:** Run the following in bash (svn-utils is already sourced from Step 2):

```bash
source svn-utils
svn_with_auth list "http://10.153.120.80/cmwcode-open/<path>/" | head -20
```

- If valid → proceed to Step 4
- If invalid → find the last valid path segment and switch to **Mode C** from that level

#### Mode B: Natural language

User describes their intent in natural language. Parse the description to extract:

| User says | Interpret as |
|---|---|
| "V9R1 main branch" / "V9R1 trunk" / "V9R1主分支" | `V9R1/trunk` |
| "V9R1 bugfix for tag XXX, ticket YYY" | `V9R1/branches_bugfix/XXX/YYY` |
| "V7R1_SPRINGB75 project branch XXX" | `V7R1_SPRINGB75/branches_project/XXX/...` |
| "latest V9R1 tag" | Need to `svn list` tags to find latest |

After parsing, validate as in Mode A.

#### Mode C: Interactive level-by-level browsing

Guide the user through the SVN directory hierarchy level by level.

**Level 1 — Major branch:**

```bash
source svn-utils
svn_with_auth list "http://10.153.120.80/cmwcode-open/" | head -50
```

Known major branches (prioritize display):
- **Main branches (old→new):** `V7R1_SPRINGB64`, `V7R1_SPRINGB75`, `V9R1`
- **Tag-based major branches (examples):** `V7R1_B64D029SP`, `V7R1_B70D011SP`, `V7R1B75D071SP`

Present the list and ask the user to choose.

**Level 2 — Branch type:**

```bash
source svn-utils
svn_with_auth list "http://10.153.120.80/cmwcode-open/<L1>/"
```

Common directories and their meanings:
- `trunk/` — Current main branch of this major version (**most common**)
- `branches_bugfix/` — Bug fix branches (**common**)
- `branches_project/` — Feature project branches (**common**)
- `branches_ai/` — AI and automation tool branches
- `tags/` — Periodic snapshots from trunk

Present with explanations and ask the user to choose.

**Level 3+ — Varies by Level 2 selection:**

- **`trunk`** → This IS the code directory. No further level selection needed. Proceed to Step 4.

- **`tags/`** → List contents:
  ```bash
  svn_with_auth list "http://10.153.120.80/cmwcode-open/<L1>/tags/"
  ```
  Typically shows `ai_tags/` and `trunk_tags/`. User usually wants `trunk_tags/`, then selects a specific tag name from the listing.

- **`branches_bugfix/`** → List tag directories:
  ```bash
  svn_with_auth list "http://10.153.120.80/cmwcode-open/<L1>/branches_bugfix/"
  ```
  Each entry is a tag name (corresponding to `tags/trunk_tags/` entries). After selecting a tag, list ticket numbers within it:
  ```bash
  svn_with_auth list "http://10.153.120.80/cmwcode-open/<L1>/branches_bugfix/<tag_name>/"
  ```
  Each entry is a bug ticket number. The code directory is inside the ticket directory.

- **`branches_project/`** → Same structure as `branches_bugfix/`: tag name → project name → code directory.

At each level, always run `svn_with_auth list` to get the actual directory listing and present it to the user. **Never guess directory names.**

### Step 4: Select Platform Folder List

After determining the full platform SVN URL, decide which subdirectories to checkout.

```bash
source svn-utils
svn_with_auth list "http://10.153.120.80/cmwcode-open/<full_branch_path>/" | head -80
```

Present the directory listing to the user and explain options:

1. **Select specific modules** (recommended for daily development — faster checkout):
   - Show the available directories
   - Let user pick by name, e.g., "I need ospf and nqa"
   - Validate each selection exists in the listing

2. **Checkout everything** (empty list — full checkout):
   - Warn that full checkout may take significant time
   - User must explicitly confirm

**If user specifies folders that don't exist:**

For each non-existent folder, run `svn_with_auth list` on the parent level again and suggest similar names (case-insensitive matching, prefix matching). Let the user correct their selection.

### Step 5: Determine Public Branch Path

By default, the public SVN uses the **same branch path** as the platform SVN.

- Tell user: "Public SVN will use the same branch path `<branch_path>`. Is that correct, or do you need a different path?"
- If user confirms → use same path
- If user provides override → validate with `svn_with_auth list` (same as Step 3)

### Step 6: Select Public Folder List

The public repository has a different structure from platform. Under the code directory, there may be:
- `PUBLIC/` (always present)
- `PUBLIC2/` (present on some major branches)
- `PUBLIC3/` (present on some major branches)

**Process:**

1. List the top-level directories:
   ```bash
   source svn-utils
   svn_with_auth list "http://10.153.120.104/cmwcode-public/<full_branch_path>/"
   ```

2. **`PUBLIC/include` is ALWAYS included** — inform the user this is mandatory for symbol indexing.

3. If only `PUBLIC/` exists:
   - Ask if user needs additional subdirectories beyond `PUBLIC/include`
   - Show available subdirectories: `svn_with_auth list ".../PUBLIC/"`

4. If `PUBLIC2/` or `PUBLIC3/` also exist:
   - Inform user: "This branch also has PUBLIC2/ and PUBLIC3/. Usually only PUBLIC/ is needed. Do you need the others?"
   - If yes, let user select subdirectories within each

5. **If user specifies folders that don't exist:**
   - Same behavior as Step 4: list actual contents and suggest corrections

### Step 7: Write Config and Execute Checkout

1. **Write the configuration file:**

   The `<base64_password>` value should be computed from the raw password collected in Step 2: `printf '%s' '<raw_password>' | base64 -w0`

   ```bash
   cat > ~/.svn_project_env << 'ENVEOF'
   export SVN_USERNAME="<username>"
   export SVN_PASSWORD_B64="<base64_password>"
   export PROJECT_PLATFORM_SVN="http://10.153.120.80/cmwcode-open/<branch_path>"
   export PROJECT_PLATFORM_FOLDER_LIST='["folder1","folder2"]'
   export PROJECT_PLATFORM_PATH="$HOME/project/platform"
   export PROJECT_PUBLIC_SVN="http://10.153.120.104/cmwcode-public/<branch_path>"
   export PROJECT_PUBLIC_FOLDER_LIST='["PUBLIC/include","PUBLIC/lib"]'
   export PROJECT_PUBLIC_PATH="$HOME/project/public"
   ENVEOF
   chmod 600 ~/.svn_project_env
   ```

   **IMPORTANT:** Use single-quoted heredoc delimiter (`'ENVEOF'`) to prevent variable expansion during write. The `$HOME` in PATH values should be written literally so it resolves at source-time.

2. **Source the config and execute checkout:**

   ```bash
   source ~/.svn_project_env
   checkout-list platform
   ```

   Then:

   ```bash
   source ~/.svn_project_env
   checkout-list public
   ```

3. **Report results** to the user: checkout success/failure, number of files, time taken.

### Step 8: Maintenance Flow (Subsequent Invocations)

When config and checkout both exist, do NOT ask for parameters again. Instead:

1. **Load existing config:**
   ```bash
   source ~/.svn_project_env
   ```

2. **Check current status:**
   ```bash
   source svn-utils
   svn_with_auth status "$PROJECT_PLATFORM_PATH"
   svn_with_auth status "$PROJECT_PUBLIC_PATH"
   ```

3. **Based on status, suggest appropriate actions:**

   | Status | Suggestion |
   |---|---|
   | Local modifications exist | "You have uncommitted changes. Would you like to review them (`svn diff`), commit them, or revert?" |
   | No modifications | "Your working copy is clean. Would you like to update to the latest revision (`svn update`)?" |
   | User asks for new modules | Add folders to the existing checkout using `svn update --set-depth infinity --parents <path>/<new_folder>`, then update `PROJECT_PLATFORM_FOLDER_LIST` in the config file |

4. **Config modification:** If user wants to change the branch, folder list, or credentials, update `~/.svn_project_env` accordingly and re-run the relevant checkout.

## Important Notes

1. **All `svn` commands requiring authentication MUST use `svn_with_auth` from `svn-utils`**, never plain `svn` with hardcoded credentials.

2. **Script location:** All scripts (`svn-utils`, `checkout-list`, `project-env`, `abuild`, `build-job`, `shadow-branch`) are in `/usr/local/bin/` (in PATH). Always use `source svn-utils` — NEVER try to find or guess the path with `find`, `locate`, or manual path construction.

3. **Encoding:** After checkout, `checkout-list` automatically converts `.c`/`.h` files from GBK to UTF-8. No manual conversion needed at this stage.

4. **Error handling:** If `svn list` or `checkout-list` fails with authentication errors, ask the user to verify their credentials and offer to update them in the config file.

5. **Large directory listings:** When `svn list` returns many entries (>50), show only the first 50 with a note that more exist. Let the user search by keyword if needed.

6. **Config recovery:** If config is lost but checkout exists, recover SVN URLs from:
   ```bash
   svn info ~/project/platform | grep "^URL:"
   svn info ~/project/public | grep "^URL:"
   ```
   Then only ask for credentials and folder list.
