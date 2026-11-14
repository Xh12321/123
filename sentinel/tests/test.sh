#!/bin/sh
# 判分入口(Verifier)
# - 自包含:仅依赖 /tests/test_outputs.py(纯标准库),不联网、不依赖第三方 pytest 插件;
#   质检侧可选用 pytest 收集运行同一文件,本入口不受影响。
# - 结果以 /logs/verifier/reward.txt 为准(0~1)。判分器内部按用例隔离异常,单用例失败/异常
#   只影响该项得分;判分器整体异常由本入口兜底为 reward=0。工具链完整性不符时仍运行可用的
#   真实验收流程以避免静默跳过,但最终 reward 强制为 0。
# - 【入口健壮性】本脚本在任何情况下都必须写出 reward 并以 0 退出:mkdir/写文件失败、
#   python 异常、结果文件缺失等一律兜底,不得把"答错/环境异常"上报成非零退出的"执行异常"。
#   内部判分进程的退出码仅作为可追踪输出打印,不作为本入口的退出码。

REWARD_FILE="/logs/verifier/reward.txt"
if ! mkdir -p /logs/verifier 2>/dev/null; then
    REWARD_FILE="/tmp/sentinel-verifier-reward.txt"
fi
echo 0 > "$REWARD_FILE" 2>/dev/null || true

# ======= 判分工具链防替换预检(R1 防作弊项) =======
# 固定 PATH(不继承答题进程可能篡改的 PATH,杜绝 PATH 投放假 python3/su/du);
# 解释器须为 ELF 实体,其散列及判分依赖实现与构建期基线(toolchain.list,已纳入封印)比对。
# 若基线不符,仍尽可能运行真实验收以诊断其余用例,并在结束时强制 reward=0;入口恒以 0 退出,
# 不把"工具链被替换"上报成执行异常。
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH
unset PYTHONPATH PYTHONHOME PYTHONSTARTUP 2>/dev/null || true
PY="$(command -v python3 2>/dev/null || true)"
PY_REAL="$(readlink -f "$PY" 2>/dev/null || true)"
TOOLCHAIN="/var/lib/sentinel/baseline/toolchain.list"
CHAIN_FAIL=""
if [ -z "$PY_REAL" ] || [ ! -f "$PY_REAL" ]; then
    CHAIN_FAIL="python3 解释器缺失或不可解析"
elif [ "$(head -c 4 "$PY_REAL" 2>/dev/null | od -An -tx1 | tr -d ' \n')" != "7f454c46" ]; then
    CHAIN_FAIL="python3 不是 ELF 实体(疑为包装脚本): $PY_REAL"
elif [ ! -f "$TOOLCHAIN" ]; then
    CHAIN_FAIL="工具链基线 toolchain.list 缺失,完整性无法核验"
elif ! sha256sum -c "$TOOLCHAIN" >/dev/null 2>&1; then
    CHAIN_FAIL="判分工具链(python3/su/du及keyword.py/base64.py)散列与构建期基线不一致(疑被替换)"
fi
# 属主/模式位异常只告警不拦截:哈希比对(已封印基线)是权威判据,模式位仅作旁证
# (部分基础镜像的工具链安装本身即 o+w,不能据此误杀)
if [ -n "$PY_REAL" ] && [ -f "$PY_REAL" ]; then
    if [ "$(stat -c %u "$PY_REAL" 2>/dev/null)" != "0" ]; then
        echo "[test.sh] 警告: python3 非 root 属主($PY_REAL),已由哈希比对兜底" >&2
    fi
    if [ -n "$(find "$PY_REAL" -maxdepth 0 -perm /022 2>/dev/null)" ]; then
        echo "[test.sh] 警告: python3 可被组/其他写入($PY_REAL),已由哈希比对兜底" >&2
    fi
fi
if [ -n "$CHAIN_FAIL" ]; then
    # 工具链不可信时仍运行可用的真实验收流程(尤其不可因 keyword.py 变化而静默跳过),
    # 但最终分数必须归零。这样既保留失败诊断/其余用例的实际执行,也不信任被篡改环境。
    echo "[test.sh] 判分工具链预检失败(仍执行验收,最终强制 0): $CHAIN_FAIL" >&2
fi

# ======= 运行复测判分器(root 身份执行,内部通过 su 降权模拟 ops/collector 真实视角)======
# -I -S:隔离模式运行,忽略 PYTHONPATH/用户 site 与 sitecustomize,防止答题进程借
# Python 导入钩子干预判分器(判分器自身为纯标准库,不依赖 site 初始化)。
if [ -n "$PY_REAL" ] && [ -f "$PY_REAL" ] \
   && [ "$(head -c 4 "$PY_REAL" 2>/dev/null | od -An -tx1 | tr -d ' \n')" = "7f454c46" ]; then
    if python3 -I -S /tests/test_outputs.py; then
        EXIT_CODE=0
    else
        EXIT_CODE=$?
        # 判分器可能在写入正分后因未捕获异常/信号退出;先持久化归零,再输出诊断。
        # 即使日志接收端已关闭导致后续输出失败/触发 SIGPIPE,也不能留下正分。
        echo 0 > "$REWARD_FILE" 2>/dev/null || true
        echo "[test.sh] checker exited abnormally after score calculation; forcing reward=0" >&2
    fi
else
    EXIT_CODE=127
    echo "[test.sh] 没有可安全启动的 ELF Python,无法运行判分器" >&2
    echo 0 > "$REWARD_FILE" 2>/dev/null || true
fi
if [ -n "$CHAIN_FAIL" ]; then
    echo 0 > "$REWARD_FILE" 2>/dev/null || true
fi
echo "[test.sh] checker exit code: $EXIT_CODE"

# 兜底:判分器未能写出结果时保持 0 分,不让入口异常退出
if ! grep -q '[0-9]' "$REWARD_FILE" 2>/dev/null; then
    echo 0 > "$REWARD_FILE" 2>/dev/null || true
fi

# ====== 打印最终 reward(供运行日志核对)======
cat "$REWARD_FILE" 2>/dev/null || echo 0

exit 0
