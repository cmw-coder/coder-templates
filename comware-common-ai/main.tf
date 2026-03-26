terraform {
  required_providers {
    coder = {
      source = "coder/coder"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.6.2"
    }
    external = {
      source = "hashicorp/external"
    }
  }
}

provider "docker" {
  registry_auth {
    address  = "registry.coder.h3c.com"
    username = "coder"
    password = "silly"
  }
}

provider "coder" {
}

# =============================================================================
# External data sources: SVN directory discovery
# =============================================================================

# Pre-fetch platform SVN directory map (version -> branch types)
data "external" "platform_svn_map" {
  program = ["bash", "${path.module}/get-svn-map.sh"]

  query = {
    base_url     = "http://10.153.120.80/cmwcode-open/"
    svn_username = "z11187"
    svn_password = "Zpr758258%"
  }
}

# Pre-fetch public SVN directory map (version -> branch types)
data "external" "public_svn_map" {
  program = ["bash", "${path.module}/get-svn-map.sh"]

  query = {
    base_url     = "http://10.153.120.104/cmwcode-public/"
    svn_username = "z11187"
    svn_password = "Zpr758258%"
  }
}

# Pre-fetch platform subtree for ALL branches under the selected version.
# This is unconditional so the Coder UI can dynamically look up branch data
# using live parameter values against the pre-computed constant map.
data "external" "platform_subtree" {
  program = ["bash", "${path.module}/get-svn-subtree.sh"]

  query = {
    base_url           = "${local.platform_prefix}/${data.coder_parameter.platform_version.value}/"
    svn_username       = "z11187"
    svn_password       = "Zpr758258%"
    code_level_markers = "ACCESS,DEV,IP,NETFWD"
  }
}

# Fetch platform code-level directory listing for folder selection
data "external" "platform_folders" {
  count = local.platform_path_complete ? 1 : 0

  program = ["bash", "${path.module}/get-svn-list.sh"]

  query = {
    url          = "${local.platform_svn_url}/"
    svn_username = "z11187"
    svn_password = "Zpr758258%"
  }
}

# Pre-fetch public subtree for ALL branches (only when custom public path enabled).
# Uses direct parameter reference for count so the Coder UI can evaluate it dynamically.
data "external" "public_subtree" {
  count = data.coder_parameter.custom_public_path.value == "true" ? 1 : 0

  program = ["bash", "${path.module}/get-svn-subtree.sh"]

  query = {
    base_url           = "${local.public_prefix}/${try(data.coder_parameter.public_version[0].value, "")}/"
    svn_username       = "z11187"
    svn_password       = "Zpr758258%"
    code_level_markers = "PUBLIC"
  }
}

# Fetch public code-level directory listing for folder selection
data "external" "public_folders" {
  count = local.public_path_complete ? 1 : 0

  program = ["bash", "${path.module}/get-svn-list.sh"]

  query = {
    url          = "${local.public_svn_url}/"
    svn_username = "z11187"
    svn_password = "Zpr758258%"
  }
}

# =============================================================================
# Coder data sources
# =============================================================================

data "coder_provisioner" "me" {
}
data "coder_workspace" "me" {
}
data "coder_workspace_owner" "me" {
}

# =============================================================================
# Locals
# =============================================================================

