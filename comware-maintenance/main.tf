terraform {
  required_providers {
    coder = {
      source  = "coder/coder"
    }
    docker = {
      source  = "kreuzwerker/docker"
    }
  }
}

provider "docker" {
  registry_auth {
    address = "registry.coder-open.h3c.com"
    username = "coder"
    password = "silly"
  }
}
provider "coder" {
}

data "external" "press_map" {
  program = ["bash", "${path.module}/get-press-json.sh"]
  
  query = {
    svn_password = "Zpr758258%"
    svn_username = "z11187"
  }
}

locals {
  assets_url = "https://assets.coder-open.h3c.com"
  coder_tutorials_url = "https://tutorials.coder-open.h3c.com"
  local_code_server_version = "4.108.2"
  press_map = jsondecode(data.external.press_map.result.data)
  proxy_url = "http://172.22.0.29:8080"
  username = data.coder_workspace_owner.me.name
  workspace = data.coder_workspace.me.name
}

data "coder_provisioner" "me" {
}
data "coder_workspace" "me" {
}
data "coder_workspace_owner" "me" {
}

data "coder_parameter" "press_document_version" {
  name = "press_document_version"
  display_name = "Press Document Version"
  description = "Select the version of the press document"
  default = "V9 press"
  form_type = "dropdown"
  order = 3
  mutable = true

  option {
    name = "V9"
    value = "V9 press"
  } 
  option {
    name = "B75"
    value = "B75 press"
  }
  option {
    name = "B70"
    value = "B70 press"
  }
  option {
    name = "B64"
    value = "B64 press"
  }
}
data "coder_parameter" "press_document_category" {
  name = "press_document_category"
  display_name = "Press Document Category"
  description = "Select the category of the press document"
  form_type = "multi-select"
  type = "list(string)"
  default = jsonencode([])
  order = 4
  mutable = true

  dynamic "option" {
    for_each = keys(local.press_map[data.coder_parameter.press_document_version.value])
    content {
      name  = option.value
      value = option.value
    }
  }
}
data "coder_parameter" "press_document_details" {
  count = length(jsondecode(data.coder_parameter.press_document_category.value))
  name = "press_document_details_${count.index}"
  display_name = "[${jsondecode(data.coder_parameter.press_document_category.value)[count.index]}] Press Document Details"
  description = "Select the details of the press document '${jsondecode(data.coder_parameter.press_document_category.value)[count.index]}'"
  form_type = "multi-select"
  type = "list(string)"
  default = jsonencode([])
  order = 5 + count.index
  mutable = true

  dynamic "option" {
    for_each = try(local.press_map[data.coder_parameter.press_document_version.value][jsondecode(data.coder_parameter.press_document_category.value)[count.index]], [""])
    content {
      name  = option.value
      value = option.value
    }
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
    HTTP_PROXY         = "${local.proxy_url}"
    HTTPS_PROXY        = "${local.proxy_url}"
    FTP_PROXY          = "${local.proxy_url}"
    NO_PROXY           = "localhost,10.0.0.0/8"
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
    order = 0
  }
  metadata {
    key          = "ram_usage"
    display_name = "RAM Usage"
    script       = "coder stat mem"
    interval     = 10
    timeout      = 1
    order = 1
  }
  metadata {
    key          = "code_server_version"
    display_name = "Code Server Version"
    script       = <<EOF
      #!/bin/bash
      if [ -f /usr/bin/code-server ]; then
        code-server --version | head -n1 | cut -d " " -f1
      else
        echo unknown
      fi
    EOF
    interval     = 30
    order        = 2
  }
}

resource "coder_app" "code_server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "Code Server"
  icon         = "/icon/coder.svg"
  url          = "http://localhost:13337/?folder=/home/${local.username}/project"
  subdomain    = true
  share        = "public"

  healthcheck {
    url       = "http://localhost:13337/healthz"
    interval  = 5
    threshold = 6
  }
}
resource "coder_app" "coder_tutorials" {
  agent_id     = coder_agent.main.id
  slug         = "coder-tutorials"
  display_name = "Coder Tutorials"
  icon         = "/emojis/1f4d6.png"
  url          = local.coder_tutorials_url
  external     = true
}
resource "coder_app" "get_workspace_id" {
  agent_id     = coder_agent.main.id
  slug         = "get-workspace-id"
  display_name = "Get workspace ID"
  icon         = "${data.coder_workspace.me.access_url}/icon/widgets.svg"
  command      = "echo \"Workspace ID:\" && echo ${data.coder_workspace.me.id} && zsh"
}

resource "coder_env" "http_proxy" {
  agent_id = coder_agent.main.id
  name     = "HTTP_PROXY"
  value    = "${local.proxy_url}"
}
resource "coder_env" "https_proxy" {
  agent_id = coder_agent.main.id
  name     = "HTTPS_PROXY"
  value    = "${local.proxy_url}"
}
resource "coder_env" "ftp_proxy" {
  agent_id = coder_agent.main.id
  name     = "FTP_PROXY"
  value    = "${local.proxy_url}"
}
resource "coder_env" "no_proxy" {
  agent_id = coder_agent.main.id
  name     = "NO_PROXY"
  value    = "localhost,10.0.0.0/8"
}
resource "coder_env" "node_extra_ca_certs" {
  agent_id = coder_agent.main.id
  name     = "NODE_EXTRA_CA_CERTS"
  value    = "/etc/ssl/certs/ca-certificates.crt"
}
resource "coder_env" "project_base_dir" {
  agent_id = coder_agent.main.id
  name     = "PROJECT_BASE_DIR"
  value    = "/home/${local.username}/project"
}

