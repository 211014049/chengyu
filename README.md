# 成语吧 - 中文成语词典

收录 570+ 常用成语的静态词典网站，中国风设计，纯 HTML/CSS/JS，无需后端。

## 本地构建

```bash
python build.py
```

生成的网站文件输出到 `docs/` 目录。

## 部署（GitHub Pages）

1. 推送到 GitHub 仓库
2. 仓库 Settings → Pages → Source 选 **Deploy from a branch**
3. Branch 选 `main`，文件夹选 **/docs**，保存
4. 访问 https://211014049.github.io/chengyu/

## 目录结构

- `build.py` — 静态站点生成器
- `data/*.json` — 成语数据（名称/拼音/释义/出处/例句/近反义词/分类）
- `static/` — 样式与脚本（构建时复制到 docs/static/）
- `docs/` — 生成的静态网站（GitHub Pages 发布目录）