locals {
  # Existing configuration
  assets_url          = "https://coder-assets.cmwcoder.h3c.com"
  code_server_dir     = "/tmp/code-server"
  coder_docs_url      = "https://coder-docs.cmwcoder.h3c.com"
  coder_tutorials_url = "https://tutorials.coder.h3c.com"
  marketplace_url     = "https://code-marketplace.cmwcoder.h3c.com"
  project_path        = "/home/${data.coder_workspace_owner.me.name}/project"

  # SVN base URLs
  platform_prefix = "http://10.153.120.80/cmwcode-open"
  public_prefix   = "http://10.153.120.104/cmwcode-public"

  # Pre-fetched SVN directory maps
  platform_svn_map = jsondecode(data.external.platform_svn_map.result.data)
  public_svn_map   = jsondecode(data.external.public_svn_map.result.data)

  # --- Platform path state ---
  platform_branch_value = try(data.coder_parameter.platform_branch[0].value, "")
  platform_is_trunk     = local.platform_branch_value == "trunk"

  # Pre-fetched subtree map for ALL branches under the selected version.
  # This is a constant map at plan time; the Coder UI uses it with live parameter values.
  # Note: try() fallback handles runtime JSON errors but NOT unknown values during
  # workspace tag parsing. The short-circuit in platform_subdir count handles that case.
  platform_subtree_all = try(jsondecode(data.external.platform_subtree.result.data), {})

  # Server-side: subtree data for the actually-selected branch
  platform_subtree     = try(local.platform_subtree_all[local.platform_branch_value], {})
  platform_extra_depth = try(local.platform_subtree.depth, 0)

  # Platform subdirectory path (from dynamic selections)
  platform_subdir_values = local.platform_extra_depth > 0 ? compact([
    for i in range(local.platform_extra_depth) :
    try(data.coder_parameter.platform_subdir[i].value, "")
  ]) : []
  platform_subdir_path = join("/", local.platform_subdir_values)

  # Constructed platform SVN URL
  platform_svn_url = "${local.platform_prefix}/${data.coder_parameter.platform_version.value}/${local.platform_branch_value}${local.platform_subdir_path != "" ? "/${local.platform_subdir_path}" : ""}"

  # Platform path completeness check
  platform_path_complete = local.platform_branch_value != "" && (
    local.platform_extra_depth == 0 ||
    try(data.coder_parameter.platform_subdir[local.platform_extra_depth - 1].value, "") != ""
  )

  # --- Public path state ---
  use_custom_public   = data.coder_parameter.custom_public_path.value == "true"
  public_branch_value = local.use_custom_public ? try(data.coder_parameter.public_branch[0].value, "") : ""
  public_is_trunk = local.use_custom_public ? (local.public_branch_value == "trunk") : local.platform_is_trunk

  # Pre-fetched subtree map for ALL branches under the selected public version
  public_subtree_all = try(jsondecode(data.external.public_subtree[0].result.data), {})

  # Server-side: subtree data for the actually-selected public branch
  public_subtree     = try(local.public_subtree_all[local.public_branch_value], {})
  public_extra_depth = try(local.public_subtree.depth, 0)

  # Public subdirectory path
  public_subdir_values = (local.use_custom_public && local.public_extra_depth > 0) ? compact([
    for i in range(local.public_extra_depth) :
    try(data.coder_parameter.public_subdir[i].value, "")
  ]) : []
  public_subdir_path = join("/", local.public_subdir_values)

  # Constructed public SVN URL (follows platform path when checkbox unchecked)
  public_svn_url = local.use_custom_public ? (
    "${local.public_prefix}/${try(data.coder_parameter.public_version[0].value, "")}/${local.public_branch_value}${local.public_subdir_path != "" ? "/${local.public_subdir_path}" : ""}"
  ) : (
    "${local.public_prefix}/${data.coder_parameter.platform_version.value}/${local.platform_branch_value}${local.platform_subdir_path != "" ? "/${local.platform_subdir_path}" : ""}"
  )

  # Public path completeness check
  public_path_complete = local.use_custom_public ? (
    local.public_branch_value != "" && (
      local.public_extra_depth == 0 ||
      try(data.coder_parameter.public_subdir[local.public_extra_depth - 1].value, "") != ""
    )
  ) : local.platform_path_complete
}

# =============================================================================
# Coder parameters: Platform SVN (cascading dropdowns)
# =============================================================================

# Platform version selection (e.g., V9R1, V7R1_SPRINGB75, ...)
data "coder_parameter" "platform_version" {
  name         = "platform_version"
  display_name = "Platform Version"
  description  = "Select the platform code version (top-level SVN directory)"
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f3e0.png"
  form_type    = "dropdown"
  default      = "V9R1"
  order        = 100
  mutable      = false

  dynamic "option" {
    for_each = keys(local.platform_svn_map)
    content {
      name  = option.value
      value = option.value
    }
  }
}

