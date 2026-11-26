# Imagens do site FRIZZA

Imagens finais geradas pelos designers, já **otimizadas e aplicadas** nas páginas. Os arquivos enviados originalmente estão em `originais/` (não são usados no site).

## Organização

| Pasta | Conteúdo |
|---|---|
| `latas/` | Latas de cada sabor (versão com gotas e `-classica`). WebP; **não têm fundo transparente**, por isso aparecem como "card" de produto. |
| `sabores/` | Foto "lata + frutas" de cada sabor (`-destaque`), fotos de ocasião e foto premium da Uva Rosé. |
| `historia/` | Gramado, produtores, ribeirinhos, horta, vinhedo, mudas, reciclagem e a ilustração 2028 (SVG). |
| `comunidade/` | Fotos #FRIZZALOVERS (galeria, feed da Home, polaroids) e foto do Contato. |
| `onde-encontrar/` | Estande em festival e prateleira de empório. |
| `elementos/` | Frutas, folhas e gelo em SVG (criados para o site, decorativos). |
| `marca/` | Logos (colorido e branco), favicon (32/180/512) e imagem de compartilhamento (Open Graph). |
| `originais/` | Arquivos originais enviados, sem alteração. |

**Otimização:** fotos em WebP qualidade 80, largura máxima de 2000 px nos heros e 1200 px no resto. Scripts em `ferramentas/otimizar_imagens.py` e `ferramentas/gerar_elementos_svg.py`.

**Para trocar uma imagem:** salve o novo arquivo com o **mesmo nome e pasta** e rode `python3 ferramentas/gerar_paginas.py .` (o gerador lê as dimensões reais e atualiza `width`/`height`).

## Em uso no site (68 arquivos)

