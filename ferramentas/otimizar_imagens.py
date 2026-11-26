"""Etapa 2: move originais para /originais, gera WebP otimizados com nomes de slot."""
import os, shutil
from PIL import Image, ImageOps

ROOT = '/home/user/frizza-site/assets/img'
ORIG = os.path.join(ROOT, 'originais')
os.makedirs(ORIG, exist_ok=True)

# move todas as imagens soltas (exceto logos que geramos) para /originais
for f in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, f)
    if os.path.isfile(p) and not f.endswith('.md') and not f.startswith('logo-frizza'):
        shutil.move(p, os.path.join(ORIG, f))

def src(name): return os.path.join(ORIG, name)
def out(rel):
    p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True); return p

def save_webp(im, rel, max_w=1200, q=80):
    im = ImageOps.exif_transpose(im).convert('RGB')
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(out(rel), 'WEBP', quality=q, method=6)
    return im.size

report = []
def photo(name, rel, max_w=1200):
    size = save_webp(Image.open(src(name)), rel, max_w)
    report.append((name, rel, size))

# ---------- latas: cada arquivo tem 2 latas; separa esquerda (clássica) e direita (com gotas)
def split_cans(name, slug):
    im = ImageOps.exif_transpose(Image.open(src(name))).convert('RGB')
    w, h = im.size
    g = im.convert('L')
    px = g.load()
    # coluna "ocupada" = tem pixels bem mais escuros que o fundo claro na faixa central
    cols = []
    for x in range(w):
        dark = sum(1 for y in range(int(h * .2), int(h * .7), 4) if px[x, y] < 205)
        cols.append(dark)
    thr = max(cols) * 0.25
    runs, cur = [], None
    for x, v in enumerate(cols):
        if v > thr and cur is None: cur = x
        if v <= thr and cur is not None:
            if x - cur > w * 0.12: runs.append((cur, x))
            cur = None
    if cur is not None: runs.append((cur, w))
    assert len(runs) >= 2, (name, runs)
    runs = sorted(runs, key=lambda r: r[1] - r[0], reverse=True)[:2]
    runs.sort()
    for (x0, x1), variant in zip(runs, ['-classica', '']):
        cw = x1 - x0
        cx = (x0 + x1) / 2
        bw = cw * 1.22
        bh = min(h, bw * 2)
        bw = bh / 2
        top = max(0, min(h - bh, h * 0.5 - bh * 0.5 + h * 0.02))
        box = (int(max(0, cx - bw / 2)), int(top), int(min(w, cx + bw / 2)), int(top + bh))
        crop = im.crop(box)
        rel = f'latas/lata-{slug}{variant}.webp'
        crop.save(out(rel), 'WEBP', quality=85, method=6)
        report.append((name, rel, crop.size))

split_cans('IMG_0963.PNG', 'laranja-bahia')
split_cans('IMG_0962.PNG', 'acai-guarana')
split_cans('IMG_0964.PNG', 'limao-hortela')
split_cans('IMG_0965.PNG', 'pessego-gengibre')
split_cans('IMG_0961.PNG', 'uva-rose')

# ---------- sabores
photo('PHOTO-2026-11-26-01-35-36 2.jpg', 'sabores/laranja-bahia-destaque.webp', 2000)
photo('PHOTO-2026-11-26-01-35-36.jpg', 'sabores/acai-guarana-destaque.webp', 2000)
photo('PHOTO-2026-11-26-01-29-00.jpg', 'sabores/limao-hortela-destaque.webp', 2000)
photo('PHOTO-2026-11-26-01-28-34.jpg', 'sabores/pessego-gengibre-destaque.webp', 2000)
photo('PHOTO-2026-11-26-01-35-36 3.jpg', 'sabores/uva-rose-destaque.webp', 2000)
photo('IMG_0990.JPG', 'sabores/uva-rose-premium.webp')
photo('IMG_0989.JPG', 'sabores/ocasiao-uva-rose.webp')
photo('PHOTO-2026-11-26-00-41-47.jpg', 'sabores/ocasiao-laranja-bahia.webp')
photo('PHOTO-2026-11-26-00-13-53.jpg', 'sabores/ocasiao-acai-guarana.webp')
photo('0ae0c9c3-f0f3-4291-8e38-0b672375a195.jpg', 'sabores/ocasiao-limao-hortela.webp')
photo('6940ae8f-21f4-4a15-839d-32866ba492a4.jpg', 'sabores/ocasiao-pessego-gengibre.webp')

