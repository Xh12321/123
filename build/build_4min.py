# -*- coding: utf-8 -*-
"""4 分钟版（内容压缩 + 图文并茂）。

- 保留核心原页，另建 7 张页：3 张纯合并页、4 张“图文”页（用参考 PPT 里的真实截图与插图）。
- 页序：封面 目录 困境+流水线 价值 覆盖+可信 创新总览 架构(图) 辩论(图) 验证+知识库(图)
  成熟度 稳定性+可观测(图) CyberGym 推广+复用 路线 致谢
"""
import sys, copy as _copy, re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE

sys.path.insert(0, '/home/user/123/build')
from deck_lib import *            # noqa
import deck_lib as D

SRC = '/home/user/123/源代码审计智能体-技术与成果汇报-完整版.pptx'
OUT = '/home/user/123/源代码审计智能体-4分钟版.pptx'
AST = '/home/user/123/build/assets/'

prs = Presentation(SRC)
BODY_TPL = prs.slides[5]
LAYOUT = BODY_TPL.slide_layout
_PIC = next(sh for sh in BODY_TPL.shapes if sh.shape_type == 13)
open('/tmp/body_bg.jpg', 'wb').write(_PIC.image.blob)
_PANEL = _copy.deepcopy(next(sh for sh in BODY_TPL.shapes
                             if sh.shape_type == 1 and abs(sh.width / 914400 - 12.70) < 0.05)._element)
sldIdLst = prs.slides._sldIdLst
old = list(sldIdLst)


def new_slide(no, title, note=None):
    s = prs.slides.add_slide(LAYOUT)
    s.shapes.add_picture('/tmp/body_bg.jpg', 0, 0, width=prs.slide_width, height=prs.slide_height)
    s.shapes._spTree.append(_copy.deepcopy(_PANEL))
    page_title(s, title, no, 15, note=note)
    return s


def figure(s, path, x, y, w, caption=None, cap_w=None):
    pic = s.shapes.add_picture(path, Inches(x), Inches(y), width=Inches(w))
    h = pic.height / 914400
    # 细边框，避免截图与白底面板粘在一起
    fr = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pic.left, pic.top, pic.width, pic.height)
    fr.fill.background()
    fr.line.color.rgb = TINT2
    fr.line.width = Pt(0.75)
    fr.shadow.inherit = False
    if caption:
        text(s, x, y + h + 0.08, cap_w or w, 0.28,
             [{'text': caption, 'size': 7.6, 'color': GRAY2}], spacing=1.15, tag='fig-cap')
    return y + h


# =====================================================================
# P3 困境 + 流水线
# =====================================================================
sA = new_slide(3, '业务价值① 从四重困境到一条流水线')
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
    text(sA, X0 + 0.60, y + 0.62, 5.02, 0.28, [{'text': '→ ' + cap, 'size': 8.4, 'color': BLUE}],
         spacing=1.0, tag='A-pc')
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
    x, y = 6.90 + c * 1.94, 1.78 + r * 1.06
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
# P5 覆盖 + 可信
# =====================================================================
sB = new_slide(5, '业务价值② 覆盖 44 类专项 · 可信 11 字段证据链')
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

