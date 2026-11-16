# -*- coding: utf-8 -*-
"""轻量 PPT 构建库：基于模板母版（国网绿底模板）绘制版式，附带文字溢出检查。"""
import copy
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------- 设计token ----------
TEAL   = RGBColor(0x00, 0x6F, 0x6B)   # 主色 深青
TEAL_D = RGBColor(0x00, 0x57, 0x54)   # 更深
TEAL2  = RGBColor(0x22, 0x82, 0x7F)   # 次级
TEAL3  = RGBColor(0x4A, 0xA3, 0xA0)   # 线条
MINT   = RGBColor(0x8E, 0xBD, 0xBC)   # 浅线
PALE   = RGBColor(0xF4, 0xFA, 0xFA)   # 卡片底
PALE2  = RGBColor(0xEE, 0xF7, 0xF7)
TINT   = RGBColor(0xE3, 0xF1, 0xF0)   # 卡片描边/浅块
TINT2  = RGBColor(0xCD, 0xE7, 0xE5)
INK    = RGBColor(0x12, 0x12, 0x12)
GRAY   = RGBColor(0x53, 0x69, 0x6A)
GRAY2  = RGBColor(0x7A, 0x8E, 0x8F)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
CREAM  = RGBColor(0xE3, 0xF1, 0xF0)
GOLD   = RGBColor(0xBA, 0x84, 0x37)

FONT = "微软雅黑"

SW, SH = 13.3333, 7.5

_checks = []   # (slide_no, 描述, 需求高, 可用高)


# ---------- 文本度量 ----------
def _char_w(ch, size):
    """估算单字符宽度（pt）。"""
    o = ord(ch)
    if o < 0x2E80:            # 半角
        if ch == ' ':
            return size * 0.30
        if ch in 'iljI.,:;|!\'`':
            return size * 0.28
        if ch in 'mwMW@%':
            return size * 0.85
        return size * 0.53
    return size * 1.0


def measure_lines(text, width_in, size, ins_lr=0.0):
    """返回 (行数, 每行字符数参考)。"""
    avail = (width_in - 2 * ins_lr) * 72.0
    if avail <= 10:
        avail = 10
    lines, cur = 1, 0.0
    for ch in text:
        w = _char_w(ch, size)
        if cur + w > avail:
            lines += 1
            cur = w
        else:
            cur += w
    return lines


def block_height(text_lines, width_in, size, line_spacing=1.45, space_before=0.0):
    """估算多段文本所需高度（英寸）。"""
    h = 0.0
    for i, t in enumerate(text_lines):
        if not t:
            h += size * 0.6 / 72.0
            continue
        n = measure_lines(t, width_in, size)
        h += n * size * line_spacing / 72.0
        if i:
            h += space_before / 72.0
    return h


# ---------- 基础图元 ----------
def rect(slide, x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         radius=0.08, shadow=False, dash=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
        if dash:
            from pptx.enum.dml import MSO_LINE_DASH_STYLE
            s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if not shadow:
        # 去掉主题阴影
        spPr = s._element.spPr
        el = spPr.find(qn('a:effectLst'))
        if el is None:
            spPr.append(copy.deepcopy(_EMPTY_EFFECT))
    s.text_frame.word_wrap = True
    s.text_frame.auto_size = MSO_AUTO_SIZE.NONE
    return s


from lxml import etree
_EMPTY_EFFECT = etree.SubElement(etree.Element('dummy'), qn('a:effectLst'))


def hline(slide, x, y, w, color=TEAL3, lw=1.0, dash=False):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x + w), Inches(y))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    if dash:
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return c


def vline(slide, x, y, h, color=TEAL3, lw=1.0):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x), Inches(y + h))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    return c


def arrow(slide, x, y, w, h=0.16, color=MINT, direction='right'):
    shp = MSO_SHAPE.RIGHT_ARROW if direction == 'right' else MSO_SHAPE.LEFT_ARROW
    s = slide.shapes.add_shape(shp, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background()
    return s


def _set_run(r, size, color, bold, font=FONT, italic=False):
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font
    # 中文字体
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = etree.SubElement(rPr, qn('a:ea'))
    ea.set('typeface', font)
    cs = rPr.find(qn('a:cs'))
    if cs is None:
        cs = etree.SubElement(rPr, qn('a:cs'))
    cs.set('typeface', font)


def text(slide, x, y, w, h, paras, size=14, color=INK, bold=False, align='l',
         anchor='t', line_spacing=1.45, space_before=0.0, ins=(0.0, 0.0, 0.0, 0.0),
         wrap=True, slide_no=None, tag='', autofit=False):
    """paras: str | list[str] | list[dict(text=,size=,color=,bold=,space_before=,align=,spacing=)]"""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    l, t, r, b = ins
    tf.margin_left = Inches(l); tf.margin_right = Inches(r)
    tf.margin_top = Inches(t); tf.margin_bottom = Inches(b)
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]

    if isinstance(paras, str):
        paras = [paras]
    plain = []
    for i, p in enumerate(paras):
        if isinstance(p, str):
            p = {'text': p}
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        sz = p.get('size', size)
        para.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER,
                          'r': PP_ALIGN.RIGHT, 'j': PP_ALIGN.JUSTIFY}[p.get('align', align)]
        para.line_spacing = p.get('spacing', line_spacing)
        sb = p.get('space_before', space_before if i else 0.0)
        if sb:
            para.space_before = Pt(sb)
        if 'space_after' in p:
            para.space_after = Pt(p['space_after'])
        # runs: text 或 parts=[(txt, dict)]
        parts = p.get('parts') or [(p.get('text', ''), {})]
        for txt, ov in parts:
            run = para.add_run()
            run.text = txt
            _set_run(run, ov.get('size', sz), ov.get('color', p.get('color', color)),
                     ov.get('bold', p.get('bold', bold)), font=ov.get('font', FONT),
                     italic=ov.get('italic', False))
        plain.append(p.get('text') or ''.join(t for t, _ in parts))

    # 溢出估算
    need = 0.0
    for i, p in enumerate(paras):
        if isinstance(p, str):
            p = {'text': p}
        sz = p.get('size', size)
        need += block_height([plain[i]], w, sz, p.get('spacing', line_spacing),
                             p.get('space_before', space_before if i else 0.0))
    _checks.append((slide_no, f"text:{tag or (plain[0][:14] if plain else '')}",
                   round(need, 2), round(h, 2), round(x, 2), round(y, 2), round(w, 2)))
    return tb


