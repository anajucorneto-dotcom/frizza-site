#!/usr/bin/env python3
"""Gera as páginas estáticas do site FRIZZA (header/footer compartilhados)
e o assets/img/README.md com a lista de todas as imagens usadas."""
import math, os, re, sys, html as H
from collections import OrderedDict

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
ICON_DIR = os.path.join(ROOT, 'assets/icons')

# ---------------------------------------------------------------- helpers
ICONS = {}
for f in os.listdir(ICON_DIR):
    if f.endswith('.svg') and f != 'favicon.svg':
        ICONS[f[:-4]] = open(os.path.join(ICON_DIR, f)).read().strip().replace(
            '<svg ', '<svg focusable="false" ')

def icon(name, cls=''):
    return f'<span class="icon icon--{name} {cls}" aria-hidden="true">{ICONS[name]}</span>'

def esc(s):
    return H.escape(s, quote=True)

def ratio(w, h):
    g = math.gcd(w, h)
    return f'{w//g} / {h//g}'

IMAGES = OrderedDict()   # arquivo -> dados para o README
CURRENT_PAGE = ['']

def register(file, w, h, alt, desc, section, kind, once=False):
    if once and file in IMAGES: return
    item = IMAGES.setdefault(file, dict(w=w, h=h, alt=alt, desc=desc, kind=kind, uses=[]))
    use = f'{CURRENT_PAGE[0]} → {section}'
    if use not in item['uses']:
        item['uses'].append(use)

IMG_DIR = os.path.join(ROOT, 'assets/img')
_dims = {}
def img_exists(rel): return os.path.exists(os.path.join(IMG_DIR, rel))
def img_dims(rel):
    if rel not in _dims:
        if rel.endswith('.svg'):
            m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', open(os.path.join(IMG_DIR, rel)).read())
            _dims[rel] = (int(float(m.group(1))), int(float(m.group(2)))) if m else (120, 120)
        else:
            from PIL import Image as _I
            _dims[rel] = _I.open(os.path.join(IMG_DIR, rel)).size
    return _dims[rel]

_alpha = {}
def img_has_alpha(rel):
    if rel not in _alpha:
        if rel.endswith('.svg'): _alpha[rel] = True
        else:
            from PIL import Image as _I
            im = _I.open(os.path.join(IMG_DIR, rel))
            _alpha[rel] = im.mode in ('RGBA', 'LA') and im.getchannel('A').getextrema()[0] < 250
    return _alpha[rel]

def img_tag(rel, alt, cls='', pos=None, eager=False, high=False, decorative=False):
    w, h = img_dims(rel)
    a = ' alt="" aria-hidden="true"' if decorative else f' alt="{esc(alt)}"'
    st = f' style="object-position:{pos}"' if pos else ''
    ld = (' fetchpriority="high"' if high else '') if eager else ' loading="lazy"'
    c = f' class="{cls}"' if cls else ''
    return f'<img src="assets/img/{rel}"{a}{c} width="{w}" height="{h}" decoding="async"{ld}{st}>'

def slot(file, w, h, alt, desc, section, cls='', color=None, style='', reveal=None, pos=None, eager=False, high=False, parallax=False, decorative=False):
    register(file, w, h, alt, desc, section, 'foto')
    st = f'--ar:{ratio(w, h)};'
    if color: st += f'--slot-c:{color};'
    st += style
    rv = f' data-reveal="{reveal}"' if reveal else ''
    if img_exists(file):
        par = ' is-parallax' if parallax else ''
        return (f'<div class="img-slot has-img is-loaded{par} {cls}" style="{st}"{rv}>'
                f'{img_tag(file, alt, pos=pos, eager=eager, high=high, decorative=decorative)}</div>')
    return (f'<div class="img-slot {cls}" style="{st}" data-img-pendente="assets/img/{file}" role="img" aria-label="{esc(alt)}"{rv}>'
            f'<div class="img-slot__ph" aria-hidden="true">{icon("image")}'
            f'<span class="img-slot__label">{file}<br>{w}×{h} px</span></div></div>')

def can(f, section, label=True, extra_cls='', variant='', eager=False, high=False):
    file = f'latas/lata-{f["slug"]}{variant}.webp'
    register(file, 800, 1600, f'Lata de FRIZZA {f["name"]}',
             f'Lata de 350 ml da FRIZZA {f["name"]} de frente, com gotas de condensação, rótulo na cor {f["color"]}. '
             f'Ideal: PNG com fundo transparente (recorte limpo, sem sombra) para flutuar e girar nas animações.',
             section, 'png')
    if img_exists(file):
        kind = 'is-cutout' if img_has_alpha(file) else 'is-photo'
        return (f'<div class="png-slot can-slot {kind} is-loaded {extra_cls}" style="--ar:1 / 2">'
                f'{img_tag(file, f"Lata de FRIZZA {f[chr(110)+chr(97)+chr(109)+chr(101)]}", eager=eager, high=high)}</div>')
    light = ' can--light' if f.get('can_light') else ''
    lab = f'<span class="png-slot__label" aria-hidden="true">{file}<br>800×1600 px</span>' if label else ''
    return (f'<div class="png-slot can-slot {extra_cls}" style="--ar:1 / 2" data-img="assets/img/{file}" role="img" aria-label="Lata de FRIZZA {esc(f["name"])}">'
            f'<div class="can{light}" style="--can:{f["color"]}" aria-hidden="true"><div class="can__body"><div class="can__label">'
            f'<img class="can__logo" src="assets/img/marca/{"logo-frizza.png" if f.get("can_light") else "logo-frizza-branco.png"}" alt="" loading="lazy" decoding="async"><span class="can__flavor">{f["short"]}</span></div></div></div>{lab}</div>')

def destaque(f, section, cls='', eager=False, high=False, ar='4 / 5', pos='86% 50%'):
    """Foto 'lata + frutas' do sabor (usa o recorte transparente quando existir)."""
    cut = f'sabores/{f["slug"]}-recorte.webp'
    if img_exists(cut):
        register(cut, 1100, 740, f'Lata de FRIZZA {f["name"]} com as frutas do sabor (recorte)', '', section, 'png')
        w, h = img_dims(cut)
        alt_txt = f'Lata de FRIZZA {f["name"]} cercada das frutas do sabor, com respingos e gelo'
        return (f'<div class="img-slot has-img is-loaded is-cutout {cls}" style="--ar:{w} / {h}">'
                f'{img_tag(cut, alt_txt, eager=eager, high=high)}</div>')
    rel = f'sabores/{f["slug"]}-destaque.webp'
    register(rel, 1376, 768, f'Lata de FRIZZA {f["name"]} cercada de frutas e respingos', f'Lata da FRIZZA {f["name"]} com as frutas do sabor, respingos e gelo sobre fundo na cor do sabor.', section, 'foto')
    return (f'<div class="img-slot has-img is-loaded photo-frame {cls}" style="--ar:{ar}">'
            f'{img_tag(rel, f"Lata de FRIZZA {f[chr(110)+chr(97)+chr(109)+chr(101)]} cercada das frutas do sabor, com respingos e gelo", pos=pos, eager=eager, high=high)}</div>')

FRUITS = {
    'fruta-laranja-fatia.png': ('Fatia de laranja bahia suculenta', '#FF9A3C', 'Fatia redonda de laranja bahia, bem suculenta, com gotas de água, vista de cima, PNG com fundo transparente.'),
    'fruta-tangerina.png': ('Tangerina com folhinha', '#FFA62B', 'Tangerina inteira com uma folha verde no cabinho, gotas frescas, PNG com fundo transparente.'),
    'fruta-acai.png': ('Cacho de açaí', '#3B1748', 'Pequeno cacho de frutos de açaí roxo-escuros e brilhantes, PNG com fundo transparente.'),
    'fruta-guarana.png': ('Fruto do guaraná aberto', '#C0392B', 'Frutos de guaraná vermelhos abertos mostrando a semente preta e branca ("olho"), PNG com fundo transparente.'),
    'fruta-limao-siciliano.png': ('Limão siciliano cortado ao meio', '#F4E04D', 'Limão siciliano cortado ao meio, polpa amarela brilhante com gotas, PNG com fundo transparente.'),
    'folha-hortela.png': ('Ramo de hortelã fresca', None, 'Ramo de hortelã fresca bem verde com gotas de água, PNG com fundo transparente.'),
    'fruta-pessego.png': ('Pêssego maduro', '#FFAB76', 'Pêssego maduro inteiro, pele aveludada laranja-rosada, com uma folha, PNG com fundo transparente.'),
    'gengibre.png': ('Raiz de gengibre fatiada', '#D9A55B', 'Raiz de gengibre in natura com duas fatias cortadas, PNG com fundo transparente.'),
    'fruta-uva-rose.png': ('Cacho de uva rosé', '#E8A0BF', 'Cacho pequeno de uvas rosadas translúcidas com gotas de orvalho, PNG com fundo transparente.'),
    'petala-rosa.png': ('Pétalas de rosa', '#F3B8CF', 'Três pétalas de rosa cor-de-rosa clarinho, delicadas, PNG com fundo transparente.'),
    'folha-videira.png': ('Folha de videira', None, 'Folha de videira verde com nervuras visíveis, PNG com fundo transparente.'),
    'folha-tropical.png': ('Folha tropical', None, 'Folha tropical (costela-de-adão ou palmeira) verde vibrante, PNG com fundo transparente.'),
    'gelo.png': ('Cubo de gelo', '#DFF6FF', 'Cubo de gelo.'),
}

def fruit(file, section, label=True, eager=False):
    """Elemento solto decorativo (SVG em assets/img/elementos/)."""
    rel = 'elementos/' + file.replace('.png', '.svg')
    alt, color, desc = FRUITS[file]
    if img_exists(rel):
        register(rel, 120, 120, '(decorativo)', f'Ilustração SVG: {alt.lower()}', section, 'svg')
        return f'<div class="png-slot fruit is-svg is-loaded" style="--ar:1 / 1">{img_tag(rel, "", eager=eager, decorative=True)}</div>'
    register(file, 600, 600, alt, desc, section, 'png')
    st = '--ar:1 / 1;' + (f'--fruit:{color};' if color else '')
    return f'<div class="png-slot fruit" style="{st}" aria-hidden="true"><span class="png-slot__shape"></span></div>'

def btn(text, href, variant='primary', ic=None, size='', attrs='', magnetic=True, ic_first=False):
    mg = ' data-magnetic' if magnetic else ''
    i = icon(ic, 'icon--arrow' if ic == 'arrow' else '') if ic else ''
    inner = f'{i}<span>{text}</span>' if ic_first else f'<span>{text}</span>{i}'
    return (f'<a class="btn btn--{variant} {size}" href="{href}"{mg} {attrs}>{inner}'
            f'<span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></a>')

WAVE_PATH = 'M0,60 C240,0 480,0 720,60 C960,120 1200,120 1440,60 C1680,0 1920,0 2160,60 C2400,120 2640,120 2880,60 L2880,120 L0,120 Z'
def wave(fill, slow=False):
    return (f'<div class="wave wave--bottom{" wave--slow" if slow else ""}" style="--wave-fill:{fill}" aria-hidden="true">'
            f'<svg viewBox="0 0 2880 120" preserveAspectRatio="none"><path d="{WAVE_PATH}"/></svg></div>')

def bubbles_canvas(count=34, color=None, mode='bubbles'):
    c = f' data-color="{color}"' if color else ''
    return f'<canvas class="bubbles-canvas" data-bubbles="{mode}" data-count="{count}"{c} aria-hidden="true"></canvas>'

def seal(uid, ring_text, mid, sub, bg, fg, label, mid_size=34):
    return (f'<div class="seal"><svg viewBox="0 0 200 200" role="img" aria-label="{esc(label)}">'
            f'<circle cx="100" cy="100" r="97" fill="{bg}"/>'
            f'<circle cx="100" cy="100" r="62" fill="none" stroke="{fg}" stroke-width="1.5" stroke-dasharray="2 5"/>'
            f'<g class="seal__ring"><path id="seal-{uid}" d="M100,100 m-78,0 a78,78 0 1,1 156,0 a78,78 0 1,1 -156,0" fill="none"/>'
            f'<text fill="{fg}" font-family="Fredoka, sans-serif" font-weight="700" font-size="15" letter-spacing="2">'
            f'<textPath href="#seal-{uid}" textLength="480" lengthAdjust="spacing">{ring_text}</textPath></text></g>'
            f'<path d="M100 52 l3.5 7 7.7 1.1-5.6 5.4 1.3 7.7-6.9-3.6-6.9 3.6 1.3-7.7-5.6-5.4 7.7-1.1z" fill="{fg}"/>'
            f'<text x="100" y="{112 if mid_size>30 else 108}" text-anchor="middle" fill="{fg}" font-family="Fredoka, sans-serif" font-weight="700" font-size="{mid_size}">{mid}</text>'
            f'<text x="100" y="134" text-anchor="middle" fill="{fg}" font-family="Poppins, sans-serif" font-weight="700" font-size="12">{sub}</text>'
            f'</svg></div>')

SEALS = [
    dict(uid='organico', ring='MELHOR REFRIGERANTE ARTESANAL • FEIRA BRASIL ORGÂNICO •', mid='2023', sub='Brasil Orgânico', bg='#FFD23F', fg='#1A1A2E',
         label='Selo: Melhor Refrigerante Artesanal, Feira Brasil Orgânico 2023', title='Melhor Refrigerante Artesanal', text='Feira Brasil Orgânico 2023'),
    dict(uid='pegn', ring='TOP 10 MARCAS SUSTENTÁVEIS • REVISTA PEGN • 2024 •', mid='TOP 10', sub='PEGN 2024', bg='#2EC4B6', fg='#1A1A2E',
         label='Selo: Top 10 Marcas Sustentáveis, Revista PEGN 2024', title='Top 10 Marcas Sustentáveis', text='Revista PEGN 2024', mid_size=30),
    dict(uid='bcorp', ring='EMPRESA B CERTIFICADA • B CORP • IMPACTO POSITIVO •', mid='B', sub='Empresa B', bg='#FAFAFA', fg='#1A1A2E',
         label='Selo: Empresa B certificada (B Corp)', title='Selo Empresa B', text='Certificação B Corp', mid_size=44),
]

def seal_from(s, suffix=''):
    return seal(s['uid'] + suffix, s['ring'], s['mid'], s['sub'], s['bg'], s['fg'], s['label'], s.get('mid_size', 34))

