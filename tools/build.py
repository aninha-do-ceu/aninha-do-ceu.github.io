#!/usr/bin/env python3
"""
Gera as páginas estáticas (com SEO) dos estudos de caso a partir de arquivos Markdown.

    static/**                 ──►  dist/**   (copiado como está: index.html, assets/, embed/...)
    content/projetos/<n>.md   ──►  dist/projetos/<n>/index.html
                                   dist/sitemap.xml, dist/robots.txt
                                   (e preenche os marcadores em dist/index.html)

Uso (a partir da raiz do repositório):
    pip install -r tools/requirements.txt  # só na primeira vez
    python tools/build.py                  # recria dist/ do zero
    python -m http.server 8000 -d dist     # pré-visualizar em http://localhost:8000

Variável opcional:  SITE_URL=https://seu-dominio  (padrão abaixo)
Em produção, o GitHub Actions (.github/workflows/deploy.yml) roda este mesmo script.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString
from markdown_it import MarkdownIt
from pygments import highlight as pyg_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

# ───────────────────────── configuração ─────────────────────────
SITE_URL = os.environ.get("SITE_URL", "https://aninha-do-ceu.github.io").rstrip("/")
SITE_NAME = "Ana Rosa Nascimento"
AUTHOR = "Ana Rosa Nascimento"
GITHUB_USER = "aninha-do-ceu"
KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"
GENERATED_MARK = "<!-- gerado por tools/build.py — edite o .md em content/, não este arquivo -->"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTENT = ROOT / "content" / "projetos"   # fonte: Markdown
STATIC = ROOT / "static"                  # copiado como está
DIST = ROOT / "dist"                      # saída (o que vai ao ar)
SITE = DIST                               # verificações de arquivo e atualizações valem sobre a saída
PROJ_DIR = DIST / "projetos"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WARNINGS = []


def warn(slug, msg):
    WARNINGS.append(f"[{slug}] {msg}")


# ───────────────────────── markdown ─────────────────────────
def highlight_code(code, lang):
    try:
        lexer = get_lexer_by_name(lang) if lang else None
    except ClassNotFound:
        lexer = None
    if lexer:
        body = pyg_highlight(code, lexer, HtmlFormatter(nowrap=True, classprefix="hl-"))
    else:
        body = html.escape(code)
    cls = f' class="language-{html.escape(lang)}"' if lang else ""
    return f"<pre><code{cls}>{body}</code></pre>\n"


MD = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])


def _fence(self, tokens, idx, options, env):
    tok = tokens[idx]
    info = tok.info.strip()
    return highlight_code(tok.content, info.split()[0] if info else "")


MD.add_render_rule("fence", _fence)


def parse_front(text):
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    m = re.match(r"^---[ \t]*\n([\s\S]*?)\n---[ \t]*(?:\n|$)", text)
    meta = {}
    if not m:
        return meta, text
    for line in m.group(1).split("\n"):
        i = line.find(":")
        if i > 0:
            val = line[i + 1:].strip()
            val = re.sub(r"""^(["'])(.*)\1$""", r"\2", val)
            meta[line[:i].strip().lower()] = val
    return meta, text[m.end():]


def slugify(text):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def is_external(src):
    return bool(re.match(r"^(https?:)?//|^data:|^mailto:|^#", src))


def site_file(src):
    return SITE / src.lstrip("/")


class Ctx:
    def __init__(self, slug):
        self.slug = slug
        self.maths = []   # (tex, display)
        self.embeds = []


def restore(text, ctx):
    """Tokens XXMATHnXX → marcação que o KaTeX (no navegador) desenha."""
    def sub(m):
        tex, display = ctx.maths[int(m.group(1))]
        t = html.escape(tex, quote=False)
        if display:
            return f'<span class="math display">\\[{t}\\]</span>'
        return f'<span class="math inline">\\({t}\\)</span>'
    return re.sub(r"XXMATH(\d+)XX", sub, text).replace("XXDOLLARXX", "$")


def plain(text, ctx):
    """Versão sem marcação (para atributos alt)."""
    text = re.sub(r"XXMATH(\d+)XX", lambda m: ctx.maths[int(m.group(1))][0], text)
    return text.replace("XXDOLLARXX", "$")


def placeholder(text):
    return f'<div class="img-placeholder">{html.escape(text)}</div>'


def embed_html(args, ctx):
    parts = [p.strip() for p in args.split("|")]
    src = parts[0]
    height = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
    cap = parts[2] if len(parts) > 2 else ""
    if not is_external(src) and not site_file(src).is_file():
        warn(ctx.slug, f"embed não encontrado: {src}")
        return placeholder(f"📊 Gráfico interativo pendente — salve o arquivo em {src}")
    url = src if is_external(src) else "/" + src.lstrip("/")
    style = f' style="height:{height}px"' if height else ""
    out = (f'<div class="embed"{style}><iframe src="{html.escape(url)}" loading="lazy" '
           f'title="{html.escape(cap or "Gráfico interativo")}"></iframe></div>')
    if cap:
        out += f'<p class="embed-caption">{html.escape(cap)}</p>'
    return out


def markdown_to_html(body, ctx):
    codes = []

    def keep(m):
        codes.append(m.group(0))
        return f"XXCODE{len(codes) - 1}XX"

    s = re.sub(r"^(```+|~~~+)[^\n]*\n[\s\S]*?^\1[ \t]*$", keep, body, flags=re.M)
    s = re.sub(r"`[^`\n]+`", keep, s)
    s = s.replace("\\$", "XXDOLLARXX")

    def embed(m):
        ctx.embeds.append(embed_html(m.group(1), ctx))
        return f"\n\nXXEMBED{len(ctx.embeds) - 1}XX\n\n"
    s = re.sub(r"^\[\[embed:([^\]]*)\]\][ \t]*$", embed, s, flags=re.M)

    def add_math(tex, display):
        ctx.maths.append((tex, display))
        return f"XXMATH{len(ctx.maths) - 1}XX"
    s = re.sub(r"\$\$([\s\S]+?)\$\$", lambda m: add_math(m.group(1).strip(), True), s)
    s = re.sub(r"\\begin\{(equation\*?)\}([\s\S]+?)\\end\{\1\}", lambda m: add_math(m.group(2).strip(), True), s)
    s = re.sub(r"\\begin\{(align\*?|gather\*?|aligned)\}[\s\S]+?\\end\{\1\}", lambda m: add_math(m.group(0), True), s)
    s = re.sub(r"\\\[([\s\S]+?)\\\]", lambda m: add_math(m.group(1).strip(), True), s)
    s = re.sub(r"\$([^\s$](?:[^$\n]*?[^\s$])?)\$(?!\d)", lambda m: add_math(m.group(1), False), s)

    s = re.sub(r"XXCODE(\d+)XX", lambda m: codes[int(m.group(1))], s)
    out = MD.render(s)
    out = re.sub(r"<p>\s*XXEMBED(\d+)XX\s*</p>", lambda m: ctx.embeds[int(m.group(1))], out)
    return re.sub(r"XXEMBED(\d+)XX", lambda m: ctx.embeds[int(m.group(1))], out)


def only_child(tag):
    kids = [c for c in tag.contents if not (isinstance(c, NavigableString) and not c.strip())]
    return len(kids) == 1


def build_content(body, meta, ctx):
    """Retorna (titulo, html_das_seções, tem_matemática)."""
    soup = BeautifulSoup(markdown_to_html(body, ctx), "html.parser")

    # comentários HTML (ex.: <!-- PREENCHA -->) não vão para a página pública
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()

    h1 = soup.find("h1")
    title = meta.get("titulo") or (h1.get_text().strip() if h1 else ctx.slug)
    if h1 and not meta.get("titulo"):
        h1.extract()

    # imagens e figuras
    fig_n = 0
    for img in list(soup.find_all("img")):
        src = img.get("src", "")
        alt = plain(img.get("alt", ""), ctx)
        cap = img.get("title")
        node = img
        if not is_external(src):
            if site_file(src).is_file():
                img["src"] = "/" + src.lstrip("/")
            else:
                warn(ctx.slug, f"imagem não encontrada: {src}")
                node = BeautifulSoup(placeholder(f"🖼 Figura pendente: {alt or 'sem descrição'} — salve a imagem em {src}"),
                                     "html.parser").div
                img.replace_with(node)
        if node is img:
            img["alt"] = alt
            img["loading"] = "lazy"
            img["decoding"] = "async"
            if cap:
                del img["title"]
        parent = node.parent
        if cap and parent is not None and parent.name == "p" and only_child(parent):
            fig_n += 1
            fig = soup.new_tag("figure")
            fc = soup.new_tag("figcaption")
            fc.append(BeautifulSoup(f"<strong>Figura {fig_n}.</strong> " + restore(MD.renderInline(cap), ctx),
                                    "html.parser"))
            node.extract()
            fig.append(node)
            fig.append(fc)
            parent.replace_with(fig)

    # cada "## Título" vira um cartão
    container = BeautifulSoup("", "html.parser")
    cur = None
    for node in list(soup.contents):
        if isinstance(node, NavigableString) and not node.strip():
            continue
        if getattr(node, "name", None) == "h2" or cur is None:
            cur = container.new_tag("section")
            container.append(cur)
        cur.append(node.extract())

    used = set()
    for h in container.find_all(["h2", "h3"]):
        base = slugify(h.get_text()) or "secao"
        hid, n = base, 2
        while hid in used:
            hid, n = f"{base}-{n}", n + 1
        used.add(hid)
        h["id"] = hid

    for a in container.find_all("a", href=True):
        if re.match(r"^https?://", a["href"]):
            a["target"] = "_blank"
            a["rel"] = "noopener"

    content = restore(str(container), ctx)
    return title, content, bool(ctx.maths)


# ───────────────────────── páginas ─────────────────────────
def short(text, limit=160):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:—-") + "…"


def inline_text(md_text):
    return BeautifulSoup(MD.renderInline(md_text), "html.parser").get_text()


def last_modified(path):
    """Data da última alteração: do último commit do arquivo (git); senão, do arquivo."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)], cwd=ROOT,
                             capture_output=True, text=True, timeout=10).stdout.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", out):
            return out
    except (OSError, subprocess.SubprocessError):
        pass
    return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()


def split_authors(s):
    names = [n.strip() for n in re.split(r",\s*|\s+e\s+", s or "") if n.strip()]
    return names or [AUTHOR]


def load_pages():
    pages = []
    for md in sorted(CONTENT.glob("*.md")):
        if md.name.startswith("_"):
            continue
        slug = md.stem
        if not re.match(r"^[A-Za-z0-9_-]+$", slug):
            warn(slug, "nome de arquivo ignorado (use só letras, números, - e _)")
            continue
        text = md.read_text(encoding="utf-8")
        meta, body = parse_front(text)
        ctx = Ctx(slug)
        title, content, has_math = build_content(body, meta, ctx)
        for pat in ("PREENCHA", "[preencher"):
            if pat in text:
                warn(slug, f'ainda há "{pat}" no texto — preencha antes de publicar')
                break
        desc = meta.get("descricao") or inline_text(meta.get("subtitulo", ""))
        if not desc:
            p = BeautifulSoup(content, "html.parser").find("p")
            desc = p.get_text() if p else title
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        langs = [t.strip() for t in meta.get("linguagens", "").split(",") if t.strip()]
        d = meta.get("data", "")
        if d and not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            warn(slug, f'campo "data" deve ser AAAA-MM-DD (recebi "{d}") — ignorado')
            d = ""
        pages.append({
            "slug": slug, "md": md, "meta": meta, "title": title, "content": content,
            "has_math": has_math, "description": short(desc), "tags": tags, "langs": langs,
            "date": d, "lastmod": d or last_modified(md),
            "draft": meta.get("rascunho", "").lower() in ("sim", "true", "1", "yes"),
            "url": f"{SITE_URL}/projetos/{slug}/",
            "subtitle_plain": short(inline_text(meta.get("subtitulo", "")) or desc, 200),
        })
    return pages


def related_for(page, pages):
    others = [p for p in pages if p is not page and not p["draft"]]
    mine = {t.lower() for t in page["tags"] + page["langs"]}
    others.sort(key=lambda p: -len(mine & {t.lower() for t in p["tags"] + p["langs"]}))
    return others[:4]


def json_ld(page):
    meta = page["meta"]
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": page["title"],
        "description": page["description"],
        "inLanguage": "pt-BR",
        "url": page["url"],
        "mainEntityOfPage": page["url"],
        "author": [{"@type": "Person", "name": n} for n in split_authors(meta.get("autores"))],
        "publisher": {"@type": "Person", "name": AUTHOR, "url": SITE_URL + "/"},
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/"},
    }
    if page["tags"] or page["langs"]:
        data["keywords"] = page["langs"] + page["tags"]
    if page["date"]:
        data["datePublished"] = page["date"]
    data["dateModified"] = page["lastmod"]
    if page.get("image"):
        data["image"] = page["image"]
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": page["title"], "item": page["url"]},
        ],
    }
    return [json.dumps(d, ensure_ascii=False).replace("</", "<\\/") for d in (data, crumbs)]


def render_page(page, pages, css):
    meta, e = page["meta"], lambda s: html.escape(s, quote=True)
    title_full = f"{page['title']} — {SITE_NAME}"
    robots = "noindex,nofollow" if page["draft"] else "index,follow,max-image-preview:large"

    image = None
    if meta.get("imagem"):
        if site_file(meta["imagem"]).is_file():
            image = f"{SITE_URL}/{meta['imagem'].lstrip('/')}"
        else:
            warn(page["slug"], f"imagem de compartilhamento não encontrada: {meta['imagem']}")
    page["image"] = image

    og = [
        ("og:type", "article"), ("og:locale", "pt_BR"), ("og:site_name", SITE_NAME),
        ("og:title", page["title"]), ("og:description", page["description"]), ("og:url", page["url"]),
    ]
    if image:
        og.append(("og:image", image))
        og.append(("og:image:alt", meta.get("imagem_alt") or page["title"]))
    if page["date"]:
        og.append(("article:published_time", page["date"]))
    og += [("article:tag", t) for t in page["tags"]]
    og_html = "\n".join(f'<meta property="{k}" content="{e(v)}">' for k, v in og)
    tw = [("twitter:card", "summary_large_image" if image else "summary"),
          ("twitter:title", page["title"]), ("twitter:description", page["description"])]
    if image:
        tw.append(("twitter:image", image))
    tw_html = "\n".join(f'<meta name="twitter:{k.split(":")[1]}" content="{e(v)}">' for k, v in tw)

    math_head = math_tail = ""
    if page["has_math"]:
        math_head = (f'<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
                     f'<link rel="stylesheet" href="{KATEX}/katex.min.css">')
        math_tail = (
            f'<script defer src="{KATEX}/katex.min.js"></script>\n'
            f'<script defer src="{KATEX}/contrib/auto-render.min.js" onload="renderMathInElement('
            "document.querySelector('main'),{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},"
            "{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false})\"></script>"
        )

    chips = "".join(f'<span class="chip lang">{e(t)}</span>' for t in page["langs"])
    chips += "".join(f'<span class="chip">{e(t)}</span>' for t in page["tags"])
    chips = f'<div class="chips">{chips}</div>' if chips else ""
    sub = f'<p class="subtitle">{MD.renderInline(meta["subtitulo"])}</p>' if meta.get("subtitulo") else ""

    rel = related_for(page, pages)
    related = ""
    if rel and not page["draft"]:
        items = "".join(
            f'<li><a href="/projetos/{r["slug"]}/">{e(r["title"])}</a><span>{e(r["subtitle_plain"])}</span></li>' for r in rel)
        related = f'<section class="related"><h2 id="outros-estudos-de-caso">Outros estudos de caso</h2><ul>{items}</ul></section>'

    foot = []
    if meta.get("autores"):
        foot.append("Autoria: " + e(meta["autores"]))
    if meta.get("rodape"):
        foot.append(MD.renderInline(meta["rodape"]))
    if meta.get("repo"):
        r = meta["repo"]
        url = r if re.match(r"^https?://", r) else f"https://github.com/{GITHUB_USER}/{r}"
        foot.append(f'<a href="{e(url)}" target="_blank" rel="noopener">código no GitHub</a>')
    foot.append('<a href="/">voltar ao portfólio</a>')

    ld = "\n".join(f'<script type="application/ld+json">{j}</script>' for j in json_ld(page))
    return f"""<!DOCTYPE html>
{GENERATED_MARK}
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title_full)}</title>
<meta name="description" content="{e(page['description'])}">
<meta name="author" content="{e(AUTHOR)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{e(page['url'])}">
{og_html}
{tw_html}
{ld}
{math_head}
<style>
{css}
</style>
</head>
<body>
<div class="page">
  <a class="back" href="/">← Voltar ao portfólio</a>
  <main>
    <article>
      <header>
        <h1>{e(page['title'])}</h1>
        {sub}
        {chips}
      </header>
{page['content']}
    </article>
    {related}
  </main>
  <footer>{' · '.join(foot)}</footer>
