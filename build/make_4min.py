# -*- coding: utf-8 -*-
"""对用户最新版做内容修订，并派生 4 分钟汇报版。

修订项：
1) 产品名统一为“瑞智源代码审计智能体”；
2) CyberGym 榜单与数据来源写清；
3) 封面标题/副标题版式修正、尾页间隔号统一。
产物：
- 源代码审计智能体-技术与成果汇报-完整版.pptx（25 页）
- 源代码审计智能体-4分钟版.pptx（11 页，页脚重排，逐页汇报词按画面重写）
"""
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

SRC = '/home/user/123/用户修改版.pptx'
FULL = '/home/user/123/源代码审计智能体-技术与成果汇报-完整版.pptx'
MINI = '/home/user/123/源代码审计智能体-4分钟版.pptx'
CREAM = RGBColor(0xE5, 0xDE, 0xDB)
BRAND = '瑞智源代码审计智能体'
KEEP = [0, 1, 3, 4, 5, 10, 12, 16, 19, 22, 24]


# ---------------------------------------------------------------- 通用修订
def apply_fixes(prs):
    for slide in prs.slides:
        for sh in slide.shapes:
            if not sh.has_text_frame:
                continue
            for para in sh.text_frame.paragraphs:
                for r in para.runs:
                    t = r.text
                    if '源代码审计智能体' in t and BRAND not in t:
                        r.text = t.replace('源代码审计智能体', BRAND)
                    elif '测评结果在同期公开榜单中位列第 9' in t:
                        r.text = t.replace('测评结果在同期公开榜单中位列第 9',
                                           '测评结果位列 CyberGym Level 1 公开榜单第 9 名')
                    elif t.startswith('数据来源：团队测评记录'):
                        r.text = '数据来源：CyberGym Level 1 公开评测榜单（2026 年）· 团队测评记录。'
                    elif '公开榜单排名' in t:
                        r.text = 'CyberGym Level 1 公开榜单'
                    elif t.strip() == BRAND + '·基于多智能体的源代码审计系统':
                        r.text = BRAND + ' · 基于多智能体的源代码审计系统'

    # 备注（汇报稿）同步改名与榜单口径
    for slide in prs.slides:
        if not slide.has_notes_slide:
            continue
        tf = slide.notes_slide.notes_text_frame
        t = tf.text
        if not t:
            continue
        t = t.replace(BRAND, '\x00')
        t = t.replace('源代码审计智能体', BRAND)
        t = t.replace('\x00', BRAND)
        t = t.replace('同期公开榜单', '同期 CyberGym Level 1 公开榜单')
        tf.text = t

    # 封面：标题 50pt 居中、副标题上移到标题下方并调为米白 16pt
    for sh in prs.slides[0].shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text.strip()
        if t == BRAND:
            p = sh.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(50)
            p.alignment = PP_ALIGN.CENTER
            sh.left, sh.top = Inches(0.8), Inches(3.48)
            sh.width, sh.height = Inches(11.97), Inches(0.86)
        elif t.startswith('——基于多智能体'):
            p = sh.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.size = Pt(16)
                r.font.color.rgb = CREAM
            sh.left, sh.top = Inches(0.8), Inches(4.32)
            sh.width, sh.height = Inches(11.97), Inches(0.36)


