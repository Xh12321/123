#!/bin/sh
# 评测侧封印生成器(构建期专用,在独立的中间构建阶段运行)
# - 封印密钥经 $SEAL_KEY 传入,本文件不承载密钥;
# - 多阶段构建下本阶段与密钥均不进入最终镜像的任何文件系统层(最终阶段仅 COPY 封印结果);
# - 封印对象(canonical 串,顺序与 tests/test_outputs.py 的 _seal_calc 严格一致):
#   凭据校验散列 : checks/log-lines/passwd/groups/suid/clean/ww/gw/toolchain/log-keep/capabilities/usrbin 基线散列
#   : 巡检器源与二进制摘要；capabilities.list 覆盖根文件系统(排除动态伪文件系统)。每项亦在 .build-meta 有摘要交叉引用。
set -e
[ -n "$SEAL_KEY" ] || { echo "seal.sh: SEAL_KEY 未提供" >&2; exit 1; }
B=/var/lib/sentinel/baseline
M=/usr/local/src/.build-meta
EVID="$(cat "$B/evidence.hash")"
LOG_LINES="$(awk -F= '/^log-lines=/{print $2}' "$M")"
CANON="$EVID:$(sha256sum "$B/checks.sha256" | awk '{print $1}'):$LOG_LINES:$(sha256sum "$B/passwd.list" | awk '{print $1}'):$(sha256sum "$B/groups.list" | awk '{print $1}'):$(sha256sum "$B/suid.list" | awk '{print $1}'):$(sha256sum "$B/clean.list" | awk '{print $1}'):$(sha256sum "$B/ww.list" | awk '{print $1}'):$(sha256sum "$B/gw.list" | awk '{print $1}'):$(sha256sum "$B/toolchain.list" | awk '{print $1}'):$(sha256sum "$B/log-keep.list" | awk '{print $1}'):$(sha256sum "$B/capabilities.list" | awk '{print $1}'):$(sha256sum "$B/usrbin.list" | awk '{print $1}'):$(awk -F= '/^packer-source-sha256=/{print $2}' "$M"):$(awk -F= '/^packer-binary-sha256=/{print $2}' "$M")"
SEAL_VAL="$(printf '%s' "$CANON" | openssl dgst -sha256 -hmac "$SEAL_KEY" -r | awk '{print $1}')"
printf 'seal=%s\n' "$SEAL_VAL" > "$B/seal.hmac"
chown root:root "$B/seal.hmac"
chmod 0644 "$B/seal.hmac"
echo "[seal] baseline seal written."