# ---------------------------------------------------------------- dados dos sabores
FLAVORS = [
    dict(slug='laranja-bahia', name='Laranja Bahia', short='Laranja Bahia', color='#FF8C42', fg='#1A1A2E', num='01',
         badge='Carro-chefe', slogan='O sol da Bahia em cada gole', cats='citricos', cat_label='Cítrico',
         big='LARANJA',
         desc='Laranja bahia com um toque de tangerina, colhida por pequenos produtores do Recôncavo Baiano. Doce na medida, com aquela acidez natural que dá vontade de mais um gole.',
         card='Laranja com toque de tangerina. O clássico que virou xodó.',
         facts=[('sun', 'Laranja do Recôncavo'), ('drop', '40% menos açúcar'), ('bubbles', 'Gás médio')],
         fruits=['fruta-laranja-fatia.png', 'fruta-tangerina.png', 'folha-tropical.png', 'fruta-laranja-fatia.png'],
         sensory=[('aroma', 'Aroma', 'Cítrico e envolvente, como abrir uma laranja recém-colhida na feira.', 'Intensidade', 4),
                  ('taste', 'Sabor', 'Doce equilibrado com leve acidez natural. Refrescante do primeiro ao último gole.', 'Doçura', 3),
                  ('bubbles', 'Carbonatação', 'Média: borbulha o suficiente para animar, sem pinicar demais.', 'Gás', 3)],
         ingredients=[('Água gaseificada', 76.5, True), ('Suco natural de laranja bahia', 12, False), ('Suco de tangerina', 3, False),
                      ('Açúcar demerara orgânico', 8, True), ('Acidulante natural', 0.5, True)],
         ring=(12, 'de suco de laranja bahia'),
         diffs=['Laranjas de pequenos produtores do Recôncavo Baiano, com preço justo.',
                '40% menos açúcar que refrigerantes de laranja tradicionais.',
                'Sem corantes nem aromas artificiais: a cor vem da própria fruta.',
                'O sabor mais vendido da FRIZZA desde o primeiro lote, em 2018.'],
         occasion=('Para todo mundo, todo dia', 'Almoço de domingo em família, praia, piquenique no parque ou aquela marmita que precisa de um upgrade. É o FRIZZA que agrada da criança à avó.'),
         occ_desc='Família reunida em um piquenique ao ar livre num parque ensolarado, toalha xadrez, frutas cortadas, pessoas de várias idades e etnias sorrindo e brindando com latas laranja da FRIZZA Laranja Bahia. Luz natural de fim de tarde, cores vivas e saturadas.',
         nutri=dict(kcal=92, carb=23, sug=22, add=14, prot=0, fat=0, fib=0, sod=12), highlight=('40%', 'menos açúcar que refri de laranja tradicional')),
    dict(slug='acai-guarana', name='Açaí com Guaraná', short='Açaí + Guaraná', color='#5B2C6F', fg='#FFFFFF', num='02',
         badge='Energia natural', slogan='A energia da Amazônia na sua mão', cats='energia', cat_label='Energia',
         big='AÇAÍ', header_light=True,
         desc='Dois superalimentos amazônicos na mesma lata: polpa de açaí e extrato natural de guaraná, com cafeína natural equivalente a meio espresso. Energia de verdade, sem nada sintético.',
         card='Açaí + guaraná: energia natural, direto da Amazônia.',
         facts=[('flame', 'Cafeína natural'), ('leaf', 'Rico em antioxidantes'), ('bubbles', 'Gás suave')],
         fruits=['fruta-acai.png', 'fruta-guarana.png', 'folha-tropical.png', 'fruta-acai.png'],
         sensory=[('aroma', 'Aroma', 'Frutado e terroso, com aquele fundinho de floresta que só o açaí tem.', 'Intensidade', 3),
                  ('taste', 'Sabor', 'Encorpado, com leve amargor do guaraná no final. Cor roxa hipnotizante.', 'Corpo', 5),
                  ('bubbles', 'Carbonatação', 'Suave: bolhas delicadas que deixam o sabor encorpado aparecer.', 'Gás', 2)],
         ingredients=[('Água gaseificada', 79.5, True), ('Polpa de açaí', 10, False), ('Extrato natural de guaraná', 2, False),
                      ('Açúcar demerara orgânico', 8, True), ('Corante natural de antocianina', 0.5, True)],
         ring=(10, 'de polpa de açaí'),
         diffs=['Parceria com cooperativas ribeirinhas do Pará, que vivem da floresta em pé.',
                'Cafeína natural do guaraná: o equivalente a meio espresso por lata.',
                'Rico em antioxidantes graças ao açaí e à antocianina natural.',
                'O preferido de quem tem entre 18 e 25 anos e quer energia sem química.'],
         occasion=('Para o rolê e a maratona de estudos', 'Pré-treino, tarde de estudos, festival de música ou aquele pôr do sol no parque com os amigos. Energia que vem da fruta.'),
         occ_desc='Grupo de jovens de 18 a 25 anos, diversos, sentados na grama de um festival de música ao ar livre ao pôr do sol, rindo e segurando latas roxas da FRIZZA Açaí com Guaraná. Luz dourada, cores vivas, clima de energia e liberdade.',
         nutri=dict(kcal=98, carb=24, sug=21, add=15, prot=0.5, fat=0, fib=1, sod=10, caf=40), highlight=('½', 'espresso de cafeína natural por lata')),
    dict(slug='limao-hortela', name='Limão com Hortelã', short='Limão + Hortelã', color='#00BFA6', fg='#1A1A2E', num='03',
         badge='O mais leve', slogan='Refresca a alma', cats='citricos', cat_label='Cítrico',
         big='LIMÃO',
         desc='Limão siciliano com hortelã fresca da nossa horta em Gramado. O mais refrescante e o mais leve da linha: só 45 kcal por lata. Perfeito com comida e como base de mocktails.',
         card='Limão siciliano + hortelã fresca. Só 45 kcal.',
         facts=[('leaf', 'Hortelã da horta própria'), ('drop', '45 kcal por lata'), ('bubbles', 'Gás alto')],
         fruits=['fruta-limao-siciliano.png', 'folha-hortela.png', 'folha-hortela.png', 'fruta-limao-siciliano.png'],
         sensory=[('aroma', 'Aroma', 'Mentolado e vibrante, com um fundo cítrico que acorda qualquer um.', 'Intensidade', 5),
                  ('taste', 'Sabor', 'Extremamente refrescante, com acidez elegante e finalização limpa.', 'Frescor', 5),
                  ('bubbles', 'Carbonatação', 'Alta: bolhas vivas que estalam e limpam o paladar.', 'Gás', 5)],
         ingredients=[('Água gaseificada', 86, True), ('Suco natural de limão siciliano', 8, False), ('Extrato de hortelã', 1.5, False),
                      ('Açúcar demerara orgânico', 4, True), ('Acidulante natural', 0.5, True)],
         ring=(8, 'de suco de limão siciliano'),
         diffs=['Hortelã cultivada na nossa própria horta, em Gramado (RS).',
                'O mais leve da linha: apenas 45 kcal por lata.',
                'Harmoniza com comida e é base perfeita para mocktails.',
                'Queridinho de quem tem de 25 a 35 anos e ama gastronomia.'],
         occasion=('Para harmonizar e inventar drinks', 'Com um prato caprichado, no happy hour sem álcool ou como base de mocktail com gelo, fatias de limão e mais hortelã.'),
         occ_desc='Mesa de restaurante ao ar livre numa varanda iluminada por luz natural, prato colorido de comida brasileira contemporânea e um copo de mocktail com gelo, limão siciliano e hortelã ao lado de uma lata verde-água da FRIZZA Limão com Hortelã. Pessoas de 25 a 35 anos conversando ao fundo, desfocadas.',
         nutri=dict(kcal=45, carb=11, sug=10, add=8, prot=0, fat=0, fib=0, sod=8), highlight=('45', 'kcal por lata: o mais leve da linha')),
    dict(slug='pessego-gengibre', name='Pêssego com Gengibre', short='Pêssego + Gengibre', color='#FFAB76', fg='#1A1A2E', num='04',
         badge='Gourmet', slogan='Doçura com atitude', cats='gourmet', cat_label='Gourmet', can_light=True,
         big='PÊSSEGO',
         desc='Pêssego maduro com gengibre in natura. O primeiro gole é doce e aveludado; logo depois vem um calorzinho do gengibre na garganta. O mais gourmet da linha, para paladares aventureiros.',
         card='Pêssego aveludado com calorzinho de gengibre.',
         facts=[('sparkle', 'O mais gourmet'), ('leaf', 'Gengibre in natura'), ('bubbles', 'Gás médio')],
         fruits=['fruta-pessego.png', 'gengibre.png', 'folha-tropical.png', 'fruta-pessego.png'],
         sensory=[('aroma', 'Aroma', 'Adocicado de pêssego maduro, daqueles que perfumam a fruteira inteira.', 'Intensidade', 4),
                  ('taste', 'Sabor', 'Doce e aveludado no início, evoluindo para um leve calor do gengibre.', 'Complexidade', 5),
                  ('bubbles', 'Carbonatação', 'Média: equilibra a doçura e destaca o picante do gengibre.', 'Gás', 3)],
         ingredients=[('Água gaseificada', 80.5, True), ('Polpa de pêssego', 11, False), ('Extrato natural de gengibre', 1, False),
                      ('Açúcar demerara orgânico', 7, True), ('Aroma natural', 0.5, True)],
         ring=(11, 'de polpa de pêssego'),
         diffs=['Gengibre in natura, com propriedades digestivas e anti-inflamatórias.',
                'Zero aromas artificiais: só fruta, raiz e açúcar demerara.',
                'Experiência complexa e sofisticada, que muda a cada gole.',
                'Feito para foodies de 25 a 35 anos com paladar aventureiro.'],
         occasion=('Para quem gosta de experimentar', 'Tábua de queijos, jantar entre amigos, brunch de domingo ou aquele momento de descobrir um sabor novo.'),
         occ_desc='Brunch ao ar livre numa varanda com plantas, mesa de madeira com tábua de queijos, pêssegos cortados e pão artesanal, duas pessoas de 25 a 35 anos brindando com latas pêssego da FRIZZA Pêssego com Gengibre. Luz natural da manhã, cores quentes e saturadas.',
         nutri=dict(kcal=86, carb=21, sug=19, add=13, prot=0, fat=0, fib=0, sod=10), highlight=('0', 'aromas artificiais')),
    dict(slug='uva-rose', name='Uva Rosé', short='Uva Rosé', color='#E8A0BF', fg='#1A1A2E', num='05',
         badge='Edição Especial', slogan='Para brindar sem precisar de motivo', cats='gourmet especial', cat_label='Edição Especial', can_light=True,
         big='ROSÉ', premium=True, header_light=True,
         full_name='Uva Rosé – Edição Especial Serra Gaúcha',
         desc='Uva rosé orgânica dos vinhedos de Bento Gonçalves com um sopro de água de rosas. Cor rosada translúcida, bolhas finas e persistentes estilo espumante. A alternativa elegante para brindar sem álcool.',
         card='Edição limitada da Serra Gaúcha, com bolhas de espumante.',
         facts=[('sparkle', 'Edição limitada'), ('glass', 'Sem álcool'), ('bubbles', 'Perlage fino')],
         fruits=['fruta-uva-rose.png', 'petala-rosa.png', 'folha-videira.png', 'petala-rosa.png'],
         sensory=[('aroma', 'Aroma', 'Floral delicado com fundo frutado, como um jardim depois da chuva.', 'Intensidade', 3),
                  ('taste', 'Sabor', 'Uva sofisticada com uma sutil nota de rosas no final.', 'Elegância', 5),
                  ('bubbles', 'Carbonatação', 'Fina e persistente, no estilo espumante.', 'Perlage', 4)],
         ingredients=[('Água gaseificada', 77, True), ('Suco de uva rosé orgânica', 15, False), ('Água de rosas', 0.5, False),
                      ('Açúcar demerara orgânico', 7, True), ('Acidulante natural', 0.5, True)],
         ring=(15, 'de suco de uva rosé: o maior da linha'),
         diffs=['Edição limitada em parceria com vinícolas de Bento Gonçalves (RS).',
                'Uvas de vinhedos orgânicos e o maior percentual de fruta da linha (15%).',
                'Embalagem colecionável que muda a cada safra.',
                'Alternativa elegante para quem não bebe álcool, ou prefere não beber hoje.'],
         occasion=('Para as ocasiões especiais (e as nem tanto)', 'Aniversários, ceias, casamentos, conquistas pequenas e grandes. Ou uma terça-feira qualquer que merece um brinde.'),
         occ_desc='Celebração elegante ao ar livre num vinhedo da Serra Gaúcha ao entardecer, mesa com toalha de linho, taças de cristal com bebida rosada borbulhante e latas rosé da FRIZZA Uva Rosé, amigos diversos brindando. Luz dourada suave, tons rosé e dourado, clima sofisticado e acolhedor.',
         nutri=dict(kcal=104, carb=26, sug=24, add=12, prot=0, fat=0, fib=0, sod=9), highlight=('0%', 'álcool, 100% celebração')),
]
FMAP = {f['slug']: f for f in FLAVORS}
PRICES = {'laranja-bahia': 9.9, 'acai-guarana': 10.9, 'limao-hortela': 9.9, 'pessego-gengibre': 10.9, 'uva-rose': 13.9}
for _f in FLAVORS: _f['price'] = PRICES[_f['slug']]
def brl(v): return 'R$ ' + f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def cart_attrs(f):
    return (f'data-add-cart data-id="{f["slug"]}" data-name="FRIZZA {esc(f["name"])}" data-price="{f["price"]:.2f}" '
            f'data-color="{f["color"]}" data-cart-img="assets/img/latas/lata-{f["slug"]}.webp" data-url="sabor-{f["slug"]}.html"')
def cart_btn(f, variant='primary', size='', label='Adicionar ao carrinho', magnetic=True):
    mg = ' data-magnetic' if magnetic else ''
    return (f'<button class="btn btn--{variant} {size}" type="button" {cart_attrs(f)}{mg} aria-label="Adicionar FRIZZA {esc(f["name"])} ao carrinho, {brl(f["price"])}">'
            f'{icon("cart")}<span data-cart-label>{label}</span><span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></button>')


# ---------------------------------------------------------------- partes comuns
NAV = [('index.html', 'Home'), ('sabores.html', 'Nossos Sabores'), ('historia.html', 'Nossa História'),
       ('onde-encontrar.html', 'Onde Encontrar'), ('frizzalovers.html', '#FRIZZALOVERS'), ('contato.html', 'Contato')]

SOCIAL = [('instagram', 'Instagram @frizzaoficial', 'https://www.instagram.com/frizzaoficial/'),
          ('tiktok', 'TikTok @frizzaoficial', 'https://www.tiktok.com/@frizzaoficial'),
          ('youtube', 'YouTube FRIZZA Refrigerantes', 'https://www.youtube.com/@frizzarefrigerantes'),
          ('linkedin', 'LinkedIn FRIZZA Bebidas', 'https://www.linkedin.com/company/frizza-bebidas')]
DEMO_SOCIAL = 'Perfil ilustrativo: a FRIZZA é uma marca fictícia criada para um projeto acadêmico.'
DEMO_SHOP = 'Loja ilustrativa: a FRIZZA é uma marca fictícia criada para um projeto acadêmico.'
DEMO_CONTACT = 'Contato ilustrativo: a FRIZZA é uma marca fictícia criada para um projeto acadêmico.'

def social_links(cls='social-links'):
    items = ''.join(f'<li><a href="{u}" aria-label="{esc(l)}" data-demo="{DEMO_SOCIAL}" target="_blank" rel="noopener">{icon(n)}</a></li>' for n, l, u in SOCIAL)
    return f'<ul class="{cls}" role="list">{items}</ul>'

def logo_word():
    return '<span class="logo-word" aria-hidden="true">FR<span class="logo-i">I<span class="logo-bubble"></span></span>ZZA</span>'

def logo_slot(file, extra=''):
    rel = 'marca/' + file
    register(rel, 796, 429, 'Logotipo FRIZZA', 'Logotipo FRIZZA (PNG transparente).', 'header e footer (todas as páginas)', 'png', once=True)
    return f'<span class="logo-slot is-loaded {extra}">{img_tag(rel, "", eager=True, decorative=True)}</span>'

def head(title, desc, theme_color, serif=False):
    fonts = 'family=Fredoka:wght@500;600;700&family=Poppins:ital,wght@0,400;0,700;1,400'
    register('marca/og-frizza.jpg', 1200, 630, 'FRIZZA Refrigerantes', 'Imagem de compartilhamento (Open Graph): as 5 latas FRIZZA lado a lado sobre fundo em gradiente tropical laranja e amarelo, com frutas e gotas, e o logo. Usada quando o link é compartilhado em redes sociais e WhatsApp.', 'meta Open Graph (todas as páginas)', 'foto', once=True)
    register('marca/favicon.png', 512, 512, 'Ícone FRIZZA', 'Favicon / ícone de app: símbolo da FRIZZA (letra F com bolha) sobre fundo laranja-amarelo, quadrado, PNG. Enquanto não existir, o site usa assets/icons/favicon.svg.', 'favicon (todas as páginas)', 'png', once=True)
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="{theme_color}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="FRIZZA Refrigerantes">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="assets/img/marca/og-frizza.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="assets/img/marca/favicon-32.png">
<link rel="icon" type="image/png" sizes="512x512" href="assets/img/marca/favicon.png">
<link rel="apple-touch-icon" href="assets/img/marca/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="assets/css/style.css?v=8">
<script>
/* Antes de pintar: define modo de animação, preloader (1ª visita) e cortina de transição */
(function(){{var d=document.documentElement,rm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;d.classList.add('js');if(!rm)d.classList.add('js-motion');try{{var pt=sessionStorage.getItem('frizza-pt');if(pt&&!rm){{d.classList.add('pt-enter');d.style.setProperty('--pt-color',pt);}}if(!sessionStorage.getItem('frizza-visited')&&!rm&&!pt)d.classList.add('has-preloader');}}catch(e){{}}setTimeout(function(){{if(!window.__frizzaReady)d.classList.remove('js-motion','pt-enter','has-preloader');}},4500);}})();
</script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/split-type@0.3.4/umd/index.min.js"></script>
<script defer src="assets/js/main.js?v=8"></script>
</head>'''

def preloader():
    import random
    random.seed(7)
    bub = ''.join(f'<span style="left:{random.randint(2,96)}%;width:{(s:=random.randint(10,46))}px;height:{s}px;animation-duration:{random.uniform(2.4,5.5):.2f}s;animation-delay:-{random.uniform(0,5):.2f}s;--dx:{random.randint(-40,40)}px"></span>' for _ in range(22))
    letters = '<img class="preloader__img" src="assets/img/marca/logo-frizza.png" alt="" width="796" height="429">'
    return (f'<div class="preloader" aria-hidden="true"><div class="preloader__bubbles">{bub}</div>'
            f'<div class="preloader__logo">{letters}</div>'
            f'<p class="preloader__text">Efervescendo…</p></div>')

def page_transition():
    wave_svg = f'<svg viewBox="0 0 2880 120" preserveAspectRatio="none"><path d="{WAVE_PATH}"/></svg>'
    bub = ''.join(f'<span style="left:{l}%;width:{s}px;height:{s}px;animation-delay:-{dl}s"></span>' for l, s, dl in
                  [(8, 26, .2), (22, 14, .9), (37, 34, .4), (51, 18, 1.2), (64, 28, .1), (78, 12, .7), (90, 30, 1.0)])
    return (f'<div class="page-transition" aria-hidden="true">'
            f'<div class="page-transition__wave page-transition__wave--top">{wave_svg}</div>'
            f'<div class="page-transition__fill"></div>'
            f'<div class="page-transition__wave page-transition__wave--bottom">{wave_svg}</div>'
            f'<div class="page-transition__bubbles">{bub}</div></div>')

def cart_drawer():
    return f'''<div class="cart-drawer" id="cart-drawer" aria-hidden="true">
  <div class="cart-drawer__overlay" data-close-cart></div>
  <aside class="cart-drawer__panel" role="dialog" aria-modal="true" aria-labelledby="cart-title">
    <header class="cart-drawer__head"><h2 id="cart-title">Seu carrinho</h2>
      <button class="cart-drawer__close" type="button" data-close-cart aria-label="Fechar carrinho">{icon("close")}</button></header>
    <ul class="cart-items" role="list" data-cart-items></ul>
    <div class="cart-empty" data-cart-empty>{icon("cart")}<p><strong>Seu carrinho está vazio.</strong></p><p>Que tal começar pelo carro-chefe, a Laranja Bahia?</p>
      <a class="btn btn--primary btn--sm" href="sabores.html"><span>Ver sabores</span></a></div>
    <footer class="cart-drawer__foot" data-cart-foot>
      <p class="cart-drawer__ship" data-cart-ship></p>
      <p class="cart-drawer__total"><span>Subtotal</span><strong data-cart-subtotal>R$ 0,00</strong></p>
      <a class="btn btn--primary cart-drawer__checkout" href="checkout.html"><span>Finalizar compra</span>{icon("arrow", "icon--arrow")}<span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></a>
      <button class="cart-drawer__continue" type="button" data-close-cart>Continuar comprando</button>
    </footer>
  </aside>
</div>'''

def header(active):
    links = ''
    mlinks = ''
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ''
        links += f'<li><a class="nav-link" href="{href}"{cur}>{label}</a></li>'
        mlinks += f'<li><a class="mm-link" href="{href}"{cur}>{label}</a></li>'
    return f'''<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
<header class="site-header" data-header>
  <div class="container header-inner">
    <a class="logo" href="index.html" aria-label="FRIZZA, ir para a página inicial">{logo_slot("logo-frizza.png", "logo-slot--color")}{logo_slot("logo-frizza-branco.png", "logo-slot--white")}</a>
    <nav class="nav" aria-label="Menu principal"><ul class="nav-list" role="list">{links}</ul></nav>
    {btn(icon("pin") + "Onde Comprar", "onde-encontrar.html", "yellow", size="btn--sm header-cta")}
    <button class="cart-toggle" type="button" aria-controls="cart-drawer" aria-expanded="false" aria-label="Abrir carrinho, 0 itens" data-open-cart>{icon("cart")}<span class="cart-count" data-cart-count aria-hidden="true">0</span></button>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Abrir menu"><span></span><span></span></button>
  </div>
