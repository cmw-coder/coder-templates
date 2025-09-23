FROM node:trixie

# Set environment variables
ENV DEVCONTAINER=true
ENV TZ=Asia/Shanghai

COPY --chmod=755 bin /usr/local/bin
COPY debian.sources /etc/apt/sources.list.d/

# Write proxy configuration to /etc/apt/apt.conf.d/00proxy.conf if PROXY_URL is provided
ARG PROXY_URL=""
RUN if [ -n "$PROXY_URL" ]; then \
    printf 'Acquire::http::Proxy "%s";\nAcquire::https::Proxy "%s";\nAcquire::ftp::Proxy "%s";\n' "$PROXY_URL" "$PROXY_URL" "$PROXY_URL" > /etc/apt/apt.conf.d/00proxy.conf; \
    fi

# Install essential packages and set locale and shell
RUN apt-get update \
    && apt-get install -y build-essential ca-certificates curl fzf git jq locales man-db nano neovim sudo unzip \
        python3 python3-venv pip python-is-python3 black zsh \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && sed -i '/en_US.UTF-8/s/^#//g' /etc/locale.gen && locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV SHELL=/bin/zsh
# Set the default editor and visual
ENV EDITOR=nvim
ENV VISUAL=nvim

# Add the H3C CA certificate to the system trust store
COPY ca-certs /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Install Claude Code
RUN if [ -n "$PROXY_URL" ]; then \
        npm config set proxy "$PROXY_URL" \
        && npm config set https-proxy "$PROXY_URL" \
        && npm config set strict-ssl false; \
    fi
RUN npm install -g @anthropic-ai/claude-code@latest

# Create a non-root user with sudo privileges
ARG USER=coder
RUN useradd --groups sudo --no-create-home --shell /bin/bash ${USER} \
    && echo "${USER} ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/${USER} \
    && chmod 0440 /etc/sudoers.d/${USER}
# Ensure user has access to /usr/local/share
RUN mkdir -p /usr/local/share/npm-global && \
  chown -R ${USER}:${USER} /usr/local/share
# Persist bash history.
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  && mkdir /commandhistory \
  && touch /commandhistory/.bash_history \
  && chown -R ${USER} /commandhistory
# Set the default user and working directory
USER ${USER}
WORKDIR /home/${USER}

# Copy user specific configuration files
COPY --chown=${USER}:${USER} .claude /home/${USER}/.claude/
COPY --chown=${USER}:${USER} code-server /home/${USER}/.local/share/code-server/
COPY --chown=${USER}:${USER} project /home/${USER}/project/

# Add languagepacks.json
ARG EXTENSION_VERSION=1.99.2025040909
RUN export LANGUAGEPACK_HASH=$(echo -n "MS-CEINTL.vscode-language-pack-zh-hans${EXTENSION_VERSION}" | md5sum | awk '{print $1}') \
    && sed -i "s|%USER%|${USER}|g;s|%LANGUAGEPACK_HASH%|${LANGUAGEPACK_HASH}|g;s|%EXTENSION_VERSION%|${EXTENSION_VERSION}|g" /home/${USER}/.local/share/code-server/languagepacks.json
