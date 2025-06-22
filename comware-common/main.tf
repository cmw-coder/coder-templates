terraform {
  required_providers {
    coder = {
      source  = "coder/coder"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.3.0"
    }
  }
}

provider "docker" {
  registry_auth {
    address = "registry.coder.h3c.com"
    username = "coder"
    password = "silly"
  }
}

provider "coder" {
}

data "coder_parameter" "project_base_svn" {
  name          = "project_base_svn"
  display_name  = "Project base SVN"
  description   = "Please provide the **base project branch** SVN URL for checkout."
  icon          = "${data.coder_workspace.me.access_url}/emojis/1f3e0.png"
  order         = 0
  type          = "string"
  mutable       = false
  default       = "http://10.153.120.80/cmwcode-open/V9R1/trunk"
}
data "coder_parameter" "project_base_folder_list" {
  name          = "project_base_folder_list"
  display_name  = "Project base folder list"
  description   = <<-EOT
    Please provide a list of **folder paths** for `Project base SVN` to checkout.\
    If you want to check out the **entire project**, leave this field **empty**.
  EOT
  icon          = "${data.coder_workspace.me.access_url}/emojis/1f3e0.png"
  order         = 1
  type          = "list(string)"
  mutable       = false
  default       = jsonencode([])
}
data "coder_parameter" "project_public_svn" {
  name          = "project_public_svn"
  display_name  = "Project public SVN"
  description   = <<-EOT
    Please provide the **base public** SVN URL for `Project Base SVN`.\
    If you want to **skip** checking out the public folder, leave this field **empty**.
  EOT
  icon          = "${data.coder_workspace.me.access_url}/emojis/1f310.png"
  order         = 2
  type          = "string"
  mutable       = false
  default       = "http://10.153.120.104/cmwcode-public/V9R1/trunk/PUBLIC"
}
data "coder_parameter" "project_public_folder_list" {
  name          = "project_public_folder_list"
  display_name  = "Public SVN List"
  description   = <<-EOT
    Please provide a list of **folder paths** for `Project public SVN` to checkout.\
    Including the `include` folder is recommended for **symbol highlighting**.\
    If you want to check out the **entire public folder**, leave this field **empty**.
  EOT
  icon          = "${data.coder_workspace.me.access_url}/emojis/1f310.png"
  order         = 3
  type          = "list(string)"
  mutable       = false
  default       = jsonencode([
    "include",
    "proto",
    "xsd",
    "yang",
  ])
}
data "coder_parameter" "svn_username" {
  name          = "svn_username"
  display_name  = "SVN username"
  order         = 4
  description   = "Specify a SVN username to checkout codes"
  type          = "string"
  mutable       = false
}
data "coder_parameter" "svn_password" {
  name          = "svn_password"
  display_name  = "SVN password"
  order         = 5
  description   = "Specify a SVN password to checkout codes"
  type          = "string"
  mutable       = false
}
data "coder_provisioner" "me" {
}
data "coder_workspace" "me" {
}
data "coder_workspace_owner" "me" {
}

locals {
  assets_url = "https://coder-assets.cmwcoder.h3c.com"
  code_server_dir = "/tmp/code-server"
  coder_docs_url = "https://coder-docs.cmwcoder.h3c.com"
  coder_tutorials_url = "https://tutorials.coder.h3c.com"
  docker_image = "127.0.0.1:5000/comware-common:1"
  marketplace_url = "https://code-marketplace.cmwcoder.h3c.com"
  project_path = "/home/${data.coder_workspace_owner.me.name}/project"
  username = data.coder_workspace_owner.me.name
  workspace = data.coder_workspace.me.name
  yunxiao = {
    organization_id = "864f6de3-3d59-46f2-9729-645fc20006b7"
  }
}

