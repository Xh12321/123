# PPT 生成脚本

- `build_deck.py`：基于模板母版（国网绿底 `default.pptx`，其母版/版式来自仓库内 `源代码审计智能体产品介绍1.pptx`）生成
  `源代码审计智能体-技术与成果汇报.pptx`（26 页，含逐页讲稿备注）。
- `deck_lib.py`：设计 token（主色 `006F6B`、浅底 `F4FAFA`）、图元与文本溢出估算工具。
- `render.py`：无 LibreOffice 环境下的近似渲染器（把 PPTX 画成 PNG，用于版式自检）。

重新生成：

```bash
python3 build/build_deck.py     # 生成 PPTX，并输出文本溢出检查报告
python3 build/render.py 源代码审计智能体-技术与成果汇报.pptx   # 输出 PNG 预览到 /tmp/preview
```

> 说明：官方模板为 GitHub Release 附件（release-assets.githubusercontent.com），当前环境无法访问该域名，
> 因此直接复用参考 PPT 中的同款模板母版（绿色背景 + 国家电网 logo + 标题版式），保证配色、版式与原模板一致。
