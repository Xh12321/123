# -*- coding: utf-8 -*-
"""生成《源代码审计智能体》四维度汇报 PPT（v2）。"""
import sys
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE

sys.path.insert(0, '/home/user/123/build')
from deck_lib import *   # noqa
import deck_lib as D

SRC = '/home/user/123/源代码审计智能体产品介绍1.pptx'
OUT = '/home/user/123/源代码审计智能体-技术与成果汇报.pptx'
TOTAL = 26

prs = Presentation(SRC)
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId)
    sldIdLst.remove(sldId)

layout_green = prs.slide_layouts[0]
layout_title = prs.slide_layouts[6]


def white():
    return prs.slides.add_slide(layout_title)


def green():
    return prs.slides.add_slide(layout_green)


def note(s, txt):
    s.notes_slide.notes_text_frame.text = txt


def para_list(s, x, y, w, h, items, size=9.5, color=GRAY, spacing=1.45, gap=8, dot=True):
    paras = []
    for i, it in enumerate(items):
        paras.append({'text': ('· ' if dot else '') + it, 'size': size, 'color': color,
                      'spacing': spacing, 'space_before': 0 if i == 0 else gap})
    return text(s, x, y, w, h, paras, line_spacing=spacing, tag='plist')


def bullet_list(s, x, y, w, items, step=0.44, size=9.5, color=GRAY, dot_color=TEAL2, dot='·'):
    for i, it in enumerate(items):
        yy = y + i * step
        text(s, x, yy - 0.03, 0.2, 0.26, [{'text': dot, 'size': size + 1, 'bold': True, 'color': dot_color}],
             line_spacing=1.0, tag='dot')
        text(s, x + 0.18, yy - 0.03, w - 0.18, step, [{'text': it, 'size': size, 'color': color}],
             line_spacing=1.35, tag='li')


# =====================================================================
# 01 封面
# =====================================================================
s = green()
hline(s, 1.18, 2.42, 0.62, color=WHITE, lw=2.2)
text(s, 1.16, 2.60, 8.6, 1.05, [{'text': '源代码审计智能体', 'size': 46, 'bold': True, 'color': WHITE}],
     line_spacing=1.12, tag='cover-title')
text(s, 1.18, 3.72, 6.4, 0.46,
     [{'text': '多智能体协同的代码审计解决方案', 'size': 20, 'color': CREAM}],
     line_spacing=1.2, tag='cover-sub')
hline(s, 1.18, 4.44, 2.15, color=MINT, lw=1.0)
text(s, 1.18, 4.62, 4.8, 0.34,
     [{'text': '国网电力科学研究院有限公司（南瑞集团有限公司）', 'size': 13, 'color': CREAM}],
     line_spacing=1.2, tag='cover-org')
text(s, 1.18, 5.06, 3.0, 0.32, [{'text': '2026年11月', 'size': 13, 'color': CREAM}],
     line_spacing=1.2, tag='cover-date')
note(s, '各位领导、各位评委：下面汇报源代码审计智能体的建设情况。汇报围绕业务价值、技术创新性、成熟度与稳定性、推广复用潜力四个维度展开。')

# =====================================================================
# 02 汇报纲要
# =====================================================================
s = white()
page_title(s, '汇报纲要', 2, TOTAL)
items = [
    ('01', '业务价值', '以 44 类专项智能体替代专家抽检，覆盖、准确与效率同步提升', '覆盖 · 可信 · 落地'),
    ('02', '技术创新性', '多智能体编排、正反裁辩论、实证验证、知识自进化四项核心创新', '编排 · 辩论 · 验证 · 知识'),
    ('03', '成熟度与稳定性', '双平面架构完整落地，隔离、容错与全链路可观测齐备', '已完成 · 可运行'),
    ('04', '推广复用潜力', '任务描述配置化交付，可从单项目复制到全域代码安全治理', '配置化 · 可复制'),
]
y0 = 1.80
for i, (no, name, desc, tag) in enumerate(items):
    y = y0 + i * 1.18
    rect(s, 0.62, y, 12.1, 0.98, fill=PALE if i % 2 == 0 else WHITE, line=TINT, radius=0.06)
    rect(s, 0.62, y + 0.14, 0.06, 0.70, fill=TEAL2, shape=MSO_SHAPE.RECTANGLE)
    text(s, 0.92, y, 0.72, 0.98, [{'text': no, 'size': 22, 'bold': True, 'color': TEAL3}],
         anchor='m', line_spacing=1.0, tag='toc-no')
    text(s, 1.66, y, 2.7, 0.98, [{'text': name, 'size': 18, 'bold': True, 'color': TEAL}],
         anchor='m', line_spacing=1.15, tag='toc-name')
    vline(s, 4.42, y + 0.22, 0.54, color=TINT2)
    text(s, 4.62, y, 5.4, 0.98, [{'text': desc, 'size': 11.5, 'color': GRAY}],
         anchor='m', line_spacing=1.3, tag='toc-desc')
    text(s, 10.15, y, 2.35, 0.98, [{'text': tag, 'size': 9, 'color': TEAL3, 'align': 'r'}],
         anchor='m', line_spacing=1.2, tag='toc-tag')
note(s, '模板规定的前两页为封面与本页。本页对应四个汇报部分：业务价值、技术创新性、成熟度与稳定性、推广复用潜力，后续内容全部围绕这四条主线组织。')

# =====================================================================
# 03 章节页 01
# =====================================================================
s = green()
section_divider(s, '01', '01', '业务价值', '让审计产能不再取决于专家数量', TOTAL, 3)
note(s, '第一部分，业务价值。核心判断是：审计产能不应由专家数量决定。')

# =====================================================================
# 04 传统审计困境
# =====================================================================
s = white()
page_title(s, '传统代码审计：专家经验难以规模化的四重困境', 4, TOTAL)
lead(s, 1.52,
     '传统代码审计高度依赖安全专家理解业务、追踪调用链并判断防护是否有效。面对多语言、多模块与持续迭代的项目，'
     '有限的专家投入难以同时兼顾风险覆盖、判断准确与经验复用。', h=0.80)
pain = [
    ('覆盖不全', '专家精力有限，只能抽检式审计；多语言、多框架、跨模块调用难以穷尽，内存安全、依赖组件等专项长期空白。',
     '44 类专项智能体 + 数据流追踪'),
    ('误报漏报', '规则扫描只给线索不给上下文，输入是否可控、防护是否有效仍需人工逐条判断，误报与漏报同时存在。',
     '正、反、裁三方辩论核验'),
    ('结论难核实', '漏洞清单缺少数据流与触发条件，研发难以定位；发现的问题无法实证，整改与复测缺少可依据的证据。',
     '统一字段证据链 + 实证验证'),
    ('经验难沉淀', '审计过程散落在个人头脑与零散文档，误判教训与审计方法无法复用，团队能力随人员流动而波动。',
     '知识库与错题本回流沉淀'),
]
for i, (t, b, cap) in enumerate(pain):
    x = 0.62 + i * 3.1
    rect(s, x, 2.52, 2.80, 2.96, fill=WHITE, line=TINT, radius=0.05)
    num_badge(s, x + 0.22, 2.72, 0.40, f'0{i+1}', size=11.5)
    text(s, x + 0.74, 2.74, 1.86, 0.36, [{'text': t, 'size': 14, 'bold': True, 'color': TEAL}],
         line_spacing=1.1, tag='pain-t')
    hline(s, x + 0.22, 3.28, 2.36, color=TINT2, lw=0.75)
    text(s, x + 0.22, 3.40, 2.38, 1.50, [{'text': b, 'size': 10.5, 'color': GRAY, 'spacing': 1.55}],
         line_spacing=1.55, tag='pain-b')
    hline(s, x + 0.22, 4.94, 2.36, color=TINT2, lw=0.75)
    text(s, x + 0.22, 5.02, 2.38, 0.30, [{'text': '对应能力', 'size': 7.5, 'color': TEAL3}],
         line_spacing=1.0, tag='pain-cl')
    text(s, x + 0.22, 5.20, 2.38, 0.26, [{'text': cap, 'size': 9, 'bold': True, 'color': TEAL2}],
         line_spacing=1.0, tag='pain-c')
rect(s, 0.62, 5.74, 12.1, 0.86, fill=TEAL, radius=0.06)
text(s, 0.98, 5.74, 11.4, 0.86,
     [{'text': '结果是：专家能力成为审计产能的天花板 —— 扩大审计规模只能加人，而质量却随人而变。',
       'size': 13.5, 'color': WHITE}], anchor='m', line_spacing=1.2, tag='pain-sum')
note(s, '四个困境：覆盖不全、误报漏报、结论难核实、经验难沉淀。它们共同指向一个问题——产能被专家个人能力锁死。')

# =====================================================================
# 05 方案总览
# =====================================================================
s = white()
page_title(s, '解决方案：一条可编排、可观测、可复算的审计流水线', 5, TOTAL)
lead(s, 1.50,
     '按漏洞成因把审计任务拆成多个专项智能体并行执行；候选漏洞先去重收敛，再由正、反、裁三方智能体辩论核验，'
     '在隔离环境实证可利用性，最终自动生成结构化报告。全流程无人工介入，每一阶段产物均留档。', h=0.78)