| Arquivo | Onde aparece | Texto alternativo |
|---|---|---|
| `latas/lata-acai-guarana.webp` | index.html → Home → hero (5 latas flutuando)<br>sabores.html → Grid de cards<br>sabor-laranja-bahia.html → Experimente também<br>sabor-limao-hortela.html → Experimente também<br>sabor-pessego-gengibre.html → Experimente também<br>(+1) | Lata de FRIZZA Açaí com Guaraná |
| `latas/lata-limao-hortela.webp` | index.html → Home → hero (5 latas flutuando)<br>sabores.html → Grid de cards<br>sabor-laranja-bahia.html → Experimente também<br>sabor-acai-guarana.html → Experimente também<br>sabor-pessego-gengibre.html → Experimente também<br>(+1) | Lata de FRIZZA Limão com Hortelã |
| `latas/lata-laranja-bahia.webp` | index.html → Home → hero (5 latas flutuando)<br>sabores.html → Grid de cards<br>sabor-acai-guarana.html → Experimente também<br>sabor-limao-hortela.html → Experimente também<br>sabor-pessego-gengibre.html → Experimente também<br>(+1) | Lata de FRIZZA Laranja Bahia |
| `latas/lata-pessego-gengibre.webp` | index.html → Home → hero (5 latas flutuando)<br>sabores.html → Grid de cards<br>sabor-laranja-bahia.html → Experimente também<br>sabor-acai-guarana.html → Experimente também<br>sabor-limao-hortela.html → Experimente também<br>(+1) | Lata de FRIZZA Pêssego com Gengibre |
| `latas/lata-uva-rose.webp` | index.html → Home → hero (5 latas flutuando)<br>sabores.html → Grid de cards<br>sabor-laranja-bahia.html → Experimente também<br>sabor-acai-guarana.html → Experimente também<br>sabor-limao-hortela.html → Experimente também<br>(+1) | Lata de FRIZZA Uva Rosé |
| `elementos/fruta-laranja-fatia.svg` | index.html → Home → hero (frutas, gelo e folhas)<br>sabor-laranja-bahia.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `elementos/fruta-uva-rose.svg` | index.html → Home → hero (frutas, gelo e folhas)<br>sabor-uva-rose.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `elementos/folha-hortela.svg` | index.html → Home → hero (frutas, gelo e folhas)<br>sabor-limao-hortela.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `elementos/fruta-acai.svg` | index.html → Home → hero (frutas, gelo e folhas)<br>sabor-acai-guarana.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `elementos/fruta-pessego.svg` | index.html → Home → hero (frutas, gelo e folhas)<br>sabor-pessego-gengibre.html → Página do sabor → hero (frutas soltas)<br>historia.html → Nossa História → origem dos sabores (mapa) | (decorativo) |
| `elementos/fruta-limao-siciliano.svg` | index.html → Home → hero (frutas, gelo e folhas)<br>sabor-limao-hortela.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `elementos/gelo.svg` | index.html → Home → hero (frutas, gelo e folhas) | (decorativo) |
| `elementos/folha-tropical.svg` | index.html → Home → hero (frutas, gelo e folhas)<br>index.html → Manifesto (decoração)<br>sabor-laranja-bahia.html → Página do sabor → hero (frutas soltas)<br>sabor-acai-guarana.html → Página do sabor → hero (frutas soltas)<br>sabor-pessego-gengibre.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `sabores/laranja-bahia-destaque.webp` | index.html → Home → vitrine dos sabores<br>sabores.html → Nossos Sabores → quiz (resultado)<br>sabor-laranja-bahia.html → Página do sabor → hero (gira no scroll) | Lata de FRIZZA Laranja Bahia cercada de frutas e respingos |
| `sabores/acai-guarana-destaque.webp` | index.html → Home → vitrine dos sabores<br>sabores.html → Nossos Sabores → quiz (resultado)<br>sabor-acai-guarana.html → Página do sabor → hero (gira no scroll) | Lata de FRIZZA Açaí com Guaraná cercada de frutas e respingos |
| `sabores/limao-hortela-destaque.webp` | index.html → Home → vitrine dos sabores<br>sabores.html → Nossos Sabores → quiz (resultado)<br>sabor-limao-hortela.html → Página do sabor → hero (gira no scroll) | Lata de FRIZZA Limão com Hortelã cercada de frutas e respingos |
| `sabores/pessego-gengibre-destaque.webp` | index.html → Home → vitrine dos sabores<br>sabores.html → Nossos Sabores → quiz (resultado)<br>sabor-pessego-gengibre.html → Página do sabor → hero (gira no scroll) | Lata de FRIZZA Pêssego com Gengibre cercada de frutas e respingos |
| `sabores/uva-rose-destaque.webp` | index.html → Home → vitrine dos sabores<br>sabores.html → Nossos Sabores → quiz (resultado)<br>sabor-uva-rose.html → Página do sabor → hero (gira no scroll) | Lata de FRIZZA Uva Rosé cercada de frutas e respingos |
| `comunidade/lovers-01.webp` | index.html → Home → #FRIZZALOVERS (feed)<br>frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Mulher de boné verde bebendo uma lata de FRIZZA Laranja Bahia |
| `comunidade/lovers-04.webp` | index.html → Home → #FRIZZALOVERS (feed)<br>frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Mulher de cabelo crespo bebendo FRIZZA Açaí com Guaraná deitada numa toalha de piquenique |
| `comunidade/lovers-03.webp` | index.html → Home → #FRIZZALOVERS (feed)<br>frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Mulher sorrindo de olhos fechados abraçando quatro latas FRIZZA sobre fundo rosa |
| `comunidade/lovers-02.webp` | index.html → Home → #FRIZZALOVERS (feed)<br>frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Rapaz de cabelo cacheado e óculos laranja segurando uma lata de FRIZZA Limão com Hortelã contra o céu azul |
| `comunidade/lovers-09.webp` | index.html → Home → #FRIZZALOVERS (feed)<br>frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Mãos segurando quatro latas FRIZZA junto ao corpo num gramado |
| `comunidade/lovers-11.webp` | index.html → Home → #FRIZZALOVERS (feed)<br>frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Casal na praia brindando com latas FRIZZA sob o céu azul |
| `sabores/uva-rose-premium.webp` | index.html → Home → banner premium Uva Rosé<br>sabor-uva-rose.html → Uva Rosé → faixa premium | Lata de FRIZZA Uva Rosé sobre superfície escura com luz dourada, pétalas e bolhas |
| `historia/horta-hortela-gramado.webp` | index.html → Home → prévia da história<br>historia.html → Nossa História → origem dos sabores (mapa) | Agricultora colhendo hortelã na horta da FRIZZA em Gramado, com araucárias e uma casa de madeira ao fundo |
| `marca/og-frizza.jpg` | index.html → meta Open Graph (todas as páginas) | FRIZZA Refrigerantes |
| `marca/favicon.png` | index.html → favicon (todas as páginas) | Ícone FRIZZA |
| `marca/logo-frizza.png` | index.html → header e footer (todas as páginas) | Logotipo FRIZZA |
| `marca/logo-frizza-branco.png` | index.html → header e footer (todas as páginas) | Logotipo FRIZZA |
| `latas/lata-laranja-bahia-classica.webp` | sabores.html → Nossos Sabores → hero (5 latas) | Lata de FRIZZA Laranja Bahia |
| `latas/lata-acai-guarana-classica.webp` | sabores.html → Nossos Sabores → hero (5 latas) | Lata de FRIZZA Açaí com Guaraná |
| `latas/lata-limao-hortela-classica.webp` | sabores.html → Nossos Sabores → hero (5 latas) | Lata de FRIZZA Limão com Hortelã |
| `latas/lata-pessego-gengibre-classica.webp` | sabores.html → Nossos Sabores → hero (5 latas) | Lata de FRIZZA Pêssego com Gengibre |
| `latas/lata-uva-rose-classica.webp` | sabores.html → Nossos Sabores → hero (5 latas) | Lata de FRIZZA Uva Rosé |
| `elementos/fruta-tangerina.svg` | sabor-laranja-bahia.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `sabores/ocasiao-laranja-bahia.webp` | sabor-laranja-bahia.html → Página do sabor → ocasião ideal | Pessoas aproveitando a FRIZZA Laranja Bahia: para todo mundo, todo dia |
| `elementos/fruta-guarana.svg` | sabor-acai-guarana.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `sabores/ocasiao-acai-guarana.webp` | sabor-acai-guarana.html → Página do sabor → ocasião ideal | Pessoas aproveitando a FRIZZA Açaí com Guaraná: para o rolê e a maratona de estudos |
| `sabores/ocasiao-limao-hortela.webp` | sabor-limao-hortela.html → Página do sabor → ocasião ideal | Pessoas aproveitando a FRIZZA Limão com Hortelã: para harmonizar e inventar drinks |
| `elementos/gengibre.svg` | sabor-pessego-gengibre.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `sabores/ocasiao-pessego-gengibre.webp` | sabor-pessego-gengibre.html → Página do sabor → ocasião ideal | Pessoas aproveitando a FRIZZA Pêssego com Gengibre: para quem gosta de experimentar |
| `elementos/petala-rosa.svg` | sabor-uva-rose.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `elementos/folha-videira.svg` | sabor-uva-rose.html → Página do sabor → hero (frutas soltas) | (decorativo) |
| `historia/vinhedo-bento-goncalves.webp` | sabor-uva-rose.html → Uva Rosé → faixa premium<br>historia.html → Nossa História → origem dos sabores (mapa) | Lata de FRIZZA Uva Rosé sobre um barril de madeira com vinhedos de Bento Gonçalves ao pôr do sol |
| `sabores/ocasiao-uva-rose.webp` | sabor-uva-rose.html → Página do sabor → ocasião ideal<br>historia.html → Nossa História → linha do tempo 2024 | Pessoas aproveitando a FRIZZA Uva Rosé: para as ocasiões especiais (e as nem tanto) |
| `onde-encontrar/festival-estande.webp` | historia.html → Nossa História → linha do tempo 2019<br>onde-encontrar.html → Onde Encontrar → festivais e feiras | Estande de madeira da FRIZZA lotado em um festival de música ao ar livre |
| `historia/timeline-2020.webp` | historia.html → Nossa História → linha do tempo 2020 | Pessoa abrindo uma lata de FRIZZA Laranja Bahia ao lado do notebook |
| `onde-encontrar/emporio-prateleira.webp` | historia.html → Nossa História → linha do tempo 2022<br>onde-encontrar.html → Onde Encontrar → hero | Prateleira de madeira de um empório cheia de latas FRIZZA dos cinco sabores |
| `historia/timeline-2028.svg` | historia.html → Nossa História → linha do tempo 2028 | Ilustração: latas FRIZZA espalhadas pelo mapa do Brasil, com um coração no centro |
| `historia/produtores-laranja-reconcavo.webp` | historia.html → Nossa História → origem dos sabores (mapa) | Agricultor e menina colhendo laranjas no Recôncavo Baiano |
| `historia/acai-colheita.webp` | historia.html → Nossa História → origem dos sabores (mapa) | Mãos segurando um cacho de açaí recém-colhido na floresta |
| `historia/historia-hero.webp` | historia.html → Nossa História → hero<br>onde-encontrar.html → Onde Encontrar → festivais e feiras | Lata de FRIZZA Uva Rosé sobre uma cerca de madeira com hortênsias coloridas e araucárias na névoa da Serra Gaúcha |
| `historia/ribeirinhos-acai.webp` | historia.html → Nossa História → sustentabilidade | Ribeirinho subindo num açaizeiro enquanto uma mulher organiza cestos de açaí numa canoa, com casas de palafita ao fundo |
| `historia/rio-para-aerea.webp` | historia.html → Nossa História → card pequenos produtores | Vista aérea de um rio amazônico com casas ribeirinhas entre a floresta ao amanhecer |
| `historia/mudas-arvores.webp` | historia.html → Nossa História → card árvores | Voluntários plantando mudas de árvores nativas em uma área de reflorestamento |
| `historia/reciclagem-festival.webp` | historia.html → Nossa História → card logística reversa<br>onde-encontrar.html → Onde Encontrar → festivais e feiras | Jovem sorridente depositando uma lata numa estação de reciclagem FRIZZA em um festival |
| `comunidade/polaroid-01.webp` | frizzalovers.html → #FRIZZALOVERS → hero (polaroids) |  |
| `comunidade/polaroid-02.webp` | frizzalovers.html → #FRIZZALOVERS → hero (polaroids) |  |
| `comunidade/polaroid-03.webp` | frizzalovers.html → #FRIZZALOVERS → hero (polaroids) |  |
| `comunidade/polaroid-04.webp` | frizzalovers.html → #FRIZZALOVERS → hero (polaroids) |  |
| `comunidade/lovers-05.webp` | frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Foto de @rafa.no.sol: Pessoa de boné laranja e óculos equilibrando uma lata de FRIZZA Limão com Hortelã na cabeça |
| `comunidade/lovers-06.webp` | frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Foto de @duda.e.amigos: Três amigos vistos de cima bebendo FRIZZA de canudinho na rua |
| `comunidade/lovers-07.webp` | frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Foto de @theo.praia: Homem de óculos escuros bebendo FRIZZA Laranja Bahia sob o céu azul com nuvens |
| `comunidade/lovers-08.webp` | frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Foto de @gabi.foodie: Mulher fazendo careta divertida com duas latas FRIZZA na frente dos olhos |
| `comunidade/lovers-10.webp` | frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Foto de @joao_nofestival: Dois amigos sorrindo com latas FRIZZA em frente a uma parede verde |
| `comunidade/lovers-12.webp` | frizzalovers.html → #FRIZZALOVERS → galeria + lightbox | Foto de @aninha.sp: Mulher de boné e óculos escuros mostrando uma lata de FRIZZA Laranja Bahia |
| `comunidade/contato-hero.webp` | contato.html → Contato → hero | Duas amigas rindo ao ar livre, cada uma com uma lata FRIZZA na mão |

## Faltando (1)

Esses lugares continuam com placeholder (borda tracejada + nome do arquivo). Prompts prontos em [`FALTANDO.md`](FALTANDO.md).

- `historia/timeline-2018.webp` → historia.html → Nossa História → linha do tempo 2018 (1200×900)