resource "coder_agent" "main" {
  arch                   = data.coder_provisioner.me.arch
  os                     = "linux"

  env = {
    GIT_AUTHOR_NAME     = coalesce(data.coder_workspace_owner.me.full_name, local.username)
    GIT_AUTHOR_EMAIL    = "${data.coder_workspace_owner.me.email}"
    GIT_COMMITTER_NAME  = coalesce(data.coder_workspace_owner.me.full_name, local.username)
    GIT_COMMITTER_EMAIL = "${data.coder_workspace_owner.me.email}"
  }

  display_apps {
    port_forwarding_helper = true
    ssh_helper = true
    vscode = false
    vscode_insiders = false
    web_terminal = true
  }

  metadata {
    key          = "cpu_usage"
    display_name = "CPU Usage"
    script       = "coder stat cpu"
    interval     = 10
    timeout      = 1
    order       = 0
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
    order        = 3
  }
}

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


resource "coder_env" "coder_workspace" {
  agent_id = coder_agent.main.id
  name     = "CODER_WORKSPACE"
  value    = "${local.workspace}"
}
resource "coder_env" "extensions_gallery" {
  agent_id = coder_agent.main.id
  name     = "EXTENSIONS_GALLERY"
  value    = "{\"serviceUrl\":\"${local.marketplace_url}/api\", \"itemUrl\":\"${local.marketplace_url}/item\", \"resourceUrlTemplate\": \"${local.marketplace_url}/files/{publisher}/{name}/{version}/{path}\"}"
}
resource "coder_env" "lingma_organization_id" {
  agent_id = coder_agent.main.id
  name     = "LINGMA_ORGANIZATION_ID"
  value    = "${local.yunxiao.organization_id}"
}
resource "coder_env" "lingma_username" {
  agent_id = coder_agent.main.id
  name     = "LINGMA_USERNAME"
  value    = "${local.username}"
}
resource "coder_env" "node_extra_ca_certs" {
  agent_id = coder_agent.main.id
  name     = "NODE_EXTRA_CA_CERTS"
  value    = "/etc/ssl/certs/ca-certificates.crt"
}
resource "coder_env" "project_base_folder_list" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_BASE_FOLDER_LIST"
  value    = "${data.coder_parameter.project_base_folder_list.value}"
}
resource "coder_env" "project_path" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_BASE_PATH"
  value    = "${local.project_path}/open"
}
resource "coder_env" "project_base_svn" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_BASE_SVN"
  value    = "${data.coder_parameter.project_base_svn.value}"
}
resource "coder_env" "project_public_folder_list" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PUBLIC_FOLDER_LIST"
  value    = "${data.coder_parameter.project_public_folder_list.value}"
}
resource "coder_env" "project_public_path" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PUBLIC_PATH"
  value    = "${local.project_path}/public"
}
resource "coder_env" "project_public_svn" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_PUBLIC_SVN"
  value    = "${data.coder_parameter.project_public_svn.value}"
}
resource "coder_env" "svn_username" {
  agent_id = coder_agent.main.id
  name     = "SVN_USERNAME"
  value    = "${data.coder_parameter.svn_username.value}"
}
resource "coder_env" "svn_password" {
  agent_id = coder_agent.main.id
  name     = "SVN_PASSWORD"
  value    = "${data.coder_parameter.svn_password.value}"
}

