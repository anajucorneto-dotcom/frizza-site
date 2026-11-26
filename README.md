# FRIZZA Refrigerantes — site institucional

> **Marca fictícia criada para fins acadêmicos** — Design de Interface, Publicidade e Propaganda, Unoeste.

Site estático (HTML + CSS + JavaScript puro, sem etapa de build) da FRIZZA, uma marca brasileira de refrigerantes artesanais nascida em Gramado (RS). Vibrante, cheio de transições e pensado para três personas: **Marina** (visual e ingredientes claros), **Lucas** (interatividade e compra fácil) e **Dona Cléo** (navegação simples, tabela nutricional legível e WhatsApp em destaque).

---

## 1. Como ver o site no seu computador

**Jeito mais fácil:** dê dois cliques no `index.html`. Ele abre no navegador e funciona (é preciso internet para carregar as fontes e as bibliotecas de animação).

**Jeito recomendado** (simula o servidor do GitHub Pages): abra o terminal na pasta do projeto e rode:

```bash
python3 -m http.server 8000
```

Depois acesse <http://localhost:8000>. No VS Code, a extensão *Live Server* faz a mesma coisa.

---

## 2. Estrutura de arquivos

```
/index.html                  Home (vitrine)
/sabores.html                Nossos Sabores (loja: cards com "Adicionar", filtro e quiz)
/sabor-laranja-bahia.html    ┐
/sabor-acai-guarana.html     │ Páginas individuais dos sabores
/sabor-limao-hortela.html    │ (mesmo template; a Uva Rosé tem
/sabor-pessego-gengibre.html │  o visual premium)
/sabor-uva-rose.html         ┘
/historia.html               Nossa História (linha do tempo, valores, mapa, sustentabilidade)
/onde-encontrar.html         Onde Encontrar (busca de lojas, mapa, loja online, festivais)
/frizzalovers.html           #FRIZZALOVERS (galeria masonry + lightbox)
/contato.html                Contato (formulário, WhatsApp, FAQ, imprensa)
/checkout.html               Finalizar compra (dados → entrega → pagamento → confirmação, simulação)
/assets/css/style.css        Todos os estilos (variáveis da marca no topo)
/assets/js/main.js           Todas as interações e animações
/assets/icons/               Ícones SVG line art (traço médio, cantos arredondados)
/assets/img/                 Imagens do site + README com a lista completa
/ferramentas/gerar_paginas.py  (opcional) gerador do HTML, ver seção 7
```

---

## 3. Imagens

As imagens finais dos designers já estão aplicadas, otimizadas em WebP e organizadas em pastas dentro de `assets/img/` (`latas/`, `sabores/`, `historia/`, `comunidade/`, `onde-encontrar/`, `elementos/`, `marca/`). Os arquivos originais ficam guardados em `assets/img/originais/` e não são usados no site.

- **[`assets/img/README.md`](assets/img/README.md)**: lista de cada imagem em uso, onde aparece e o texto alternativo.
- **[`assets/img/FALTANDO.md`](assets/img/FALTANDO.md)**: o que ainda falta, com prompt pronto (em inglês) para gerar na IA.
- **Para trocar ou adicionar uma imagem:** salve o arquivo com o **mesmo nome e pasta** e rode `python3 ferramentas/gerar_paginas.py .`. O gerador lê as dimensões reais e escreve `width`/`height`, `alt`, `loading="lazy"` e `fetchpriority` nos heros.
- Para reprocessar os originais (WebP, recortes das latas, favicon): `python3 ferramentas/otimizar_imagens.py`. Frutas, folhas e gelo são SVG próprios (`ferramentas/gerar_elementos_svg.py`).
- As latas enviadas **não têm fundo transparente**. Por isso aparecem como "card" de produto, com cantos arredondados e sombra. Com PNGs transparentes elas passam a flutuar soltas: basta salvar `latas/lata-<sabor>.png` e ajustar a extensão no gerador.

## 4. Identidade visual aplicada

| Token CSS | Cor | Uso |
|---|---|---|
| `--laranja-vibrante` | `#FF6B2B` | Primária, CTAs principais |
| `--amarelo-solar` | `#FFD23F` | Secundária, destaques, CTA "Onde Comprar" |
| `--verde-menta` | `#2EC4B6` | Frescor, CTAs secundários |
| `--roxo-acai` | `#7B2D8E` | Sofisticação |
| `--branco-gelo` | `#FAFAFA` | Fundos e respiros |
| `--preto-suave` | `#1A1A2E` | Textos, contrastes, footer |

Cada sabor tem sua cor (`--laranja-bahia`, `--acai-guarana`, `--limao-hortela`, `--pessego-gengibre`, `--uva-rose`) + uma **versão pastel** (fundo dos cards) + uma versão **"ink"** (escurecida) usada só quando o texto colorido fica sobre fundo claro, para passar no contraste.

**Tipografia:** Fredoka e Baloo 2 (títulos), Poppins (texto, mín. 16px, entrelinha 1,65) e Cormorant Garamond apenas no universo premium da Uva Rosé.

### Decisões de acessibilidade (para a banca)
- **Texto preto suave nos botões laranja.** Branco sobre `#FF6B2B` tem contraste de 2,84:1 e **não passa no WCAG AA**; preto suave dá 6,0:1. Todas as combinações de texto foram conferidas (≥ 4,5:1).
- HTML semântico (`header`, `nav`, `main`, `section`, `footer`), um `h1` por página, link "Pular para o conteúdo", foco visível em tudo, `aria-current` na página atual, `aria-expanded` no menu e no FAQ, `aria-live` nos filtros/busca/formulários.
- Contadores animados têm o valor final em texto para leitores de tela; títulos animados letra a letra mantêm o texto original em `aria-label`.
- **`prefers-reduced-motion`:** sem preloader, sem cortina, sem scroll suave e sem animações pesadas; tudo aparece direto.
- **Se o CDN falhar**, nada fica escondido: as animações simplesmente não rodam.
- Formulário com labels visíveis, mensagens de erro em português claro e foco automático no primeiro campo com problema.

