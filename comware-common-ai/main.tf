terraform {
  required_providers {
    coder = {
      source = "coder/coder"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.6.2"
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

  # --- Mode detection ---
  is_manual = data.coder_parameter.manual_svn_mode.value == "true"

  # --- Platform path state (cascading mode) ---
  # platform_version and platform_branch are hidden in manual mode (have count),
  # so use try([0].value, default) for safe access.
  platform_version_val = try(data.coder_parameter.platform_version[0].value, "V9R1")
  platform_branch_val  = try(data.coder_parameter.platform_branch[0].value, "trunk")
  platform_subdir_val  = try(data.coder_parameter.platform_subdir[0].value, "")

  # Constructed platform SVN URL (cascading mode)
  platform_svn_url_cascading = local.platform_branch_val == "trunk" ? join("/", compact([
    local.platform_prefix,
    local.platform_version_val,
    "trunk",
  ])) : join("/", compact([
    local.platform_prefix,
    local.platform_version_val,
    "branches_bugfix",
    local.platform_subdir_val,
  ]))

  # --- Public path state (cascading mode) ---
  # custom_public_path has NO count (always visible), so use .value directly
  use_custom_public   = data.coder_parameter.custom_public_path.value == "true"
  public_version_val  = try(data.coder_parameter.public_version[0].value, "")
  public_branch_val   = try(data.coder_parameter.public_branch[0].value, "trunk")
  public_subdir_val   = try(data.coder_parameter.public_subdir[0].value, "")

  # Constructed public SVN URL (cascading mode)
  # When custom_public_path is unchecked, follows platform path
  public_svn_url_cascading = local.use_custom_public ? (
    local.public_branch_val == "trunk" ? join("/", compact([
      local.public_prefix,
      local.public_version_val,
      "trunk",
    ])) : join("/", compact([
      local.public_prefix,
      local.public_version_val,
      "branches_bugfix",
      local.public_subdir_val,
    ]))
  ) : replace(local.platform_svn_url_cascading, local.platform_prefix, local.public_prefix)

  # --- Manual mode paths ---
  manual_platform_path_val = try(data.coder_parameter.manual_platform_path[0].value, "")
  manual_public_path_val   = try(data.coder_parameter.manual_public_path[0].value, "")

  # Manual SVN URLs
  platform_svn_url_manual = "${local.platform_prefix}/${local.manual_platform_path_val}"
  public_svn_url_manual = local.manual_public_path_val != "" ? (
    "${local.public_prefix}/${local.manual_public_path_val}"
  ) : replace(local.platform_svn_url_manual, local.platform_prefix, local.public_prefix)

  # --- Final computed URLs (mode-dependent) ---
  platform_svn_url = local.is_manual ? local.platform_svn_url_manual : local.platform_svn_url_cascading
  public_svn_url   = local.is_manual ? local.public_svn_url_manual : local.public_svn_url_cascading

  # --- Final folder lists ---
  platform_folder_list = data.coder_parameter.project_platform_folder_list.value
  public_folder_list   = data.coder_parameter.project_public_folder_list.value
}

# =============================================================================
# Coder parameters: Manual SVN mode toggle
# =============================================================================

data "coder_parameter" "manual_svn_mode" {
  name         = "manual_svn_mode"
  display_name = "Manual SVN Mode"
  description  = "Check to type SVN paths manually instead of using cascading dropdowns"
  icon         = "/emojis/270b.png"
  type         = "bool"
  default      = "false"
  order        = 1
  mutable      = false
}

# =============================================================================
# Coder parameters: Platform SVN (cascading dropdowns, hidden in manual mode)
# =============================================================================


# Manual platform path (e.g., "V9R1/branches_bugfix/COMWAREV900R001trunk/TB202601071176")
data "coder_parameter" "manual_platform_path" {
  count = data.coder_parameter.manual_svn_mode.value == "true" ? 1 : 0

  name         = "manual_platform_path"
  display_name = "Platform SVN Path"
  description  = "Type the platform SVN path relative to the repo root (e.g., `V9R1/trunk` or `V9R1/branches_bugfix/COMWAREV900R001trunk/TB202601071176`)"
  icon         = "/emojis/1f3e0.png"
  type         = "string"
  default      = "V9R1/trunk"
  order        = 100
  mutable      = false
}

# Platform version: static dropdown with 3 hardcoded options (DP-compatible).
# Hidden in manual mode — downstream references use try([0].value, default).
data "coder_parameter" "platform_version" {
  count = data.coder_parameter.manual_svn_mode.value == "true" ? 0 : 1

  name         = "platform_version"
  display_name = "Platform Version"
  description  = "Select the platform code version"
  icon         = "/emojis/1f3e0.png"
  form_type    = "dropdown"
  default      = "V9R1"
  order        = 101
  mutable      = false

  option {
    name  = "V9R1"
    value = "V9R1"
  }
  option {
    name  = "V7R1_SPRINGB64"
    value = "V7R1_SPRINGB64"
  }
  option {
    name  = "V7R1_SPRINGB75"
    value = "V7R1_SPRINGB75"
  }
}

# Platform branch: static dropdown with 2 options (DP-compatible).
# Hidden in manual mode — downstream references use try([0].value, default).
data "coder_parameter" "platform_branch" {
  count = data.coder_parameter.manual_svn_mode.value == "true" ? 0 : 1

  name         = "platform_branch"
  display_name = "Platform Branch"
  description  = "Select the branch type"
  icon         = "/emojis/1f3e0.png"
  form_type    = "dropdown"
  default      = "trunk"
  order        = 102
  mutable      = false

  option {
    name  = "trunk"
    value = "trunk"
  }
  option {
    name  = "branches_bugfix"
    value = "branches_bugfix"
  }
}

# Platform bugfix subdirectory: text input shown only when branch = branches_bugfix.
# User types the path manually (e.g., "COMWAREV900R001trunk/TB202601071176").
# References platform_branch via try(.value) since platform_branch has count.
data "coder_parameter" "platform_subdir" {
  count = (
    data.coder_parameter.manual_svn_mode.value != "true" &&
    try(data.coder_parameter.platform_branch.value, "trunk") == "branches_bugfix"
  ) ? 1 : 0

  name         = "platform_subdir"
  display_name = "Platform Bugfix Path"
  description  = "Type the path under `branches_bugfix/` (e.g., `COMWAREV900R001trunk/TB202601071176`)"
  icon         = "/emojis/1f3e0.png"
  type         = "string"
  order        = 103
  mutable      = false
}

# Platform folder list: tag-select for user to type folder names.
data "coder_parameter" "project_platform_folder_list" {
  name         = "project_platform_folder_list"
  display_name = "Platform Folder List"
  description  = <<-EOT
    Type the **code directories** to checkout from platform SVN.
    If you want to check out the **entire folder**, leave this field **empty**.
  EOT
  icon         = "/emojis/1f3e0.png"
  form_type    = "tag-select"
  type         = "list(string)"
  default      = jsonencode([])
  order        = 104
  mutable      = true
}

# =============================================================================
# Coder parameters: Public SVN (checkbox + conditional cascading)
# =============================================================================

# Checkbox: use a different branch path for public SVN (hidden in manual mode)
# NO count — always visible so that downstream public_version, public_branch,
# public_subdir can reference .value without [0] indexing.
data "coder_parameter" "custom_public_path" {
  name         = "custom_public_path"
  display_name = "Custom Public Path"
  description  = "Check to select a **different** branch path for public SVN checkout (default: same as platform)"
  icon         = "/emojis/270b.png"
  type         = "bool"
  default      = "false"
  order        = 200
  mutable      = false
}

# Manual public path (shown only in manual mode with custom public path enabled)
data "coder_parameter" "manual_public_path" {
  count = (
    data.coder_parameter.manual_svn_mode.value == "true" &&
    data.coder_parameter.custom_public_path.value == "true"
  ) ? 1 : 0

  name         = "manual_public_path"
  display_name = "Public SVN Path"
  description  = "Type the public SVN path (leave **empty** to use the same path as platform)"
  icon         = "/emojis/1f310.png"
  type         = "string"
  default      = ""
  order        = 201
  mutable      = false
}

# Public version: static dropdown (only when custom path enabled)
# References custom_public_path.value directly (no [0]) since it has no count.
data "coder_parameter" "public_version" {
  count = (
    data.coder_parameter.manual_svn_mode.value != "true" &&
    data.coder_parameter.custom_public_path.value == "true"
  ) ? 1 : 0

  name         = "public_version"
  display_name = "Public Version"
  description  = "Select the public code version"
  icon         = "/emojis/1f310.png"
  form_type    = "dropdown"
  default      = "V9R1"
  order        = 202
  mutable      = false

  option {
    name  = "V9R1"
    value = "V9R1"
  }
  option {
    name  = "V7R1_SPRINGB64"
    value = "V7R1_SPRINGB64"
  }
  option {
    name  = "V7R1_SPRINGB75"
    value = "V7R1_SPRINGB75"
  }
}

# Public branch: static dropdown (only when custom path enabled)
# References custom_public_path.value directly (no [0]) since it has no count.
data "coder_parameter" "public_branch" {
  count = (
    data.coder_parameter.manual_svn_mode.value != "true" &&
    data.coder_parameter.custom_public_path.value == "true"
  ) ? 1 : 0

  name         = "public_branch"
  display_name = "Public Branch"
  description  = "Select the branch type for public SVN"
  icon         = "/emojis/1f310.png"
  form_type    = "dropdown"
  default      = "trunk"
  order        = 203
  mutable      = false

  option {
    name  = "trunk"
    value = "trunk"
  }
  option {
    name  = "branches_bugfix"
    value = "branches_bugfix"
  }
}

# Public bugfix subdirectory: text input (only when custom path + branches_bugfix).
# References public_branch via try(.value) since public_branch has count.
data "coder_parameter" "public_subdir" {
  count = (
    data.coder_parameter.manual_svn_mode.value != "true" &&
    data.coder_parameter.custom_public_path.value == "true" &&
    try(data.coder_parameter.public_branch.value, "trunk") == "branches_bugfix"
  ) ? 1 : 0

  name         = "public_subdir"
  display_name = "Public Bugfix Path"
  description  = "Type the path under `branches_bugfix/` for public SVN (leave **empty** if branch is trunk)"
  icon         = "/emojis/1f310.png"
  type         = "string"
  order        = 204
  mutable      = false
}

# Public folder list: tag-select.
data "coder_parameter" "project_public_folder_list" {
  name         = "project_public_folder_list"
  display_name = "Public Folder List"
  description  = <<-EOT
    Type the **code directories** to checkout from public SVN.
    Typing `PUBLIC/include` is recommended for **symbol highlighting**.
    If you want to check out the **entire folder**, leave this field **empty**.
  EOT
  icon         = "/emojis/1f310.png"
  form_type    = "tag-select"
  type         = "list(string)"
  default      = jsonencode(["PUBLIC/include"])
  order        = 205
  mutable      = true
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
  value    = local.platform_folder_list
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
  value    = local.public_folder_list
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
