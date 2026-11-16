# -*- coding: utf-8 -*-
"""将 PPTX 近似渲染为 PNG，用于版式自检（无 LibreOffice 环境下的替代方案）。
支持：图片、纯色/渐变填充、线条、自动图形、组合变换、主题色、段落折行。"""
import os, sys, io
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.oxml.ns import qn

EMU_IN = 914400.0
FONT_PATH = '/tmp/font/scp_zh-master/fonts/SimHei.ttf'
SCALE = 160
_cache = {}
SCHEME = {}


def font(size_pt, bold=False):
    key = (int(size_pt * 2), bold)
    if key not in _cache:
        px = max(6, int(round(size_pt * SCALE / 72.0)))
        _cache[key] = ImageFont.truetype(FONT_PATH, px)
    return _cache[key]


def E(v):
    return 0 if v is None else v / EMU_IN * SCALE


def load_scheme(prs):
    global SCHEME
    SCHEME = {}
    try:
        theme = prs.slide_masters[0].part.part_related_by(
            'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme')
        from lxml import etree
        root = etree.fromstring(theme.blob)
        cs = root.find('.//' + qn('a:clrScheme'))
        for child in cs:
            tag = child.tag.split('}')[1]
            c = child[0]
            val = c.get('lastClr') or c.get('val')
            if val:
                SCHEME[tag] = val
        SCHEME['bg1'] = SCHEME.get('lt1', 'FFFFFF')
        SCHEME['tx1'] = SCHEME.get('dk1', '000000')
        SCHEME['bg2'] = SCHEME.get('lt2', 'FFFFFF')
        SCHEME['tx2'] = SCHEME.get('dk2', '000000')
    except Exception as e:
        pass


