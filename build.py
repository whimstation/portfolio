#!/usr/bin/env python3
"""Генератор портфолио.

Все тексты и настройки — в src/site.json, кейсы — src/cases/*.html,
разделы — src/sections/*.html, видео — src/media.json + папка media/.
Запуск:  python3 build.py   (пишет готовый сайт в корень репозитория)
"""
import html, json, os, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
SITE = json.load(open(os.path.join(SRC, 'site.json'), encoding='utf-8'))
MEDIA = json.load(open(os.path.join(SRC, 'media.json'), encoding='utf-8'))
P = SITE['person']

SECTION_NAMES = {'work': 'Work', 'writing': 'Writing', 'practice': 'Practice',
                 'expertise': 'Expertise', 'process': 'Process', 'about': 'About',
                 'contact': 'Contact'}


def t(v):
    """{'ru':..,'en':..} -> двуязычный span; строка -> как есть."""
    if isinstance(v, dict):
        return f'<span class="lang-ru">{v["ru"]}</span><span class="lang-en">{v["en"]}</span>'
    return v


def tp(v, lang='ru'):
    return v[lang] if isinstance(v, dict) else v


def media_file(slug, ext):
    return os.path.exists(os.path.join(ROOT, 'media', f'{slug}.{ext}'))


def poster_url(slug, root):
    if slug.startswith('img:'):
        return f'{root}media/{slug[4:]}'
    if media_file(slug, 'jpg'):
        return f'{root}media/{slug}.jpg'
    m = MEDIA[slug]
    if 'drive' in m:
        return f'https://drive.google.com/thumbnail?id={m["drive"]}&sz=w800'
    return f'https://i.ytimg.com/vi/{m["yt"]}/hqdefault.jpg'


PLAY = '<span class="play" aria-hidden="true"></span>'


def player(slug, root):
    """Видео: локальный MP4 (основной путь) → Drive → YouTube (запасные)."""
    m = MEDIA[slug]
    badge = f'<span class="badge">{m["badge"]}</span>' if m.get('badge') else ''
    poster = poster_url(slug, root)
    if media_file(slug, 'mp4'):
        return (f'<video class="vid" preload="none" playsinline poster="{poster}" '
                f'src="{root}media/{slug}.mp4"></video>'
                f'<button class="vid-cover" aria-label="Play">{PLAY}</button>{badge}')
    if 'drive' in m:
        src = f'https://drive.google.com/file/d/{m["drive"]}/preview'
    else:
        src = f'https://www.youtube-nocookie.com/embed/{m["yt"]}?autoplay=1&rel=0'
    return (f'<img class="vid-poster" src="{poster}" alt="" loading="lazy">'
            f'<button class="vid-cover" data-embed="{src}" aria-label="Play">{PLAY}</button>{badge}')


def expand_media(s, root, cv='assets/cv.pdf'):
    s = re.sub(r'\[\[tile:([\w-]+)\]\]',
               lambda m: f'<div class="case-tile case-tile-{MEDIA[m.group(1)]["aspect"]}">{player(m.group(1), root)}</div>', s)
    s = re.sub(r'\[\[hero:([\w-]+)\]\]',
               lambda m: f'<div class="case-hero-video">{player(m.group(1), root)}</div>', s)
    s = re.sub(r'\[\[inline:([\w-]+)\]\]',
               lambda m: f'<div class="case-tile case-tile-16-9 inline-media">{player(m.group(1), root)}</div>', s)
    return s.replace('{{cv}}', root + cv).replace('{{root}}', root)


def read(*p):
    return open(os.path.join(SRC, *p), encoding='utf-8').read()


# ---------- общие куски ----------

