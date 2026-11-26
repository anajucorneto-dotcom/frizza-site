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
/sabores.html                Nossos Sabores (grid + filtro + guia rápido)
/sabor-laranja-bahia.html    ┐
/sabor-acai-guarana.html     │ Páginas individuais dos sabores
/sabor-limao-hortela.html    │ (mesmo template; a Uva Rosé tem
/sabor-pessego-gengibre.html │  o visual premium)
/sabor-uva-rose.html         ┘
/historia.html               Nossa História (linha do tempo, valores, mapa, sustentabilidade)
/onde-encontrar.html         Onde Encontrar (busca de lojas, mapa, loja online, festivais)
/frizzalovers.html           #FRIZZALOVERS (galeria masonry + lightbox)
/contato.html                Contato (formulário, WhatsApp, FAQ, imprensa)
/assets/css/style.css        Todos os estilos (variáveis da marca no topo)
/assets/js/main.js           Todas as interações e animações
/assets/icons/               Ícones SVG line art (traço médio, cantos arredondados)
/assets/img/                 Imagens do site + README com a lista completa
/ferramentas/gerar_paginas.py  (opcional) gerador do HTML, ver seção 7
```

---

## 3. Como trocar as imagens (é só salvar com o nome certo!)

Todas as imagens ainda são **placeholders**: caixas com gradiente, borda tracejada e uma etiqueta com o **nome do arquivo esperado e o tamanho recomendado** (ex.: `historia-fundadores.jpg — 1080×1350 px`).

1. Abra **[`assets/img/README.md`](assets/img/README.md)**. Lá está a tabela com as **52 imagens** do site: nome do arquivo, tamanho, onde aparece, texto alternativo e uma **descrição pronta para gerar com IA**.
2. Gere/edite a imagem e salve **dentro de `/assets/img/`** com **exatamente** o nome da tabela.
3. Pronto. O `main.js` percebe que o arquivo existe, carrega a imagem e esconde o placeholder sozinho. O `alt` (acessibilidade) já está escrito.

Dicas:
- **Latas, frutas e logos** devem ser **PNG com fundo transparente** (eles flutuam e giram nas animações).
- Enquanto o logotipo não chega, o site mostra a palavra **FRIZZA** em Fredoka com uma **bolha animada no lugar do pingo do "i"**. Existem duas versões: `logo-frizza.png` (colorida) e `logo-frizza-branco.png` (footer e topo das páginas escuras).
- O favicon provisório é `assets/icons/favicon.svg`. O `favicon.png` (512×512) é usado como ícone de app.

---

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