def chip(slide, x, y, w, h, label, size=11, fill=TINT, color=TEAL, bold=False, radius=0.28, line=None):
    s = rect(slide, x, y, w, h, fill=fill, line=line, radius=radius)
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.04); tf.margin_right = Inches(0.04)
    tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    _set_run(r, size, color, bold)
    return s


def num_badge(slide, x, y, d, label, size=12, fill=TEAL2, color=WHITE, bold=True):
    s = rect(slide, x, y, d, d, fill=fill, radius=0.22, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = s.text_frame
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    _set_run(r, size, color, bold)
    return s


# ---------- 版式 ----------
def page_title(slide, title, no, total, note=None):
    text(slide, 0.62, 0.40, 9.6, 0.55, [{'text': title, 'size': 25, 'bold': True, 'color': TEAL}],
         line_spacing=1.15, slide_no=no, tag='title')
    if note:
        text(slide, 9.4, 0.62, 3.32, 0.34, [{'text': note, 'size': 10.5, 'color': GRAY2, 'align': 'r'}],
             line_spacing=1.0, slide_no=no, tag='title-note')
    pageno(slide, no, total)


def pageno(slide, no, total):
    text(slide, 11.75, 7.04, 0.95, 0.28,
         [{'text': f"{no:02d} / {total}", 'size': 9.5, 'color': GRAY2, 'align': 'r'}],
         line_spacing=1.0, slide_no=no, tag='pageno')


def lead(slide, y, body, h=0.95, size=12.5, x=0.62, w=12.1, slide_no=None):
    """标题下的导语条：浅底 + 左侧色条。"""
    rect(slide, x, y, w, h, fill=PALE, line=TINT, radius=0.05)
    rect(slide, x, y + 0.10, 0.055, h - 0.20, fill=TEAL2, shape=MSO_SHAPE.RECTANGLE)
    text(slide, x + 0.22, y, w - 0.5, h, [{'text': body, 'size': size, 'color': GRAY, 'spacing': 1.5}],
         anchor='m', line_spacing=1.5, slide_no=slide_no, tag='lead')
    return y + h


def section_divider(slide, no, cn, title, tagline, total, pageno_val=None):
    text(slide, 0.98, 2.16, 4.6, 1.30, [{'text': no, 'size': 84, 'bold': True, 'color': TEAL3}],
         line_spacing=1.0, slide_no=None, tag='div-no')
    text(slide, 1.02, 3.48, 5.2, 0.70, [{'text': title, 'size': 34, 'bold': True, 'color': WHITE}],
         line_spacing=1.1, slide_no=None, tag='div-title')
    hline(slide, 1.05, 4.26, 2.2, color=WHITE, lw=1.4)
    text(slide, 1.05, 4.36, 4.4, 0.42, [{'text': tagline, 'size': 13.5, 'color': WHITE}],
         line_spacing=1.2, slide_no=None, tag='div-tagline')
    text(slide, 11.75, 7.04, 0.95, 0.3,
         [{'text': f"{pageno_val or '--':0>2} / {total}" if isinstance(pageno_val, int) else f"-- / {total}",
           'size': 9.5, 'color': CREAM, 'align': 'r'}],
         line_spacing=1.0, slide_no=None, tag='div-pg')


def report():
    bad = [c for c in _checks if c[2] > c[3] + 0.02]
    print(f"\n=== 溢出检查：共 {len(_checks)} 处文本，超限 {len(bad)} 处 ===")
    for c in sorted(bad, key=lambda x: -(x[2] - x[3]))[:40]:
        print(f"  slide {c[0]} {c[1]:32s} need={c[2]} box={c[3]}  @({c[4]},{c[5]}) w={c[6]}")
    return bad
