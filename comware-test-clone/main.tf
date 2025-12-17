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
}

provider "coder" {
}

locals {
  coder_tutorials_url = "https://tutorials.coder-open.h3c.com"
  local_code_server_version = "4.105.1"
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

data "coder_parameter" "coder_workspace_id" {
  name          = "coder_workspace_id"
  display_name  = "Coder Workspace ID"
  order         = 1
  description   = "Specify a Coder workspace ID to clone workspace from."
  type          = "string"
  mutable       = false
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
    NO_PROXY           = "localhost"
  }

  display_apps {
    port_forwarding_helper = true
    ssh_helper = true
    vscode = true
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
  value    = "localhost"
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
    sudo dpkg -i /opt/coder/assets/code-server.deb

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

    mkdir -p /home/${local.username}/project    
    cp -a /opt/coder/home-clone/project/. /home/${local.username}/project

    mkdir -p /home/${local.username}/.claude
    cp -r /opt/coder/home-clone/.claude/* /home/${local.username}/.claude/
  EOF
}

resource "coder_script" "init_python_venv" {
  agent_id     = coder_agent.main.id
  display_name = "Init Python Virtual Environment"
  icon         = "/emojis/1f3e0.png"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    set -euo pipefail

    rm -rf /home/${local.username}/project/.venv

    LOCAL_VENV_PATH="/home/${local.username}/project/.venv"
    SHARED_VENV_PATH="/opt/coder/venvs/comware-test"
    SYNC_MARKER="$LOCAL_VENV_PATH/.shared_venv_synced"
    FORCE_REFRESH="$${FORCE_SHARED_VENV_SYNC:-false}"

    if [ ! -d "$SHARED_VENV_PATH" ]; then
      echo -e "\033[31m- Shared venv $SHARED_VENV_PATH not found, please verify host setup.\033[0m"
      exit 1
    fi

    if [ -L "$LOCAL_VENV_PATH" ]; then
      echo -e "\033[33m- Removing legacy symlinked venv at $LOCAL_VENV_PATH\033[0m"
      rm -f "$LOCAL_VENV_PATH"
    fi

    if [ "$FORCE_REFRESH" = "true" ]; then
      echo -e "\033[33m- FORCE_SHARED_VENV_SYNC requested; refreshing local venv copy.\033[0m"
      rm -rf "$LOCAL_VENV_PATH"
      rm -f "$SYNC_MARKER"
    fi

    if [ ! -f "$SYNC_MARKER" ]; then
      echo -e "\033[36m- Syncing shared venv into $LOCAL_VENV_PATH ...\033[0m"
      rm -rf "$LOCAL_VENV_PATH"
      mkdir -p "$LOCAL_VENV_PATH"
      if command -v rsync >/dev/null 2>&1; then
        rsync -a --delete "$SHARED_VENV_PATH/" "$LOCAL_VENV_PATH/"
      else
        (cd "$SHARED_VENV_PATH" && tar -cf - .) | (cd "$LOCAL_VENV_PATH" && tar -xf -)
      fi
      chown -R ${local.username}:${local.username} "$LOCAL_VENV_PATH"
      if find "$LOCAL_VENV_PATH" -name EXTERNALLY-MANAGED -print -quit >/dev/null 2>&1; then
        find "$LOCAL_VENV_PATH" -name EXTERNALLY-MANAGED -delete
      fi
      "$LOCAL_VENV_PATH/bin/python" -m ensurepip --upgrade
      touch "$SYNC_MARKER"
      echo -e "\033[32m- ✔️ Local venv cloned. Install additional packages freely (set FORCE_SHARED_VENV_SYNC=true to refresh).\033[0m"
    else
      echo -e "\033[32m- ✔️ Local venv already synced; custom packages preserved.\033[0m"
    fi

    mkdir -p ./.local/share/topo_editor
    cp -r /opt/coder/home-clone/.local/share/topo_editor/* ./.local/share/topo_editor/

    LOG_FILE="/home/${local.username}/.local/share/topo_editor/app.log"
    echo -e "\033[36m- 🚀 Starting topo editor (logs: $LOG_FILE)\033[0m"
    nohup $${LOCAL_VENV_PATH}/bin/python ./.local/share/topo_editor/main.py >"$LOG_FILE" 2>&1 </dev/null &
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

resource "docker_container" "workspace" {
  count = data.coder_workspace.me.start_count
  image = docker_image.main.name
  name = "coder-${local.username}-${lower(local.workspace)}"
  hostname = lower(local.workspace)
  dns = ["10.72.66.36", "10.72.66.37"]
  # Use the docker gateway if the access URL is 127.0.0.1
  entrypoint = ["sh", "-c", replace(coder_agent.main.init_script, "/localhost|127\\.0\\.0\\.1/", "host.docker.internal")]
  env = [
    "CODER_AGENT_TOKEN=${coder_agent.main.token}",
  ]
  host {
    host = "host.docker.internal"
    ip   = "host-gateway"
  }
  volumes {
    container_path = "/home/${local.username}"
    volume_name    = docker_volume.home_volume.name
    read_only      = false
  }
  # Add labels in Docker to keep track of orphan resources.
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
  mounts {
    read_only = true
    source    = "/opt/coder/assets/bin/h3ccodecli"
    target    = "/usr/local/bin/h3ccodecli"
    type      = "bind"
  }
  mounts {
    read_only = true
    source    = "/opt/coder/assets/code-server_${local.local_code_server_version}_amd64.deb"
    target    = "/opt/coder/assets/code-server.deb"
    type      = "bind"
  }
  mounts {
    read_only = true
    source    = "/opt/coder/assets/site-packages.tgz"
    target    = "/opt/coder/assets/site-packages.tgz"
    type      = "bind"
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
  mounts {
    read_only = true
    source    = "coder-${data.coder_parameter.coder_workspace_id.value}-home"
    target    = "/opt/coder/home-clone"
    type      = "volume"
  }
  mounts {
    read_only = true
    source    = "/opt/coder/venvs/comware-test"
    target    = "/opt/coder/venvs/comware-test"
    type      = "bind"
  }
}

resource "docker_image" "main" {
  name = "coder-${data.coder_workspace.me.id}"
  build {
    context = "build"
    build_args = {
      EXTENSION_VERSION = "1.104.0"
      PROXY_URL = "${local.proxy_url}"
      USER = "${local.username}"
      WORKSPACE_NAME = "${local.workspace}"
    }
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