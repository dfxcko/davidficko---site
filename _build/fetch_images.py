"""Downloads every project image from the old Adobe Portfolio CDN into /images,
as optimised WebP in two sizes, and records them in _build/images.json.
Safe to re-run: images already in the manifest are skipped.
Runs automatically in GitHub Actions (.github/workflows/images.yml)."""
import io, json, pathlib, time, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.load(open(ROOT / '_build' / 'projects.json', encoding='utf-8'))
MAN_PATH = ROOT / '_build' / 'images.json'
man = json.load(open(MAN_PATH)) if MAN_PATH.exists() else {}


def get(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://davidficko.com/'})
            return urllib.request.urlopen(req, timeout=90).read()
        except Exception as e:
            print('  retry', attempt + 1, e); time.sleep(3 * (attempt + 1))
    raise RuntimeError('failed: ' + url)


def save(url, folder, name, widths):
    if url in man and all((ROOT / p.lstrip('/')).exists() for p in man[url]['files']):
        return
    raw = get(url)
    folder.mkdir(parents=True, exist_ok=True)
    rel = '/' + str(folder.relative_to(ROOT)) + '/'
    im = Image.open(io.BytesIO(raw))
    w, h = im.size
    if url.split('?')[0].lower().endswith('.gif'):  # keep animation
        (folder / f'{name}.gif').write_bytes(raw)
        man[url] = {'w': w, 'h': h, 'src': rel + f'{name}.gif', 'set': '', 'files': [rel + f'{name}.gif']}
        return
    im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    files, srcset = [], []
    for W in widths:
        W2 = min(W, w)
        out = im if W2 == w else im.resize((W2, round(h * W2 / w)), Image.LANCZOS)
        fn = f'{name}-{W}.webp'
        out.save(folder / fn, 'WEBP', quality=82, method=6)
        files.append(rel + fn); srcset.append(f'{rel}{fn} {W2}w')
    man[url] = {'w': w, 'h': h, 'src': files[-1], 'set': ', '.join(srcset), 'files': files}


for p in DATA['order']:
    slug = p['slug']; folder = ROOT / 'images' / slug
    print(slug)
    save(p['cover'], folder, 'cover', [640, 1280])
    imgs = [m.split(' ', 1)[1] for m in DATA['projects'][slug]['mods'] if isinstance(m, str)]
    for i, u in enumerate(imgs):
        save(DATA['cdn'] + u, folder, f'{i + 1:02d}', [960, 1920])
    json.dump(man, open(MAN_PATH, 'w'), indent=0)
print('images:', len(man))
