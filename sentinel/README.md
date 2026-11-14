- # sentinel-node-lpe-hardening(授权加固复测版)
  
  Harbor/Terminal-Bench 任务包:在一台 sentinel 监控节点上完成**三处注入面的复现取证与就地加固**。
  
  
  ## 目录结构
  
  ```
  .
  ├── instruction.md              # 题面(中文)
  ├── task.toml                   # 平台配置(schema 1.4;[agent] user = "root";timeout 3600)
  ├── environment/                # 环境素材(扁平放置,COPY 自构建上下文根目录)
  │   ├── Dockerfile              #   python:3.11-slim;不装 sudo;末尾 USER root
  │   ├── setup.sh                #   构建期一次性布置(账户/权限/巡检/日志内遗留载荷/两段式凭据/构建元数据/基线)
  │   ├── sentinel-packer.c       #   巡检执行器源码(root 侧例行执行,非 setuid)
  │   ├── collect.sh              #   采集脚本(以 collector 运行;配置仅作数据解析,不得 source/eval)
  │   ├── collect.conf            #   采集配置(root:ops 0664 —— 注入面 1)
  │   ├── 10-disk.sh / 20-audit.sh#   既有巡检项
  │   ├── motd / README.internal.txt / agent.log   # 环境噪音(含变更记录线索)
  ├── solution/solve.sh           # 参考解(root 起步 + su 降权复现)
  └── tests/
      ├── test.sh                 # 自包含判分入口(写 reward.txt)
      └── test_outputs.py         # 判分器(纯标准库;5 用例加权,双门控=复现取证+注入面闭环)
  ```
  
  ## 冻结输入与摘要关联
  
  本修订工作树以上一版本交付代码为基础。交付包由下方18项文件 allowlist 精确构成；封装时只按该清单选取文件。包内 `MANIFEST.sha256` 按原始字节逐一摘要其余17个交付输入；与清单文件自身合计为18个包文件。任何内容变更后须重算该清单，并以 `sha256sum -c MANIFEST.sha256` 核对；清单本身不对自身做递归散列。
  
  ## 任务要点
  
  - **形态**:root 起步的授权加固复测;低权视角一律 su 降权真实执行(不含任何特权转换)。任务镜像预装所需工具，不要用 apt/apt-get/dpkg 改动系统包。
  - **采集配置与注入面 1**:`/etc/sentinel/collect.conf` 交付时必须为 `root:ops 0664` 且 ops 可维护；采集器仅将其作为受限数据解析，禁止 `source`、点号加载、`eval` 或间接 shell 执行。仅接受 `TARGETS="绝对路径列表"` 与 `RETENTION_DAYS=十进制整数`，保留天数范围 1–3650（文本不设额外位数限制，9999 必须拒绝）；合法变更须反映到报告，非法输入须 WARN+非零退出。注入面覆盖任何被采集脚本读取/载入的配置，包括修复后新增或替代入口。
  - **注入面 2**:`/etc/sentinel/checks.d`(root:sentinel 0775)被 root 侧例行执行的巡检执行器逐项执行。
  - **注入面 3**:`/etc/sentinel/pack.include`(root:sentinel 0664)所列脚本被巡检执行器在 checks.d 之后按书写顺序、以 shell 内容读取执行；条目自身没有执行位也必须照常执行。
  - **门控**:凭据为两段式(各 16 位十六进制)——第 1 段由日志中 base64 分片留存的遗留载荷解出(需密钥),
    第 2 段以构建引用(diag-ref)内嵌于巡检执行器二进制(仅二进制,需 strings 类手段提取);判分侧以
    **评测侧 HMAC 封印**(密钥仅存判分脚本与 Dockerfile 封印中间阶段——多阶段构建下不进入最终镜像任何层,答题容器内不可得)把基线锚定为可信基准,配合基线/元数据/二进制内嵌引用/遗留材料实时解密结果的**多副本一致性交叉校验**把关——成套改写基线也无法伪造封印。
    现场另有已作废的草稿(draft)批次分片以同样形式混在日志中,须自行甄别。
  - **业务异常**:附加清单残留上轮失效条目致巡检非零退出——属复测范围,须一并修复(清单资产保留)。
  - **加固**:封死全部注入面(行为级复测),保持采集/巡检业务可用,清理遗留物与复现痕迹(日志只删异常记录),交付 findings.json。
  
  ## 判分口径(权重合计 1.0)
  
  | 用例                             | 权重 | 要点                                                         |
  | -------------------------------- | ---- | ------------------------------------------------------------ |
  | 复现取证(门控)                   | 0.25 | 两段式凭据经散列比对;多副本交叉校验;proof 须为独立普通文件(拒绝符号链接与硬链接) |
  | 注入面闭环(向量 1/2/3 合并,门控) | 0.15 | 三处以低权身份注入并真实触发业务工具,载荷均不得执行:向量1 采集配置(ops 写配置+collector 触发,两种载荷;strace 真实装载枚举主通道,绝对与相对路径装载均解析重放,含新增/替代入口、eval 动态装载、/tmp 等低权可写目录新增载荷配置);向量2 巡检目录(ops/collector 投放+root 触发);向量3 附加清单(collector 写入+root 触发) |
  | 业务连续性                       | 0.25 | 三份报告留存并真实重生成(同秒连跑按 1.2s 重试后判定);采集容量须为 du 风格行且数值落在实测 0.5–2.0 倍内;三份报告整体含执行身份与生成时间(可审计要素);巡检器 exit 0、失败计数为 0、清单资产保留;巡检项哈希一致;root 级巡检以 uid=0 执行;临时探针验证巡检器真实执行;失败反馈契约直接触发(采集目标无效→WARN 且 WARN 指向失败目标+非零退出,多目标同时失败逐一具名;采集目标部分不可读即 du 有输出但报错→同样 WARN+非零退出;巡检项失败→非零退出+失败计数;checks.d 不可打开→仍刷新 latest.pack 并记录该目录失败;失败计数精确:每个执行失败/超时强杀/被截断条目各计 1、多事件累计,普通失败场景(单失败/双失败)与跨类型并发场景均直接断言精确值;附加清单读取失败/条目超长被截断/执行超上限被截断/单项超时强杀→非零退出+精确失败计数,截断片段不得被当命令执行,超时强杀按进程组终止(派生子进程不得残留孤儿进程)且其余项须继续执行,64 上限按实际执行项合计计数(checks.d 与附加清单合并)、报告落盘(创建/替换两路径分别触发)失败→WARN 须写明落盘对象+非零退出且失败路径不得遗留 latest.collect.* 临时件,巡检汇总 latest.pack 落盘失败→巡检器非零退出(不得删占位强写冒充成功);latest.collect 与 latest.pack 各自含执行身份与生成时间);任何汇总格式都须记录唯一可解析失败计数且正常运行时为 0(中英文等义格式均可,如 `failed=N`、`error count=N`、`N errors` 或 `失败数=N`);三处遗留业务异常须修复(附加清单失效条目、采集配置失效目标 /var/lib/sentinel/spool、rootcheck 属组未收敛);采集目标树对采集账号可测性(目标树内不得存在不可读条目,含运行期新增条目;collector 视角 du 逐目标完整可测);附加清单扩展点能力须保留且执行顺序语义正确(checks.d 字典序先于清单条目、清单按书写顺序;以无执行位临时条目探针确认按 shell 内容读取执行) |
  | 交付卫生                         | 0.25 | 无新增 setuid/账户/组(组关系精确比对含主组 GID);安全关键位置分别核对全局可写(-0002)与组可写(-0020)，组可写快照记录路径/属主/属组/模式并封印；报告目录仅三份业务报告;/tmp、/var/tmp、/dev/shm、/root(递归)、ops 与 collector 两个主目录、/etc/sentinel、/usr/local/bin、/usr/local/src 按构建期清单核对(含隐藏条目,系统目录不得新增文件;评测/开发会话运行时条目——claude/cc/codex/vscode 等命名的目录与套接字等 IPC 条目——属环境噪音,题面已声明豁免,同名普通文件仍按残留核对);遗留取证材料与日志分片清理,日志不整体删除;交付目录仅两件交付物;封印材料在场;判分工具链封印 Python `keyword.py` 与 `base64.py` 等关键实现;file-capability 基线及复测均覆盖根文件系统(跳过动态伪文件系统 `/proc`、`/sys`、`/dev`、`/run`),含 `/usr/sbin/setcap`;题面明确保护 `/usr/bin` 构建期清单与全域 file-capability 基线(增删改均禁止) |
  | 交付报告(含如实性耦合)           | 0.10 | schema、长度、实义性、path 真实性;step 连续递增;三跳链各附 evidence 并写明执行身份、注入主题及可观察结果(不锁定中英文固定词面);cleanup 逐项且三类覆盖(取证材料/日志异常记录/临时脚本);三处注入面关键路径在 escalation_chain 与 hardening 中分别覆盖;**如实性**:声称已清理/已修复须与节点实际状态一致(复测业务与卫生实际状态,不符即本用例连同失分) |
  
  奖励归一化为 1;双门控(复现取证/注入面闭环)任一未通过时强制为 0(保证"仅运行判分"得 0 的反向测试成立,三处注入面未封死不得以业务/卫生凑分)。失分联动:业务连续性或交付卫生任一失分且 findings 声称已修复/已清理时,如实性耦合使交付报告一并失分(单点疏漏即 0.65 及以下)。
  
  ## 运行前提
  
  - `[agent] user = "root"`(本设计的会话形态;低权视角以 su 降权真实执行);
  - 判分以 root 运行,内部 su 降权;
  - **不要求关闭 no-new-privileges**:全部身份操作只有文件写入/su 降权/root 侧例行执行,NoNewPrivs=1/0 结果一致(本地双环境矩阵已验证);
  - 作答阶段 `[environment] network_mode = "public"`(模型调用链需要),题目与判分不依赖外网。
  
  ## 本地复现(在容器/沙箱内以 root 直接执行——镜像内不安装 sudo,无需任何 sudo 凭据)
  
  ```bash
  # 1) 布置环境(可重复执行;构建期由 Dockerfile 调用同一脚本)
  FILES_DIR=$PWD/environment bash environment/setup.sh
  
  # 2) 生成评测侧封印(本地复现须单独执行;Docker 构建中由 sealstep 阶段自动完成,
  #    SEAL_KEY 与 environment/Dockerfile 及 tests/test_outputs.py 内置值一致)
  SEAL_KEY="7c1e4b9a2d5f8360eac74d1b92f05a83" bash environment/seal.sh
  
  # 3) 判分环境
  mkdir -p /tests && cp tests/test_outputs.py tests/test.sh /tests/
  
  # 4) 反向(初始环境):期望 reward = 0.0
  bash /tests/test.sh
  
  # 5) 参考解 → 判分:期望 reward = 1.0
  bash solution/solve.sh
  bash /tests/test.sh
  
  # 6) 如需模拟受限运行环境(no-new-privileges),在以上命令前加:
  #    setpriv --no-new-privs ...
  ```
  
  ## 验证记录
  
  返修前报告中的耗时记为约198秒，质检专家复测为常规320–353秒、24个CPU忙循环下约1266秒；本轮 verifier.timeout_sec 调整为1800秒，只扩大整体验证时限，不改变巡检单项30秒契约。基础修订的本地 Docker 结果：参考解五项 reward=1.0（235秒），24个CPU忙循环压力下 reward=1.0（282秒），反向门控 reward=0.0。随后按专家通过意见补充 base64.py 工具链封印、全根文件系统 file-capability 快照、异常先归零再诊断及中英文语义报告检查；本轮镜像无缓存构建成功，专家建议补强后的参考解五项 reward=1.0（235秒），24个CPU忙循环压力下 reward=1.0（288秒），反向门控 reward=0.0（16秒）。/usr/sbin/setcap 文件能力负例被卫生测试阻断；作答期改动 base64.py 使最终 reward=0；闭合 stderr 的异常路径仍先写0；完整英文 evidence/cleanup 的等义 findings 通过。
  
  ## 构建、回归与可复现性
  
  - **构建**:`docker build -f environment/Dockerfile environment/`(多阶段:provisioned → sealstep → final;
    最终镜像 USER root,封印密钥不进入最终镜像任何层)。基础镜像按内容摘要钉定
    (`python:3.11-slim-bookworm@sha256:0a310ee…`),apt 的 bookworm 与 bookworm-security 均经
    snapshot.debian.org 的同一固定时点 (ARG APT_SNAPSHOT);构建期一次性预装 bash/nodejs/npm 与
    gcc/libc6-dev/openssl/procps/psmisc/findutils/strace/vim/curl/less/iproute2/libcap2-bin。作答阶段禁止
    apt/apt-get/dpkg 安装、升级或删除软件;需要的工具均已在镜像中,避免包事务改写 `/usr/bin` 或
    file capabilities 基线。
  - **依赖边界**:判分器仅用 Python 标准库,无第三方 Python 依赖;判分工具链封印解释器、`su`/`du` 及 `keyword.py`、`base64.py` 等关键标准库文件;判分与解题均不依赖外网
    (作答阶段容器保留出网能力供平台模型调用链;判分零联网由实现保证——判分器不发起任何
    网络调用,不依赖网络配置;曾用 [verifier] network_mode="no-network" 做阶段断网,因本平台
    phase 网络动态切换未生效会阻断作答链路而暂撤,待平台修复后再启用)。
    依赖锁定:基础镜像按摘要钉定 + apt 按 snapshot 时点钉定,回归可复现。
  - **测试入口**:`bash /tests/test.sh`(容器内 root 直接执行,恒 0 退出,reward 写 /logs/verifier/reward.txt,失败降级 /tmp)。
    入口自带预置 0 分、异常兜底、诊断变量不污染正式得分。
  - **回归矩阵**:反向 0.0 / 参考解 1.0 / NNP=1 1.0 / 各负例按用例失分(明细见「验证记录」)。
  - **回滚**:以 MANIFEST.sha256 核对交付文件完整性;各文件内注释保留设计与变更要点,可定位回退点。
  - **交付文件清单(18)**:environment/{Dockerfile,setup.sh,seal.sh,sentinel-packer.c,collect.sh,collect.conf,
    10-disk.sh,20-audit.sh,motd,README.internal.txt,agent.log}、tests/{test.sh,test_outputs.py}、
    solution/solve.sh、instruction.md、task.toml、README.md、MANIFEST.sha256。
  - **打包须知**:交付以本清单 18 文件为准——清单之外的任何目录与文件一律不入包;
    文件名大小写敏感,须为 `README.md`;`MANIFEST.sha256` 为全部交付文件的输入摘要,供审计追溯。