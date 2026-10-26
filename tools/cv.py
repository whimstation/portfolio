#!/usr/bin/env python3
"""Собирает PDF-резюме из src/cv.json: assets/cv.pdf, cv-creative.pdf, cv-writing.pdf, cv-product.pdf.
Нужен Playwright (python): pip install playwright && playwright install chromium"""
import json, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'src', 'cv.json'), encoding='utf-8'))
FONTS = os.path.join(ROOT, 'tools', 'fonts')


def ff(fam, w, file, style='normal'):
    return '\n'.join(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{style};src:url('file://{FONTS}/{file.format(s)}') format('woff2');unicode-range:{r}}}"
                     for s, r in (('latin', 'U+0000-00FF,U+2000-206F,U+2190-21FF'), ('cyrillic', 'U+0400-04FF')))


CSS = '\n'.join([ff('Sans', 400, 'noto-sans-{}-400-normal.woff2'), ff('Sans', 600, 'noto-sans-{}-600-normal.woff2'),
                 ff('Sans', 700, 'noto-sans-{}-700-normal.woff2'), ff('Mono', 400, 'ibm-plex-mono-{}-400-normal.woff2'),
                 ff('Mono', 500, 'ibm-plex-mono-{}-500-normal.woff2')]) + """
@page{size:A4;margin:13mm 15mm 13mm}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Sans',sans-serif;font-size:9.2pt;line-height:1.42;color:#1A1A1A}
a{color:inherit;text-decoration:none}
.mono{font-family:'Mono',monospace}
header{padding-bottom:10pt;border-bottom:.6pt solid #1A1A1A;margin-bottom:10pt}
h1{font-size:25pt;font-weight:700;letter-spacing:-.4pt;line-height:1.05}
.latin{font-family:'Mono',monospace;font-size:7.5pt;letter-spacing:1.6pt;color:#6B6A62;text-transform:uppercase;margin-top:3pt}
.role{font-size:12.5pt;font-weight:600;margin-top:6pt}
.contacts{margin-top:7pt;font-size:8.6pt;color:#3A3935;display:flex;flex-wrap:wrap;gap:2pt 14pt}
.contacts .pf{background:#E8E23C;padding:1pt 5pt;color:#1A1A1A;font-weight:600}
.summary{font-size:9.8pt;line-height:1.5;margin-bottom:4pt}
h2{font-family:'Mono',monospace;font-weight:500;font-size:7.6pt;letter-spacing:1.6pt;text-transform:uppercase;color:#6B6A62;
   margin:12pt 0 6pt;padding-top:5pt;border-top:.4pt solid #C9C3B1;break-after:avoid}
.job{display:grid;grid-template-columns:64pt 1fr;gap:0 12pt;margin-bottom:8pt;break-inside:avoid}
.yr{font-family:'Mono',monospace;font-size:7.8pt;color:#6B6A62;padding-top:1.5pt}
.jt{font-weight:600;font-size:10pt}
.jt .org{font-weight:700}
.jw{color:#6B6A62;font-weight:400}
.case{font-family:'Mono',monospace;font-size:7pt;color:#6B6A62;margin-left:4pt;white-space:nowrap}
ul{margin-top:2.5pt;padding-left:10pt}
li{margin-bottom:2pt}
li::marker{color:#9C9890}
.row{display:grid;grid-template-columns:64pt 1fr;gap:0 12pt;margin-bottom:3pt;break-inside:avoid}
.row .k{font-family:'Mono',monospace;font-size:7.8pt;color:#6B6A62;padding-top:1pt}
.sk .k{font-family:'Sans';font-size:8.6pt;color:#1A1A1A;font-weight:600;padding-top:0}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:0 18pt}
"""


def contacts(v):
    url = D['site'] + v['path']
    items = [f'<a href="{h}">{t}</a>' for t, h in D['contacts']]
    items.append(f'<a class="pf" href="{url}">Портфолио: {url.replace("https://", "")}</a>')
    items.append(f'<span>{D["location"]}</span>')
    return ''.join(items)


def render(key, v):
    out = [f"<header><h1>{D['name']}</h1><div class='latin'>{D['name_latin']}</div>"
           f"<div class='role'>{v['role']}</div><div class='contacts'>{contacts(v)}</div></header>",
           f"<p class='summary'>{v['summary']}</p>", '<h2>Опыт</h2>']
    base = D['site'] + v['path']
    for jid, bl in v['jobs']:
        j = D['jobs'][jid]
        where = f" <span class='jw'>· {j['where']}</span>" if j['where'] else ''
        case = f"<a class='case' href='{base}{j['case']}'>→ кейс</a>" if j.get('case') else ''
        lis = ''.join(f'<li>{j["b"][b]}</li>' for b in bl)
        out.append(f"<div class='job'><div class='yr'>{j['years']}</div><div><div class='jt'><span class='org'>{j['org']}</span> — {j['title']}{where}{case}</div><ul>{lis}</ul></div></div>")
    if v['writing']:
        out.append('<h2>Тексты и публикации</h2>')
        out += [f"<div class='row'><div class='k'>{a}</div><div><a href='{u}'>{b} <span class='case'>→ читать</span></a></div></div>" for a, b, u in D['writing']]
    out.append('<h2>Навыки и инструменты</h2>')
    out += [f"<div class='row sk'><div class='k'>{D['skills'][s][0]}</div><div>{D['skills'][s][1]}</div></div>" for s in v['skills']]
    def rows(lst):
        return ''.join(f"<div class='row'><div class='k'>{a}</div><div>{b}</div></div>" for a, b in lst)
    edu = sorted(D['education'] + D['courses'], key=lambda r: r[0], reverse=True)
    out.append(f"<h2>Образование и курсы</h2>{rows(edu)}")
    out.append(f"<h2>Фестивали и кредиты</h2>{rows(D['credits'])}")
    out.append(f"<h2>Языки</h2><div class='row'><div class='k'></div><div>{D['languages']}</div></div>")
    return f"<!DOCTYPE html><html lang='ru'><head><meta charset='utf-8'><title>{D['name_latin']} — CV</title><style>{CSS}</style></head><body>{''.join(out)}</body></html>"


def main(only=None):
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for key, v in D['versions'].items():
            if only and key not in only:
                continue
            html_path = os.path.join('/tmp', f'cv-{key}.html')
            open(html_path, 'w', encoding='utf-8').write(render(key, v))
            pg.goto('file://' + html_path)
            pg.wait_for_timeout(300)
            pdf = os.path.join(ROOT, 'assets', v['file'])
            pg.pdf(path=pdf, format='A4', prefer_css_page_size=True, print_background=True,
                   display_header_footer=True, header_template='<span></span>',
                   footer_template=f"<div style='width:100%;font-family:monospace;font-size:7px;color:#888;padding:0 15mm;display:flex;justify-content:space-between'><span>{D['name_latin'].upper()} · CV</span><span><span class='pageNumber'></span> / <span class='totalPages'></span></span></div>")
            print(pdf)
        b.close()


if __name__ == '__main__':
    main(sys.argv[1:])