</header>
{cart_drawer()}
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <div class="mobile-menu__inner">
    <span class="mobile-menu__blob mobile-menu__blob--1" aria-hidden="true"></span>
    <span class="mobile-menu__blob mobile-menu__blob--2" aria-hidden="true"></span>
    <nav aria-label="Menu mobile"><ul role="list">{mlinks}</ul></nav>
    <div class="mobile-menu__foot">{btn("Onde Comprar", "onde-encontrar.html", "dark", ic="pin", ic_first=True, magnetic=False)}{social_links()}</div>
  </div>
</div>'''

def footer():
    flav = ''.join(f'<li><a href="sabor-{f["slug"]}.html">{f["name"]}</a></li>' for f in FLAVORS)
    seals = ''.join(f'<li>{seal_from(s, "-f")}<p><b>{s["title"]}</b>{s["text"]}</p></li>' for s in SEALS)
    nb = ''.join(f'<span style="width:{s}px;height:{s}px;left:{l}%;top:{t}%"></span>' for s, l, t in [(60, 92, 10), (24, 85, 70), (36, 4, 75), (14, 48, 12)])
    return f'''<footer class="site-footer">
  <div class="container">
    <section class="newsletter" aria-labelledby="newsletter-title" data-reveal>
      <div class="newsletter__bubbles" aria-hidden="true">{nb}</div>
      <div>
        <h2 id="newsletter-title">Receba novidades borbulhantes</h2>
        <p>Lançamentos, receitas de mocktails e promoções antes de todo mundo. Sem spam, prometemos: só coisa boa.</p>
      </div>
      <form class="newsletter__form" data-validate aria-label="Inscrição na newsletter">
        <div class="field" data-msg-empty="Digite seu e-mail para receber as novidades.">
          <label for="news-email">Seu melhor e-mail</label>
          <input id="news-email" name="email" type="email" autocomplete="email" placeholder="nome@email.com" required aria-describedby="news-email-err">
          <p class="field__error" id="news-email-err">{icon("close")}<span></span></p>
        </div>
        <button class="btn btn--dark" type="submit" data-magnetic><span>Quero receber</span>{icon("send")}<span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></button>
        <p class="newsletter__msg" data-form-msg role="status" aria-live="polite"></p>
      </form>
    </section>

    <div class="footer-main">
      <div class="footer-brand">
        <a class="logo" href="index.html" aria-label="FRIZZA, ir para a página inicial">{logo_slot("logo-frizza-branco.png")}</a>
        <p>Refrigerantes artesanais com frutas brasileiras de verdade. Feitos com carinho em Gramado (RS) desde 2018.</p>
        {social_links()}
      </div>
      <nav class="footer-col" aria-labelledby="f-inst"><h3 id="f-inst">Institucional</h3><ul role="list">
        <li><a href="historia.html">Nossa História</a></li><li><a href="historia.html#sustentabilidade">Sustentabilidade</a></li>
        <li><a href="frizzalovers.html">#FRIZZALOVERS</a></li><li><a href="contato.html#imprensa">Imprensa</a></li></ul></nav>
      <nav class="footer-col" aria-labelledby="f-sab"><h3 id="f-sab">Sabores</h3><ul role="list">{flav}</ul></nav>
      <nav class="footer-col" aria-labelledby="f-aj"><h3 id="f-aj">Ajuda</h3><ul role="list">
        <li><a href="onde-encontrar.html">Onde comprar</a></li><li><a href="sabores.html">Comprar online</a></li><li><a href="checkout.html">Finalizar compra</a></li>
        <li><a href="contato.html#faq">Perguntas frequentes</a></li><li><a href="contato.html#faq">Devolução de garrafas</a></li></ul></nav>
      <div class="footer-col"><h3>Contato</h3><ul role="list">
        <li><a href="https://wa.me/5554999990000" data-demo="{DEMO_CONTACT}">WhatsApp (54) 99999-0000</a></li>
        <li><a href="mailto:oi@frizza.com.br" data-demo="{DEMO_CONTACT}">oi@frizza.com.br</a></li>
        <li><a href="tel:+555430000000" data-demo="{DEMO_CONTACT}">(54) 3000-0000</a></li>
        <li>Gramado, RS</li></ul></div>
    </div>

    <ul class="footer-seals" role="list" aria-label="Prêmios e certificações">{seals}</ul>

    <div class="footer-bottom">
      <p>© 2026 FRIZZA Refrigerantes. Feito no Brasil, com fruta de verdade.</p>
      <p class="disclaimer">Marca fictícia criada para fins acadêmicos — Design de Interface, Publicidade e Propaganda, Unoeste.</p>
    </div>
  </div>
  <div class="footer-big" aria-hidden="true"><img src="assets/img/marca/logo-frizza-branco.png" alt="" width="796" height="429" loading="lazy" decoding="async"></div>
</footer>'''

PAGES = []
def page(filename, title, desc, main, active, theme_color='#FF6B2B', body_attrs='', serif=False):
    CURRENT_PAGE[0] = filename
    out = (head(title, desc, theme_color, serif) + f'\n<body {body_attrs}>\n' + preloader() + '\n' + page_transition() + '\n' +
           header(active) + f'\n<main id="conteudo" tabindex="-1">\n{main}\n</main>\n' + footer() + '\n</body>\n</html>\n')
    PAGES.append((filename, out))

def set_page(name):
    CURRENT_PAGE[0] = name

# ---------------------------------------------------------------- componentes
def product_card(f, section):
    return f'''<li class="product-card" data-theme="{f["slug"]}" data-cat="{f["cats"]}" data-tilt>
  <div class="product-card__inner">
    <div class="card-bubbles" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
    <span class="product-card__badge">{f["badge"]}</span>
    <div class="product-card__visual">{can(f, section)}</div>
    <h3><a href="sabor-{f["slug"]}.html" data-cursor="ver">FRIZZA {f["name"]}</a></h3>
    <p class="product-card__slogan">“{f["slogan"]}”</p>
    <p class="product-card__price"><strong>{brl(f["price"])}</strong> <span>lata 350 ml</span></p>
    {cart_btn(f, "dark", "btn--sm", "Adicionar", magnetic=False)}
  </div>
</li>'''

def stat(ic, value, label, prefix='', suffix='', sr=None):
    sr = sr or f'{prefix}{value:,}{suffix}'.replace(',', '.')
    shown = f'{prefix}{value:,}{suffix}'.replace(',', '.')
    return (f'<li class="stat">{icon(ic)}<span class="stat__num" aria-hidden="true" data-count="{value}" data-prefix="{prefix}" data-suffix="{suffix}">{shown}</span>'
            f'<span class="sr-only">{sr} </span><span class="stat__label">{label}</span></li>')

def marquee(items, cls='', reverse=False):
    group = ''.join(f'<span>{t}</span>{icon("sparkle")}' for t in items)
    g = f'<div class="marquee__group">{group}</div>'
    return (f'<div class="marquee {cls}{" marquee--reverse" if reverse else ""}"><p class="sr-only">{" · ".join(items)}</p>'
            f'<div class="marquee__track" aria-hidden="true">{g}{g}</div></div>')

# =================================================================== HOME
set_page('index.html')
hero_cans = ''
order = ['acai-guarana', 'limao-hortela', 'laranja-bahia', 'pessego-gengibre', 'uva-rose']
depths = [0.5, 0.8, 1.2, 0.8, 0.5]
for i, (slug, dp) in enumerate(zip(order, depths)):
    fl = ['float', 'float--2', 'float--3', 'float--2', 'float'][i]
    hero_cans += f'<div class="hero__can hero__can--{i+1}" data-depth="{dp}"><div class="float {fl}">{can(FMAP[slug], "Home → hero (5 latas flutuando)", eager=True, high=(i == 2))}</div></div>'
hero_fruits_files = ['fruta-laranja-fatia.png', 'fruta-uva-rose.png', 'folha-hortela.png', 'fruta-acai.png', 'fruta-pessego.png', 'fruta-limao-siciliano.png', 'gelo.png', 'folha-tropical.png']
hero_fruits = ''.join(f'<div class="hero__fruit hero__fruit--{i+1}" data-depth="{[1.8,1.6,2.2,2.4,1.4,1.7,2.6,1.2][i]}"><div class="float float--{[2,3,2,3,2,3,2,3][i]}">{fruit(f, "Home → hero (frutas, gelo e folhas)", eager=True)}</div></div>' for i, f in enumerate(hero_fruits_files))
drops = ''.join(f'<span class="hero__drop" data-depth="{dp}" style="left:{l}%;top:{t}%"></span>' for l, t, dp in [(30, 20, 2.6), (68, 30, 2.2), (12, 55, 2.8), (88, 50, 2.4), (46, 8, 3)])

vit_panels = ''
for f in FLAVORS:
    tags = ''.join(f'<li class="tag">{icon(i)}{t}</li>' for i, t in f['facts'])
    vit_panels += f'''<article class="vitrine__panel" data-color="{f["color"]}" data-fg="{f["fg"]}" aria-labelledby="vit-{f["slug"]}">
  <div class="vitrine__visual"><span class="vitrine__ring" aria-hidden="true"></span><div class="vitrine__can">{destaque(f, "Home → vitrine dos sabores", cls="vitrine__photo")}</div></div>
  <div class="vitrine__info">
    <p class="eyebrow">{f["badge"]}</p>
    <h3 id="vit-{f["slug"]}">{f["name"]}</h3>
    <p class="slogan">“{f["slogan"]}”</p>
    <p>{f["desc"].split(". ")[0]}.</p>
    <ul class="vitrine__tags" role="list">{tags}</ul>
    <p class="vitrine__price"><strong>{brl(f["price"])}</strong> · lata 350 ml</p>
    <div class="btn-row">{cart_btn(f, "dark")}{btn("Saiba mais", f"sabor-{f['slug']}.html", "white", ic="arrow", attrs=f'aria-label="Saiba mais sobre FRIZZA {esc(f["name"])}"')}</div>
  </div>
</article>'''

feed_users = [('mari.desenha', 'Laranja Bahia no piquenique do Barigui ☀️'), ('lucas.barista', 'Açaí + guaraná pra aguentar o turno 💜'),
              ('cleo.profe', 'Brinde de fim de ano com a turma 🥂'), ('nathy.picnic', 'Pêssego com gengibre + tábua de queijos = amor'),
              ('rafa.trilhas', 'Limão com hortelã no topo da trilha 🌿'), ('bia.praia', 'Pôr do sol em Floripa com FRIZZA 🌅')]
LOVERS = [  # (arquivo, largura, altura, usuário, legenda, alt, object-position)
    ('comunidade/lovers-01.webp', 1200, 1200, 'mari.desenha', 'Laranja Bahia gelada pra começar o dia ☀️', 'Mulher de boné verde bebendo uma lata de FRIZZA Laranja Bahia', '50% 40%'),
    ('comunidade/lovers-02.webp', 1200, 896, 'lucas.barista', 'Limão com Hortelã pra refrescar o turno 🌿', 'Rapaz de cabelo cacheado e óculos laranja segurando uma lata de FRIZZA Limão com Hortelã contra o céu azul', '50% 40%'),
    ('comunidade/lovers-03.webp', 1121, 1403, 'bia.colecionadora', 'Coleção completa e o coração quentinho 💛', 'Mulher sorrindo de olhos fechados abraçando quatro latas FRIZZA sobre fundo rosa', '50% 30%'),
    ('comunidade/lovers-04.webp', 1200, 800, 'nathy.picnic', 'Açaí com Guaraná no piquenique de domingo 💜', 'Mulher de cabelo crespo bebendo FRIZZA Açaí com Guaraná deitada numa toalha de piquenique', '55% 40%'),
    ('comunidade/lovers-05.webp', 1122, 1402, 'rafa.no.sol', 'Equilibrando a FRIZZA no rolê 😎', 'Pessoa de boné laranja e óculos equilibrando uma lata de FRIZZA Limão com Hortelã na cabeça', '50% 35%'),
    ('comunidade/lovers-06.webp', 1024, 1535, 'duda.e.amigos', 'A turma toda de canudinho e FRIZZA 🫧', 'Três amigos vistos de cima bebendo FRIZZA de canudinho na rua', '50% 35%'),
    ('comunidade/lovers-07.webp', 1100, 1430, 'theo.praia', 'Laranja Bahia gelada no fim de tarde 🌅', 'Homem de óculos escuros bebendo FRIZZA Laranja Bahia sob o céu azul com nuvens', '50% 30%'),
    ('comunidade/lovers-08.webp', 1085, 1450, 'gabi.foodie', 'Uva Rosé ou Limão? Fiquei com as duas 😝', 'Mulher fazendo careta divertida com duas latas FRIZZA na frente dos olhos', '50% 35%'),
    ('comunidade/lovers-09.webp', 853, 1280, 'carol.serra', 'Abraço coletivo de sabores 🍇🍋🍊', 'Mãos segurando quatro latas FRIZZA junto ao corpo num gramado', '50% 45%'),
    ('comunidade/lovers-10.webp', 1024, 1536, 'joao_nofestival', 'Açaí e limão pra dançar a noite toda 🎶', 'Dois amigos sorrindo com latas FRIZZA em frente a uma parede verde', '50% 35%'),
    ('comunidade/lovers-11.webp', 1122, 1402, 'pedro.e.ju', 'Verão é isso: praia, sol e FRIZZA 🌊', 'Casal na praia brindando com latas FRIZZA sob o céu azul', '50% 35%'),
    ('comunidade/lovers-12.webp', 1024, 1536, 'aninha.sp', 'Laranja Bahia na mão e sorriso no rosto 😮', 'Mulher de boné e óculos escuros mostrando uma lata de FRIZZA Laranja Bahia', '50% 35%'),
    ('comunidade/lovers-13.webp', 1122, 1402, 'leo.ipanema', 'Uva Rosé de canudinho em Ipanema 🏖️', 'Rapaz de óculos escuros bebendo FRIZZA Uva Rosé de canudinho na praia, com morros ao fundo', '50% 40%'),
    ('comunidade/lovers-14.webp', 1086, 1448, 'flor.boho', 'Look do dia combinando com a FRIZZA 🌿', 'Mulher de vestido longo segurando uma lata FRIZZA em frente a uma parede de bambu', '50% 35%'),
    ('comunidade/lovers-15.webp', 1060, 1484, 'bastidores.do.som', 'Bastidores do show, Uva Rosé na mão 🎤', 'Dois amigos rindo nos bastidores de um show, um deles erguendo uma lata de FRIZZA Uva Rosé', '50% 35%'),
]
feed = ''
for k in [0, 3, 2, 1, 8, 10]:
    (file, w, h, user, cap, d, pos) = LOVERS[k]
    feed += (f'<li class="feed__item">{slot(file, w, h, d, d, "Home → #FRIZZALOVERS (feed)", style="--ar:1 / 1;", pos=pos)}'
             f'<a class="feed__overlay" href="frizzalovers.html" aria-label="Ver post de @{user} na galeria #FRIZZALOVERS">{icon("instagram")}<span>@{user}</span></a></li>')

uva = FMAP['uva-rose']
register("sabores/uva-rose-lata-premium.webp", 371, 629, "Lata de FRIZZA Uva Rosé, edição premium", "", "Home → banner premium Uva Rosé", "png")
home = f'''
<section class="hero" data-hero aria-labelledby="hero-title">
  <div class="hero__blobs" aria-hidden="true"><span class="blob b1"></span><span class="blob b2"></span><span class="blob b3"></span><span class="blob b4"></span></div>
  {bubbles_canvas(40)}
  <div class="container hero__inner">
    <div class="hero__copy">
      <p class="eyebrow" data-intro-fade style="color:var(--preto-suave)">Refrigerantes artesanais</p>
      <h1 class="hero__title" id="hero-title"><span class="line" data-split="chars" data-intro>Seu paladar merece</span> <span class="line line--2" data-split="chars" data-intro>esse upgrade</span></h1>
      <p class="hero__sub" data-intro-fade>Refrigerantes artesanais com frutas brasileiras de verdade, até 40% menos açúcar e nenhum ingrediente que você não sabe pronunciar.</p>
      <div class="btn-row" data-intro-fade>{btn("Conheça os sabores", "sabores.html", "primary", ic="arrow", size="btn--lg")}{btn("Onde comprar", "onde-encontrar.html", "white", ic="pin", size="btn--lg", ic_first=True)}</div>
    </div>
    <div class="hero__stage">{hero_cans}{hero_fruits}{drops}</div>
  </div>
  <a class="hero__scroll" href="#manifesto"><i aria-hidden="true"></i>Role</a>
  {wave("#1A1A2E")}
</section>

<div class="marquee-wrap" style="background:var(--preto-suave)">
  {marquee(["100% natural", "40% menos açúcar", "Feito no Brasil", "Sem conservantes", "Frutas de pequenos produtores", "Garrafa retornável", "Zero corante artificial"], "marquee--yellow marquee--tilt")}
</div>

<section class="section manifesto" id="manifesto" aria-labelledby="manifesto-title">
  <div class="manifesto__deco float" aria-hidden="true">{fruit("folha-tropical.png", "Manifesto (decoração)", label=False)}</div>
  <div class="container container--narrow">
    <h2 class="sr-only" id="manifesto-title">Manifesto FRIZZA</h2>
    <p class="manifesto__text" data-manifesto>A FRIZZA nasceu do sonho de criar um refrigerante que representa o <span class="accent-1">sabor brasileiro</span> e valoriza o <span class="accent-2">pequeno produtor</span>. A gente pega <span class="accent-1">fruta brasileira de verdade</span>, de pequenos produtores, junta com gás na medida e <span class="accent-2">menos açúcar</span>. Sem corante artificial, sem conservante, sem enrolação. <span class="accent-3">Natural de verdade. Gostoso de verdade.</span> Simples assim.</p>
    <div class="manifesto__sign" data-reveal>{btn("Conheça nossa história", "historia.html", "mint", ic="arrow")}<span class="muted">Desde 2018, em Gramado (RS) 🫧</span></div>
  </div>
</section>