stages = [
    ('知识库释放', '方法论/漏洞模式/错题本'),
    ('静态预扫描', '规则映射 + CWE 命中'),
    ('代码分析', '技术栈/入口/依赖清单'),
    ('智能体筛选', '规则优先，补选防漏'),
    ('专项审计', '44 类智能体并行挖掘'),
    ('去重收敛', '按类型与位置归并'),
    ('辩论核验', '正、反、裁三方博弈'),
    ('漏洞验证', 'PoC 实证可达性'),
    ('报告生成', '结构化 + 可读报告'),
]
BW, BH, GAP = 2.06, 1.16, 0.42
x0 = 0.68
row_y = [2.42, 4.12]
for i, (t, d) in enumerate(stages):
    row = 0 if i < 5 else 1
    idx = i if row == 0 else 8 - i
    x = x0 + idx * (BW + GAP)
    y = row_y[row]
    hi = (i == 4)
    rect(s, x, y, BW, BH, fill=TEAL if hi else PALE, line=None if hi else TINT, radius=0.07)
    text(s, x + 0.14, y + 0.13, 0.5, 0.28,
         [{'text': f'{i+1:02d}', 'size': 10, 'bold': True, 'color': MINT if hi else TEAL3}],
         line_spacing=1.0, tag='st-no')
    text(s, x + 0.14, y + 0.38, BW - 0.28, 0.32,
         [{'text': t, 'size': 12, 'bold': True, 'color': WHITE if hi else TEAL}],
         line_spacing=1.1, tag='st-t')
    text(s, x + 0.14, y + 0.73, BW - 0.24, 0.34,
         [{'text': d, 'size': 8.5, 'color': CREAM if hi else GRAY}],
         line_spacing=1.2, tag='st-d')
    if i < 8 and not hi:
        if i < 4:
            arrow(s, x + BW + 0.08, y + BH / 2 - 0.07, 0.26, 0.14)
        if 4 < i < 8:
            arrow(s, x - 0.34, y + BH / 2 - 0.07, 0.26, 0.14, direction='left')
x5 = x0 + 4 * (BW + GAP)
a = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(x5 + BW / 2 - 0.10), Inches(row_y[0] + BH + 0.09),
                       Inches(0.20), Inches(0.44))
a.fill.solid(); a.fill.fore_color.rgb = MINT; a.line.fill.background()