resource "coder_script" "start_code_server" {
  agent_id     = coder_agent.main.id
  display_name = "Start Code Server"
  icon         = "/icon/code.svg"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    echo -e "\033[36m- 📦 Installing code-server v${local.local_code_server_version}\033[0m"
    wget "${local.assets_url}/code-server_${local.local_code_server_version}_amd64.deb" -O /tmp/code-server.deb
    sudo dpkg -i /tmp/code-server.deb

    echo -e "\033[36m- Copying host extensions to user directory...\033[0m"
    cp -r /opt/coder/code-server/extensions "/home/${local.username}/.local/share/code-server/extensions"

    code-server \
    --auth none \
    --disable-workspace-trust \
    --locale zh-cn \
    --port 13337 \
    --trusted-origins * \
    >/home/${local.username}/.local/share/code-server/main.log 2>&1 &

    echo -e "\033[32m- ✔️ Code server started!\033[0m"
  EOF
}
resource "coder_script" "create_project_folders" {
  agent_id     = coder_agent.main.id
  display_name = "Create Project Folders"
  icon         = "/emojis/1f3e0.png"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash

    cd /home/${local.username}/project
    mkdir -p ./报文抓包
    mkdir -p ./设备配置
    mkdir -p ./设备日志
    mkdir -p ./网络拓扑
    mkdir -p ./问题描述
    mkdir -p ./press

    press_version="${data.coder_parameter.press_document_version.value}"
    press_category_list=$(echo "${try(data.coder_parameter.press_document_category.value, jsonencode([]))}" | tr -d '[]"')
    press_details_list=$(echo "${join(";", [for d in data.coder_parameter.press_document_details : join(",", jsondecode(d.value))])}")
    echo "press_version: $${press_version}"
    echo "press_category_list: $${press_category_list}"
    echo "press_details_list: $${press_details_list}"
    get-press-files --version "$${press_version}" --categories "$${press_category_list}" --details "$${press_details_list}"

    get-skill-files
  EOF
}
resource "coder_script" "install_oh_my_zsh" {
  agent_id     = coder_agent.main.id
  display_name = "Install Oh My Zsh"
  icon         = "/icon/terminal.svg"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    if [ -d "/home/${local.username}/.oh-my-zsh" ]; then
      echo -e "\033[36m- Oh My Zsh is already installed.\033[0m"
      exit 0
    fi
    bash -c "$(curl -fsSL https://install.ohmyz.sh)" "" --unattended;
  EOF
}
resource "coder_script" "write_assets" {
  agent_id     = coder_agent.main.id
  display_name = "Write Assets to Container"
  icon         = "/emojis/1f4c4.png"
  run_on_start = true
  start_blocks_login = false
  script = <<EOF
    #!/bin/bash

    cd /home/${local.username}

    echo -e "\033[36m- 📄 Writing '~/project/CLAUDE.md'...\033[0m"
    echo "${filebase64("${path.module}/assets/project/CLAUDE.md")}" | base64 -d > ./project/CLAUDE.md

    echo -e "\033[32m- ✔️ Assets written successfully!\033[0m"
  EOF
}
resource "coder_script" "copy_time_master_statistics" {
  agent_id     = coder_agent.main.id
  display_name = "Copy Time Master Statistics"
  icon         = "/emojis/1f3e0.png"
  cron         = "0 0 * * * *"
  run_on_stop = true
  script = <<EOF
    #!/bin/bash
    copy-time-master-statistics
  EOF
}

resource "docker_service" "workspace" {
  count = data.coder_workspace.me.start_count
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
          read_only = false
          source    = docker_volume.home_volume.name
          target    = "/home/${local.username}"
          type      = "volume"
      }
      mounts {
        read_only = true
        source    = "/opt/coder/code-server/extensions"
        target    = "/opt/coder/code-server/extensions"
        type      = "bind"
      }
      mounts {
        read_only = false
        source    = "/opt/coder/statistics/build"
        target    = "/opt/coder/statistics/build"
        type      = "bind"
      }
    }
  }
}

resource "docker_image" "main" {
  name = "registry.coder-open.h3c.com/coder-${data.coder_workspace.me.id}"
  build {
    context = "build"
    build_args = {
      EXTENSION_VERSION = "1.104.0"
      PROXY_URL = "${local.proxy_url}"
      USER = "${local.username}"
    }
    force_remove = true
  }
  force_remove = true
  triggers = {
    dir_sha1 = sha1(join("", concat(
      [for f in fileset(path.module, "build/**") : filesha1("${path.module}/${f}")],
      [for f in fileset(path.module, "build/_*/**") : filesha1("${path.module}/${f}")],
      [for f in fileset(path.module, "build/**/.*") : filesha1("${path.module}/${f}")],
      [for f in fileset(path.module, "build/**/_*") : filesha1("${path.module}/${f}")]
    )))
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
  name = docker_image.main.name
  insecure_skip_verify  = true
  keep_remotely = false
  triggers  = {
    dir_sha1 = sha1(join("", concat(
      [for f in fileset(path.module, "build/**") : filesha1("${path.module}/${f}")],
      [for f in fileset(path.module, "build/_*/**") : filesha1("${path.module}/${f}")],
      [for f in fileset(path.module, "build/**/.*") : filesha1("${path.module}/${f}")],
      [for f in fileset(path.module, "build/**/_*") : filesha1("${path.module}/${f}")]
    )))
  }
}