<section class="vitrine" data-vitrine aria-labelledby="vitrine-title">
  <div class="vitrine__pin">
    <div class="container vitrine__head">
      <div><p class="eyebrow">Nossos sabores</p><h2 id="vitrine-title">Cada garrafa, uma<br>mini viagem pelo Brasil</h2></div>
    </div>
    <div class="vitrine__track" tabindex="0" role="region" aria-label="Vitrine dos 5 sabores (role para ver todos)">{vit_panels}</div>
    <div class="vitrine__dots" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
  </div>
</section>

<section class="rose-banner section" aria-labelledby="rose-title">
  {bubbles_canvas(90, color="255, 222, 236", mode="sparkle")}
  <div class="container rose-banner__grid">
    <div>
      <p class="eyebrow">Edição Limitada · Serra Gaúcha</p>
      <h2 class="premium-title" id="rose-title" data-reveal>Para brindar <span class="accent">sem precisar de motivo</span></h2>
      <p class="premium-text" data-reveal>A nova FRIZZA Uva Rosé nasce da parceria com vinícolas de Bento Gonçalves: uva rosé orgânica, um sopro de água de rosas e bolhas finas e persistentes, estilo espumante. Sem álcool, cheia de celebração.</p>
      <div class="btn-row" style="margin-top:34px" data-reveal>{btn("Descobrir a Uva Rosé", "sabor-uva-rose.html", "yellow", ic="arrow")}{cart_btn(uva, "white")}</div>
    </div>
    <div class="rose-banner__visual">
      <span class="rose-banner__halo" aria-hidden="true"></span>
      <div class="float rose-banner__can" data-parallax="0.15"><div class="png-slot is-cutout is-loaded" style="--ar:371 / 629">{img_tag("sabores/uva-rose-lata-premium.webp", "Lata de FRIZZA Uva Rosé, edição premium")}</div></div>
      {seal("rose-home", "EDIÇÃO LIMITADA • SERRA GAÚCHA • SAFRA 2026 •", "Rosé", "Safra 2026", "#FFD23F", "#1A1A2E", "Selo Edição Limitada, Serra Gaúcha", 34)}
    </div>
  </div>
</section>

<section class="section section--pastel" data-theme="roxo" aria-labelledby="lovers-title">
  <div class="container">
    <div class="section-head center"><p class="eyebrow">Comunidade</p><h2 id="lovers-title" data-split="words">#FRIZZALOVERS</h2>
      <p>Gente de verdade, momentos de verdade. Olha quem já está borbulhando com a gente.</p></div>
    <ul class="feed" role="list" data-stagger>{feed}</ul>
    <div class="lovers-cta" data-reveal>
      <p>Poste sua FRIZZA com <strong>#FRIZZALOVERS</strong> e apareça aqui 📸</p>
      {btn("Seguir @frizzaoficial", "https://www.instagram.com/frizzaoficial/", "primary", ic="instagram", ic_first=True, attrs=f'data-demo="{DEMO_SOCIAL}" target="_blank" rel="noopener"')}
    </div>
  </div>
</section>

<section class="section" aria-labelledby="why-title">
  <div class="container">
    <div class="section-head center"><p class="eyebrow">Por que FRIZZA</p><h2 id="why-title" data-split="words">Menos ingredientes estranhos, mais sabor inesquecível</h2>
      <p>Menos ingredientes que você não sabe pronunciar, mais sabor que você não vai esquecer.</p></div>
    <ul class="features" role="list" data-stagger>
      <li class="feature"><div class="feature__icon">{ICONS["leaf"]}</div><h3>Ingredientes naturais</h3><p>Fruta de verdade, extratos naturais e açúcar demerara orgânico. Sem corantes, aromas ou conservantes artificiais.</p></li>
      <li class="feature"><div class="feature__icon">{ICONS["drop"]}</div><h3>Menos açúcar</h3><p>Até 40% menos açúcar que os refrigerantes tradicionais. Doce na medida, sem adoçante artificial.</p></li>
      <li class="feature"><div class="feature__icon">{ICONS["hands"]}</div><h3>Pequenos produtores</h3><p>Laranja do Recôncavo Baiano, açaí do Pará, uvas da Serra Gaúcha: 23 famílias parceiras, com preço justo.</p></li>
      <li class="feature"><div class="feature__icon">{ICONS["recycle"]}</div><h3>Sustentabilidade</h3><p>Garrafas de vidro retornáveis, logística reversa e árvores plantadas a cada lote. Ainda tem muito a fazer, e a gente segue fazendo.</p></li>
    </ul>
  </div>
</section>

<section class="section story-preview" aria-labelledby="story-title">
  <div class="container grid-2">
    <div class="story-preview__media">
      {slot("historia/fundadoras-2018.webp", 1080, 1350, "As duas amigas fundadoras da FRIZZA cortando laranjas na cozinha, em 2018", "", "Home → prévia da história", reveal="mask", pos="50% 45%", parallax=True)}
      <div class="story-preview__badge" aria-hidden="true"><span><b>2018</b><small>Gramado · RS</small></span></div>
    </div>
    <div class="stack">
      <p class="eyebrow">Nossa história</p>
      <h2 id="story-title" data-split="words">Nasceu em Gramado, em 2018, de uma pergunta simples</h2>
      <p class="lead" data-reveal>Por que refrigerante precisa ter gosto de laboratório? Duas amigas, jovens empreendedoras, resolveram responder na prática: fruta brasileira, pouco açúcar e muito cuidado.</p>
      <p data-reveal>Começou numa cozinha e numa feira de rua. Hoje são mais de 200 pontos de venda no Sul e Sudeste e entrega para todo o Brasil. O jeito de fazer continua o mesmo.</p>
      <p data-reveal><a class="link-arrow" href="historia.html">Ler a história completa {icon("arrow")}</a></p>
    </div>
  </div>
</section>
'''
page('index.html', 'FRIZZA Refrigerantes | Seu paladar merece esse upgrade',
     'Refrigerantes artesanais com frutas brasileiras de verdade, menos açúcar e ingredientes naturais. Conheça os 5 sabores FRIZZA, feitos em Gramado (RS).',
     home, 'index.html', serif=True)

# =================================================================== SABORES
set_page('sabores.html')
cards = ''.join(product_card(f, 'Grid de cards') for f in FLAVORS)
row = ''.join(f'<div class="float float--{(i%3)+1}" data-reveal="fade">{can(f, "Nossos Sabores → hero (5 latas)", variant="-classica", eager=True, high=(i == 2))}</div>' for i, f in enumerate(FLAVORS))

QUIZ = [
    ('Pra que momento é a sua FRIZZA?', 'sun', [
        ('Dia a dia, com a família', {'laranja-bahia': 3, 'limao-hortela': 1}),
        ('Energia pro rolê ou pros estudos', {'acai-guarana': 3}),
        ('Acompanhar comida ou fazer drinks', {'limao-hortela': 3, 'pessego-gengibre': 1}),
        ('Comemorar alguma coisa', {'uva-rose': 3, 'pessego-gengibre': 1}),
        ('Experimentar algo diferente', {'pessego-gengibre': 3, 'uva-rose': 1}),
    ]),
    ('Que tipo de sabor te conquista?', 'taste', [
        ('Cítrico e refrescante', {'laranja-bahia': 2, 'limao-hortela': 3}),
        ('Frutado e encorpado', {'acai-guarana': 3, 'uva-rose': 1}),
        ('Doce com um toque picante', {'pessego-gengibre': 3}),
        ('Floral e delicado', {'uva-rose': 3}),
        ('Doce e clássico', {'laranja-bahia': 3}),
    ]),
    ('Quanto gás você curte?', 'bubbles', [
        ('Suave, quase nada', {'acai-guarana': 2}),
        ('Na medida certa', {'laranja-bahia': 2, 'pessego-gengibre': 2}),
        ('Bastante, que estala!', {'limao-hortela': 3}),
        ('Fininho, estilo espumante', {'uva-rose': 3}),
    ]),
    ('E as calorias?', 'drop', [
        ('Quero o mais leve possível', {'limao-hortela': 3}),
        ('Equilibrado está ótimo', {'laranja-bahia': 1, 'pessego-gengibre': 1, 'acai-guarana': 1}),
        ('Hoje é dia de festa, tanto faz', {'uva-rose': 2, 'acai-guarana': 1}),
    ]),
]
import json as _json
quiz_steps = ''
for qi, (q, ic, opts) in enumerate(QUIZ):
    options = ''.join(
        f'<li><button class="quiz__opt" type="button" data-score="{esc(_json.dumps(sc))}" aria-pressed="false">{o}</button></li>' for o, sc in opts)
    quiz_steps += (f'<fieldset class="quiz__step{" is-current" if qi == 0 else ""}" data-step="{qi}"{"" if qi == 0 else " hidden"}>'
                   f'<legend class="quiz__q">{icon(ic)}<span>{q}</span></legend><ul class="quiz__opts" role="list">{options}</ul></fieldset>')
quiz_products = ''.join(
    f'<template data-quiz-product="{f["slug"]}"><article class="quiz-result" data-theme="{f["slug"]}">'
    f'<div class="quiz-result__can">{destaque(f, "Nossos Sabores → quiz (resultado)", ar="1 / 1", pos="94% 50%")}</div>'
    f'<div class="quiz-result__info"><p class="quiz-result__match"><span data-match></span> de combinação</p>'
    f'<h4>FRIZZA {f["name"]}</h4><p class="quiz-result__slogan">“{f["slogan"]}”</p><p class="quiz-result__why">{f["card"]}</p>'
    f'<p class="product-card__price"><strong>{brl(f["price"])}</strong> <span>lata 350 ml</span></p>'
    f'<div class="btn-row">{cart_btn(f, "dark", "btn--sm", "Adicionar", magnetic=False)}<a class="link-arrow" href="sabor-{f["slug"]}.html">Conhecer {icon("arrow")}</a></div></div></article></template>'
    for f in FLAVORS)
quiz_html = f'''<div class="quiz" data-quiz data-reveal>
  <div class="quiz__top">
    <button class="quiz__back" type="button" data-quiz-back hidden>{icon("arrow")}<span>Voltar</span></button>
    <p class="quiz__progress-label" aria-live="polite"><span data-quiz-count>Pergunta 1 de {len(QUIZ)}</span></p>
  </div>
  <div class="quiz__bar" aria-hidden="true"><i style="--p:{1/len(QUIZ):.3f}"></i></div>
  <form class="quiz__form" onsubmit="return false">{quiz_steps}</form>
  <div class="quiz__result" data-quiz-result hidden tabindex="-1">
    <p class="eyebrow">Seu match</p>
    <h3 class="quiz__result-title">Os sabores com a sua cara</h3>
    <div class="quiz__results" data-quiz-results></div>
    <div class="btn-row quiz__actions"><button class="btn btn--primary" type="button" data-quiz-add-all><span data-quiz-add-label>Adicionar os favoritos ao carrinho</span>{icon("cart")}<span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></button>
      <button class="btn btn--ghost" type="button" data-quiz-restart><span>Refazer o quiz</span></button></div>
  </div>
  {quiz_products}
  <noscript><p>O quiz precisa de JavaScript. Veja todos os sabores na lista acima.</p></noscript>
</div>'''
sabores = f'''
<section class="page-hero center" data-theme="solar" aria-labelledby="sab-title">
  {bubbles_canvas(30)}
  <div class="container" style="position:relative;z-index:2">
    <p class="eyebrow" data-intro-fade>A linha completa</p>
    <h1 class="page-hero__title" id="sab-title" data-split="chars" data-intro>Nossos Sabores</h1>
    <p class="page-hero__lead" data-intro-fade>Cinco sabores, cinco cantos do Brasil. Todos com fruta de verdade, menos açúcar e zero ingrediente esquisito. Qual vai ser o seu?</p>
    <div class="cans-row">{row}</div>
  </div>
  {wave("#FAFAFA")}
</section>

<section class="section" aria-labelledby="grid-title">
  <div class="container">
    <h2 class="sr-only" id="grid-title">Todos os sabores</h2>
    <div class="filters" role="group" aria-label="Filtrar sabores por categoria" data-filters=".product-grid .product-card">
      <button class="filter-btn" type="button" data-filter="todos" aria-pressed="true">Todos</button>
      <button class="filter-btn" type="button" data-filter="citricos" aria-pressed="false">Cítricos</button>
      <button class="filter-btn" type="button" data-filter="energia" aria-pressed="false">Energia</button>
      <button class="filter-btn" type="button" data-filter="gourmet" aria-pressed="false">Gourmet</button>
      <button class="filter-btn" type="button" data-filter="especial" aria-pressed="false">Edição Especial</button>
    </div>
    <p class="filter-status" id="filter-status" role="status" aria-live="polite">5 sabores encontrados</p>
    <ul class="product-grid" role="list" data-stagger>{cards}</ul>
  </div>
</section>

<section class="section section--pastel" data-theme="menta" id="quiz" aria-labelledby="guide-title">
  <div class="container container--narrow">
    <div class="section-head center"><p class="eyebrow">Quiz</p><h2 id="guide-title" data-split="words">Qual FRIZZA combina com você?</h2>
      <p>Responda 4 perguntinhas rápidas e a gente indica os sabores com a sua cara.</p></div>
    {quiz_html}
  </div>
</section>

<section class="section" aria-labelledby="buy-title">
  <div class="container">
    <div class="buy-band" data-theme="laranja-bahia" data-reveal>
      <span class="blob" aria-hidden="true"></span>
      <div style="position:relative"><p class="eyebrow" style="color:var(--amarelo-solar)">Bateu vontade?</p><h2 id="buy-title">Tem FRIZZA pertinho de você</h2>
        <p style="margin-top:12px;max-width:520px">Compre aqui mesmo, com entrega para todo o Brasil, ou encontre um dos mais de 200 pontos de venda no Sul e Sudeste.</p></div>
      <div class="btn-row" style="position:relative"><button class="btn btn--yellow" type="button" data-open-cart data-magnetic>{icon("cart")}<span>Ver carrinho</span><span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></button>{btn("Onde comprar", "onde-encontrar.html", "primary", ic="pin", ic_first=True)}</div>
    </div>
  </div>
</section>
'''
page('sabores.html', 'Nossos Sabores | FRIZZA Refrigerantes',
     'Laranja Bahia, Açaí com Guaraná, Limão com Hortelã, Pêssego com Gengibre e Uva Rosé: conheça os 5 refrigerantes artesanais FRIZZA.',
     sabores, 'sabores.html', theme_color='#FFD23F', body_attrs='data-cta="orange"')

# =================================================================== PÁGINAS DE SABOR
def nutri_table(f):
    n = f['nutri']
    def vd(v, base): return f'{max(1, round(v / base * 100))}%' if v else '0%'
    rows = [
        ('Valor energético', f'{n["kcal"]} kcal', vd(n['kcal'], 2000), ''),
        ('Carboidratos', f'{n["carb"]} g', vd(n['carb'], 300), ''),
        ('Açúcares totais', f'{n["sug"]} g', '—', 'sub'),
        ('Açúcares adicionados', f'{n["add"]} g', vd(n['add'], 50), 'sub'),
        ('Proteínas', f'{str(n["prot"]).replace(".", ",")} g', vd(n['prot'], 50) if n['prot'] else '0%', ''),
        ('Gorduras totais', '0 g', '0%', ''),
        ('Fibra alimentar', f'{n["fib"]} g', vd(n['fib'], 25) if n['fib'] else '0%', ''),
        ('Sódio', f'{n["sod"]} mg', '<1%', ''),
    ]
    if n.get('caf'): rows.append(('Cafeína (natural do guaraná)', f'{n["caf"]} mg', '—', ''))
    body = ''.join(f'<tr class="{c}"><th scope="row">{a}</th><td>{b}</td><td>{v}</td></tr>' for a, b, v, c in rows)
    return f'''<table class="nutri">
  <caption>Informação nutricional · porção de 350 ml (1 lata)</caption>
  <thead><tr><th scope="col">Nutriente</th><th scope="col">Quantidade por porção</th><th scope="col">%VD*</th></tr></thead>
  <tbody>{body}</tbody>
</table>'''

def flavor_page(f):
    fn = f'sabor-{f["slug"]}.html'
    set_page(fn)
    premium = f.get('premium')
    full = f.get('full_name', f['name'])
    fruits = ''.join(f'<div class="flavor-hero__fruit flavor-hero__fruit--{i+1}" data-parallax="{[0.3,0.5,0.2,0.6][i]}" data-depth="{[1.6,2.2,1.2,2.6][i]}"><div class="float float--{(i%3)+1}">{fruit(fr, "Página do sabor → hero (frutas soltas)", eager=True)}</div></div>' for i, fr in enumerate(f['fruits']))
    facts = ''.join(f'<li>{icon(i)}{t}</li>' for i, t in f['facts'])
    sens = ''
    for k, (ic, title, text, mlabel, lvl) in enumerate(f['sensory']):
        meter = ''.join(f'<i class="{"on" if j < lvl else ""}"></i>' for j in range(5))
        sens += (f'<li class="sensory__card"><div class="sensory__icon" aria-hidden="true">{ICONS[ic]}</div>'
                 f'<h3>{title}</h3><p>{text}</p><div class="meter" role="img" aria-label="{mlabel}: {lvl} de 5">{meter}<span>{mlabel}</span></div></li>')
    bars = ''
    for name, pct, illus in f['ingredients']:
        v = max(pct / 100, 0.015)
        p = (f'{pct:g}'.replace('.', ',')) + '%'
        note = '<p class="bar__note">valor ilustrativo</p>' if illus else ''
        bars += (f'<li class="bar"><div class="bar__top"><span>{name}</span><span>{p}</span></div>'
                 f'<div class="bar__track" aria-hidden="true"><div class="bar__fill" style="--v:{v:.3f}"></div></div>{note}</li>')
    C = 2 * math.pi * 80
    ring_pct, ring_label = f['ring']
    off = C * (1 - ring_pct / 100 * 4)  # anel em escala 25% = volta completa
    off = max(off, 0)
    diffs = ''.join(f'<li>{icon("check")}<span>{t}</span></li>' for t in f['diffs'])
    others = ''.join(product_card(o, 'Experimente também') for o in FLAVORS if o is not f)
    hl_num, hl_text = f['highlight']
    premium_band = (f'''<section class="section section--tight premium-band" aria-label="Universo Uva Rosé"><div class="container premium-band__grid">
  <figure class="premium-band__item" data-reveal>{slot("historia/vinhedo-bento-goncalves.webp", 3, 4, "Lata de FRIZZA Uva Rosé sobre um barril de madeira com vinhedos de Bento Gonçalves ao pôr do sol", "", "Uva Rosé → faixa premium", pos="86% 50%", parallax=True)}<figcaption>Vinhedos orgânicos de Bento Gonçalves</figcaption></figure>
  <figure class="premium-band__item premium-band__item--dark" data-reveal data-delay=".15">{slot("sabores/uva-rose-premium.webp", 3, 4, "Lata de FRIZZA Uva Rosé em fundo escuro com luz dourada, pétalas e bolhas", "", "Uva Rosé → faixa premium", pos="88% 50%", parallax=True)}<figcaption>Bolhas finas, estilo espumante</figcaption></figure>
