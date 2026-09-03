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
 │ 1. Image (12)  │ │ 2. Profile (9) │ │ 3. 3D & Math(4)│ │ 4. FX/Screens(12│ │ 5. Recorder(2) │ │ 6. Animator(1) │
 ├────────────────┤ ├────────────────┤ ├────────────────┤ ├────────────────┤ ├────────────────┤ ├────────────────┤
 │ • Chafa (C)    │ │ • Heatmap      │ │ • 3D City Voxel│ │ • The Matrix   │ │ • VHS (Go)     │ │ • SVG Animator │
 │ • Braille 2x4  │ │   Cascade SVG  │ │ • 3D Wordmark  │ │ • cbonsai Tree │ │   .tape to GIF │ │   Oscillation, │
 │ • TrueColor RGB│ │ • Neofetch Card│ │ • FIGlet Text  │ │ • Asciiquarium │ │ • AGG (Rust)   │ │   Scanline CRT,│
 │ • Drawille HD  │ │ • Dark Stats   │ │ • 3D Donut.c   │ │ • Cowsay Studio│ │   .cast to GIF │ │   Waves & Drop │
 │ • Retro Dither │ │ • Pokemon Card │ └────────────────┘ │ • Tetris Reveal│ └────────────────┘ └────────────────┘
 │ • jp2a Classic │ │ • wttr.in Card │                    │ • BBS CP437 VGA│
 │ • Halftone Dot │ │ • TTY Clock LED│                    │ • QR Code Badge│
 │ • Edge Art Ink │ │ • Chess Match  │                    │ • Pipes.sh Loop│
 │ • Glitch VHS   │ │ • File Tree    │                    │ • CAVA Equalizer
 │ • Pixel Mosaic │ │ • Fortune Card │                    │ • Doom Fire 1992
 │ • Palette Swap │ └────────────────┘                    │ • Synthwave Grid
 │ • Rainbow Wave │                                       │ • Game of Life │
 └────────────────┘                                       └────────────────┘
```

---

## 🎨 Tabela Completa de Motores e Efeitos

### 🖼️ Transformação de Imagens & Cores (12 Motores)

| Motor | Inspiração / Upstream | Tipo | O que faz |
| :--- | :--- | :--- | :--- |
| **`rgb_ascii`** | Mezzold Core | TrueColor | Converte fotos em ASCII 24-bit colorido de alta fidelidade com animações de onda contínua. |
| **`drawille`** | `asciimoo/drawille` | Subpixel Braille | Matriz 2x4 Unicode com **8x mais resolução** que o ASCII padrão e amostragem TrueColor. |
| **`dither`** | `leeoniya/dither` | Retro Dither | Algoritmos históricos de difusão: **Atkinson** (Macintosh 1984), **Floyd-Steinberg** e **Bayer 4x4** (Game Boy). |
| **`jp2a`** | `cslarsen/jp2a` | Unix Classic | Conversor JPEG-to-ASCII com equalização de histograma, inversão e rampas personalizadas. |
| **`halftone`** | `ironwallaby/dither` | Press Retícula | Retícula de impressão de jornais antigos e histórias em quadrinhos com pontos geométricos (`• ● ⬤`). |
| **`edge_art`** | Sobel Filter | Manga Blueprint | Detecção de bordas direcionais mapeando gradientes para traços nanquim (`/ \ │ ─ +`). |
| **`glitch`** | Cyberpunk VHS | Glitch & CRT | Aberração cromática com divisão de canais RGB horizontal, scanlines analógicas e ruído digital. |
| **`pixel_mosaic`** | PICO-8 / C64 | 8-Bit Arcade | Sprites retrô com quantização para paletas dos consoles clássicos (**PICO-8**, **Commodore 64**, **Game Boy**). |
| **`palette_swap`** | Developer Themes | Quantização | Quantiza fotos para temas de IDEs: **Dracula**, **Catppuccin**, **Nord**, **Gruvbox**, **TokyoNight**. |
| **`rainbow_wave`** | `busyloop/lolcat` | Rainbow Shifter | Aplica gradiente contínuo de onda senoidal de arco-íris sobre textos e arte ASCII com ciclo animado. |
| **`chafa`** | `hpjansson/chafa` | Binário C Nativo | Gráficos de terminal ultra-HD usando múltiplos símbolos e blocos Unicode. |
| **`signature`** | Mezzold HD | Caligrafia | Assinaturas e logotipos com recorte cirúrgico de margens e gradientes vibrantes. |

---

### 🕹️ Screensavers Retrô, 3D & Efeitos Ambientais (12 Motores)

| Motor | Inspiração / Upstream | Tipo | O que faz |
| :--- | :--- | :--- | :--- |
| **`doom_fire`** | `posva/terminal-fire` | Simulação 1992 | A lendária rotina de fogo do Doom / PSX com partículas dissipando em chamas vivas em SVG 60fps. |
| **`cmatrix`** | `abishekvashok/cmatrix` | Screensaver | Chuva de código digital de *The Matrix* com Katakana, líderes brilhantes brancos e rastros verdes em 60fps. |
| **`cbonsai`** | `jallbrit/cbonsai` | Procedural | Árvores Bonsai japonesas fractais com flores de cerejeira (*Sakura*) ou pinheiro (*Pine*) oscilando ao vento. |
| **`asciiquarium`**| `cmatsuoka/asciiquarium`| Screensaver | Aquário marinho com cardumes de peixes, tubarão patrulheiro, bolhas de ar e algas marinhas. |
| **`donut_3d`** | `a1k0n/donut.c` | Matemática 3D | O lendário Donut giratório 3D de Andy Sloane em flipbook vetorial SVG 60fps com iluminação Phong. |
| **`synthwave_grid`**| Outrun 80s | 3D Wireframe | Horizonte synthwave dos anos 80 com sol neon fatiado e grade de perspectiva 3D em movimento infinito. |
| **`cava`** | `karlstav/cava` | Audio Visualizer| Barras de espectro de áudio equalizadas oscilando em tempo real com gradientes cyberpunk. |
| **`game_of_life`** | John Conway | Autômato Celular | O clássico Jogo da Vida com gliders, pulsars e naves espaciais evoluindo em loop contínuo. |
| **`pipes`** | `pipeseroni/pipes.sh` | Screensaver | Labirinto procedural de encanamentos 3D com loop infinito e animação de crescimento. |
| **`cowsay`** | `cowsay / ponysay` | Balão Unix | Balões de diálogo clássicos com mascotes (**Cow**, **Dragon**, **Robot**, **Cat**, **Ghost**). |
| **`tetris_reveal`**| Gravity Engine | Revelação | Os blocos de pixels caem do teto com gravidade e ricochete até travar em suas posições e revelar a imagem. |
| **`ansi_cp437`** | `ansilove / TheDraw` | BBS Teletext | Arte de BBS dos anos 90 com blocos sombreados do Code Page 437 (`░ ▒ ▓ █`) e 16 cores VGA. |

---

### 📊 Widgets de Perfil & Estética Developer (9 Motores)

| Motor | Inspiração / Upstream | O que faz |
| :--- | :--- | :--- |
| **`pokemon_card`** | `phisch/pokemon-colorscripts` | Card RPG de batalha com sprites 8-bit/16-bit de Pokémon clássicos, barra de HP e Pokédex. |
| **`weather_card`** | `chubin/wttr.in` | Previsão do tempo retro em ASCII com fases da lua, tendências térmicas e ícones animados. |
| **`tty_clock`** | `xorg62/tty-clock` | Relógio digital LED 7-segmentos em blocos com dois pontos pulsantes e carimbo de data. |
| **`chess_board`** | GNU Chess / FEN | Tabuleiro de xadrez com peças Unicode, coordenadas algébricas e partidas históricas (Kasparov). |
| **`file_tree`** | Unix `tree` / `eza` | Árvore de diretórios com ícones de desenvolvedor e guias de ramos (`├──`, `└──`). |
| **`fortune_banner`**| BSD `fortune` | Biscoito da sorte Unix com citações de pioneiros da computação e cursor piscante. |
| **`heatmap`** | Zero-Token Scraper | Heatmap em cascata animada de contribuições do GitHub sem requisição de API tokens. |
| **`neofetch`** | Unix `neofetch` | Cartão de especificações técnicas do desenvolvedor no estilo terminal macOS. |
| **`stats_card`** | `github-readme-stats` | Card de métricas e estatísticas do GitHub em dark-mode moderno. |

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
* **Download Direto:** Baixe o arquivo SVG gerado pronto para colocar no seu README do GitHub.

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

## 📦 Upstream Repositories & Reconhecimentos

* [hpjansson/chafa](https://github.com/hpjansson/chafa) — Motor C de gráficos subpixel
* [asciimoo/drawille](https://github.com/asciimoo/drawille) — Algoritmo 2x4 Unicode Braille
* [leeoniya/dither](https://github.com/leeoniya/dither) — Dithering com difusão de erro
* [cslarsen/jp2a](https://github.com/cslarsen/jp2a) — JPEG para ASCII clássico
* [abishekvashok/cmatrix](https://github.com/abishekvashok/cmatrix) — Screensaver The Matrix em C
* [jallbrit/cbonsai](https://github.com/jallbrit/cbonsai) — Árvore Bonsai procedural
* [cmatsuoka/asciiquarium](https://github.com/cmatsuoka/asciiquarium) — Aquário marinho animado
* [a1k0n/donut.c](https://www.a1k0n.net/2011/07/20/donut-math.html) — O clássico 3D Donut de Andy Sloane
* [karlstav/cava](https://github.com/karlstav/cava) — Visualizador de áudio ALSA em ASCII
* [phisch/pokemon-colorscripts](https://github.com/phisch/pokemon-colorscripts) — Sprites de Pokémon em terminal
* [chubin/wttr.in](https://github.com/chubin/wttr.in) — Previsão do tempo em ASCII
* [xorg62/tty-clock](https://github.com/xorg62/tty-clock) — Relógio digital de terminal
* [busyloop/lolcat](https://github.com/busyloop/lolcat) — Gradiente contínuo de arco-íris
* [posva/terminal-fire](https://github.com/posva/terminal-fire) — Efeito de fogo Doom 1992
* [charmbracelet/vhs](https://github.com/charmbracelet/vhs) — Gravador de sessões de terminal em Go
* [asciinema/agg](https://github.com/asciinema/agg) — Renderizador de terminal em Rust
* [yoshi389111/github-profile-3d-contrib](https://github.com/yoshi389111/github-profile-3d-contrib) — Cidade 3D isométrica de commits
* [pipeseroni/pipes.sh](https://github.com/pipeseroni/pipes.sh) — Canos procedurais de terminal

---

## 👨‍💻 Autor & Licença

* **Arquiteto Líder:** [Vinícius Noetzold](https://github.com/ViniciusNoetzold) — **Mezzold Studios**
* **Licença:** [MIT License](LICENSE)
