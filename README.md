<div align="center">

```text
  __  __                         _      _____                     _         _   
 |  \/  |                       | |    |_   _|                   / \   _ __| |_ 
 | |\/| | ___ ___________  _  __| |______| | ___ _ __ _ __ ___  / _ \ | '__| __|
 | |  | |/ _ \_  /_  / _ \| |/ _` |______| |/ _ \ '__| '_ ` _ \/ ___ \| |  | |_ 
 |_|  |_|\___//__//__\___/|_|\__,_|      |_|\___/_|  |_| |_| /_/   \_\_|   \__|
```

# Mezzold TermArt Suite v2.0 🚀
### *The Ultimate Terminal Art, Image Conversion & GitHub Profile Studio*

**A powerhouse uniting 32 world-class open-source engines into a single CLI and real-time Visual Web Studio.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Engines](https://img.shields.io/badge/Engines-Go_%2B_Rust_%2B_C_%2B_Python-00ADD8?style=for-the-badge)](#)
[![Zero Token](https://img.shields.io/badge/Security-Zero_Token-2ea44f?style=for-the-badge&logo=github)](#)
[![Pure SVG](https://img.shields.io/badge/Graphics-Pure_Animated_SVG-orange?style=for-the-badge)](#)
[![Mezzold Studios](https://img.shields.io/badge/Creator-Mezzold_Studios-8a2be2?style=for-the-badge)](#)

</div>

---

## ⚡ Visão Geral / Overview

O **Mezzold TermArt Suite** é a mais completa suíte open-source para criação de arte em terminal, transformação estilística de fotos e personalização estética de perfis do GitHub.

Reúne motores compilados de alta performance em **C**, **Go**, **Rust** e algoritmos matemáticos em **Python** sob uma **arquitetura modular e extensível de plugins** (`@registry.register`). Oferece tanto uma interface via linha de comando (**CLI**) quanto um **Web Studio Visual em Tempo Real** com suporte a arrastar-e-soltar e pré-visualização instantânea.

---

## 🏛️ Os 6 Pilares & 32 Motores Registrados

```
                                 ┌────────────────────────────────────────────────────────┐
                                 │                Mezzold TermArt Suite                   │
                                 │            (Extensible Plugin Registry)                │
                                 └───────────────────────────┬────────────────────────────┘
                                                             │
         ┌──────────────────┬─────────────────┼──────────────────┬──────────────────┬─────────────────┐
         ▼                  ▼                 ▼                  ▼                  ▼                 ▼
 ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
 │ 1. Image (12)  │ │ 2. Profile (9) │ │ 3. 3D & Math(4)│ │ 4. FX & CRT(12)│ │ 5. Recorder(2) │ │ 6. Animator(1) │
 ├────────────────┤ ├────────────────┤ ├────────────────┤ ├────────────────┤ ├────────────────┤ ├────────────────┤
 │ • Chafa (C)    │ │ • Heatmap Live │ │ • 3D City Voxel│ │ • The Matrix   │ │ • VHS (Go)     │ │ • SVG Animator │
 │ • Braille 2x4  │ │ • Neofetch Card│ │ • 3D Wordmark  │ │ • cbonsai Tree │ │   .tape to GIF │ │   Oscillation, │
 │ • TrueColor RGB│ │ • Dark Stats   │ │ • FIGlet Text  │ │ • Asciiquarium │ │ • AGG (Rust)   │ │   Scanline CRT,│
 │ • Drawille HD  │ │ • Pokemon Card │ │ • 3D Donut.c   │ │ • Cowsay Studio│ │   .cast to GIF │ │   Waves & Drop │
 │ • Retro Dither │ │ • wttr.in Card │ │                │ │ • Tetris Reveal│ │                │ │                │
 │ • jp2a Classic │ │ • TTY Clock LED│ │                │ │ • BBS CP437 VGA│ │                │ │                │
 │ • Halftone Dot │ │ • Chess Match  │ │                │ │ • QR Code Badge│ │                │ │                │
 │ • Edge Art Ink │ │ • File Tree    │ │                │ │ • Pipes.sh Loop│ │                │ │                │
 │ • Glitch VHS   │ │ • Fortune Card │ │                │ │ • CAVA Bars    │ │                │ │                │
 │ • Pixel Mosaic │ │                │ │                │ │ • Doom Fire    │ │                │ │                │
 │ • Palette Swap │ │                │ │                │ │ • Synthwave 80s│ │                │ │                │
 │ • Rainbow Wave │ │                │ │                │ │ • Game of Life │ │                │ │                │
 └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘
```

---

## 🎨 Tabela Completa de Motores e Efeitos

### 🖼️ Transformação de Imagens & Cores (12 Motores)

| Motor | Estilo / Tecnologia | Tipo | O que faz |
| :--- | :--- | :--- | :--- |
| **`rgb_ascii`** | TrueColor Matrix | Alta Resolução | Converte fotos em ASCII 24-bit colorido de alta fidelidade com animações de onda contínua. |
| **`drawille`** | Subpixel Braille | Matriz 2x4 | Matriz 2x4 Unicode com **8x mais resolução** que o ASCII padrão e amostragem TrueColor. |
| **`dither`** | Retro Dither | Difusão de Erro | Algoritmos históricos de difusão: **Atkinson** (Macintosh 1984), **Floyd-Steinberg** e **Bayer 4x4** (Game Boy). |
| **`jp2a`** | Unix Classic | Escala de Cinza | Conversor JPEG-to-ASCII com equalização de histograma, inversão e rampas personalizadas. |
| **`halftone`** | Press Retícula | Pontos Geométricos | Retícula de impressão de jornais antigos e histórias em quadrinhos com pontos geométricos (`• ● ⬤`). |
| **`edge_art`** | Sobel Filter | Manga Blueprint | Detecção de bordas direcionais mapeando gradientes para traços nanquim (`/ \ │ ─ +`). |
| **`glitch`** | Cyberpunk VHS | Aberração RGB | Aberração cromática com divisão de canais RGB horizontal, scanlines analógicas e ruído digital. |
| **`pixel_mosaic`** | PICO-8 / C64 | 8-Bit Arcade | Sprites retrô com quantização para paletas dos consoles clássicos (**PICO-8**, **Commodore 64**, **Game Boy**). |
| **`palette_swap`** | Developer Themes | Quantização | Quantiza fotos para temas de IDEs: **Dracula**, **Catppuccin**, **Nord**, **Gruvbox**, **TokyoNight**. |
| **`rainbow_wave`** | Rainbow Shifter | Espectro Contínuo | Aplica gradiente contínuo de onda senoidal de arco-íris sobre textos e arte ASCII com ciclo animado. |
| **`chafa`** | Binário Nativo | Sub-pixel HD | Gráficos de terminal ultra-HD usando múltiplos símbolos e blocos Unicode. |
| **`signature`** | Caligrafia Vetorial | Logotipos | Assinaturas e logotipos com recorte cirúrgico de margens e gradientes vibrantes. |

---

### 🕹️ Screensavers Retrô, 3D & Efeitos Ambientais (12 Motores)

| Motor | Estilo / Tecnologia | Tipo | O que faz |
| :--- | :--- | :--- | :--- |
| **`doom_fire`** | Simulação 1992 | Partículas PSX | A lendária rotina de fogo do Doom / PSX com partículas dissipando em chamas vivas em SVG 60fps. |
| **`cmatrix`** | Chuva Digital | Katakana Matrix | Chuva de código digital de *The Matrix* com Katakana, líderes brilhantes brancos e rastros verdes em 60fps. |
| **`cbonsai`** | Procedural Fractal | Botânica Zen | Árvores Bonsai japonesas fractais com flores de cerejeira (*Sakura*) ou pinheiro (*Pine*) oscilando ao vento. |
| **`asciiquarium`**| Aquário Dinâmico | Vida Marinha | Aquário marinho com cardumes de peixes, tubarão patrulheiro, bolhas de ar e algas marinhas. |
| **`donut_3d`** | Geometria 3D | Phong Shading | O lendário Donut giratório 3D em flipbook vetorial SVG 60fps com iluminação Phong. |
| **`synthwave_grid`**| Outrun 80s | 3D Wireframe | Horizonte synthwave dos anos 80 com sol neon fatiado e grade de perspectiva 3D em movimento infinito. |
| **`cava`** | Equalizador | Audio Visualizer| Barras de espectro de áudio equalizadas oscilando em tempo real com gradientes cyberpunk. |
| **`game_of_life`** | Autômato Celular | Matemática Discreta | O clássico Jogo da Vida com gliders, pulsars e naves espaciais evoluindo em loop contínuo. |
| **`pipes`** | Labirinto Procedural | Screensaver 3D | Labirinto procedural de encanamentos 3D com loop infinito e animação de crescimento. |
| **`cowsay`** | Balão Retrô | Mascotes ASCII | Balões de diálogo clássicos com mascotes (**Cow**, **Dragon**, **Robot**, **Cat**, **Ghost**). |
| **`tetris_reveal`**| Simulação Física | Revelação por Blocos| Os blocos de pixels caem do teto com gravidade e ricochete até travar em suas posições e revelar a imagem. |
| **`ansi_cp437`** | BBS Teletext | Code Page 437 | Arte de BBS dos anos 90 com blocos sombreados do Code Page 437 (`░ ▒ ▓ █`) e 16 cores VGA. |

---

### 📊 Widgets de Perfil & Estética Developer (9 Motores)

| Motor | Estilo / Tecnologia | O que faz |
| :--- | :--- | :--- |
| **`pokemon_card`** | Card RPG Battle | 16 Pokémon clássicos, modo Shiny com sparkles, seleção de Nível (Lv.5 a 100), HP dinâmico e lore da Pokédex. |
| **`weather_card`** | Terminal Radar | Previsão meteorológica detalhada com seletor de cidades mundiais, unidade (°C/°F), ícones ASCII ricos e telemetria. |
| **`tty_clock`** | Relógio Digital LED | Relógio digital LED 7-segmentos com 8 esquemas de cores (Matrix, Cyan, Âmbar, Rubi, etc.) e formato 12h/24h. |
| **`chess_board`** | Tabuleiro Animado | Reprodução animada completa lance a lance desde o lance 1 até o XEQUE-MATE (Opera Game, Pastor, Kasparov). |
| **`file_tree`** | Árvore de Código | Árvore de diretórios com ícones de desenvolvedor e guias de ramos (`├──`, `└──`). |
| **`fortune_banner`**| Filosofia Hacker | Biscoito da sorte Unix com citações de pioneiros da computação e cursor piscante. |
| **`heatmap`** | Contribuições GitHub | Heatmap em cascata animada de contribuições do GitHub sem requisição de API tokens. |
| **`neofetch`** | Terminal System Specs | Cartão de especificações técnicas do desenvolvedor no estilo terminal macOS. |
| **`stats_card`** | Métricas GitHub | Card de métricas e estatísticas do GitHub em dark-mode moderno. |

---

## 🖱️ Windows 1-Click Launchers (.bat)

Para uso imediato no Windows, basta dar **duplo clique**:

| Arquivo `.bat` | Função |
| :--- | :--- |
| **`iniciar_studio.bat`** | Inicia o servidor local e abre o **Web Studio Visual** no navegador (`localhost:7860`). |
| **`iniciar_terminal.bat`** | Abre o console interativo com menu visual, atalhos rápidos e gerador guiado de arte. |
| **`instalar_ferramentas.bat`** | Instala todas as dependências Python (`requirements.txt`) e valida os binários nativos. |

---

## 🖥️ Visual Web Studio (`termstudio.py`)

Inicie o estúdio visual com:
```bash
python termstudio.py
```
> Acesse automaticamente em: `http://localhost:7860`

* **Drag-and-Drop:** Arraste qualquer imagem e visualize a conversão em tempo real.
* **Seletor de Motores:** Alterne instantaneamente entre Drawille, Dither, Glitch, Pixel Mosaic, Chafa, etc.
* **Aba Screensavers & FX:** Escolha entre The Matrix, cbonsai, Asciiquarium, Donut 3D, CAVA, Doom Fire, Synthwave, Game of Life e gere SVGs em 1 clique.
* **Aba Stats & Widgets:** Gere cartões de Pokémon, Previsão do Tempo, Relógio LED, Tabuleiro de Xadrez, Árvore de Arquivos e Heatmaps.
* **Comparador em Grade (Multi-Seleção):** Compare múltiplos motores de imagem (*Chafa, RGB ASCII, Drawille, Dither, Halftone, etc.*) ou dezenas de fontes tipográficas FIGlet (*Slant, Isometric, Doom, Bloody, etc.*) simultaneamente lado a lado em blocos responsivos! Cada bloco possui botão individual **⭳ Baixar Este** e **📋 Copiar**, além de exportação completa do pacote em **.ZIP**.
* **Modo Leve (Economia de CPU):** Ative ou desative todas as animações com 1 clique para renderização estática ultrarrápida e navegação suave sem sobrecarregar a máquina.
* **Gravador VHS & AGG:** Editor visual de fitas `.tape` com inserção rápida de comandos, simulação animada 60fps em SVG e renderização ultrarrápida de gravações `.cast` em GIFs via `agg` (Rust).
* **Download Direto:** Baixe o arquivo SVG ou GIF gerado pronto para colocar no seu README do GitHub.

---

## 💻 Comandos da Linha de Comando (CLI)

```bash
# === Screensavers & Efeitos ===
python termart.py fire --cols 56 --rows 22 --out doom_fire.svg
python termart.py synthwave --out synthwave.svg
python termart.py life --theme phosphor --out game_of_life.svg
python termart.py cmatrix --color matrix_green --cols 50 --out matrix.svg
python termart.py cbonsai --type sakura --out bonsai.svg
python termart.py asciiquarium --fish 8 --out aquarium.svg
python termart.py donut --theme cyberpunk --out donut.svg
python termart.py cava --theme ocean --bars 36 --out cava.svg
python termart.py cowsay "Building epic terminal art!" --mascot dragon --out speech.svg
python termart.py qr "https://github.com/ViniciusNoetzold" --label "VINICIUS PROFILE" --out qr.svg
python termart.py pipes --username ViniciusNoetzold --out pipes.svg

# === Widgets de Perfil & Estética ===
python termart.py pokemon --pokemon gengar --out pokemon_gengar.svg
python termart.py weather --city "Curitiba, Brazil" --condition sunny --out weather.svg
python termart.py clock --color phosphor --out tty_clock.svg
python termart.py chess --match kasparov --out chess_kasparov.svg
python termart.py tree --title "mezzold-termart-suite" --out project_tree.svg
python termart.py fortune --out hacker_fortune.svg
python termart.py city ViniciusNoetzold --theme green --out contrib-3d-city.svg
python termart.py heatmap ViniciusNoetzold --out contrib-heatmap.svg
python termart.py neofetch --username ViniciusNoetzold --out info-card.svg
python termart.py stats ViniciusNoetzold --out stats-card.svg

# === Transformações de Imagem ===
python termart.py rainbow --text "MEZZOLD TERMART" --out rainbow.svg
python termart.py image foto.png --engine drawille --cols 60 --out drawille.svg
python termart.py image foto.png --engine dither --cols 60 --out retro_dither.svg
python termart.py image foto.png --engine glitch --cols 60 --out glitch.svg
python termart.py image foto.png --engine pixel_mosaic --cols 48 --out sprite_8bit.svg
python termart.py image foto.png --engine edge_art --cols 60 --out manga_sketch.svg
python termart.py image foto.png --engine palette_swap --cols 60 --out dracula_theme.svg
```

---

## 🧪 Testes Automatizados

Para rodar a suíte completa de validação de todos os motores:
```bash
python tests/test_all_engines.py
```

---

## 🧩 Extensibilidade: Como Adicionar Novos Plugins

Adicionar novos motores ao **Mezzold TermArt Suite** requer apenas criar uma classe em `src/termart/modules/<categoria>/`:

```python
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class MeuNovoMotor(BasePlugin):
    name = "meu_motor"
    category = "fx"
    description = "Descricao do meu efeito incrivel"

    def run(self, out_svg="output.svg", **kwargs):
        # Sua logica de geracao em SVG
        return {"status": "success", "output_path": out_svg}
```
O motor é **automaticamente descoberto e integrado** na CLI e no Web Studio!

---

## 💡 Inspirações & Referências

* [chafa](https://github.com/hpjansson/chafa) • [wttr.in](https://github.com/chubin/wttr.in) • [cmatrix](https://github.com/abishekvashok/cmatrix) • [cbonsai](https://github.com/jallbrit/cbonsai) • [asciiquarium](https://github.com/cmatsuoka/asciiquarium) • [drawille](https://github.com/asciimoo/drawille) • [vhs](https://github.com/charmbracelet/vhs) • [agg](https://github.com/asciinema/agg) • [cava](https://github.com/karlstav/cava) • [donut.c](https://www.a1k0n.net/2011/07/20/donut-math.html) • [tty-clock](https://github.com/xorg62/tty-clock) • [pokemon-colorscripts](https://github.com/phisch/pokemon-colorscripts) • [pipes.sh](https://github.com/pipeseroni/pipes.sh)

---

## 👨‍💻 Autor & Licença

* **Arquiteto Líder:** [Vinícius Noetzold](https://github.com/ViniciusNoetzold) — **Mezzold Studios**
* **Licença:** [MIT License](LICENSE)
