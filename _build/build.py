"""Generates /<slug>/index.html for every project from projects.json.
Run:  python3 _build/build.py   (from the repository root or anywhere)"""
import json, re, html, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALL = json.load(open(ROOT / '_build' / 'projects.json', encoding='utf-8'))
CDN, ORDER, data = ALL['cdn'], ALL['order'], ALL['projects']
MAN_PATH = ROOT / '_build' / 'images.json'
MAN = json.load(open(MAN_PATH)) if MAN_PATH.exists() else {}

def local(url):
    """Local copy (made by fetch_images.py) if present, else the original CDN url."""
    m = MAN.get(url)
    if m and all((ROOT / f.lstrip('/')).exists() for f in m['files']):
        return m
    return {'src': url, 'set': '', 'w': 0, 'h': 0}

def img_attrs(url, sizes):
    m = local(url)
    a = f'src="{esc(m["src"])}"'
    if m['set']: a += f' srcset="{esc(m["set"])}" sizes="{sizes}"'
    if m['w']: a += f' width="{m["w"]}" height="{m["h"]}"'
    return a

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
    def fig(u, sizes='(max-width:720px) 100vw, 96vw'):
        nonlocal n; n += 1
        return (f'<figure class="p-fig"><img {img_attrs(CDN + u, sizes)} alt="{esc(title)} — {n:02d}" '
                f'loading="{"eager" if n < 3 else "lazy"}" decoding="async"></figure>')
    while i < len(imgs):
        kind, u = imgs[i].split(' ', 1)
        if kind == 'G' and i + 1 < len(imgs) and imgs[i + 1].startswith('G '):
            half = '(max-width:720px) 100vw, 48vw'
            out.append('<div class="p-pair">' + fig(u, half) + fig(imgs[i + 1].split(' ', 1)[1], half) + '</div>'); i += 2
        else:
            out.append(fig(u)); i += 1
    return '\n'.join(out)


TR_PATH = ROOT / '_build' / 'translations.json'
TR = json.load(open(TR_PATH, encoding='utf-8')) if TR_PATH.exists() else {}

def render_both(slug, texts, title, meta):
    """English + Slovenian versions; the page shows the one matching the EN/SL switch."""
    t = TR.get(slug)
    if not t:
        return render_text(texts, title, meta)
    out = []
    for lang in ('en', 'sl'):
        body = render_text(t.get(lang, []), title, t.get('meta_' + lang, meta))
        out.append(f'<div data-lang="{lang}">\n{body}\n</div>')
    return '\n'.join(out)

def og_image(p):
    """1200x630 JPEG for link previews (WhatsApp, LinkedIn, ...), cropped from the local cover."""
    out = ROOT / 'images' / p['slug'] / 'og.jpg'
    if not out.exists():
        srcs = [ROOT / 'images' / p['slug'] / n for n in ('cover-1280.webp', 'cover.gif')]
        src = next((x for x in srcs if x.exists()), None)
        if not src:
            return '/og.jpg'
        try:
            from PIL import Image
            im = Image.open(src).convert('RGB'); W, H = 1200, 630
            k = max(W / im.width, H / im.height); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
            l, t = (im.width - W) // 2, (im.height - H) // 2
            im.crop((l, t, l + W, t + H)).save(out, 'JPEG', quality=84, optimize=True, progressive=True)
        except Exception:
            return '/og.jpg'
    return f'/images/{p["slug"]}/og.jpg'

TPL = open(ROOT / '_build' / 'project.tpl.html', encoding='utf-8').read()
for k, p in enumerate(ORDER):
    d = data[p['slug']]
    texts = [m['t'] for m in d['mods'] if isinstance(m, dict)]
    imgs = [m for m in d['mods'] if isinstance(m, str)]
    nxt = ORDER[(k + 1) % len(ORDER)]
    first_p = next((re.sub(r'\s+', ' ', t) for t in texts), d['meta']) or p['name']
    desc = (first_p[:155] + '…') if len(first_p) > 156 else first_p
    page = (TPL
        .replace('{{SLUG}}', p['slug'])
        .replace('{{OG}}', og_image(p))
        .replace('{{TITLE}}', esc(p['name']))
        .replace('{{DESC}}', esc(desc))
        .replace('{{YEAR}}', str(p['year']))
        .replace('{{NO}}', f'{k + 1:02d}')
        .replace('{{TOTAL}}', f'{len(ORDER):02d}')
        .replace('{{COUNT}}', f'{len(imgs):02d}')
        .replace('{{COVER_ATTRS}}', img_attrs(p['cover'], '100vw'))
        .replace('{{COVER}}', esc(local(p['cover'])['src'] if local(p['cover'])['w'] else p['cover']))
        .replace('{{TEXT}}', render_both(p['slug'], texts, p['name'], d['meta']))
        .replace('{{GALLERY}}', render_gallery(imgs, p['name']))
        .replace('{{NEXT_SLUG}}', nxt['slug'])
        .replace('{{NEXT_NAME}}', esc(nxt['name']))
        .replace('{{NEXT_COVER_ATTRS}}', img_attrs(nxt['cover'], '100vw')))
    out = ROOT / p['slug'] / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')

# keep the home page list in sync (names, years, links, thumbnails)
idx_path = ROOT / 'index.html'
idx = idx_path.read_text(encoding='utf-8')
thumb = lambda p: (MAN[p['cover']]['files'][0] if local(p['cover'])['w'] else p['thumb'])
big = lambda p: (MAN[p['cover']]['files'][-1] if local(p['cover'])['w'] else p['cover'])
rows = ',\n'.join('  ' + json.dumps([p['name'], p['year'], p['slug'], thumb(p), big(p)], ensure_ascii=False) for p in ORDER)
idx = re.sub(r"const IMG='[^']*';", "const IMG='';", idx)
idx = re.sub(r'const PROJECTS = \[.*?\n\];', lambda _: 'const PROJECTS = [\n' + rows + '\n];', idx, flags=re.S)
idx_path.write_text(idx, encoding='utf-8')
print(f'built {len(ORDER)} project pages')