# Platform branch type selection (e.g., trunk, branches_bugfix, tags, ...)
data "coder_parameter" "platform_branch" {
  count = data.coder_parameter.platform_version.value != "" ? 1 : 0

  name         = "platform_branch"
  display_name = "Platform Branch"
  description  = "Select the branch type"
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f3e0.png"
  form_type    = "dropdown"
  default      = "trunk"
  order        = 101
  mutable      = false

  dynamic "option" {
    for_each = try(local.platform_svn_map[data.coder_parameter.platform_version.value], [])
    content {
      name  = option.value
      value = option.value
    }
  }
}

# Platform subdirectory levels (dynamic count based on actual SVN tree depth)
# For trunk: count=0 (no extra levels needed)
# For tags/bugfix/project/etc: count=N (detected by get-svn-subtree.sh)
#
# IMPORTANT: The count expression uses a conditional short-circuit so that
# during workspace tag parsing (when external data is unknown), the default
# branch "trunk" resolves to count=0 without touching the unknown external data.
# During actual plan and Coder UI re-evaluation, platform_subtree_all is a
# known constant map and the non-trunk branch resolves to the actual depth.
data "coder_parameter" "platform_subdir" {
  count = (
    try(data.coder_parameter.platform_branch[0].value, "trunk") == "trunk"
  ) ? 0 : try(
    local.platform_subtree_all[
      try(data.coder_parameter.platform_branch[0].value, "trunk")
    ]["depth"],
    0
  )

  name         = "platform_subdir_${count.index}"
  display_name = "Platform Subdirectory ${count.index + 1}"
  description  = "Select subdirectory level ${count.index + 1}"
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f3e0.png"
  form_type    = "dropdown"
  order        = 102 + count.index
  mutable      = false

  dynamic "option" {
    for_each = try(
      local.platform_subtree_all[
        try(data.coder_parameter.platform_branch[0].value, "trunk")
      ][
        count.index == 0
        ? "level_0"
        : "level_${count.index}__${join("__", [
          for i in range(count.index) :
          data.coder_parameter.platform_subdir[i].value
        ])}"
      ],
      []
    )
    content {
      name  = option.value
      value = option.value
    }
  }
}

# Platform folder list (multi-select from code-level directories)
data "coder_parameter" "project_platform_folder_list" {
  count = (
    length(data.external.platform_folders) > 0 &&
    length(try(jsondecode(data.external.platform_folders[0].result.data), [])) > 0
  ) ? 1 : 0

  name         = "project_platform_folder_list"
  display_name = "Platform Folder List"
  description  = <<-EOT
    Select the **code directories** to checkout from platform SVN.
    If you want to check out the **entire folder**, leave this field **empty**.
  EOT
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f3e0.png"
  form_type    = "multi-select"
  type         = "list(string)"
  default      = jsonencode([])
  order        = 110
  mutable      = true

  dynamic "option" {
    for_each = try(jsondecode(data.external.platform_folders[0].result.data), [])
    content {
      name  = option.value
      value = option.value
    }
  }
}

# =============================================================================
# Coder parameters: Public SVN (checkbox + conditional cascading)
# =============================================================================

# Checkbox: use a different branch path for public SVN
data "coder_parameter" "custom_public_path" {
  name         = "custom_public_path"
  display_name = "Custom Public Path"
  description  = "Check to select a **different** branch path for public SVN checkout (default: same as platform)"
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f310.png"
  type         = "bool"
  default      = "false"
  order        = 200
  mutable      = false
}

# Public version selection (only when custom path enabled)
# Uses direct parameter reference for count so the Coder UI can evaluate dynamically.
data "coder_parameter" "public_version" {
  count = data.coder_parameter.custom_public_path.value == "true" ? 1 : 0

  name         = "public_version"
  display_name = "Public Version"
  description  = "Select the public code version"
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f310.png"
  form_type    = "dropdown"
  default      = "V9R1"
  order        = 201
  mutable      = false

  dynamic "option" {
    for_each = keys(local.public_svn_map)
    content {
      name  = option.value
      value = option.value
    }
  }
}

