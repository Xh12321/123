#!/bin/sh
# 特权巡检项:审计通道写入自检(目标日志仅 root 可写,用于确认巡检以特权执行)
# 记录中携带执行身份 uid:root 特权执行时写入 uid=0,业务被降级时该记录会缺失或身份异常
printf '%s [audit] uid=%s channel=rootcheck-ok\n' "$(date -Is)" "$(id -u)" >> /var/log/sentinel/rootcheck.log
