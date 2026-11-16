# -*- coding: utf-8 -*-
"""4 分钟版（内容压缩版）：四部分内容全部保留，把相邻内容合并到一页，文字压缩。

做法：保留 25 页中的核心页，另用 deck_lib 新建 5 张“合并页”，
按“困境→流水线 / 覆盖+可信 / 验证+知识库 / 稳定性+可观测 / 复用+推广”重排为 15 页。
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE

sys.path.insert(0, '/home/user/123/build')
from deck_lib import *            # noqa
import deck_lib as D

SRC = '/home/user/123/源代码审计智能体-技术与成果汇报-完整版.pptx'
OUT = '/home/user/123/源代码审计智能体-4分钟版.pptx'

import copy as _copy

prs = Presentation(SRC)
# 用户保存后版式已被“压平”：底图与白底面板都在页面上，新建页需自行补上
BODY_TEMPLATE = prs.slides[5]
LAYOUT = BODY_TEMPLATE.slide_layout
_PIC = next(sh for sh in BODY_TEMPLATE.shapes if sh.shape_type == 13)
open('/tmp/body_bg.jpg', 'wb').write(_PIC.image.blob)
_PANEL = _copy.deepcopy(next(sh for sh in BODY_TEMPLATE.shapes
                             if sh.shape_type == 1 and abs(sh.width / 914400 - 12.70) < 0.05)._element)
sldIdLst = prs.slides._sldIdLst
old = list(sldIdLst)          # 25 页

# 保留的原始页（0 基）：封面 目录 价值四卡 创新总览 架构 辩论 成熟度 CyberGym 路线 致谢
KEEP = [0, 1, 5, 10, 11, 12, 16, 19, 23, 24]
keep_ids = [old[i] for i in KEEP]


def new_slide():
    s = prs.slides.add_slide(LAYOUT)
    s.shapes.add_picture('/tmp/body_bg.jpg', 0, 0, width=prs.slide_width, height=prs.slide_height)
    s.shapes._spTree.append(_copy.deepcopy(_PANEL))
    return s


# =====================================================================
# A 困境 + 流水线
# =====================================================================
sA = new_slide()
page_title(sA, '业务价值① 从四重困境到一条流水线', 3, 15)
rect(sA, X0, 1.30, 5.92, 5.04, fill=PALE, line=TINT, radius=0.04)
text(sA, X0 + 0.18, 1.42, 4.4, 0.28,
     [{'text': '传统审计的四重困境', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='A-l1')
pains = [('覆盖不全', '专家只能抽检，多语言、跨模块调用难以穷尽', '44 类专项 + 数据流追踪'),
         ('误报漏报', '规则只给线索，防护是否有效仍靠人工判断', '三方辩论核验'),
         ('结论难核实', '清单缺数据流与触发条件，无法实证', '11 字段证据链 + 实证'),
         ('经验难沉淀', '能力长在个人身上，随人员流动而波动', '知识库 + 错题本')]
for i, (t, d, cap) in enumerate(pains):
    y = 1.78 + i * 1.08
    num_badge(sA, X0 + 0.18, y + 0.02, 0.32, f'0{i+1}', size=8.5, fill=GOLD, color=INK)
    text(sA, X0 + 0.60, y, 1.60, 0.28, [{'text': t, 'size': 10.5, 'bold': True, 'color': INK, 'font': FONT_B}],
         spacing=1.0, tag='A-pt')
    text(sA, X0 + 0.60, y + 0.30, 5.02, 0.30, [{'text': d, 'size': 8.6, 'color': GRAY}], spacing=1.2, tag='A-pd')
    text(sA, X0 + 0.60, y + 0.62, 5.02, 0.28,
         [{'text': '→ ' + cap, 'size': 8.4, 'color': BLUE}], spacing=1.0, tag='A-pc')
    if i < 3:
        hline(sA, X0 + 0.18, y + 0.98, 5.56, color=TINT2, lw=0.5)

rect(sA, 6.74, 1.30, 5.98, 5.04, fill=WHITE, line=TINT, radius=0.04)
text(sA, 6.92, 1.42, 5.4, 0.28,
     [{'text': '九阶段流水线 · 全流程无人工介入', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='A-l2')
stages = [('知识库释放', '方法论/漏洞模式'), ('静态预扫描', '规则映射 + CWE'), ('代码分析', '技术栈/入口/依赖'),
          ('智能体筛选', '规则优先，补选防漏'), ('专项审计', '44 类并行挖掘'), ('去重收敛', '按类型与位置归并'),
          ('辩论核验', '正、反、裁三方'), ('漏洞验证', 'PoC 实证可达'), ('报告生成', '结构化 + 可读')]
for i, (t, d) in enumerate(stages):
    r, c = divmod(i, 3)
    x = 6.90 + c * 1.94
    y = 1.78 + r * 1.06
    hi = (i == 4)
    rect(sA, x, y, 1.80, 0.92, fill=BLUE if hi else PALE, line=None if hi else TINT, radius=0.06)
    text(sA, x + 0.12, y + 0.10, 1.5, 0.24,
         [{'text': f'{i+1:02d}', 'size': 7.6, 'bold': True, 'color': CREAM if hi else GOLD_D}], spacing=1.0, tag='A-sn')
    text(sA, x + 0.12, y + 0.34, 1.58, 0.26,
         [{'text': t, 'size': 8.8, 'bold': True, 'color': WHITE if hi else INK, 'font': FONT_B}], spacing=1.0, tag='A-st')
    text(sA, x + 0.12, y + 0.63, 1.60, 0.24,
         [{'text': d, 'size': 6.8, 'color': CREAM if hi else GRAY}], spacing=1.0, tag='A-sd')
text(sA, 6.92, 5.06, 5.6, 0.72,
     [{'text': '四类智能体：代码分析 · 专项审计 · 辩论核验 · 漏洞验证。规则可判定的交给代码，'
               '需要理解与推理的交给智能体。', 'size': 8.2, 'color': GRAY}], spacing=1.4, tag='A-n1')
text(sA, 6.92, 5.72, 5.6, 0.50,
     [{'text': '每阶段产物留档，进度、思维链、辩论对话实时推送前端。', 'size': 8.2, 'color': GOLD_D}],
     spacing=1.4, tag='A-n2')

# =====================================================================
# B 覆盖 + 可信
# =====================================================================
sB = new_slide()
page_title(sB, '业务价值② 覆盖 44 类专项 · 可信 11 字段证据链', 5, 15)
rect(sB, X0, 1.30, 5.34, 4.18, fill=PALE, line=TINT, radius=0.04)
text(sB, X0 + 0.18, 1.42, 4.6, 0.28,
     [{'text': '7 大类 · 44 个专项智能体', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='B-l1')
cats = [('注入类', 7, 'SQL · 命令 · 模板 · NoSQL'), ('Web 前端与交互', 6, 'XSS · CSRF · 上传 · 走私'),
        ('访问控制', 6, '认证绕过 · 越权 · 会话'), ('服务端与数据', 9, 'SSRF · XXE · 穿越 · 反序列化'),
        ('内存安全（C/C++）', 8, '栈/堆溢出 · UAF · 整数溢出'), ('业务与逻辑', 3, '业务逻辑 · 竞态 · 异常'),
        ('其他', 5, '依赖 CVE · 编码绕过 · 提示注入')]
for i, (c, n, d) in enumerate(cats):
    y = 1.76 + i * 0.50
    text(sB, X0 + 0.18, y, 1.55, 0.26, [{'text': c, 'size': 8.4, 'bold': True, 'color': INK, 'font': FONT_B}],
         spacing=1.0, tag='B-c')
    text(sB, X0 + 1.72, y, 0.28, 0.26, [{'text': str(n), 'size': 8.4, 'bold': True, 'color': GOLD_D, 'align': 'r'}],
         spacing=1.0, tag='B-n')
    text(sB, X0 + 2.10, y, 3.10, 0.26, [{'text': d, 'size': 7.2, 'color': GRAY}], spacing=1.0, tag='B-d')
    if i < 6:
        hline(sB, X0 + 0.18, y + 0.40, 5.00, color=TINT2, lw=0.5)
rect(sB, X0, 5.60, 5.34, 0.72, fill=WHITE, line=TINT, radius=0.05)
text(sB, X0 + 0.16, 5.60, 5.02, 0.72,
     [{'text': '三类场景：项目级全量/增量 · 漏洞实证复现 · 依赖组件筛查', 'size': 8.2, 'color': GRAY}],
     anchor='m', spacing=1.3, tag='B-scene')

rect(sB, 5.98, 1.30, 6.74, 5.02, fill=WHITE, line=TINT, radius=0.04)
text(sB, 6.16, 1.42, 5.0, 0.28,
     [{'text': '一条漏洞记录 = 11 个结构化字段', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='B-l2')
fields = ['标题', '危害等级', '漏洞类型', 'CWE 编号', '文件与行号', '完整数据流',
          '漏洞描述', '代码片段', '修复建议', '验证数据包', '辩论痕迹']
for i, f in enumerate(fields):
    r, c = divmod(i, 3)
    x = 6.16 + c * 2.14
    y = 1.76 + r * 0.60
    rect(sB, x, y, 2.02, 0.50, fill=PALE, line=TINT, radius=0.10)
    text(sB, x + 0.12, y, 1.80, 0.50, [{'text': f, 'size': 8.6, 'color': INK}], anchor='m',
         spacing=1.0, tag='B-f')
hline(sB, 6.16, 4.44, 6.40, color=TINT2, lw=0.75)
text(sB, 6.16, 4.52, 3.0, 0.26,
     [{'text': '三级质量闸门', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}], spacing=1.0, tag='B-g')
gates = [('规则去重', '同类型同位置归并'), ('辩论核验', '采纳 / 驳回 / 存疑'), ('实证验证', '隔离环境实发请求')]
for i, (t, d) in enumerate(gates):
    x = 6.16 + i * 2.14
    rect(sB, x, 4.82, 2.02, 0.66, fill=PALE, line=TINT, radius=0.08)
    text(sB, x + 0.12, 4.86, 1.80, 0.26, [{'text': t, 'size': 8.8, 'bold': True, 'color': INK, 'font': FONT_B}],
         spacing=1.0, tag='B-gt')
    text(sB, x + 0.12, 5.12, 1.82, 0.30, [{'text': d, 'size': 7.4, 'color': GRAY}], spacing=1.0, tag='B-gd')
text(sB, 6.16, 5.68, 6.36, 0.52,
     [{'text': '过三道闸门后：可复核、可追责、可复测；报告里的每个漏洞都能回查到智能体与裁决记录。',
       'size': 8.2, 'color': GOLD_D}], spacing=1.35, tag='B-n')

# =====================================================================
# C 验证 + 知识库
# =====================================================================
sC = new_slide()
page_title(sC, '创新三 · 创新四 实证验证与知识库自进化', 9, 15)
rect(sC, X0, 1.30, 6.00, 5.04, fill=PALE, line=TINT, radius=0.04)
text(sC, X0 + 0.18, 1.42, 5.4, 0.28,
     [{'text': '创新三 漏洞实证：从代码推断到运行时证实', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='C-l1')
vsteps = [('接收上下文', '漏洞位置、描述、数据流、代码片段与验证包一并下发'),
          ('构造 PoC', '隔离容器内自动构造最小化验证脚本，不依赖人工'),
          ('实发请求', '对受控环境发起真实请求，验证可达性与可触发性'),
          ('结论沉淀', '输出通过/失败，并归集可复用的关键技术信息')]
for i, (t, d) in enumerate(vsteps):
    y = 1.80 + i * 0.86
    num_badge(sC, X0 + 0.18, y + 0.04, 0.34, str(i + 1), size=8.5)
    text(sC, X0 + 0.62, y, 1.5, 0.26, [{'text': t, 'size': 9.4, 'bold': True, 'color': INK, 'font': FONT_B}],
         spacing=1.0, tag='C-vt')
    text(sC, X0 + 0.62, y + 0.28, 5.16, 0.46, [{'text': d, 'size': 8.2, 'color': GRAY}], spacing=1.25, tag='C-vd')
hline(sC, X0 + 0.18, 5.22, 5.60, color=TINT2, lw=0.75)
text(sC, X0 + 0.18, 5.30, 5.62, 0.90,
     [{'text': '安全红线写进提示词：只证存在不做利用 · 禁破坏性操作 · 不碰真实数据 · 脚本只写临时目录 · '
               '并发 3、单漏洞 ≤3 次 · 默认关闭，仅限受控环境。', 'size': 7.8, 'color': GOLD_D}],
     spacing=1.35, tag='C-red')

rect(sC, 6.74, 1.30, 5.98, 5.04, fill=WHITE, line=TINT, radius=0.04)
text(sC, 6.92, 1.42, 5.4, 0.28,
     [{'text': '创新四 知识库驱动：三类知识 + 自进化闭环', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='C-l2')
kbs = [('技能类', '审计方法论：攻击面分析、数据流追踪、危害评级'),
       ('智能体类', '正、反、裁辩论角色定义与举证、质疑规范'),
       ('知识文档类', '漏洞模式库、安全编码指南、错题本')]
for i, (t, d) in enumerate(kbs):
    y = 1.80 + i * 0.66
    rect(sC, 6.92, y, 5.58, 0.58, fill=PALE, line=TINT, radius=0.10)
    text(sC, 7.04, y, 1.10, 0.58, [{'text': t, 'size': 8.8, 'bold': True, 'color': INK, 'font': FONT_B}],
         anchor='m', spacing=1.0, tag='C-kt')
    text(sC, 8.18, y, 4.20, 0.58, [{'text': d, 'size': 8.2, 'color': GRAY}], anchor='m',
         spacing=1.2, tag='C-kd')
text(sC, 6.92, 3.88, 4.0, 0.26,
     [{'text': '自进化闭环', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}], spacing=1.0, tag='C-loop')
loop = ['执行', '反思', '更新', '验证']
for i, t in enumerate(loop):
    x = 6.92 + i * 1.42
    chip(sC, x, 4.18, 1.28, 0.50, t, size=8.6, fill=BLUE if i == 3 else PALE,
         color=WHITE if i == 3 else BLUE_D, line=None if i == 3 else TINT2, radius=0.3)
    if i < 3:
        arrow(sC, x + 1.30, 4.35, 0.10, 0.14, color=GOLD)
text(sC, 6.92, 4.86, 5.58, 0.60,
     [{'text': '候选技能树过独立门控、同口径比较，提升才接纳；误报经错题本回流，审计越多判断越准。',
       'size': 8.2, 'color': GRAY}], spacing=1.35, tag='C-n1')
text(sC, 6.92, 5.52, 5.58, 0.50,
     [{'text': '知识按任务释放，任务前全量刷新，避免陈旧内容污染。', 'size': 8.2, 'color': GOLD_D}],
     spacing=1.3, tag='C-n2')

# =====================================================================
# D 稳定性 + 可观测
# =====================================================================
sD = new_slide()
page_title(sD, '成熟度② 稳定性与可观测：单点失败不阻断审计', 11, 15)
rect(sD, X0, 1.30, 6.20, 5.04, fill=PALE, line=TINT, radius=0.04)
text(sD, X0 + 0.18, 1.42, 5.6, 0.28,
     [{'text': '异常分级与降级处理', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='D-l1')
faults = [('静态扫描失败', '记录错误，以空结果继续'),
          ('代码分析解析失败', '恢复已存结果，否则启动全部专项'),
          ('单个专项智能体失败', '跳过，不影响整体任务'),
          ('执行容器连接失败', '任务立即标记失败，不留挂起'),
          ('管理端重启', '自动恢复未完结任务，清理孤儿容器')]
for i, (a, b) in enumerate(faults):
    y = 1.78 + i * 0.64
    if i % 2 == 0:
        rect(sD, X0 + 0.10, y - 0.06, 6.00, 0.56, fill=WHITE, line=None, radius=0.10)
    text(sD, X0 + 0.22, y, 2.10, 0.44, [{'text': a, 'size': 8.8, 'bold': True, 'color': INK, 'font': FONT_B}],
         anchor='m', spacing=1.1, tag='D-fa')
    text(sD, X0 + 2.42, y, 3.62, 0.44, [{'text': b, 'size': 8.6, 'color': GRAY}], anchor='m',
         spacing=1.1, tag='D-fb')
hline(sD, X0 + 0.18, 5.12, 5.86, color=TINT2, lw=0.75)
text(sD, X0 + 0.18, 5.22, 5.88, 0.90,
     [{'text': '资源与安全边界：单任务 48 小时 · 专项并发 3 · 默认并发 1 · 双容器独立配额 · '
               '任务间独立网桥 · 联网类工具一律禁用。', 'size': 7.8, 'color': GOLD_D}],
     spacing=1.35, tag='D-lim')

rect(sD, 7.00, 1.30, 5.72, 5.04, fill=WHITE, line=TINT, radius=0.04)
text(sD, 7.18, 1.42, 5.2, 0.28,
     [{'text': '过程可观测：审计不是黑盒', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='D-l2')
evs = ['进度', '阶段消息', '思维链', '工具调用与结果', '漏洞发现', '辩论对话', '回合统计（token/时长）', '报告分节产出']
for i, e in enumerate(evs):
    r, c = divmod(i, 2)
    x = 7.18 + c * 2.70
    y = 1.80 + r * 0.54
    chip(sD, x, y, 2.58, 0.44, e, size=7.8, fill=PALE, color=INK, line=TINT, radius=0.3)
text(sD, 7.18, 4.12, 4.0, 0.26,
     [{'text': '留档与回溯', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}], spacing=1.0, tag='D-arc')
arcs = ['分阶段留档：扫描、分析、漏洞清单、报告统一归档',
        '下游确定性代码直接消费留档数据，不再二次理解文字']
for i, a in enumerate(arcs):
    y = 4.42 + i * 0.50
    text(sD, 7.18, y, 5.28, 0.46, [{'text': '· ' + a, 'size': 8.2, 'color': GRAY}], spacing=1.3, tag='D-a')
text(sD, 7.18, 5.52, 5.28, 0.60,
     [{'text': '结论可被信任、可被追责、可被复算——这是智能体审计进入生产流程的前提。',
       'size': 8.4, 'color': GOLD_D}], spacing=1.35, tag='D-n')

# =====================================================================
# E 复用 + 推广
# =====================================================================
sE = new_slide()
page_title(sE, '推广复用：配置化复用 + 四类场景三步走', 13, 15)
rect(sE, X0, 1.30, 5.60, 2.56, fill=PALE, line=TINT, radius=0.04)
text(sE, X0 + 0.18, 1.42, 5.1, 0.28,
     [{'text': '一份任务描述 = 一次审计', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='E-l1')
task = ['代码位置与语言', '流程开关', '模型配置', '定制知识库', '自定义智能体']
for i, t in enumerate(task):
    r, c = divmod(i, 2)
    chip(sE, X0 + 0.18 + c * 2.56, 1.78 + r * 0.50, 2.38, 0.42, t, size=8.4,
         fill=WHITE, color=BLUE_D, line=TINT2, radius=0.3)
text(sE, X0 + 0.18, 3.42, 5.20, 0.34,
     [{'text': '有特殊需求时，换一份任务描述即可，无需改动系统。', 'size': 8.2, 'color': GOLD_D}],
     spacing=1.3, tag='E-n1')

rect(sE, X0, 4.02, 5.60, 2.32, fill=WHITE, line=TINT, radius=0.04)
text(sE, X0 + 0.18, 4.14, 4.0, 0.26,
     [{'text': '四类复用', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}], spacing=1.0, tag='E-l2')
reuse = ['交付：镜像 + Compose，常驻仅控制平面与扫描服务',
         '策略：专项白名单、任务级提示词、知识集覆盖',
         '扩展：新增漏洞类型只需一份 YAML 定义',
         '接入：API-Key 鉴权 + 事件通道，可被平台/CICD 调用']
for i, r in enumerate(reuse):
    text(sE, X0 + 0.18, 4.46 + i * 0.42, 5.24, 0.34, [{'text': '· ' + r, 'size': 8.0, 'color': GRAY}],
         spacing=1.2, tag='E-r')

rect(sE, 6.40, 1.30, 6.32, 2.90, fill=PALE, line=TINT, radius=0.04)
text(sE, 6.58, 1.42, 5.4, 0.28,
     [{'text': '四类推广场景', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}], spacing=1.0, tag='E-l3')
scenes = [('研发自检', '开发/测试团队', '关键模块审计 · 修改后复测'),
          ('上线前过检', '安全/研发团队', '版本集中检查 · 上线评审依据'),
          ('安全专项检查', '安全团队', '聚焦风险类型 · 定向排查'),
          ('平台化接入', '企业平台 / CI/CD', 'Webhook 触发 · 质量门禁')]
for i, (t, who, cap) in enumerate(scenes):
    y = 1.78 + i * 0.64
    text(sE, 6.58, y, 1.42, 0.28, [{'text': t, 'size': 8.8, 'bold': True, 'color': INK, 'font': FONT_B}],
         spacing=1.0, tag='E-sc-t')
    text(sE, 8.06, y, 2.10, 0.28, [{'text': who, 'size': 7.4, 'color': GOLD_D}], spacing=1.0, tag='E-sc-w')
    text(sE, 10.20, y, 2.38, 0.28, [{'text': cap, 'size': 7.6, 'color': GRAY}], spacing=1.0, tag='E-sc-c')

rect(sE, 6.40, 4.36, 6.32, 1.98, fill=WHITE, line=TINT, radius=0.04)
text(sE, 6.58, 4.46, 4.0, 0.26,
     [{'text': '推广三步走', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}], spacing=1.0, tag='E-l4')
steps = [('第一步', '试点项目验证'), ('第二步', '专业条线复制'), ('第三步', '全域平台接入')]
for i, (n, t) in enumerate(steps):
    x = 6.58 + i * 2.02
    rect(sE, x, 4.78, 1.92, 0.74, fill=PALE, line=TINT, radius=0.08)
    text(sE, x + 0.10, 4.82, 1.72, 0.24, [{'text': n, 'size': 7.0, 'color': GOLD_D}], spacing=1.0, tag='E-st-n')
    text(sE, x + 0.10, 5.06, 1.74, 0.42, [{'text': t, 'size': 8.2, 'bold': True, 'color': INK}],
         spacing=1.2, tag='E-st-t')
text(sE, 6.58, 5.66, 6.00, 0.50,
     [{'text': '同一套方法论与知识集：项目越多，错题本越厚，边际成本越低。', 'size': 8.2, 'color': GOLD_D}],
     spacing=1.3, tag='E-n2')

# =====================================================================
# 组装顺序：封面 目录 A 价值 创新总览 架构 辩论 C 成熟度 D CyberGym E 路线 致谢
# =====================================================================
# 取新建页的 sldId 元素（新增页在末尾，按创建顺序）
tail = list(sldIdLst)[len(old):]
idA, idB, idC, idD, idE = tail[0], tail[1], tail[2], tail[3], tail[4]

order = [old[0], old[1], idA, old[5], idB, old[10], old[11], old[12], idC,
         old[16], idD, old[19], idE, old[23], old[24]]
assert len(order) == 15

for sid in list(sldIdLst):
    if sid not in order:
        prs.part.drop_rel(sid.rId)
        sldIdLst.remove(sid)
for sid in list(sldIdLst):
    sldIdLst.remove(sid)
for sid in order:
    sldIdLst.append(sid)

# 页脚统一为 NN / 15
import re
for no, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        if sh.has_text_frame and re.fullmatch(r'\d\d\s*/\s*\d\d', sh.text_frame.text.strip()):
            p = sh.text_frame.paragraphs[0]
            p.runs[0].text = f'{no:02d} / 15'
            for r in p.runs[1:]:
                r.text = ''

# =====================================================================
# 逐页汇报词（与页面内容一一对应，总计 ≈ 4 分钟）
# =====================================================================
BODY = {
1: ('开场', '各位评委好。今天汇报瑞智源代码审计智能体——用多智能体把专家经验工程化，让代码审计成为可复制的流水线。'),
2: ('结构', '汇报四部分：业务价值、技术创新、成熟度与稳定性、推广复用。'),
3: ('困境与解法', '传统审计卡在四点：只能抽检、误报漏报、结论难实证、经验难沉淀，专家能力成了产能天花板。'
                '我们的解法是九个阶段的流水线：知识库释放、静态扫描、代码分析、智能体筛选，44 类专项并行挖掘，'
                '去重后过辩论与实证两道质量关，最后自动出报告，全程无人工介入。'),
4: ('四项价值', '价值四点：覆盖更全，44 类专项逐类追踪数据流；结论更准，候选漏洞全部经三方辩论，驳回不入库；'
              '响应更快，增量模式只审变动文件；沉淀可复用，方法论与错题本进知识库。'),
5: ('覆盖与可信', '覆盖上是 7 大类 44 个专项智能体；可信上每条漏洞固定 11 个字段，带 CWE、行号和完整数据流，'
                '再过规则去重、辩论核验、实证验证三道闸门，可复核、可追责、可复测。'),
6: ('创新总览', '四项创新：编排解决做得全，辩论解决判得准，实证解决能落地，知识库解决经验积累。'),
7: ('架构', '架构上控制与执行分离：控制平面不碰被审计代码，只负责任务、事件、容器与配置；'
          '分析能力全部下沉到一次性执行容器，跑完即回收。'),
8: ('辩论', '重点讲辩论。反方假设是误报、依托代码逐条质疑，正方必须构建攻击链回应，裁判按可达性终裁。'
          '结局三态：采纳入库、驳回不入库、存疑交人工——误报在下游之前就被拦掉。'),
9: ('验证与知识库', '验证在隔离容器里构造 PoC 实发请求，把推断变成实测，红线写进提示词：只证存在、不做利用。'
                 '知识库三类知识随任务释放，执行、反思、更新、验证闭环，误报经错题本回流。'),
10: ('成熟度', '这已是可用系统：双平面落地，44 类专项加五类阶段智能体全部实现，知识集可任务级定制，隔离、配额、白名单都已落地。'),
11: ('稳定性与可观测', '稳定性靠分级处理：扫描失败降级继续、单点失败跳过、重启自动恢复。过程全程可观测，'
                   '每个结论都能回查到智能体与分析依据。'),
12: ('效果', '效果有外部参照：CyberGym Level 1 独立测评，严格通过率 91.4%，1377 项任务成功，公开榜单第 9 名。'),
13: ('推广', '换一份任务描述就能复用：五类配置项覆盖代码、流程、模型与知识；四类场景从研发自检到平台化接入；'
           '节奏三步走——试点、条线复制、全域接入。'),
14: ('路线', '后续三个版本：先把评估体系建起来，再优化深度与效率，最后做场景集成与规模化。'),
15: ('收尾', '总结一句：把经验工程化，把不确定性变成可证伪，让结论站得住，让它能被复制。请评委批评指正，谢谢。'),
}
RATE = 240.0
t = 0.0
for i, sl in enumerate(prs.slides, 1):
    tag, body = BODY[i]
    dur = len(body) / RATE * 60
    sl.notes_slide.notes_text_frame.text = (
        f'【{int(t)//60}:{int(t)%60:02d}–{int(t+dur)//60}:{int(t+dur)%60:02d} {tag}】\n{body}')
    t += dur

prs.core_properties.title = '瑞智源代码审计智能体（4 分钟汇报版 · 内容压缩）'
prs.save(OUT)
chars = sum(len(v[1]) for v in BODY.values())
print('saved', OUT, 'slides', len(prs.slides))
print(f'汇报词 {chars} 字 ≈ {chars/RATE:.2f} 分钟')
D.report()
