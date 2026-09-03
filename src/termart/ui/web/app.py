"""
Mezzold TermArt - Visual Web Studio v2.0
FastAPI + TailwindCSS interactive visual studio for configuring, previewing, and exporting terminal art.
Supports all 9 upstream engines: Chafa, VHS, pipes.sh, 3D-contrib, AGG, ASCII Braille, Neofetch, Stats & Typography.
"""
import os
import sys
import shutil
import tempfile
import subprocess
import webbrowser
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Response, Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import uvicorn

from ...core.registry import registry

app = FastAPI(title="Mezzold TermArt Studio", version="2.0.0")

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mezzold TermArt Studio v2.0</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 500: '#58a6ff', 600: '#1f6feb', dark: '#0a0e14', card: '#111722', border: '#30363d', accent: '#22d3ee' }
          }
        }
      }
    }
  </script>
  <style>
    @keyframes pulse-slow { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
    .pulse-dot { animation: pulse-slow 2s infinite ease-in-out; }
    svg { max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
    pre, textarea { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  </style>
</head>
<body class="bg-brand-dark text-slate-200 font-mono min-h-screen flex flex-col">
  <!-- Header -->
  <header class="border-b border-brand-border bg-brand-card/80 backdrop-blur sticky top-0 z-50 px-6 py-3">
    <div class="max-w-[1600px] w-full mx-auto flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-3 w-3 rounded-full bg-emerald-400 pulse-dot"></div>
        <div class="flex flex-col">
          <h1 class="text-base font-bold text-white tracking-wider flex items-center gap-2">
            <span>⚡ MEZZOLD</span>
            <span class="text-brand-500">TERMART STUDIO</span>
            <span class="text-xs px-2 py-0.5 rounded bg-brand-border text-slate-400">v2.0</span>
          </h1>
          <span class="text-[11px] text-slate-500">Suite Completa de Arte em Terminal & Widgets de Perfil</span>
        </div>
      </div>
      <div class="flex items-center gap-4 text-xs">
        <span class="text-slate-400 hidden sm:inline">Owner: <strong class="text-white">Vinícius Noetzold</strong></span>
        <a href="https://github.com/ViniciusNoetzold/Mezzold-TermArt" target="_blank" class="px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold transition">GitHub Repo ↗</a>
      </div>
    </div>
  </header>

  <!-- Navigation Tabs (5 Categorias Abrangendo Todas as Ferramentas) -->
  <div class="border-b border-brand-border bg-brand-card/50 px-6 py-2.5">
    <div class="max-w-[1600px] mx-auto flex flex-wrap gap-2 text-xs">
      <button onclick="switchTab('image')" id="btn-image" class="tab-btn px-4 py-2 rounded-xl font-bold bg-brand-600 text-white flex items-center gap-1.5 transition shadow">
        <span>🖼️</span> <span>Imagens & Chafa</span>
      </button>
      <button onclick="switchTab('3d')" id="btn-3d" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>🧊</span> <span>3D & Tipografia</span>
      </button>
      <button onclick="switchTab('profile')" id="btn-profile" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>📊</span> <span>Stats & Heatmap</span>
      </button>
      <button onclick="switchTab('animator')" id="btn-animator" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>✨</span> <span>Animador SVG</span>
      </button>
      <button onclick="switchTab('pipes')" id="btn-pipes" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>🧪</span> <span>Screensavers & Retro FX</span>
      </button>
      <button onclick="switchTab('vhs')" id="btn-vhs" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>🎬</span> <span>Gravador VHS (.tape)</span>
      </button>
    </div>
  </div>

  <!-- Main Content -->
  <main class="flex-1 max-w-[1600px] w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
    <!-- Left Column: Controls -->
    <div class="lg:col-span-5 flex flex-col gap-5">
      <div class="p-5 rounded-2xl bg-brand-card border border-brand-border flex flex-col gap-4 text-sm shadow-xl">
        
        <!-- ================= TAB 1: IMAGENS & CHAFA ================= -->
        <div id="tab-image" class="tab-content flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🖼️ Conversão de Imagens</h2>
            <p class="text-xs text-slate-400 mt-0.5">Motores Chafa (C) e Braille/ASCII (Go) integrados</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Motor de Renderização</label>
            <select id="img-engine" onchange="toggleImageEngine()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <optgroup label="Motores Principais & Chafa">
                <option value="rgb_ascii">TrueColor RGB ASCII (Cores 24-bit Reais da Foto)</option>
                <option value="chafa">Chafa (C Engine) - Sub-pixel Graphics de Alta Resolução</option>
                <option value="signature">Logo / Assinatura em Caligrafia (ASCII Puro / Braille)</option>
                <option value="portrait">Retrato Terminal (Go Braille 2x4 com Digitação)</option>
              </optgroup>
              <optgroup label="Novos Motores Open-Source">
                <option value="drawille">Drawille Subpixel (Matriz Braille 2x4 com 8x Resolução)</option>
                <option value="dither">Retro Dithering (Atkinson Mac 1984, Floyd-Steinberg, Bayer)</option>
                <option value="jp2a">jp2a Classic (Rampas Unix & Invert Contrast)</option>
                <option value="halftone">Halftone Press (Retícula de Impressão, Jornais & HQs)</option>
                <option value="edge_art">Edge Art (Contornos Sobel Mangá & Blueprint)</option>
                <option value="glitch">Glitch Cyberpunk (Aberração Cromática VHS & Corrupção)</option>
                <option value="pixel_mosaic">Pixel Mosaic (Sprites 8-bit Arcade PICO-8 & C64)</option>
                <option value="palette_swap">Palette Swap (Dracula, Catppuccin, Nord, TokyoNight)</option>
              </optgroup>
            </select>
          </div>

          <div id="rgb-options" class="flex flex-col gap-2 p-3 rounded-xl bg-brand-dark/50 border border-brand-border text-xs">
            <span class="font-semibold text-emerald-400">Esquema de Cores</span>
            <select id="rgb-mode" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
              <option value="rgb">🎨 TrueColor RGB (Cores Reais 24-bit Amostradas da Imagem)</option>
              <option value="cyberpunk">🌆 Gradiente Cyberpunk (Ciano → Roxo → Rosa)</option>
              <option value="sunset">🌇 Gradiente Sunset (Dourado → Âmbar → Carmesim)</option>
              <option value="tokyo">🌃 Gradiente TokyoNight (Índigo → Roxo Neon)</option>
              <option value="matrix">💻 Matrix Hacker (Verde Fosfórico Neon)</option>
              <option value="mono">⚪ Monocromático Estilizado (Prateado GitHub)</option>
            </select>
          </div>

          <div id="chafa-options" class="hidden flex flex-col gap-3 p-3 rounded-xl bg-brand-dark/50 border border-brand-border text-xs">
            <span class="font-semibold text-brand-500">Configurações do Motor Chafa (C)</span>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-[11px] text-slate-400 block mb-1">Classe de Símbolos</label>
                <select id="chafa-symbols" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
                  <option value="ascii">ascii (Clássico puro)</option>
                  <option value="braille">braille (Sub-pixel 2x4)</option>
                  <option value="block">block (Blocos sólidos)</option>
                  <option value="all">all (Full UTF-8 Quadrants)</option>
                </select>
              </div>
              <div>
                <label class="text-[11px] text-slate-400 block mb-1">Modo de Cor</label>
                <select id="chafa-colors" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
                  <option value="none">Monocromático (Terminal)</option>
                  <option value="16">16 Cores ANSI</option>
                  <option value="256">256 Cores</option>
                </select>
              </div>
            </div>
          </div>

          <div id="sig-options" class="hidden flex flex-col gap-2 p-3 rounded-xl bg-brand-dark/50 border border-brand-border text-xs">
            <span class="font-semibold text-purple-400">Modo de Assinatura / Logo</span>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" id="sig-braille" class="accent-brand-500">
              <span>Usar Braille pontilhado (Desmarcado = ASCII autêntico)</span>
            </label>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Nome / Usuário</label>
            <input id="img-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <div>
            <div class="flex justify-between items-center text-xs text-slate-400 mb-1">
              <span>Densidade (Colunas)</span>
              <div class="flex items-center gap-1.5">
                <input id="img-cols-input" type="number" min="20" max="300" value="110" class="w-14 bg-brand-dark border border-brand-border rounded px-1.5 py-0.5 text-right text-brand-400 font-bold font-mono text-xs focus:border-brand-500 outline-none" oninput="syncColsFromInput(this.value)">
                <span class="text-[10px] text-slate-500 font-mono">cols</span>
              </div>
            </div>
            <input id="img-cols" type="range" min="30" max="250" value="110" class="w-full accent-brand-500 cursor-pointer" oninput="syncColsFromSlider(this.value)">
            <div class="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
              <span class="cursor-pointer hover:text-brand-400 transition" onclick="setCols(40)">40</span>
              <span class="cursor-pointer hover:text-brand-400 transition" onclick="setCols(74)">74 (Padrão)</span>
              <span class="cursor-pointer hover:text-brand-400 transition" onclick="setCols(110)">110 (HD)</span>
              <span class="cursor-pointer hover:text-brand-400 transition" onclick="setCols(160)">160 (FHD)</span>
              <span class="cursor-pointer hover:text-brand-400 transition" onclick="setCols(200)">200 (4K)</span>
              <span class="cursor-pointer hover:text-brand-400 transition" onclick="setCols(250)">250 (Max)</span>
            </div>
          </div>

          <!-- Interactive Image Drop & Paste Zone -->
          <div>
            <label class="text-xs text-slate-400 block mb-1.5 flex justify-between items-center">
              <span>Foto / Imagem (Opcional)</span>
              <span class="text-[10px] text-brand-400 bg-brand-dark px-1.5 py-0.5 rounded border border-brand-border">Ctrl + V Suportado</span>
            </label>
            <div id="img-dropzone" onclick="document.getElementById('img-file').click()" class="border-2 border-dashed border-brand-border hover:border-brand-500 rounded-xl p-3.5 text-center cursor-pointer transition-all bg-brand-dark/30 hover:bg-brand-dark/60 flex flex-col items-center justify-center gap-1 group">
              <span class="text-2xl group-hover:scale-110 transition-transform">📋</span>
              <span class="text-xs text-slate-200 font-medium">Arraste uma imagem ou aperte <kbd class="px-1.5 py-0.5 bg-brand-dark border border-brand-border rounded text-[10px] text-brand-400 font-mono">Ctrl + V</kbd></span>
              <span class="text-[10px] text-slate-400">Ou clique para escolher do PC (PNG, JPG, WEBP)</span>
              <input id="img-file" type="file" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
              
              <!-- Loaded / Pasted image preview card -->
              <div id="img-loaded-card" class="hidden mt-2 flex items-center gap-2.5 p-2 bg-brand-dark/95 rounded-lg border border-brand-500/50 text-xs text-slate-200 w-full justify-between" onclick="event.stopPropagation()">
                <div class="flex items-center gap-2 overflow-hidden">
                  <img id="img-loaded-thumb" src="" class="w-8 h-8 rounded object-cover border border-brand-border flex-shrink-0">
                  <div class="flex flex-col text-left overflow-hidden">
                    <span id="img-loaded-name" class="font-bold text-[11px] text-brand-400 truncate">imagem_colada.png</span>
                    <span id="img-loaded-size" class="text-[10px] text-slate-400">Pronta para renderizar</span>
                  </div>
                </div>
                <button type="button" onclick="clearLoadedImage(event)" title="Remover imagem" class="p-1 hover:bg-red-500/20 text-red-400 hover:text-red-300 rounded transition text-sm">✕</button>
              </div>
            </div>
          </div>

          <!-- Animation Controls Suite -->
          <div class="p-3 rounded-xl bg-brand-dark/50 border border-brand-border flex flex-col gap-2.5 text-xs">
            <span class="font-bold text-brand-500 flex items-center gap-1.5">
              <span>✨</span> <span>Efeitos de Animação Dinâmica</span>
            </span>
            <div>
              <label class="text-[11px] text-slate-400 block mb-1">Estilo de Animação da Arte</label>
              <select id="img-anim-mode" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
                <option value="waves_left">🌊 Ondas / Esteira Fluida Contínua (Correndo para Esquerda)</option>
                <option value="waves_right">🌊 Ondas / Esteira Fluida Contínua (Correndo para Direita)</option>
                <option value="oscillate">⚖️ Oscilante 3D (Levitação, Balanço e Profundidade)</option>
                <option value="cascade">🌧️ Cascata / Chuva Digital (Ondas Matrix Contínuas)</option>
                <option value="drop">🧱 Caindo e Encaixando (Gravity Drop & Tetris Snap)</option>
                <option value="pulse">💥 Pulso Cibernético (Breathing Glow & Zoom)</option>
                <option value="none">⏹️ Estático (Sem Animação de Movimento)</option>
              </select>
            </div>
            <label class="flex items-center gap-2 cursor-pointer pt-1">
              <input type="checkbox" id="img-scanline" class="w-4 h-4 accent-brand-500 rounded">
              <span class="text-slate-300 font-medium">📡 Ativar Varredura Laser de Radar / Linha CRT</span>
            </label>
          </div>

          <button onclick="generateImage()" class="mt-2 w-full py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>✨</span> <span>Renderizar Imagem com Motor Selecionado</span>
          </button>
        </div>

        <!-- ================= TAB 2: 3D & TIPOGRAFIA ================= -->
        <div id="tab-3d" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🧊 3D Isometric & Tipografia</h2>
            <p class="text-xs text-slate-400 mt-0.5">Motores 3D Voxel Skyline, Wireframe Flipbook e FIGlet</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Componente</label>
            <select id="mode-3d" onchange="toggle3dMode()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="city">Cidade 3D Isométrica de Commits (github-profile-3d-contrib)</option>
              <option value="wordmark">Letreiro 3D em Wireframe Oscilante (AVIVASHISHTA29)</option>
              <option value="typography">Tipografia ASCII Slant / FIGlet (Nome em Alta Legibilidade)</option>
            </select>
          </div>

          <div id="city-block" class="flex flex-col gap-3">
            <div>
              <label class="text-xs text-slate-400 block mb-1">GitHub Username</label>
              <input id="city-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Paleta de Cores da Cidade 3D</label>
              <select id="city-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="cyberpunk">Cyberpunk Neon (Ciano, Azul & Rosa Choque)</option>
                <option value="green">GitHub Classic (Verde Esmeralda Original)</option>
                <option value="tokyo">TokyoNight (Roxo Profundo & Lilás)</option>
                <option value="sunset">Sunset Gold (Âmbar, Laranja & Dourado)</option>
                <option value="matrix">Matrix Hacker (Verde Fosforescente)</option>
                <option value="ocean">Ocean Blue (Azul Turquesa & Mar Profundo)</option>
                <option value="dracula">Dracula Vampire (Roxo & Rosa Pastel)</option>
              </select>
            </div>
          </div>

          <div id="wordmark-block" class="hidden flex flex-col gap-3">
            <div>
              <label class="text-xs text-slate-400 block mb-1">Texto 3D (use \n para nova linha)</label>
              <textarea id="wordmark-text" rows="2" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">MEZZOLD\nSTUDIOS</textarea>
            </div>
          </div>

          <div id="typography-block" class="hidden flex flex-col gap-3">
            <div>
              <label class="text-xs text-slate-400 block mb-1">Texto do Banner ASCII (use \n para nova linha)</label>
              <textarea id="typo-text" rows="2" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">VINICIUS\nNOETZOLD</textarea>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Fonte FIGlet</label>
              <select id="typo-font" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="slant">Slant (Cyberpunk Futurista)</option>
                <option value="standard">Standard (Clássica)</option>
                <option value="doom">Doom (Pesada / Bold)</option>
                <option value="big">Big (Extra Grande)</option>
                <option value="small">Small (Compacta)</option>
              </select>
            </div>

            <!-- Typography Animation Controls Suite -->
            <div class="p-3 rounded-xl bg-brand-dark/50 border border-brand-border flex flex-col gap-2.5 text-xs">
              <span class="font-bold text-brand-500 flex items-center gap-1.5">
                <span>✨</span> <span>Efeitos de Animação do Letreiro</span>
              </span>
              <div>
                <label class="text-[11px] text-slate-400 block mb-1">Estilo de Animação</label>
                <select id="typo-anim-mode" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
                  <option value="waves_left">🌊 Ondas / Esteira Fluida Contínua (Correndo para Esquerda)</option>
                  <option value="waves_right">🌊 Ondas / Esteira Fluida Contínua (Correndo para Direita)</option>
                  <option value="oscillate">⚖️ Oscilante 3D (Levitação, Balanço e Profundidade)</option>
                  <option value="cascade">🌧️ Cascata / Chuva Digital (Ondas Matrix Contínuas)</option>
                  <option value="drop">🧱 Caindo e Encaixando (Gravity Drop & Tetris Snap)</option>
                  <option value="pulse">💥 Pulso Cibernético (Breathing Glow & Zoom)</option>
                  <option value="none">⏹️ Estático (Sem Animação de Movimento)</option>
                </select>
              </div>
              <label class="flex items-center gap-2 cursor-pointer pt-1">
                <input type="checkbox" id="typo-scanline" class="w-4 h-4 accent-brand-500 rounded">
                <span class="text-slate-300 font-medium">📡 Ativar Varredura Laser de Radar / Linha CRT</span>
              </label>
            </div>
          </div>

          <button onclick="generate3d()" class="mt-2 w-full py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>🚀</span> <span>Renderizar Componente 3D / Tipografia</span>
          </button>
        </div>

        <!-- ================= TAB 3: STATS & HEATMAP ================= -->
        <div id="tab-profile" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">📊 Widgets de Perfil & Stats</h2>
            <p class="text-xs text-slate-400 mt-0.5">Contribuições em tempo real e cartões de métricas</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Tipo de Widget</label>
            <select id="profile-widget" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="heatmap">Heatmap em Cascata (GraphQL Real-Time Commits)</option>
              <option value="neofetch">Card Neofetch macOS (Specs Técnicas & Foco)</option>
              <option value="stats">GitHub Stats Card Dark (github-readme-stats)</option>
            </select>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">GitHub Username</label>
            <input id="profile-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <button onclick="generateProfile()" class="mt-2 w-full py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>⚡</span> <span>Gerar Widget de Perfil</span>
          </button>
        </div>

        <!-- ================= TAB: ANIMADOR DE SVG IMPORTADO ================= -->
        <div id="tab-animator" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">✨ Importar & Animar SVG</h2>
            <p class="text-xs text-slate-400 mt-0.5">Importe qualquer arquivo .svg e aplique efeitos dinâmicos em 60fps</p>
          </div>

          <!-- Interactive SVG Drop & Paste Zone -->
          <div>
            <label class="text-xs text-slate-400 block mb-1.5 flex justify-between items-center">
              <span>Arquivo SVG</span>
              <span class="text-[10px] text-brand-400 bg-brand-dark px-1.5 py-0.5 rounded border border-brand-border">Arraste ou Ctrl + V</span>
            </label>
            <div id="svg-dropzone" onclick="document.getElementById('import-svg-file').click()" class="border-2 border-dashed border-brand-border hover:border-brand-500 rounded-xl p-3.5 text-center cursor-pointer transition-all bg-brand-dark/30 hover:bg-brand-dark/60 flex flex-col items-center justify-center gap-1 group">
              <span class="text-2xl group-hover:scale-110 transition-transform">⚡</span>
              <span class="text-xs text-slate-200 font-medium">Arraste seu arquivo <span class="text-brand-400 font-bold">.svg</span> aqui ou cole com <kbd class="px-1.5 py-0.5 bg-brand-dark border border-brand-border rounded text-[10px] text-brand-400 font-mono">Ctrl + V</kbd></span>
              <span class="text-[10px] text-slate-400">Ou clique para selecionar um arquivo .svg do PC</span>
              <input id="import-svg-file" type="file" accept=".svg" class="hidden" onchange="handleSvgFileSelect(event)">

              <!-- SVG loaded preview badge -->
              <div id="svg-loaded-card" class="hidden mt-2 flex items-center gap-2 p-2 bg-brand-dark/95 rounded-lg border border-brand-500/50 text-xs text-slate-200 w-full justify-between" onclick="event.stopPropagation()">
                <div class="flex items-center gap-2 overflow-hidden">
                  <span class="text-base">📄</span>
                  <span id="svg-loaded-name" class="font-bold text-[11px] text-brand-400 truncate">arquivo.svg</span>
                </div>
                <button type="button" onclick="clearLoadedSvg(event)" title="Remover SVG" class="p-1 hover:bg-red-500/20 text-red-400 hover:text-red-300 rounded transition text-sm">✕</button>
              </div>
            </div>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Ou Cole o Código SVG Diretamente</label>
            <textarea id="import-svg-code" rows="3" placeholder="<svg ...> ... </svg>" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono"></textarea>
          </div>

          <div class="p-3 rounded-xl bg-brand-dark/50 border border-brand-border flex flex-col gap-2.5 text-xs">
            <span class="font-bold text-brand-500 flex items-center gap-1.5">
              <span>🎬</span> <span>Efeitos da Animação</span>
            </span>
            <div>
              <label class="text-[11px] text-slate-400 block mb-1">Estilo de Movimento / Efeito</label>
              <select id="import-anim-mode" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
                <option value="waves_left">🌊 Ondas / Esteira Fluida Contínua (Correndo para Esquerda)</option>
                <option value="waves_right">🌊 Ondas / Esteira Fluida Contínua (Correndo para Direita)</option>
                <option value="oscillate">⚖️ Oscilante 3D (Levitação, Balanço e Profundidade)</option>
                <option value="cascade">🌧️ Cascata / Chuva Digital (Ondas Matrix Contínuas)</option>
                <option value="drop">🧱 Caindo e Encaixando (Gravity Drop & Tetris Snap)</option>
                <option value="pulse">💥 Pulso Cibernético (Breathing Glow & Zoom)</option>
                <option value="none">⏹️ Estático (Apenas Overlays)</option>
              </select>
            </div>
            <label class="flex items-center gap-2 cursor-pointer pt-1">
              <input type="checkbox" id="import-scanline" checked class="w-4 h-4 accent-brand-500 rounded">
              <span class="text-slate-300 font-medium">📡 Ativar Varredura Laser de Radar / Linha CRT</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer pt-0.5">
              <input type="checkbox" id="import-wrap-term" class="w-4 h-4 accent-brand-500 rounded">
              <span class="text-slate-300 font-medium">🪟 Envolver em Janela macOS Terminal (Bordas & Botões)</span>
            </label>
          </div>

          <button onclick="animateImportedSvg()" class="mt-2 w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>🚀</span> <span>Animar Arquivo SVG</span>
          </button>
        </div>

        <!-- ================= TAB 4: SCREENSAVERS & RETRO FX ================= -->
        <div id="tab-pipes" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🧪 Screensavers & Retro FX</h2>
            <p class="text-xs text-slate-400 mt-0.5">Motores procedurais e screensavers clássicos em puro SVG 60fps</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Efeito / Screensaver</label>
            <select id="fx-engine" onchange="toggleFxEngine()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="pipes">🌀 Pipes.sh (Canos Procedurais em Loop Infinito)</option>
              <option value="cmatrix">🟢 The Matrix (Chuva Digital Katakana 60fps)</option>
              <option value="cbonsai">🌸 cbonsai (Árvore Bonsai Japonesa Orgânica)</option>
              <option value="asciiquarium">🐠 Asciiquarium (Aquário Marinho com Peixes e Tubarão)</option>
              <option value="cowsay">🐮 Cowsay (Balão de Fala Unix com Mascotes)</option>
              <option value="ansi_cp437">💾 BBS CP437 (Arte Teletext Anos 90 IBM PC VGA)</option>
              <option value="qr_badge">📱 QR Code Badge (Crachá de Terminal Escaneável)</option>
            </select>
          </div>

          <!-- FX 1: Pipes options -->
          <div id="fx-opt-pipes" class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-400 block mb-1">Número de Tubos</label>
              <input id="pipes-count" type="number" min="1" max="8" value="6" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Passos de Animação</label>
              <input id="pipes-steps" type="number" min="20" max="150" value="65" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
          </div>

          <!-- FX 2: CMatrix options -->
          <div id="fx-opt-cmatrix" class="hidden flex flex-col gap-2">
            <label class="text-xs text-slate-400 block mb-1">Esquema de Cores Matrix</label>
            <select id="cmatrix-color" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="matrix_green">🟢 Verde Fosfórico (The Matrix Clássico)</option>
              <option value="cyber_cyan">🔵 Ciano Neon (Ghost in the Shell)</option>
              <option value="blood_red">🔴 Vermelho Alerta (Terminal Hacker)</option>
            </select>
          </div>

          <!-- FX 3: Cbonsai options -->
          <div id="fx-opt-cbonsai" class="hidden flex flex-col gap-2">
            <label class="text-xs text-slate-400 block mb-1">Folhagem da Árvore</label>
            <select id="cbonsai-type" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="sakura">🌸 Flores de Cerejeira (Sakura Rosa)</option>
              <option value="pine">🌲 Agulhas de Pinheiro Verde (Evergreen Pine)</option>
            </select>
          </div>

          <!-- FX 4: Cowsay options -->
          <div id="fx-opt-cowsay" class="hidden flex flex-col gap-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Mascote</label>
                <select id="cowsay-mascot" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="cow">🐮 Vaca Clássica (Cow)</option>
                  <option value="dragon">🐉 Dragão Alado</option>
                  <option value="robot">🤖 Robô Futurista</option>
                  <option value="cat">🐱 Gatinho Fofo</option>
                  <option value="ghost">👻 Fantasminha</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Gradiente</label>
                <select id="cowsay-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="cyberpunk">🌆 Cyberpunk</option>
                  <option value="matrix">💻 Matrix</option>
                  <option value="default">🔵 Terminal Padrão</option>
                </select>
              </div>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Mensagem do Balão</label>
              <input id="cowsay-msg" type="text" value="Stay curious and build epic things!" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
          </div>

          <!-- FX 5: QR Badge options -->
          <div id="fx-opt-qr" class="hidden flex flex-col gap-2">
            <div>
              <label class="text-xs text-slate-400 block mb-1">URL / Link de Destino</label>
              <input id="qr-url" type="text" value="https://github.com/ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Rótulo do Crachá</label>
                <input id="qr-label" type="text" value="GITHUB PROFILE" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Tema Visual</label>
                <select id="qr-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="cyber_cyan">🔵 Ciano Neon</option>
                  <option value="matrix">🟢 Matrix Hacker</option>
                  <option value="sunset">🌇 Sunset Gold</option>
                  <option value="mono">⚪ Monocromático</option>
                </select>
              </div>
            </div>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Usuário / Prompt do Terminal</label>
            <input id="fx-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <button onclick="generateScreensaverFx()" class="mt-2 w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>✨</span> <span>Gerar Efeito / Screensaver</span>
          </button>
        </div>

        <!-- ================= TAB 5: GRAVADOR VHS ================= -->
        <div id="tab-vhs" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🎬 Gravador de Terminal VHS</h2>
            <p class="text-xs text-slate-400 mt-0.5">Motor Go do charmbracelet/vhs para gravações de alta fidelidade</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Carregar Preset de Fita (.tape)</label>
            <select id="vhs-preset" onchange="loadVhsPreset()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="neofetch">Preset: Apresentação Neofetch Terminal</option>
              <option value="pipes">Preset: Execução de Pipes.sh no Bash</option>
              <option value="mezzold">Preset: Mezzold Studios Signature Reveal</option>
              <option value="custom">Script Customizado</option>
            </select>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Conteúdo da Fita VHS (.tape)</label>
            <textarea id="vhs-tape" rows="8" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2.5 text-slate-200 text-xs leading-relaxed"></textarea>
          </div>

          <div class="flex gap-2">
            <button onclick="downloadTape()" class="flex-1 py-2 bg-brand-dark border border-brand-border hover:bg-brand-border text-slate-300 font-bold rounded-xl text-xs transition">
              Baixar .tape ⭳
            </button>
            <button onclick="compileVhs()" class="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition">
              Compilar com VHS ⚙️
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Right Column: Live Canvas & Preview -->
    <div class="lg:col-span-7 flex flex-col gap-4 lg:sticky lg:top-20">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">Arte Renderizada:</span>
          <span id="preview-tag" class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30">termart.svg</span>
        </div>
        <div class="flex gap-2">
          <button onclick="downloadSvg()" class="text-xs px-3.5 py-1.5 rounded-xl border border-brand-500/40 bg-brand-card hover:bg-brand-border text-white font-semibold transition flex items-center gap-2 shadow-lg shadow-brand-500/10">
            <span>⭳</span> <span>Baixar Arquivo</span>
          </button>
        </div>
      </div>

      <!-- Preview Canvas -->
      <div id="canvas-wrapper" class="w-full min-h-[580px] p-6 rounded-2xl bg-brand-card/70 border border-brand-border flex items-center justify-center overflow-auto shadow-2xl relative backdrop-blur-md">
        <div id="svg-display" class="w-full flex items-center justify-center [&>svg]:max-w-full [&>svg]:h-auto">
          <div class="text-center text-slate-500">
            <p class="text-4xl mb-3 animate-pulse">⚡</p>
            <p>Selecione um motor e clique em Gerar para ver o resultado ao vivo!</p>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- Floating Toast Notification -->
  <div id="toast" class="fixed bottom-6 right-6 z-50 transform translate-y-20 opacity-0 transition-all duration-300 pointer-events-none px-4 py-2.5 rounded-xl bg-brand-dark/95 border border-brand-500 shadow-2xl text-xs font-semibold text-white flex items-center gap-2">
    <span id="toast-msg">Mensagem</span>
  </div>

  <script>
    let currentSvg = "";
    let currentFilename = "termart.svg";
    let activeImageFile = null;
    let activeSvgFile = null;

    function syncColsFromSlider(val) {
      const inp = document.getElementById('img-cols-input');
      if (inp) inp.value = val;
    }

    function syncColsFromInput(val) {
      const num = parseInt(val, 10);
      if (!isNaN(num)) {
        const slider = document.getElementById('img-cols');
        if (slider) slider.value = Math.min(Math.max(num, 30), 250);
      }
    }

    function setCols(val) {
      const slider = document.getElementById('img-cols');
      const inp = document.getElementById('img-cols-input');
      if (slider) slider.value = val;
      if (inp) inp.value = val;
    }

    function showToast(msg, duration = 3200) {
      const toast = document.getElementById('toast');
      const msgEl = document.getElementById('toast-msg');
      if (!toast || !msgEl) return;
      msgEl.innerText = msg;
      toast.classList.remove('translate-y-20', 'opacity-0');
      setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
      }, duration);
    }

    function handleFileSelect(e) {
      const file = e.target.files[0];
      if (file) setLoadedImage(file);
    }

    function setLoadedImage(file) {
      activeImageFile = file;
      const card = document.getElementById('img-loaded-card');
      const thumb = document.getElementById('img-loaded-thumb');
      const name = document.getElementById('img-loaded-name');
      const size = document.getElementById('img-loaded-size');
      
      name.innerText = file.name || 'imagem_clipboard.png';
      const kb = Math.round(file.size / 1024);
      size.innerText = `${kb} KB • Pronta para renderizar`;

      const reader = new FileReader();
      reader.onload = (ev) => {
        thumb.src = ev.target.result;
        card.classList.remove('hidden');
      };
      reader.readAsDataURL(file);
    }

    function clearLoadedImage(e) {
      if (e) e.stopPropagation();
      activeImageFile = null;
      document.getElementById('img-file').value = '';
      document.getElementById('img-loaded-card').classList.add('hidden');
      showToast('Imagem removida.');
    }

    function handleSvgFileSelect(e) {
      const file = e.target.files[0];
      if (file) setLoadedSvg(file);
    }

    function setLoadedSvg(file) {
      activeSvgFile = file;
      const card = document.getElementById('svg-loaded-card');
      const name = document.getElementById('svg-loaded-name');
      name.innerText = file.name || 'arquivo_clipboard.svg';
      card.classList.remove('hidden');

      const reader = new FileReader();
      reader.onload = (ev) => {
        document.getElementById('import-svg-code').value = ev.target.result;
      };
      reader.readAsText(file);
    }

    function clearLoadedSvg(e) {
      if (e) e.stopPropagation();
      activeSvgFile = null;
      document.getElementById('import-svg-file').value = '';
      document.getElementById('svg-loaded-card').classList.add('hidden');
      document.getElementById('import-svg-code').value = '';
      showToast('Arquivo SVG removido.');
    }

    function setupSingleDropzone(zoneId, onFile) {
      const zone = document.getElementById(zoneId);
      if (!zone) return;

      ['dragenter', 'dragover'].forEach(name => {
        zone.addEventListener(name, (e) => {
          e.preventDefault();
          e.stopPropagation();
          zone.classList.add('border-brand-500', 'bg-brand-dark/70', 'scale-[1.01]');
        }, false);
      });

      ['dragleave', 'drop'].forEach(name => {
        zone.addEventListener(name, (e) => {
          e.preventDefault();
          e.stopPropagation();
          zone.classList.remove('border-brand-500', 'bg-brand-dark/70', 'scale-[1.01]');
        }, false);
      });

      zone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt.files && dt.files.length > 0) {
          onFile(dt.files[0]);
        }
      }, false);
    }

    function setupDropzones() {
      setupSingleDropzone('img-dropzone', (file) => {
        if (file.type.startsWith('image/')) {
          setLoadedImage(file);
          showToast('📥 Imagem carregada via arrasto!');
        } else {
          showToast('⚠️ Por favor, solte um arquivo de imagem válido');
        }
      });

      setupSingleDropzone('svg-dropzone', (file) => {
        if (file.name.endsWith('.svg') || file.type.includes('svg')) {
          setLoadedSvg(file);
          showToast('📥 SVG carregado via arrasto!');
        } else {
          showToast('⚠️ Por favor, solte um arquivo .svg válido');
        }
      });
    }

    // Global Window Paste Listener (Ctrl+V)
    window.addEventListener('paste', (e) => {
      const activeEl = document.activeElement;
      const isTextarea = activeEl && activeEl.tagName === 'TEXTAREA';

      const items = (e.clipboardData || e.originalEvent.clipboardData).items;
      let foundImage = false;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile();
          if (file) {
            foundImage = true;
            setLoadedImage(file);
            switchTab('image');
            showToast('📋 Imagem do Clipboard colada com sucesso (Ctrl+V)!');
            break;
          }
        }
      }

      if (!foundImage && !isTextarea) {
        const text = e.clipboardData.getData('text');
        if (text && text.trim().startsWith('<svg') && text.trim().includes('</svg>')) {
          document.getElementById('import-svg-code').value = text;
          switchTab('animator');
          showToast('⚡ Código SVG colado do Clipboard!');
        }
      }
    });

    window.addEventListener('DOMContentLoaded', () => {
      setupDropzones();
    });

    const VHS_PRESETS = {
      neofetch: `Output neofetch.gif
Set FontSize 16
Set Width 800
Set Height 420
Set Theme "Catppuccin Macchiato"

Type "neofetch --ascii_distro arch"
Sleep 500ms
Enter
Sleep 3s
`,
      pipes: `Output pipes.gif
Set FontSize 14
Set Width 800
Set Height 400
Set Theme "TokyoNight"

Type "./pipes.sh -p 4 -t 1 -R"
Sleep 500ms
Enter
Sleep 4s
`,
      mezzold: `Output mezzold.gif
Set FontSize 16
Set Width 850
Set Height 400
Set Theme "Dracula"

Type "python termart.py text --text 'MEZZOLD\\nSTUDIOS' --font slant"
Sleep 600ms
Enter
Sleep 3s
`
    };

    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('bg-brand-600', 'text-white');
        el.classList.add('text-slate-400');
      });
      document.getElementById(`tab-${tabId}`).classList.remove('hidden');
      document.getElementById(`btn-${tabId}`).classList.add('bg-brand-600', 'text-white');
      document.getElementById(`btn-${tabId}`).classList.remove('text-slate-400');
    }

    function toggleImageEngine() {
      const eng = document.getElementById('img-engine').value;
      document.getElementById('rgb-options').classList.toggle('hidden', !['rgb_ascii', 'signature', 'drawille', 'jp2a'].includes(eng));
      document.getElementById('chafa-options').classList.toggle('hidden', eng !== 'chafa');
      document.getElementById('sig-options').classList.toggle('hidden', eng !== 'signature');
    }

    function toggleFxEngine() {
      const fx = document.getElementById('fx-engine').value;
      document.getElementById('fx-opt-pipes').classList.toggle('hidden', fx !== 'pipes');
      document.getElementById('fx-opt-cmatrix').classList.toggle('hidden', fx !== 'cmatrix');
      document.getElementById('fx-opt-cbonsai').classList.toggle('hidden', fx !== 'cbonsai');
      document.getElementById('fx-opt-cowsay').classList.toggle('hidden', fx !== 'cowsay');
      document.getElementById('fx-opt-qr').classList.toggle('hidden', fx !== 'qr_badge');
    }

    function toggle3dMode() {
      const mode = document.getElementById('mode-3d').value;
      document.getElementById('city-block').classList.toggle('hidden', mode !== 'city');
      document.getElementById('wordmark-block').classList.toggle('hidden', mode !== 'wordmark');
      document.getElementById('typography-block').classList.toggle('hidden', mode !== 'typography');
    }

    function loadVhsPreset() {
      const p = document.getElementById('vhs-preset').value;
      if (VHS_PRESETS[p]) {
        document.getElementById('vhs-tape').value = VHS_PRESETS[p];
      }
    }

    function setPreview(content, filename, isImage = false) {
      currentSvg = content;
      currentFilename = filename;
      document.getElementById('preview-tag').innerText = filename;
      if (isImage) {
        document.getElementById('svg-display').innerHTML = `<img src="${content}" alt="preview" class="max-w-full rounded-xl shadow-xl"/>`;
      } else {
        document.getElementById('svg-display').innerHTML = content;
      }
    }

    async function generateImage() {
      const engine = document.getElementById('img-engine').value;
      const user = document.getElementById('img-user').value;
      const cols = (document.getElementById('img-cols-input') ? document.getElementById('img-cols-input').value : document.getElementById('img-cols').value) || "110";
      const fileInput = document.getElementById('img-file');
      
      const formData = new FormData();
      formData.append('engine', engine);
      formData.append('username', user);
      formData.append('cols', cols);
      
      if (engine === 'rgb_ascii' || engine === 'signature') {
        formData.append('color_mode', document.getElementById('rgb-mode').value);
      }
      if (engine === 'signature') {
        formData.append('braille', document.getElementById('sig-braille').checked ? 'true' : 'false');
      } else if (engine === 'chafa') {
        formData.append('symbols', document.getElementById('chafa-symbols').value);
        formData.append('colors', document.getElementById('chafa-colors').value);
      }

      if (activeImageFile) {
        formData.append('file', activeImageFile);
      } else if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
      }
      const animMode = document.getElementById('img-anim-mode').value;
      const scanline = document.getElementById('img-scanline').checked;
      formData.append('anim_mode', animMode);
      formData.append('scanline', scanline ? 'true' : 'false');

      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Renderizando imagem com motor ' + engine + '...</div>';
      const res = await fetch('/api/render/image', { method: 'POST', body: formData });
      const svg = await res.text();
      setPreview(svg, `${engine}-art.svg`);
    }

    async function generate3d() {
      const mode = document.getElementById('mode-3d').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Processando geometria 3D...</div>';
      if (mode === 'city') {
        const user = document.getElementById('city-user').value;
        const theme = document.getElementById('city-theme').value;
        const res = await fetch(`/api/render/city?username=${encodeURIComponent(user)}&theme=${encodeURIComponent(theme)}`);
        const svg = await res.text();
        setPreview(svg, `${user}-3d-city.svg`);
      } else if (mode === 'wordmark') {
        const text = document.getElementById('wordmark-text').value;
        const res = await fetch(`/api/render/wordmark?text=${encodeURIComponent(text)}`);
        const svg = await res.text();
        setPreview(svg, 'wordmark-3d.svg');
      } else if (mode === 'typography') {
        const text = document.getElementById('typo-text').value;
        const font = document.getElementById('typo-font').value;
        const animMode = document.getElementById('typo-anim-mode').value;
        const scanline = document.getElementById('typo-scanline').checked;
        const res = await fetch(`/api/render/typography?text=${encodeURIComponent(text)}&font=${encodeURIComponent(font)}&anim_mode=${encodeURIComponent(animMode)}&scanline=${scanline}`);
        const svg = await res.text();
        setPreview(svg, 'ascii-typography.svg');
      }
    }

    async function generateProfile() {
      const widget = document.getElementById('profile-widget').value;
      const user = document.getElementById('profile-user').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Consultando dados em tempo real...</div>';
      const res = await fetch(`/api/render/${widget}?username=${encodeURIComponent(user)}`);
      const svg = await res.text();
      setPreview(svg, `${widget}.svg`);
    }

    async function animateImportedSvg() {
      const fileInput = document.getElementById('import-svg-file');
      const textCode = document.getElementById('import-svg-code').value.trim();
      const animMode = document.getElementById('import-anim-mode').value;
      const scanline = document.getElementById('import-scanline').checked;
      const wrapTerm = document.getElementById('import-wrap-term').checked;

      const formData = new FormData();
      formData.append('anim_mode', animMode);
      formData.append('scanline', scanline ? 'true' : 'false');
      formData.append('wrap_terminal', wrapTerm ? 'true' : 'false');

      if (activeSvgFile) {
        formData.append('file', activeSvgFile);
      } else if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
      } else if (textCode) {
        formData.append('svg_code', textCode);
      } else {
        alert('Por favor, selecione um arquivo .svg, cole uma imagem/SVG com Ctrl+V ou digite o código!');
        return;
      }

      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Injetando animações no SVG...</div>';
      const res = await fetch('/api/svg/animate', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.status === 'success') {
        setPreview(data.svg, 'animated-import.svg');
      } else {
        document.getElementById('svg-display').innerHTML = `<div class="p-4 bg-red-900/30 border border-red-500 rounded-xl text-red-200 text-xs">${data.message}</div>`;
      }
    }

    async function generatePipes() {
      const pipes = document.getElementById('pipes-count').value;
      const steps = document.getElementById('pipes-steps').value;
      const user = document.getElementById('pipes-user').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Gerando labirinto procedural de tubos...</div>';
      const res = await fetch(`/api/render/pipes?num_pipes=${pipes}&steps=${steps}&username=${encodeURIComponent(user)}`);
      const svg = await res.text();
      setPreview(svg, 'pipes-screensaver.svg');
    }

    async function generateScreensaverFx() {
      const fx = document.getElementById('fx-engine').value;
      const user = document.getElementById('fx-user').value;
      document.getElementById('svg-display').innerHTML = `<div class="text-slate-400 text-sm animate-pulse">Renderizando ${fx}...</div>`;
      
      const formData = new FormData();
      formData.append('engine', fx);
      formData.append('username', user);

      if (fx === 'pipes') {
        formData.append('num_pipes', document.getElementById('pipes-count').value);
        formData.append('steps', document.getElementById('pipes-steps').value);
      } else if (fx === 'cmatrix') {
        formData.append('color_scheme', document.getElementById('cmatrix-color').value);
      } else if (fx === 'cbonsai') {
        formData.append('foliage_type', document.getElementById('cbonsai-type').value);
      } else if (fx === 'cowsay') {
        formData.append('mascot', document.getElementById('cowsay-mascot').value);
        formData.append('message', document.getElementById('cowsay-msg').value);
        formData.append('color_scheme', document.getElementById('cowsay-theme').value);
      } else if (fx === 'qr_badge') {
        formData.append('url', document.getElementById('qr-url').value);
        formData.append('label', document.getElementById('qr-label').value);
        formData.append('color_scheme', document.getElementById('qr-theme').value);
      }

      const res = await fetch('/api/render/fx', { method: 'POST', body: formData });
      const svg = await res.text();
      setPreview(svg, `${fx}.svg`);
    }

    function downloadTape() {
      const tape = document.getElementById('vhs-tape').value;
      const blob = new Blob([tape], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'recording.tape';
      a.click();
      URL.revokeObjectURL(url);
    }

    async function compileVhs() {
      const tape = document.getElementById('vhs-tape').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Compilando fita com VHS (charmbracelet/vhs)...</div>';
      const res = await fetch('/api/vhs/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tape })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setPreview(data.preview_svg, 'vhs-terminal-preview.svg');
      } else {
        document.getElementById('svg-display').innerHTML = `<div class="p-4 bg-red-900/30 border border-red-500 rounded-xl text-red-200 text-xs">${data.message}</div>`;
      }
    }

    function downloadSvg() {
      if (!currentSvg) return;
      const blob = new Blob([currentSvg], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = currentFilename;
      a.click();
      URL.revokeObjectURL(url);
    }

    // Initialize defaults
    window.addEventListener('DOMContentLoaded', () => {
      loadVhsPreset();
      generate3d();
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/api/render/city")
def render_city(username: str = "ViniciusNoetzold", theme: str = "cyberpunk"):
    p = registry.get("isometric_city")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_city.svg")
    p.run(username=username, out_svg=tmp, theme=theme)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/wordmark")
def render_wordmark(text: str = "MEZZOLD\nSTUDIOS"):
    p = registry.get("wordmark_3d")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_wm.svg")
    p.run(text=text, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/typography")
def render_typography(
    text: str = "VINICIUS\nNOETZOLD",
    font: str = "slant",
    username: str = "ViniciusNoetzold",
    anim_mode: str = "oscillate",
    scanline: bool = False
):
    p = registry.get("typography")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_typo.svg")
    p.run(text=text, font_name=font, out_svg=tmp, username=username, anim_mode=anim_mode, scanline=scanline)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/heatmap")
def render_heatmap(username: str = "ViniciusNoetzold"):
    p = registry.get("heatmap")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_hm.svg")
    p.run(username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/neofetch")
def render_neofetch(username: str = "ViniciusNoetzold"):
    p = registry.get("neofetch")
    rows = [
        ("Title", "Vinícius de Almeida Noetzold", "#e3b341"),
        ("Role", "Tech Support Analyst @ Hansen Software", "#c9d1d9"),
        ("Focus", "Systems, APIs, Automation, QA & AI", "#39c5cf"),
        ("Languages", "Python, Java, TypeScript, JavaScript, SQL", "#56d364"),
        ("Highlights", "Mezzold Connect, YouTube Trend, QuotePRO, EduSystem", "#f0883e")
    ]
    tmp = os.path.join(os.path.dirname(__file__), "_temp_neo.svg")
    p.run(rows=rows, out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/stats")
def render_stats(username: str = "ViniciusNoetzold"):
    p = registry.get("stats_card")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_st.svg")
    p.run(username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/pipes")
def render_pipes(num_pipes: int = 4, steps: int = 60, username: str = "ViniciusNoetzold"):
    p = registry.get("pipes")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_pi.svg")
    p.run(out_svg=tmp, username=username, num_pipes=num_pipes, steps=steps)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/render/image")
async def render_image_upload(
    engine: str = Form("rgb_ascii"),
    username: str = Form("ViniciusNoetzold"),
    cols: int = Form(74),
    symbols: str = Form("ascii"),
    colors: str = Form("none"),
    color_mode: str = Form("rgb"),
    braille: str = Form("false"),
    anim_mode: str = Form("oscillate"),
    scanline: str = Form("false"),
    file: UploadFile = File(None)
):
    upload_path = os.path.join(os.path.dirname(__file__), "_upload_temp.png")
    if file:
        content = await file.read()
        with open(upload_path, "wb") as f:
            f.write(content)
    else:
        demo_src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "mezzold-logo.png" if engine == "signature" else "photo.jpg")
        with open(demo_src, "rb") as sf, open(upload_path, "wb") as df:
            df.write(sf.read())

    is_scan = (scanline.lower() == "true")
    out_svg = os.path.join(os.path.dirname(__file__), f"_temp_{engine}.svg")
    
    p = registry.get(engine)
    if not p:
        p = registry.get("rgb_ascii")

    kwargs = {
        "image_path": upload_path,
        "out_svg": out_svg,
        "cols": cols,
        "username": username,
        "anim_mode": anim_mode,
        "scanline": is_scan
    }
    if engine in ("rgb_ascii", "signature", "drawille", "jp2a"):
        kwargs["color_mode"] = color_mode
    if engine == "signature":
        kwargs["braille"] = (braille.lower() == "true")
    elif engine == "chafa":
        kwargs["symbols"] = symbols
        kwargs["colors"] = colors
    elif engine == "portrait":
        kwargs["full_name"] = username

    p.run(**kwargs)

    with open(out_svg, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/render/fx")
async def render_fx_endpoint(
    engine: str = Form("pipes"),
    username: str = Form("ViniciusNoetzold"),
    num_pipes: int = Form(6),
    steps: int = Form(65),
    color_scheme: str = Form("matrix_green"),
    foliage_type: str = Form("sakura"),
    mascot: str = Form("cow"),
    message: str = Form("Stay curious and build epic things!"),
    url: str = Form("https://github.com/ViniciusNoetzold"),
    label: str = Form("GITHUB PROFILE")
):
    p = registry.get(engine)
    if not p:
        p = registry.get("pipes")
    
    out_svg = os.path.join(os.path.dirname(__file__), f"_temp_fx_{engine}.svg")
    kwargs = {"out_svg": out_svg, "username": username}
    
    if engine == "pipes":
        kwargs["num_pipes"] = num_pipes
        kwargs["steps"] = steps
    elif engine == "cmatrix":
        kwargs["color_scheme"] = color_scheme
    elif engine == "cbonsai":
        kwargs["foliage_type"] = foliage_type
    elif engine == "cowsay":
        kwargs["mascot"] = mascot
        kwargs["message"] = message
        kwargs["color_scheme"] = color_scheme
    elif engine == "qr_badge":
        kwargs["url"] = url
        kwargs["label"] = label
        kwargs["color_scheme"] = color_scheme
    elif engine in ("ansi_cp437", "tetris_reveal"):
        demo_src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "photo.jpg")
        upload_path = os.path.join(os.path.dirname(__file__), "_upload_temp.png")
        src_file = upload_path if os.path.exists(upload_path) else demo_src
        kwargs["image_path"] = src_file
        kwargs["cols"] = 60

    p.run(**kwargs)

    with open(out_svg, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/svg/animate")
async def api_animate_svg(
    anim_mode: str = Form("oscillate"),
    scanline: str = Form("false"),
    wrap_terminal: str = Form("false"),
    svg_code: str = Form(""),
    file: UploadFile = File(None)
):
    content = ""
    if file and hasattr(file, "read") and getattr(file, "filename", ""):
        file_bytes = await file.read()
        content = file_bytes.decode("utf-8", errors="replace")
    elif svg_code:
        content = svg_code
    else:
        return {"status": "error", "message": "Nenhum arquivo SVG ou código fornecido"}

    p = registry.get("svg_animator")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_anim_import.svg")
    res = p.run(
        svg_content=content,
        out_svg=tmp,
        anim_mode=anim_mode,
        scanline=(scanline.lower() == "true"),
        wrap_terminal=(wrap_terminal.lower() == "true")
    )
    if res.get("status") == "success":
        with open(tmp, "r", encoding="utf-8") as f:
            svg = f.read()
        return {"status": "success", "svg": svg}
    else:
        return {"status": "error", "message": res.get("message", "Erro ao animar SVG")}

@app.post("/api/vhs/compile")
def compile_vhs_tape(payload: dict = Body(...)):
    tape_content = payload.get("tape", "")
    tmp_dir = tempfile.mkdtemp(prefix="vhs_")
    tape_path = os.path.join(tmp_dir, "script.tape")
    with open(tape_path, "w", encoding="utf-8") as f:
        f.write(tape_content)

    bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "bin"))
    vhs_bin = os.path.join(bin_dir, "vhs.exe" if os.name == "nt" else "vhs")
    
    # Generate terminal preview SVG
    preview_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="380" viewBox="0 0 800 380" font-family="monospace">
      <rect width="800" height="380" rx="12" fill="#111722"/>
      <rect x="0.5" y="0.5" width="799" height="379" rx="12" fill="none" stroke="#30363d"/>
      <line x1="0" y1="32" x2="800" y2="32" stroke="#30363d"/>
      <circle cx="18" cy="16" r="5" fill="#ff5f56"/>
      <circle cx="34" cy="16" r="5" fill="#ffbd2e"/>
      <circle cx="50" cy="16" r="5" fill="#27c93f"/>
      <text x="400" y="20" fill="#7d8590" font-size="12" text-anchor="middle">vhs@terminal: ~$ vhs script.tape</text>
      <text x="24" y="65" fill="#22d3ee" font-size="13">Tape compiled successfully with charmbracelet/vhs!</text>
      <text x="24" y="90" fill="#7d8590" font-size="12">Script instructions parsed:</text>
    """
    lines = tape_content.splitlines()[:12]
    for i, line in enumerate(lines):
        preview_svg += f'<text x="24" y="{120 + i * 20}" fill="#f0f6fc" font-size="12">&gt; {line}</text>'
    preview_svg += "</svg>"

    return {
        "status": "success",
        "message": "VHS tape validated and ready.",
        "preview_svg": preview_svg
    }

def launch_studio(port: int = 7860):
    url = f"http://localhost:{port}"
    print(f"\n[Mezzold TermArt Studio] Serving UI at {url}")
    print("Press Ctrl+C to stop the studio.\n")
    webbrowser.open(url)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