</div></section>''' if premium else '')
    big_strip = (f'<div class="premium-strip" aria-hidden="true">Edição limitada · Safra 2026 · <span>Serra Gaúcha</span> · Embalagem colecionável</div>' + premium_band if premium else
                 marquee([f['slogan'], f'FRIZZA {f["name"]}', *[t for _, t in f['facts']]], 'marquee--yellow' if f['slug'] != 'acai-guarana' else ''))
    rose_grad = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="rose-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8A0BF"/><stop offset="1" stop-color="#7B2D8E"/></linearGradient></defs></svg>' if premium else ''
    hero_bubbles = bubbles_canvas(100, color="255, 222, 236", mode="sparkle") if premium else bubbles_canvas(36)
    hero_btn2 = btn("Ver ingredientes", "#ingredientes", "ghost")
    hero_btn1 = btn("Onde comprar", "onde-encontrar.html", "ghost", ic="pin", ic_first=True)
    wave_after_hero = '#FCF6F8' if premium else '#FAFAFA'
    main = f'''
<section class="flavor-hero" aria-labelledby="fl-title">
  {hero_bubbles}
  <span class="flavor-hero__big" aria-hidden="true">{f["big"]}</span>
  <div class="container flavor-hero__grid">
    <div style="position:relative;z-index:3">
      <p class="eyebrow" data-intro-fade>{f["badge"]}</p>
      <h1 class="flavor-hero__name" id="fl-title"><img class="flavor-hero__logo" data-intro-fade src="assets/img/marca/{"logo-frizza-branco.png" if f.get("header_light") else "logo-frizza.png"}" alt="FRIZZA" width="796" height="429"> <span data-split="chars" data-intro>{f["name"]}</span></h1>
      <p class="flavor-hero__slogan" data-intro-fade>“{f["slogan"]}”</p>
      <p class="flavor-hero__desc" data-intro-fade>{f["desc"]}</p>
      <p class="flavor-hero__price" data-intro-fade><strong>{brl(f["price"])}</strong> · lata 350 ml</p>
      <div class="btn-row" data-intro-fade>{cart_btn(f, "white" if f.get("header_light") else "dark", "btn--lg")}{hero_btn1}{hero_btn2}</div>
      <ul class="flavor-hero__facts" role="list" data-intro-fade>{facts}</ul>
    </div>
    <div class="flavor-hero__visual">
      <span class="flavor-hero__disc" aria-hidden="true"></span>
      <div class="flavor-hero__can flavor-hero__photo" data-spin-can>{destaque(f, "Página do sabor → hero (gira no scroll)", eager=True, high=True)}</div>
      {fruits}
    </div>
  </div>
  {wave(wave_after_hero)}
</section>
{big_strip}

<section class="section" aria-labelledby="sens-title">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Experiência sensorial</p><h2 id="sens-title" data-split="words">Como é tomar uma FRIZZA {f["name"]}</h2></div>
    <ul class="sensory" role="list" data-stagger>{sens}</ul>
  </div>
</section>

<section class="section section--pastel" id="ingredientes" aria-labelledby="ing-title">
  {rose_grad}
  <div class="container ingredients">
    <div class="ring" data-ring data-reveal="scale">
      <svg viewBox="0 0 200 200" aria-hidden="true"><circle class="ring__bg" cx="100" cy="100" r="80"/><circle class="ring__fg" cx="100" cy="100" r="80" stroke-dasharray="{C:.2f}" stroke-dashoffset="{off:.2f}"/></svg>
      <div class="ring__center"><b>{ring_pct}%</b><span>{ring_label}</span></div>
    </div>
    <div>
      <p class="eyebrow">Ingredientes</p>
      <h2 id="ing-title" data-split="words">Só o que precisa. Nada que você não conheça.</h2>
      <p class="lead" style="margin:16px 0 30px">A lista inteira cabe numa frase. Percentuais por volume.</p>
      <ul class="bars" role="list">{bars}</ul>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="diff-title">
  <div class="container grid-2">
    <div class="stack">
      <p class="eyebrow">Diferenciais</p>
      <h2 id="diff-title" data-split="words">Por que ela é especial</h2>
      <ul class="diff-list" role="list" data-stagger>{diffs}</ul>
    </div>
    <div class="occasion" data-reveal>
      {slot(f"sabores/ocasiao-{f['slug']}.webp", 1080, 1350, f"Pessoas aproveitando a FRIZZA {f['name']}: {f['occasion'][0].lower()}", f['occ_desc'], "Página do sabor → ocasião ideal", color=f['color'], reveal="mask", pos={'laranja-bahia': '50% 40%', 'acai-guarana': '55% 40%', 'limao-hortela': '50% 35%', 'pessego-gengibre': '50% 40%', 'uva-rose': '22% 50%'}[f['slug']], parallax=True)}
      <div class="occasion__card"><h3>{f["occasion"][0]}</h3><p>{f["occasion"][1]}</p></div>
    </div>
  </div>
</section>

<section class="section section--pastel" aria-labelledby="nut-title">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Transparência</p><h2 id="nut-title" data-split="words">Informação nutricional</h2>
      <p>Tudo às claras, com letra grande. Porque saber o que a gente bebe é direito de todo mundo.</p></div>
    <div class="grid-2" style="align-items:start">
      <div class="nutri-wrap" data-reveal>{nutri_table(f)}
        <p class="nutri-note">*% Valores Diários de referência com base em uma dieta de 2.000 kcal. <strong>Valores ilustrativos</strong> (marca fictícia, projeto acadêmico).</p></div>
      <ul class="nutri-highlights" role="list" data-stagger>
        <li><b>{f["nutri"]["kcal"]}</b>kcal por lata</li>
        <li><b>{hl_num}</b>{hl_text}</li>
        <li><b>0</b>conservantes</li>
        <li><b>100%</b>açúcar demerara orgânico</li>
      </ul>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="more-title">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Experimente também</p><h2 id="more-title" data-split="words">Outros sabores pra sua coleção</h2></div>
    <ul class="product-grid" role="list" data-stagger>{others}</ul>
    <div class="buy-band" style="margin-top:clamp(50px,7vw,90px)" data-reveal>
      <span class="blob" aria-hidden="true"></span>
      <div style="position:relative"><p class="eyebrow" style="color:var(--amarelo-solar)">Bateu vontade?</p><h2>Garanta sua FRIZZA {f["name"]}</h2>
        <p style="margin-top:12px;max-width:520px">Receba em casa, em qualquer lugar do Brasil, ou encontre um ponto de venda pertinho de você. {brl(f["price"])} a lata.</p></div>
      <div class="btn-row" style="position:relative">{cart_btn(f, "yellow")}{btn("Onde comprar", "onde-encontrar.html", "primary", ic="pin", ic_first=True)}</div>
    </div>
  </div>
</section>
'''
    body = f'data-theme="{f["slug"]}"'
    if f.get('header_light'): body += ' data-header="light"'
    if premium: body += ' class="theme-premium"'
    page(fn, f'FRIZZA {full} | {f["slogan"]}',
         f'FRIZZA {full}: {f["desc"][:120].rsplit(" ", 1)[0]}… Ingredientes, informação nutricional e onde comprar.',
         main, 'sabores.html', theme_color=('#7B2D8E' if premium else f['color']), body_attrs=body, serif=bool(premium))

for f in FLAVORS:
    flavor_page(f)

# =================================================================== HISTÓRIA
set_page('historia.html')
TIMELINE = [
    ('2018', 'Nasce em Gramado', 'Duas amigas, uma cozinha e dezenas de receitas testadas. O primeiro lote de Laranja Bahia esgota numa feira de rua da cidade, em uma tarde.', '#FF6B2B', '#B3410C',
     'historia/fundadoras-2018.webp', 'As duas amigas fundadoras da FRIZZA cortando laranjas na cozinha para o primeiro lote, em 2018', 'Barraca simples de feira de rua em Gramado com garrafas de vidro artesanais de refrigerante de laranja, plaquinha escrita à mão "FRIZZA", fundadores atendendo clientes sorridentes, arquitetura típica da Serra Gaúcha ao fundo, luz natural.'),
    ('2019', 'Das redes para os festivais', 'Os vídeos dos bastidores viralizam no Instagram e no TikTok. A FRIZZA vira presença confirmada em festivais de música e feiras orgânicas do Sul.', '#FFD23F', '#8A5A00',
     'onde-encontrar/festival-mulher.webp', 'Mulher em um festival de música segurando uma lata FRIZZA, com o palco da FRIZZA ao fundo', 'Estande colorido da FRIZZA em festival de música ao ar livre, fila de jovens diversos, latas e garrafas coloridas num balde de gelo, bandeirolas, luz do fim de tarde.'),
    ('2020', 'Loja online para todo o Brasil', 'Com o e-commerce, a FRIZZA passa a chegar em qualquer CEP do país, em caixas que viram brinquedo (e casinha de gato).', '#2EC4B6', '#0B7268',
     'historia/timeline-2020.webp', 'Pessoa abrindo uma lata de FRIZZA Laranja Bahia ao lado do notebook', 'Mãos abrindo uma caixa de papelão kraft da FRIZZA em casa, com cinco latas coloridas dentro, papel semente e bilhete escrito à mão, mesa de madeira, luz natural.'),
    ('2022', 'Mais de 200 pontos de venda', 'Empórios, cafés, restaurantes e mercados do Sul e Sudeste abrem suas geladeiras para a FRIZZA.', '#7B2D8E', '#7B2D8E',
     'onde-encontrar/emporio-prateleira.webp', 'Prateleira de madeira de um empório cheia de latas FRIZZA dos cinco sabores', 'Geladeira de vidro de um empório charmoso cheia de latas FRIZZA dos cinco sabores organizadas por cor, atendente sorrindo ao lado, luz quente.'),
    ('2024', 'Chega a Uva Rosé', 'Em parceria com vinícolas de Bento Gonçalves, lançamos a edição especial Serra Gaúcha: para brindar sem precisar de motivo.', '#E8A0BF', '#9A3B67',
     'sabores/ocasiao-uva-rose.webp', 'Brinde com taças de bebida rosada ao lado de uma lata de FRIZZA Uva Rosé', 'Evento de lançamento elegante num vinhedo de Bento Gonçalves ao entardecer, latas rosé da FRIZZA Uva Rosé em uma mesa de madeira com taças e cachos de uva, pessoas brindando.'),
    ('2028', 'A meta: a mais amada do Brasil', 'Queremos ser a marca de refrigerantes artesanais mais amada do país. Com fruta de verdade, gente de verdade e muito gás.', '#FF8C42', '#A3470C',
     'historia/timeline-2028.svg', 'Ilustração: latas FRIZZA espalhadas pelo mapa do Brasil, com um coração no centro', 'Composição lúdica e colorida (ilustração 3D ou colagem) de latas FRIZZA voando sobre um mapa estilizado do Brasil com frutas, bolhas e confetes, gradiente tropical laranja e amarelo.'),
]
tl_items = ''
for i, (year, title, text, c, ink, file, alt, desc) in enumerate(TIMELINE):
    side = 'left' if i % 2 == 0 else 'right'
    tl_items += (f'<li class="timeline__item" style="--tl-c:{c};--tl-ink:{ink}"><span class="timeline__dot" aria-hidden="true"></span>'
                 f'<div class="timeline__card" data-reveal="{side}"><div><span class="timeline__year">{year}</span><h3>{title}</h3><p>{text}</p></div>'
                 f'{slot(file, 1200, 900, alt, desc, "Nossa História → linha do tempo " + year, color=c, pos={"2024": "12% 50%", "2020": "50% 55%", "2018": "50% 55%", "2019": "50% 30%"}.get(year, "50% 45%"))}</div></li>')

VALUES = [('heart', 'Autenticidade', 'A gente é o que parece: sem pose, sem letra miúda.', '#FFD23F'),
          ('brasil', 'Brasilidade', 'Fruta, gente e jeito brasileiro em cada lata.', '#2EC4B6'),
          ('recycle', 'Sustentabilidade', 'Cuidar do planeta no que dá pra fazer hoje, e melhorar amanhã.', '#8FE3A3'),
          ('bulb', 'Criatividade', 'Sabores que surpreendem e ideias que borbulham.', '#FF8C42'),
          ('users', 'Comunidade', 'Produtores, parceiros e #FRIZZALOVERS: ninguém borbulha sozinho.', '#E8A0BF'),
          ('eye', 'Transparência', 'Ingredientes, números e processos sempre às claras.', '#B98AD0')]
values = ''.join(f'<li class="value" style="--val-c:{c}"><div class="value__icon" aria-hidden="true">{ICONS[ic]}</div><h3>{t}</h3><p>{p}</p></li>' for ic, t, p, c in VALUES)

# Mapa do Brasil (contorno simplificado gerado a partir de lon/lat)
BR = [(-60.7,5.2),(-59.8,4.4),(-58.4,1.9),(-56.5,1.9),(-54.6,2.3),(-52.9,2.2),(-51.6,4.2),(-51.0,3.3),(-50.4,1.8),(-49.9,1.0),(-48.6,-0.2),(-47.8,-0.6),
      (-46.4,-1.0),(-44.7,-1.6),(-44.3,-2.5),(-42.6,-2.7),(-41.4,-2.9),(-39.9,-2.9),(-38.5,-3.7),(-37.2,-4.8),(-35.9,-5.0),(-35.2,-5.6),(-34.8,-7.1),
      (-35.0,-8.4),(-35.7,-9.6),(-36.6,-10.6),(-37.6,-11.6),(-38.5,-13.0),(-38.9,-14.5),(-39.0,-16.2),(-39.3,-17.9),(-39.7,-19.5),(-40.4,-20.6),
      (-41.0,-21.7),(-42.0,-22.9),(-43.2,-23.0),(-44.7,-23.4),(-46.4,-24.1),(-47.9,-25.2),(-48.6,-26.3),(-48.6,-28.0),(-49.6,-29.3),(-50.6,-30.9),
      (-51.6,-32.0),(-52.4,-33.2),(-53.4,-33.7),(-53.5,-32.6),(-54.7,-31.7),(-55.9,-30.9),(-57.6,-30.2),(-56.0,-28.6),(-54.6,-27.2),(-53.7,-26.3),
      (-54.6,-25.5),(-54.3,-24.0),(-55.6,-23.7),(-55.8,-22.3),(-57.8,-22.1),(-58.0,-20.2),(-58.2,-19.8),(-57.6,-18.0),(-58.4,-16.4),(-60.2,-16.2),
      (-60.4,-13.9),(-62.6,-13.0),(-64.4,-12.5),(-65.3,-10.8),(-66.6,-9.9),(-68.0,-10.7),(-69.5,-10.9),(-70.6,-9.5),(-72.2,-9.9),(-73.2,-9.4),
      (-73.8,-7.3),(-72.9,-5.2),(-70.9,-4.4),(-70.0,-4.3),(-69.4,-1.1),(-69.9,1.1),(-67.8,1.8),(-66.9,1.2),(-65.5,0.7),(-64.0,1.9),(-64.2,4.0),
      (-62.7,4.0),(-61.4,4.4),(-60.7,5.2)]
def proj(lon, lat): return ((lon + 75) * 10, (6 - lat) * 10)
pts = [proj(*p) for p in BR]
br_path = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'
ORIGINS = [('reconcavo', 'Recôncavo Baiano · BA', 'Laranjas da Laranja Bahia', (-38.9, -12.6), '#FF8C42', 'sabor-laranja-bahia.html', 'end', -14, 5),
           ('para', 'Cooperativas do Pará · PA', 'Açaí e guaraná da Açaí com Guaraná', (-49.0, -1.8), '#5B2C6F', 'sabor-acai-guarana.html', 'start', 16, 5),
           ('gramado', 'Gramado · RS (nossa casa)', 'Hortelã da horta própria e a fábrica', (-50.4, -29.4), '#00BFA6', 'sabor-limao-hortela.html', 'start', 16, 4),
           ('bento', 'Bento Gonçalves · RS', 'Uvas orgânicas da Uva Rosé', (-51.9, -28.9), '#E8A0BF', 'sabor-uva-rose.html', 'end', -14, -6),
           ('pelotas', 'Pelotas · RS', 'Pêssegos da Pêssego com Gengibre', (-52.3, -31.6), '#FFAB76', 'sabor-pessego-gengibre.html', 'end', -14, 8)]
gx, gy = proj(-50.4, -29.4)
routes = ''
points_svg = ''
legend = ''
for key, name, what, (lon, lat), c, href, anchor, dx, dy in ORIGINS:
    x, y = proj(lon, lat)
    if key != 'gramado':
        cx, cy = (x + gx) / 2 + (40 if x < gx else -40), (y + gy) / 2 - 30
        routes += f'<path class="route" d="M{x:.1f},{y:.1f} Q{cx:.1f},{cy:.1f} {gx:.1f},{gy:.1f}"/>'
    short = name.split(' · ')[0]
    points_svg += (f'<a class="map-point" href="{href}" data-key="{key}" aria-label="{esc(name)}: {esc(what)}">'
                   f'<circle class="pulse" cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{c}" opacity=".5"/>'
                   f'<circle class="core" cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{c}" stroke="#1A1A2E" stroke-width="2.5"/>'
                   f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}">{short}</text></a>')
    _oi = {'reconcavo': ('historia/produtores-laranja-reconcavo.webp', 'Agricultor e menina colhendo laranjas no Recôncavo Baiano', '45% 50%'), 'para': ('historia/acai-colheita.webp', 'Mãos segurando um cacho de açaí recém-colhido na floresta', '75% 45%'), 'gramado': ('historia/horta-hortela-gramado.webp', 'Agricultora colhendo hortelã na horta da FRIZZA em Gramado', '60% 50%'), 'bento': ('historia/vinhedo-bento-goncalves.webp', 'Vinhedos de Bento Gonçalves ao pôr do sol', '72% 50%'), 'pelotas': ('historia/pessegos-pelotas.webp', 'Pessegueiro carregado de pêssegos maduros num pomar ao pôr do sol', '50% 40%')}[key]
    _thumb = img_tag(_oi[0], _oi[1], cls="origin__img" + (" origin__img--svg" if _oi[0].endswith(".svg") else ""), pos=_oi[2], decorative=_oi[0].endswith(".svg"))
    register(_oi[0], 1, 1, _oi[1] or "(decorativo)", "", "Nossa História → origem dos sabores (mapa)", "foto" if not _oi[0].endswith(".svg") else "svg")
    legend += f'<li class="origin" data-origin="{key}" style="--o-c:{c}"><span class="origin__thumb">{_thumb}<span class="origin__dot" aria-hidden="true"></span></span><div><b>{name}</b><span>{what}</span></div></li>'
map_svg = (f'<svg class="brazil-map" data-map viewBox="0 -10 420 420" role="group" aria-label="Mapa do Brasil com a origem dos ingredientes de cada sabor FRIZZA">'
           f'<path class="land-shadow" d="{br_path}" transform="translate(10 12)"/><path class="land" d="{br_path}"/>{routes}{points_svg}</svg>')

hist = f'''
<section class="history-hero" aria-labelledby="hist-title">
  {bubbles_canvas(30)}
  <div class="container" style="position:relative;z-index:2">
    <p class="eyebrow" data-intro-fade style="color:var(--preto-suave)">Nossa história</p>
    <h1 class="page-hero__title" id="hist-title" data-split="words" data-intro>Cada garrafa é uma mini viagem pelo Brasil</h1>
    <p class="page-hero__lead" data-intro-fade>Do Recôncavo Baiano à Serra Gaúcha, passando pelos rios do Pará: a FRIZZA nasceu para provar que dá para ser gostoso, divertido e consciente ao mesmo tempo.</p>
    <div class="history-hero__media" data-intro-fade>{slot("historia/historia-hero.webp", 2100, 900, "Lata de FRIZZA Uva Rosé sobre uma cerca de madeira com hortênsias coloridas e araucárias na névoa da Serra Gaúcha", "", "Nossa História → hero", color="#FFD23F", pos="50% 55%", eager=True, high=True, parallax=True)}</div>
  </div>
  {wave("#FAFAFA")}
