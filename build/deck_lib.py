# -*- coding: utf-8 -*-
"""PPT 构建库（对齐官方模板：深蓝 + 金色、思源宋体/思源黑体、圆角白底面板）。"""
import copy
from lxml import etree
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------------- 设计 token（取自模板主题） ----------------
BLUE   = RGBColor(0x26, 0x6A, 0xBD)   # accent1
BLUE_D = RGBColor(0x1B, 0x4E, 0x8C)
BLUE_M = RGBColor(0x4A, 0x85, 0xC8)
GOLD   = RGBColor(0xDF, 0xB8, 0x65)   # accent2
GOLD_D = RGBColor(0xA9, 0x7F, 0x35)
INK    = RGBColor(0x39, 0x30, 0x2A)   # dk1
GRAY   = RGBColor(0x5B, 0x64, 0x72)
GRAY2  = RGBColor(0x8A, 0x8F, 0x98)
PALE   = RGBColor(0xF4, 0xF7, 0xFC)
TINT   = RGBColor(0xDF, 0xE6, 0xF2)
TINT2  = RGBColor(0xC9, 0xD6, 0xEA)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
CREAM  = RGBColor(0xE5, 0xDE, 0xDB)   # lt2

FONT_H = "思源宋体 CN Heavy"    # 标题（衬线特粗）
FONT_B = "思源黑体 CN Bold"     # 小标题
FONT_O = "思源黑体 CN Normal"   # 正文

SW, SH = 13.3333, 7.5
X0, X1 = 0.62, 12.72            # 内容安全区（白底面板内）
_checks = []


# ---------------- 文本度量 ----------------
def _char_w(ch, size):
    o = ord(ch)
    if o < 0x2E80:
        if ch == ' ':
            return size * 0.30
        if ch in 'iljI.,:;|!\'`':
            return size * 0.28
        if ch in 'mwMW@%':
            return size * 0.85
        return size * 0.53
    return size * 1.0


def measure_lines(text, width_in, size):
    avail = max(10.0, width_in * 72.0)
    lines, cur = 1, 0.0
    for ch in text:
        w = _char_w(ch, size)
        if cur + w > avail:
            lines += 1
            cur = w
        else:
            cur += w
    return lines


def block_height(t, width_in, size, spacing):
    return measure_lines(t, width_in, size) * size * spacing / 72.0


# ---------------- 图元 ----------------
_EMPTY = etree.SubElement(etree.Element('d'), qn('a:effectLst'))


def _no_shadow(shp):
    spPr = shp._element.spPr
    if spPr.find(qn('a:effectLst')) is None:
        spPr.append(copy.deepcopy(_EMPTY))


def rect(slide, x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         radius=0.06, alpha=None):
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
        if alpha is not None:
            srgb = s.fill.fore_color._xFill.find(qn('a:srgbClr'))
            a = etree.SubElement(srgb, qn('a:alpha'))
            a.set('val', str(int(alpha * 100000)))
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    _no_shadow(s)
    s.text_frame.word_wrap = True
    s.text_frame.auto_size = MSO_AUTO_SIZE.NONE
    return s


def hline(slide, x, y, w, color=TINT2, lw=1.0):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x + w), Inches(y))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    return c


def vline(slide, x, y, h, color=TINT2, lw=1.0):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x), Inches(y + h))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    return c