# Public branch type selection (only when custom path enabled)
# Uses direct parameter references for count so the Coder UI can evaluate dynamically.
data "coder_parameter" "public_branch" {
  count = (
    data.coder_parameter.custom_public_path.value == "true" &&
    try(data.coder_parameter.public_version[0].value, "") != ""
  ) ? 1 : 0

  name         = "public_branch"
  display_name = "Public Branch"
  description  = "Select the branch type for public SVN"
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f310.png"
  form_type    = "dropdown"
  default      = "trunk"
  order        = 202
  mutable      = false

  dynamic "option" {
    for_each = try(local.public_svn_map[try(data.coder_parameter.public_version[0].value, "")], [])
    content {
      name  = option.value
      value = option.value
    }
  }
}

# Public subdirectory levels (dynamic count, only when custom path enabled)
# Uses the same conditional short-circuit pattern as platform_subdir to ensure
# workspace tag parsing succeeds (trunk defaults to count=0).
data "coder_parameter" "public_subdir" {
  count = (
    try(data.coder_parameter.public_branch[0].value, "trunk") == "trunk"
  ) ? 0 : try(
    local.public_subtree_all[
      try(data.coder_parameter.public_branch[0].value, "trunk")
    ]["depth"],
    0
  )

  name         = "public_subdir_${count.index}"
  display_name = "Public Subdirectory ${count.index + 1}"
  description  = "Select subdirectory level ${count.index + 1} for public SVN"
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f310.png"
  form_type    = "dropdown"
  order        = 203 + count.index
  mutable      = false

  dynamic "option" {
    for_each = try(
      local.public_subtree_all[
        try(data.coder_parameter.public_branch[0].value, "trunk")
      ][
        count.index == 0
        ? "level_0"
        : "level_${count.index}__${join("__", [
          for i in range(count.index) :
          data.coder_parameter.public_subdir[i].value
        ])}"
      ],
      []
    )
    content {
      name  = option.value
      value = option.value
    }
  }
}

# Public folder list (multi-select from code-level directories)
data "coder_parameter" "project_public_folder_list" {
  count = (
    length(data.external.public_folders) > 0 &&
    length(try(jsondecode(data.external.public_folders[0].result.data), [])) > 0
  ) ? 1 : 0

  name         = "project_public_folder_list"
  display_name = "Public Folder List"
  description  = <<-EOT
    Select the **code directories** to checkout from public SVN.
    Selecting `PUBLIC` is recommended for **symbol highlighting**.
    If you want to check out the **entire folder**, leave this field **empty**.
  EOT
  icon         = "${data.coder_workspace.me.access_url}/emojis/1f310.png"
  form_type    = "multi-select"
  type         = "list(string)"
  default      = jsonencode([])
  order        = 215
  mutable      = true

  dynamic "option" {
    for_each = try(jsondecode(data.external.public_folders[0].result.data), [])
    content {
      name  = option.value
      value = option.value
    }
  }
}

# =============================================================================
# Coder parameters: SVN credentials
# =============================================================================

data "coder_parameter" "svn_username" {
  name         = "svn_username"
  display_name = "SVN Username"
  description  = "Specify a SVN username to checkout codes"
  type         = "string"
  order        = 300
  mutable      = false
}

data "coder_parameter" "svn_password" {
  name         = "svn_password"
  display_name = "SVN Password"
  description  = "Specify a SVN password to checkout codes"
  type         = "string"
  order        = 301
  mutable      = true

  styling = jsonencode({
    mask_input = true
  })
}

# =============================================================================
# Coder agent
# =============================================================================