by = 5.64
rect(s, 0.62, by, 12.1, 1.06, fill=PALE, line=TINT, radius=0.05)
notes_row = [
    ('四类智能体', '代码分析 · 专项审计 · 辩论核验 · 漏洞验证'),
    ('确定性兜底', '规则可判定的交给代码，需要推理与理解的交给智能体'),
    ('全程可观测', '进度、思维链、工具调用与辩论对话实时推送'),
]
for i, (t, d) in enumerate(notes_row):
    x = 0.86 + i * 4.02
    text(s, x, by + 0.14, 3.7, 0.28, [{'text': t, 'size': 11, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='note-t')
    text(s, x, by + 0.46, 3.72, 0.50, [{'text': d, 'size': 9.5, 'color': GRAY}],
         line_spacing=1.35, tag='note-d')
    if i:
        vline(s, x - 0.18, by + 0.20, 0.66, color=TINT2)
note(s, '九个阶段串成一条流水线：能靠规则确定的用代码解决，需要理解与推理的交给智能体；每一阶段产物都留档，既能被下游确定性处理，也能事后回溯。')

# =====================================================================
# 06 业务价值总览
# =====================================================================
s = white()
page_title(s, '业务价值：覆盖更全、结论更准、响应更快、沉淀可复用', 6, TOTAL)
vals = [
    ('覆盖更全', '44 类专项智能体按漏洞类型垂直划分，覆盖注入、Web 交互、访问控制、服务端与数据、内存安全、业务逻辑、依赖组件等大类，逐类做数据流追踪。',
     ['44 类专项', '7 大类别', '全量 + 增量']),
    ('结论更准', '候选漏洞 100% 经正、反、裁三方辩论，驳回不入库、存疑单独标注；每条漏洞含 CWE 编号、文件行号、完整数据流与验证数据包。',
     ['三方辩论', '五级危害', '11 项字段']),
    ('响应更快', '九阶段流水线全自动执行，单任务最长可跑 48 小时；增量模式跳过全量与扫描直达变动文件，把反馈压缩到提交级。',
     ['九阶段自动', '48 小时长跑', '提交级反馈']),
    ('沉淀可复用', '审计方法论、漏洞模式与错题本沉淀为可插拔知识库，报告可回溯到智能体、证据与裁决记录，支撑整改与复测闭环。',
     ['知识库可插拔', '错题本回流', '报告可溯源']),
]
pos = [(0.62, 1.66), (6.78, 1.66), (0.62, 4.02), (6.78, 4.02)]
for (x, y), (t, b, tags) in zip(pos, vals):
    rect(s, x, y, 5.95, 2.18, fill=PALE, line=TINT, radius=0.05)
    rect(s, x, y + 0.16, 0.06, 0.52, fill=TEAL2, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.30, y + 0.20, 4.9, 0.42, [{'text': t, 'size': 17, 'bold': True, 'color': TEAL}],
         line_spacing=1.1, tag='val-t')
    hline(s, x + 0.30, y + 0.72, 5.34, color=TINT2, lw=0.75)
    text(s, x + 0.30, y + 0.80, 5.36, 0.84, [{'text': b, 'size': 10, 'color': GRAY, 'spacing': 1.5}],
         line_spacing=1.5, tag='val-b')
    for j, tg in enumerate(tags):
        chip(s, x + 0.30 + j * 1.72, y + 1.70, 1.62, 0.34, tg, size=8.5,
             fill=WHITE, color=TEAL2, line=TINT2, radius=0.18)
note(s, '四个价值点：覆盖更全、结论更准、响应更快、沉淀可复用。它们分别对应前面四个困境。')

# =====================================================================
# 07 价值① 覆盖面
# =====================================================================
s = white()
page_title(s, '业务价值① 覆盖：从专家抽检到漏洞类型全矩阵', 7, TOTAL)
rect(s, 0.62, 1.62, 5.55, 4.38, fill=PALE, line=TINT, radius=0.04)
text(s, 0.92, 1.80, 1.9, 0.92, [{'text': '44', 'size': 54, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='44')
text(s, 2.72, 1.92, 3.2, 0.70,
     [{'text': '个专项审计智能体', 'size': 14, 'bold': True, 'color': TEAL},
      {'text': '按漏洞成因垂直划分，并行执行', 'size': 9.5, 'color': GRAY, 'space_before': 2}],
     line_spacing=1.25, tag='44t')
hline(s, 0.92, 2.84, 4.95, color=TINT2, lw=0.75)
cats = [
    ('注入类', 7, 'SQL · 命令 · 表达式 · 模板 · NoSQL'),
    ('Web 前端与交互', 6, 'XSS · CSRF · 点击劫持 · 文件上传'),
    ('访问控制', 6, '认证绕过 · 越权 · 会话 · OAuth / SSO'),
    ('服务端与数据', 9, 'SSRF · XXE · 穿越 · 反序列化 · 原型污染'),
    ('内存安全（C/C++）', 8, '栈溢出 · 堆溢出 · 释放后使用 · 整数溢出'),
    ('业务与逻辑', 3, '业务逻辑 · 竞态条件 · 异常处理'),
    ('其他', 5, '依赖组件 CVE · 编码绕过 · 提示注入'),
]
for i, (c, n, d) in enumerate(cats):
    y = 2.92 + i * 0.42
    text(s, 0.92, y, 1.55, 0.28, [{'text': c, 'size': 9, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='cat')
    text(s, 2.44, y, 0.30, 0.28, [{'text': str(n), 'size': 9, 'bold': True, 'color': TEAL3, 'align': 'r'}],
         line_spacing=1.0, tag='catn')
    text(s, 2.86, y, 3.10, 0.28, [{'text': d, 'size': 7.6, 'color': GRAY}],
         line_spacing=1.0, tag='catd')
    if i < 6:
        hline(s, 0.92, y + 0.34, 4.95, color=TINT2, lw=0.5)
text(s, 0.92, 5.72, 4.95, 0.36,
     [{'text': '每个专项智能体内置 CWE 映射、攻击面关键词与检测要点提示词。',
       'size': 8.5, 'color': GRAY2}], line_spacing=1.3, tag='cat-note')
# 右侧对比
tb_x, tb_w = 6.48, 6.25
rect(s, tb_x, 1.62, tb_w, 4.38, fill=WHITE, line=TINT, radius=0.04)
text(s, tb_x + 0.22, 1.74, 5.0, 0.32, [{'text': '审计方式对比', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='cmp-t')
cols = [(tb_x + 0.16, 1.30), (tb_x + 1.60, 2.05), (tb_x + 3.80, 2.30)]
for (cx, cw), hd in zip(cols, ['维度', '传统人工审计', '智能体审计']):
    text(s, cx, 2.14, cw, 0.28, [{'text': hd, 'size': 9, 'bold': True, 'color': GRAY2}],
         line_spacing=1.0, tag='hd')
hline(s, tb_x + 0.16, 2.44, tb_w - 0.34, color=TINT2, lw=0.75)
rows = [
    ('覆盖范围', '依赖专家专长，抽检式覆盖', '44 类专项并行，逐类追踪'),
    ('判断依据', '个人经验，口径不一', '统一方法论与统一字段'),
    ('结论状态', '清单为主，缺证据链', '数据流 + 代码 + 验证包'),
    ('反馈周期', '项目级周期性', '增量模式提交级反馈'),
    ('经验复用', '难以沉淀，随人流动', '知识库沉淀，越用越准'),
]
for i, (a, b, c) in enumerate(rows):
    y = 2.58 + i * 0.66
    if i % 2 == 0:
        rect(s, tb_x + 0.12, y - 0.08, tb_w - 0.24, 0.58, fill=PALE, line=None, radius=0.12)
    text(s, cols[0][0], y, 1.30, 0.40, [{'text': a, 'size': 9.5, 'bold': True, 'color': INK}],
         line_spacing=1.2, tag='cmp-a')
    text(s, cols[1][0], y - 0.02, 2.05, 0.44, [{'text': b, 'size': 9, 'color': GRAY}],
         line_spacing=1.2, tag='cmp-b')
    text(s, cols[2][0], y - 0.02, 2.28, 0.44, [{'text': c, 'size': 9, 'color': TEAL}],
         line_spacing=1.2, tag='cmp-c')
note(s, '覆盖面的变化来自两点：一是把审计知识拆成 44 个按漏洞类型划分的专项智能体；二是每个专项都按"来源—转化—汇聚点"追踪完整数据流，而不是只看规则命中。')

# =====================================================================
# 08 价值② 可信
# =====================================================================
s = white()
page_title(s, '业务价值② 可信：每条漏洞都带证据链，可复核、可整改', 8, TOTAL)
text(s, 0.62, 1.56, 6.6, 0.32, [{'text': '一条漏洞记录 = 11 个结构化字段', 'size': 12, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='ev-h')
fields = [
    ('标题', 'title'), ('危害等级', 'severity'), ('漏洞类型', 'category'),
    ('CWE 编号', 'cwe_id'), ('文件与行号', 'file · line'), ('完整数据流', 'data_flow'),
    ('漏洞描述', 'description'), ('代码片段', 'code'), ('修复建议', 'fix'),
    ('验证数据包', 'poc'), ('辩论痕迹', 'debate'),
]
for i, (cn, en) in enumerate(fields):
    r, c = divmod(i, 3)
    x = 0.62 + c * 2.14
    y = 2.00 + r * 0.78
    rect(s, x, y, 2.00, 0.66, fill=PALE, line=TINT, radius=0.10)
    text(s, x + 0.14, y + 0.08, 1.74, 0.26, [{'text': cn, 'size': 10, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='f-cn')
    text(s, x + 0.14, y + 0.35, 1.74, 0.24, [{'text': en, 'size': 7.5, 'color': GRAY2}],
         line_spacing=1.0, tag='f-en')
text(s, 0.62, 5.22, 6.3, 0.66,
     [{'text': '统一字段的用意：多个智能体的产出可被去重、验证、报告等下游环节用确定性代码直接处理，'
               '无需再对文字做二次理解。', 'size': 9.5, 'color': GRAY}], line_spacing=1.45, tag='ev-note')
gx, gw = 7.28, 5.44
text(s, gx, 1.56, 5.2, 0.32, [{'text': '三级质量闸门', 'size': 12, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='gate-h')
gates = [
    ('规则去重', '按漏洞类型、文件位置归并收敛，同一个问题不重复入库。'),
    ('辩论核验', '正、反、裁三方逐条博弈，采纳 / 驳回 / 存疑三类终裁。'),
    ('实证验证', '可选：隔离环境实发请求，验证运行时可达与可利用。'),
]
for i, (t, d) in enumerate(gates):
    y = 1.96 + i * 1.10
    rect(s, gx, y, gw, 0.98, fill=WHITE, line=TINT, radius=0.06)
    num_badge(s, gx + 0.16, y + 0.28, 0.40, str(i + 1), size=11)
    text(s, gx + 0.70, y + 0.14, 1.30, 0.30, [{'text': t, 'size': 10.5, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='gate-t')
    text(s, gx + 0.70, y + 0.44, 4.55, 0.44, [{'text': d, 'size': 9, 'color': GRAY}],
         line_spacing=1.3, tag='gate-d')
    if i < 2:
        text(s, gx + gw / 2 - 0.12, y + 0.97, 0.30, 0.16,
             [{'text': '▼', 'size': 7, 'color': MINT, 'align': 'c'}], line_spacing=1.0, tag='gate-ar')
rect(s, gx, 5.34, gw, 0.66, fill=TINT, line=None, radius=0.10)
text(s, gx + 0.20, 5.34, gw - 0.4, 0.66,
     [{'text': '过三道闸门后的记录：可复核、可追责、可复测。', 'size': 9.5, 'bold': True, 'color': TEAL}],
     anchor='m', line_spacing=1.2, tag='gate-sum')
rect(s, 0.62, 6.14, 12.1, 0.78, fill=TEAL, radius=0.06)
text(s, 0.92, 6.14, 11.5, 0.78,
     [{'text': '交付物：结构化报告 + 可读报告；报告计数与去重后真实结果一致，任一漏洞都能回查到智能体、分析结论与裁决记录。',
       'size': 11, 'color': WHITE}], anchor='m', line_spacing=1.2, tag='deliver')
note(s, '结论质量靠三件事保证：统一字段让结果可被确定性处理；三级闸门拦住误报；报告与留档让每个数字都能回溯。')

# =====================================================================
# 09 价值③ 落地
# =====================================================================
s = white()
page_title(s, '业务价值③ 落地：三类场景共用一条审计链路', 9, TOTAL)
scenes = [
    ('项目级代码审计', '全量 · 增量', [
        ('痛点', '代码规模大、组件多，人工审计周期长、覆盖有限，迭代后难以快速反馈。'),
        ('能力', '全量模式 44 类专项并行深度审计；增量模式只审变动文件，可嵌入 CI 流水线。'),
        ('价值', '覆盖从专家抽检扩展到类型全矩阵，反馈从项目级压缩到提交级。'),
    ]),
    ('漏洞实证与复现', 'PoC · 可达性', [
        ('痛点', '漏洞需实证才能进入修复流程，人工构造 PoC 耗时且依赖经验。'),
        ('能力', '在隔离环境为每条漏洞构造最小化 PoC，实发请求验证运行时可达。'),
        ('价值', '把代码层推断升级为运行时证实，关键技术信息可沉淀复用。'),
    ]),
    ('依赖与开源筛查', '供应链 · CVE', [
        ('痛点', '第三方组件与开源代码大量引入，已知漏洞与历史缺陷难以逐一排查。'),
        ('能力', '代码分析阶段枚举依赖清单，依赖组件专项智能体开展 CVE 筛查。'),
        ('价值', '供应链安全纳入常规流程，上线或引入组件时自动完成筛查。'),
    ]),
]
for i, (t, tag, parts) in enumerate(scenes):
    x = 0.62 + i * 4.10
    rect(s, x, 1.66, 3.90, 3.44, fill=PALE, line=TINT, radius=0.05)
    text(s, x + 0.24, 1.78, 2.6, 0.34, [{'text': t, 'size': 13.5, 'bold': True, 'color': TEAL}],
         line_spacing=1.1, tag='sc-t')
    text(s, x + 0.24, 2.14, 3.4, 0.26, [{'text': tag, 'size': 8.5, 'color': TEAL3}],
         line_spacing=1.0, tag='sc-tag')
    for j, (lab, body) in enumerate(parts):
        y = 2.50 + j * 0.86
        text(s, x + 0.24, y, 0.5, 0.24, [{'text': lab, 'size': 8.5, 'bold': True, 'color': TEAL2}],
             line_spacing=1.0, tag='sc-lab')
        text(s, x + 0.74, y - 0.04, 2.98, 0.82, [{'text': body, 'size': 9.3, 'color': GRAY}],
             line_spacing=1.35, tag='sc-b')
        if j:
            hline(s, x + 0.24, y - 0.12, 3.42, color=TINT2, lw=0.5)
rect(s, 0.62, 5.36, 12.1, 0.92, fill=WHITE, line=TINT, radius=0.06)
text(s, 0.90, 5.44, 4.0, 0.32, [{'text': '当前落地模式', 'size': 10, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='mode-t')
text(s, 0.90, 5.76, 8.7, 0.42,
     [{'text': '以“智能体审计 + 人工校核”的复合模式融入研发 CI/CD 流程，形成 审计 → 复核 → 整改 → 复测 的闭环。',
       'size': 10.5, 'color': GRAY}], line_spacing=1.2, tag='mode-b')
for i, step in enumerate(['审计', '复核', '整改', '复测']):
    chip(s, 9.86 + i * 0.68, 5.60, 0.60, 0.36, step, size=8, fill=TINT, color=TEAL)
note(s, '三类场景：项目级全量与增量审计、漏洞实证复现、依赖与开源组件筛查。它们共用同一条流水线，只是流程开关与知识集不同。')

# =====================================================================
# 10 章节页 02
# =====================================================================
s = green()
section_divider(s, '02', '02', '技术创新性', '把不确定性关进工程化的笼子', TOTAL, 10)
note(s, '第二部分，技术创新性。四项创新都围绕同一个目标：让大模型的不确定性可控。')

# =====================================================================
# 11 创新总览
# =====================================================================
s = white()
page_title(s, '技术创新：四项关键创新，互相补位', 11, TOTAL)
inns = [
    ('多智能体\n流水线编排', '单一大模型端到端不可控', '按阶段拆分任务、分工并行，规则与推理互补，过程与产物全程留档。', '创新一 · 详见 P12'),
    ('正反裁\n三方辩论', '模型存在事实性幻觉与误报', '强制证伪：反方质疑、正方举证、裁判终裁，输出转为可检验的逻辑对抗。', '创新二 · 详见 P13'),
    ('漏洞\n实证验证', '代码层推断难以直接落地', '隔离环境构造最小化 PoC 实发请求，把推断升级为运行时证实。', '创新三 · 详见 P14'),
    ('知识库驱动\n自进化', '通用模型缺少专业审计经验', '方法论、错题本与技能按任务释放，误报回流沉淀，越用越准。', '创新四 · 详见 P15'),
]
for i, (t, p, b, nav) in enumerate(inns):
    x = 0.62 + i * 3.10
    rect(s, x, 1.68, 2.80, 3.90, fill=PALE, line=TINT, radius=0.05)
    text(s, x + 0.22, 1.80, 0.9, 0.50, [{'text': f'0{i+1}', 'size': 22, 'bold': True, 'color': TEAL3}],
         line_spacing=1.0, tag='inn-no')
    text(s, x + 0.22, 2.32, 2.38, 0.86, [{'text': t, 'size': 13, 'bold': True, 'color': TEAL, 'spacing': 1.2}],
         line_spacing=1.2, tag='inn-t')
    hline(s, x + 0.22, 3.16, 2.36, color=TINT2, lw=0.75)
    text(s, x + 0.22, 3.24, 2.36, 0.30, [{'text': '解决问题', 'size': 8, 'bold': True, 'color': TEAL2}],
         line_spacing=1.0, tag='inn-pl')
    text(s, x + 0.22, 3.50, 2.36, 0.52, [{'text': p, 'size': 9.5, 'color': INK}],
         line_spacing=1.3, tag='inn-p')
    text(s, x + 0.22, 4.14, 2.36, 0.90, [{'text': b, 'size': 9.5, 'color': GRAY, 'spacing': 1.5}],
         line_spacing=1.5, tag='inn-b')
    hline(s, x + 0.22, 5.04, 2.36, color=TINT2, lw=0.75)
    text(s, x + 0.22, 5.12, 2.36, 0.30, [{'text': nav, 'size': 8.5, 'color': TEAL3}],
         line_spacing=1.0, tag='inn-nav')
rect(s, 0.62, 5.86, 12.1, 0.68, fill=WHITE, line=TINT, radius=0.06)
text(s, 0.90, 5.86, 11.6, 0.68,
     [{'text': '四项创新分工：编排解决“做得全”，辩论与验证解决“判得准”，知识库解决“经验能不能积累”。',
       'size': 10.5, 'color': TEAL}], anchor='m', line_spacing=1.2, tag='inn-sum')
note(s, '四项创新不是并列堆叠，而是分别对应"做得全""判得准""经验能积累"三个层面。')

# =====================================================================
# 12 创新一 架构
# =====================================================================
s = white()
page_title(s, '创新一 控制与执行分离的多智能体编排架构', 12, TOTAL)
layers = [
    ('控制', '任务管理层', ['任务生命周期', '双向事件通道', '容器编排', '统一 API-Key 鉴权'], 1.62, 1.16),
    ('执行', '审计执行层', ['编排器', '状态跟踪', '事件管理器', '结果留档', 'AI 引擎适配'], 2.92, 1.16),
    ('能力', '智能体与工具层', ['代码分析', '专项审计 44', '辩论核验', '漏洞验证', '静态扫描服务', '代码知识图谱'], 4.22, 1.62),
]
for tag, name, items, y, h in layers:
    rect(s, 0.62, y, 7.30, h, fill=PALE, line=TINT, radius=0.04)
    rect(s, 0.62, y, 1.46, h, fill=TEAL, radius=0.06)
    text(s, 0.74, y + h / 2 - 0.44, 1.24, 0.28, [{'text': tag, 'size': 9, 'color': MINT}],
         line_spacing=1.0, tag='ly-tag')
    text(s, 0.74, y + h / 2 - 0.14, 1.26, 0.52,
         [{'text': name, 'size': 9.5, 'bold': True, 'color': WHITE}], line_spacing=1.15, tag='ly-name')
    n = len(items)
    per = (7.30 - 1.62) / n
    for i, it in enumerate(items):
        cx = 2.22 + i * per
        chip(s, cx, y + h / 2 - 0.20, per - 0.12, 0.40, it, size=8.5,
             fill=WHITE, color=TEAL, line=TINT, radius=0.12)
rx = 8.20
text(s, rx, 1.56, 4.5, 0.32, [{'text': '关键设计', 'size': 12, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='kd-h')
bullets = [
    ('规则先行', '能靠规则确定的用代码解决，需要理解与推理的交给智能体，保证结果可控、过程可观测。'),
    ('确定性筛选', '以规则为主、AI 建议为辅；静态扫描命中即强制补选，拿不准的一律保留，宁可多查不漏查。'),
    ('产物留档', '各阶段产物统一保存，既是下一阶段的输入，也是事后回溯的凭据。'),
    ('资源复用', '同一项目多个智能体共用 AI 引擎容器，任务结束自动回收，按标签统一清理。'),
]
for i, (t, d) in enumerate(bullets):
    y = 1.94 + i * 1.20
    text(s, rx, y, 0.2, 0.26, [{'text': '·', 'size': 14, 'bold': True, 'color': TEAL2}],
         line_spacing=1.0, tag='kd-dot')
    text(s, rx + 0.20, y - 0.02, 4.24, 0.30, [{'text': t, 'size': 10.5, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='kd-t')
    text(s, rx + 0.20, y + 0.28, 4.24, 0.86, [{'text': d, 'size': 9, 'color': GRAY}],
         line_spacing=1.4, tag='kd-b')
text(s, 0.62, 6.10, 7.30, 0.72,
     [{'text': '控制平面不接触被审计代码：任务、事件、容器与配置在管理层收敛，分析能力全部下沉到一次性执行容器，任务结束即回收。',
       'size': 9, 'color': GRAY}], line_spacing=1.4, tag='arch-note')
note(s, '架构上做了控制与执行分离：控制平面只负责任务、事件、容器与配置；分析能力全部下沉到一次性执行容器里，跑完即回收。')

# =====================================================================
# 13 创新二 辩论
# =====================================================================
s = white()
page_title(s, '创新二 正、反、裁三方辩论：把幻觉转化为可证伪的对抗', 13, TOTAL)
deb = [
    ('候选漏洞', '专项审计产出全部暂存，不立即输出'),
    ('反方质疑', '假设是误报，依托实际代码逐条性质疑，禁止无依据臆测'),
    ('正方举证', '结合原始漏洞信息与质疑，构建攻击链逐条回应'),
    ('反方复判', '对正方的回应再做立场判定，形成对抗闭环'),
    ('裁判终裁', '围绕可达性与攻击者可控程度两个维度裁决'),
]
BW2 = 2.18
for i, (t, d) in enumerate(deb):
    x = 0.68 + i * (BW2 + 0.27)
    hi = (i == 4)
    rect(s, x, 1.72, BW2, 1.34, fill=TEAL if hi else PALE, line=None if hi else TINT, radius=0.07)
    text(s, x + 0.16, 1.84, BW2 - 0.32, 0.28,
         [{'text': t, 'size': 11.5, 'bold': True, 'color': WHITE if hi else TEAL}],
         line_spacing=1.0, tag='deb-t')
    text(s, x + 0.16, 2.16, BW2 - 0.30, 0.82,
         [{'text': d, 'size': 8.5, 'color': CREAM if hi else GRAY}],
         line_spacing=1.35, tag='deb-d')
    if i < 4:
        arrow(s, x + BW2 + 0.04, 2.32, 0.19, 0.13)
text(s, 0.68, 3.30, 4.0, 0.30, [{'text': '裁判三类终裁与处置', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='jd-h')
outs = [
    ('采纳', '进入漏洞记录，随报告输出', TEAL),
    ('驳回', '一律不入库，直接过滤', GRAY),
    ('存疑', '仍然输出并单独标注，供人工复核', TEAL2),
]
for i, (t, d, c) in enumerate(outs):
    x = 0.68 + i * 4.06
    rect(s, x, 3.64, 3.86, 0.80, fill=WHITE, line=TINT, radius=0.06)
    rect(s, x, 3.64, 0.06, 0.80, fill=c, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.24, 3.64, 0.9, 0.80, [{'text': t, 'size': 12, 'bold': True, 'color': c}],
         anchor='m', line_spacing=1.0, tag='out-t')
    text(s, x + 1.16, 3.64, 2.54, 0.80, [{'text': d, 'size': 9, 'color': GRAY}],
         anchor='m', line_spacing=1.35, tag='out-d')
rect(s, 0.68, 4.70, 12.05, 2.04, fill=PALE, line=TINT, radius=0.05)
text(s, 0.92, 4.84, 4.4, 0.30, [{'text': '为什么有效', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='why-h')
why = [
    '把模型的自由输出，改造成“立场对立、逐条举证”的可检验过程，幻觉无处藏身。',
    '辩论全过程（角色、观点、轮次）以结构化事件实时推送前端，裁决痕迹随漏洞入库。',
    '经对抗核验的漏洞记录附带完整正反裁对话，人工复核不必从零判断。',
    '凡被裁判驳回的问题一律不进入漏洞记录，误报在下游环节之前就被拦下。',
]
para_list(s, 0.90, 5.22, 11.7, 1.44, why, size=9.5, spacing=1.4, gap=10)
note(s, '辩论机制的核心是把模型的自由生成，改造成"立场对立、逐条举证"的可检验过程：反方假设是误报，正方必须构建攻击链，裁判按可达性终裁。')

# =====================================================================
# 14 创新三 验证
# =====================================================================
s = white()
page_title(s, '创新三 漏洞实证验证：从代码层推断到运行时证实', 14, TOTAL)
steps = [
    ('接收上下文', '单条漏洞的位置、描述、数据流、代码片段与验证数据包参考一并下发。'),
    ('构造 PoC', '在隔离的 AI 引擎容器内构造最小化验证脚本，不依赖人工编写。'),
    ('实发请求', '对受控测试环境发起真实请求，验证运行时可达性与可触发性。'),
    ('结论沉淀', '输出验证通过 / 失败结论，并归集可复用的关键技术信息。'),
]
for i, (t, d) in enumerate(steps):
    y = 1.70 + i * 1.10
    rect(s, 0.62, y, 6.55, 0.98, fill=PALE, line=TINT, radius=0.06)
    num_badge(s, 0.78, y + 0.26, 0.44, str(i + 1), size=12)
    text(s, 1.38, y + 0.14, 2.0, 0.30, 1 and [{'text': t, 'size': 11, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='vs-t')
    text(s, 1.38, y + 0.44, 5.55, 0.44, [{'text': d, 'size': 9.2, 'color': GRAY}],
         line_spacing=1.3, tag='vs-d')
    if i < 3:
        text(s, 0.95, y + 0.97, 0.30, 0.15, [{'text': '▼', 'size': 7, 'color': MINT, 'align': 'c'}],
             line_spacing=1.0, tag='vs-ar')
gx, gw = 7.45, 5.28
rect(s, gx, 1.70, gw, 2.90, fill=WHITE, line=TINT, radius=0.10)
rect(s, gx, 1.70, gw, 0.50, fill=TEAL, radius=0.10)
text(s, gx + 0.22, 1.70, 4.6, 0.50,
     [{'text': '安全红线（内置提示词约束）', 'size': 10.5, 'bold': True, 'color': WHITE}],
     anchor='m', line_spacing=1.0, tag='red-h')
reds = ['仅证明漏洞存在，不做深度利用', '禁止破坏性操作（DELETE、DROP、rm -rf 等）',
        '禁止窃取真实用户数据', '脚本仅允许写入临时目录',
        '并发 3，单漏洞最多尝试 3 次']
para_list(s, gx + 0.20, 2.34, 4.92, 2.16, reds, size=9.2, spacing=1.4, gap=11)
rect(s, gx, 4.76, gw, 1.18, fill=PALE, line=TINT, radius=0.05)
text(s, gx + 0.22, 4.86, 4.8, 0.30, [{'text': '使用边界', 'size': 10.5, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='ub-h')
text(s, gx + 0.22, 5.16, 4.84, 0.72,
     [{'text': '默认关闭，需配合受控测试环境使用；只对已确认的候选漏洞做最小化实证，不提供攻击环境管理能力。',
       'size': 9, 'color': GRAY}], line_spacing=1.4, tag='ub-b')
text(s, 0.62, 6.16, 6.55, 0.62,
     [{'text': '验证中沉淀的可复用技术信息（加解密脚本、报文构造规则、登录凭证、绕过方式）自动归集，供后续项目复用。',
       'size': 8.5, 'color': GRAY}], line_spacing=1.4, tag='vs-note')
note(s, '验证环节把"代码层推断"变成"运行时证实"。为避免风险，安全约束直接写进提示词：只证存在、不做利用、不碰真实数据。')

# =====================================================================
# 15 创新四 知识库
# =====================================================================
s = white()
page_title(s, '创新四 知识库驱动：经验可沉淀、可回流、可复用', 15, TOTAL)
text(s, 0.62, 1.56, 5.8, 0.30, [{'text': '三类知识随任务释放', 'size': 11.5, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='kb-h')
kbs = [
    ('技能类', '审计方法论：攻击面分析、数据流追踪、危害评级标准'),
    ('智能体类', '正、反、裁三类辩论角色定义与举证、质疑规范'),
    ('知识文档类', '漏洞模式库、安全编码指南、错题本（按主题沉淀误报教训）'),
]
for i, (t, d) in enumerate(kbs):
    y = 1.94 + i * 1.16
    rect(s, 0.62, y, 5.55, 1.02, fill=PALE, line=TINT, radius=0.06)
    rect(s, 0.62, y, 0.06, 1.02, fill=TEAL2, shape=MSO_SHAPE.RECTANGLE)
    text(s, 0.86, y + 0.16, 1.6, 0.28, [{'text': t, 'size': 10.5, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='kb-t')
    text(s, 0.86, y + 0.46, 5.1, 0.50, [{'text': d, 'size': 9.2, 'color': GRAY}],
         line_spacing=1.3, tag='kb-d')
rect(s, 0.62, 5.48, 5.55, 1.18, fill=WHITE, line=TINT, radius=0.05)
text(s, 0.86, 5.58, 5.1, 0.28, [{'text': '两种来源', 'size': 9.5, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='kb-src-t')
text(s, 0.86, 5.86, 5.06, 0.72,
     [{'text': '任务创建方按语言或场景定制传入；未传时使用镜像内置默认知识集。任务开始前自动清理旧内容并全新释放，避免陈旧污染。',
       'size': 8.5, 'color': GRAY}], line_spacing=1.45, tag='kb-src')
rx = 6.55
rect(s, rx, 1.56, 6.18, 5.10, fill=WHITE, line=TINT, radius=0.05)
text(s, rx + 0.24, 1.70, 5.4, 0.30,
     [{'text': '自进化闭环：执行 → 反思 → 更新 → 验证', 'size': 11.5, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='evo-h')
loop = [('执行', '智能体按技能树路由技能，完成任务并记录操作、反馈与成败'),
        ('反思', '对小批轨迹做反思、跨批归纳，提炼技能增删改建议'),
        ('更新', '在编辑预算内生成候选技能树，保留可回退的版本'),
        ('验证', '候选技能树经独立门控，同口径比较，提升则接纳否则回退')]
vline(s, rx + 0.44, 2.6, 2.5, color=TINT2, lw=1.2)
for i, (t, d) in enumerate(loop):
    y = 2.16 + i * 0.90
    num_badge(s, rx + 0.26, y, 0.36, str(i + 1), size=9.5, fill=TINT, color=TEAL)
    text(s, rx + 0.74, y - 0.02, 0.9, 0.26, [{'text': t, 'size': 10, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='evo-t')
    text(s, rx + 1.58, y - 0.04, 4.36, 0.72, [{'text': d, 'size': 8.8, 'color': GRAY}],
         line_spacing=1.3, tag='evo-d')
hline(s, rx + 0.26, 5.86, 5.64, color=TINT2, lw=0.75)
text(s, rx + 0.26, 5.96, 5.62, 0.34,
     [{'text': '误报经错题本回流，审计越多、判断越准；技能版本冻结后才进入独立测试集，避免自测偏差。',
       'size': 8.5, 'color': TEAL2}], line_spacing=1.35, tag='evo-note')
note(s, '知识库解决"经验能不能积累"：三类知识随任务释放；闭环是执行、反思、更新、验证，每次更新都要过独立门控，避免自我感觉良好。')

# =====================================================================
# 16 章节页 03
# =====================================================================
s = green()
section_divider(s, '03', '03', '成熟度与稳定性', '已落地运行，而非原型演示', TOTAL, 16)
note(s, '第三部分，成熟度与稳定性。')

# =====================================================================
# 17 成熟度
# =====================================================================
s = white()
page_title(s, '成熟度：双平面架构完整落地，能力已进入可用状态', 17, TOTAL,
           note='已完成主体开发，非原型')
mats = [
    ('系统建设', '控制平面（任务管理、事件通道、容器编排、配置管理）与执行平面（九阶段流水线、状态跟踪、事件管理、过程留档）双平面落地，Docker Compose 一键部署。',
     ['双平面架构', 'Compose 部署', '冒烟测试']),
    ('智能体', '44 个专项智能体，以及代码分析、辩论核验、漏洞验证、报告生成、自定义阶段智能体全部实现；筛选以确定性规则把关，静态扫描补选防止漏选。',
     ['44 类专项', '6 类智能体', '规则化筛选']),
    ('知识库', '通用基础审计、Java 代码审计等知识集已建成，含审计方法论技能、错题本体系与辩论角色定义，支持任务级定制与覆盖。',
     ['3 类知识', '任务级定制', '错题本回流']),
    ('工程化', '任务级容器隔离、资源配额、镜像白名单、网络隔离、API-Key 鉴权、48 小时执行超时、任务恢复与孤儿容器清理均已落地。',
     ['容器隔离', '配额与白名单', '自恢复']),
]
pos = [(0.62, 1.62), (6.78, 1.62), (0.62, 3.88), (6.78, 3.88)]
for (x, y), (t, b, tags) in zip(pos, mats):
    rect(s, x, y, 5.95, 2.02, fill=PALE, line=TINT, radius=0.05)
    rect(s, x + 0.26, y + 0.22, 0.10, 0.22, fill=TEAL2, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.46, y + 0.15, 4.8, 0.32, [{'text': t, 'size': 13, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='mat-t')
    hline(s, x + 0.26, y + 0.58, 5.42, color=TINT2, lw=0.75)
    text(s, x + 0.26, y + 0.66, 5.44, 0.90, [{'text': b, 'size': 9.2, 'color': GRAY, 'spacing': 1.5}],
         line_spacing=1.5, tag='mat-b')
    for j, tg in enumerate(tags):
        chip(s, x + 0.26 + j * 1.60, y + 1.50, 1.50, 0.32, tg, size=8,
             fill=WHITE, color=TEAL2, line=TINT2, radius=0.18)
rect(s, 0.62, 6.14, 12.1, 0.66, fill=WHITE, line=TINT, radius=0.06)
text(s, 0.90, 6.14, 11.6, 0.66,
     [{'text': '结论：主体功能已完成开发，并通过冒烟测试与真实项目审计验证，具备进入试点应用的条件。',
       'size': 10, 'color': TEAL}], anchor='m', line_spacing=1.2, tag='mat-sum')
note(s, '成熟度四个方面：系统建设、智能体、知识库、工程化，都已经是完成态，不是 PPT 上的规划。')

# =====================================================================
# 18 稳定性：容错
# =====================================================================
s = white()
page_title(s, '稳定性：异常分级处理，任何单点失败都不阻断审计', 18, TOTAL)
tx, tw = 0.62, 8.15
text(s, tx, 1.52, 5.0, 0.30, [{'text': '异常分级与降级策略', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='ft-h')
text(s, tx + 0.14, 1.94, 2.6, 0.28, [{'text': '异常场景', 'size': 8.5, 'bold': True, 'color': GRAY2}],
     line_spacing=1.0, tag='ft-h1')
text(s, tx + 2.86, 1.94, 5.0, 0.28, [{'text': '处理策略', 'size': 8.5, 'bold': True, 'color': GRAY2}],
     line_spacing=1.0, tag='ft-h2')
hline(s, tx, 2.26, tw, color=TEAL3, lw=0.9)
faults = [
    ('静态扫描失败', '记录错误，以空扫描结果继续后续流程'),
    ('代码分析解析失败', '先恢复已保存结果，仍失败则启动全部专项智能体'),
    ('智能体输出格式异常', '自动容错解析，代码片段截断可恢复'),
    ('单个专项智能体失败', '跳过该智能体，不影响整体任务'),
    ('辩论环节未开启', '明确提示跳过，不做无谓消耗'),
    ('执行容器连接失败', '任务立即标记失败，不留挂起任务'),
    ('管理端重启 / 实例异常', '自动恢复未完结任务，孤儿容器按标签统一清理'),
]
for i, (a, b) in enumerate(faults):
    y = 2.36 + i * 0.62
    if i % 2 == 0:
        rect(s, tx, y, tw, 0.56, fill=PALE, line=None, radius=0.10)
    text(s, tx + 0.14, y, 2.55, 0.56, [{'text': a, 'size': 9.2, 'bold': True, 'color': INK}],
         anchor='m', line_spacing=1.2, tag='ft-a')
    text(s, tx + 2.86, y, 5.15, 0.56, [{'text': b, 'size': 9.2, 'color': GRAY}],
         anchor='m', line_spacing=1.2, tag='ft-b')
hline(s, tx, 2.36 + 7 * 0.62, tw, color=TEAL3, lw=0.9)
rx, rw = 9.05, 3.68
rect(s, rx, 1.52, rw, 5.02, fill=PALE, line=TINT, radius=0.05)
text(s, rx + 0.22, 1.66, 3.2, 0.30, [{'text': '资源与安全边界', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='bnd-h')
bounds = [('48 h', '单任务执行上限'), ('3', '专项智能体并发'), ('1', '默认并发任务数'),
          ('CPU / 内存', '双容器独立配额'), ('独立网桥', '任务间网络隔离'),
          ('只读工具', '联网类工具一律禁用')]
for i, (k, v) in enumerate(bounds):
    y = 2.10 + i * 0.74
    text(s, rx + 0.22, y, 1.9, 0.28, [{'text': k, 'size': 11, 'bold': True, 'color': TEAL2}],
         line_spacing=1.0, tag='bnd-k')
    text(s, rx + 0.22, y + 0.28, 3.2, 0.26, [{'text': v, 'size': 8.5, 'color': GRAY}],
         line_spacing=1.0, tag='bnd-v')
note(s, '稳定性不是靠"不出错"，而是靠分级处理：扫描失败就降级继续，解析失败就回退到全量，单点失败就跳过，重启能恢复。')

# =====================================================================
# 19 可观测
# =====================================================================
s = white()
page_title(s, '过程可观测：审计不是黑盒，每个结论都能回溯', 19, TOTAL)
lead(s, 1.52, '智能体在读哪个文件、调了什么工具、正在怎么推理，都以事件流实时推送；各阶段产物同步留档，'
              '报告里的任何一个漏洞，都能回查到它由哪个智能体、依据哪份分析结论报出。', h=0.78)
text(s, 0.62, 2.48, 5.4, 0.30, [{'text': '实时事件流（双向通道）', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='ev2-h')
evs = ['进度', '阶段消息', '思维链', '工具调用与结果', '漏洞发现', '辩论对话',
       '回合统计（token/时长）', '报告分节产出']
for i, e in enumerate(evs):
    r, c = divmod(i, 2)
    chip(s, 0.62 + c * 2.74, 2.86 + r * 0.62, 2.60, 0.50, e, size=8.8,
         fill=PALE, color=INK, line=TINT, radius=0.14)
rx = 6.30
rect(s, rx, 2.48, 6.42, 3.16, fill=WHITE, line=TINT, radius=0.05)
text(s, rx + 0.24, 2.60, 5.4, 0.30, [{'text': '留档与回溯', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='arc2-h')
arcs = [('分阶段留档', '静态扫描、代码分析、漏洞清单、最终报告统一归档到任务目录'),
        ('确定性下游', '留档数据被去重、验证与报告环节直接消费，不再二次理解文字'),
        ('顺序一致', '报告内容先缓冲，待辩论等实时环节展示完毕再统一放出'),
        ('断线不丢', '历史事件支持翻页回看，重连后仍可完整复盘')]
for i, (t, d) in enumerate(arcs):
    y = 3.02 + i * 0.66
    text(s, rx + 0.26, y, 1.55, 0.28, [{'text': t, 'size': 9.5, 'bold': True, 'color': TEAL2}],
         line_spacing=1.0, tag='arc2-t')
    text(s, rx + 1.86, y - 0.02, 4.35, 0.56, [{'text': d, 'size': 8.8, 'color': GRAY}],
         line_spacing=1.35, tag='arc2-d')
rect(s, 0.62, 5.86, 12.1, 0.86, fill=TEAL, radius=0.06)
text(s, 0.92, 5.86, 11.5, 0.86,
     [{'text': '可观测的意义：审计结论可被信任、可被追责、可被复算 —— 这是智能体审计进入生产流程的前提。',
       'size': 11, 'color': WHITE}], anchor='m', line_spacing=1.2, tag='obs-sum')
note(s, '可观测解决的是信任问题：过程看得见，结论能回溯，审计结果才敢放进生产流程里用。')

# =====================================================================
# 20 效果验证
# =====================================================================
s = white()
page_title(s, '效果验证：CyberGym Level 1 独立测评', 20, TOTAL, note='真实开源软件漏洞复现基准')
stats = [('91.4%', '严格通过率', '按严格判定口径计算'),
         ('1377 / 1507', '成功任务', '完成并判定的任务数'),
         ('第 9 名', '全球排行榜', '同期公开榜单排名')]
for i, (v, k, d) in enumerate(stats):
    y = 1.62 + i * 1.52
    rect(s, 0.62, y, 4.30, 1.34, fill=PALE, line=TINT, radius=0.05)
    text(s, 0.84, y + 0.14, 3.9, 0.60, [{'text': v, 'size': 30, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='stat-v')
    text(s, 0.84, y + 0.80, 1.9, 0.26, [{'text': k, 'size': 9.5, 'bold': True, 'color': TEAL2}],
         line_spacing=1.0, tag='stat-k')
    text(s, 2.70, y + 0.82, 2.05, 0.42, [{'text': d, 'size': 8, 'color': GRAY}],
         line_spacing=1.2, tag='stat-d')
text(s, 0.62, 6.12, 4.30, 0.60,
     [{'text': '数据来源：团队测评记录，同期公开榜单。', 'size': 8, 'color': GRAY2}],
     line_spacing=1.3, tag='stat-src')
rx = 5.20
text(s, rx, 1.58, 7.5, 0.30,
     [{'text': '能力提升路径：基于任务轨迹反馈的技能自进化', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='cg-h')
text(s, rx, 1.92, 7.50, 0.92,
     [{'text': '针对源代码审计智能体难以持续积累漏洞分析经验的问题，研究基于任务轨迹反馈的 Skill 自进化技术，'
               '在同类任务数据集上形成“执行—反思—更新—验证”的多轮闭环，使能力可持续提升。',
       'size': 9.5, 'color': GRAY}], line_spacing=1.45, tag='cg-b')
loop4 = [('漏洞数据', '训练集 / 验证集'), ('技能路由', '按需装载技能节点'),
         ('轨迹反馈', '操作、工具反馈、成败'), ('门控验证', '同口径比较后冻结')]
for i, (t, d) in enumerate(loop4):
    x = rx + i * 1.86
    rect(s, x, 2.94, 1.72, 0.86, fill=WHITE, line=TINT, radius=0.08)
    text(s, x + 0.12, 3.02, 1.48, 0.26, [{'text': t, 'size': 9, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='lp-t')
    text(s, x + 0.12, 3.30, 1.50, 0.44, [{'text': d, 'size': 7.5, 'color': GRAY}],
         line_spacing=1.2, tag='lp-d')
    if i < 3:
        arrow(s, x + 1.74, 3.31, 0.10, 0.12)
text(s, rx, 3.94, 7.5, 0.56,
     [{'text': '技能版本通过门控后才进入独立测试集，避免自测偏差；测评结果在同期公开榜单中位列第 9。',
       'size': 8.8, 'color': TEAL2}], line_spacing=1.35, tag='cg-note')
rect(s, rx, 4.66, 7.50, 1.96, fill=PALE, line=TINT, radius=0.05)
text(s, rx + 0.22, 4.78, 7.0, 0.30,
     [{'text': '为什么这项结果对成熟度有意义', 'size': 10.5, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='cg2-h')
why2 = ['用的是真实开源软件漏洞复现任务，考的是“能不能真找出并说清楚”，而不是模板化问答。',
        '结果由外部独立测试集给出，与内部自测分离，可复现、可对比。',
        '能力提升来自可沉淀的技能与知识，而不是换更大的模型。']
para_list(s, rx + 0.18, 5.16, 7.10, 1.36, why2, size=8.8, spacing=1.4, gap=10)
note(s, '效果验证采用 CyberGym Level 1 独立测评：严格通过率 91.4%，1377/1507 项任务成功，同期公开榜单第 9 名，说明能力提升是可度量的。')

# =====================================================================
# 21 章节页 04
# =====================================================================
s = green()
section_divider(s, '04', '04', '推广复用潜力', '换一份任务描述，就能复用一次能力', TOTAL, 21)
note(s, '第四部分，推广复用潜力。')

# =====================================================================
# 22 复用设计
# =====================================================================
s = white()
page_title(s, '复用设计：复用的不是代码，是能力加配置', 22, TOTAL)
gx, gw = 0.62, 5.85
rect(s, gx, 1.60, gw, 4.08, fill=PALE, line=TINT, radius=0.05)
text(s, gx + 0.24, 1.72, 5.2, 0.32, [{'text': '一份任务描述 = 一次审计', 'size': 12, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='task-h')
task_items = [
    ('代码位置与语言', '指明仓库路径与技术栈，系统据此映射扫描规则集'),
    ('流程开关', '静态扫描、代码分析、辩论核验、漏洞验证、知识库、增量模式'),
    ('模型配置', '兼容多类大模型服务，按项目指定'),
    ('定制知识库', '按语言或业务场景传入专项知识'),
    ('自定义智能体', '按五类触发事件注入定制分析阶段'),
]
for i, (t, d) in enumerate(task_items):
    y = 2.14 + i * 0.62
    chip(s, gx + 0.24, y, 1.62, 0.44, t, size=8.5, fill=WHITE, color=TEAL, line=TINT, radius=0.14)
    text(s, gx + 1.98, y - 0.02, 3.70, 0.56, [{'text': d, 'size': 8.8, 'color': GRAY}],
         line_spacing=1.25, tag='task-d')
hline(s, gx + 0.24, 5.26, 5.37, color=TINT2, lw=0.75)
text(s, gx + 0.24, 5.34, 5.37, 0.30,
     [{'text': '有特殊需求时无需改动系统，换一份任务描述即可。', 'size': 9, 'bold': True, 'color': TEAL2}],
     line_spacing=1.3, tag='task-note')
rx = 6.72
reuse = [('交付形态可复用', '镜像 + Compose 交付；常驻仅控制平面与扫描服务，执行容器按任务创建、结束即回收。'),
         ('审计策略可复用', '专项白名单、任务级提示词、知识集覆盖，把企业规范与历史经验固化进流程。'),
         ('扩展方式可复用', '新增漏洞类型只需一份 YAML 智能体定义；新增语言只需补知识集与规则映射。'),
         ('接入方式可复用', '统一 API-Key 鉴权与事件通道，可被企业平台、CI/CD 直接调用。')]
for i, (t, d) in enumerate(reuse):
    y = 1.60 + i * 1.04
    rect(s, rx, y, 5.98, 0.94, fill=WHITE, line=TINT, radius=0.06)
    num_badge(s, rx + 0.18, y + 0.26, 0.42, f'0{i+1}', size=9.5)
    text(s, rx + 0.74, y + 0.11, 4.9, 0.30, [{'text': t, 'size': 10.5, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='reuse-t')
    text(s, rx + 0.74, y + 0.41, 5.06, 0.48, [{'text': d, 'size': 8.8, 'color': GRAY}],
         line_spacing=1.25, tag='reuse-d')
rect(s, 0.62, 5.86, 12.1, 0.80, fill=PALE, line=TINT, radius=0.05)
text(s, 0.90, 5.86, 11.5, 0.80,
     [{'text': '部署形态：常驻组件仅控制平面与静态扫描服务，执行容器与 AI 引擎容器按任务动态创建、结束自动回收；对外只开放控制平面端口。',
       'size': 10, 'color': GRAY}], anchor='m', line_spacing=1.3, tag='deploy')
note(s, '复用的关键是"配置化"：同一条流水线，换一份任务描述就换了一种审计，不需要为每个项目改代码。')

# =====================================================================
# 23 推广场景
# =====================================================================
s = white()
page_title(s, '推广路径：从单项目审计到集团代码安全治理', 23, TOTAL)
promo = [('研发自检', '开发 / 测试团队', '关键模块审计 · 修改后复测', '在编码阶段把问题挡在提测之前'),
         ('上线前过检', '安全 / 研发团队', '版本集中检查 · 上线评审依据', '以证据链代替经验判断，过检有据'),
         ('安全专项检查', '安全团队', '聚焦风险类型 · 定向排查', '按漏洞类型定向收敛存量风险'),
         ('平台化接入', '企业平台 / CI/CD', 'Webhook 触发 · 质量门禁', '嵌入流水线，审计自动化、常态化')]
for i, (t, who, cap, val) in enumerate(promo):
    x = 0.62 + i * 3.10
    rect(s, x, 1.66, 2.80, 2.20, fill=PALE, line=TINT, radius=0.05)
    text(s, x + 0.22, 1.78, 2.38, 0.34, [{'text': t, 'size': 12, 'bold': True, 'color': TEAL}],
         line_spacing=1.1, tag='pm-t')
    text(s, x + 0.22, 2.14, 2.38, 0.26, [{'text': who, 'size': 8.5, 'color': TEAL3}],
         line_spacing=1.0, tag='pm-w')
    hline(s, x + 0.22, 2.46, 2.36, color=TINT2, lw=0.75)
    text(s, x + 0.22, 2.56, 2.36, 0.50, [{'text': cap, 'size': 9, 'bold': True, 'color': INK}],
         line_spacing=1.3, tag='pm-c')
    text(s, x + 0.22, 3.12, 2.36, 0.68, [{'text': val, 'size': 8.8, 'color': GRAY}],
         line_spacing=1.35, tag='pm-v')
text(s, 0.62, 4.10, 4.0, 0.30, [{'text': '推广节奏：三步走', 'size': 11, 'bold': True, 'color': TEAL}],
     line_spacing=1.0, tag='step-h')
steps3 = [('第一步', '试点项目验证', '选 1–2 个自研系统全量审计，与人工审计交叉比对，形成基线报告'),
          ('第二步', '专业条线复制', '按事业部 / 专业条线推广，沉淀行业知识集与专项策略'),
          ('第三步', '全域平台接入', '接入集团统一平台与 CI/CD，形成代码安全治理常态')]
for i, (n, t, d) in enumerate(steps3):
    x = 0.62 + i * 4.10
    rect(s, x, 4.46, 3.90, 1.30, fill=WHITE, line=TINT, radius=0.06)
    text(s, x + 0.22, 4.58, 0.9, 0.26, [{'text': n, 'size': 8.5, 'color': TEAL3}],
         line_spacing=1.0, tag='s3-n')
    text(s, x + 0.84, 4.56, 2.86, 0.30, [{'text': t, 'size': 10.5, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='s3-t')
    hline(s, x + 0.22, 4.92, 3.46, color=TINT2, lw=0.75)
    text(s, x + 0.22, 5.00, 3.46, 0.70, [{'text': d, 'size': 8.8, 'color': GRAY}],
         line_spacing=1.4, tag='s3-d')
text(s, 0.62, 6.16, 12.0, 0.40,
     [{'text': '复用的一致性来自同一套方法论与知识集：项目越多，错题本与知识沉淀越厚，边际成本越低。',
       'size': 9, 'color': GRAY}], line_spacing=1.3, tag='promo-note')
note(s, '推广分三步：试点验证、条线复制、全域接入。每推进一步，知识集与错题本都在变厚，边际成本递减。')

# =====================================================================
# 24 演进路线
# =====================================================================
s = white()
page_title(s, '演进路线：能力完善 → 深度效率 → 场景集成', 24, TOTAL)
plan = [('V1.1', '评估体系建设与能力完善', [
            '构建评估数据集，定义检出率、误报率、平均审计时长、token 成本等指标',
            '对辩论机制效果做量化验证，优化辩论提示词与裁决标准',
            '扩充知识库错题本，建立误报回流沉淀机制',
            '在 2–3 个真实项目上完成基线测评，形成对比报告']),
        ('V1.2', '审计深度与效率优化', [
            '基于项目特征实现语言与框架精准路由，减少无效智能体启动',
            '新增大项目分片与断点续审能力',
            '扩充静态扫描规则集，提升代码知识图谱索引覆盖与检索质量',
            '建立任务分片调度与失败续跑策略，压缩长任务的等待时间']),
        ('V1.3', '场景深化与集成', [
            'CI/CD 深度集成：Webhook 触发增量审计与结果质量门禁',
            '增强漏洞验证的协议支持，扩充 Go、C# 等语言智能体与知识集',
            '优化多任务并发与算力调度，支撑规模化落地',
            '沉淀集团级代码安全知识集与专项审计策略模板'])]
for i, (v, t, items) in enumerate(plan):
    x = 0.62 + i * 4.10
    rect(s, x, 1.66, 3.90, 3.48, fill=PALE, line=TINT, radius=0.05)
    text(s, x + 0.24, 1.78, 1.2, 0.44, [{'text': v, 'size': 19, 'bold': True, 'color': TEAL}],
         line_spacing=1.0, tag='pl-v')
    text(s, x + 0.24, 2.24, 3.42, 0.30, [{'text': t, 'size': 10.5, 'bold': True, 'color': TEAL2}],
         line_spacing=1.1, tag='pl-t')
    hline(s, x + 0.24, 2.62, 3.42, color=TINT2, lw=0.75)
    para_list(s, x + 0.24, 2.74, 3.44, 2.44, items, size=8.8, spacing=1.4, gap=12)
rect(s, 0.62, 5.36, 12.1, 0.78, fill=WHITE, line=TINT, radius=0.06)
text(s, 0.90, 5.36, 11.6, 0.78,
     [{'text': '以上为规划项，排期以研发资源确认为准；与生产系统对接前的验证与灰度策略另行评估。',
       'size': 9.5, 'color': GRAY}], anchor='m', line_spacing=1.25, tag='plan-note')
note(s, '后续三个版本的路线：先把评估体系建起来，再优化深度与效率，最后做场景集成与规模化。')

# =====================================================================
# 25 结束页
# =====================================================================
s = green()
hline(s, 1.18, 2.55, 0.62, color=WHITE, lw=2.2)
text(s, 1.16, 2.72, 8.0, 0.86, [{'text': '感谢聆听，敬请批评指正', 'size': 38, 'bold': True, 'color': WHITE}],
     line_spacing=1.15, tag='end-t')
text(s, 1.18, 3.78, 6.4, 0.40, [{'text': '源代码审计智能体', 'size': 16, 'color': CREAM}],
     line_spacing=1.2, tag='end-s')
hline(s, 1.18, 4.42, 2.15, color=MINT, lw=1.0)
text(s, 1.18, 4.60, 4.8, 0.34,
     [{'text': '国网电力科学研究院有限公司（南瑞集团有限公司）', 'size': 12, 'color': CREAM}],
     line_spacing=1.2, tag='end-org')
note(s, '汇报完毕，请各位领导、评委批评指正。')

# =====================================================================
# 26 附录：44 个专项智能体清单
# =====================================================================
s = white()
page_title(s, '附录：44 个专项审计智能体清单', 26, TOTAL, note='按漏洞类型垂直划分')
appendix = [
    ('注入类', 7, 'SQL 注入 · 命令注入 · 表达式注入 · 模板注入 · NoSQL 注入 · 日志注入 · 格式化字符串'),
    ('Web 前端与交互类', 6, '跨站脚本 · 跨站请求伪造 · 点击劫持 · 开放重定向 · 文件上传 · HTTP 走私'),
    ('访问控制类', 6, '认证绕过 · 越权 · 提权 · 会话管理 · OAuth 与 SSO · API 安全'),
    ('业务与逻辑类', 3, '业务逻辑 · 竞态条件 · 异常处理'),
]
appendix2 = [
    ('服务端与数据类', 9, 'SSRF · 外部实体注入 · 路径穿越 · 反序列化 · 不安全反射 · 原型污染 · 信息泄露 · 密钥暴露 · 密码学误用'),
    ('内存安全类（C 与 C++）', 8, '栈溢出 · 堆溢出 · 释放后使用 · 双重释放 · 悬垂指针 · 整数溢出 · 类型混淆 · 资源生命周期'),
    ('其他', 5, '依赖组件漏洞 · 编码绕过 · 拒绝服务 · 提示注入 · 归档解压'),
]
for col, grp, x in ((0, appendix, 0.62), (1, appendix2, 6.78)):
    for i, (name, n, items) in enumerate(grp):
        y = 1.62 + i * 1.14
        rect(s, x, y, 5.90, 1.02, fill=PALE, line=TINT, radius=0.05)
        num_badge(s, x + 0.20, y + 0.16, 0.40, str(n), size=10.5)
        text(s, x + 0.72, y + 0.10, 4.8, 0.30, [{'text': name, 'size': 10.5, 'bold': True, 'color': TEAL}],
             line_spacing=1.0, tag='ap-t')
        text(s, x + 0.72, y + 0.42, 4.98, 0.64, [{'text': items, 'size': 8.4, 'color': GRAY}],
             line_spacing=1.35, tag='ap-i')
rect(s, 6.78, 5.04, 5.90, 1.02, fill=TINT, line=None, radius=0.05)
text(s, 7.00, 5.14, 5.46, 0.84,
     [{'text': '除专项审计智能体外，系统还内置代码分析、辩论核验（正 / 反 / 裁）、漏洞验证、报告生成与自定义阶段智能体。',
       'size': 9, 'color': TEAL}], line_spacing=1.45, tag='ap-note')
text(s, 0.62, 6.20, 5.90, 0.36,
     [{'text': '每个智能体定义含目标语言与框架、CWE 编号、扫描规则映射、攻击面关键词、排除信号与检测要点提示词。',
       'size': 8.4, 'color': GRAY2}], line_spacing=1.3, tag='ap-note2')
note(s, '附录列出 44 个专项智能体的分类清单，可按需裁剪成白名单，也可按新漏洞类型扩充 YAML 定义。')

cp = prs.core_properties
cp.title = '源代码审计智能体'
cp.subject = '业务价值 · 技术创新性 · 成熟度与稳定性 · 推广复用潜力'
cp.author = '国网电力科学研究院有限公司（南瑞集团有限公司）'
cp.keywords = '源代码审计;多智能体;漏洞挖掘;代码安全'
prs.save(OUT)
print('saved', OUT)
D.report()