</section>

<section class="section" aria-labelledby="start-title">
  <div class="container container--narrow center stack">
    <p class="eyebrow">Como tudo começou</p>
    <h2 id="start-title" data-split="words">Tudo começou com uma pergunta</h2>
    <p class="lead" data-reveal>“Por que refrigerante precisa ter gosto de laboratório?” Em 2018, duas amigas de Gramado, jovens empreendedoras, resolveram responder na cozinha de casa, com fruta brasileira, menos açúcar e um bocado de teimosia.</p>
    <p data-reveal>Deu certo. E continua dando, porque o propósito segue o mesmo: transformar cada gole em uma experiência sensorial que celebra o sabor autêntico do Brasil.</p>
  </div>
</section>

<section class="section section--tight" aria-labelledby="tl-title">
  <div class="container">
    <div class="section-head center"><p class="eyebrow">Linha do tempo</p><h2 id="tl-title" data-split="words">De uma feira de rua para o Brasil inteiro</h2></div>
    <ol class="timeline" role="list" data-timeline><span class="timeline__line" aria-hidden="true"><i></i></span>{tl_items}</ol>
  </div>
</section>

<section class="section" aria-labelledby="pmv-title">
  <div class="container">
    <div class="section-head"><p class="eyebrow">No que a gente acredita</p><h2 id="pmv-title" data-split="words">Propósito, missão e visão</h2></div>
    <ul class="pmv" role="list" data-stagger>
      <li class="pmv__card">{icon("heart")}<h3>Propósito</h3><p>Transformar cada gole em uma experiência sensorial que celebra o sabor autêntico do Brasil, provando que dá para ser gostoso, divertido e consciente ao mesmo tempo.</p></li>
      <li class="pmv__card">{icon("target")}<h3>Missão</h3><p>Criar refrigerantes que respeitem o paladar, o corpo e o planeta, com ingredientes naturais brasileiros e processos sustentáveis.</p></li>
      <li class="pmv__card">{icon("compass")}<h3>Visão</h3><p>Ser a marca de refrigerantes artesanais mais amada do país até 2028.</p></li>
    </ul>
    <div class="section-head" style="margin-top:clamp(70px,9vw,120px)"><p class="eyebrow">Nossos valores</p><h2 data-split="words">Seis ingredientes que não estão no rótulo</h2></div>
    <ul class="values" role="list" data-stagger>{values}</ul>
  </div>
</section>

<section class="section section--pastel" data-theme="menta" aria-labelledby="map-title">
  <div class="container map-wrap">
    <div data-reveal="scale">{map_svg}</div>
    <div class="stack">
      <p class="eyebrow">Brasilidade</p>
      <h2 id="map-title" data-split="words">De onde vem cada sabor</h2>
      <p class="lead" data-reveal>Cada ingrediente tem endereço, sobrenome e história. Passe o mouse (ou toque) nos pontos do mapa para conhecer a origem.</p>
      <ul class="origins" role="list" data-stagger>{legend}</ul>
    </div>
  </div>
</section>

<section class="section" id="sustentabilidade" aria-labelledby="sus-title">
  <div class="container">
    <div class="grid-2" style="margin-bottom:clamp(50px,7vw,90px)">
      <div class="stack">
        <p class="eyebrow">Sustentabilidade</p>
        <h2 id="sus-title" data-split="words">Fazer bem feito, do pé de fruta à garrafa de volta</h2>
        <p class="lead" data-reveal>A gente não é perfeito, e não vai fingir que é. Mas leva a sério cada escolha que dá pra fazer melhor, e conta tudo por aqui, com números.</p>
      </div>
      {slot("historia/colheita-acai.webp", 1080, 1350, "Coletor subindo num açaizeiro para colher um cacho de açaí na floresta amazônica", "", "Nossa História → sustentabilidade", color="#2EC4B6", reveal="mask", pos="50% 40%", parallax=True)}
    </div>
    <ul class="sust" role="list" data-stagger>
      <li class="sust__card">{slot("historia/rio-para-aerea.webp", 16, 10, "Vista aérea de um rio amazônico com casas ribeirinhas entre a floresta ao amanhecer", "", "Nossa História → card pequenos produtores", cls="sust__img")}{icon("hands")}<h3>Pequenos produtores</h3><p>Compramos direto de 23 famílias de agricultores e cooperativas, com preço justo e contrato de longo prazo.</p></li>
      <li class="sust__card">{slot("historia/plantio-vista-alto.webp", 16, 10, "Vista do alto de uma plantação comunitária, com pessoas plantando mudas em canteiros", "", "Nossa História → card árvores", cls="sust__img", pos="50% 55%")}{icon("tree")}<h3>Compensação com árvores</h3><p>A cada lote produzido, plantamos árvores nativas em parceria com projetos de reflorestamento da Mata Atlântica.</p></li>
      <li class="sust__card">{slot("historia/reciclagem-festival.webp", 16, 10, "Jovem sorridente depositando uma lata numa estação de reciclagem FRIZZA em um festival", "", "Nossa História → card logística reversa", cls="sust__img", pos="45% 50%")}{icon("recycle")}<h3>Logística reversa</h3><p>Garrafas de vidro voltam para a fábrica, são higienizadas e enchidas de novo. Devolva nos pontos de coleta e ganhe desconto.</p></li>
    </ul>
  </div>
</section>

<section class="section section--light-stats section--pastel" data-theme="menta" aria-labelledby="sus-num-title">
  <div class="container">
    <h2 class="sr-only" id="sus-num-title">Números de impacto</h2>
    <ul class="stats" role="list" data-stagger>
      {stat("hands", 23, "famílias de agricultores parceiros")}
      {stat("tree", 5000, "árvores plantadas", "+", "", "Mais de 5.000")}
      {stat("recycle", 180000, "embalagens de vidro retornadas", "+", "", "Mais de 180.000")}
      {stat("bottle", 2, "milhões de garrafas vendidas", "+", "", "Mais de 2")}
    </ul>
  </div>
</section>

<section class="section" aria-labelledby="awards-title">
  <div class="container">
    <div class="section-head center"><p class="eyebrow">Reconhecimento</p><h2 id="awards-title" data-split="words">Prêmios e selos</h2>
      <p>Prêmio bom é cliente feliz. Mas estes aqui a gente também comemorou muito.</p></div>
    <ul class="awards" role="list" data-stagger>{"".join(f'<li>{seal_from(s, "-h")}<p>{s["title"]}<br><span class="muted">{s["text"]}</span></p></li>' for s in SEALS)}</ul>
  </div>
</section>
'''
page('historia.html', 'Nossa História | FRIZZA Refrigerantes',
     'Da cozinha em Gramado (2018) para mais de 200 pontos de venda: conheça a história, o propósito, os valores e a sustentabilidade da FRIZZA.',
     hist, 'historia.html', theme_color='#2EC4B6', body_attrs='data-theme="menta"')

# =================================================================== ONDE ENCONTRAR
set_page('onde-encontrar.html')
STORES = [
    ('Curitiba', 'PR', 'Empório Araucária', 'Empório', 'Rua das Araucárias, 120 · Centro'),
    ('Curitiba', 'PR', 'Café Pinhão', 'Café', 'Alameda dos Pinheirais, 455 · Batel'),
    ('Curitiba', 'PR', 'Mercado Verde Vivo', 'Mercado', 'Av. das Hortas, 2.010 · Água Verde'),
    ('Londrina', 'PR', 'Armazém Pé Vermelho', 'Empório', 'Rua do Café, 88 · Centro'),
    ('Florianópolis', 'SC', 'Mercadinho Ilha Natural', 'Mercado', 'Rua da Lagoa, 301 · Lagoa da Conceição'),
    ('Florianópolis', 'SC', 'Bistrô Maré Alta', 'Restaurante', 'Av. das Gaivotas, 77 · Jurerê'),
    ('Blumenau', 'SC', 'Empório do Vale', 'Empório', 'Rua dos Enxaimeis, 540 · Centro'),
    ('Gramado', 'RS', 'Loja Conceito FRIZZA', 'Loja oficial', 'Av. das Hortênsias, 1.800 · Centro'),
    ('Gramado', 'RS', 'Café da Serra', 'Café', 'Rua do Lago Negro, 210 · Planalto'),
    ('Porto Alegre', 'RS', 'Empório Redenção', 'Empório', 'Rua dos Ipês, 1.020 · Bom Fim'),
    ('Porto Alegre', 'RS', 'Café Guaíba', 'Café', 'Rua do Pôr do Sol, 64 · Cidade Baixa'),
    ('Bento Gonçalves', 'RS', 'Casa do Vale dos Vinhedos', 'Empório', 'Estrada dos Vinhedos, km 4'),
    ('Caxias do Sul', 'RS', 'Mercado Serra Viva', 'Mercado', 'Rua das Uvas, 900 · São Pelegrino'),
    ('São Paulo', 'SP', 'Empório Vila Madalena', 'Empório', 'Rua dos Grafites, 233 · Vila Madalena'),
    ('São Paulo', 'SP', 'Mercado Orgânico Pinheiros', 'Mercado', 'Rua das Feiras, 1.440 · Pinheiros'),
    ('São Paulo', 'SP', 'Café Paulista Natural', 'Café', 'Alameda Central, 15 · Bela Vista'),
    ('Campinas', 'SP', 'Armazém Barão', 'Empório', 'Av. dos Estudantes, 702 · Barão Geraldo'),
    ('Rio de Janeiro', 'RJ', 'Quiosque Leblon Natural', 'Quiosque', 'Orla do Leblon, posto 11'),
    ('Rio de Janeiro', 'RJ', 'Hortifruti Botafogo Bem', 'Mercado', 'Rua das Palmeiras, 410 · Botafogo'),
    ('Niterói', 'RJ', 'Empório Icaraí', 'Empório', 'Rua da Praia, 98 · Icaraí'),
    ('Belo Horizonte', 'MG', 'Café Savassi', 'Café', 'Rua dos Baristas, 350 · Savassi'),
    ('Belo Horizonte', 'MG', 'Empório Pampulha', 'Empório', 'Av. da Lagoa, 1.900 · Pampulha'),
    ('Belo Horizonte', 'MG', 'Mercado Serra do Curral', 'Mercado', 'Rua das Montanhas, 77 · Serra'),
]
UF_NAMES = {'PR': 'Paraná', 'SC': 'Santa Catarina', 'RS': 'Rio Grande do Sul', 'SP': 'São Paulo', 'RJ': 'Rio de Janeiro', 'MG': 'Minas Gerais'}
colors = [f['color'] for f in FLAVORS]
from urllib.parse import quote
MAPS_OVERRIDE = {
    'Loja Conceito FRIZZA': 'Avenida das Hortênsias, Gramado - RS',
    'Casa do Vale dos Vinhedos': 'Vale dos Vinhedos, Bento Gonçalves - RS',
    'Quiosque Leblon Natural': 'Praia do Leblon, Rio de Janeiro - RJ',
}
def maps_query(city, uf, name, addr):
    # Endereços fictícios: o mapa aponta para o bairro real da cidade.
    # Quando houver endereços reais, troque esta função (ou MAPS_OVERRIDE) pelo endereço completo.
    if name in MAPS_OVERRIDE: return MAPS_OVERRIDE[name]
    bairro = addr.split(' · ')[1] if ' · ' in addr else ''
    return f'{bairro + ", " if bairro else ""}{city} - {uf}'
def maps_link(q): return 'https://www.google.com/maps/search/?api=1&amp;query=' + quote(q + ', Brasil')
DEFAULT_STORE = 'Loja Conceito FRIZZA'
stores = ''
for i, (city, uf, name, typ, addr) in enumerate(STORES):
    q = maps_query(city, uf, name, addr)
    act = name == DEFAULT_STORE
    stores += (f'<li class="store{" is-active" if act else ""}" data-uf="{uf}" data-search="{esc(city + " " + uf + " " + UF_NAMES[uf] + " " + name + " " + addr)}" '
               f'data-name="{esc(name)}" data-address="{esc(addr + " — " + city + " · " + uf)}" data-maps-q="{esc(q + ", Brasil")}" style="--store-c:{colors[i % 5]}">'
               f'<button class="store__select" type="button" aria-pressed="{"true" if act else "false"}" aria-controls="stores-map" aria-label="Mostrar {esc(name)} no mapa"></button>'
               f'<span class="store__type">{typ}</span><h3>{name}</h3><p class="store__city">{icon("pin")}{city} · {uf}</p><p>{addr}</p>'
               f'<a class="store__maps" href="{maps_link(q)}" target="_blank" rel="noopener" aria-label="Abrir {esc(name)} no Google Maps (nova aba)">{icon("compass")}Abrir no Google Maps</a></li>')
_d = [s_ for s_ in STORES if s_[2] == DEFAULT_STORE][0]
DEFAULT_Q = maps_query(_d[0], _d[1], _d[2], _d[4]) + ', Brasil'
chips = '<button class="filter-btn" type="button" data-uf="todos" aria-pressed="true">Todos</button>' + ''.join(
    f'<button class="filter-btn" type="button" data-uf="{uf}" aria-pressed="false" aria-label="{UF_NAMES[uf]}">{uf}</button>' for uf in UF_NAMES)
EVENTS = [('onde-encontrar/festival-mulher.webp', 'Janeiro', 'Festival Verão Orgânico', 'Florianópolis · SC', 'Praia, música ao vivo e estande FRIZZA com degustação gelada dos 5 sabores.',
           'Festival de verão na praia em Florianópolis, estande colorido da FRIZZA com guarda-sol, pessoas diversas em roupas de praia provando refrigerante, mar azul ao fundo, luz forte do meio-dia.'),
          ('historia/reciclagem-festival.webp', 'Junho', 'Feira Brasil Orgânico', 'São Paulo · SP', 'Onde levamos o prêmio de Melhor Refrigerante Artesanal em 2023. Vem brindar com a gente!',
           'Feira de produtos orgânicos em pavilhão arejado em São Paulo, estande de madeira da FRIZZA com garrafas e frutas expostas, visitantes provando em copinhos, luz natural.'),
          ('historia/historia-hero.webp', 'Julho', 'Festival de Inverno da Serra', 'Gramado · RS', 'Em casa! Lançamentos de safra da Uva Rosé, oficinas de mocktail e muita bolha.',
           'Festival de inverno ao ar livre em Gramado à noite, luzinhas penduradas, pessoas agasalhadas e sorridentes segurando latas FRIZZA, barracas de madeira, clima aconchegante.')]
events = ''.join(f'<li class="event">{slot(file, 1200, 800, ["Mulher em um festival de música segurando uma lata FRIZZA, com o palco da FRIZZA ao fundo", "Público de festival ao ar livre e estação de reciclagem de latas da FRIZZA", "Lata de FRIZZA Uva Rosé com hortênsias e araucárias na Serra Gaúcha"][i], desc, "Onde Encontrar → festivais e feiras", color=["#2EC4B6","#FFD23F","#E8A0BF"][i], pos=["50% 28%", "50% 50%", "100% 50%"][i])}'
                 f'<div class="event__body"><p class="event__date">{icon("tent")}{month} · {where}</p><h3>{title}</h3><p>{txt}</p></div></li>'
                 for i, (file, month, title, where, txt, desc) in enumerate(EVENTS))
onde = f'''
<section class="page-hero" data-theme="laranja-bahia" aria-labelledby="onde-title">
  {bubbles_canvas(30)}
  <div class="container grid-2 onde-hero" style="position:relative;z-index:2">
    <div>
    <p class="eyebrow" data-intro-fade>Mais de 200 pontos no Sul e Sudeste</p>
    <h1 class="page-hero__title" id="onde-title" data-split="chars" data-intro>Onde encontrar</h1>
    <p class="page-hero__lead" data-intro-fade>Procure pela sua cidade ou estado e descubra a geladeira mais próxima com FRIZZA. Prefere receber em casa? Compre aqui no site e a gente entrega no Brasil todo.</p>
    <div class="btn-row" style="margin-top:28px" data-intro-fade>{btn("Comprar online", "sabores.html", "dark", ic="cart", ic_first=True)}</div>
    </div>
    <div data-intro-fade>{slot("onde-encontrar/emporio-prateleira.webp", 4, 3, "Prateleira de madeira de um empório cheia de latas FRIZZA dos cinco sabores, com plantas ao redor", "", "Onde Encontrar → hero", pos="35% 50%", eager=True, high=True, parallax=True)}</div>
  </div>
  {wave("#FAFAFA")}