resource "coder_agent" "main" {
  arch = data.coder_provisioner.me.arch
  os   = "linux"

  env = {
    GIT_AUTHOR_NAME     = coalesce(data.coder_workspace_owner.me.full_name, data.coder_workspace_owner.me.name)
    GIT_AUTHOR_EMAIL    = "${data.coder_workspace_owner.me.email}"
    GIT_COMMITTER_NAME  = coalesce(data.coder_workspace_owner.me.full_name, data.coder_workspace_owner.me.name)
    GIT_COMMITTER_EMAIL = "${data.coder_workspace_owner.me.email}"
  }

  display_apps {
    port_forwarding_helper = true
    ssh_helper             = true
    vscode                 = false
    vscode_insiders        = false
    web_terminal           = true
  }

  metadata {
    key          = "cpu_usage"
    display_name = "CPU Usage"
    script       = "coder stat cpu"
    interval     = 10
    timeout      = 1
    order        = 0
  }
  metadata {
    key          = "ram_usage"
    display_name = "RAM Usage"
    script       = "coder stat mem"
    interval     = 10
    timeout      = 1
    order        = 1
  }
  metadata {
    key          = "code_server_version"
    display_name = "Code Server Version"
    script       = <<EOF
      #!/bin/bash
      if [ -f ${local.code_server_dir}/bin/code-server ]; then
        ${local.code_server_dir}/bin/code-server --version | head -n1 | cut -d " " -f1
      else
        echo unknown
      fi
    EOF
    interval     = 30
    timeout      = 1
    order        = 2
  }
  metadata {
    key          = "python_version"
    display_name = "Python Version"
    script       = <<EOF
      #!/bin/bash
      if command -v python3 >/dev/null 2>&1; then
        python3 --version | head -n1 | cut -d " " -f2
      else
        echo unknown
      fi
    EOF
    interval     = 30
    timeout      = 1
    order        = 3
  }
}

# =============================================================================
# Coder apps
# =============================================================================

resource "coder_app" "code_server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "Code Server"
  icon         = "/icon/code.svg"
  url          = "http://localhost:13337/?folder=${local.project_path}"
  subdomain    = true
  share        = "public"

  healthcheck {
    url       = "http://localhost:13337/healthz"
    interval  = 5
    threshold = 6
  }
}
resource "coder_app" "coder_docs" {
  agent_id     = coder_agent.main.id
  slug         = "coder-docs"
  display_name = "Coder Docs"
  icon         = "/emojis/1f4dd.png"
  url          = local.coder_docs_url
  external     = true
}
resource "coder_app" "coder_tutorials" {
  agent_id     = coder_agent.main.id
  slug         = "coder-tutorials"
  display_name = "Coder Tutorials"
  icon         = "/emojis/1f4d6.png"
  url          = local.coder_tutorials_url
  external     = true
}

# =============================================================================
# Coder environment variables
# =============================================================================

resource "coder_env" "coder_service_name" {
  agent_id = coder_agent.main.id
  name     = "CODER_SERVICE_NAME"
  value    = "coder-${data.coder_workspace_owner.me.name}-${lower(data.coder_workspace.me.name)}"
}
resource "coder_env" "extensions_gallery" {
  agent_id = coder_agent.main.id
  name     = "EXTENSIONS_GALLERY"
  value    = "{\"serviceUrl\":\"${local.marketplace_url}/api\", \"itemUrl\":\"${local.marketplace_url}/item\", \"resourceUrlTemplate\": \"${local.marketplace_url}/files/{publisher}/{name}/{version}/{path}\"}"
}
resource "coder_env" "node_extra_ca_certs" {
  agent_id = coder_agent.main.id
  name     = "NODE_EXTRA_CA_CERTS"
  value    = "/etc/ssl/certs/ca-certificates.crt"
}
resource "coder_env" "node_options" {
  agent_id = coder_agent.main.id
  name     = "NODE_OPTIONS"
  value    = "--max-old-space-size=16384"
}
resource "coder_env" "project_platform_folder_list" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PLATFORM_FOLDER_LIST"
  value    = try(data.coder_parameter.project_platform_folder_list[0].value, jsonencode([]))
}
resource "coder_env" "project_platform_path" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PLATFORM_PATH"
  value    = "${local.project_path}/platform"
}
resource "coder_env" "project_platform_svn" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PLATFORM_SVN"
  value    = local.platform_svn_url
}
resource "coder_env" "project_public_folder_list" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PUBLIC_FOLDER_LIST"
  value    = try(data.coder_parameter.project_public_folder_list[0].value, jsonencode([]))
}
resource "coder_env" "project_public_path" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PUBLIC_PATH"
  value    = "${local.project_path}/public"
}
resource "coder_env" "project_public_svn" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PUBLIC_SVN"
  value    = local.public_svn_url
}
resource "coder_env" "svn_password" {
  agent_id = coder_agent.main.id
  name     = "SVN_PASSWORD_B64"
  value    = base64encode(data.coder_parameter.svn_password.value)
}
resource "coder_env" "svn_username" {
  agent_id = coder_agent.main.id
  name     = "SVN_USERNAME"
  value    = "${data.coder_parameter.svn_username.value}"
}

