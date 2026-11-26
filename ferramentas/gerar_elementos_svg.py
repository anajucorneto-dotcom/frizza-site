"""Elementos soltos em SVG (flat + contorno arredondado, paleta FRIZZA)."""
import os
D = '/home/user/frizza-site/assets/img/elementos'
os.makedirs(D, exist_ok=True)
INK = '#1A1A2E'
S = f'stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"'

def svg(name, body, vb='0 0 120 120'):
    open(os.path.join(D, name + '.svg'), 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" fill="none">{body}</svg>\n')

shine = lambda x, y, r=8: f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.6}" fill="#fff" opacity=".7" transform="rotate(-30 {x} {y})"/>'

# fatia de laranja
seg = ''.join(f'<path d="M60 60 L{60+40*__import__("math").cos(a*0.7854):.1f} {60+40*__import__("math").sin(a*0.7854):.1f}" stroke="#FFB36B" stroke-width="3"/>' for a in range(8))
svg('fruta-laranja-fatia', f'<circle cx="60" cy="60" r="50" fill="#FF8C42" {S}/><circle cx="60" cy="60" r="42" fill="#FFD9A8"/><circle cx="60" cy="60" r="38" fill="#FFA24D"/>{seg}<circle cx="60" cy="60" r="5" fill="#FFD9A8"/>{shine(42,40,7)}')
svg('fruta-tangerina', f'<circle cx="60" cy="66" r="42" fill="#FFA62B" {S}/><path d="M60 26c0-8 4-12 10-14" {S}/><path d="M64 22c10-12 26-10 30-4-8 8-22 10-30 4z" fill="#3DBB6B" {S}/>{shine(44,50,9)}<circle cx="78" cy="78" r="2" fill="{INK}" opacity=".25"/><circle cx="70" cy="90" r="2" fill="{INK}" opacity=".25"/>')
berries = [(40, 48), (62, 40), (82, 52), (50, 70), (72, 68), (60, 90), (38, 88), (84, 84)]
svg('fruta-acai', '<path d="M60 14 C58 30 50 40 40 48 M60 14 C64 32 74 40 82 52" stroke="#5B3A1E" stroke-width="4" stroke-linecap="round"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="12" fill="#3B1748" {S}/>{shine(x-4,y-4,3)}' for x, y in berries))
svg('fruta-guarana', f'<path d="M60 14v14" {S}/><path d="M60 30c26 0 40 18 40 40s-18 38-40 38-40-16-40-38 14-40 40-40z" fill="#D63A2F" {S}/><path d="M60 46c14 0 24 10 24 24S74 94 60 94 36 84 36 70s10-24 24-24z" fill="#fff" {S}/><circle cx="60" cy="70" r="12" fill="{INK}"/>{shine(56,66,3)}')
svg('fruta-limao-siciliano', f'<path d="M14 64c0-26 20-46 46-46s46 20 46 46c0 6-6 10-12 10H26c-6 0-12-4-12-10z" fill="#F4E04D" {S}/><path d="M24 64c0-20 16-36 36-36s36 16 36 36" fill="#FFF4A8"/>' +
    ''.join(f'<path d="M60 64 L{60+34*__import__("math").cos(3.1416+a*0.5236):.1f} {64+34*__import__("math").sin(3.1416+a*0.5236):.1f}" stroke="#F4E04D" stroke-width="3"/>' for a in range(7)) +
    f'<circle cx="60" cy="64" r="4" fill="#F4E04D"/><path d="M14 64h92" {S}/>')
