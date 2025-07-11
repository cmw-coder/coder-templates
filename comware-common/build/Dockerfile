FROM registry.coder.h3c.com/ubuntu:24.04

COPY --chmod=755 bin /usr/local/bin
COPY ca-certs /usr/local/share/ca-certificates/
COPY ubuntu.sources /etc/apt/sources.list.d/

RUN apt-get update \
    && apt-get install -y build-essential ca-certificates curl jq nano neovim sudo \
    && update-ca-certificates \
    && apt-get install -y language-pack-en-base locales subversion \
    && sed -i '/en_US.UTF-8/s/^#//g' /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    && apt-get install -y python3 python3-pip black \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/glibc/include \
    && mkdir -p /opt/open-headers/include

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

ARG USER=coder
RUN useradd --groups sudo --no-create-home --shell /bin/bash ${USER} \
    && echo "${USER} ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/${USER} \
    && chmod 0440 /etc/sudoers.d/${USER}

USER ${USER}
WORKDIR /home/${USER}

COPY --chown=${USER}:${USER} code-server /home/${USER}/.local/share/code-server/
COPY --chown=${USER}:${USER} pip.conf /home/${USER}/.pip/

# Add languagepacks.json
ARG EXTENSION_VERSION=1.99.2025040909
RUN export LANGUAGEPACK_HASH=$(echo -n "MS-CEINTL.vscode-language-pack-zh-hans${EXTENSION_VERSION}" | md5sum | awk '{print $1}') \
    && sed -i "s|%USER%|${USER}|g;s|%LANGUAGEPACK_HASH%|${LANGUAGEPACK_HASH}|g;s|%EXTENSION_VERSION%|${EXTENSION_VERSION}|g" /home/${USER}/.local/share/code-server/languagepacks.json
