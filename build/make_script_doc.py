# -*- coding: utf-8 -*-
"""从 4 分钟版 PPTX 的备注生成《汇报稿》Word 文档。"""
from pptx import Presentation
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

SRC = '/home/user/123/源代码审计智能体-4分钟版.pptx'
OUT = '/home/user/123/源代码审计智能体-4分钟汇报稿.docx'
BLUE = RGBColor(0x26, 0x6A, 0xBD)
GOLD = RGBColor(0xA9, 0x7F, 0x35)
GRAY = RGBColor(0x5B, 0x64, 0x72)


def page_title(slide, idx, total):
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        try:
            if abs(sh.left / 914400 - 0.80) < 0.06 and abs(sh.top / 914400 - 0.44) < 0.06:
                t = sh.text_frame.text.strip()
                if t:
                    return t
        except Exception:
            pass
    return {1: '封面', 2: '目录', total: '致谢'}.get(idx, f'第 {idx} 页')


prs = Presentation(SRC)
rows = []
for i, s in enumerate(prs.slides, 1):
    note = s.notes_slide.notes_text_frame.text
    parts = note.split('\n')
    head = parts[0].strip('【】')
    span, _, tag = head.partition(' ')
    body = parts[1].strip() if len(parts) > 1 else ''
    extra = ''
    for p in parts[2:]:
        if '追问备用' in p:
            extra = p.replace('〔追问备用，不计入 4 分钟〕', '').strip()
    rows.append(dict(no=i, title=page_title(s, i, len(prs.slides)), span=span, tag=tag,
                     body=body, extra=extra))

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)
style = doc.styles['Normal']
style.font.name = '微软雅黑'
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')


def para(text, size=10.5, bold=False, color=None, space_after=4, align=None, indent=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.35
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if align:
        p.alignment = align
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    if color:
        r.font.color.rgb = color
    r.font.name = '微软雅黑'
    r._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    return p


total_chars = sum(len(r['body']) for r in rows)
para('瑞智源代码审计智能体', 18, True, BLUE, 2)
para('4 分钟汇报稿（逐页备注版）', 13, True, GRAY, 10)
para(f'共 {len(rows)} 页 · 主稿 {total_chars} 字 · 全程约 4 分 03 秒（按 270 字/分）', 10, False, GRAY, 6)

para('使用说明', 11, True, GOLD, 3)
for i, t in enumerate([
        '每页先看时间点，再到“主稿”——这段是要照着念的；',
        '〔追问备用〕只在评委追问或时间有余时使用，不占 4 分钟；',
        '若现场超时，优先省掉第 14 页“路线”（约 8 秒）和第 2 页“目录”（约 13 秒）。'], 1):
    para(f'{i}. {t}', 9.5, False, GRAY, 2, indent=0.4)

para('时间轴', 11, True, GOLD, 3)
tbl = doc.add_table(rows=1, cols=4)
tbl.style = 'Table Grid'
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = ['页码', '页面内容', '时间点', '时长']
for c, h in enumerate(hdr):
    cell = tbl.rows[0].cells[c]
    cell.text = ''
    r = cell.paragraphs[0].add_run(h)
    r.bold = True
    r.font.size = Pt(9)
import re
for r in rows:
    cells = tbl.add_row().cells
    m = re.search(r'约\s*(\d+)\s*秒', r['tag'])
    secs = (m.group(1) if m else '') + ' 秒'
    tag = re.sub(r'\s*·\s*约\s*\d+\s*秒', '', r['tag'])
    for c, v in enumerate([f"P{r['no']:02d}", r['title'][:26], r['span'] + ' · ' + tag, secs]):
        cells[c].text = ''
        run = cells[c].paragraphs[0].add_run(v)
        run.font.size = Pt(9)
for row in tbl.rows:
    for c in row.cells:
        c.width = Cm(4.1)

doc.add_page_break()
para('逐页汇报词', 14, True, BLUE, 8)

for r in rows:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"P{r['no']:02d}  {r['title']}")
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = BLUE
    run.font.name = '微软雅黑'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(3)
    r2 = p2.add_run(f"{r['span']} · {r['tag']}")
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = GRAY
    para(r['body'], 11, False, None, 3)
    if r['extra']:
        para('〔追问备用〕' + r['extra'], 9.5, False, GOLD, 6)

doc.save(OUT)
print('saved', OUT, 'pages', len(rows))
