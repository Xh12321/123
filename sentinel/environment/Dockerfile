# 可复现构建:基础镜像按内容摘要钉定,apt 走 snapshot.debian.org 固定时点,
# 构建输入不随上游仓库更新漂移(版本漂移整改)。如需更换时点,只改 APT_SNAPSHOT。
FROM python:3.11-slim-bookworm@sha256:0a310eeecf4e1f5a0743f9a6520c90c88d089c903ca5fd283f501e3a805f5f89 AS provisioned
ENV DEBIAN_FRONTEND=noninteractive
ARG APT_SNAPSHOT=20261001T000000Z

# 基础镜像为 bookworm 底座(与平台示例一致),补装节点画像所需工具:
# gcc/libc6-dev(编译内置巡检器)、openssl(构建期生成密文凭据)、procps/psmisc/iproute2 运维噪音
# strace(判分器以真实文件装载枚举采集链路的载入入口)、findutils(基线清单)
# vim/curl/less 为真实运维节点噪音兼解题辅助
# 注意:本设计不依赖任何特权转换(无 sudo、无 setuid),故不安装 sudo
RUN printf 'Types: deb\nURIs: https://snapshot.debian.org/archive/debian/%s/\nSuites: bookworm bookworm-updates\nComponents: main\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\nCheck-Valid-Until: no\n' "$APT_SNAPSHOT" \
        > /etc/apt/sources.list.d/debian.sources \
    && printf 'Types: deb\nURIs: https://snapshot.debian.org/archive/debian-security/%s/\nSuites: bookworm-security\nComponents: main\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\nCheck-Valid-Until: no\n' "$APT_SNAPSHOT" \
        > /etc/apt/sources.list.d/debian-security.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        nodejs \
        npm \
        gcc \
        libc6-dev \
        openssl \
        procps \
        psmisc \
        findutils \
        strace \
        vim \
        curl \
        less \
        iproute2 \
        libcap2-bin \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app /logs/verifier

# 环境素材扁平放置(兼容平台单文件上传);setup.sh 构建完成后随 /opt/setup 一并删除,
# 避免向解题者泄露故障布置细节
COPY setup.sh sentinel-packer.c collect.sh collect.conf 10-disk.sh 20-audit.sh \
     motd README.internal.txt agent.log /opt/setup/files/
RUN bash /opt/setup/files/setup.sh && rm -rf /opt/setup

# ===== 封印阶段(独立中间阶段) =====
# 评测侧 HMAC 封印在这里生成:密钥只存在于本阶段的构建命令中,
# 多阶段构建下本阶段的层不进入最终镜像——最终阶段仅 COPY 封印结果(seal.hmac)。
# (对照行为:把密钥写进 setup.sh 等被 COPY 的文件,即使事后 rm,仍会留在最终镜像的历史层里。)
FROM provisioned AS sealstep
COPY seal.sh /opt/seal.sh
RUN SEAL_KEY="7c1e4b9a2d5f8360eac74d1b92f05a83" sh /opt/seal.sh && rm -f /opt/seal.sh

# ===== 最终镜像 =====
FROM provisioned AS final
COPY --from=sealstep /var/lib/sentinel/baseline/seal.hmac /var/lib/sentinel/baseline/seal.hmac

# 平台评测兼容:镜像最终 USER 必须为 root(平台硬校验项),否则评测框架无法完成环境与判分注入。
# 本任务为"root 起步的授权加固复测"形态:agent 以 root 进入,低权视角操作一律以 su 降权真实执行;
# 设计上不依赖任何特权增益(setuid/sudo),因此在 NoNewPrivs=1 与 =0 的容器中均可正常作答与判分。
USER root
WORKDIR /home/ops

CMD ["/bin/bash"]