# ---------------------------------------------------------------- 4 分钟版汇报词
BODY = {
1: ('开场', '各位评委好。今天汇报瑞智源代码审计智能体——用多智能体把专家经验工程化，让代码审计成为一条可复制的流水线。'
          '汇报分四部分：业务价值、技术创新、成熟度、推广复用。'),
2: ('结构', '四部分对应四个问题：有没有用、有没有创新、靠不靠得住、能不能复制。'),
3: ('痛点', '传统审计卡在四点：覆盖不全，专家只能抽检；误报漏报并存，规则只给线索不给上下文；结论难核实，'
          '清单没有数据流、无法实证；经验难沉淀，能力长在个人身上。四条叠加，专家能力成了产能天花板。'),
4: ('解法', '解法是把审计拆成九个阶段：知识库释放、静态扫描、代码分析、筛选智能体，44 类专项并行挖掘，'
          '去重后进两道质量关——三方辩论与隔离环境实证，最后自动出报告。三条原则：四类智能体分工、'
          '规则可判定的交给代码、全过程实时可见。'),
5: ('价值', '价值四点：覆盖更全，44 类专项按类型划分、逐类追踪数据流；结论更准，候选漏洞全部经三方辩论，'
          '驳回不入库，每条带 CWE 与完整数据流；响应更快，增量只审变动文件；沉淀可复用，方法论与错题本进知识库。'),
6: ('创新总览', '四项创新：流水线编排解决做得全，三方辩论解决判得准，实证验证解决能落地，知识库自进化解决经验积累。'
              '核心只有一句：把大模型的不确定性关进工程的笼子。'),
7: ('辩论', '重点讲辩论。候选漏洞先暂存；反方假设它是误报，依托代码逐条质疑；正方构建攻击链回应；反方复判；'
          '裁判按可达性和可控程度终裁。结局三态：采纳入库、驳回不入库、存疑交人工。误报在下游之前就被拦掉，'
          '记录自带辩论痕迹，复核不用从零判断。'),
8: ('成熟度', '这已是可用系统，不是原型：双平面落地、Compose 部署；44 类专项加五类阶段智能体全部实现；'
             '知识集支持任务级定制；容器隔离、配额、白名单、48 小时超时都已落地。稳定性靠分级处理，'
             '单点失败不阻断审计。'),
9: ('效果', '效果有外部参照：CyberGym Level 1 独立测评，严格通过率 91.4%，1377 项任务成功，公开榜单第 9 名。'
          '提升来自任务轨迹反馈的技能自进化，不是换了个更大的模型。'),
10: ('推广', '推广有四类场景：研发自检、上线前过检、安全专项检查、平台化接入，越往后越靠流水线自动化。'
           '节奏三步走：试点验证、条线复制、全域接入集团平台与 CI/CD。项目越多，错题本越厚，边际成本越低。'),
11: ('收尾', '总结一句：把经验工程化，把不确定性变成可证伪，让结论站得住，让它能被复制。汇报完毕，请评委批评指正，谢谢。'),
}
RATE = 240.0   # 字/分钟


def build_notes():
    """按字数自动生成时间戳，保证备注与 4 分钟节奏一致。"""
    out, t = {}, 0.0
    for i in sorted(BODY):
        tag, body = BODY[i]
        dur = len(body) / RATE * 60
        out[i] = f'【{int(t)//60}:{int(t)%60:02d}–{int(t+dur)//60}:{int(t+dur)%60:02d} {tag}】\n{body}'
        t += dur
    return out, t


# ---------------------------------------------------------------- 主流程
prs = Presentation(SRC)
apply_fixes(prs)
prs.core_properties.title = BRAND
prs.core_properties.subject = '业务价值与成效 · 技术创新性 · 成熟度与稳定性 · 推广复用潜力'
prs.save(FULL)
print('saved', FULL, 'slides', len(prs.slides))

# 压缩为 11 页
prs = Presentation(FULL)
sldIdLst = prs.slides._sldIdLst
for i, sldId in enumerate(list(sldIdLst)):
    if i not in KEEP:
        prs.part.drop_rel(sldId.rId)
        sldIdLst.remove(sldId)

total = len(KEEP)
for no, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        if sh.has_text_frame and re.fullmatch(r'\d\d\s*/\s*\d\d', sh.text_frame.text.strip()):
            p = sh.text_frame.paragraphs[0]
            p.runs[0].text = f'{no:02d} / {total}'
            for r in p.runs[1:]:
                r.text = ''

notes, total_s = build_notes()
for i, sl in enumerate(prs.slides, 1):
    sl.notes_slide.notes_text_frame.text = notes[i]

prs.core_properties.title = BRAND + '（4 分钟汇报版）'
prs.save(MINI)
print('saved', MINI, 'slides', len(prs.slides))
chars = sum(len(v[1]) for v in BODY.values())
print(f'汇报词 {chars} 字，按 {RATE:.0f} 字/分 ≈ {chars/RATE:.2f} 分钟（脚本累计 {int(total_s)//60}:{int(total_s)%60:02d}）')
for i in sorted(BODY):
    print(f'  P{i:02d} {len(BODY[i][1]):3d}字  {notes[i].splitlines()[0]}')