def _color_of_el(el):
    if el is None:
        return None
    tag = el.tag.split('}')[1]
    if tag == 'srgbClr':
        hexv = el.get('val')
    elif tag == 'schemeClr':
        hexv = SCHEME.get(el.get('val'))
    elif tag == 'prstClr':
        hexv = {'black': '000000', 'white': 'FFFFFF'}.get(el.get('val'))
    else:
        return None
    if not hexv:
        return None
    if len(hexv) != 6:
        from PIL import ImageColor
        try:
            return ImageColor.getrgb(hexv)[:3]
        except Exception:
            return None
    try:
        r, g, b = (int(hexv[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        from PIL import ImageColor
        try:
            r, g, b = ImageColor.getrgb(hexv)[:3]
        except Exception:
            return None
    # 处理亮度调整
    for mod in el:
        m = mod.tag.split('}')[1]
        v = int(mod.get('val', '0')) / 100000.0
        if v > 1:
            v = v
        if m == 'lumMod':
            r, g, b = r * v, g * v, b * v
        elif m == 'lumOff':
            r, g, b = r + (255 - r) * v, g + (255 - g) * v, b + (255 - b) * v
        elif m == 'alpha':
            pass
    return tuple(max(0, min(255, int(x))) for x in (r, g, b))


def fill_color(sh):
    spPr = sh._element.find(qn('p:spPr'))
    if spPr is None:
        return None
    solid = spPr.find(qn('a:solidFill'))
    if solid is not None:
        for c in solid:
            col = _color_of_el(c)
            if col:
                return col
    grad = spPr.find(qn('a:gradFill'))
    if grad is not None:
        gs = grad.find(qn('a:gsLst'))
        if gs is not None:
            for g in gs:
                for c in g:
                    col = _color_of_el(c)
                    if col:
                        return col
    return None


def line_props(sh):
    spPr = sh._element.find(qn('p:spPr'))
    if spPr is None:
        return None, 0
    ln = spPr.find(qn('a:ln'))
    if ln is None:
        return None, 0
    if ln.find(qn('a:noFill')) is not None:
        return None, 0
    solid = ln.find(qn('a:solidFill'))
    w = int(ln.get('w', '12700'))
    if solid is not None:
        for c in solid:
            col = _color_of_el(c)
            if col:
                return col, max(1, int(w / EMU_IN * SCALE))
    return None, 0


def run_color(run):
    rPr = run._r.find(qn('a:rPr'))
    if rPr is not None:
        solid = rPr.find(qn('a:solidFill'))
        if solid is not None:
            for c in solid:
                col = _color_of_el(c)
                if col:
                    return col
    return (0x39, 0x30, 0x2A)


def render_text(dr, sh, ox, oy, sx, sy):
    tf = sh.text_frame
    x = ox + E(sh.left) * sx
    y = oy + E(sh.top) * sy
    w = E(sh.width) * sx
    h = E(sh.height) * sy
    ml = E(tf.margin_left or 0); mr = E(tf.margin_right or 0)
    mt = E(tf.margin_top or 0); mb = E(tf.margin_bottom or 0)
    avail = max(10, w - ml - mr)
    blocks = []
    for para in tf.paragraphs:
        if not para.runs:
            continue
        sz = max((r.font.size.pt if r.font.size else 18) for r in para.runs)
        spacing = para.line_spacing if isinstance(para.line_spacing, float) else 1.25
        sb = (para.space_before.pt if para.space_before else 0) * SCALE / 72.0
        al = para.alignment
        segs = []
        cur_w = 0
        lines = [[]]
        for run in para.runs:
            rs = run.font.size.pt if run.font.size else 18
            f = font(rs, bool(run.font.bold))
            col = run_color(run)
            for ch in run.text:
                if ch == '\n':
                    lines.append([])
                    cur_w = 0
                    continue
                cw = dr.textlength(ch, font=f)
                if cur_w + cw > avail and lines[-1]:
                    lines.append([])
                    cur_w = 0
                lines[-1].append((ch, f, col, cw))
                cur_w += cw
        lh = sz * spacing * SCALE / 72.0
        blocks.append((lines, lh, sb, al))
    total = sum(len(b[0]) * b[1] + b[2] for b in blocks)
    anchor = tf.vertical_anchor
    cy = y + mt
    if anchor == 3:
        cy = y + (h - total) / 2
    elif anchor == 4:
        cy = y + h - mb - total
    for lines, lh, sb, al in blocks:
        cy += sb
        for segs in lines:
            lw = sum(s[3] for s in segs)
            if al == 2:
                cx = x + ml + (avail - lw) / 2
            elif al == 3:
                cx = x + ml + avail - lw
            else:
                cx = x + ml
            for ch, f, col, cw in segs:
                dr.text((cx, cy + (lh - f.size) / 2 - lh * 0.05), ch, font=f, fill=col)
                cx += cw
            cy += lh


def render_shape(dr, sh, img, ox=0, oy=0, sx=1.0, sy=1.0):
    st = sh.shape_type
    if st == MSO_SHAPE_TYPE.PICTURE:
        try:
            pic = Image.open(io.BytesIO(sh.image.blob)).convert('RGB')
            x = ox + E(sh.left) * sx; y = oy + E(sh.top) * sy
            w = max(1, int(E(sh.width) * sx)); h = max(1, int(E(sh.height) * sy))
            img.paste(pic.resize((w, h), Image.LANCZOS), (int(x), int(y)))
        except Exception:
            pass
        return
    if st == MSO_SHAPE_TYPE.GROUP:
        try:
            grp = sh._element.find(qn('p:grpSpPr')).find(qn('a:xfrm'))
            off = grp.find(qn('a:off')); ext = grp.find(qn('a:ext'))
            chOff = grp.find(qn('a:chOff')); chExt = grp.find(qn('a:chExt'))
            gx = ox + E(sh.left) * sx; gy = oy + E(sh.top) * sy
            gw = E(sh.width) * sx; gh = E(sh.height) * sy

            def px(v):  # child EMU -> px in parent space
                return gx + (v - int(chOff.get('x'))) * gw / int(chExt.get('cx'))

            def py(v):
                return gy + (v - int(chOff.get('y'))) * gh / int(chExt.get('cy'))

            nsx = gw / (int(chExt.get('cx')) / EMU_IN * SCALE) if chExt.get('cx') else 1
            nsy = gh / (int(chExt.get('cy')) / EMU_IN * SCALE) if chExt.get('cy') else 1
            # 用绝对偏移 + 缩放实现：先记录子元素原始 EMU 与父空间映射
            for child in sh.shapes:
                save = (child.left, child.top, child.width, child.height)
                try:
                    child.left = int(round((px(int(save[0])) / sx) * EMU_IN / SCALE))
                    child.top = int(round((py(int(save[1])) / sy) * EMU_IN / SCALE))
                    child.width = int(round((E(save[2]) * nsx) / sx * EMU_IN / SCALE))
                    child.height = int(round((E(save[3]) * nsy) / sy * EMU_IN / SCALE))
                    if child.shape_type == MSO_SHAPE_TYPE.GROUP:
                        render_shape(dr, child, img, ox, oy, sx, sy)
                    else:
                        render_shape(dr, child, img, ox, oy, sx, sy)
                        if child.has_text_frame and child.text_frame.text.strip():
                            render_text(dr, child, 0, 0, 1.0, 1.0)
                finally:
                    child.left, child.top, child.width, child.height = save
        except Exception:
            pass
        return
    if st == MSO_SHAPE_TYPE.LINE:
        col, lw = line_props(sh)
        if col:
            x = ox + E(sh.left) * sx; y = oy + E(sh.top) * sy
            dr.line([(x, y), (x + E(sh.width) * sx, y + E(sh.height) * sy)], fill=col, width=max(1, lw))
        return
    fill = fill_color(sh)
    lc, lw = line_props(sh)
    if not fill and not lw:
        return
    x = ox + E(sh.left) * sx; y = oy + E(sh.top) * sy
    w = E(sh.width) * sx; h = E(sh.height) * sy
    try:
        kind = sh.auto_shape_type
    except Exception:
        kind = None
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        adj = 0.08
        try:
            adj = sh.adjustments[0]
        except Exception:
            pass
        r = max(0, int(min(w, h) * adj)) if adj else 0
        dr.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=lc, width=lw or 1)
    elif kind == MSO_SHAPE.OVAL:
        dr.ellipse([x, y, x + w, y + h], fill=fill, outline=lc, width=lw or 1)
    elif kind == MSO_SHAPE.DOWN_ARROW:
        cx = x + w / 2
        dr.polygon([(x, y), (x + w, y), (x + w, y + h * 0.55), (x + w * 0.75, y + h * 0.55),
                    (cx, y + h), (x + w * 0.25, y + h * 0.55), (x, y + h * 0.55)], fill=fill)
    elif kind == MSO_SHAPE.RIGHT_ARROW:
        dr.polygon([(x, y + h * 0.28), (x + w * 0.55, y + h * 0.28), (x + w * 0.55, y),
                    (x + w, y + h / 2), (x + w * 0.55, y + h), (x + w * 0.55, y + h * 0.72),
                    (x, y + h * 0.72)], fill=fill)
    elif kind == MSO_SHAPE.LEFT_ARROW:
        dr.polygon([(x + w, y + h * 0.28), (x + w * 0.45, y + h * 0.28), (x + w * 0.45, y),
                    (x, y + h / 2), (x + w * 0.45, y + h), (x + w * 0.45, y + h * 0.72),
                    (x + w, y + h * 0.72)], fill=fill)
    else:
        dr.rectangle([x, y, x + w, y + h], fill=fill, outline=lc, width=lw or 1)


def render(path, outdir, only=None):
    prs = Presentation(path)
    load_scheme(prs)
    W = int(prs.slide_width / EMU_IN * SCALE)
    H = int(prs.slide_height / EMU_IN * SCALE)
    os.makedirs(outdir, exist_ok=True)
    files = []
    for i, slide in enumerate(prs.slides, 1):
        if only and i not in only:
            continue
        img = Image.new('RGB', (W, H), 'white')
        dr = ImageDraw.Draw(img)
        try:
            c = None
            bg = slide.background
            if bg.fill.type == 1:
                c = bg.fill.fore_color.rgb
                img = Image.new('RGB', (W, H), tuple(int(str(c)[i:i+2], 16) for i in (0, 2, 4)))
                dr = ImageDraw.Draw(img)
        except Exception:
            pass
        for sh in slide.slide_layout.shapes:
            render_shape(dr, sh, img)
        for sh in slide.shapes:
            render_shape(dr, sh, img)
        dr = ImageDraw.Draw(img)
        for sh in slide.shapes:
            if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                for s2 in sh.shapes:
                    if s2.has_text_frame and s2.text_frame.text.strip():
                        # 组内文字位置已由 render_shape 恢复，粗略回退到原坐标
                        pass
            if sh.has_text_frame and sh.text_frame.text.strip():
                render_text(dr, sh, 0, 0, 1.0, 1.0)
        f = os.path.join(outdir, f's{i:02d}.png')
        img.save(f)
        files.append(f)
    return files


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/123/源代码审计智能体-技术与成果汇报.pptx'
    only = set(int(a) for a in sys.argv[2:]) or None
    print('\n'.join(render(path, '/tmp/preview', only)))