HEAD_SCRIPT = """<script>
(function(){var d=document.documentElement,q=new URLSearchParams(location.search),t=null,l=null;
try{t=localStorage.getItem('nt-theme');l=localStorage.getItem('nt-lang')}catch(e){}
var ql=q.get('lang');if(ql==='ru'||ql==='en'){l=ql;try{localStorage.setItem('nt-lang',l)}catch(e){}}
if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
if(t==='dark')d.classList.add('dark');d.setAttribute('lang',l||'ru');})();
</script>"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23EDE8D9'/%3E"
           "%3Ctext x='50' y='62' font-family='Helvetica,Arial,sans-serif' font-size='40' font-weight='500' text-anchor='middle' fill='%231A1A1A'%3ENT%3C/text%3E%3C/svg%3E")

SUN = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="4"/>'
       '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>')


def page(title, desc, root, home, nav_html, main_html, ticker, version):
    name_en = P['name']['en']
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Lora:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css">
<link rel="icon" href="{FAVICON}">
{HEAD_SCRIPT}
</head>
<body>

<header class="site-header">
  <div class="site-header-inner">
    <div class="site-name"><a href="{home}">{name_en}</a></div>
    <div class="site-meta">{version['title']}</div>
    <div class="controls">
      <div class="lang-switcher"><button class="lang-btn" data-lang="ru">RU</button><button class="lang-btn" data-lang="en">EN</button></div>
      <div class="theme-switcher"><button class="theme-btn" id="themeToggle" aria-label="Toggle theme">{SUN}</button></div>
      <button class="burger" id="burger" aria-label="Menu"><span></span><span></span></button>
    </div>
  </div>
</header>

<div class="page">
{nav_html}
  <main>
{main_html}
  </main>
{meta_col(root, home, version)}
</div>

<footer class="ticker">
  <div><a href="mailto:{P['email']}">{P['email']}</a></div>
  <div class="ticker-center">{ticker}</div>
  <div><a href="#top" class="to-top">↑ TOP</a></div>
</footer>

<script src="{root}js/main.js"></script>
</body>
</html>
"""


def meta_col(root, home, version):
    return f"""  <aside class="meta-col" id="metaCol">
    <div class="meta-label">CONTACT</div>
    <div class="meta-val"><a href="mailto:{P['email']}">{P['email']}</a><br><a href="https://t.me/{P['telegram']}" target="_blank" rel="noopener">@{P['telegram']} · Telegram</a></div>
    <div class="meta-label">BASED</div>
    <div class="meta-val">{t(P['based'])}</div>
    <div class="meta-label">LANGUAGES</div>
    <div class="meta-val">{t(P['languages'])}</div>
    <div class="meta-label">YEARS IN VISUAL</div>
    <div class="meta-val">{P['years']}</div>
    <div class="meta-label">CV</div>
    <div class="meta-val"><a href="{root}{version['cv']}" download class="cv-link">→ Download PDF</a></div>
  </aside>"""


def nav(version, home, active=None, on_home=True):
    links = []
    for sec in ['work'] + [s for s in version['sections'] if s != 'work']:
        href = f'#{sec}' if on_home else f'{home}#{sec}'
        cls = 'nav-link' + (' active' if sec == active else '')
        links.append(f'    <a href="{href}" class="{cls}">{SECTION_NAMES[sec]}</a>')
    return '  <nav class="side-nav" id="sideNav">\n' + '\n'.join(links) + \
        f'\n    <div class="side-nav-tag">↑ {version["title"].upper()}</div>\n  </nav>'


# ---------- главная версии ----------

def card(slug, root, prefix):
    c = SITE['cards'][slug]
    thumbs = c['thumbs']
    imgs = ''.join(f'<img src="{poster_url(s, root)}" alt="" loading="lazy">' for s in thumbs)
    return (f'<a href="{prefix}cases/{slug}.html" class="work-card">'
            f'<div class="work-card-media n{len(thumbs)}">{imgs}</div>'
            f'<div class="work-card-body"><div class="work-card-head"><span class="work-card-title">{t(c["title"])}</span>'
            f'<span class="work-card-year">{c["years"]}</span></div>'
            f'<div class="work-card-line">{t(c["line"])}</div></div></a>')


def about_section(version):
    paras = ''.join(f'<p class="about-text">{t(SITE["about"][k])}</p>' for k in version['about'])
    bg = read('sections', 'about.html')
    i = bg.find('<div class="section-label" style="margin-top:32px">↓ BACKGROUND')
    return ('<h2 class="section-title">About</h2>\n' + paras + '\n' + (bg[i:] if i >= 0 else ''))