# ---------- história
photo('IMG_0987.JPG', 'historia/historia-hero.webp', 2000)
photo('IMG_0982.JPG', 'historia/horta-hortela-gramado.webp')
photo('IMG_0986.JPG', 'historia/produtores-laranja-reconcavo.webp')
photo('IMG_0983.JPG', 'historia/acai-colheita.webp')
photo('IMG_0988.JPG', 'historia/vinhedo-bento-goncalves.webp')
photo('IMG_0985.JPG', 'historia/ribeirinhos-acai.webp')
photo('IMG_0984.JPG', 'historia/rio-para-aerea.webp')
photo('IMG_0981.JPG', 'historia/mudas-arvores.webp')
photo('IMG_0980.JPG', 'historia/reciclagem-festival.webp')
photo('PHOTO-2026-11-26-00-42-46.jpg', 'historia/timeline-2020.webp')

# ---------- onde encontrar
photo('IMG_0979.JPG', 'onde-encontrar/festival-estande.webp')
photo('IMG_0993.JPG', 'onde-encontrar/emporio-prateleira.webp')

# ---------- comunidade
lovers = ['PHOTO-2026-11-26-00-02-14.jpg', '96949940-038c-455e-b7f6-46b1d07368d0.jpg', '06521286-bd8c-4004-b064-864896f46747.jpg',
          'PHOTO-2026-11-26-00-13-53.jpg', '0ae0c9c3-f0f3-4291-8e38-0b672375a195.jpg', 'PHOTO-2026-11-26-00-23-33.jpg',
          'PHOTO-2026-11-25-23-48-28.jpg', '1c513a88-f6bf-4ba9-af79-784c6a3feb57.jpg', 'PHOTO-2026-11-26-00-44-35.jpg',
          'PHOTO-2026-11-26-00-23-15.jpg', 'PHOTO-2026-11-26-00-32-27.jpg', 'PHOTO-2026-11-26-00-04-59.jpg']
for i, n in enumerate(lovers, 1):
    photo(n, f'comunidade/lovers-{i:02d}.webp')
for i, n in enumerate(['PHOTO-2026-11-26-00-41-47.jpg', 'PHOTO-2026-11-26-00-47-50.jpg', 'Gemini_Generated_Image_kifml0kifml0kifm.jpg', '6940ae8f-21f4-4a15-839d-32866ba492a4.jpg'], 1):
    im = ImageOps.exif_transpose(Image.open(src(n))).convert('RGB')
    s = min(im.size); im = im.crop(((im.width - s) // 2, int((im.height - s) * .3), (im.width - s) // 2 + s, int((im.height - s) * .3) + s))
    save_webp(im, f'comunidade/polaroid-{i:02d}.webp', 500); report.append((n, f'comunidade/polaroid-{i:02d}.webp', (500, 500)))
photo('PHOTO-2026-11-26-00-11-58.jpg', 'comunidade/contato-hero.webp')

# ---------- marca
os.makedirs(out('marca/x').rsplit('/', 1)[0], exist_ok=True)
for lg in ['logo-frizza.png', 'logo-frizza-branco.png']:
    if os.path.exists(os.path.join(ROOT, lg)): shutil.move(os.path.join(ROOT, lg), out('marca/' + lg))
fav = ImageOps.exif_transpose(Image.open(src('IMG_0992.JPG'))).convert('RGB')
# recorta o quadrado laranja do ícone
g = fav.convert('L'); bw = g.point(lambda v: 255 if v < 235 else 0); bbox = bw.getbbox()
fav = fav.crop(bbox)
s = max(fav.size); sq = Image.new('RGB', (s, s), (255, 255, 255)); sq.paste(fav, ((s - fav.width) // 2, (s - fav.height) // 2))
# cantos arredondados transparentes
mask = Image.new('L', (s, s), 0)
from PIL import ImageDraw
ImageDraw.Draw(mask).rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * .22), fill=255)
icon = sq.convert('RGBA'); icon.putalpha(mask)
for size, name in [(512, 'favicon.png'), (180, 'apple-touch-icon.png'), (32, 'favicon-32.png')]:
    icon.resize((size, size), Image.LANCZOS).save(out('marca/' + name), optimize=True)
report.append(('IMG_0992.JPG', 'marca/favicon.png (+180, +32)', (512, 512)))
og = ImageOps.exif_transpose(Image.open(src('PHOTO-2026-11-26-01-35-36 2.jpg'))).convert('RGB')
r = 1200 / 630; w, h = og.size; nh = int(w / r); og = og.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh)).resize((1200, 630), Image.LANCZOS)
og.save(out('marca/og-frizza.jpg'), 'JPEG', quality=82, optimize=True)
report.append(('PHOTO-…01-35-36 2.jpg', 'marca/og-frizza.jpg', (1200, 630)))

for a, b, c in report: print(f'{a[:42]:42s} -> {b:48s} {c[0]}x{c[1]}')
tot_o = sum(os.path.getsize(os.path.join(ORIG, f)) for f in os.listdir(ORIG))
tot_n = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(ROOT) if 'originais' not in dp for f in fs if not f.endswith(('.md', '.svg')))
print(f'originais: {tot_o/1e6:.1f} MB | otimizadas: {tot_n/1e6:.1f} MB')