</div>
{math_tail}
</body>
</html>
"""


# ───────────────────────── index, sitemap, robots ─────────────────────────
def update_index(pages):
    idx = SITE / "index.html"
    if not idx.is_file():
        warn("index", "static/index.html não encontrado — nada atualizado")
        return
    src = idx.read_text(encoding="utf-8")
    live = [p for p in pages if not p["draft"]]
    e = lambda s: html.escape(s, quote=True)

    cards = "".join(
        f'<article class="card"><h3><a href="projetos/{p["slug"]}/">{e(p["title"])}</a></h3>'
        f'<p class="desc">{e(p["subtitle_plain"])}</p>'
        f'<div class="meta">' + "".join(f'<span class="topic">{e(t)}</span>' for t in (p["langs"] + p["tags"])[:4]) +
        '</div></article>' for p in live)
    block = (f'<h2>Estudos de caso</h2>\n  <div class="grid">{cards}</div>' if live else "")

    # repo → página (usado pelos cartões gerados via API do GitHub)
    # um repositório pode ter vários estudos: repo → [[url, título], ...]
    by_repo = {}
    for p in live:
        repo = p["meta"].get("repo")
        if repo and "/" not in repo:
            by_repo.setdefault(repo, []).append((p["slug"], p["title"]))
    mapping = ",\n".join(
        f"      {json.dumps(repo)}: [" +
        ", ".join(f"[{json.dumps(f'projetos/{s}/')}, {json.dumps(t, ensure_ascii=False)}]" for s, t in items) + "]"
        for repo, items in by_repo.items())
    case_js = "var CASE_PAGES = {\n" + mapping + "\n    };" if mapping else "var CASE_PAGES = {};"

    new, n1 = re.subn(r"(<!-- CASES:START -->).*?(<!-- CASES:END -->)",
                      lambda m: f"{m.group(1)}\n  {block}\n  {m.group(2)}", src, flags=re.S)
    new, n2 = re.subn(r"(/\* CASES_MAP:START \*/).*?(/\* CASES_MAP:END \*/)",
                      lambda m: f"{m.group(1)}\n    {case_js}\n    {m.group(2)}", new, flags=re.S)
    if not (n1 and n2):
        warn("index", "marcadores CASES:START/END ou CASES_MAP:START/END ausentes em index.html")
    if new != src:
        idx.write_text(new, encoding="utf-8")


def write_sitemap(pages):
    urls = [(SITE_URL + "/", max([p["lastmod"] for p in pages if not p["draft"]] or [date.today().isoformat()]))]
    urls += [(p["url"], p["lastmod"]) for p in pages if not p["draft"]]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, d in urls:
        xml.append(f"  <url><loc>{html.escape(u)}</loc><lastmod>{d}</lastmod></url>")
    xml.append("</urlset>\n")
    (SITE / "sitemap.xml").write_text("\n".join(xml), encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")


def main():
    if not CONTENT.is_dir():
        sys.exit(f"Pasta de conteúdo não encontrada: {CONTENT}")
    # dist/ é sempre recriada do zero: não sobra página órfã nem arquivo velho
    if DIST.exists():
        shutil.rmtree(DIST)
    if STATIC.is_dir():
        shutil.copytree(STATIC, DIST, ignore=shutil.ignore_patterns(".gitkeep"))
    else:
        DIST.mkdir()
    PROJ_DIR.mkdir(exist_ok=True)

    css = HtmlFormatter(style="github-dark", classprefix="hl-").get_style_defs("pre code") + "\n" + \
        (HERE / "page.css").read_text(encoding="utf-8")
    pages = load_pages()
    for p in pages:
        out = PROJ_DIR / p["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(render_page(p, pages, css), encoding="utf-8")
        flag = "  [rascunho: noindex]" if p["draft"] else ""
        print(f"✔ dist/projetos/{p['slug']}/index.html{flag}")
    update_index(pages)
    write_sitemap(pages)
    print(f"✔ dist/sitemap.xml, dist/robots.txt e dist/index.html  (SITE_URL = {SITE_URL})")
    if WARNINGS:
        print("\nAvisos:")
        for w in WARNINGS:
            print("  ⚠", w)


if __name__ == "__main__":
    main()