leaf = lambda d, fill='#3DBB6B': f'<path d="{d}" fill="{fill}" {S}/>'
svg('folha-hortela', leaf('M60 108C30 96 18 66 30 40c18 4 34 22 30 68z', '#2FB463') + leaf('M60 108c30-12 42-42 30-68-18 4-34 22-30 68z', '#46C97A') + leaf('M60 60c-14-10-18-30-6-48 16 8 18 30 6 48z', '#3DBB6B') + f'<path d="M60 108V20" {S}/>')
svg('fruta-pessego', f'<path d="M60 30c-30-4-46 22-42 46 4 22 22 34 42 34s38-12 42-34c4-24-12-50-42-46z" fill="#FFAB76" {S}/><path d="M60 32c-8 16-8 46 0 76" stroke="#F07E54" stroke-width="4" stroke-linecap="round"/><path d="M60 32c-2-10 2-18 8-22" {S}/><path d="M66 22c12-14 32-8 34 0-10 10-26 10-34 0z" fill="#3DBB6B" {S}/><circle cx="40" cy="62" r="14" fill="#FF8C6B" opacity=".5"/>{shine(40,56,7)}')
svg('gengibre', f'<path d="M20 70c-6-14 6-26 18-22 4-12 20-14 26-4 10-8 26-4 28 8 12 0 18 14 10 24-6 10-20 10-26 4-8 8-24 8-30-2-10 6-22 2-26-8z" fill="#E3B26A" {S}/><path d="M40 60c4 4 4 10 0 14M66 56c4 6 2 12-2 16M84 70c4 2 4 8 0 10" stroke="#B9843E" stroke-width="3" stroke-linecap="round"/>')
grapes = [(46, 40), (66, 40), (86, 42), (56, 58), (76, 58), (46, 76), (66, 76), (56, 94)]
svg('fruta-uva-rose', f'<path d="M66 10c0 10-2 18-6 26" {S}/>' + leaf('M68 18c12-10 30-6 34 4-12 8-26 8-34-4z', '#5DBF6E') + ''.join(f'<circle cx="{x}" cy="{y}" r="13" fill="#E8A0BF" {S}/>{shine(x-4,y-5,3.5)}' for x, y in grapes))
svg('petala-rosa', f'<path d="M60 108C26 92 18 52 34 24c12 10 20 14 26 14s14-4 26-14c16 28 8 68-26 84z" fill="#F3B8CF" {S}/><path d="M60 40v56" stroke="#E68AB0" stroke-width="3" stroke-linecap="round"/>{shine(44,52,6)}')
svg('folha-videira', leaf('M60 110C56 92 40 90 24 96c6-16 0-28-12-36 16-6 22-18 18-32 14 4 24 0 30-14 6 14 16 18 30 14-4 14 2 26 18 32-12 8-18 20-12 36-16-6-32-4-36 14z', '#5DBF6E') + f'<path d="M60 108V30M60 70 32 54M60 70l28-16M60 90 40 82M60 90l20-8" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
svg('folha-tropical', leaf('M60 112C20 100 8 60 26 22c30 6 52 34 34 90z', '#2EA35C') + leaf('M60 112c40-12 52-52 34-90-30 6-52 34-34 90z', '#3DBB6B') + f'<path d="M60 112C58 80 52 52 40 30M60 112c2-32 8-60 20-82" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
svg('gelo', f'<path d="M24 40 62 24l36 18-4 44-38 14-34-18z" fill="#DFF6FF" fill-opacity=".9" {S}/><path d="M24 40l34 16 40-14M58 56l-2 44" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity=".6"/><path d="M34 48l12 6M70 34l14 6" stroke="#fff" stroke-width="5" stroke-linecap="round"/>')

# timeline 2028: Brasil estilizado com bolhas e corações
import re
gen = open('/home/user/frizza-site/historia.html').read()
m = re.search(r'<path class="land" d="([^"]+)"', gen)
br = m.group(1)
cans = ''.join(f'<g transform="translate({x} {y}) rotate({r})"><rect x="-14" y="-26" width="28" height="52" rx="8" fill="{c}" stroke="{INK}" stroke-width="3.5"/><rect x="-14" y="-26" width="28" height="8" rx="4" fill="#E8EAF0" stroke="{INK}" stroke-width="3"/><circle cx="-4" cy="4" r="4" fill="#fff" opacity=".8"/></g>'
               for x, y, r, c in [(300, 150, -12, '#FF8C42'), (180, 110, 8, '#5B2C6F'), (330, 260, 10, '#00BFA6'), (240, 330, -8, '#FFAB76'), (130, 230, -16, '#E8A0BF')])
bubbles = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" fill-opacity=".35" stroke="#fff" stroke-width="3"/>' for x, y, r in [(60, 60, 14), (380, 70, 10), (390, 330, 16), (40, 330, 9), (210, 40, 7), (110, 380, 12)])
heart = '<path d="M210 230c-18-14-34-26-34-44 0-12 10-22 22-22 6 0 10 3 12 7 2-4 6-7 12-7 12 0 22 10 22 22 0 18-16 30-34 44z" fill="#FF6B2B" stroke="#1A1A2E" stroke-width="4" stroke-linejoin="round"/>'
open('/home/user/frizza-site/assets/img/historia/timeline-2028.svg', 'w').write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 315" role="img" aria-label="Ilustração: latas FRIZZA espalhadas pelo mapa do Brasil, com um coração no centro">'
    f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFD23F"/><stop offset="1" stop-color="#FF8C42"/></linearGradient></defs>'
    f'<rect width="420" height="315" rx="24" fill="url(#g)"/>{bubbles}'
    f'<g transform="translate(70 8) scale(.7)"><path d="{br}" fill="#2EC4B6" opacity=".35" transform="translate(10 12)"/><path d="{br}" fill="#FAFAFA" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>{heart}{cans}</g>'
    f'<text x="392" y="292" text-anchor="end" font-family="Fredoka, sans-serif" font-weight="700" font-size="54" fill="{INK}">2028</text></svg>\n')
print(sorted(os.listdir(D)))
