# -*- coding: utf-8 -*-
"""将生成的 PPTX 近似渲染为 PNG，用于版式自检（无 LibreOffice 环境下的替代方案）。"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Emu
from pptx.enum.shapes import MSO_SHAPE_TYPE

EMU_IN = 914400.0
FONT_PATH = '/tmp/font/scp_zh-master/fonts/SimHei.ttf'
SCALE = 160          # px per inch

_cache = {}


def font(size_pt, bold=False):
    key = (size_pt, bold)
    if key not in _cache:
        px = max(6, int(round(size_pt * SCALE / 72.0)))
        _cache[key] = ImageFont.truetype(FONT_PATH, px)
    return _cache[key]


def E(v):
    return 0 if v is None else v / EMU_IN * SCALE


def color_of(fmt, default=None):
    try:
        if fmt.type is None:
            return default
        if fmt.type == 1:  # solid
            rgb = fmt.fore_color
            if rgb.type == 1:
                c = str(rgb.rgb)
                return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        pass
    return default


def shape_fill(sh):
    try:
        f = sh.fill
        if f.type == 1:
            return color_of(f)
    except Exception:
        pass
    return None


def shape_line(sh):
    try:
        ln = sh.line
        if ln.fill.type == 1:
            c = color_of(ln.fill)
            w = ln.width.pt if ln.width else 1
            return c, max(1, int(w * SCALE / 72))
    except Exception:
        pass
    return None, 0


def draw_shape(dr, sh, img):
    st = sh.shape_type
    x, y = E(sh.left), E(sh.top)
    w, h = E(sh.width), E(sh.height)
    if st == MSO_SHAPE_TYPE.PICTURE:
        try:
            blob = sh.image.blob
            import io
            pic = Image.open(io.BytesIO(blob)).convert('RGB')
            pic = pic.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
            img.paste(pic, (int(x), int(y)))
        except Exception as e:
            pass
        return
    if st == MSO_SHAPE_TYPE.LINE:
        c, lw = shape_line(sh)
        if c:
            dr.line([(x, y), (x + w, y + h)], fill=c, width=max(1, lw))
        return
    # 自动图形
    fill = shape_fill(sh)
    lc, lw = shape_line(sh)
    try:
        name = sh.auto_shape_type
    except Exception:
        name = None
    from pptx.enum.shapes import MSO_SHAPE
    if fill or lw:
        if name in (MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.DOWN_ARROW, MSO_SHAPE.RIGHT_ARROW):
            adj = 0.08
            try:
                adj = sh.adjustments[0]
            except Exception:
                pass
            if name == MSO_SHAPE.ROUNDED_RECTANGLE:
                r = max(0, int(min(w, h) * adj))
                dr.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill,
                                     outline=lc, width=lw)
            elif name == MSO_SHAPE.DOWN_ARROW:
                cx = x + w / 2
                pts = [(x, y), (x + w, y), (x + w, y + h * 0.55), (x + w * 0.75, y + h * 0.55),
                       (cx, y + h), (x + w * 0.25, y + h * 0.55), (x, y + h * 0.55)]
                dr.polygon(pts, fill=fill)
            else:
                pts = [(x, y + h * 0.28), (x + w * 0.55, y + h * 0.28), (x + w * 0.55, y),
                       (x + w, y + h / 2), (x + w * 0.55, y + h), (x + w * 0.55, y + h * 0.72),
                       (x, y + h * 0.72)]
                dr.polygon(pts, fill=fill)
        else:
            dr.rectangle([x, y, x + w, y + h], fill=fill, outline=lc, width=lw)


def wrap_runs(para, maxw, draw):
    """返回 [(segment_text, font, color)] 分行结果（按字符粒度折行）。"""
    out, line = [], []
    cur_w = 0
    for run in para.runs:
        sz = run.font.size.pt if run.font.size else 18
        col = '000000'
        try:
            if run.font.color and run.font.color.type == 1:
                col = str(run.font.color.rgb)
        except Exception:
            pass
        c = tuple(int(col[i:i+2], 16) for i in (0, 2, 4))
        f = font(sz, bool(run.font.bold))
        for ch in run.text:
            if ch == '\n':
                out.append(line); line = []; cur_w = 0; continue
            cw = draw.textlength(ch, font=f)
            if maxw and cur_w + cw > maxw and line:
                out.append(line); line = []; cur_w = 0
            line.append((ch, f, c, cw))
            cur_w += cw
    out.append(line)
    return out


def draw_text(dr, sh, img):
    tf = sh.text_frame
    x, y = E(sh.left), E(sh.top)
    w, h = E(sh.width), E(sh.height)
    ml = E(tf.margin_left or 0); mr = E(tf.margin_right or 0)
    mt = E(tf.margin_top or 0); mb = E(tf.margin_bottom or 0)
    avail = max(10, w - ml - mr)
    blocks = []
    for para in tf.paragraphs:
        if not para.runs:
            continue
        sz = max(r.font.size.pt if r.font.size else 18 for r in para.runs)
        spacing = para.line_spacing if isinstance(para.line_spacing, float) else 1.2
        sb = para.space_before.pt if para.space_before else 0
        lines = wrap_runs(para, avail, dr)
        lh = sz * spacing * SCALE / 72.0
        al = para.alignment
        blocks.append((lines, lh, sb * SCALE / 72.0, al, sz))
    total = sum(len(b[0]) * b[1] + b[2] for b in blocks)
    anchor = tf.vertical_anchor
    cy = y + mt
    if anchor == 3:      # middle
        cy = y + (h - total) / 2
    elif anchor == 4:    # bottom
        cy = y + h - mb - total
    for lines, lh, sb, al, sz in blocks:
        cy += sb
        for segs in lines:
            lw = sum(s[3] for s in segs)
            if al == 2:      # center
                cx = x + ml + (avail - lw) / 2
            elif al == 3:    # right
                cx = x + ml + avail - lw
            else:
                cx = x + ml
            for ch, f, c, cw in segs:
                dr.text((cx, cy + (lh - f.size) / 2 - lh * 0.04), ch, font=f, fill=c)
                cx += cw
            cy += lh


def render(path, outdir, only=None):
    prs = Presentation(path)
    W = int(prs.slide_width / EMU_IN * SCALE)
    H = int(prs.slide_height / EMU_IN * SCALE)
    os.makedirs(outdir, exist_ok=True)
    files = []
    for i, slide in enumerate(prs.slides, 1):
        if only and i not in only:
            continue
        img = Image.new('RGB', (W, H), 'white')
        # 背景
        try:
            bg = slide.background
            c = color_of(bg.fill)
            if c:
                img = Image.new('RGB', (W, H), c)
        except Exception:
            pass
        dr = ImageDraw.Draw(img)
        for sh in slide.slide_layout.slide_master.shapes:
            draw_shape(dr, sh, img)
        for sh in slide.slide_layout.shapes:
            draw_shape(dr, sh, img)
        for sh in slide.shapes:
            draw_shape(dr, sh, img)
        dr = ImageDraw.Draw(img)
        for sh in slide.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                draw_text(dr, sh, img)
        f = os.path.join(outdir, f's{i:02d}.png')
        img.save(f)
        files.append(f)
    return files


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/123/源代码审计智能体-四维度汇报.pptx'
    only = set(int(a) for a in sys.argv[2:]) or None
    fs = render(path, '/tmp/preview', only)
    print('\n'.join(fs))
