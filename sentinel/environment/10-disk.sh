#!/bin/sh
# 常规巡检项:磁盘用量快照
df -h > /var/lib/sentinel/reports/latest.disk 2>&1