rect(sB, 5.98, 1.30, 6.74, 5.32, fill=WHITE, line=TINT, radius=0.04)
text(sB, 6.16, 1.42, 5.0, 0.28,
     [{'text': '一条漏洞记录 = 11 个结构化字段', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='B-l2')
fields = ['标题', '危害等级', '漏洞类型', 'CWE 编号', '文件与行号', '完整数据流',
          '漏洞描述', '代码片段', '修复建议', '验证数据包', '辩论痕迹']
for i, f in enumerate(fields):
    r, c = divmod(i, 3)
    x, y = 6.16 + c * 2.14, 1.72 + r * 0.54
    rect(sB, x, y, 2.02, 0.46, fill=PALE, line=TINT, radius=0.10)
    text(sB, x + 0.12, y, 1.80, 0.46, [{'text': f, 'size': 8.6, 'color': INK}], anchor='m',
         spacing=1.0, tag='B-f')
figure(sB, AST + 'ui_report.png', 6.30, 3.36, 6.10,
       caption='平台实拍：漏洞清单（编号 / 类型 / 风险等级）与漏洞统计', cap_w=6.10)
text(sB, 6.30, 6.24, 6.10, 0.30,
     [{'text': '过三道闸门（规则去重 → 辩论核验 → 实证验证）后，结论可复核、可追责、可复测。',
       'size': 7.8, 'color': GOLD_D}], spacing=1.2, tag='B-n')

# =====================================================================
# P7 架构 + 部署架构图
# =====================================================================
sF = new_slide(7, '创新一 控制与执行分离的多智能体编排架构')
layers = [('控制平面', ['任务生命周期', '双向事件通道', '容器编排', 'API-Key 鉴权'], '不接触被审计代码'),
          ('执行平面', ['编排器', '状态跟踪', '事件管理', '结果留档'], '任务级一次性容器'),
          ('能力层', ['44 类专项', '静态扫描', '知识图谱', '辩论/验证'], '可插拔的分析能力')]
for i, (name, items, cap) in enumerate(layers):
    y = 1.36 + i * 1.42
    rect(sF, X0, y, 3.92, 1.26, fill=PALE, line=TINT, radius=0.05)
    rect(sF, X0, y, 0.06, 1.26, fill=BLUE, shape=MSO_SHAPE.RECTANGLE)
    text(sF, X0 + 0.20, y + 0.12, 1.9, 0.28, [{'text': name, 'size': 10, 'bold': True, 'color': INK, 'font': FONT_B}],
         spacing=1.0, tag='F-lt')
    text(sF, X0 + 2.10, y + 0.13, 1.68, 0.26, [{'text': cap, 'size': 7.2, 'color': GOLD_D, 'align': 'r'}],
         spacing=1.0, tag='F-lc')
    for j, it in enumerate(items):
        r, c = divmod(j, 2)
        chip(sF, X0 + 0.20 + c * 1.86, y + 0.48 + r * 0.38, 1.72, 0.32, it, size=7.4,
             fill=WHITE, color=BLUE_D, line=TINT2, radius=0.3)
text(sF, X0, 5.66, 3.92, 0.90,
     [{'text': '控制平面只管任务、事件、容器与配置；分析能力全部下沉到一次性执行容器，跑完即回收。',
       'size': 8.0, 'color': GRAY}], spacing=1.35, tag='F-note')

figure(sF, AST + 'arch_deploy.png', 4.78, 1.36, 7.94,
       caption='部署视图：Manager 与静态扫描常驻；Worker、AI 执行容器按任务创建、退出即回收', cap_w=7.94)
text(sF, 4.78, 5.34, 7.90, 0.28,
     [{'text': '关键设计', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}], spacing=1.0, tag='F-k')
keys = ['规则先行：能靠规则确定的用代码解决，需推理的交给智能体',
        '确定性筛选：扫描命中即强制补选，拿不准的一律保留',
        '资源复用：多个智能体共用 AI 引擎容器，结束按标签回收',
        '双模型：支持内网模型部署或外部模型 API 接入']
for i, k in enumerate(keys):
    r, c = divmod(i, 2)
    text(sF, 4.78 + c * 4.00, 5.66 + r * 0.34, 3.86, 0.30,
         [{'text': '· ' + k, 'size': 7.4, 'color': GRAY}], spacing=1.2, tag='F-kk')

# =====================================================================
# P8 辩论 + 插画
# =====================================================================
sG = new_slide(8, '创新二 正、反、裁三方辩论：把幻觉变成可证伪')
deb = ['候选漏洞', '反方质疑', '正方举证', '反方复判', '裁判终裁']
for i, t in enumerate(deb):
    x = 0.70 + i * 2.48
    hi = (i == 4)
    rect(sG, x, 1.34, 2.30, 0.56, fill=BLUE if hi else PALE, line=None if hi else TINT, radius=0.2)
    text(sG, x, 1.34, 2.30, 0.56, [{'text': f'{i+1:02d}  {t}', 'size': 8.6, 'bold': True,
                                   'color': WHITE if hi else INK, 'align': 'c', 'font': FONT_B}],
         anchor='m', spacing=1.0, tag='G-step')
    if i < 4:
        arrow(sG, x + 2.32, 1.58, 0.14, 0.10, color=BLUE_M)

figure(sG, AST + 'debate_flow.png', X0, 2.14, 6.86,
       caption='复核去重 → 证据与限制条件逐条对照 → 正、反、裁三方对话留下复核线索', cap_w=6.86)
text(sG, X0, 5.44, 6.86, 0.90,
     [{'text': '反方假设是误报、依托实际代码逐条质疑，正方必须构建攻击链回应；'
               '辩论的角色、观点与轮次以结构化事件实时推送，并随漏洞入库。', 'size': 8.0, 'color': GRAY}],
     spacing=1.35, tag='G-n1')

rx = 7.70
text(sG, rx, 2.14, 4.8, 0.28, [{'text': '裁判三类终裁与处置', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='G-h')
outs = [('采纳', '进入漏洞记录，随报告输出', BLUE), ('驳回', '一律不入库，直接过滤', GRAY2),
        ('存疑', '仍然输出并单独标注，交人工复核', GOLD)]
for i, (t, d, c) in enumerate(outs):
    y = 2.46 + i * 0.86
    rect(sG, rx, y, 5.00, 0.74, fill=WHITE, line=TINT, radius=0.06)
    rect(sG, rx, y, 0.06, 0.74, fill=c, shape=MSO_SHAPE.RECTANGLE)
    text(sG, rx + 0.20, y, 0.80, 0.74, [{'text': t, 'size': 11, 'bold': True, 'color': c, 'font': FONT_B}],
         anchor='m', spacing=1.0, tag='G-ot')
    text(sG, rx + 1.02, y, 3.86, 0.74, [{'text': d, 'size': 8.2, 'color': GRAY}], anchor='m',
         spacing=1.3, tag='G-od')
rect(sG, rx, 5.16, 5.00, 1.06, fill=PALE, line=TINT, radius=0.05)
text(sG, rx + 0.20, 5.24, 4.62, 0.90,
     [{'text': '为什么有效：把自由生成改造成“立场对立、逐条举证”的可检验过程——'
               '误报在进报告之前就被拦掉。', 'size': 8.2, 'color': BLUE_D}], spacing=1.35, tag='G-why')

# =====================================================================
# P9 验证 + 知识库 + 插画
# =====================================================================
sC = new_slide(9, '创新三 · 创新四 实证验证与知识库自进化')
figure(sC, AST + 'verify_flow.png', X0, 1.34, 6.10,
       caption='验证链路：候选漏洞 + 验证条件 → 条件检查 → 受控环境实发请求 → 状态与证据入报告', cap_w=6.10)
steps = ['① 接收上下文', '② 构造 PoC', '③ 实发请求', '④ 结论沉淀']
for i, t in enumerate(steps):
    chip(sC, X0 + i * 1.55, 4.34, 1.42, 0.40, t, size=7.6, fill=WHITE, color=BLUE_D, line=TINT2, radius=0.3)
text(sC, X0, 4.86, 6.10, 0.90,
     [{'text': '安全红线写进提示词：只证存在不做利用 · 禁破坏性操作 · 不碰真实数据 · 脚本只写临时目录 · '
               '并发 3、单漏洞 ≤3 次 · 默认关闭，仅限受控环境。', 'size': 7.8, 'color': GOLD_D}],
     spacing=1.35, tag='C-red')

rect(sC, 6.96, 1.34, 5.76, 4.98, fill=WHITE, line=TINT, radius=0.04)
text(sC, 7.14, 1.46, 5.2, 0.28,
     [{'text': '知识库：三类知识 + 自进化闭环', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='C-l2')
kbs = [('技能类', '审计方法论：攻击面分析、数据流追踪、危害评级'),
       ('智能体类', '正、反、裁辩论角色定义与举证、质疑规范'),
       ('知识文档类', '漏洞模式库、安全编码指南、错题本')]
for i, (t, d) in enumerate(kbs):
    y = 1.84 + i * 0.66
    rect(sC, 7.14, y, 5.40, 0.58, fill=PALE, line=TINT, radius=0.10)
    text(sC, 7.26, y, 1.10, 0.58, [{'text': t, 'size': 8.8, 'bold': True, 'color': INK, 'font': FONT_B}],
         anchor='m', spacing=1.0, tag='C-kt')
    text(sC, 8.40, y, 4.02, 0.58, [{'text': d, 'size': 8.0, 'color': GRAY}], anchor='m',
         spacing=1.2, tag='C-kd')
text(sC, 7.14, 3.94, 4.0, 0.26, [{'text': '自进化闭环', 'size': 9.0, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='C-loop')
for i, t in enumerate(['执行', '反思', '更新', '验证']):
    x = 7.14 + i * 1.36
    chip(sC, x, 4.22, 1.24, 0.48, t, size=8.4, fill=BLUE if i == 3 else PALE,
         color=WHITE if i == 3 else BLUE_D, line=None if i == 3 else TINT2, radius=0.3)
    if i < 3:
        arrow(sC, x + 1.26, 4.38, 0.08, 0.14, color=GOLD)
text(sC, 7.14, 4.86, 5.40, 0.60,
     [{'text': '候选技能树过独立门控、同口径比较，提升才接纳；误报经错题本回流，越用越准。',
       'size': 8.0, 'color': GRAY}], spacing=1.3, tag='C-n1')
text(sC, 7.14, 5.52, 5.40, 0.50,
     [{'text': '知识按任务释放，任务前全量刷新，避免陈旧内容污染。', 'size': 8.0, 'color': GOLD_D}],
     spacing=1.3, tag='C-n2')

# =====================================================================
# P11 稳定性 + 可观测（平台实拍）
# =====================================================================
sD = new_slide(11, '成熟度② 稳定性与可观测：单点失败不阻断')
rect(sD, X0, 1.30, 6.10, 5.04, fill=PALE, line=TINT, radius=0.04)
text(sD, X0 + 0.18, 1.42, 5.5, 0.28,
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
        rect(sD, X0 + 0.10, y - 0.06, 5.90, 0.56, fill=WHITE, line=None, radius=0.10)
    text(sD, X0 + 0.22, y, 2.06, 0.44, [{'text': a, 'size': 8.6, 'bold': True, 'color': INK, 'font': FONT_B}],
         anchor='m', spacing=1.1, tag='D-fa')
    text(sD, X0 + 2.34, y, 3.56, 0.44, [{'text': b, 'size': 8.4, 'color': GRAY}], anchor='m',
         spacing=1.1, tag='D-fb')
hline(sD, X0 + 0.18, 5.12, 5.76, color=TINT2, lw=0.75)
text(sD, X0 + 0.18, 5.22, 5.78, 0.90,
     [{'text': '资源与安全边界：单任务 48 小时 · 专项并发 3 · 默认并发 1 · 双容器独立配额 · '
               '任务间独立网桥 · 联网类工具一律禁用。', 'size': 7.8, 'color': GOLD_D}],
     spacing=1.35, tag='D-lim')

figure(sD, AST + 'ui_activity.png', 6.94, 1.34, 5.78,
       caption='平台实拍：思维链、工具调用与漏洞列表（HIGH / 未核验）实时可见', cap_w=5.78)
text(sD, 6.94, 5.46, 5.76, 0.86,
     [{'text': '留档与回溯：扫描、分析、漏洞清单、报告统一归档；每个结论都能回查到'
               '哪个智能体、依据哪份分析、由谁裁决。', 'size': 8.0, 'color': GRAY}],
     spacing=1.35, tag='D-n')

# =====================================================================
# P13 推广复用
# =====================================================================
sE = new_slide(13, '推广复用：配置化复用 + 四类场景三步走')
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
text(sE, X0 + 0.18, 4.14, 4.0, 0.26, [{'text': '四类复用', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='E-l2')
reuse = ['交付：镜像 + Compose，常驻仅控制平面与扫描服务',
         '策略：专项白名单、任务级提示词、知识集覆盖',
         '扩展：新增漏洞类型只需一份 YAML 定义',
         '接入：API-Key 鉴权 + 事件通道，可被平台/CICD 调用']
for i, r in enumerate(reuse):
    text(sE, X0 + 0.18, 4.46 + i * 0.42, 5.24, 0.34, [{'text': '· ' + r, 'size': 8.0, 'color': GRAY}],
         spacing=1.2, tag='D-r')

rect(sE, 6.40, 1.30, 6.32, 2.90, fill=PALE, line=TINT, radius=0.04)
text(sE, 6.58, 1.42, 5.4, 0.28, [{'text': '四类推广场景', 'size': 9.5, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='E-l3')
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
text(sE, 6.58, 4.46, 4.0, 0.26, [{'text': '推广三步走', 'size': 9.2, 'bold': True, 'color': BLUE, 'font': FONT_B}],
     spacing=1.0, tag='E-l4')
steps3 = [('第一步', '试点项目验证'), ('第二步', '专业条线复制'), ('第三步', '全域平台接入')]
for i, (n, t) in enumerate(steps3):
    x = 6.58 + i * 2.02
    rect(sE, x, 4.78, 1.92, 0.74, fill=PALE, line=TINT, radius=0.08)
    text(sE, x + 0.10, 4.82, 1.72, 0.24, [{'text': n, 'size': 7.0, 'color': GOLD_D}], spacing=1.0, tag='E-st-n')
    text(sE, x + 0.10, 5.06, 1.74, 0.42, [{'text': t, 'size': 8.2, 'bold': True, 'color': INK}],
         spacing=1.2, tag='E-st-t')
text(sE, 6.58, 5.66, 6.00, 0.50,
     [{'text': '同一套方法论与知识集：项目越多，错题本越厚，边际成本越低。', 'size': 8.2, 'color': GOLD_D}],
     spacing=1.3, tag='E-n2')

# =====================================================================
# 组装
# =====================================================================
tail = list(sldIdLst)[len(old):]
idA, idB, idF, idG, idC, idD, idE = tail[0], tail[1], tail[2], tail[3], tail[4], tail[5], tail[6]
order = [old[0], old[1], idA, old[5], idB, old[10], idF, idG, idC, old[16], idD, old[19], idE, old[23], old[24]]
assert len(order) == 15

for sid in list(sldIdLst):
    if sid not in order:
        prs.part.drop_rel(sid.rId)
        sldIdLst.remove(sid)
for sid in list(sldIdLst):
    sldIdLst.remove(sid)
for sid in order:
    sldIdLst.append(sid)

for no, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        if sh.has_text_frame and re.fullmatch(r'\d\d\s*/\s*\d\d', sh.text_frame.text.strip()):
            p = sh.text_frame.paragraphs[0]
            p.runs[0].text = f'{no:02d} / 15'
            for r in p.runs[1:]:
                r.text = ''

# =====================================================================
# 逐页汇报词
# =====================================================================
BODY = {
1: ('开场',
    '各位评委好，我们是信息安全研究中心团队。今天汇报瑞智源代码审计智能体——把专家经验工程化，'
    '让代码审计成为可复制的流水线。',
    '它要解决的问题是：审计产能被专家人数锁死。我们要做的是把这个能力装进系统里，让它可复制、可度量、可追溯。'),
2: ('结构',
    '汇报分四部分：业务价值与成效、技术创新性、成熟度与稳定性、推广复用潜力——就是有用、有新意、靠得住、能复制。',
    '四部分都按“问题—做法—结果”讲，每部分末了给一句结论。'),
3: ('困境与解法',
    '传统审计卡在四点：专家只能抽检；规则只给线索，误报并存；清单缺数据流，结论难核实；'
    '经验长在人身上，难沉淀——能力成了产能天花板。解法是拆成九个阶段：知识库释放、扫描、'
    '44 类专项并行挖掘，再经辩论与实证两道关，自动出报告。',
    '九个阶段里，前四步是准备（知识库、扫描、代码分析、智能体筛选），中间是并行挖掘与去重，后三步是核验与输出。'),
4: ('四项价值',
    '价值落在四点：覆盖更全，44 类专项逐类追数据流；结论更准，候选漏洞全经三方辩论，驳回不入库；'
    '响应更快，增量只审变动文件；沉淀可复用，方法论与错题本入库。',
    '每一点都能对应到前面的一个困境：覆盖对应抽检、准确对应误报、速度对应周期、沉淀对应人走能力走。'),
5: ('覆盖与可信',
    '覆盖是 7 大类、44 个专项，每类都带 CWE 映射；可信是每条漏洞固定 11 个字段——右边是平台里的'
    '漏洞清单，编号、类型、等级一目了然，再配数据流与验证包，过三道闸门后可复核、可追责、可复测。',
    '11 个字段的意义是让下游环节能用确定性代码直接处理，不必再对自然语言做二次理解。'),
6: ('创新总览',
    '技术上是四项创新：编排解决做得全，辩论判得准，实证能落地，知识库能积累——'
    '把大模型的不确定性关进工程笼子。',
    '四项不是并列堆叠，而是分别对应“做得全、判得准、能落地、可积累”四个层次。'),
7: ('架构',
    '这张是部署视图。Manager 与静态扫描常驻，管接口、任务、容器与事件；Worker 与 AI 执行容器按任务创建，'
    '跑完即回收，数据落持久化卷。控制平面不碰被审计代码，一个任务出问题不影响别的任务。',
    '关键设计四条：规则先行、确定性筛选、资源复用、双模型（内网部署或外部 API）。'),
8: ('辩论',
    '重点讲辩论，左边这张图就是全过程：重复发现先按 CWE 和位置归并，再核对支持风险的证据和'
    '限制风险的条件，最后交给正、反、裁三方对话。裁判三种结论：采纳、驳回、存疑——驳回不入库，存疑交人工。',
    '辩论的角色、观点、轮次都以结构化事件推送并随漏洞入库，人工复核不必从零判断。'),
9: ('验证与知识库',
    '验证再走一步：候选漏洞加验证条件，在受控环境构造请求实打过去，按响应判成功、失败或未验证，'
    '证据入报告；红线写进提示词——只证存在、不做利用。知识库沉淀三类知识，按执行、反思、更新、验证闭环。',
    '验证默认关闭，只在指定授权的测试环境开启；并发 3、单漏洞最多尝试 3 次。'),
10: ('成熟度',
     '这套系统已经可用，不是原型：双平面落地，44 类专项加五类阶段智能体全部实现，知识集可任务级定制，'
     '隔离、配额、白名单到位。',
     '已完成主体开发，通过冒烟测试与真实项目审计验证，具备试点条件。'),
11: ('稳定性与可观测',
     '稳定性靠分级处理：扫描失败降级继续，单点失败跳过，重启自动恢复。右边是平台实拍——思维链、'
     '漏洞列表实时刷新，每个结论都能回查到智能体与裁决记录。',
     '资源边界：单任务 48 小时、专项并发 3、双容器独立配额、任务间独立网桥、联网工具禁用。'),
12: ('效果',
     '效果有外部参照：CyberGym Level 1 独立测评，考真实开源软件漏洞复现，严格通过率 91.4%，1377 项任务成功，'
     '公开榜单第 9 名。',
     '提升来自任务轨迹反馈的技能自进化，技能版本过独立门控才进测试集，不是换更大的模型。'),
13: ('推广',
     '推广上，复用的不是代码，是能力和配置：换一份任务描述就是一次审计。场景从研发自检到平台接入，'
     '节奏三步走：试点、条线复制、全域接入。',
     '交付是镜像加 Compose，常驻只有控制平面与扫描服务；对外只开放控制平面端口。'),
14: ('路线',
     '后续三个版本：先建评估体系，再优化深度与效率，最后做场景集成与规模化。',
     '这些都是规划项，排期以研发资源确认为准。'),
15: ('收尾',
     '总结一句：把经验工程化，把不确定性变成可证伪，让结论站得住、能复制。汇报完毕，请评委批评指正。',
     '如需现场演示，可从报告页下钻到某条漏洞的辩论记录与验证数据包。'),
}
RATE = 270.0
t = 0.0
for i, sl in enumerate(prs.slides, 1):
    tag, body, extra = BODY[i]
    dur = len(body) / RATE * 60
    sl.notes_slide.notes_text_frame.text = (
        f'【{int(t)//60}:{int(t)%60:02d}–{int(t+dur)//60}:{int(t+dur)%60:02d} {tag} · 约 {round(dur)} 秒】\n'
        f'{body}\n\n〔追问备用，不计入 4 分钟〕{extra}')
    t += dur

prs.core_properties.title = '瑞智源代码审计智能体（4 分钟汇报版 · 图文版）'
prs.save(OUT)
chars = sum(len(v[1]) for v in BODY.values())
print('saved', OUT, 'slides', len(prs.slides))
print(f'主稿 {chars} 字 ≈ {chars/RATE:.2f} 分钟')
D.report()
