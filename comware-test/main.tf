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

data "coder_parameter" "domain_password" {
  name          = "domain_password"
  display_name  = "Domain password"
  order         = 0
  description   = "Specify a domain password to login with your domain account."
  type          = "string"
  mutable       = true
}
data "coder_provisioner" "me" {
}
data "coder_workspace" "me" {
}
data "coder_workspace_owner" "me" {
}

locals {
  username = data.coder_workspace_owner.me.name
  password = data.coder_parameter.domain_password.value
  proxy_url = "http://${data.coder_workspace_owner.me.name}:${data.coder_parameter.domain_password.value}@proxy02.h3c.com:8080"
  workspace = data.coder_workspace.me.name
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
      code-server --version | head -n1 | cut -d " " -f1 || echo unknown
    EOF
    interval     = 30
    order        = 2
  }
}

resource "coder_app" "code_server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "Code Server"
  icon         = "/icon/code.svg"
  url          = "http://localhost:13337/?folder=/home/${local.username}/project"
  subdomain    = true
  share        = "public"

  healthcheck {
    url       = "http://localhost:13337/healthz"
    interval  = 5
    threshold = 6
  }
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

resource "coder_script" "start_code_server" {
  agent_id     = coder_agent.main.id
  display_name = "Start Code Server"
  icon         = "/icon/code.svg"
  run_on_start = true
  start_blocks_login = true
  script = <<EOF
    #!/bin/bash
    echo -e "\033[36m- 📦 Installing code-server\033[0m"
    curl -fsSL https://code-server.dev/install.sh | sh

    # echo -e "\033[36m- ⏳ Installing extensions\033[0m"
    # code-server --install-extension "alefragnani.bookmarks"
    # code-server --install-extension "Alibaba-Cloud.tongyi-lingma-onpremise"
    # code-server --install-extension "anjali.clipboard-history"
    # code-server --install-extension "beaugust.blamer-vs"
    # code-server --install-extension "bierner.markdown-mermaid"
    # code-server --install-extension "dbaeumer.vscode-eslint@prerelease"
    # code-server --install-extension "esbenp.prettier-vscode"
    # code-server --install-extension "johnstoncode.svn-scm"
    # code-server --install-extension "ms-ceintl.vscode-language-pack-zh-hans"
    # code-server --install-extension "ms-python.debugpy@prerelease"
    # code-server --install-extension "ms-vscode.cpptools@prerelease"
    # code-server --install-extension "timonwong.shellcheck"
    # code-server --install-extension "rangav.vscode-thunder-client"
    # code-server --install-extension "redhat.vscode-xml@prerelease"
    # code-server --install-extension "rsbondi.highlight-words"

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
}

resource "docker_image" "main" {
  name = "coder-${data.coder_workspace.me.id}"
  build {
    context = "build"
    build_args = {
      EXTENSION_VERSION = "1.103.2025081309"
      PROXY_URL = local.proxy_url
      USER = local.username
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