# =============================================================================
# Coder scripts
# =============================================================================

resource "coder_script" "start_code_server" {
  agent_id           = coder_agent.main.id
  display_name       = "Start Code Server"
  icon               = "/icon/code.svg"
  run_on_start       = true
  start_blocks_login = true
  script             = <<EOF
    #!/bin/bash
    echo -e "\033[36m- Installing code-server\033[0m"
    mkdir -p ${local.code_server_dir}
    curl -fsSL "${local.assets_url}/code-server-4.102.3-linux-amd64.tar.gz" | tar -C "${local.code_server_dir}" -xz --strip-components 1

    echo -e "\033[36m- Installing extensions\033[0m"
    ${local.code_server_dir}/bin/code-server --install-extension "alefragnani.bookmarks" --force
    ${local.code_server_dir}/bin/code-server --install-extension "anjali.clipboard-history" --force
    ${local.code_server_dir}/bin/code-server --install-extension "beaugust.blamer-vs" --force
    ${local.code_server_dir}/bin/code-server --install-extension "bierner.markdown-mermaid" --force
    ${local.code_server_dir}/bin/code-server --install-extension "comware.comware-vscode" --force
    ${local.code_server_dir}/bin/code-server --install-extension "dbaeumer.vscode-eslint@prerelease" --force
    ${local.code_server_dir}/bin/code-server --install-extension "esbenp.prettier-vscode" --force
    ${local.code_server_dir}/bin/code-server --install-extension "h3c-rd.h3c-vscode-all-in-one" --force
    ${local.code_server_dir}/bin/code-server --install-extension "johnstoncode.svn-scm" --force
    ${local.code_server_dir}/bin/code-server --install-extension "ms-ceintl.vscode-language-pack-zh-hans" --force
    ${local.code_server_dir}/bin/code-server --install-extension "ms-python.debugpy@prerelease" --force
    ${local.code_server_dir}/bin/code-server --install-extension "ms-vscode.cpptools@prerelease" --force
    ${local.code_server_dir}/bin/code-server --install-extension "timonwong.shellcheck" --force
    ${local.code_server_dir}/bin/code-server --install-extension "redhat.vscode-xml@prerelease" --force
    ${local.code_server_dir}/bin/code-server --install-extension "rogalmic.bash-debug" --force
    ${local.code_server_dir}/bin/code-server --install-extension "rsbondi.highlight-words" --force

    echo -e "\033[36m- Starting code-server\033[0m"
    ${local.code_server_dir}/bin/code-server \
      --auth none \
      --disable-telemetry \
      --disable-update-check \
      --disable-workspace-trust \
      --locale zh-cn \
      --port 13337 \
      --trusted-origins * \
      >${local.code_server_dir}/main.log 2>&1 &
    echo -e "\033[32m- Code server started!\033[0m"
  EOF
}
resource "coder_script" "install_clangd" {
  agent_id           = coder_agent.main.id
  display_name       = "Install clangd"
  icon               = "/emojis/1f9e0.png"
  run_on_start       = true
  start_blocks_login = true
  script             = <<EOF
    #!/bin/bash
    if command -v clangd >/dev/null 2>&1; then
      echo -e "\033[32m- clangd is already installed\033[0m"
      exit 0
    fi
    echo -e "\033[36m- Installing clangd\033[0m"
    curl -fsSL "${local.assets_url}/clangd-linux-22.1.0.zip" -o /tmp/clangd-linux-22.1.0.zip \
      && cd /tmp \
      && unzip -q clangd-linux-22.1.0.zip \
      && rm clangd-linux-22.1.0.zip \
      && sudo mv clangd_22.1.0 /opt/clangd \
      && sudo ln -s /opt/clangd/bin/clangd /usr/local/bin/clangd
    echo -e "\033[32m- clangd installed!\033[0m"
  EOF
}
resource "coder_script" "checkout_base_svn" {
  agent_id           = coder_agent.main.id
  display_name       = "Checkout base SVN project"
  icon               = "/emojis/1f3e0.png"
  run_on_start       = true
  start_blocks_login = true
  script             = <<EOF
    #!/bin/bash
    checkout-list platform
  EOF
}
resource "coder_script" "checkout_public_svn" {
  agent_id           = coder_agent.main.id
  display_name       = "Checkout public SVN project"
  icon               = "/emojis/1f310.png"
  run_on_start       = true
  start_blocks_login = true
  script             = <<EOF
    #!/bin/bash
    checkout-list public
  EOF
}
resource "coder_script" "create_python_venv" {
  agent_id           = coder_agent.main.id
  display_name       = "Create Python Venv"
  icon               = "/icon/python.svg"
  run_on_start       = true
  start_blocks_login = true
  script             = <<EOF
    #!/bin/bash
    cd "${local.project_path}"
    python -m venv .venv --system-site-packages
    .venv/bin/pip install tree-sitter tree-sitter-c
  EOF
}

