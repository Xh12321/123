# -*- coding: utf-8 -*-
"""把用户修改版（25 页）压缩为 4 分钟版（11 页），并修正封面版式、重写逐页汇报词。"""
import re, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

SRC = '/home/user/123/用户修改版.pptx'
OUT = '/home/user/123/源代码审计智能体-4分钟版.pptx'

# 保留页（0 基）：封面、目录、四重困境、流水线、四项价值、创新总览、辩论、成熟度、CyberGym、推广、致谢
KEEP = [0, 1, 3, 4, 5, 10, 12, 16, 19, 22, 24]

prs = Presentation(SRC)
sldIdLst = prs.slides._sldIdLst
ids = list(sldIdLst)
for i, sldId in enumerate(ids):
    if i not in KEEP:
        prs.part.drop_rel(sldId.rId)
        sldIdLst.remove(sldId)

total = len(KEEP)

# ---------- 页码重排：NN / 11 ----------
for no, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        if sh.has_text_frame and re.fullmatch(r'\d\d\s*/\s*\d\d', sh.text_frame.text.strip()):
            p = sh.text_frame.paragraphs[0]
            p.runs[0].text = f'{no:02d} / {total}'
            for r in p.runs[1:]:
                r.text = ''

# ---------- 封面版式修正 ----------
cover = prs.slides[0]
CREAM = RGBColor(0xE5, 0xDE, 0xDB)
for sh in cover.shapes:
    if not sh.has_text_frame:
        continue
    t = sh.text_frame.text.strip()
    if t == '瑞智源代码审计智能体':
        r = sh.text_frame.paragraphs[0].runs[0]
        r.font.size = Pt(50)
        sh.left, sh.top = Inches(0.8), Inches(3.48)
        sh.width, sh.height = Inches(11.97), Inches(0.86)
        sh.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    elif t.startswith('——基于多智能体'):
        p = sh.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        for r in p.runs:
            r.font.size = Pt(16)
            r.font.color.rgb = CREAM
        sh.left, sh.top = Inches(0.8), Inches(4.32)
        sh.width, sh.height = Inches(11.97), Inches(0.36)

NOTES = {
1: "【0:00–0:16 开场】\n各位评委好。我们汇报瑞智源代码审计智能体：用多智能体把专家经验工程化，让代码审计成为"
   "可复制的流水线。汇报分价值、创新、成熟度、推广四部分。",
2: "【0:15–0:25 结构】\n四部分对应四个问题：有没有用、有没有创新、靠不靠得住、能不能复制。",
3: "【0:25–0:47 痛点】\n传统审计卡在四点：专家精力有限只能抽检，覆盖不全；规则扫描只给线索，误报漏报并存；"
   "清单缺数据流，结论难核实；能力长在个人身上，经验难沉淀。专家能力成了产能的天花板。",
4: "【0:47–1:15 解法】\n解法是把审计拆成九个阶段：从知识库释放、静态扫描、代码分析到智能体筛选，"
   "44 类专项并行挖掘，去重后进两道质量关——三方辩论核验与隔离环境实证，最后自动出报告。"
   "能靠规则确定的用代码解决，需要推理的交给智能体，每阶段产物留档。",
5: "【1:15–1:43 价值】\n价值落在四点：覆盖更全，44 类专项按漏洞类型划分、逐类追踪数据流；结论更准，"
   "候选漏洞全部经三方辩论，驳回不入库，每条带 CWE 和完整数据流；响应更快，增量模式只审变动文件；"
   "沉淀可复用，方法论与错题本进知识库。",
6: "【1:43–2:01 创新总览】\n四项创新各有分工：流水线编排解决做得全，三方辩论解决判得准，实证验证解决能落地，"
   "知识库自进化解决经验能不能积累。核心是把大模型的不确定性关进工程的笼子。",
7: "【2:01–2:34 辩论】\n重点讲辩论。候选漏洞先暂存、不进结论；反方假设它是误报，依托代码逐条质疑；"
   "正方必须构建攻击链回应；反方复判；裁判按可达性和攻击者可控程度终裁。结局三态：采纳、驳回、存疑——"
   "驳回不入库，存疑交人工。误报在下游之前被拦掉，通过对抗的记录自带辩论痕迹，复核不用从零判断。",
8: "【2:34–2:56 成熟度】\n这已是可用系统，不是原型：双平面落地、Compose 部署，44 类专项加五类阶段智能体全部实现，"
   "隔离、配额、白名单、48 小时超时都已落地。稳定性靠分级处理：扫描失败降级继续、解析失败回退全量、"
   "单点失败跳过、重启自动恢复，任何单点失败都不阻断审计。",
9: "【2:56–3:20 效果】\n效果有外部参照：CyberGym Level 1 独立测评，严格通过率 91.4%，1377 项任务成功，"
   "同期公开榜单第 9 名。能力来自基于任务轨迹的技能自进化，不是换了个更大的模型。",
10: "【3:20–3:44 推广】\n最后是推广。复用的不是代码，是能力和配置：一份任务描述就是一次审计，"
    "新增漏洞类型只要一份 YAML。路径三步走：试点验证、条线复制、全域接入集团平台与 CI/CD。项目越多，"
    "错题本越厚，边际成本越低。",
11: "【3:44–4:00 收尾】\n总结一句：把经验工程化，把不确定性变成可证伪，让结论站得住，让它能被复制。"
    "汇报完毕，请评委批评指正，谢谢。",
}

for i, sl in enumerate(prs.slides, 1):
    sl.notes_slide.notes_text_frame.text = NOTES[i]

cp = prs.core_properties
cp.title = '瑞智源代码审计智能体（4 分钟汇报版）'
cp.subject = '业务价值与成效 · 技术创新性 · 成熟度与稳定性 · 推广复用潜力'
prs.save(OUT)
print('saved', OUT, 'slides', len(prs.slides._sldIdLst))
words = sum(len(''.join(v.split('\n')[1:])) for v in NOTES.values())
for k, v in NOTES.items():
    body = ''.join(v.split('\n')[1:])
    print(f'  P{k:02d} {len(body):3d}字 ≈ {len(body)/230*60:4.1f}s')
print('合计', words, '字 ≈', f'{words/230:.2f}', '分钟（按 230 字/分）')
