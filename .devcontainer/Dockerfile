FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    genisoimage \
    gettext-base \
    git \
    gpg \
    iproute2 \
    fdisk \
    jq \
    libvirt-clients \
    locales \
    openssh-client \
    ovmf \
    python3 \
    python3-pip \
    qemu-kvm \
    qemu-system-x86 \
    qemu-utils \
    rsync \
    sudo \
    unzip \
    wget \
    xorriso \
    vim \
    wireguard-tools \
 && sed -i 's/^# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen \
 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
 && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

RUN install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
RUN apt-get update \
 && apt-get install -y docker-ce-cli docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*

ENV HOME=/root

# Installer kubectl (version stable) — compatible k3s
RUN KUBECTL_VERSION=$(curl -fsSL https://dl.k8s.io/release/stable.txt) \
 && curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/$(dpkg --print-architecture)/kubectl" \
    -o /usr/local/bin/kubectl \
 && chmod +x /usr/local/bin/kubectl

# Installer Ansible
RUN pip3 install --break-system-packages \
    ansible-core \
    ansible-lint \
    sphinx \
    sphinx-rtd-theme \
    sphinx-copybutton \
    sphinx-tabs \
 && ansible-galaxy collection install \
    ansible.posix \
    community.general

# Installer d2 (générateur de diagrammes)
RUN D2_VERSION=$(curl -fsSL https://api.github.com/repos/terrastruct/d2/releases/latest | grep '"tag_name"' | cut -d'"' -f4) \
 && curl -fsSL "https://github.com/terrastruct/d2/releases/download/${D2_VERSION}/d2-${D2_VERSION}-linux-$(dpkg --print-architecture).tar.gz" \
    | tar -xz --strip-components=2 -C /usr/local/bin "d2-${D2_VERSION}/bin/d2"

# Installer Claude Code (binaire natif) pour l'utilisateur root
RUN curl -fsSL https://claude.ai/install.sh | bash

# Ajouter Claude Code au PATH
ENV PATH="/root/.local/bin:${PATH}"

# Aussi sourcer ESP-IDF et ajouter Claude au PATH pour les shells interactifs
RUN echo 'export PATH="/root/.local/bin:${PATH}"' >> ~/.bashrc

WORKDIR /workspace

CMD ["/bin/bash"]