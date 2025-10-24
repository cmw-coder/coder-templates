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
  ke_file_map = jsondecode(file("${path.module}/ke_file_map.json"))
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

data "coder_parameter" "business_component" {
  name = "business_component"
  display_name = "Business Component"
  description = "Select the business component"
  default = ""
  form_type = "dropdown"
  order = 0
  mutable = false

  option {
    name = "All"
    value = ""
  }

  dynamic "option" {
    for_each = keys(local.ke_file_map)
    content {
      name  = option.value
      value = option.value
    }
  }
}

data "coder_parameter" "business_module" {
  name = "business_module"
  display_name = "Business Module"
  description = "Select the module for the chosen component"
  default = ""
  form_type = "dropdown"
  order = 1
  mutable = false

  option {
    name = "All"
    value = ""
  }

  dynamic "option" {
    for_each = data.coder_parameter.business_component.value != "" ? keys(local.ke_file_map[data.coder_parameter.business_component.value]) : []
    content {
      name = option.value
      value = option.value
    }
  }
}

data "coder_parameter" "module_tag_file_list" {
  count = data.coder_parameter.business_component.value != "" && data.coder_parameter.business_module.value != "" ? 1 : 0
  name = "module_tag_file_list"
  display_name = "Module Tag File List"
  description = "Select the KE files to be pulled"
  form_type = "multi-select"
  type = "list(string)"
  default = jsonencode([])
  order = 2
  mutable = false

  dynamic "option" {
    for_each = local.ke_file_map[data.coder_parameter.business_component.value][data.coder_parameter.business_module.value]
    content {
      name = option.value
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
    NO_PROXY           = "localhost"
    PROJECT_BASE_DIR    = "/home/${local.username}/project"
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
resource "coder_env" "disable_autoupdater" {
  agent_id = coder_agent.main.id
  name     = "DISABLE_AUTOUPDATER"
  value    = "1"
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

resource "coder_script" "start_code_server" {
  agent_id     = coder_agent.main.id
  display_name = "Start Code Server"
  icon         = "/icon/code.svg"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    echo -e "\033[36m- 📦 Installing code-server\033[0m"
    sudo dpkg -i /opt/coder/assets/code-server.deb

    echo -e "\033[36m- ⏳ Installing extensions\033[0m"
    install-extension --local /opt/coder/assets/extensions/alefragnani.bookmarks-13.5.0.vsix
    install-extension --local /opt/coder/assets/extensions/bierner.markdown-mermaid-1.29.0.vsix
    install-extension --local /opt/coder/assets/extensions/dbaeumer.vscode-eslint-3.0.16.vsix
    install-extension --local /opt/coder/assets/extensions/chrisjsewell.myst-tml-syntax-0.1.3.vsix
    install-extension --local /opt/coder/assets/extensions/esbenp.prettier-vscode-11.0.0.vsix
    install-extension --local /opt/coder/assets/extensions/iceworks-team.iceworks-time-master-1.0.4.vsix
    install-extension --local /opt/coder/assets/extensions/MS-CEINTL.vscode-language-pack-zh-hans-1.104.0.vsix
    install-extension --local /opt/coder/assets/extensions/ms-python.black-formatter-2025.2.0.vsix
    install-extension --local /opt/coder/assets/extensions/ms-python.debugpy-2025.14.0.vsix
    install-extension --local /opt/coder/assets/extensions/ms-python.python-2025.16.0.vsix
    install-extension --local /opt/coder/assets/extensions/redhat.vscode-xml-0.29.2025081108.vsix
    install-extension --local /opt/coder/assets/extensions/swyddfa.esbonio-0.96.6.vsix
    install-extension --local /opt/coder/assets/extensions/timonwong.shellcheck-0.38.3.vsix

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
    mkdir -p ./KE

    business_component="${data.coder_parameter.business_component.value}"
    business_module="${data.coder_parameter.business_module.value}"
    module_tag_file_list=$(echo "${try(data.coder_parameter.module_tag_file_list[0].value, jsonencode([]))}" | tr -d '[]"')
    echo "Selected Business Component: $${business_component}"
    echo "Selected Business Module: $${business_module}"
    echo "Selected KE Files: $${module_tag_file_list}"

    if [ -n "$${business_component}" ]; then
      if [ -n "$${business_module}" ]; then
        if [ -n "$${module_tag_file_list}" ]; then
          IFS=',' read -ra files <<< "$${module_tag_file_list}"
          for file in "$${files[@]}"; do
            trimmed_file=$(echo "$file" | xargs)
            echo "Copying KE file: $${trimmed_file}"
            cp /opt/coder/assets/ke/"$${business_component}"/"$${business_module}"/"$${trimmed_file}" ./KE/"$${trimmed_file}"
          done
        else
          echo "Copying whole module KE files."
          cp /opt/coder/assets/ke/"$${business_component}"/"$${business_module}"/* ./KE/
        fi
      else
        echo "Copying whole component KE files."
        find /opt/coder/assets/ke/"$${business_component}" -name "*.md" -type f -exec cp {} ./KE/ \;
      fi
    else
      echo "Copying all KE files."
      find /opt/coder/assets/ke -name "*.md" -type f -exec cp {} ./KE/ \;
    fi

    mkdir -p ./press
    mkdir -p ./test_cases
    mkdir -p ./test_example
    mkdir -p ./test_scripts
    python -m venv .venv
    source .venv/bin/activate
    # pip install -i http://rdmirrors.h3c.com/pypi/web/simple --trusted-host rdmirrors.h3c.com -r requirements.txt
    tar -zxf /opt/coder/assets/site-packages.tgz -C .venv/lib/python3.13/site-packages/
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
    source    = "/opt/coder/assets/extensions"
    target    = "/opt/coder/assets/extensions"
    type      = "bind"
  }
  mounts {
    read_only = true
    source    = "/opt/coder/assets/ke"
    target    = "/opt/coder/assets/ke"
    type      = "bind"
  }
  mounts {
    read_only = true
    source    = "/opt/coder/assets/site-packages.tgz"
    target    = "/opt/coder/assets/site-packages.tgz"
    type      = "bind"
  }
  mounts {
    read_only = false
    source    = "/opt/coder/statistics/build"
    target    = "/opt/coder/statistics/build"
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
    }
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