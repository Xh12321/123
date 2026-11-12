#!/bin/sh
# 评测侧封印生成器(构建期专用,在独立的中间构建阶段运行)
# - 封印密钥经 $SEAL_KEY 传入,本文件不承载密钥;
# - 多阶段构建下本阶段与密钥均不进入最终镜像的任何文件系统层(最终阶段仅 COPY 封印结果);
# - 封印对象(canonical 串,顺序与 tests/test_outputs.py 的 _seal_calc 严格一致):
#   凭据校验散列 : 巡检项基线散列 : log-lines : passwd/groups/suid/clean/ww 五个基线清单散列
#   : log-keep(日志保全锚点)散列。
set -e
[ -n "$SEAL_KEY" ] || { echo "seal.sh: SEAL_KEY 未提供" >&2; exit 1; }
B=/var/lib/sentinel/baseline
M=/usr/local/src/.build-meta
EVID="$(cat "$B/evidence.hash")"
LOG_LINES="$(awk -F= '/^log-lines=/{print $2}' "$M")"
CANON="$EVID:$(sha256sum "$B/checks.sha256" | awk '{print $1}'):$LOG_LINES:$(sha256sum "$B/passwd.list" | awk '{print $1}'):$(sha256sum "$B/groups.list" | awk '{print $1}'):$(sha256sum "$B/suid.list" | awk '{print $1}'):$(sha256sum "$B/clean.list" | awk '{print $1}'):$(sha256sum "$B/ww.list" | awk '{print $1}'):$(sha256sum "$B/toolchain.list" | awk '{print $1}'):$(sha256sum "$B/log-keep.list" | awk '{print $1}'):$(sha256sum "$B/capabilities.list" | awk '{print $1}'):$(sha256sum "$B/usrbin.list" | awk '{print $1}')"
SEAL_VAL="$(printf '%s' "$CANON" | openssl dgst -sha256 -hmac "$SEAL_KEY" -r | awk '{print $1}')"
printf 'seal=%s\n' "$SEAL_VAL" > "$B/seal.hmac"
chown root:root "$B/seal.hmac"
chmod 0644 "$B/seal.hmac"
echo "[seal] baseline seal written."