def arrow(slide, x, y, w, h=0.16, color=TINT2, direction='right'):
    shp = {'right': MSO_SHAPE.RIGHT_ARROW, 'left': MSO_SHAPE.LEFT_ARROW,
           'down': MSO_SHAPE.DOWN_ARROW}[direction]
    s = slide.shapes.add_shape(shp, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background()
    _no_shadow(s)
    return s


def _set_run(r, size, color, bold, font, italic=False, spc=None):
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font
    rPr = r._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set('typeface', font)
    if spc:
        rPr.set('spc', str(int(spc)))


def text(slide, x, y, w, h, paras, size=12, color=INK, bold=False, align='l', anchor='t',
         spacing=1.4, space_before=0.0, font=FONT_O, wrap=True, slide_no=None, tag=''):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]

    if isinstance(paras, str):
        paras = [paras]
    plain = []
    for i, p in enumerate(paras):
        if isinstance(p, str):
            p = {'text': p}
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT,
                          'j': PP_ALIGN.JUSTIFY}[p.get('align', align)]
        para.line_spacing = p.get('spacing', spacing)
        sb = p.get('space_before', space_before if i else 0.0)
        if sb:
            para.space_before = Pt(sb)
        parts = p.get('parts') or [(p.get('text', ''), {})]
        for txt, ov in parts:
            run = para.add_run()
            run.text = txt
            _set_run(run, ov.get('size', p.get('size', size)),
                     ov.get('color', p.get('color', color)),
                     ov.get('bold', p.get('bold', bold)),
                     ov.get('font', p.get('font', font)),
                     ov.get('italic', False), ov.get('spc', p.get('spc')))
        plain.append(p.get('text') or ''.join(t for t, _ in parts))
    need = 0.0
    for i, p in enumerate(paras):
        if isinstance(p, str):
            p = {'text': p}
        need += block_height(plain[i], w, p.get('size', size), p.get('spacing', spacing))
    _checks.append((slide_no, f"text:{tag or (plain[0][:12] if plain else '')}",
                   round(need, 2), round(h, 2), x, y, w))
    return tb


def chip(slide, x, y, w, h, label, size=10, fill=PALE, color=BLUE, bold=False, line=TINT, radius=0.5):
    s = rect(slide, x, y, w, h, fill=fill, line=line, radius=radius)
    tf = s.text_frame
    tf.margin_left = Inches(0.03); tf.margin_right = Inches(0.03)
    tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    p.line_spacing = 1.1
    r = p.add_run(); r.text = label
    _set_run(r, size, color, bold, FONT_O)
    return s


def num_badge(slide, x, y, d, label, size=11, fill=BLUE, color=WHITE, bold=True, h=None):
    s = rect(slide, x, y, d, h or d, fill=fill, radius=0.18)
    tf = s.text_frame
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    _set_run(r, size, color, bold, FONT_B)
    return s


# ---------------- 版式 ----------------
def pageno(slide, no, total, light=False):
    text(slide, 11.92, 6.92, 0.80, 0.26,
         [{'text': f"{no:02d} / {total}", 'size': 9, 'color': TINT if light else GRAY2, 'align': 'r'}],
         spacing=1.0, tag='pageno')


def page_title(slide, title, no, total, note=None):
    rect(slide, X0, 0.55, 0.055, 0.34, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
    text(slide, X0 + 0.18, 0.44, 10.4, 0.56,
         [{'text': title, 'size': 25, 'bold': True, 'color': INK, 'font': FONT_H}],
         spacing=1.15, tag='title', slide_no=no)
    if note:
        text(slide, 10.7, 0.62, 2.02, 0.30,
             [{'text': note, 'size': 9.5, 'color': GRAY2, 'align': 'r'}], spacing=1.0, tag='title-note')
    hline(slide, X0, 1.08, X1 - X0, color=TINT, lw=1.0)
    pageno(slide, no, total)


def lead(slide, y, body, h=0.9, size=11.5, x=X0, w=X1 - X0, slide_no=None):
    rect(slide, x, y, w, h, fill=PALE, line=TINT, radius=0.05)
    rect(slide, x, y + 0.10, 0.05, h - 0.20, fill=BLUE, shape=MSO_SHAPE.RECTANGLE)
    text(slide, x + 0.22, y, w - 0.44, h, [{'text': body, 'size': size, 'color': GRAY, 'spacing': 1.5}],
         anchor='m', spacing=1.5, slide_no=slide_no, tag='lead')
    return y + h


def para_list(slide, x, y, w, h, items, size=9.5, color=GRAY, spacing=1.4, gap=9, dot='· '):
    paras = []
    for i, it in enumerate(items):
        paras.append({'text': dot + it, 'size': size, 'color': color, 'spacing': spacing,
                      'space_before': 0 if i == 0 else gap})
    return text(slide, x, y, w, h, paras, spacing=spacing, tag='plist')


def report():
    bad = [c for c in _checks if c[2] > c[3] + 0.03]
    print(f"\n=== 溢出检查：共 {len(_checks)} 处文本，超限 {len(bad)} 处 ===")
    for c in sorted(bad, key=lambda x: -(x[2] - x[3]))[:40]:
        print(f"  slide {c[0]} {c[1]:30s} need={c[2]} box={c[3]} @({c[4]},{c[5]}) w={c[6]}")
    return bad