def build_home(version):
    vid = version['id']
    depth = 1 if vid else 0
    root = '../' * depth
    out_dir = os.path.join(ROOT, vid) if vid else ROOT
    home = './'

    hero = f"""    <section id="top" class="hero">
      <div class="eyebrow">{t(version['role'])}</div>
      <h1 class="hero-title">{t(P['name'])}</h1>
      <p class="hero-intro">{t(version['intro'])}</p>
      <div class="hero-cta">
        <a href="mailto:{P['email']}" class="btn btn-accent">{P['email']}</a>
        <a href="https://t.me/{P['telegram']}" target="_blank" rel="noopener" class="btn">Telegram</a>
        <a href="{root}{version['cv']}" download class="btn">CV · PDF</a>
      </div>
    </section>"""

    parts = [hero]
    for sec in ['work'] + [s for s in version['sections'] if s != 'work']:
        if sec == 'work':
            cards = '\n'.join(card(s, root, '') for s in version['cases'])
            body = (f'<div class="section-label">↓ SELECTED WORK · {len(version["cases"]):02d}</div>\n'
                    f'<div class="work-grid">\n{cards}\n</div>')
            if 'practice' not in version['sections']:
                pass
        elif sec == 'about':
            body = about_section(version)
        else:
            body = read('sections', f'{sec}.html')
        parts.append(f'    <section id="{sec}">\n{expand_media(body, root, version["cv"])}\n    </section>')

    # writing-версия: блок писем идёт первым после hero
    order = version['sections']
    if order and order[0] != 'work':
        first = [p for p in parts if f'id="{order[0]}"' in p]
        rest = [p for p in parts[1:] if p not in first]
        parts = [parts[0]] + first + rest

    title = f"{P['name']['en']} — {version['title']}"
    html_out = page(title, tp(version['intro']), root, home,
                    nav(version, home), '\n\n'.join(parts), version['ticker'], version)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(html_out)

    # кейсы этой версии
    cases = version['cases']
    for i, slug in enumerate(cases):
        build_case(version, slug, cases[i - 1] if i > 0 else None,
                   cases[i + 1] if i + 1 < len(cases) else None, depth + 1, out_dir)


def build_case(version, slug, prev, nxt, depth, out_dir):
    root = '../' * depth
    home = '../'
    body = expand_media(read('cases', f'{slug}.html'), root)

    def link(s, label):
        if not s:
            return '<span></span>'
        c = SITE['cards'][s]
        return f'<a href="{s}.html" class="case-nav-link"><span class="case-nav-l">{label}</span>{t(c["title"])}</a>'

    main_html = f"""    <a href="{home}#work" class="back-link">← <span class="lang-ru">Все работы</span><span class="lang-en">All work</span></a>
    <article class="case-block" id="top">
{body}
    </article>
    <nav class="case-nav">{link(prev, '← PREV')}{link(nxt, 'NEXT →')}</nav>"""
    c = SITE['cards'][slug]
    title = f"{tp(c['title'], 'en')} — {P['name']['en']}"
    out = page(title, tp(c['line']), root, home, nav(version, home, 'work', on_home=False),
               main_html, version['ticker'], version)
    os.makedirs(os.path.join(out_dir, 'cases'), exist_ok=True)
    open(os.path.join(out_dir, 'cases', f'{slug}.html'), 'w', encoding='utf-8').write(out)


REDIRECTS = {'work.html': './#work', 'writing.html': './#writing', 'about.html': './#about',
             'contact.html': './#contact', 'expertise.html': 'creative/#expertise',
             'process.html': 'product/#process', 'practice.html': './#practice',
             '0-PREVIEW.html': './'}


def build():
    ids = [v['id'] for v in SITE['versions']]
    for v in SITE['versions']:
        if v['id']:
            shutil.rmtree(os.path.join(ROOT, v['id']), ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT, 'cases'), ignore_errors=True)
    for v in SITE['versions']:
        build_home(v)
    for f, to in REDIRECTS.items():
        open(os.path.join(ROOT, f), 'w').write(
            f'<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={to}">'
            f'<link rel="canonical" href="{to}"><a href="{to}">→</a>')
    open(os.path.join(ROOT, '.nojekyll'), 'w').close()
    missing = [s for s in MEDIA if not media_file(s, 'mp4')]
    print('versions:', ', '.join('/' + i for i in ids))
    print(f'video: {len(MEDIA) - len(missing)}/{len(MEDIA)} local mp4' + (f'; fallback embeds: {", ".join(missing)}' if missing else ''))


if __name__ == '__main__':
    build()