</section>

<section class="section section--tight" style="padding-top:0" aria-labelledby="finder-title">
  <div class="container finder" data-store-finder>
    <div class="finder__box" data-reveal>
      <h2 class="h3" id="finder-title" style="margin-bottom:16px">Buscar ponto de venda</h2>
      <form role="search" aria-label="Buscar pontos de venda">
        <div class="search-field">{icon("search")}
          <label for="busca-cidade" class="sr-only">Digite sua cidade, estado ou bairro</label>
          <input id="busca-cidade" type="search" placeholder="Digite sua cidade, estado ou bairro" autocomplete="address-level2">
        </div>
      </form>
      <div class="chips" role="group" aria-label="Filtrar por estado">{chips}</div>
      <p class="finder__status" id="stores-status" role="status" aria-live="polite">{len(STORES)} pontos de venda encontrados</p>
    </div>
    <div class="stores-layout">
      <div>
        <ul class="stores" role="list" data-stagger>{stores}</ul>
        <div class="stores-empty"><p><strong>Ainda não chegamos aí 😢</strong></p><p>Mas a gente entrega em qualquer CEP do Brasil!</p><p style="margin-top:14px">{btn("Comprar online", "sabores.html", "primary", ic="cart", ic_first=True, size="btn--sm")}</p></div>
      </div>
      <figure class="stores-map" id="stores-map" data-reveal tabindex="-1">
        <iframe title="Mapa do ponto de venda selecionado: {DEFAULT_STORE}" src="https://www.google.com/maps?q={quote(DEFAULT_Q)}&amp;z=15&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        <figcaption>
          <p class="stores-map__hint">Clique em um ponto de venda para ver no mapa</p>
          <strong class="stores-map__name" aria-live="polite">{DEFAULT_STORE}</strong>
          <span class="stores-map__address">{_d[4]} — {_d[0]} · {_d[1]}</span>
          {btn("Abrir no Google Maps", maps_link(DEFAULT_Q.replace(", Brasil", "")), "primary", ic="compass", ic_first=True, size="btn--sm stores-map__link", attrs='target="_blank" rel="noopener"', magnetic=False)}
        </figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="section section--pastel" data-theme="solar" aria-labelledby="fest-title">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Ao vivo e a cores</p><h2 id="fest-title" data-split="words">Encontre a FRIZZA em festivais e feiras</h2>
      <p>Degustação gelada, música boa e gente legal. Confira onde a gente vai estar este ano.</p></div>
    <ul class="events" role="list" data-stagger>{events}</ul>
  </div>
</section>
'''
page('onde-encontrar.html', 'Onde Encontrar | FRIZZA Refrigerantes',
     'Encontre a FRIZZA em mais de 200 pontos de venda no Sul e Sudeste ou compre online com entrega para todo o Brasil.',
     onde, 'onde-encontrar.html', body_attrs='data-theme="laranja-bahia"')

# =================================================================== #FRIZZALOVERS
set_page('frizzalovers.html')
pols = ''.join(f'<div class="polaroid polaroid--{i+1}" data-parallax="{[0.3,0.5,0.4,0.2][i]}">{slot(f"comunidade/polaroid-{i+1:02d}.webp", 1, 1, "", "", "#FRIZZALOVERS → hero (polaroids)", eager=True, decorative=True)}</div>'
               for i in range(4))
gallery = ''
for (file, w, h, user, cap, desc, pos) in LOVERS:
    alt = f'Foto de @{user}: {desc}'
    gallery += (f'<li class="masonry__item"><button class="masonry__btn" type="button" data-lightbox data-user="@{user}" data-caption="{esc(cap)}" data-alt="{esc(alt)}" aria-label="Ampliar foto de @{user}" data-cursor="ver">'
                f'{slot(file, w, h, alt, desc, "#FRIZZALOVERS → galeria + lightbox", pos=pos)}'
                f'<span class="masonry__meta" aria-hidden="true"><b>{icon("instagram")}@{user}</b><span>{cap}</span></span></button></li>')
lovers = f'''
<section class="lovers-hero on-dark" aria-labelledby="lov-title">
  {bubbles_canvas(40)}
  <div class="lovers-hero__polaroids" aria-hidden="true">{pols}</div>
  <div class="container" style="position:relative;z-index:2">
    <p class="eyebrow" data-intro-fade>Galeria da comunidade</p>
    <h1 class="lovers-hero__tag" id="lov-title" aria-label="#FRIZZALOVERS"><span data-split="chars" data-intro data-wave><span class="hash">#</span>FRIZZALOVERS</span></h1>
    <p class="page-hero__lead" style="margin-inline:auto" data-intro-fade>Momentos de verdade de quem borbulha com a gente. Praia, parque, varanda, festival… onde tem FRIZZA, tem história boa.</p>
    <div class="btn-row" style="justify-content:center;margin-top:30px" data-intro-fade>{btn("Postar no Instagram", "https://www.instagram.com/frizzaoficial/", "yellow", ic="instagram", ic_first=True, attrs=f'data-demo="{DEMO_SOCIAL}" target="_blank" rel="noopener"')}</div>
  </div>
  {wave("#FAFAFA")}
</section>

<section class="section" aria-labelledby="gal-title">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Feed da comunidade</p><h2 id="gal-title" data-split="words">Quem já está borbulhando</h2><p>Clique em uma foto para ampliar.</p></div>
    <ul class="masonry" role="list">{gallery}</ul>
  </div>
</section>

<dialog class="lightbox" id="lightbox" aria-label="Foto ampliada da galeria #FRIZZALOVERS">
  <button class="lightbox__btn lightbox__close" type="button" aria-label="Fechar">{icon("close")}</button>
  <div class="lightbox__inner">
    <div class="lightbox__media"></div>
    <div class="lightbox__info">
      <b>{icon("instagram")}<span class="lightbox__user"></span></b>
      <p class="lightbox__caption"></p>
      <div class="lightbox__nav">
        <button class="lightbox__btn lightbox__btn--prev" type="button" aria-label="Foto anterior">{icon("arrow")}</button>
        <button class="lightbox__btn lightbox__btn--next" type="button" aria-label="Próxima foto">{icon("arrow")}</button>
      </div>
    </div>
  </div>
</dialog>

<section class="section section--pastel" data-theme="roxo" aria-labelledby="how-title">
  <div class="container">
    <div class="section-head center"><p class="eyebrow">Sua vez</p><h2 id="how-title" data-split="words">Como aparecer aqui</h2></div>
    <ol class="steps" role="list" data-stagger>
      <li class="step"><span class="step__num" aria-hidden="true">1</span>{icon("cart")}<h3>Compre sua FRIZZA</h3><p>Num ponto de venda pertinho de você ou na loja online.</p></li>
      <li class="step"><span class="step__num" aria-hidden="true">2</span>{icon("camera")}<h3>Poste com #FRIZZALOVERS</h3><p>No feed, nos stories ou no TikTok. Vale piquenique, praia, festival…</p></li>
      <li class="step"><span class="step__num" aria-hidden="true">3</span>{icon("heart")}<h3>Marque @frizzaoficial</h3><p>A gente escolhe as favoritas toda semana para aparecer aqui.</p></li>
    </ol>
  </div>
</section>

<section class="section section--dark on-dark overflow-clip" aria-labelledby="soc-title">
  {bubbles_canvas(24, color="255, 210, 63")}
  <div class="container" style="position:relative;z-index:1">
    <div class="section-head"><p class="eyebrow">Siga a FRIZZA</p><h2 id="soc-title" data-split="words">A gente borbulha nas redes também</h2></div>
    <ul class="socials-grid" role="list" data-stagger>
      <li><a class="social-card" href="https://www.instagram.com/frizzaoficial/" data-demo="{DEMO_SOCIAL}" target="_blank" rel="noopener">{icon("instagram")}<span class="social-card__num" aria-hidden="true" data-count="127" data-suffix=" mil">127 mil</span><span>seguidores no Instagram <span class="sr-only">(127 mil)</span></span><span class="social-card__cta">@frizzaoficial {icon("arrow")}</span></a></li>
      <li><a class="social-card" href="https://www.tiktok.com/@frizzaoficial" data-demo="{DEMO_SOCIAL}" target="_blank" rel="noopener">{icon("tiktok")}<span class="social-card__num" aria-hidden="true" data-count="89" data-suffix=" mil">89 mil</span><span>seguidores no TikTok <span class="sr-only">(89 mil)</span></span><span class="social-card__cta">@frizzaoficial {icon("arrow")}</span></a></li>
      <li><a class="social-card" href="https://www.youtube.com/@frizzarefrigerantes" data-demo="{DEMO_SOCIAL}" target="_blank" rel="noopener">{icon("youtube")}<span class="social-card__num" aria-hidden="true" data-count="12" data-suffix=" mil">12 mil</span><span>inscritos no YouTube <span class="sr-only">(12 mil)</span></span><span class="social-card__cta">FRIZZA Refrigerantes {icon("arrow")}</span></a></li>
      <li><a class="social-card" href="https://www.linkedin.com/company/frizza-bebidas" data-demo="{DEMO_SOCIAL}" target="_blank" rel="noopener">{icon("linkedin")}<span class="social-card__num" aria-hidden="true" data-count="3.4" data-decimals="1" data-suffix=" mil">3,4 mil</span><span>seguidores no LinkedIn <span class="sr-only">(3,4 mil)</span></span><span class="social-card__cta">FRIZZA Bebidas {icon("arrow")}</span></a></li>
    </ul>
  </div>
</section>
'''
page('frizzalovers.html', '#FRIZZALOVERS | FRIZZA Refrigerantes',
     'Galeria da comunidade FRIZZA: poste sua FRIZZA com #FRIZZALOVERS, marque @frizzaoficial e apareça aqui.',
     lovers, 'frizzalovers.html', theme_color='#7B2D8E', body_attrs='data-theme="roxo" data-header="light"')

# =================================================================== CONTATO
set_page('contato.html')
FAQ = [('Onde comprar a FRIZZA?', 'Em mais de 200 pontos de venda no Sul e Sudeste (empórios, cafés, mercados e restaurantes) e na nossa loja online, que entrega em todo o Brasil. Use a busca da página <a href="onde-encontrar.html">Onde Encontrar</a> para achar o ponto mais perto de você.'),
       ('A FRIZZA tem conservantes?', 'Não. Nenhum sabor tem conservantes, corantes ou aromas artificiais. A cor e o sabor vêm das frutas, dos extratos naturais e do açúcar demerara orgânico. Por isso, depois de aberta, guarde na geladeira e consuma em até 2 dias.'),
       ('Quanto açúcar tem cada lata?', 'Depende do sabor: de 10 g (Limão com Hortelã, só 45 kcal) a 24 g (Uva Rosé) por lata de 350 ml, contando o açúcar da própria fruta. Isso é até 40% menos que refrigerantes tradicionais. A tabela completa está na página de cada sabor.'),
       ('Como devolver as garrafas de vidro?', 'É fácil: leve as garrafas vazias (não precisa lavar muito, só enxaguar) a qualquer ponto de venda participante ou à nossa loja em Gramado. A cada 6 garrafas devolvidas, você ganha desconto na próxima compra. Elas são higienizadas e voltam a ser usadas.'),
       ('A Uva Rosé tem álcool?', 'Não! A FRIZZA Uva Rosé tem 0% de álcool. Ela é feita com suco de uva rosé orgânica e água de rosas, e tem bolhas finas estilo espumante, mas é um refrigerante. Pode servir para todo mundo brindar junto.'),
       ('Vocês vendem para revenda?', 'Sim! Se você tem um empório, café, restaurante ou mercado, escolha o assunto “Revenda” no formulário ou chame no WhatsApp que nosso time comercial responde em até 1 dia útil.')]
faq = ''.join(f'<div class="faq__item{" is-open" if i == 0 else ""}"><h3><button class="faq__q" type="button" aria-expanded="{"true" if i == 0 else "false"}" aria-controls="faq-{i}" id="faq-q-{i}">{q}<span class="faq__icon" aria-hidden="true"></span></button></h3>'
              f'<div class="faq__a" id="faq-{i}" role="region" aria-labelledby="faq-q-{i}"><div><p>{a}</p></div></div></div>' for i, (q, a) in enumerate(FAQ))
contato = f'''
<section class="page-hero" data-theme="solar" aria-labelledby="ct-title">
  {bubbles_canvas(28)}
  <div class="container grid-2" style="position:relative;z-index:2">
    <div>
      <p class="eyebrow" data-intro-fade>Contato</p>
      <h1 class="page-hero__title" id="ct-title" data-split="chars" data-intro>Fala com a gente!</h1>
      <p class="page-hero__lead" data-intro-fade>Dúvida, sugestão, revenda ou só vontade de dar um oi? A gente responde rapidinho, de verdade. O jeito mais rápido é pelo WhatsApp.</p>
    </div>
    <div data-intro-fade>{slot("comunidade/contato-hero.webp", 1200, 900, "Duas amigas rindo ao ar livre, cada uma com uma lata FRIZZA na mão", "", "Contato → hero", color="#FF6B2B", pos="50% 22%", eager=True, high=True, parallax=True)}</div>
  </div>
  {wave("#FAFAFA")}
</section>

<section class="section section--tight" style="padding-top:0" aria-label="Canais de atendimento">
  <div class="container">
    <ul class="contact-quick" role="list" data-stagger>
      <li><a class="contact-card contact-card--wa" href="https://wa.me/5554999990000?text=Ol%C3%A1%2C%20FRIZZA!" data-demo="{DEMO_CONTACT}">{icon("whatsapp")}<small>Chame no WhatsApp</small><strong>(54) 99999-0000</strong><small>Seg. a sáb., das 8h às 20h</small></a></li>
      <li><a class="contact-card" href="mailto:oi@frizza.com.br" data-demo="{DEMO_CONTACT}" style="--cc-bg:var(--verde-menta)">{icon("mail")}<small>Mande um e-mail</small><strong>oi@frizza.com.br</strong><small>Respondemos em até 1 dia útil</small></a></li>
      <li><a class="contact-card" href="tel:+555430000000" data-demo="{DEMO_CONTACT}" style="--cc-bg:var(--laranja-vibrante)">{icon("phone")}<small>Ligue para a gente</small><strong>(54) 3000-0000</strong><small>Seg. a sex., das 9h às 18h</small></a></li>
    </ul>
  </div>
</section>

<section class="section section--tight" aria-labelledby="form-title">
  <div class="container contact-layout">
    <div>
      <div class="section-head" style="margin-bottom:28px"><p class="eyebrow">Formulário</p><h2 id="form-title" data-split="words">Escreva sua mensagem</h2><p>Os campos com <span class="req" style="color:var(--laranja-ink)">*</span> são obrigatórios.</p></div>
      <form class="form" data-validate aria-labelledby="form-title" data-reveal>
        <div class="field" data-msg-empty="Conta pra gente como você se chama.">
          <label for="ct-nome">Nome <span class="req" aria-hidden="true">*</span></label>
          <input id="ct-nome" name="nome" type="text" autocomplete="name" required aria-describedby="ct-nome-err">
          <p class="field__error" id="ct-nome-err">{icon("close")}<span></span></p>
        </div>
        <div class="field" data-msg-empty="Precisamos do seu e-mail para responder.">
          <label for="ct-email">E-mail <span class="req" aria-hidden="true">*</span></label>
          <input id="ct-email" name="email" type="email" autocomplete="email" placeholder="nome@email.com" required aria-describedby="ct-email-hint ct-email-err">
          <p class="field__hint" id="ct-email-hint">É por ele que vamos te responder.</p>
          <p class="field__error" id="ct-email-err">{icon("close")}<span></span></p>
        </div>
        <fieldset class="field radio-pills" data-msg-empty="Escolha o assunto da mensagem.">
          <legend>Assunto <span class="req" aria-hidden="true">*</span></legend>
          <input type="radio" id="as-duvida" name="assunto" value="duvida" required aria-describedby="ct-assunto-err"><label for="as-duvida">Dúvida</label>
          <input type="radio" id="as-revenda" name="assunto" value="revenda"><label for="as-revenda">Revenda</label>
          <input type="radio" id="as-imprensa" name="assunto" value="imprensa"><label for="as-imprensa">Imprensa</label>
          <input type="radio" id="as-parcerias" name="assunto" value="parcerias"><label for="as-parcerias">Parcerias</label>
          <p class="field__error" id="ct-assunto-err" style="flex-basis:100%">{icon("close")}<span></span></p>
        </fieldset>
        <div class="field" data-msg-empty="Escreva sua mensagem, pode ser curtinha." data-msg-short="Conta um pouquinho mais: pelo menos 10 caracteres.">
          <label for="ct-msg">Mensagem <span class="req" aria-hidden="true">*</span></label>
          <textarea id="ct-msg" name="mensagem" minlength="10" required aria-describedby="ct-msg-err"></textarea>
          <p class="field__error" id="ct-msg-err">{icon("close")}<span></span></p>
        </div>
        <p data-form-msg role="status" aria-live="polite" style="font-weight:600;color:#B71C1C"></p>
        <div><button class="btn btn--primary btn--lg" type="submit" data-magnetic><span>Enviar mensagem</span>{icon("send")}<span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></button></div>
        <div class="form-success" role="status" aria-live="polite">
          <svg class="check" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="46"/><path d="M30 52 l14 14 l27 -30"/></svg>
          <h3>Mensagem enviada!</h3>
          <p>Valeu por escrever! A gente responde em até 1 dia útil. 🫧<br><span class="small">(Demonstração: nenhum dado foi enviado de verdade.)</span></p>
          <button class="btn btn--dark btn--sm" type="button" data-form-again><span>Enviar outra mensagem</span></button>
        </div>
      </form>
    </div>
    <div id="faq">
      <div class="section-head" style="margin-bottom:28px"><p class="eyebrow">Perguntas frequentes</p><h2 data-split="words">Tira-dúvidas</h2></div>
      <div class="faq" data-stagger>{faq}</div>
    </div>
  </div>
