# -*- coding: utf-8 -*-
"""
成语词典站构建脚本
运行: python build.py
读取 data/*.json 成语数据，生成 docs/ 下全部静态页面。
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
DATA_DIR = os.path.join(ROOT, "data")

SITE_NAME = "成语吧"
SITE_URL = "https://211014049.github.io/chengyu"

# ---------------------------------------------------------------------------
# 拼音处理：声调标记 → 无调（用于 URL slug）
# ---------------------------------------------------------------------------
TONE_MAP = {
    "ā": "a", "á": "a", "ǎ": "a", "à": "a",
    "ē": "e", "é": "e", "ě": "e", "è": "e",
    "ī": "i", "í": "i", "ǐ": "i", "ì": "i",
    "ō": "o", "ó": "o", "ǒ": "o", "ò": "o",
    "ū": "u", "ú": "u", "ǔ": "u", "ù": "u",
    "ǖ": "u", "ǘ": "u", "ǚ": "u", "ǜ": "u", "ü": "u",
}


def slugify(pinyin):
    s = "".join(TONE_MAP.get(c, c) for c in pinyin)
    return s.replace(" ", "").lower()


# ---------------------------------------------------------------------------
# 主题分类（20 个）
# ---------------------------------------------------------------------------
THEMES = [
    {"slug": "shuzi", "name": "数字成语", "desc": "以一至万等数字开头的成语"},
    {"slug": "dongwu", "name": "动物成语", "desc": "与龙虎马牛等动物相关的成语"},
    {"slug": "ziran", "name": "自然成语", "desc": "与风雨雷电、山水云月相关的成语"},
    {"slug": "renwu", "name": "人物成语", "desc": "描写英雄豪杰、名人典故的成语"},
    {"slug": "pinde", "name": "品德成语", "desc": "关于诚信、善良、勇敢等品格的成语"},
    {"slug": "xuexi", "name": "学习成语", "desc": "关于勤奋、刻苦、读书求知的成语"},
    {"slug": "zhanzheng", "name": "战争成语", "desc": "关于兵法、谋略、胜败的成语"},
    {"slug": "qinggan", "name": "情感成语", "desc": "描写喜怒哀乐、悲欢离合的成语"},
    {"slug": "zheli", "name": "哲理成语", "desc": "蕴含人生道理、辩证思维的成语"},
    {"slug": "miaoxie", "name": "描写成语", "desc": "描写外貌、神态、动作、环境的成语"},
    {"slug": "lishidiangu", "name": "历史典故成语", "desc": "源于真实历史事件与人物的成语"},
    {"slug": "shenhuayuyan", "name": "神话寓言成语", "desc": "源于神话传说与寓言故事的成语"},
    {"slug": "youqing", "name": "友情成语", "desc": "关于友谊、知音、交情的成语"},
    {"slug": "aiqing", "name": "爱情成语", "desc": "关于爱情、婚姻、相思的成语"},
    {"slug": "jiating", "name": "家庭成语", "desc": "关于家庭、亲情、和睦的成语"},
    {"slug": "gongzuo", "name": "工作成语", "desc": "关于职场、做事、事业的成语"},
    {"slug": "shijian", "name": "时间成语", "desc": "关于时光、岁月、早晚的成语"},
    {"slug": "fangwei", "name": "方位成语", "desc": "含有东南西北等方位词的成语"},
    {"slug": "yanse", "name": "颜色成语", "desc": "含有红白青黑等颜色词的成语"},
    {"slug": "shiwu", "name": "食物成语", "desc": "与饮食、食物相关的成语"},
]
THEME_BY_NAME = {t["name"]: t for t in THEMES}
THEME_BY_SLUG = {t["slug"]: t for t in THEMES}

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["other"]
LETTER_NAME = {"other": "非字母开头"}

FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
           "<text y='.9em' font-size='90'>📖</text></svg>")

AD_TOP = '''<!-- AD SLOT: top -->
<!-- Google AdSense：内容顶部 Banner（发布时替换为 AdSense 代码） -->
<div class="ad-slot ad-banner" data-ad="top"><span>广告位 · 顶部</span></div>'''

AD_BOTTOM = '''<!-- AD SLOT: bottom -->
<!-- Google AdSense：内容底部 Banner（发布时替换为 AdSense 代码） -->
<div class="ad-slot ad-banner" data-ad="bottom"><span>广告位 · 底部</span></div>'''

# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------


def load_idioms():
    items, seen = [], set()
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for it in data:
            name = it["name"].strip()
            if name in seen:
                continue
            seen.add(name)
            it["slug"] = slugify(it["pinyin"])
            it["letter"] = it["slug"][0].upper() if it["slug"] else "?"
            if it["letter"] not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                it["letter"] = "other"
            items.append(it)
    return items


# ---------------------------------------------------------------------------
# 页面骨架
# ---------------------------------------------------------------------------

def header(root, active=""):
    nav = f'<a href="{root}index.html"{" class=active" if active=="home" else ""}>首页</a>'
    nav += f'<a href="{root}category/letter-a.html">按字母</a>'
    for t in THEMES[:8]:
        cls = ' class="active"' if active == t["slug"] else ""
        nav += f'<a href="{root}category/{t["slug"]}.html"{cls}>{t["name"][:2]}</a>'
    return f'''<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="{root}index.html"><span class="logo-mark">语</span>{SITE_NAME}</a>
    <nav class="main-nav">{nav}</nav>
    <div class="header-right">
      <div class="search-box">
        <input type="search" id="globalSearch" placeholder="搜索成语，如：画蛇添足" autocomplete="off">
        <div class="search-results" id="searchResults"></div>
      </div>
      <button id="themeToggle" class="theme-toggle" aria-label="切换暗色模式">🌙</button>
    </div>
  </div>
</header>'''


def footer(root):
    themes = "".join(f'<a href="{root}category/{t["slug"]}.html">{t["name"]}</a>' for t in THEMES[:10])
    more = "".join(f'<a href="{root}category/{t["slug"]}.html">{t["name"]}</a>' for t in THEMES[10:])
    return f'''<footer class="site-footer">
  <div class="container footer-grid">
    <div><h4>主题分类</h4>{themes}</div>
    <div><h4>更多分类</h4>{more}</div>
    <div><h4>快速入口</h4>
      <a href="{root}search.html">成语搜索</a>
      <a href="{root}category/letter-a.html">按字母查询</a>
      <a href="{root}sitemap.xml">站点地图</a></div>
    <div><h4>关于本站</h4>
      <a href="{root}about.html">关于我们</a>
      <a href="{root}privacy-policy.html">隐私政策</a>
      <a href="{root}contact.html">联系我们</a></div>
  </div>
  <div class="footer-bottom container">
    <p>© <span id="year"></span> {SITE_NAME} · 传承中华语言文化，共收录常用成语数据，仅供学习参考</p>
  </div>
</footer>'''


def page(title, desc, path, content, root, jsonld_extra=None, keywords=""):
    full_title = title if title.endswith(SITE_NAME) else f"{title} | {SITE_NAME}"
    jsonld = [{"@context": "https://schema.org", "@type": "WebSite",
               "name": SITE_NAME, "url": SITE_URL + "/",
               "potentialAction": {"@type": "SearchAction",
                                   "target": SITE_URL + "/search.html?q={search_term_string}",
                                   "query-input": "required name=search_term_string"}}]
    if jsonld_extra:
        jsonld.extend(jsonld_extra)
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
                   for x in jsonld)
    kw = f'<meta name="keywords" content="{keywords}">' if keywords else ""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<meta name="google-site-verification" content="VKlDaiEpSwFJMstdGA2OyU6zg6as5YLcQUNNLompxkk" />
{kw}
<link rel="canonical" href="{SITE_URL}/{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE_URL}/{path}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{FAVICON}">
{ld}
<link rel="stylesheet" href="{root}static/style.css">
</head>
<body data-root="{root}">
{header(root)}
<main>{content}</main>
{footer(root)}
<script src="{root}static/app.js"></script>
</body>
</html>'''


def breadcrumb(items, root):
    parts = []
    for name, href in items:
        parts.append(f'<a href="{href}">{name}</a>' if href else f'<span aria-current="page">{name}</span>')
    return f'<nav class="breadcrumb container" aria-label="面包屑">{" <span class=sep>›</span> ".join(parts)}</nav>'


def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n,
                 **({"item": SITE_URL + "/" + h} if h else {})}
                for i, (n, h) in enumerate(items)]}


# ---------------------------------------------------------------------------
# 卡片与链接辅助
# ---------------------------------------------------------------------------

def idiom_card(it, root):
    return f'''<a class="card idiom-card" href="{root}idiom/{it["slug"]}.html">
  <h3>{it["name"]}</h3>
  <p class="py">{it["pinyin"]}</p>
  <p class="meaning">{it["meaning"][:46]}…</p>
</a>'''


def term_link(word, by_name, root):
    """近义词/反义词：数据集中存在则链接，否则纯文本。"""
    if word in by_name:
        return f'<a class="term" href="{root}idiom/{by_name[word]["slug"]}.html">{word}</a>'
    return f'<span class="term term-plain">{word}</span>'


# ---------------------------------------------------------------------------
# 首页
# ---------------------------------------------------------------------------

def gen_index(idioms, by_name):
    hot_names = ["画蛇添足", "一鸣惊人", "三顾茅庐", "完璧归赵", "守株待兔", "画龙点睛",
                 "卧薪尝胆", "破釜沉舟", "草船借箭", "愚公移山", "刻舟求剑", "掩耳盗铃",
                 "杯弓蛇影", "狐假虎威", "塞翁失马", "精卫填海", "胸有成竹", "望梅止渴",
                 "亡羊补牢", "凿壁偷光"]
    hot = [by_name[n] for n in hot_names if n in by_name]
    hot_cards = "".join(idiom_card(i, "") for i in hot)
    theme_cards = "".join(
        f'''<a class="card theme-card" href="category/{t["slug"]}.html">
  <h3>{t["name"]}</h3><p class="cat-count">{sum(1 for i in idioms if i["category"] == t["name"])} 个成语</p></a>'''
        for t in THEMES)
    letters = "".join(
        f'<a class="letter-chip" href="category/letter-{l.lower()}.html">{l}</a>'
        for l in LETTERS if l != "other")
    content = f'''
<section class="hero">
  <div class="container">
    <h1><span class="accent">成语</span>大全</h1>
    <p class="hero-sub">收录 {len(idioms)}+ 常用中文成语，附拼音、释义、出处典故、例句造句、近义词反义词与成语接龙。</p>
    <div class="search-box hero-search">
      <input type="search" id="globalSearch" placeholder="输入成语或释义关键词，如：画蛇添足" autocomplete="off">
      <div class="search-results" id="searchResults"></div>
    </div>
    <div class="hero-stats">
      <div class="stat"><strong>{len(idioms)}+</strong><span>已收录成语</span></div>
      <div class="stat"><strong>{len(THEMES)}</strong><span>主题分类</span></div>
      <div class="stat"><strong>26</strong><span>字母索引</span></div>
      <div class="stat"><strong>免费</strong><span>在线查询</span></div>
    </div>
  </div>
</section>

<section class="container section">
  <h2 class="section-title">热门成语</h2>
  <div class="grid grid-idioms">{hot_cards}</div>
</section>

<section class="container section">
  <h2 class="section-title">按首字母查询</h2>
  <div class="letter-row">{letters}</div>
</section>

<section class="container section">
  <h2 class="section-title">按主题分类</h2>
  <div class="grid grid-themes">{theme_cards}</div>
</section>'''
    desc = f"{SITE_NAME}成语大全收录 {len(idioms)}+ 常用中文成语，提供拼音、释义、出处典故、例句造句、近义词、反义词与成语接龙，支持按字母和主题查询，免费在线成语词典。"
    title = f"成语大全 - {len(idioms)}+ 中文成语词典在线查询"
    return page(title, desc, "", content, root="",
                keywords="成语大全,成语词典,成语查询,成语解释,成语接龙")


# ---------------------------------------------------------------------------
# 成语详情页
# ---------------------------------------------------------------------------

def gen_idiom(it, idioms, by_name, by_letter):
    root = "../"
    cat = THEME_BY_NAME[it["category"]]
    syns = "".join(term_link(w, by_name, root) for w in it.get("synonyms", [])) or '<span class="muted">暂无收录</span>'
    ants = "".join(term_link(w, by_name, root) for w in it.get("antonyms", [])) or '<span class="muted">暂无收录</span>'
    examples = "".join(f"<li>{e}</li>" for e in it["examples"])

    # 成语接龙：最后一个字开头的成语
    last_char = it["name"].strip()[-1]
    jielong = [x for x in idioms if x["name"] != it["name"] and x["name"].startswith(last_char)][:6]
    jielong_html = ("".join(idiom_card(x, root) for x in jielong)
                    or '<p class="muted">暂无以「' + last_char + '」开头的收录成语</p>')

    related = [x for x in idioms if x["category"] == it["category"] and x["name"] != it["name"]][:5]
    related_html = "".join(idiom_card(x, root) for x in related)

    desc = f"{it['name']}，拼音{it['pinyin']}。{it['meaning'][:50]}。包含{it['name']}的出处、例句、近义词、反义词。"
    title = f"{it['name']}是什么意思 - {it['name']}的解释、出处、造句、近义词"

    crumbs = [(SITE_NAME, "../index.html"),
              (cat["name"], f"../category/{cat['slug']}.html"),
              (it["name"], None)]
    jsonld = [
        breadcrumb_ld([(SITE_NAME, ""), (cat["name"], f"category/{cat['slug']}.html"),
                       (it["name"], f"idiom/{it['slug']}.html")]),
        {"@context": "https://schema.org", "@type": "DefinedTerm",
         "name": it["name"], "alternateName": it["pinyin"],
         "description": it["meaning"],
         "inDefinedTermSet": SITE_URL + "/"},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [
             {"@type": "Question", "name": f"{it['name']}是什么意思？",
              "acceptedAnswer": {"@type": "Answer", "text": f"{it['name']}，拼音{it['pinyin']}。{it['meaning']}"}},
             {"@type": "Question", "name": f"{it['name']}的出处是什么？",
              "acceptedAnswer": {"@type": "Answer", "text": it["origin"][:220]}},
             {"@type": "Question", "name": f"{it['name']}的近义词有哪些？",
              "acceptedAnswer": {"@type": "Answer",
                                 "text": f"{it['name']}的近义词有：" + "、".join(it.get("synonyms", []) or ["暂无"]) + "。"}},
         ]},
    ]

    content = f'''
{breadcrumb(crumbs, root)}
<div class="container idiom-page">
  <header class="idiom-hero card">
    <h1>{it["name"]}</h1>
    <p class="py big">{it["pinyin"]}</p>
    <div class="idiom-meta">
      <a class="badge" href="../category/{cat["slug"]}.html">{cat["name"]}</a>
      <a class="badge badge-letter" href="../category/letter-{it["letter"].lower()}.html">首字母 {it["letter"]}</a>
    </div>
  </header>

  {AD_TOP}

  <section class="card section-card"><h2>释义</h2><p>{it["meaning"]}</p></section>
  <section class="card section-card"><h2>出处 / 典故</h2><p>{it["origin"]}</p></section>
  <section class="card section-card"><h2>例句 / 造句</h2><ul class="example-list">{examples}</ul></section>
  <section class="card section-card two-col">
    <div><h2>近义词</h2><div class="term-row">{syns}</div></div>
    <div><h2>反义词</h2><div class="term-row">{ants}</div></div>
  </section>
  <section class="card section-card"><h2>成语接龙：「{last_char}」字开头</h2>
    <div class="grid grid-idioms sm">{jielong_html}</div></section>

  {AD_BOTTOM}

  <section class="section"><h2 class="section-title">相关{cat["name"]}</h2>
    <div class="grid grid-idioms">{related_html}</div>
    <p class="center"><a class="btn" href="../category/{cat["slug"]}.html">查看全部{cat["name"]} →</a></p>
  </section>
</div>'''
    return page(title, desc, f"idiom/{it['slug']}.html", content, root=root,
                jsonld_extra=jsonld,
                keywords=f"{it['name']},{it['name']}的意思,{it['name']}造句,{it['name']}近义词")


# ---------------------------------------------------------------------------
# 分类页（字母 + 主题）
# ---------------------------------------------------------------------------

def gen_category(name, desc_extra, slug, items, idioms, kind):
    root = "../"
    cards = "".join(idiom_card(i, root) for i in sorted(items, key=lambda x: x["slug"]))
    related_themes = "".join(
        f'<a class="side-link" href="../category/{t["slug"]}.html">{t["name"]}<span>{sum(1 for i in idioms if i["category"]==t["name"])}</span></a>'
        for t in THEMES[:8] if t["name"] != name)
    letter_nav = "".join(
        f'<a class="letter-chip{" on" if l == slug.replace("letter-", "").upper() else ""}" href="../category/letter-{l.lower()}.html">{l}</a>'
        for l in LETTERS if l != "other") if kind == "letter" else ""

    content = f'''
{breadcrumb([(SITE_NAME, "../index.html"), (name, None)], root)}
<div class="container page-layout">
  <div class="page-main">
    <header class="page-head">
      <h1>{name}成语大全</h1>
      <p class="muted">本页共收录 {len(items)} 个{name}成语，按拼音排序。{desc_extra}</p>
      {f'<div class="letter-row">{letter_nav}</div>' if letter_nav else ""}
    </header>
    <div class="grid grid-idioms">{cards or '<p class="muted">该分类暂无收录成语，持续补充中。</p>'}</div>
  </div>
  <aside class="page-side">
    {AD_TOP}
    <div class="card side-card"><h3>相关分类</h3>{related_themes}</div>
  </aside>
</div>'''
    title = f"{name}成语大全 - 精选{name}成语列表"
    desc = f"精选 {len(items)} 个{name}成语，含拼音、释义、出处与例句，{name}成语大全在线查询。"
    jsonld = [breadcrumb_ld([(SITE_NAME, ""), (name, f"category/{slug}.html")]),
              {"@context": "https://schema.org", "@type": "ItemList",
               "name": f"{name}成语大全",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x["name"],
                                    "url": f"{SITE_URL}/idiom/{x['slug']}.html"}
                                   for i, x in enumerate(items[:50])]}]
    return page(title, desc, f"category/{slug}.html", content, root=root,
                jsonld_extra=jsonld, keywords=f"{name}成语,{name}成语大全,{name}成语列表")


# ---------------------------------------------------------------------------
# 搜索页 / 政策页
# ---------------------------------------------------------------------------

def gen_search(idioms):
    content = f'''
<div class="container narrow">
  <h1>成语搜索</h1>
  <p class="muted">在 {len(idioms)}+ 条成语数据中，按名称或释义关键词查找。</p>
  <div class="search-box hero-search">
    <input type="search" id="globalSearch" placeholder="输入成语或关键词，如：守株待兔" autocomplete="off">
    <div class="search-results" id="searchResults"></div>
  </div>
  <div id="searchPageResults" class="grid grid-idioms search-page-results"></div>
</div>'''
    return page("成语搜索 - 按名称或释义查询成语", f"{SITE_NAME}成语搜索：支持按成语名称与释义关键词在线查询 {len(idioms)}+ 条成语数据。",
                "search.html", content, root="", keywords="成语搜索,成语查询")


def gen_privacy():
    content = '''
<div class="container narrow">
<h1>隐私政策</h1>
<p class="muted">最后更新：2026 年 9 月 27 日</p>
<h2>1. 引言</h2>
<p>欢迎使用本站（下称"本站"）。本政策说明我们如何处理您访问本站时产生的信息，使用本站即表示您同意本政策。</p>
<h2>2. Cookie 与本地存储</h2>
<p>本站使用浏览器本地存储记住您的主题偏好（暗色模式）。本站可能使用第三方分析服务收集匿名访问统计。</p>
<h2>3. 广告与 Google AdSense</h2>
<p>本站使用 Google AdSense 展示广告。Google 及其合作伙伴可能使用 Cookie（包括第三方 Cookie）根据您以往的访问记录投放个性化广告。您可以访问 <a href="https://adssettings.google.com" target="_blank" rel="nofollow noopener">Google 广告设置</a> 管理个性化广告，或访问 <a href="https://www.aboutads.info" target="_blank" rel="nofollow noopener">aboutads.info</a> 选择退出第三方 Cookie。</p>
<h2>4. 内容声明</h2>
<p>本站成语释义、出处等内容整理自公开典籍与资料，仅供学习参考。如有错误欢迎指正。</p>
<h2>5. 联系我们</h2>
<p>如对本政策有疑问，请通过<a href="contact.html">联系我们</a>页面告知。</p>
</div>'''
    return page("隐私政策", "本站隐私政策：Cookie 使用、Google AdSense 广告与内容声明。", "privacy-policy.html", content, root="")


def gen_about():
    content = f'''
<div class="container narrow">
<h1>关于我们</h1>
<p><strong>{SITE_NAME}</strong> 是一个免费的中文成语在线词典，收录常用成语 500 余条，提供拼音、释义、出处典故、例句造句、近义词反义词与成语接龙查询。</p>
<h2>我们的目标</h2>
<p>帮助中小学生、家长和所有中文学习者更方便地理解和使用成语，传承中华语言文化。</p>
<h2>内容说明</h2>
<p>成语释义与出处整理自公开典籍资料，逐条人工核对。若发现错误，欢迎通过<a href="contact.html">联系我们</a>指正。</p>
</div>'''
    return page("关于我们", f"了解 {SITE_NAME}：免费在线成语词典，收录 500+ 常用成语，附拼音释义出处与例句。", "about.html", content, root="")


def gen_contact():
    content = '''
<div class="container narrow">
<h1>联系我们</h1>
<p>欢迎通过以下方式与我们联系。</p>
<h2>📮 意见与合作</h2>
<p>成语纠错、内容建议、商务合作：<strong>hello@chengyu.example.com</strong></p>
<h2>📝 联系表单</h2>
<div class="card contact-form">
  <form action="#" method="post" onsubmit="alert('演示站点：请通过邮件联系我们');return false;">
    <label>你的邮箱<input type="email" required placeholder="you@example.com"></label>
    <label>留言内容<textarea rows="5" required placeholder="想对我们说什么…"></textarea></label>
    <button type="submit" class="btn">发送留言</button>
    <p class="muted">正式上线时可接入 Formspree 等静态表单服务。</p>
  </form>
</div>
</div>'''
    return page("联系我们", f"联系 {SITE_NAME}：成语纠错、内容建议与合作联系方式。", "contact.html", content, root="")


# ---------------------------------------------------------------------------
# sitemap / robots / 搜索索引
# ---------------------------------------------------------------------------

def gen_sitemap(urls):
    items = "\n".join(
        f"  <url><loc>{SITE_URL}/{u}</loc><changefreq>{'weekly' if 'idiom' in u else 'monthly'}</changefreq>"
        f"<priority>{'1.0' if u == '' else ('0.9' if 'idiom' in u else '0.6')}</priority></url>"
        for u in urls)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>'''


def write(path, content):
    full = os.path.join(DOCS, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    idioms = load_idioms()
    by_name = {i["name"]: i for i in idioms}
    by_letter = {}
    for i in idioms:
        by_letter.setdefault(i["letter"], []).append(i)

    print(f"成语数据：{len(idioms)} 条")
    write("index.html", gen_index(idioms, by_name))
    write("search.html", gen_search(idioms))
    for i in idioms:
        write(f"idiom/{i['slug']}.html", gen_idiom(i, idioms, by_name, by_letter))
    for t in THEMES:
        items = [i for i in idioms if i["category"] == t["name"]]
        write(f"category/{t['slug']}.html", gen_category(t["name"], t["desc"] + "。", t["slug"], items, idioms, "theme"))
    for l in LETTERS:
        items = by_letter.get(l, [])
        lname = f"首字母 {l}" if l != "other" else LETTER_NAME[l]
        write(f"category/letter-{l.lower()}.html",
              gen_category(lname, "按拼音首字母索引。", f"letter-{l.lower()}", items, idioms, "letter"))
    write("privacy-policy.html", gen_privacy())
    write("about.html", gen_about())
    write("contact.html", gen_contact())

    urls = ["", "search.html"]
    urls += [f"idiom/{i['slug']}.html" for i in idioms]
    urls += [f"category/{t['slug']}.html" for t in THEMES]
    urls += [f"category/letter-{l.lower()}.html" for l in LETTERS]
    urls += ["privacy-policy.html", "about.html", "contact.html"]
    write("sitemap.xml", gen_sitemap(urls))
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

    # 搜索索引（纯 JS，客户端加载）
    idx = [{"n": i["name"], "p": i["pinyin"], "m": i["meaning"][:40], "u": f"idiom/{i['slug']}.html"}
           for i in idioms]
    os.makedirs(os.path.join(DOCS, "static"), exist_ok=True)
    with open(os.path.join(DOCS, "static", "search-index.js"), "w", encoding="utf-8") as f:
        f.write("window.SEARCH_INDEX=" + json.dumps(idx, ensure_ascii=False) + ";")

    # 复制静态资源到 docs/static/
    for name in ("style.css", "app.js"):
        src = os.path.join(ROOT, "static", name)
        with open(src, encoding="utf-8") as fsrc:
            write(f"static/{name}", fsrc.read())

    total = len(urls)
    print(f"完成：共 {total} 个页面（成语 {len(idioms)} + 主题分类 {len(THEMES)} + 字母分类 {len(LETTERS)} + 其他 7）")


if __name__ == "__main__":
    main()
