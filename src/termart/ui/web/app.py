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
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
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
        <span>🎬</span> <span>Gravador VHS & AGG</span>
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

          <!-- Image Mode Switcher: Motor Único vs Comparar Vários Motores -->
          <div class="flex p-1 bg-brand-dark rounded-xl border border-brand-border text-xs">
            <button type="button" id="img-btn-single" onclick="setImageSelectionMode('single')" class="flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5">
              <span>🖼️</span> <span>Motor Único</span>
            </button>
            <button type="button" id="img-btn-multi" onclick="setImageSelectionMode('multi')" class="flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5">
              <span>📑</span> <span>Comparar Motores (Grade)</span>
            </button>
          </div>

          <!-- Single Engine Dropdown -->
          <div id="img-engine-single-wrap">
            <label class="text-xs text-slate-400 block mb-1">Motor de Renderização</label>
            <select id="img-engine" onchange="toggleImageEngine()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <optgroup label="Motores de Alta Resolução">
                <option value="rgb_ascii">TrueColor RGB ASCII (Cores 24-bit Reais da Foto)</option>
                <option value="chafa">Chafa Studio - Sub-pixel Graphics de Alta Resolução</option>
                <option value="signature">Logo / Assinatura em Caligrafia (ASCII Puro / Braille)</option>
                <option value="portrait">Retrato Terminal (Braille 2x4 com Digitação)</option>
              </optgroup>
              <optgroup label="Estilos Visuais & Filtros Especiais">
                <option value="drawille">Drawille Subpixel (Matriz Braille 2x4 com 8x Resolução)</option>
                <option value="dither">Retro Dithering (Atkinson Mac 1984, Floyd-Steinberg, Bayer)</option>
                <option value="jp2a">jp2a Classic (Rampas Unix & Invert Contrast)</option>
                <option value="halftone">Halftone Press (Retícula de Impressão, Jornais & HQs)</option>
                <option value="edge_art">Edge Art (Contornos Sobel Mangá & Blueprint)</option>
                <option value="glitch">Glitch Cyberpunk (Aberração Cromática VHS & Corrupção)</option>
                <option value="pixel_mosaic">Pixel Mosaic (Sprites 8-bit Arcade PICO-8 & C64)</option>
                <option value="palette_swap">Palette Swap (Dracula, Catppuccin, Nord, TokyoNight)</option>
                <option value="rainbow_wave">Rainbow Wave (Espectro Arco-Íris Contínuo)</option>
              </optgroup>
            </select>
          </div>

          <!-- Multi Engine Selector Wrap -->
          <div id="img-engine-multi-wrap" class="hidden flex flex-col gap-2 p-3 rounded-xl bg-brand-dark/50 border border-brand-border text-xs">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-200 flex items-center gap-1">
                <span>🎨</span> <span>Selecione Motores para Comparar</span>
              </span>
              <span id="img-batch-count" class="text-[11px] text-brand-400 font-bold bg-brand-dark px-2 py-0.5 rounded border border-brand-border font-mono">4 selecionados</span>
            </div>

            <!-- Quick Presets -->
            <div class="flex flex-wrap gap-1">
              <button type="button" onclick="selectImgPreset('recommended')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-brand-400 font-bold">⚡ Top 4 Recomendados</button>
              <button type="button" onclick="selectImgPreset('all')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-slate-300 font-medium">🎨 Todos os 10</button>
              <button type="button" onclick="selectImgPreset('clear')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-red-500 text-[10px] text-red-400">✕ Limpar</button>
            </div>

            <!-- Engine Checkboxes Grid -->
            <div class="grid grid-cols-2 gap-1.5 p-1 border border-brand-border/60 rounded-lg bg-black/20">
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="chafa" checked class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Chafa (Braille 256)</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="rgb_ascii" checked class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>RGB TrueColor</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="drawille" checked class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Drawille (Subpixel)</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="dither" checked class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Dither (Floyd)</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="jp2a" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>jp2a (ASCII B&W)</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="halftone" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Halftone (Jornal)</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="edge_art" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Edge Art (Mangá)</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="glitch" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Glitch (VHS Cyber)</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="pixel_mosaic" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Pixel Mosaic</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="rainbow_wave" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Rainbow Wave</span>
              </label>
            </div>
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

          <label class="flex items-center gap-2 cursor-pointer p-2 bg-brand-dark/40 rounded-lg border border-brand-border/60 text-xs select-none">
            <input type="checkbox" id="img-disable-anim" class="w-4 h-4 accent-brand-500 rounded" onchange="syncGlobalAnimToggle('img')">
            <span class="text-slate-200 font-medium">⏸️ Desativar todas as animações (Modo Leve / Economia de CPU)</span>
          </label>

          <button id="img-submit-btn" onclick="executeImageRender()" class="mt-2 w-full py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>✨</span> <span id="img-submit-label">Renderizar Imagem com Motor Selecionado</span>
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
            <!-- Typography Mode Switcher: Fonte Única vs Comparar Várias Fontes -->
            <div class="flex p-1 bg-brand-dark rounded-xl border border-brand-border text-xs">
              <button type="button" id="typo-btn-single" onclick="setTypoSelectionMode('single')" class="flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5">
                <span>🔤</span> <span>Fonte Única</span>
              </button>
              <button type="button" id="typo-btn-multi" onclick="setTypoSelectionMode('multi')" class="flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5">
                <span>📑</span> <span>Comparar Fontes (Grade)</span>
              </button>
            </div>

            <!-- Single Font Dropdown Wrap -->
            <div id="typo-font-single-wrap">
              <label class="text-xs text-slate-400 block mb-1">Fonte FIGlet (30+ Estilos Curados)</label>
              <select id="typo-font" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <optgroup label="👾 3D & Isométricas">
                  <option value="isometric1">Isometric 1 (3D Cúbico Sólido)</option>
                  <option value="isometric2">Isometric 2 (3D Negrito Isométrico)</option>
                  <option value="isometric3">Isometric 3 (3D Cubos Sombreados)</option>
                  <option value="larry3d">Larry 3D (Perspectiva com Sombra)</option>
                  <option value="banner3-D">Banner 3D (Letreiro Billboard)</option>
                  <option value="shadow">Shadow (3D Sombra Projetada)</option>
                </optgroup>
                <optgroup label="⚡ Cyberpunk & Sci-Fi">
                  <option value="slant" selected>Slant (Cyberpunk Futurista Clássico)</option>
                  <option value="cyberlarge">CyberLarge (Terminal Futurista Largo)</option>
                  <option value="cybermedium">CyberMedium (HUD Tático Sci-Fi)</option>
                  <option value="speed">Speed (Alta Velocidade Itálico)</option>
                  <option value="starwars">Star Wars (Clássico Sci-Fi Galáctico)</option>
                  <option value="cosmic">Cosmic (Espaço Profundo Interstelar)</option>
                </optgroup>
                <optgroup label="🔥 Heavy, Gothic & Metal">
                  <option value="doom">Doom (Heavy Id Software Original)</option>
                  <option value="bloody">Bloody (Gótico Sangrento / Horror)</option>
                  <option value="poison">Poison (Punk & Metal com Bordas Afiadas)</option>
                  <option value="gothic">Gothic (Gótico Medieval Autêntico)</option>
                  <option value="colossal">Colossal (Blocos Monolíticos Pesados)</option>
                  <option value="sub-zero">Sub-Zero (Lâminas Congeladas Sharp)</option>
                  <option value="epic">Epic (Cinemático Dramático)</option>
                </optgroup>
                <optgroup label="🎨 Graffiti, Cartoons & Estilizados">
                  <option value="graffiti">Graffiti (Street Art Spray Tag)</option>
                  <option value="ogre">Ogre (Desenho Animado Graffiti Chunky)</option>
                  <option value="alligator">Alligator (Ondulado Escamas de Réptil)</option>
                  <option value="bulbhead">Bulbhead (Bolha Arredondada Retrô)</option>
                  <option value="chunky">Chunky (Arcade Retrô Chunky)</option>
                  <option value="broadway">Broadway (Letreiro Broadway Neon Retrô)</option>
                </optgroup>
                <optgroup label="💻 Clássicas, BBS & Minimalistas">
                  <option value="standard">Standard (Clássica Unix FIGlet 1990)</option>
                  <option value="big">Big (Letras Grandes em Linhas)</option>
                  <option value="small">Small (Compacta Multi-Linha)</option>
                  <option value="mini">Mini (Minimalista Ultra Compacto)</option>
                  <option value="ghost">Ghost (Holográfico Wireframe Oco)</option>
                  <option value="digital">Digital (Display LCD 7 Segmentos)</option>
                  <option value="thin">Thin (Elegante Traço Fino)</option>
                </optgroup>
              </select>
            </div>

            <!-- Multi Font Checkbox Grid Wrap -->
            <div id="typo-font-multi-wrap" class="hidden flex flex-col gap-2 p-3 rounded-xl bg-brand-dark/50 border border-brand-border text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-200 flex items-center gap-1">
                  <span>🔤</span> <span>Selecione Fontes para Comparar</span>
                </span>
                <span id="typo-batch-count" class="text-[11px] text-brand-400 font-bold bg-brand-dark px-2 py-0.5 rounded border border-brand-border font-mono">6 selecionadas</span>
              </div>

              <!-- Category Presets -->
              <div class="flex flex-wrap gap-1">
                <button type="button" onclick="selectTypoPreset('popular')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-brand-400 font-bold">⚡ Populares</button>
                <button type="button" onclick="selectTypoPreset('3d')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-slate-300 font-medium">👾 3D</button>
                <button type="button" onclick="selectTypoPreset('cyber')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-slate-300 font-medium">⚡ Cyber</button>
                <button type="button" onclick="selectTypoPreset('gothic')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-slate-300 font-medium">🔥 Heavy</button>
                <button type="button" onclick="selectTypoPreset('graffiti')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-slate-300 font-medium">🎨 Graffiti</button>
                <button type="button" onclick="selectTypoPreset('all')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-slate-300 font-medium">💻 Todas (32)</button>
                <button type="button" onclick="selectTypoPreset('clear')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-red-500 text-[10px] text-red-400">✕ Limpar</button>
              </div>

              <!-- Fonts Checkbox Grid -->
              <div class="max-h-48 overflow-y-auto grid grid-cols-2 gap-1.5 p-1.5 border border-brand-border/60 rounded-lg bg-black/30">
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="slant" checked class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Slant</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="isometric1" checked class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Isometric 1</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="doom" checked class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Doom</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="bloody" checked class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Bloody</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="graffiti" checked class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Graffiti</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="starwars" checked class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Star Wars</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="isometric2" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Isometric 2</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="isometric3" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Isometric 3</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="larry3d" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Larry 3D</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="banner3-D" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Banner 3D</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="shadow" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Shadow 3D</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="cyberlarge" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>CyberLarge</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="cybermedium" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>CyberMedium</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="speed" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Speed</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="cosmic" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Cosmic</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="poison" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Poison</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="gothic" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Gothic</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="colossal" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Colossal</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="sub-zero" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Sub-Zero</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="epic" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Epic</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="ogre" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Ogre</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="alligator" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Alligator</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="bulbhead" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Bulbhead</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="chunky" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Chunky</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="broadway" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Broadway</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="standard" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Standard</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="big" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Big</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="small" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Small</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="mini" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Mini</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="ghost" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Ghost</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="digital" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Digital</span>
                </label>
                <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                  <input type="checkbox" name="typo_batch_font" value="thin" class="accent-brand-500" onchange="updateTypoBatchCounter()">
                  <span>Thin</span>
                </label>
              </div>
            </div>

            <div>
              <label class="text-xs text-slate-400 block mb-1">Paleta de Cores & Gradiente</label>
              <select id="typo-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="cyberpunk" selected>🌆 Cyberpunk Neon (Ciano → Rosa Choque → Roxo)</option>
                <option value="matrix">💻 Matrix Hacker (Verde Fosfórico com Esmeralda)</option>
                <option value="sunset">🌇 Sunset Gold (Dourado → Âmbar → Carmesim)</option>
                <option value="dracula">🧛 Dracula Vampire (Lilás → Rosa Neon → Ciano)</option>
                <option value="nord">❄️ Nord Frost (Gelo Glacial & Azul Ártico)</option>
                <option value="gold">👑 Ouro Real (Champagne & Ouro Nobre)</option>
                <option value="blood">🩸 Crimson Blood (Carmesim & Vermelho Rubi)</option>
                <option value="ocean">🌊 Ocean Blue (Azul Turquesa & Safira)</option>
                <option value="rainbow">🌈 Lolcat Rainbow (Onda de Arco-Íris Senoidal)</option>
                <option value="two_tone">🌗 Two-Tone (Azul GitHub & Branco Puro)</option>
                <option value="monochrome">⚪ Branco Minimalista (Apple Crisp White)</option>
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

          <label class="flex items-center gap-2 cursor-pointer p-2 bg-brand-dark/40 rounded-lg border border-brand-border/60 text-xs select-none">
            <input type="checkbox" id="typo-disable-anim" class="w-4 h-4 accent-brand-500 rounded" onchange="syncGlobalAnimToggle('typo')">
            <span class="text-slate-200 font-medium">⏸️ Desativar todas as animações (Modo Leve / Economia de CPU)</span>
          </label>

          <button id="typo-submit-btn" onclick="execute3dRender()" class="mt-2 w-full py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>🚀</span> <span id="typo-submit-label">Renderizar Componente 3D / Tipografia</span>
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
            <select id="profile-widget" onchange="onProfileWidgetChange()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="pokemon">🎮 Card RPG Pokémon (16 Espécies, Shiny & Níveis)</option>
              <option value="weather">⛅ Previsão do Tempo (wttr.in ASCII Radar & Cidades)</option>
              <option value="clock">⏰ TTY Digital Clock (LED Neon & Formato 12h/24h)</option>
              <option value="chess">♟️ Partida de Xadrez (Animação até o Xeque-Mate!)</option>
              <option value="heatmap">Heatmap em Cascata (GraphQL Real-Time Commits)</option>
              <option value="neofetch">Card Neofetch macOS (Specs Técnicas & Foco)</option>
              <option value="stats">GitHub Stats Card Dark (github-readme-stats)</option>
              <option value="tree">📁 Architecture File Tree (Estrutura de Pastas)</option>
              <option value="fortune">🥠 Fortune Cookie (Filosofia Hacker & Zen)</option>
            </select>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">GitHub Username / Treinador</label>
            <input id="profile-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <!-- POKEMON OPTIONS -->
          <div id="profile-opt-pokemon" class="flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-brand-accent flex items-center gap-1.5">
              <span>🎮</span> <span>Opções do Pokémon</span>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Escolha o Pokémon</label>
              <select id="pk-select" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="gengar">Gengar (#0094 - Fantasma/Veneno)</option>
                <option value="pikachu">Pikachu (#0025 - Elétrico)</option>
                <option value="charizard">Charizard (#0006 - Fogo/Voador)</option>
                <option value="blastoise">Blastoise (#0009 - Água)</option>
                <option value="venusaur">Venusaur (#0003 - Planta/Veneno)</option>
                <option value="mewtwo">Mewtwo (#0150 - Psíquico)</option>
                <option value="rayquaza">Rayquaza (#0384 - Dragão/Voador)</option>
                <option value="umbreon">Umbreon (#0197 - Sombrio)</option>
                <option value="lucario">Lucario (#0448 - Lutador/Aço)</option>
                <option value="dragonite">Dragonite (#0149 - Dragão/Voador)</option>
                <option value="snorlax">Snorlax (#0143 - Normal)</option>
                <option value="eevee">Eevee (#0133 - Normal)</option>
                <option value="gyarados">Gyarados (#0130 - Água/Voador)</option>
                <option value="alakazam">Alakazam (#0065 - Psíquico)</option>
                <option value="lugia">Lugia (#0249 - Psíquico/Voador)</option>
                <option value="garchomp">Garchomp (#0445 - Dragão/Terrestre)</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Nível (Level)</label>
                <select id="pk-level" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                  <option value="100">Lv. 100 (Max)</option>
                  <option value="75">Lv. 75</option>
                  <option value="50">Lv. 50</option>
                  <option value="25">Lv. 25</option>
                  <option value="5">Lv. 5 (Inicial)</option>
                </select>
              </div>
              <div class="flex items-end pb-1">
                <label class="flex items-center gap-2 text-xs text-amber-300 font-semibold cursor-pointer">
                  <input id="pk-shiny" type="checkbox" class="rounded accent-brand-500">
                  <span>✨ Modo Shiny</span>
                </label>
              </div>
            </div>
          </div>

          <!-- WEATHER OPTIONS -->
          <div id="profile-opt-weather" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
              <span>⛅</span> <span>Localização & Clima</span>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Cidade / Localização</label>
              <input id="weather-city" type="text" value="Curitiba, Brazil" placeholder="Ex: Curitiba, Tokyo, London" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <div class="flex flex-wrap gap-1 mt-1.5">
                <button type="button" onclick="setWeatherCity('Curitiba, Brazil')" class="text-[10px] px-2 py-0.5 bg-brand-surface hover:bg-brand-border text-slate-300 rounded">Curitiba</button>
                <button type="button" onclick="setWeatherCity('São Paulo, Brazil')" class="text-[10px] px-2 py-0.5 bg-brand-surface hover:bg-brand-border text-slate-300 rounded">São Paulo</button>
                <button type="button" onclick="setWeatherCity('Rio de Janeiro, Brazil')" class="text-[10px] px-2 py-0.5 bg-brand-surface hover:bg-brand-border text-slate-300 rounded">Rio</button>
                <button type="button" onclick="setWeatherCity('Tokyo, Japan')" class="text-[10px] px-2 py-0.5 bg-brand-surface hover:bg-brand-border text-slate-300 rounded">Tóquio</button>
                <button type="button" onclick="setWeatherCity('New York, USA')" class="text-[10px] px-2 py-0.5 bg-brand-surface hover:bg-brand-border text-slate-300 rounded">Nova York</button>
                <button type="button" onclick="setWeatherCity('London, UK')" class="text-[10px] px-2 py-0.5 bg-brand-surface hover:bg-brand-border text-slate-300 rounded">Londres</button>
                <button type="button" onclick="setWeatherCity('Paris, France')" class="text-[10px] px-2 py-0.5 bg-brand-surface hover:bg-brand-border text-slate-300 rounded">Paris</button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Condição do Tempo</label>
                <select id="weather-condition" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                  <option value="sunny">☀️ Ensolarado / Céu Limpo</option>
                  <option value="rainy">🌧️ Chuva Cyberpunk</option>
                  <option value="thunder">⛈️ Tempestade Elétrica</option>
                  <option value="snow">❄️ Neve Suave</option>
                  <option value="cloudy">⛅ Parcialmente Nublado</option>
                  <option value="night">🌙 Noite Estrelada & Lua</option>
                  <option value="windy">💨 Ventania & Vórtice</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Unidade</label>
                <select id="weather-unit" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                  <option value="C">°C (Celsius)</option>
                  <option value="F">°F (Fahrenheit)</option>
                </select>
              </div>
            </div>
          </div>

          <!-- CLOCK OPTIONS -->
          <div id="profile-opt-clock" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <span>⏰</span> <span>Cores & Formato do Relógio</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Cor do Display LED</label>
                <select id="clock-color" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                  <option value="phosphor">🟢 Verde Matrix (Phosphor)</option>
                  <option value="cyan">🔵 Ciano Neon (Cyberpunk)</option>
                  <option value="amber">🟠 Âmbar Vintage (Plasma)</option>
                  <option value="ruby">🔴 Vermelho Rubi (Alarme)</option>
                  <option value="purple">🟣 Roxo Synthwave</option>
                  <option value="ice">🧊 Azul Ártico</option>
                  <option value="gold">🟡 Ouro Imperial</option>
                  <option value="white">⚪ Branco Puro</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Formato de Hora</label>
                <select id="clock-format" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                  <option value="24h">24 Horas (14:35:00)</option>
                  <option value="12h">12 Horas (02:35:00 PM)</option>
                </select>
              </div>
            </div>
          </div>

          <!-- CHESS OPTIONS -->
          <div id="profile-opt-chess" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
              <span>♟️</span> <span>Partida & Xeque-Mate</span>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Partida Histórica</label>
              <select id="chess-match" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="opera">🎭 Paul Morphy (Opera Game 1858) - 17 lances, Sacrifício de Dama & Mate!</option>
                <option value="scholar">⚡ Mate do Pastor (4 Lances) - Ataque veloz em f7</option>
                <option value="fools">⚡ Mate do Louco (2 Lances) - O mate mais rápido da história</option>
                <option value="immortal">👑 The Immortal Game 1851 (Anderssen) - Triplo Sacrifício</option>
                <option value="kasparov">🤖 Kasparov vs Deep Blue 1996 - Ruptura tática decisiva</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Velocidade</label>
                <select id="chess-speed" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                  <option value="1.0">1x (Normal)</option>
                  <option value="1.5">1.5x (Rápido)</option>
                  <option value="2.0">2x (Turbo)</option>
                  <option value="0.7">0.7x (Cadenciado)</option>
                </select>
              </div>
              <div class="flex items-end pb-1">
                <label class="flex items-center gap-2 text-xs text-slate-200 font-semibold cursor-pointer">
                  <input id="chess-animated" type="checkbox" checked class="rounded accent-brand-500">
                  <span>▶ Animar até o Mate</span>
                </label>
              </div>
            </div>
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
              <option value="donut_3d">🍩 Donut 3D (Andy Sloane Torus Giratório 3D)</option>
              <option value="cava">📊 CAVA Visualizer (Equalizador de Áudio Rítmico)</option>
              <option value="doom_fire">🔥 Doom / PSX Fire 1992 (Fogo em Chamas Vivas)</option>
              <option value="synthwave_grid">🌆 Synthwave 80s (Horizonte Outrun com Sol Neon)</option>
              <option value="game_of_life">🧬 Game of Life (Autômato Celular de Conway)</option>
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

        <!-- ================= TAB 5: GRAVADOR VHS & AGG ================= -->
        <div id="tab-vhs" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2 flex justify-between items-start">
            <div>
              <h2 class="font-bold text-white text-base flex items-center gap-2">🎬 Gravador de Terminal Studio</h2>
              <p class="text-xs text-slate-400 mt-0.5">Automação com VHS (Go) & Renderização ultrarrápida com AGG (Rust)</p>
            </div>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono font-bold">
              vhs + agg ativos
            </span>
          </div>

          <!-- Engine Switcher: VHS Tape vs Asciinema AGG -->
          <div class="flex p-1 bg-brand-dark rounded-xl border border-brand-border text-xs">
            <button id="vhs-subtab-btn-tape" onclick="switchVhsSubTab('tape')" class="flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5">
              <span>📼</span> <span>Fita VHS (.tape)</span>
            </button>
            <button id="vhs-subtab-btn-agg" onclick="switchVhsSubTab('agg')" class="flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5">
              <span>🦀</span> <span>Asciinema AGG (.cast)</span>
            </button>
          </div>

          <!-- SUB-TAB 1: VHS TAPE STUDIO -->
          <div id="vhs-view-tape" class="flex flex-col gap-3.5">
            <!-- Preset Selector -->
            <div>
              <label class="text-xs text-slate-400 block mb-1">Carregar Preset de Demonstração (.tape)</label>
              <select id="vhs-preset" onchange="loadVhsPreset()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="showcase">⚡ Preset: Showcase Geral Mezzold TermArt (CLI Tour)</option>
                <option value="bonsai">🌸 Preset: cbonsai Árvore Japonesa Crescendo ao Vivo</option>
                <option value="matrix">🟢 Preset: The Matrix Cascata de Código Katakana</option>
                <option value="donut">🍩 Preset: Donut 3D Rotativo em C (Andy Sloane)</option>
                <option value="neofetch">💻 Preset: Neofetch & Git Stats Terminal Card</option>
                <option value="pokemon">🎮 Preset: Pokémon RPG Colorscript (Gengar Lv.100)</option>
                <option value="coffee">☕ Preset: Dev Coffee Typing Routine</option>
                <option value="custom">🛠️ Script Customizado do Usuário</option>
              </select>
            </div>

            <!-- Visual Setting Bar (Synced into tape) -->
            <div class="p-2.5 rounded-xl bg-brand-dark/50 border border-brand-border flex flex-col gap-2 text-xs">
              <span class="text-[11px] font-bold text-slate-300">Configuração Rápida da Fita</span>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-[10px] text-slate-400 block mb-0.5">Tema do Terminal</label>
                  <select id="vhs-cfg-theme" onchange="applyVhsConfig()" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
                    <option value="Catppuccin Macchiato" selected>Catppuccin Macchiato</option>
                    <option value="Dracula">Dracula</option>
                    <option value="Nord">Nord</option>
                    <option value="TokyoNight">TokyoNight</option>
                    <option value="Monokai">Monokai</option>
                    <option value="Cyberpunk">Cyberpunk Neon</option>
                  </select>
                </div>
                <div>
                  <label class="text-[10px] text-slate-400 block mb-0.5">Formato de Saída</label>
                  <select id="vhs-cfg-ext" onchange="applyVhsConfig()" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
                    <option value=".gif" selected>Animação GIF (.gif)</option>
                    <option value=".mp4">Vídeo MP4 (.mp4)</option>
                    <option value=".webm">Vídeo WebM (.webm)</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-[10px] text-slate-400 block mb-0.5">Tamanho da Fonte</label>
                  <select id="vhs-cfg-fontsize" onchange="applyVhsConfig()" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
                    <option value="14">14 px (Compacto)</option>
                    <option value="16" selected>16 px (Equilibrado)</option>
                    <option value="18">18 px (Grande)</option>
                    <option value="20">20 px (Extra Grande)</option>
                  </select>
                </div>
                <div>
                  <label class="text-[10px] text-slate-400 block mb-0.5">Resolução do Terminal</label>
                  <select id="vhs-cfg-res" onchange="applyVhsConfig()" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
                    <option value="800 420" selected>800 x 420 (Padrão)</option>
                    <option value="850 450">850 x 450 (Médio)</option>
                    <option value="1000 500">1000 x 500 (Widescreen)</option>
                    <option value="1280 720">1280 x 720 (HD 720p)</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Quick Snippets Inserter Chips -->
            <div>
              <label class="text-[11px] text-slate-400 block mb-1">Inserir Comandos Rápidos na Fita</label>
              <div class="flex flex-wrap gap-1.5">
                <button type="button" onclick="insertVhsSnippet('type')" class="px-2 py-1 rounded-lg bg-brand-dark border border-brand-border hover:border-brand-500 text-[11px] text-slate-300 font-mono transition">⌨️ +Type</button>
                <button type="button" onclick="insertVhsSnippet('sleep')" class="px-2 py-1 rounded-lg bg-brand-dark border border-brand-border hover:border-brand-500 text-[11px] text-slate-300 font-mono transition">⏱️ +Sleep 500ms</button>
                <button type="button" onclick="insertVhsSnippet('enter')" class="px-2 py-1 rounded-lg bg-brand-dark border border-brand-border hover:border-brand-500 text-[11px] text-slate-300 font-mono transition">↵ +Enter</button>
                <button type="button" onclick="insertVhsSnippet('clear')" class="px-2 py-1 rounded-lg bg-brand-dark border border-brand-border hover:border-brand-500 text-[11px] text-slate-300 font-mono transition">🧹 +Clear</button>
                <button type="button" onclick="insertVhsSnippet('ctrl_c')" class="px-2 py-1 rounded-lg bg-brand-dark border border-brand-border hover:border-brand-500 text-[11px] text-slate-300 font-mono transition">🛑 +Ctrl+C</button>
                <button type="button" onclick="insertVhsSnippet('backspace')" class="px-2 py-1 rounded-lg bg-brand-dark border border-brand-border hover:border-brand-500 text-[11px] text-slate-300 font-mono transition">⌫ +Backspace</button>
              </div>
            </div>

            <!-- Tape Codearea -->
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="text-xs text-slate-400">Editor da Fita VHS (.tape)</label>
                <span id="vhs-lines-count" class="text-[10px] text-slate-500 font-mono">10 linhas</span>
              </div>
              <textarea id="vhs-tape" rows="8" oninput="updateTapeLines()" class="w-full bg-brand-dark border border-brand-border focus:border-brand-500 rounded-lg p-2.5 text-slate-200 text-xs leading-relaxed font-mono resize-y"></textarea>
            </div>

            <!-- Action Buttons -->
            <div class="grid grid-cols-2 gap-2">
              <button onclick="simulateVhs()" class="py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5 shadow-lg">
                <span>▶️</span> <span>Simular Execução (SVG)</span>
              </button>
              <button onclick="compileVhs()" class="py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5 shadow-lg">
                <span>⚙️</span> <span>Compilar GIF Real (VHS)</span>
              </button>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <button onclick="downloadTape()" class="py-2 bg-brand-dark border border-brand-border hover:bg-brand-border text-slate-300 font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5">
                <span>⭳</span> <span>Baixar .tape</span>
              </button>
              <button onclick="copyTapeScript()" class="py-2 bg-brand-dark border border-brand-border hover:bg-brand-border text-slate-300 font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5">
                <span>📋</span> <span>Copiar Script</span>
              </button>
            </div>
          </div>

          <!-- SUB-TAB 2: ASCIINEMA AGG STUDIO -->
          <div id="vhs-view-agg" class="hidden flex flex-col gap-3.5">
            <div class="p-3 rounded-xl bg-brand-dark/50 border border-brand-border flex flex-col gap-2 text-xs">
              <div class="flex items-center gap-2 text-slate-300 font-bold">
                <span>🦀</span> <span>asciinema/agg (Rust Compiler)</span>
              </div>
              <p class="text-[11px] text-slate-400">Renderiza arquivos de gravação terminal <code class="text-brand-400 font-mono">.cast</code> em GIFs otimizados com anti-aliasing e aceleração nativa.</p>
            </div>

            <div>
              <label class="text-xs text-slate-400 block mb-1">Arquivo de Entrada (.cast)</label>
              <select id="agg-cast-select" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="demo">Terminal Session Demo (Mezzold TermArt Tour)</option>
              </select>
            </div>

            <div class="grid grid-cols-3 gap-2">
              <div>
                <label class="text-[10px] text-slate-400 block mb-1">Tema</label>
                <select id="agg-theme" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
                  <option value="dracula" selected>Dracula</option>
                  <option value="monokai">Monokai</option>
                  <option value="nord">Nord</option>
                  <option value="solarized-dark">Solarized Dark</option>
                  <option value="gruvbox-dark">Gruvbox Dark</option>
                  <option value="kanagawa">Kanagawa</option>
                </select>
              </div>
              <div>
                <label class="text-[10px] text-slate-400 block mb-1">Velocidade</label>
                <select id="agg-speed" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
                  <option value="1.0" selected>1.0x (Normal)</option>
                  <option value="1.5">1.5x (Rápido)</option>
                  <option value="2.0">2.0x (Turbo)</option>
                </select>
              </div>
              <div>
                <label class="text-[10px] text-slate-400 block mb-1">Fonte (px)</label>
                <select id="agg-fontsize" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
                  <option value="14" selected>14 px</option>
                  <option value="16">16 px</option>
                  <option value="18">18 px</option>
                </select>
              </div>
            </div>

            <button onclick="compileAgg()" class="mt-2 w-full py-2.5 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2 text-xs">
              <span>🦀</span> <span>Renderizar GIF com AGG (Rust Engine)</span>
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Right Column: Live Canvas & Preview -->
    <div class="lg:col-span-7 flex flex-col gap-4 lg:sticky lg:top-20">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">Arte Renderizada:</span>
          <span id="preview-tag" class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30">termart.svg</span>
          <span id="preview-count-badge" class="hidden text-xs px-2.5 py-0.5 rounded-full bg-brand-500/20 text-brand-400 font-semibold border border-brand-500/30">0 itens</span>
        </div>
        <div class="flex items-center gap-2">
          <button id="btn-global-anim" onclick="toggleGlobalAnimations()" class="text-xs px-3 py-1.5 rounded-xl border border-brand-border bg-brand-card hover:bg-brand-border text-slate-300 font-semibold transition flex items-center gap-1.5 shadow" title="Ativar ou desativar todas as animações para economia de CPU">
            <span id="global-anim-icon">✨</span> <span id="global-anim-label">Animações: ON</span>
          </button>
          <button id="btn-download-zip" onclick="downloadAllAsZip()" class="hidden text-xs px-3.5 py-1.5 rounded-xl border border-purple-500/40 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 font-semibold transition flex items-center gap-1.5 shadow-lg shadow-purple-500/10">
            <span>📦</span> <span>Baixar Todas (.ZIP)</span>
          </button>
          <button id="btn-download-single" onclick="downloadSvg()" class="text-xs px-3.5 py-1.5 rounded-xl border border-brand-500/40 bg-brand-card hover:bg-brand-border text-white font-semibold transition flex items-center gap-2 shadow-lg shadow-brand-500/10">
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
      showcase: `Output mezzold_showcase.gif
Set FontSize 16
Set Width 850
Set Height 440
Set Theme "Catppuccin Macchiato"

Type "python termart.py text --text 'MEZZOLD' --font slant --theme cyberpunk"
Sleep 600ms
Enter
Sleep 3s
`,
      bonsai: `Output bonsai_growth.gif
Set FontSize 14
Set Width 800
Set Height 420
Set Theme "TokyoNight"

Type "python termart.py cbonsai --type sakura --out sakura.svg"
Sleep 500ms
Enter
Sleep 4s
`,
      matrix: `Output matrix_rain.gif
Set FontSize 14
Set Width 800
Set Height 420
Set Theme "Cyberpunk"

Type "python termart.py cmatrix --color matrix_green --cols 55"
Sleep 500ms
Enter
Sleep 4s
`,
      donut: `Output donut_3d.gif
Set FontSize 14
Set Width 800
Set Height 420
Set Theme "Dracula"

Type "python termart.py donut --theme cyberpunk"
Sleep 500ms
Enter
Sleep 4s
`,
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
      pokemon: `Output pokemon_battle.gif
Set FontSize 16
Set Width 800
Set Height 420
Set Theme "Dracula"

Type "python termart.py pokemon --pokemon gengar"
Sleep 500ms
Enter
Sleep 3s
`,
      coffee: `Output dev_coffee.gif
Set FontSize 16
Set Width 800
Set Height 420
Set Theme "Nord"

Type "echo '☕ Brewing artisanal dark roast...'"
Sleep 600ms
Enter
Sleep 1s
Type "git status && git commit -m 'feat: clean terminal aesthetic'"
Sleep 800ms
Enter
Sleep 3s
`,
      custom: `Output custom_run.gif
Set FontSize 16
Set Width 800
Set Height 420
Set Theme "Catppuccin Macchiato"

Type "python termart.py --help"
Sleep 500ms
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
        if (typeof updateTapeLines === 'function') updateTapeLines();
      }
    }

    let currentBatchResults = [];
    let globalAnimationsDisabled = false;
    let currentImageSelectionMode = 'single';
    let currentTypoSelectionMode = 'single';

    function setPreview(content, filename, isImage = false) {
      currentSvg = content;
      currentFilename = filename;
      currentBatchResults = [{ id: 'single', title: filename, filename: filename, svg: content }];
      document.getElementById('preview-tag').innerText = filename;
      document.getElementById('preview-count-badge').classList.add('hidden');
      document.getElementById('btn-download-zip').classList.add('hidden');
      if (isImage) {
        document.getElementById('svg-display').innerHTML = `<img src="${content}" alt="preview" class="max-w-full rounded-xl shadow-xl"/>`;
      } else {
        document.getElementById('svg-display').innerHTML = content;
      }
    }

    function toggleGlobalAnimations() {
      globalAnimationsDisabled = !globalAnimationsDisabled;
      const icon = document.getElementById('global-anim-icon');
      const label = document.getElementById('global-anim-label');
      const chkImg = document.getElementById('img-disable-anim');
      const chkTypo = document.getElementById('typo-disable-anim');

      if (chkImg) chkImg.checked = globalAnimationsDisabled;
      if (chkTypo) chkTypo.checked = globalAnimationsDisabled;

      if (globalAnimationsDisabled) {
        if (icon) icon.innerText = '⏸️';
        if (label) label.innerText = 'Animações: OFF';
        showToast('⏸️ Modo Leve: animações desativadas para economizar CPU!');
      } else {
        if (icon) icon.innerText = '✨';
        if (label) label.innerText = 'Animações: ON';
        showToast('✨ Animações ativadas em 60 FPS!');
      }
    }

    function syncGlobalAnimToggle(src) {
      let isChecked = false;
      if (src === 'img') isChecked = document.getElementById('img-disable-anim').checked;
      else if (src === 'typo') isChecked = document.getElementById('typo-disable-anim').checked;

      globalAnimationsDisabled = isChecked;
      const icon = document.getElementById('global-anim-icon');
      const label = document.getElementById('global-anim-label');
      const chkImg = document.getElementById('img-disable-anim');
      const chkTypo = document.getElementById('typo-disable-anim');

      if (chkImg) chkImg.checked = isChecked;
      if (chkTypo) chkTypo.checked = isChecked;

      if (isChecked) {
        if (icon) icon.innerText = '⏸️';
        if (label) label.innerText = 'Animações: OFF';
      } else {
        if (icon) icon.innerText = '✨';
        if (label) label.innerText = 'Animações: ON';
      }
    }

    function renderBatchResultsGrid(title, results) {
      currentBatchResults = results;
      if (!results || results.length === 0) {
        document.getElementById('svg-display').innerHTML = '<div class="text-slate-500 text-sm">Nenhum resultado gerado.</div>';
        return;
      }

      document.getElementById('preview-tag').innerText = `${results.length} itens gerados`;
      const badge = document.getElementById('preview-count-badge');
      badge.innerText = `${results.length} blocos`;
      badge.classList.remove('hidden');

      document.getElementById('btn-download-zip').classList.remove('hidden');

      currentSvg = results[0].svg;
      currentFilename = results[0].filename;

      let html = `<div class="w-full flex flex-col gap-4">`;
      html += `<div class="text-xs text-slate-400 flex items-center justify-between border-b border-brand-border/60 pb-2">`;
      html += `<span><strong>${title}</strong> &bull; Escolha o que mais gostou e baixe diretamente!</span>`;
      html += `<span class="text-brand-400 font-bold font-mono">${results.length} resultados comparados</span>`;
      html += `</div>`;
      
      html += `<div class="grid grid-cols-1 xl:grid-cols-2 gap-4 w-full">`;
      results.forEach((item, idx) => {
        html += `
          <div class="rounded-xl border border-brand-border bg-brand-dark/90 hover:border-brand-500/80 transition-all p-3 flex flex-col gap-2.5 shadow-xl group">
            <div class="flex items-center justify-between border-b border-brand-border/60 pb-2">
              <div class="flex items-center gap-2 overflow-hidden">
                <span class="font-bold text-white text-xs truncate">${item.title}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-400 font-mono font-semibold">${item.tag || 'Arte'}</span>
              </div>
              <div class="flex items-center gap-1.5 flex-shrink-0">
                <button onclick="copySingleBatchSvg(${idx})" class="p-1 px-2 text-slate-400 hover:text-white rounded bg-brand-card border border-brand-border text-[11px] transition" title="Copiar código SVG">
                  📋 Copiar
                </button>
                <button onclick="downloadSingleBatchSvg(${idx})" class="px-2.5 py-1 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition shadow">
                  <span>⭳</span> <span>Baixar Este</span>
                </button>
              </div>
            </div>
            <div class="w-full flex items-center justify-center overflow-x-auto bg-[#090d14] rounded-lg p-2 min-h-[160px] max-h-[420px] overflow-y-auto [&>svg]:max-w-full [&>svg]:h-auto">
              ${item.svg}
            </div>
          </div>
        `;
      });
      html += `</div></div>`;

      document.getElementById('svg-display').innerHTML = html;
      showToast(`🎉 ${results.length} variações renderizadas na grade!`);
    }

    function downloadSingleBatchSvg(idx) {
      const item = currentBatchResults[idx];
      if (!item) return;
      const blob = new Blob([item.svg], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = item.filename;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`⭳ Baixando ${item.filename}!`);
    }

    function copySingleBatchSvg(idx) {
      const item = currentBatchResults[idx];
      if (!item) return;
      navigator.clipboard.writeText(item.svg).then(() => {
        showToast(`📋 Código SVG de "${item.title}" copiado!`);
      });
    }

    async function downloadAllAsZip() {
      if (!currentBatchResults || currentBatchResults.length === 0) return;
      showToast('📦 Empacotando ' + currentBatchResults.length + ' arquivos em .ZIP...');
      if (typeof JSZip === 'undefined') {
        alert('Biblioteca JSZip carregando... Tente novamente em alguns segundos.');
        return;
      }
      try {
        const zip = new JSZip();
        currentBatchResults.forEach((item, idx) => {
          const name = item.filename || `arte-${idx+1}.svg`;
          zip.file(name, item.svg);
        });
        const blob = await zip.generateAsync({ type: 'blob' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'termart-comparativo-pacote.zip';
        a.click();
        URL.revokeObjectURL(url);
        showToast('🎉 Arquivo ZIP baixado com sucesso!');
      } catch (err) {
        showToast('Erro ao criar ZIP: ' + err.message);
      }
    }

    // --- Image Multi-Engine Selection Logic ---
    function setImageSelectionMode(mode) {
      currentImageSelectionMode = mode;
      const isMulti = (mode === 'multi');
      document.getElementById('img-btn-single').className = isMulti 
        ? "flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5"
        : "flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5";
      document.getElementById('img-btn-multi').className = isMulti 
        ? "flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5"
        : "flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5";

      document.getElementById('img-engine-single-wrap').classList.toggle('hidden', isMulti);
      document.getElementById('img-engine-multi-wrap').classList.toggle('hidden', !isMulti);

      updateImgBatchCounter();
    }

    const IMG_PRESETS = {
      recommended: ['chafa', 'rgb_ascii', 'drawille', 'dither'],
      all: ['chafa', 'rgb_ascii', 'drawille', 'dither', 'jp2a', 'halftone', 'edge_art', 'glitch', 'pixel_mosaic', 'rainbow_wave']
    };

    function selectImgPreset(type) {
      const checkboxes = document.querySelectorAll('input[name="img_batch_eng"]');
      if (type === 'clear') {
        checkboxes.forEach(cb => cb.checked = false);
      } else {
        const allowed = new Set(IMG_PRESETS[type] || []);
        checkboxes.forEach(cb => {
          cb.checked = allowed.has(cb.value);
        });
      }
      updateImgBatchCounter();
    }

    function updateImgBatchCounter() {
      const selected = document.querySelectorAll('input[name="img_batch_eng"]:checked');
      const count = selected.length;
      const countEl = document.getElementById('img-batch-count');
      if (countEl) countEl.innerText = `${count} selecionados`;

      const submitLabel = document.getElementById('img-submit-label');
      if (submitLabel) {
        if (currentImageSelectionMode === 'multi') {
          submitLabel.innerText = `Comparar ${count} Motores na Grade`;
        } else {
          submitLabel.innerText = 'Renderizar Imagem com Motor Selecionado';
        }
      }
    }

    async function executeImageRender() {
      if (currentImageSelectionMode === 'multi') {
        await generateImageBatch();
      } else {
        await generateImage();
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
      const disableAnim = globalAnimationsDisabled || document.getElementById('img-disable-anim').checked;

      formData.append('anim_mode', disableAnim ? 'none' : animMode);
      formData.append('scanline', (scanline && !disableAnim) ? 'true' : 'false');

      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Renderizando imagem com motor ' + engine + '...</div>';
      const res = await fetch('/api/render/image', { method: 'POST', body: formData });
      const svg = await res.text();
      setPreview(svg, `${engine}-art.svg`);
    }

    async function generateImageBatch() {
      const selected = Array.from(document.querySelectorAll('input[name="img_batch_eng"]:checked')).map(cb => cb.value);
      if (selected.length === 0) {
        showToast('⚠️ Selecione ao menos 1 motor de imagem!');
        return;
      }
      const user = document.getElementById('img-user').value;
      const cols = (document.getElementById('img-cols-input') ? document.getElementById('img-cols-input').value : document.getElementById('img-cols').value) || "110";
      const fileInput = document.getElementById('img-file');
      const animMode = document.getElementById('img-anim-mode').value;
      const scanline = document.getElementById('img-scanline').checked;
      const disableAnim = globalAnimationsDisabled || document.getElementById('img-disable-anim').checked;

      const formData = new FormData();
      formData.append('engines', selected.join(','));
      formData.append('username', user);
      formData.append('cols', cols);
      formData.append('color_mode', document.getElementById('rgb-mode').value);
      formData.append('anim_mode', animMode);
      formData.append('scanline', scanline ? 'true' : 'false');
      formData.append('disable_anim', disableAnim ? 'true' : 'false');

      if (activeImageFile) {
        formData.append('file', activeImageFile);
      } else if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
      }

      document.getElementById('svg-display').innerHTML = `<div class="text-slate-400 text-sm animate-pulse">Renderizando imagem através de ${selected.length} motores simultaneamente...</div>`;

      const res = await fetch('/api/render/image_batch', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.status === 'success') {
        renderBatchResultsGrid("Comparativo de Motores de Imagem", data.results);
      } else {
        document.getElementById('svg-display').innerHTML = `<div class="p-4 bg-red-900/30 border border-red-500 rounded-xl text-red-200 text-xs">${data.message || 'Erro na renderização'}</div>`;
      }
    }

    // --- Typography Multi-Font Selection Logic ---
    function setTypoSelectionMode(mode) {
      currentTypoSelectionMode = mode;
      const isMulti = (mode === 'multi');
      document.getElementById('typo-btn-single').className = isMulti 
        ? "flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5"
        : "flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5";
      document.getElementById('typo-btn-multi').className = isMulti 
        ? "flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5"
        : "flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5";

      document.getElementById('typo-font-single-wrap').classList.toggle('hidden', isMulti);
      document.getElementById('typo-font-multi-wrap').classList.toggle('hidden', !isMulti);

      updateTypoBatchCounter();
    }

    const TYPO_PRESETS = {
      popular: ['slant', 'isometric1', 'doom', 'bloody', 'graffiti', 'starwars'],
      '3d': ['isometric1', 'isometric2', 'isometric3', 'larry3d', 'banner3-D', 'shadow'],
      cyber: ['slant', 'cyberlarge', 'cybermedium', 'speed', 'starwars', 'cosmic'],
      gothic: ['doom', 'bloody', 'poison', 'gothic', 'colossal', 'sub-zero', 'epic'],
      graffiti: ['graffiti', 'ogre', 'alligator', 'bulbhead', 'chunky', 'broadway'],
      all: ['slant', 'isometric1', 'isometric2', 'isometric3', 'larry3d', 'banner3-D', 'shadow', 'cyberlarge', 'cybermedium', 'speed', 'starwars', 'cosmic', 'doom', 'bloody', 'poison', 'gothic', 'colossal', 'sub-zero', 'epic', 'graffiti', 'ogre', 'alligator', 'bulbhead', 'chunky', 'broadway', 'standard', 'big', 'small', 'mini', 'ghost', 'digital', 'thin']
    };

    function selectTypoPreset(cat) {
      const checkboxes = document.querySelectorAll('input[name="typo_batch_font"]');
      if (cat === 'clear') {
        checkboxes.forEach(cb => cb.checked = false);
      } else {
        const allowed = new Set(TYPO_PRESETS[cat] || []);
        checkboxes.forEach(cb => {
          cb.checked = allowed.has(cb.value);
        });
      }
      updateTypoBatchCounter();
    }

    function updateTypoBatchCounter() {
      const selected = document.querySelectorAll('input[name="typo_batch_font"]:checked');
      const count = selected.length;
      const countEl = document.getElementById('typo-batch-count');
      if (countEl) countEl.innerText = `${count} selecionadas`;

      const submitLabel = document.getElementById('typo-submit-label');
      if (submitLabel) {
        if (currentTypoSelectionMode === 'multi') {
          submitLabel.innerText = `Comparar ${count} Fontes na Grade`;
        } else {
          submitLabel.innerText = 'Renderizar Componente 3D / Tipografia';
        }
      }
    }

    async function execute3dRender() {
      const mode = document.getElementById('mode-3d').value;
      if (mode === 'typography' && currentTypoSelectionMode === 'multi') {
        await generateTypoBatch();
      } else {
        await generate3d();
      }
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
        const theme = document.getElementById('typo-theme').value;
        const animMode = document.getElementById('typo-anim-mode').value;
        const scanline = document.getElementById('typo-scanline').checked;
        const disableAnim = globalAnimationsDisabled || document.getElementById('typo-disable-anim').checked;
        const res = await fetch(`/api/render/typography?text=${encodeURIComponent(text)}&font=${encodeURIComponent(font)}&theme=${encodeURIComponent(theme)}&anim_mode=${encodeURIComponent(disableAnim ? 'none' : animMode)}&scanline=${(scanline && !disableAnim)}`);
        const svg = await res.text();
        setPreview(svg, 'ascii-typography.svg');
      }
    }

    async function generateTypoBatch() {
      const selected = Array.from(document.querySelectorAll('input[name="typo_batch_font"]:checked')).map(cb => cb.value);
      if (selected.length === 0) {
        showToast('⚠️ Selecione ao menos 1 fonte FIGlet!');
        return;
      }
      const text = document.getElementById('typo-text').value;
      const theme = document.getElementById('typo-theme').value;
      const animMode = document.getElementById('typo-anim-mode').value;
      const scanline = document.getElementById('typo-scanline').checked;
      const disableAnim = globalAnimationsDisabled || document.getElementById('typo-disable-anim').checked;

      document.getElementById('svg-display').innerHTML = `<div class="text-slate-400 text-sm animate-pulse">Renderizando ${selected.length} fontes FIGlet simultaneamente...</div>`;

      const res = await fetch('/api/render/typography_batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          fonts: selected,
          theme,
          anim_mode: animMode,
          scanline,
          disable_anim: disableAnim
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        renderBatchResultsGrid("Comparativo de Tipografias ASCII Slant & FIGlet", data.results);
      } else {
        document.getElementById('svg-display').innerHTML = `<div class="p-4 bg-red-900/30 border border-red-500 rounded-xl text-red-200 text-xs">${data.message || 'Erro na renderização'}</div>`;
      }
    }

    function onProfileWidgetChange() {
      const w = document.getElementById('profile-widget').value;
      const optPk = document.getElementById('profile-opt-pokemon');
      const optWe = document.getElementById('profile-opt-weather');
      const optCl = document.getElementById('profile-opt-clock');
      const optCh = document.getElementById('profile-opt-chess');

      if (optPk) optPk.classList.toggle('hidden', w !== 'pokemon');
      if (optWe) optWe.classList.toggle('hidden', w !== 'weather');
      if (optCl) optCl.classList.toggle('hidden', w !== 'clock');
      if (optCh) optCh.classList.toggle('hidden', w !== 'chess');
    }

    function setWeatherCity(c) {
      const el = document.getElementById('weather-city');
      if (el) el.value = c;
    }

    async function generateProfile() {
      const widget = document.getElementById('profile-widget').value;
      const user = document.getElementById('profile-user').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Consultando dados em tempo real...</div>';

      let url = `/api/render/${widget}?username=${encodeURIComponent(user)}`;

      if (widget === 'pokemon') {
        const pk = document.getElementById('pk-select') ? document.getElementById('pk-select').value : 'gengar';
        const shiny = document.getElementById('pk-shiny') ? document.getElementById('pk-shiny').checked : false;
        const level = document.getElementById('pk-level') ? document.getElementById('pk-level').value : 100;
        url += `&pokemon=${encodeURIComponent(pk)}&shiny=${shiny}&level=${encodeURIComponent(level)}`;
      } else if (widget === 'weather') {
        const city = document.getElementById('weather-city') ? document.getElementById('weather-city').value : 'Curitiba, Brazil';
        const cond = document.getElementById('weather-condition') ? document.getElementById('weather-condition').value : 'sunny';
        const unit = document.getElementById('weather-unit') ? document.getElementById('weather-unit').value : 'C';
        url += `&city=${encodeURIComponent(city)}&condition=${encodeURIComponent(cond)}&unit=${encodeURIComponent(unit)}`;
      } else if (widget === 'clock') {
        const col = document.getElementById('clock-color') ? document.getElementById('clock-color').value : 'phosphor';
        const fmt = document.getElementById('clock-format') ? document.getElementById('clock-format').value : '24h';
        url += `&color=${encodeURIComponent(col)}&format_mode=${encodeURIComponent(fmt)}`;
      } else if (widget === 'chess') {
        const match = document.getElementById('chess-match') ? document.getElementById('chess-match').value : 'opera';
        const anim = globalAnimationsDisabled ? false : (document.getElementById('chess-animated') ? document.getElementById('chess-animated').checked : true);
        const speed = document.getElementById('chess-speed') ? document.getElementById('chess-speed').value : 1.0;
        url += `&match=${encodeURIComponent(match)}&animated=${anim}&speed=${encodeURIComponent(speed)}`;
      }

      const res = await fetch(url);
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

    function switchVhsSubTab(subTab) {
      const isTape = (subTab === 'tape');
      document.getElementById('vhs-view-tape').classList.toggle('hidden', !isTape);
      document.getElementById('vhs-view-agg').classList.toggle('hidden', isTape);

      const btnTape = document.getElementById('vhs-subtab-btn-tape');
      const btnAgg = document.getElementById('vhs-subtab-btn-agg');

      if (isTape) {
        btnTape.className = "flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5";
        btnAgg.className = "flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5";
      } else {
        btnAgg.className = "flex-1 py-1.5 rounded-lg font-bold bg-brand-600 text-white transition flex items-center justify-center gap-1.5";
        btnTape.className = "flex-1 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition flex items-center justify-center gap-1.5";
      }
    }

    function insertVhsSnippet(snippet) {
      const area = document.getElementById('vhs-tape');
      let textToInsert = "";
      if (snippet === 'type') textToInsert = 'Type "python termart.py pipes"\n';
      else if (snippet === 'sleep') textToInsert = 'Sleep 500ms\n';
      else if (snippet === 'enter') textToInsert = 'Enter\n';
      else if (snippet === 'clear') textToInsert = 'Hide\nType "clear"\nEnter\nShow\n';
      else if (snippet === 'ctrl_c') textToInsert = 'Ctrl+C\n';
      else if (snippet === 'backspace') textToInsert = 'Backspace 5\n';

      area.value += (area.value.endsWith('\n') ? '' : '\n') + textToInsert;
      updateTapeLines();
      showToast(`Comando inserido: ${snippet}`);
    }

    function applyVhsConfig() {
      const theme = document.getElementById('vhs-cfg-theme').value;
      const ext = document.getElementById('vhs-cfg-ext').value;
      const fs = document.getElementById('vhs-cfg-fontsize').value;
      const [w, h] = document.getElementById('vhs-cfg-res').value.split(' ');

      let val = document.getElementById('vhs-tape').value;
      
      // Update Output
      val = val.replace(/^Output\s+\S+/m, `Output recording${ext}`);
      // Update Set Theme
      val = val.replace(/^Set\s+Theme\s+".*"/m, `Set Theme "${theme}"`);
      // Update Set FontSize
      val = val.replace(/^Set\s+FontSize\s+\d+/m, `Set FontSize ${fs}`);
      // Update Set Width
      val = val.replace(/^Set\s+Width\s+\d+/m, `Set Width ${w}`);
      // Update Set Height
      val = val.replace(/^Set\s+Height\s+\d+/m, `Set Height ${h}`);

      document.getElementById('vhs-tape').value = val;
      updateTapeLines();
      showToast('⚡ Configurações aplicadas na Fita!');
    }

    function updateTapeLines() {
      const tape = document.getElementById('vhs-tape').value;
      const count = tape.split('\n').filter(l => l.trim().length > 0).length;
      const el = document.getElementById('vhs-lines-count');
      if (el) el.innerText = `${count} instruções`;
    }

    function copyTapeScript() {
      const tape = document.getElementById('vhs-tape').value;
      navigator.clipboard.writeText(tape).then(() => {
        showToast('📋 Script .tape copiado para a Área de Transferência!');
      });
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

    async function simulateVhs() {
      const tape = document.getElementById('vhs-tape').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Simulando execução do terminal em 60fps...</div>';
      const res = await fetch('/api/vhs/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tape, compile_real: false })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setPreview(data.preview_svg, 'vhs-session-sim.svg');
        showToast('▶️ Simulação de terminal renderizada em 60 FPS!');
      } else {
        document.getElementById('svg-display').innerHTML = `<div class="p-4 bg-red-900/30 border border-red-500 rounded-xl text-red-200 text-xs">${data.message}</div>`;
      }
    }

    async function compileVhs() {
      const tape = document.getElementById('vhs-tape').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Invocando charmbracelet/vhs nativo para gravação...</div>';
      const res = await fetch('/api/vhs/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tape, compile_real: true })
      });
      const data = await res.json();
      if (data.status === 'success') {
        if (data.gif_data) {
          setPreview(data.gif_data, 'vhs-recording.gif', true);
          showToast('🎉 GIF compilado com sucesso pelo VHS Engine!');
        } else {
          setPreview(data.preview_svg, 'vhs-session-sim.svg');
          showToast('▶️ Simulação SVG interativa pronta!');
        }
      } else {
        document.getElementById('svg-display').innerHTML = `<div class="p-4 bg-red-900/30 border border-red-500 rounded-xl text-red-200 text-xs">${data.message}</div>`;
      }
    }

    async function compileAgg() {
      const theme = document.getElementById('agg-theme').value;
      const speed = document.getElementById('agg-speed').value;
      const fontSize = document.getElementById('agg-fontsize').value;

      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Compilando .cast com asciinema/agg (Rust Engine)...</div>';
      const res = await fetch('/api/agg/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme, speed, font_size: fontSize })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setPreview(data.gif_data, data.filename, true);
        showToast('🦀 GIF compilado em alta velocidade pelo AGG!');
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
    theme: str = "cyberpunk",
    username: str = "ViniciusNoetzold",
    anim_mode: str = "oscillate",
    scanline: bool = False
):
    p = registry.get("typography")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_typo.svg")
    p.run(text=text, font_name=font, theme=theme, out_svg=tmp, username=username, anim_mode=anim_mode, scanline=scanline)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/render/typography_batch")
def render_typography_batch(payload: dict = Body(...)):
    text = payload.get("text", "VINICIUS\nNOETZOLD")
    fonts = payload.get("fonts", ["slant", "isometric1", "doom"])
    theme = payload.get("theme", "cyberpunk")
    username = payload.get("username", "ViniciusNoetzold")
    anim_mode = payload.get("anim_mode", "oscillate")
    scanline = payload.get("scanline", False)
    disable_anim = payload.get("disable_anim", False)
    
    if disable_anim:
        anim_mode = "none"
        scanline = False

    p = registry.get("typography")
    results = []
    
    for font_name in fonts[:35]:
        try:
            tmp = os.path.join(tempfile.gettempdir(), f"_typo_batch_{font_name}.svg")
            p.run(
                text=text,
                font_name=font_name,
                theme=theme,
                out_svg=tmp,
                username=username,
                anim_mode=anim_mode,
                scanline=scanline
            )
            with open(tmp, "r", encoding="utf-8") as f:
                svg = f.read()
            results.append({
                "id": font_name,
                "title": font_name.title(),
                "tag": "FIGlet",
                "filename": f"typo-{font_name}-{theme}.svg",
                "svg": svg
            })
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

    return {
        "status": "success",
        "results": results
    }

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

@app.get("/api/render/pokemon")
def render_pokemon(pokemon: str = "gengar", shiny: bool = False, level: int = 100, username: str = "trainer_vini"):
    p = registry.get("pokemon_card")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_pk.svg")
    p.run(pokemon=pokemon, shiny=shiny, level=level, out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/weather")
def render_weather(city: str = "Curitiba, Brazil", condition: str = "sunny", unit: str = "C", username: str = "meteorologist"):
    p = registry.get("weather_card")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_we.svg")
    p.run(city=city, condition=condition, unit=unit, out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/clock")
def render_clock(color: str = "phosphor", format_mode: str = "24h", username: str = "chronos"):
    p = registry.get("tty_clock")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_cl.svg")
    p.run(color_scheme=color, format_mode=format_mode, out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/chess")
def render_chess(match: str = "opera", animated: bool = True, speed: float = 1.0, username: str = "grandmaster"):
    p = registry.get("chess_board")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_ch.svg")
    p.run(match=match, animated=animated, speed=speed, out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/tree")
def render_tree(title: str = "mezzold-termart-suite", username: str = "architect"):
    p = registry.get("file_tree")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_tr.svg")
    p.run(title=title, out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/fortune")
def render_fortune(username: str = "philosopher"):
    p = registry.get("fortune_banner")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_fo.svg")
    p.run(out_svg=tmp, username=username)
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

@app.post("/api/render/image_batch")
async def render_image_batch(
    engines: str = Form("chafa,rgb_ascii,drawille,dither"),
    username: str = Form("ViniciusNoetzold"),
    cols: int = Form(74),
    color_mode: str = Form("rgb"),
    anim_mode: str = Form("oscillate"),
    scanline: str = Form("false"),
    disable_anim: str = Form("false"),
    file: UploadFile = File(None)
):
    upload_path = os.path.join(tempfile.gettempdir(), "_upload_batch_temp.png")
    if file and hasattr(file, "read") and getattr(file, "filename", ""):
        content = await file.read()
        with open(upload_path, "wb") as f:
            f.write(content)
    else:
        demo_src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "photo.jpg")
        with open(demo_src, "rb") as sf, open(upload_path, "wb") as df:
            df.write(sf.read())

    is_disable = (disable_anim.lower() == "true")
    if is_disable:
        anim_mode = "none"
        is_scan = False
    else:
        is_scan = (scanline.lower() == "true")

    engine_list = [e.strip() for e in engines.split(",") if e.strip()]
    results = []

    ENGINE_TITLES = {
        "chafa": ("Chafa", "Braille 256"),
        "rgb_ascii": ("RGB ASCII", "TrueColor 24-bit"),
        "drawille": ("Drawille", "Subpixel 2x4"),
        "dither": ("Dither", "Floyd-Steinberg"),
        "jp2a": ("JP2A", "ASCII B&W"),
        "halftone": ("Halftone", "Retícula Vintage"),
        "edge_art": ("Edge Art", "Sobel Mangá"),
        "glitch": ("Glitch Cyberpunk", "VHS Corrupção"),
        "pixel_mosaic": ("Pixel Mosaic", "Arcade 8-bit"),
        "palette_swap": ("Palette Swap", "Catppuccin/Nord"),
        "rainbow_wave": ("Rainbow Wave", "Lolcat Arco-Íris")
    }

    for eng in engine_list[:12]:
        p = registry.get(eng)
        if not p:
            continue
        try:
            tmp = os.path.join(tempfile.gettempdir(), f"_img_batch_{eng}.svg")
            kwargs = {
                "image_path": upload_path,
                "out_svg": tmp,
                "cols": cols,
                "username": username,
                "anim_mode": anim_mode,
                "scanline": is_scan
            }
            if eng in ("rgb_ascii", "signature", "drawille", "jp2a"):
                kwargs["color_mode"] = color_mode
            elif eng == "chafa":
                kwargs["symbols"] = "braille"
                kwargs["colors"] = "256"

            p.run(**kwargs)
            with open(tmp, "r", encoding="utf-8") as f:
                svg = f.read()

            title_info = ENGINE_TITLES.get(eng, (eng.title(), "Filtro"))
            results.append({
                "id": eng,
                "title": title_info[0],
                "tag": title_info[1],
                "filename": f"{eng}-{cols}cols.svg",
                "svg": svg
            })
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

    return {
        "status": "success",
        "results": results
    }

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
    elif engine == "donut_3d":
        kwargs["theme"] = "cyberpunk"
        kwargs["frames_count"] = 16
    elif engine == "cava":
        kwargs["theme"] = "cyberpunk"
        kwargs["bars_count"] = 36
    elif engine == "doom_fire":
        kwargs["cols"] = 56
        kwargs["rows"] = 22
        kwargs["frames_count"] = 12
    elif engine == "synthwave_grid":
        pass
    elif engine == "game_of_life":
        kwargs["cols"] = 50
        kwargs["rows"] = 22
        kwargs["frames_count"] = 14
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
    compile_real = payload.get("compile_real", False)
    
    p = registry.get("vhs_recorder")
    preview_svg = p.render_simulation_svg(tape_content)
    
    gif_data = None
    if compile_real and p.has_binary():
        tmp_dir = tempfile.mkdtemp(prefix="vhs_")
        tape_path = os.path.join(tmp_dir, "script.tape")
        with open(tape_path, "w", encoding="utf-8") as f:
            f.write(tape_content)
        
        try:
            subprocess.run([p.bin_path, "script.tape"], cwd=tmp_dir, capture_output=True, text=True, timeout=30)
            for f in os.listdir(tmp_dir):
                if f.endswith(".gif") and os.path.getsize(os.path.join(tmp_dir, f)) > 0:
                    import base64
                    with open(os.path.join(tmp_dir, f), "rb") as gf:
                        gif_data = f"data:image/gif;base64,{base64.b64encode(gf.read()).decode('ascii')}"
                    break
        except Exception:
            pass

    return {
        "status": "success",
        "message": "Fita processada com sucesso!",
        "preview_svg": preview_svg,
        "gif_data": gif_data
    }

@app.post("/api/agg/compile")
def compile_agg_cast(payload: dict = Body(...)):
    theme = payload.get("theme", "dracula")
    font_size = int(payload.get("font_size", 14))
    speed = float(payload.get("speed", 1.0))
    
    cast_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "demo.cast"))
    tmp_dir = tempfile.mkdtemp(prefix="agg_")
    out_gif = os.path.join(tmp_dir, "agg_output.gif")
    
    p = registry.get("agg_generator")
    if not p.has_binary():
        return {"status": "error", "message": "bin/agg.exe não encontrado"}
    
    cmd = [p.bin_path, cast_path, out_gif, "--theme", theme, "--font-size", str(font_size), "--speed", str(speed)]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if os.path.exists(out_gif) and os.path.getsize(out_gif) > 0:
            import base64
            with open(out_gif, "rb") as gf:
                gif_data = f"data:image/gif;base64,{base64.b64encode(gf.read()).decode('ascii')}"
            return {
                "status": "success",
                "gif_data": gif_data,
                "filename": f"agg-{theme}.gif"
            }
        else:
            return {"status": "error", "message": "Falha na compilação do arquivo .cast com AGG"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def launch_studio(port: int = 7860):
    url = f"http://localhost:{port}"
    print(f"\n[Mezzold TermArt Studio] Serving UI at {url}")
    print("Press Ctrl+C to stop the studio.\n")
    webbrowser.open(url)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