</section>

<section class="section section--dark on-dark" id="imprensa" aria-labelledby="press-title">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Imprensa, parceiros e investidores</p><h2 id="press-title" data-split="words">Vamos fazer algo juntos?</h2></div>
    <ul class="press" role="list" data-stagger>
      <li class="press__card">{icon("news")}<h3>Imprensa</h3><p>Kit de imprensa, fotos em alta e entrevistas com as fundadoras.</p><a href="mailto:imprensa@frizza.com.br" data-demo="{DEMO_CONTACT}">imprensa@frizza.com.br</a></li>
      <li class="press__card">{icon("handshake")}<h3>Parceiros e revenda</h3><p>Quer FRIZZA na sua geladeira, no seu cardápio ou no seu evento?</p><a href="mailto:parcerias@frizza.com.br" data-demo="{DEMO_CONTACT}">parcerias@frizza.com.br</a></li>
      <li class="press__card">{icon("chart")}<h3>Investidores</h3><p>Conheça nossos números, metas para 2028 e o relatório de impacto.</p><a href="mailto:ri@frizza.com.br" data-demo="{DEMO_CONTACT}">ri@frizza.com.br</a></li>
    </ul>
  </div>
</section>
'''
page('contato.html', 'Contato | FRIZZA Refrigerantes',
     'Fale com a FRIZZA pelo WhatsApp, e-mail ou formulário. Perguntas frequentes sobre ingredientes, açúcar, devolução de garrafas e revenda.',
     contato, 'contato.html', theme_color='#FFD23F', body_attrs='data-theme="solar" data-cta="orange"')


# =================================================================== CHECKOUT
set_page('checkout.html')
UFS = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
uf_opts = '<option value="">Selecione</option>' + ''.join(f'<option value="{u}">{u}</option>' for u in UFS)
def field(id_, label, typ='text', ac='', req=True, extra='', hint='', msg='', width=''):
    r = ' required' if req else ''
    star = ' <span class="req" aria-hidden="true">*</span>' if req else ' <span class="muted small">(opcional)</span>'
    h = f'<p class="field__hint" id="{id_}-hint">{hint}</p>' if hint else ''
    desc = f'{id_}-hint {id_}-err' if hint else f'{id_}-err'
    m = f' data-msg-empty="{msg}"' if msg else ''
    return (f'<div class="field {width}"{m}><label for="{id_}">{label}{star}</label>'
            f'<input id="{id_}" name="{id_}" type="{typ}" autocomplete="{ac or "off"}"{r} {extra} aria-describedby="{desc}">{h}'
            f'<p class="field__error" id="{id_}-err">{icon("close")}<span></span></p></div>')
checkout = f'''
<section class="page-hero checkout-hero" data-theme="solar" aria-labelledby="co-title">
  <div class="container" style="position:relative;z-index:2">
    <p class="eyebrow" data-intro-fade>Loja FRIZZA</p>
    <h1 class="page-hero__title checkout-hero__title" id="co-title" data-split="words" data-intro>Finalizar compra</h1>
    <ol class="co-steps" role="list" aria-label="Etapas da compra">
      <li class="is-current" data-co-step-label="0"><span>1</span>Seus dados</li>
      <li data-co-step-label="1"><span>2</span>Entrega</li>
      <li data-co-step-label="2"><span>3</span>Pagamento</li>
      <li data-co-step-label="3"><span>{icon("check")}</span>Pronto!</li>
    </ol>
  </div>
  {wave("#FAFAFA")}
</section>

<section class="section section--tight" aria-label="Formulário de compra" data-checkout>
  <div class="container checkout">
    <div class="checkout__main">
      <div class="co-empty" data-co-empty hidden>{icon("cart")}<h2>Seu carrinho está vazio</h2><p>Escolha seus sabores favoritos e volte aqui para finalizar.</p>
        {btn("Ver sabores", "sabores.html", "primary", ic="arrow")}</div>

      <form class="form co-form" data-co-form novalidate aria-label="Dados da compra">
        <fieldset class="co-panel is-current" data-co-panel="0">
          <legend class="h3">1. Seus dados</legend>
          <div class="co-grid">
            {field("co-nome", "Nome completo", ac="name", msg="Digite seu nome completo.", width="co-full")}
            {field("co-email", "E-mail", "email", "email", extra='placeholder="nome@email.com"', hint="Enviamos a confirmação do pedido para ele.", msg="Precisamos do seu e-mail para enviar o pedido.")}
            {field("co-tel", "Celular / WhatsApp", "tel", "tel", extra='inputmode="numeric" placeholder="(00) 00000-0000" data-mask="tel" minlength="14"', msg="Digite seu celular com DDD.")}
            {field("co-cpf", "CPF", "text", extra='inputmode="numeric" placeholder="000.000.000-00" data-mask="cpf" minlength="14"', hint="Necessário para a nota fiscal. Use um CPF fictício: é uma simulação.", msg="Digite o CPF (11 números).")}
          </div>
          <div class="co-nav"><button class="btn btn--primary" type="button" data-co-next><span>Continuar para entrega</span>{icon("arrow", "icon--arrow")}</button></div>
        </fieldset>

        <fieldset class="co-panel" data-co-panel="1" hidden>
          <legend class="h3">2. Entrega</legend>
          <div class="co-grid">
            {field("co-cep", "CEP", "text", "postal-code", extra='inputmode="numeric" placeholder="00000-000" data-mask="cep" minlength="9"', msg="Digite o CEP (8 números).")}
            <div class="field" data-msg-empty="Selecione o estado."><label for="co-uf">Estado <span class="req" aria-hidden="true">*</span></label>
              <select id="co-uf" name="co-uf" required aria-describedby="co-uf-err" autocomplete="address-level1">{uf_opts}</select>
              <p class="field__error" id="co-uf-err">{icon("close")}<span></span></p></div>
            {field("co-cidade", "Cidade", ac="address-level2", msg="Digite a cidade.")}
            {field("co-bairro", "Bairro", ac="address-level3", msg="Digite o bairro.")}
            {field("co-rua", "Rua / Avenida", ac="address-line1", msg="Digite o endereço.", width="co-full")}
            {field("co-num", "Número", ac="", extra='inputmode="numeric"', msg="Digite o número (ou s/n).")}
            {field("co-comp", "Complemento", req=False, ac="address-line2", extra='placeholder="Apto, bloco, referência"')}
          </div>
          <fieldset class="field co-options" data-msg-empty="Escolha uma forma de entrega.">
            <legend>Forma de entrega <span class="req" aria-hidden="true">*</span></legend>
            <label class="co-option"><input type="radio" name="co-frete" value="padrao" required aria-describedby="co-frete-err" checked><span class="co-option__body"><b>Entrega padrão</b><small>5 a 8 dias úteis</small></span><span class="co-option__price" data-frete-price="padrao"></span></label>
            <label class="co-option"><input type="radio" name="co-frete" value="expressa"><span class="co-option__body"><b>Entrega expressa</b><small>2 a 3 dias úteis</small></span><span class="co-option__price" data-frete-price="expressa"></span></label>
            <label class="co-option"><input type="radio" name="co-frete" value="retirada"><span class="co-option__body"><b>Retirar na Loja Conceito</b><small>Gramado (RS), em 1 dia útil</small></span><span class="co-option__price" data-frete-price="retirada"></span></label>
            <p class="field__error" id="co-frete-err">{icon("close")}<span></span></p>
          </fieldset>
          <div class="co-nav"><button class="btn btn--ghost" type="button" data-co-prev><span>Voltar</span></button>
            <button class="btn btn--primary" type="button" data-co-next><span>Continuar para pagamento</span>{icon("arrow", "icon--arrow")}</button></div>
        </fieldset>

        <fieldset class="co-panel" data-co-panel="2" hidden>
          <legend class="h3">3. Pagamento</legend>
          <p class="co-demo">{icon("eye")}<span><strong>Simulação acadêmica:</strong> nenhum pagamento é processado e nenhum dado sai do seu navegador. Não use dados reais de cartão.</span></p>
          <fieldset class="field co-options co-pay" data-msg-empty="Escolha a forma de pagamento.">
            <legend>Forma de pagamento <span class="req" aria-hidden="true">*</span></legend>
            <label class="co-option"><input type="radio" name="co-pag" value="pix" required aria-describedby="co-pag-err" checked><span class="co-option__body"><b>Pix</b><small>Aprovação na hora · 5% de desconto</small></span></label>
            <label class="co-option"><input type="radio" name="co-pag" value="cartao"><span class="co-option__body"><b>Cartão de crédito</b><small>Em até 3x sem juros</small></span></label>
            <label class="co-option"><input type="radio" name="co-pag" value="boleto"><span class="co-option__body"><b>Boleto bancário</b><small>Vence em 2 dias úteis</small></span></label>
            <p class="field__error" id="co-pag-err">{icon("close")}<span></span></p>
          </fieldset>
          <div class="co-pay-detail" data-pay-detail="pix"><p>{icon("bolt" if False else "sparkle")}Ao confirmar, você recebe o QR Code do Pix (simulado) com <strong>5% de desconto</strong>.</p></div>
          <div class="co-pay-detail co-grid" data-pay-detail="cartao" hidden>
            {field("co-card", "Número do cartão", "text", extra='inputmode="numeric" placeholder="0000 0000 0000 0000" data-mask="card" minlength="19" data-pay-req', msg="Digite os 16 números do cartão (fictício).", width="co-full")}
            {field("co-card-nome", "Nome impresso no cartão", extra='data-pay-req', msg="Digite o nome como está no cartão.", width="co-full")}
            {field("co-card-val", "Validade", "text", extra='inputmode="numeric" placeholder="MM/AA" data-mask="val" minlength="5" data-pay-req', msg="Digite a validade (MM/AA).")}
            {field("co-card-cvv", "CVV", "text", extra='inputmode="numeric" placeholder="000" data-mask="cvv" minlength="3" data-pay-req', msg="Digite os 3 números do verso.")}
            <div class="field co-full"><label for="co-parcelas">Parcelas</label><select id="co-parcelas" name="co-parcelas" data-parcelas></select></div>
          </div>
          <div class="co-pay-detail" data-pay-detail="boleto" hidden><p>{icon("news")}O boleto (simulado) é gerado ao confirmar e o pedido é enviado após a compensação.</p></div>
          <p class="co-error" data-co-error role="alert"></p>
          <div class="co-nav"><button class="btn btn--ghost" type="button" data-co-prev><span>Voltar</span></button>
            <button class="btn btn--primary btn--lg" type="submit" data-co-submit>{icon("check")}<span>Confirmar pedido</span><span class="btn__bubbles" aria-hidden="true"><i></i><i></i><i></i></span></button></div>
        </fieldset>
      </form>

      <div class="co-success" data-co-success hidden tabindex="-1">
        <svg class="check" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="46"/><path d="M30 52 l14 14 l27 -30"/></svg>
        <h2>Pedido confirmado!</h2>
        <p class="co-success__num">Pedido <strong data-co-order></strong></p>
        <p data-co-success-msg></p>
        <div class="co-pix" data-co-pix hidden><div class="co-pix__qr" aria-hidden="true"></div><p>QR Code Pix <strong>simulado</strong>. Em uma loja real, você escanearia este código no app do banco.</p></div>
        <p class="small muted">Simulação acadêmica: nenhum pagamento foi processado e nenhum dado foi enviado.</p>
        <div class="btn-row" style="justify-content:center">{btn("Voltar para a home", "index.html", "dark")}{btn("Ver mais sabores", "sabores.html", "yellow", ic="arrow")}</div>
      </div>
    </div>

    <aside class="co-summary" aria-labelledby="co-sum-title" data-co-summary>
      <h2 class="h3" id="co-sum-title">Resumo do pedido</h2>
      <ul class="co-summary__items" role="list" data-co-items></ul>
      <dl class="co-summary__totals">
        <div><dt>Subtotal</dt><dd data-co-subtotal>R$ 0,00</dd></div>
        <div><dt>Entrega</dt><dd data-co-frete>—</dd></div>
        <div class="co-discount" data-co-discount-row hidden><dt>Desconto Pix (5%)</dt><dd data-co-discount></dd></div>
        <div class="co-summary__total"><dt>Total</dt><dd data-co-total>R$ 0,00</dd></div>
      </dl>
      <p class="small muted">Frete grátis acima de R$ 150 para o Sul e Sudeste na entrega padrão.</p>
      <button class="link-arrow co-summary__edit" type="button" data-open-cart>Editar carrinho {icon("arrow")}</button>
    </aside>
  </div>
</section>
'''
page('checkout.html', 'Finalizar compra | FRIZZA Refrigerantes',
     'Finalize sua compra na loja FRIZZA: dados, entrega e pagamento (simulação acadêmica).',
     checkout, '', theme_color='#FFD23F', body_attrs='data-theme="solar" data-cta="orange" data-page="checkout"')

# =================================================================== ESCRITA
for name, content in PAGES:
    open(os.path.join(ROOT, name), 'w').write(content)

# README de imagens (gerado a partir do que cada página usa)
present = [(f, it) for f, it in IMAGES.items() if img_exists(f)]
missing = [(f, it) for f, it in IMAGES.items() if not img_exists(f)]
def uses_md(it):
    u = it['uses']
    return '<br>'.join(u[:5]) + (f'<br>(+{len(u) - 5})' if len(u) > 5 else '')
lines = ['# Imagens do site FRIZZA', '',
         'Imagens finais geradas pelos designers, já **otimizadas e aplicadas** nas páginas. Os arquivos enviados originalmente estão em `originais/` (não são usados no site).', '',
         '## Organização', '',
         '| Pasta | Conteúdo |', '|---|---|',
         '| `latas/` | Latas de cada sabor, recortadas com **fundo transparente** (versão com gotas e `-classica`). Flutuam soltas nas animações. |',
         '| `sabores/` | "Lata + frutas" recortada de cada sabor (`-recorte`, transparente), fotos de ocasião e fotos premium da Uva Rosé. |',
         '| `historia/` | Gramado, produtores, ribeirinhos, horta, vinhedo, mudas, reciclagem e a ilustração 2028 (SVG). |',
         '| `comunidade/` | Fotos #FRIZZALOVERS (galeria, feed da Home, polaroids) e foto do Contato. |',
         '| `onde-encontrar/` | Estande em festival e prateleira de empório. |',
         '| `elementos/` | Frutas, folhas e gelo em SVG (criados para o site, decorativos). |',
         '| `marca/` | Logos (colorido e branco), favicon (32/180/512) e imagem de compartilhamento (Open Graph). |',
         '| `originais/` | Arquivos originais enviados, sem alteração. |', '',
         '**Otimização:** fotos em WebP qualidade 80, largura máxima de 2000 px nos heros e 1200 px no resto. Scripts em `ferramentas/otimizar_imagens.py` e `ferramentas/gerar_elementos_svg.py`.', '',
         '**Para trocar uma imagem:** salve o novo arquivo com o **mesmo nome e pasta** e rode `python3 ferramentas/gerar_paginas.py .` (o gerador lê as dimensões reais e atualiza `width`/`height`).', '',
         f'## Em uso no site ({len(present)} arquivos)', '',
         '| Arquivo | Onde aparece | Texto alternativo |', '|---|---|---|']
for f, it in present:
    lines.append(f'| `{f}` | {uses_md(it)} | {it["alt"]} |')
lines += ['', f'## Faltando ({len(missing)})', '',
          'Esses lugares continuam com placeholder (borda tracejada + nome do arquivo). Prompts prontos em [`FALTANDO.md`](FALTANDO.md).', '']
for f, it in missing:
    lines.append(f'- `{f}` → {uses_md(it)} ({it["w"]}×{it["h"]})')
open(os.path.join(ROOT, 'assets/img/README.md'), 'w').write('\n'.join(lines) + '\n')

PROMPTS = {
    'historia/timeline-2018.webp': 'Candid documentary photo of a small handmade street-market stall in Gramado, southern Brazil (Serra Gaúcha), with rustic wooden table, colorful craft soda cans in orange, purple, teal, peach and pink, a hand-lettered chalk sign reading "FRIZZA", two young founders (a man and a woman, around 30, diverse) smiling and serving customers, European-style timber houses and hydrangeas in the background, natural soft daylight, vivid saturated colors, fresh tropical mood, genuine people, shot on 35mm, 4:3.',
}
OPTIONAL = []
fl = ['# Imagens que faltam', '',
      'Lista gerada automaticamente pelo `ferramentas/gerar_paginas.py`. Gere a imagem, salve com o **nome e a pasta indicados** dentro de `assets/img/` e rode o gerador de novo (ou peça para mim).', '',
      'Estilo do briefing: luz natural, cores vivas e saturadas, frescor, tropical, pessoas diversas e genuínas.', '']
if missing:
    fl += ['## Obrigatórias (o site mostra placeholder)', '']
    for f, it in missing:
        fl += [f'### `{f}`', '', f'- **Onde entra:** {", ".join(it["uses"])}', f'- **Proporção:** {ratio(it["w"], it["h"]).replace(" ", "")} ({it["w"]}×{it["h"]} px)',
               f'- **Alt:** {it["alt"]}', '', '**Prompt (EN):**', '', '```', PROMPTS.get(f, it['desc']), '```', '']
fl += [] if missing else ['Nenhuma imagem faltando no momento. 🎉', '']
if OPTIONAL: fl += ['## Recomendadas (melhorariam o resultado)', '']
for f, where, prop, prompt in OPTIONAL:
    fl += [f'### `{f}`', '', f'- **Onde entra:** {where}', f'- **Proporção:** {prop}', '', '**Prompt (EN):**', '', '```', prompt, '```', '']
open(os.path.join(ROOT, 'assets/img/FALTANDO.md'), 'w').write('\n'.join(fl))
print(f'{len(PAGES)} páginas, {len(present)} imagens em uso, {len(missing)} faltando')