# =============================================================================
# Docker resources
# =============================================================================

resource "docker_service" "workspace" {
  name = "coder-${data.coder_workspace_owner.me.name}-${lower(data.coder_workspace.me.name)}"
  task_spec {
    container_spec {
      image = docker_registry_image.main.name

      labels {
        label = "coder.owner"
        value = data.coder_workspace_owner.me.name
      }
      labels {
        label = "coder.owner_id"
        value = data.coder_workspace_owner.me.id
      }
      labels {
        label = "coder.workspace_id"
        value = data.coder_workspace.me.id
      }
      labels {
        label = "coder.workspace_name"
        value = data.coder_workspace.me.name
      }

      command  = ["sh", "-c", replace(coder_agent.main.init_script, "/localhost|127\\.0\\.0\\.1/", "host.docker.internal")]
      hostname = lower(data.coder_workspace.me.name)

      env = {
        CODER_AGENT_TOKEN = "${coder_agent.main.token}"
      }

      hosts {
        host = "host.docker.internal"
        ip   = "host-gateway"
      }

      dns_config {
        nameservers = ["10.72.66.36", "10.72.66.37"]
      }

      mounts {
        target    = "/home/${data.coder_workspace_owner.me.name}"
        type      = "volume"
        read_only = false
        source    = docker_volume.home_volume.name
      }

      mounts {
        target    = "/opt/glibc-headers/include"
        type      = "bind"
        read_only = true
        source    = "/opt/glibc-headers/include"
      }

      mounts {
        target    = "/opt/open-headers/include"
        type      = "bind"
        read_only = true
        source    = "/opt/open-headers/V9R1/trunk/include"
      }
    }
  }
}

resource "docker_image" "main" {
  name = "registry.coder.h3c.com/coder-${data.coder_workspace.me.id}"
  build {
    context = "build"
    build_args = {
      USER              = data.coder_workspace_owner.me.name
      EXTENSION_VERSION = "1.99.2025040909"
    }
    force_remove = true
  }
  force_remove = true
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "build/**") : filesha1(f)]))
  }
}

resource "docker_volume" "home_volume" {
  name = "coder-${data.coder_workspace.me.id}-home"
  # Protect the volume from being deleted due to changes in attributes.
  lifecycle {
    ignore_changes = all
  }
}

resource "docker_registry_image" "main" {
  name                 = docker_image.main.name
  insecure_skip_verify = true
  keep_remotely        = false
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "build/**") : filesha1(f)]))
  }
}
