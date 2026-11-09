"""Generates /<slug>/index.html for every project from projects.json.
Run:  python3 _build/build.py   (from the repository root or anywhere)"""
import json, re, html, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CDN = 'https://cdn.myportfolio.com/082ff3c2-43cd-4de5-9163-6118ee4564e0/'
data = json.load(open(ROOT / '_build' / 'projects.json', encoding='utf-8'))

# order, display name, year, cover (1280 crop) — read from the index page so both stay in sync
idx = open(ROOT / 'index.html', encoding='utf-8').read()
plist = json.loads('[' + re.search(r'const PROJECTS = \[(.*?)\n\];', idx, re.S).group(1) + ']')
ORDER = [{'name': p[0], 'year': p[1], 'slug': p[2], 'cover': CDN + p[4]} for p in plist]

esc = lambda s: html.escape(s, quote=True)
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
is_credit = lambda l: bool(re.search(r'&|/|authors?:|mentor', l, re.I))


def render_text(texts, title, meta):
    if not texts:
        return f'<p class="p-only-meta">{esc(meta)}</p>' if meta else ''
    long_form = sum(len(t) for t in texts) > 3000
    out, sub_done = [], False
    for ti, t in enumerate(texts):
        lines = [l.strip().replace('​', '') for l in t.split('\n')]
        lines = [l for l in lines if l]
        if ti == 0 and lines and norm(lines[0]) == norm(title):
            lines = lines[1:]
        if long_form:  # re-join lines that were wrapped mid-sentence
            merged = []
            for l in lines:
                if merged and l[:1].islower() and not merged[-1].endswith(('.', ':', '?', '!', '«', '»')):
                    merged[-1] += ' ' + l
                else:
                    merged.append(l)
            lines = merged
        for l in lines:
            if long_form and re.match(r'^\d+\.\s', l):
                cls = 'p-ref' + ('' if any('p-ref' in o for o in out) else ' first')
                out.append(f'<p class="{cls}">{esc(l)}</p>')
            elif long_form and re.match(r'^\[\d', l):
                out.append(f'<p class="p-cite mono">{esc(l)}</p>')
            elif long_form and not l.isupper():
                out.append(f'<p>{esc(l)}</p>')
            elif len(l) <= 90 and not l.endswith('.'):
                if long_form or (l.isupper() and sub_done):
                    out.append(f'<h3>{esc(l)}</h3>')
                elif not sub_done and not is_credit(l):
                    out.append(f'<div class="p-sub">{esc(l)}</div>'); sub_done = True
                else:
                    out.append(f'<div class="p-cred mono">{esc(l)}</div>')
            else:
                out.append(f'<p>{esc(l)}</p>')
    return '\n'.join(out)


def render_gallery(imgs, title):
    out, i, n = [], 0, 0
    def fig(u):
        nonlocal n; n += 1
        return (f'<figure class="p-fig"><img src="{esc(CDN + u)}" alt="{esc(title)} — {n:02d}" '
                f'loading="{"eager" if n < 3 else "lazy"}" decoding="async"><span class="n mono">{n:02d}</span></figure>')
    while i < len(imgs):
        kind, u = imgs[i].split(' ', 1)
        if kind == 'G' and i + 1 < len(imgs) and imgs[i + 1].startswith('G '):
            out.append('<div class="p-pair">' + fig(u) + fig(imgs[i + 1].split(' ', 1)[1]) + '</div>'); i += 2
        else:
            out.append(fig(u)); i += 1
    return '\n'.join(out)


TPL = open(ROOT / '_build' / 'project.tpl.html', encoding='utf-8').read()
for k, p in enumerate(ORDER):
    d = data[p['slug']]
    texts = [m['t'] for m in d['mods'] if isinstance(m, dict)]
    imgs = [m for m in d['mods'] if isinstance(m, str)]
    nxt = ORDER[(k + 1) % len(ORDER)]
    first_p = next((re.sub(r'\s+', ' ', t) for t in texts), d['meta']) or p['name']
    desc = (first_p[:155] + '…') if len(first_p) > 156 else first_p
    page = (TPL
        .replace('{{TITLE}}', esc(p['name']))
        .replace('{{DESC}}', esc(desc))
        .replace('{{YEAR}}', str(p['year']))
        .replace('{{NO}}', f'{k + 1:02d}')
        .replace('{{TOTAL}}', f'{len(ORDER):02d}')
        .replace('{{COUNT}}', f'{len(imgs):02d}')
        .replace('{{COVER}}', esc(p['cover']))
        .replace('{{TEXT}}', render_text(texts, p['name'], d['meta']))
        .replace('{{GALLERY}}', render_gallery(imgs, p['name']))
        .replace('{{NEXT_SLUG}}', nxt['slug'])
        .replace('{{NEXT_NAME}}', esc(nxt['name']))
        .replace('{{NEXT_COVER}}', esc(nxt['cover'])))
    out = ROOT / p['slug'] / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')
print(f'built {len(ORDER)} project pages')
