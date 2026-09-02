<div align="center">

```text
  __  __                         _      _____                     _         _   
 |  \/  |                       | |    |_   _|                   / \   _ __| |_ 
 | |\/| | ___ ___________  _  __| |______| | ___ _ __ _ __ ___  / _ \ | '__| __|
 | |  | |/ _ \_  /_  / _ \| |/ _` |______| |/ _ \ '__| '_ ` _ \/ ___ \| |  | |_ 
 |_|  |_|\___//__//__\___/|_|\__,_|      |_|\___/_|  |_| |_| /_/   \_\_|   \__|
```

# Mezzold TermArt Suite v2.0 🚀
### *The Extensible Terminal Art, Image Conversion & GitHub Profile Studio*

**A modular, all-in-one powerhouse uniting 9 world-class open-source engines into a single CLI and interactive Visual Web Studio.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Engines](https://img.shields.io/badge/Engines-Go_%2B_Rust_%2B_C_%2B_Python-00ADD8?style=for-the-badge)](#)
[![Zero Token](https://img.shields.io/badge/Security-Zero_Token-2ea44f?style=for-the-badge&logo=github)](#)
[![Pure SVG](https://img.shields.io/badge/Graphics-Pure_Animated_SVG-orange?style=for-the-badge)](#)
[![Mezzold Studios](https://img.shields.io/badge/Creator-Mezzold_Studios-8a2be2?style=for-the-badge)](#)

</div>

---

## ⚡ Overview

**Mezzold TermArt Suite** is the ultimate developer tool for terminal art, media transformation, and GitHub profile aesthetics. 

It unifies **C**, **Go**, **Rust**, and **Python** high-performance engines under an **extensible plugin architecture**, offering both a **fast Terminal CLI** and a **real-time Visual Web Studio**.

---

## 🏗️ The 5 Pillars & Integrated Upstream Engines

```
                                 ┌────────────────────────────────────────────────────────┐
                                 │                Mezzold TermArt Suite                   │
                                 │            (Extensible Plugin Registry)                │
                                 └───────────────────────────┬────────────────────────────┘
                                                             │
            ┌───────────────────────┬────────────────────────┼───────────────────────┬───────────────────────┐
            ▼                       ▼                        ▼                       ▼                       ▼
 ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
 │ 1. Image Engines    │ │ 2. Profile Widgets  │ │ 3. 3D & Isometric   │ │ 4. Term Recorders   │ │ 5. Procedural FX    │
 ├─────────────────────┤ ├─────────────────────┤ ├─────────────────────┤ ├─────────────────────┤ ├─────────────────────┤
 │ • Chafa (C Engine)  │ │ • Neofetch Specs    │ │ • 3D Voxel Skyline  │ │ • VHS (Go Engine)   │ │ • Retro Pipes       │
 │   Sub-pixel graphics│ │   macOS style SVG   │ │   (3d-contrib city) │ │   .tape to GIF/WebM │ │   (pipes.sh in SVG) │
 │ • Ascii-Converter   │ │ • Cascade Heatmap   │ │ • 3D Wireframe Text │ │ • AGG (Rust Engine) │ │ • Matrix Code Rain  │
 │   (Go Braille 2x4)  │ │   Zero-token commits│ │   Continuous flip   │ │   .cast to GIF      │ │   Digital cascade   │
 │ • Tight-Crop Logos  │ │ • Stats Card Dark   │ │   projection        │ │ • SVG-Term          │ │ • Future Shaders    │
 └─────────────────────┘ └─────────────────────┘ └─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

---

## 🖥️ Visual Web Studio (`termstudio.py`)

Prefer a visual experience? Launch the local Web Studio:

```bash
python termstudio.py
```
> Opens automatically in your browser at `http://localhost:7860`.

### ✨ Web Studio Features:
* **Drag-and-Drop Image Conversion:** Upload photos or cursive signatures, tweak columns/density, and see the live ASCII/Braille SVG preview instantly.
* **3D City & Wireframe Visualizer:** Enter any GitHub username to inspect their 3D isometric voxel skyline or render oscillating 3D text.
* **Live Heatmap & Neofetch Designer:** Real-time preview of your contribution cascade and system specification cards.
* **1-Click Download:** Download any rendered SVG directly from the preview canvas.

---

## 💻 CLI Commands

The suite exposes a unified, intuitive command-line interface:

### 🖼️ Image & Portraits
```bash
# High-DPI Sub-pixel conversion via Chafa (C engine)
python termart.py image avatar.jpg --engine chafa --cols 80

# High-DPI Braille conversion via Go binary
python termart.py image avatar.jpg --engine ascii_braille --braille --cols 76

# Self-typing terminal portrait with titlebar and animated cursor
python termart.py portrait avatar.jpg --username ViniciusNoetzold --name "Vinícius Noetzold" --out portrait.svg

# Tight-cropped cursive signature / brand logo in Braille HD
python termart.py signature signature.png --title "./signature.sh" --cols 58 --out signature.svg
```

### 🧊 3D & Isometric
```bash
# 3D Isometric Voxel Contribution City (inspired by github-profile-3d-contrib)
python termart.py city ViniciusNoetzold --out contrib-3d-city.svg

# 3D Oscillating Wireframe Wordmark flipbook
python termart.py wordmark --text "MEZZOLD\nSTUDIOS" --cols 52 --out wordmark.svg
```

### 📊 Profile & Widgets
```bash
# Real-time contribution heatmap (zero tokens required!)
python termart.py heatmap ViniciusNoetzold --out contrib-heatmap.svg

# Unix Neofetch terminal specs card with palette chips
python termart.py neofetch --username ViniciusNoetzold --out info-card.svg

# Sleek dark-mode GitHub stats card
python termart.py stats ViniciusNoetzold --out stats-card.svg
```

### 🕹️ Procedural FX & Screensavers
```bash
# Nostalgic procedural pipes screensaver in animated SVG (inspired by pipes.sh)
python termart.py pipes --username ViniciusNoetzold --out pipes.svg
```

### 🔌 Inspect Loaded Plugins
```bash
python termart.py plugins
```

---

## 🧩 Extensibility: How to Add New Plugins

Adding new modules to **Mezzold TermArt Suite** is effortless. Just create a file in `src/termart/modules/<category>/` inheriting from `BasePlugin`:

```python
from ...core.plugin import BasePlugin
from ...core.registry import registry

@registry.register
class MyCustomPlugin(BasePlugin):
    name = "custom_effect"
    category = "fx"
    description = "My awesome new terminal effect"

    def run(self, **kwargs):
        # Your custom generation logic
        return {"status": "success", "output_path": "output.svg"}
```

The plugin is **automatically discovered and registered** into both the CLI and the Web Studio!

---

## 📦 Upstream Repositories & Inspirations

This suite stands on the shoulders of giants:
* [hpjansson/chafa](https://github.com/hpjansson/chafa) — Sub-pixel terminal graphics engine (C)
* [TheZoraiz/ascii-image-converter](https://github.com/TheZoraiz/ascii-image-converter) — Braille & ASCII converter (Go)
* [charmbracelet/vhs](https://github.com/charmbracelet/vhs) — Terminal recording tool (Go)
* [asciinema/agg](https://github.com/asciinema/agg) — Asciinema GIF generator (Rust)
* [yoshi389111/github-profile-3d-contrib](https://github.com/yoshi389111/github-profile-3d-contrib) — 3D contribution city (TypeScript)
* [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats) — Dynamic GitHub stats (Node.js)
* [lowlighter/metrics](https://github.com/lowlighter/metrics) — Comprehensive SVG metrics (TypeScript)
* [pipeseroni/pipes.sh](https://github.com/pipeseroni/pipes.sh) — Retro terminal pipes animation (Bash)
* [marionebl/svg-term-cli](https://github.com/marionebl/svg-term-cli) — Terminal session to SVG (Node.js)
* [AVIVASHISHTA29](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29) — Animated SVG profile concept

---

## 👨‍💻 Creator & License

* **Lead Architect:** [Vinícius Noetzold](https://github.com/ViniciusNoetzold) — **Mezzold Studios**
* **License:** [MIT License](LICENSE)