resource "coder_script" "start_code_server" {
  agent_id     = coder_agent.main.id
  display_name = "Start Code Server"
  icon         = "/icon/code.svg"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    echo -e "\033[36m- 📦 Installing code-server\033[0m"
    mkdir -p ${local.code_server_dir}
    curl -fsSL "${local.assets_url}/code-server-4.99.1-linux-amd64.tar.gz" | tar -C "${local.code_server_dir}" -xz --strip-components 1

    echo -e "\033[36m- ⏳ Installing extensions\033[0m"
    ${local.code_server_dir}/bin/code-server --install-extension --force "alefragnani.bookmarks"
    ${local.code_server_dir}/bin/code-server --install-extension --force "Alibaba-Cloud.tongyi-lingma-onpremise"
    ${local.code_server_dir}/bin/code-server --install-extension --force "anjali.clipboard-history"
    ${local.code_server_dir}/bin/code-server --install-extension --force "beaugust.blamer-vs"
    ${local.code_server_dir}/bin/code-server --install-extension --force "bierner.markdown-mermaid"
    ${local.code_server_dir}/bin/code-server --install-extension --force "dbaeumer.vscode-eslint@prerelease"
    ${local.code_server_dir}/bin/code-server --install-extension --force "esbenp.prettier-vscode"
    ${local.code_server_dir}/bin/code-server --install-extension --force "johnstoncode.svn-scm"
    ${local.code_server_dir}/bin/code-server --install-extension --force "ms-ceintl.vscode-language-pack-zh-hans"
    ${local.code_server_dir}/bin/code-server --install-extension --force "ms-python.debugpy@prerelease"
    ${local.code_server_dir}/bin/code-server --install-extension --force "ms-vscode.cpptools@prerelease"
    ${local.code_server_dir}/bin/code-server --install-extension --force "timonwong.shellcheck"
    ${local.code_server_dir}/bin/code-server --install-extension --force "rangav.vscode-thunder-client"
    ${local.code_server_dir}/bin/code-server --install-extension --force "redhat.vscode-xml@prerelease"
    ${local.code_server_dir}/bin/code-server --install-extension --force "rsbondi.highlight-words"

    echo -e "\033[36m- ⏳ Starting code-server\033[0m"
    ${local.code_server_dir}/bin/code-server \
      --auth none \
      --disable-telemetry \
      --disable-update-check \
      --disable-workspace-trust \
      --locale zh-cn \
      --port 13337 \
      --trusted-origins * \
      >${local.code_server_dir}/main.log 2>&1 &
    echo -e "\033[32m- ✔️ Code server started!\033[0m"
  EOF
}
resource "coder_script" "checkout_base_svn" {
  agent_id     = coder_agent.main.id
  display_name = "Checkout base SVN project"
  icon         = "/emojis/1f3e0.png"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    if [ ! -d "${local.project_path}/open" ]; then
      svn-co "${data.coder_parameter.project_base_svn.value}" \
        "${data.coder_parameter.project_base_folder_list.value}" \
        "${local.project_path}/open" \
        "${data.coder_parameter.svn_username.value}" \
        "${data.coder_parameter.svn_password.value}"
    fi
  EOF
}
resource "coder_script" "checkout_public_svn" {
  agent_id     = coder_agent.main.id
  display_name = "Checkout public SVN project"
  icon         = "/emojis/1f310.png"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    if [ ! -d "${local.project_path}/public" ] && [ -n "${data.coder_parameter.project_public_svn.value}" ]; then
      svn-co "${data.coder_parameter.project_public_svn.value}" \
        "${data.coder_parameter.project_public_folder_list.value}" \
        "${local.project_path}/public" \
        "${data.coder_parameter.svn_username.value}" \
        "${data.coder_parameter.svn_password.value}"
    fi
  EOF
}

resource "docker_service" "workspace" {
  name = "coder-${local.username}-${lower(local.workspace)}"
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

      command = ["sh", "-c", replace(coder_agent.main.init_script, "/localhost|127\\.0\\.0\\.1/", "host.docker.internal")]
      hostname = lower(local.workspace)

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
        target    = "/home/${local.username}"
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

resource "docker_registry_image" "main" {
  name = docker_image.main.name
  insecure_skip_verify  = true
  triggers              = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "build/*") : filesha1(f)]))
  }
}

resource "docker_image" "main" {
  name = "registry.coder.h3c.com/coder-${data.coder_workspace.me.id}"
  build {
    context = "build"
    build_args = {
      USER = local.username
      EXTENSION_VERSION = "1.99.2025040909"
    }
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.module, "build/*") : filesha1(f)]))
  }
}

resource "docker_volume" "home_volume" {
  name = "coder-${data.coder_workspace.me.id}-home"
  # Protect the volume from being deleted due to changes in attributes.
  lifecycle {
    ignore_changes = all
  }
}
