"""Lote 2: recortes transparentes + fotos novas."""
import os, shutil, glob
from PIL import Image, ImageOps

ROOT = '/home/user/frizza-site/assets/img'
NEWO = os.path.join(ROOT, 'originais', 'lote-2')
os.makedirs(NEWO, exist_ok=True)

# move tudo o que chegou (fora das pastas organizadas) para originais/lote-2
KEEP = {'latas', 'sabores', 'historia', 'comunidade', 'onde-encontrar', 'elementos', 'marca', 'originais'}
for f in os.listdir(ROOT):
    p = os.path.join(ROOT, f)
    if f.endswith('.md') or f in KEEP: continue
    if os.path.isdir(p):
        for fp in glob.glob(p + '/**/*', recursive=True):
            if os.path.isfile(fp): shutil.move(fp, os.path.join(NEWO, os.path.basename(fp) if 'latas.png' not in fp else 'latas-' + os.path.basename(fp)))
        shutil.rmtree(p)
    else:
        shutil.move(p, os.path.join(NEWO, f))
O = lambda n: os.path.join(NEWO, n)
out = lambda rel: os.path.join(ROOT, rel)
rep = []

def trim(im, pad=0.03):
    a = im.getchannel('A').point(lambda v: 255 if v > 12 else 0)
    x0, y0, x1, y1 = a.getbbox()
    px, py = int((x1 - x0) * pad), int((y1 - y0) * pad)
    return im.crop((max(0, x0 - px), max(0, y0 - py), min(im.width, x1 + px), min(im.height, y1 + py)))

def save_alpha(im, rel, max_w=1200):
    if im.width > max_w: im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(out(rel), 'WEBP', quality=88, method=6, exact=False)
    rep.append((rel, im.size))

# ---------- latas transparentes (2 por arquivo: esquerda clássica, direita com gotas)
for n, slug in [(1, 'acai-guarana'), (2, 'pessego-gengibre'), (3, 'uva-rose'), (4, 'laranja-bahia'), (5, 'limao-hortela')]:
    im = ImageOps.exif_transpose(Image.open(O(f'latas-{n}.png'))).convert('RGBA')
    a = im.getchannel('A').load()
    w, h = im.size
    cols = [sum(1 for y in range(0, h, 3) if a[x, y] > 40) for x in range(w)]
    thr = max(cols) * 0.15
    runs, cur = [], None
    for x, v in enumerate(cols + [0]):
        if v > thr and cur is None: cur = x
        if v <= thr and cur is not None:
            if x - cur > w * 0.1: runs.append((cur, x))
            cur = None
    runs = sorted(sorted(runs, key=lambda r: r[1] - r[0], reverse=True)[:2])
    assert len(runs) == 2, (n, runs)
    for (x0, x1), variant in zip(runs, ['-classica', '']):
        can = trim(im.crop((max(0, x0 - 6), 0, min(w, x1 + 6), h)), 0.04)
        # tela 1:2 transparente, lata centralizada
        H = max(can.height, can.width * 2); W = H // 2
        canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        canvas.paste(can, ((W - can.width) // 2, (H - can.height) // 2), can)
        save_alpha(canvas, f'latas/lata-{slug}{variant}.webp', 700)

# ---------- lata + frutas recortadas
for n, slug in [(1, 'acai-guarana'), (2, 'uva-rose'), (3, 'limao-hortela'), (4, 'pessego-gengibre'), (5, 'laranja-bahia')]:
    im = trim(ImageOps.exif_transpose(Image.open(O(f'{n}.png'))).convert('RGBA'), 0.02)
    save_alpha(im, f'sabores/{slug}-recorte.webp', 1400)

# lata Uva Rosé avulsa (banner premium da Home)
im = trim(ImageOps.exif_transpose(Image.open(O('Design sem nome (3).png'))).convert('RGBA'), 0.03)
save_alpha(im, 'sabores/uva-rose-lata-premium.webp', 700)

# ---------- fotos
def photo(name, rel, max_w=1200):
    im = ImageOps.exif_transpose(Image.open(O(name))).convert('RGB')
    if im.width > max_w: im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(out(rel), 'WEBP', quality=80, method=6); rep.append((rel, im.size))

photo('IMG_1022.JPG', 'historia/fundadoras-2018.webp')
photo('IMG_1017.JPG', 'onde-encontrar/festival-mulher.webp')
photo('IMG_1024.JPG', 'historia/plantio-vista-alto.webp')
photo('8e4c94b606b46e02705a5a0cae61a9b0.jpg', 'historia/pessegos-pelotas.webp')
photo('IMG_1023.JPG', 'historia/colheita-acai.webp')
photo('IMG_1013.JPG', 'comunidade/lovers-13.webp')
photo('IMG_1016.JPG', 'comunidade/lovers-14.webp')
photo('IMG_1021.JPG', 'comunidade/lovers-15.webp')
for r in rep: print(r)
