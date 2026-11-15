#!/bin/bash
# sentinel-collect —— 采集脚本
# 按 /etc/sentinel/collect.conf 中的采集参数汇总日志目录容量信息,
# 输出到 /var/lib/sentinel/reports/latest.collect,供运维侧日常查阅。
CONF=/etc/sentinel/collect.conf
OUT=/var/lib/sentinel/reports/latest.collect

# 载入采集配置(采集目标、保留天数等)
if [ -r "$CONF" ]; then
    . "$CONF"
fi

TARGETS="${TARGETS:-/var/log}"
FAILED=0

# 先写临时文件再原子替换,避免采集失败时留下半截报告
# 写入失败(如配额/文件大小限制)必须按落盘失败契约反馈:WARN 定位对象+非零码,不得静默
trap '' XFSZ 2>/dev/null || true   # 写超限转为 EFBIG 错误返回,保证失败分支可执行(非被信号杀死)
TMP="$(mktemp "${OUT}.XXXXXX")" || { echo "WARN report create failed: $OUT" >&2; exit 1; }
chmod 0644 "$TMP"
{
    echo "host=$(hostname)"
    echo "ts=$(date -Is)"
    echo "user=$(id -un)"
    echo "targets=$TARGETS"
    for t in $TARGETS; do
        # 失败反馈契约(SRE-3417):目标不存在/完全不可读(无输出),或 du 报错
        # (存在不可读内容、测量结果不完整),都必须记 WARN 行并以失败计数退出,
        # 不得把"部分输出"当成功静默吞错
        _size="$(du -sh "$t" 2>/dev/null)"
        _drc=$?
        if [ -z "$_size" ]; then
            echo "WARN unreadable target: $t"
            FAILED=1
        elif [ "$_drc" -ne 0 ]; then
            echo "$_size"
            echo "WARN unreadable target: $t"
            FAILED=1
        else
            echo "$_size"
        fi
    done
    echo "retention_days=${RETENTION_DAYS:-14}"
} > "$TMP" || { echo "WARN report write failed: $OUT" >&2; rm -f "$TMP"; exit 2; }
# 报告落盘失败必须可定位:替换失败以 WARN + 非零码反馈,不得静默成功(SRE-3715)
if ! mv -f "$TMP" "$OUT"; then
    echo "WARN report replace failed: $OUT" >&2
    rm -f "$TMP"
    exit 4
fi

if [ "$FAILED" -ne 0 ]; then
    echo "sentinel-collect: 采集不完整:存在不可读/无效的采集目标($TARGETS)" >&2
    exit 3
fi
exit 0
