FROM registry.coder-route.h3c.com/node:trixie-slim

# Set environment variables
ENV DEVCONTAINER=true
ENV TZ=Asia/Shanghai

COPY --chmod=755 bin /usr/local/bin
COPY ca-certs /usr/local/share/ca-certificates/
COPY debian.sources /etc/apt/sources.list.d/

RUN apt-get update \
    && apt-get install -y build-essential ca-certificates curl fzf jq man-db nano neovim sudo unzip \
    && update-ca-certificates \
    && apt-get install -y locales subversion \
    && sed -i 's|# en_US.UTF-8|en_US.UTF-8|g' /etc/locale.gen \
    && locale-gen \
    && apt-get install -y python3 python3-pip black \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/glibc/include \
    && mkdir -p /opt/open-headers/include

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
# Set the default editor and visual
ENV EDITOR=nvim
ENV VISUAL=nvim

# Install Claude Code
RUN npm config set registry http://rdmirrors.h3c.com/npm \
    && npm install -g @anthropic-ai/claude-code@2.0.14

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

COPY --chown=${USER}:${USER} bashrc /home/${USER}/.bashrc
COPY --chown=${USER}:${USER} code-server /home/${USER}/.local/share/code-server/
COPY --chown=${USER}:${USER} pip.conf /home/${USER}/.pip/

# Add languagepacks.json
ARG EXTENSION_VERSION=1.99.2025040909
RUN export LANGUAGEPACK_HASH=$(echo -n "MS-CEINTL.vscode-language-pack-zh-hans${EXTENSION_VERSION}" | md5sum | awk '{print $1}') \
    && sed -i "s|%USER%|${USER}|g;s|%LANGUAGEPACK_HASH%|${LANGUAGEPACK_HASH}|g;s|%EXTENSION_VERSION%|${EXTENSION_VERSION}|g" /home/${USER}/.local/share/code-server/languagepacks.json
