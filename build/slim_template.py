# -*- coding: utf-8 -*-
"""把模板里的超大清空图（PNG 各 ~12MB）转成高质量 JPEG，生成“轻量模板”。

仅替换 ppt/media/image*.png 的存储格式（内容近似无损，视觉一致），
并同步修改 rels 目标与 [Content_Types].xml，模板版式/母版结构完全不变。
"""
import io, os, re, shutil, zipfile
from PIL import Image

MAXW = 2000
QUALITY = 90


def _to_jpeg(data):
    im = Image.open(io.BytesIO(data)).convert('RGB')
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, 'JPEG', quality=QUALITY, subsampling=0, optimize=True, progressive=True)
    return out.getvalue()


def build(src, dst):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    # 清空旧缓存图片，保证每次都是同一份轻量模板
    tmp = dst + '.tmp'
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        names = zin.namelist()
        big = {}
        for n in names:
            data = zin.read(n)
            if re.match(r'ppt/media/.+\.png$', n) and len(data) > 1_500_000:
                big[n] = n.rsplit('.', 1)[0] + '.jpg'
        for n in names:
            data = zin.read(n)
            if n in big:
                zout.writestr(big[n], _to_jpeg(data), zipfile.ZIP_STORED)
                continue
            if n == '[Content_Types].xml':
                txt = data.decode('utf-8')
                if 'Extension="jpg"' not in txt:
                    txt = txt.replace('<Types ', '<Types ', 1)
                    txt = re.sub(r'(<Types[^>]*>)',
                                 r'\1<Default Extension="jpg" ContentType="image/jpeg"/>', txt, count=1)
                data = txt.encode('utf-8')
            elif n.startswith('ppt/') and n.endswith('.rels'):
                txt = data.decode('utf-8')
                for old, new in big.items():
                    txt = txt.replace(old, new).replace(old.split('/')[-1], new.split('/')[-1])
                data = txt.encode('utf-8')
            zout.writestr(n, data)
    shutil.move(tmp, dst)
    return dst


if __name__ == '__main__':
    out = build('/home/user/123/模板.pptx', '/tmp/tpl_light.pptx')
    print(out, round(os.path.getsize(out) / 1e6, 2), 'MB')