---

## 5. Animações e interações

Preloader com bolhas (1ª visita da sessão) · cortina em onda colorida entre páginas (cor da página de destino) · scroll suave (Lenis) · títulos letra a letra/palavra a palavra (SplitType) · reveals com máscara e cascata (GSAP ScrollTrigger) · parallax que segue o mouse no hero · vitrine horizontal fixada com troca de cor de fundo e lata girando · manifesto que "acende" palavra por palavra · marquee infinito · bolhas de gás em canvas (pausam fora da tela) · brilho de espumante na Uva Rosé · contadores · lata girando no scroll nas páginas de sabor · barras e anel de ingredientes · linha do tempo que se desenha · mapa do Brasil interativo · cursor-bolha que mostra "ver" sobre cards (só desktop) · botões magnéticos com bolhas · tilt 3D nos cards · divisórias em onda · menu mobile em tela cheia com links em cascata · filtro de sabores, busca de lojas (ignora acentos), lightbox com teclado, FAQ em acordeão e formulários com microinterações.

Animações usam apenas `transform` e `opacity` sempre que possível, para manter 60 fps.

**Bibliotecas (CDN, carregadas com `defer`):** GSAP 3.12.5 + ScrollTrigger, Lenis 1.1.13, SplitType 0.3.4. Fontes do Google Fonts.

### Loja online (simulação)
- **Carrinho** no canto superior direito de todas as páginas, com contador. Abre uma gaveta lateral com os produtos, botões de quantidade (+/−), remover, subtotal e aviso de frete grátis (acima de R$ 150 no Sul e Sudeste).
- **Adicionar ao carrinho** aparece junto dos produtos: cards da página Nossos Sabores, vitrine e banner da Uva Rosé na Home, topo e rodapé de cada página de sabor e resultado do quiz.
- O carrinho fica salvo **no navegador** (localStorage) e acompanha a pessoa pelas páginas.
- **Quiz "Qual FRIZZA combina com você?"** (página Nossos Sabores): 4 perguntas, uma por vez, com barra de progresso e botão voltar. No final, mostra os sabores com a % de combinação e um botão para adicionar todos ao carrinho.
- **`checkout.html`**: 3 etapas (dados, entrega e pagamento) com validação amigável e máscaras (celular, CPF, CEP, cartão). Calcula frete (padrão, expressa ou retirada em Gramado), dá 5% de desconto no Pix, parcela em até 3x no cartão e termina na tela "Pedido confirmado".
- Preços (fictícios) por lata de 350 ml: Laranja Bahia e Limão com Hortelã R$ 9,90 · Açaí com Guaraná e Pêssego com Gengibre R$ 10,90 · Uva Rosé R$ 13,90. Ficam em `PRICES`, no topo de `ferramentas/gerar_paginas.py`.
- ⚠️ **É uma simulação acadêmica:** nenhum pagamento é processado e nenhum dado sai do navegador. A própria página avisa para não usar dados reais de cartão.

### Links ilustrativos
Como a marca é fictícia, links de redes sociais, WhatsApp, e-mail, telefone e loja online têm o atributo `data-demo`: ao clicar, aparece um aviso ("link ilustrativo…") em vez de abrir um perfil que não existe. Para transformar em link real, basta apagar o `data-demo` do elemento.

### Pontos de venda e Google Maps
Em **Onde Encontrar**, clicar em um ponto de venda mostra a localização no mapa ao lado (no celular, a página rola até o mapa) e atualiza o botão **"Abrir no Google Maps"**. Cada cartão também tem o próprio link para o Google Maps (abre em nova aba).
Como os endereços são fictícios, o mapa aponta para o **bairro real** de cada cidade (ex.: "Savassi, Belo Horizonte - MG"). Para usar endereços reais, troque o atributo `data-maps-q` e o link `store__maps` de cada cartão em `onde-encontrar.html` (ou a função `maps_query` em `ferramentas/gerar_paginas.py`).

---

## 6. Publicar no GitHub Pages

1. Crie um repositório no GitHub (ex.: `frizza-site`) e envie os arquivos para a branch **`main`**:
   ```bash
   git remote add origin https://github.com/SEU-USUARIO/frizza-site.git
   git push -u origin main
   ```
2. No GitHub, abra o repositório → **Settings** → **Pages**.
3. Em **Build and deployment → Source**, escolha **Deploy from a branch**.
4. Em **Branch**, selecione **`main`** e a pasta **`/ (root)`**. Clique em **Save**.
5. Aguarde 1–2 minutos. O link aparece no topo da mesma página: `https://SEU-USUARIO.github.io/frizza-site/`.

O arquivo `.nojekyll` na raiz garante que o GitHub publique os arquivos exatamente como estão.

---

## 7. (Opcional) Gerador das páginas

Header, footer e o template dos sabores são iguais em todas as páginas. Eles foram gerados por `ferramentas/gerar_paginas.py`, que também monta o `assets/img/README.md` com a lista de imagens. **O site não depende dele**: pode editar os `.html` direto.

Se preferir mudar algo em um lugar só (por exemplo, um link do menu ou um texto de sabor), edite o script e rode na raiz do projeto:

```bash
python3 ferramentas/gerar_paginas.py .
```

⚠️ Rodar o gerador **sobrescreve** os arquivos `.html`. Escolha um caminho: ou edita o script, ou edita os HTML à mão.
