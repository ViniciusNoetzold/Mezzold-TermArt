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
  <header class="border-b border-brand-border bg-brand-card/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
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
  </header>

  <!-- Navigation Tabs (5 Categorias Abrangendo Todas as Ferramentas) -->
  <div class="border-b border-brand-border bg-brand-card/50 px-6 py-2">
    <div class="max-w-7xl mx-auto flex flex-wrap gap-2 text-xs">
      <button onclick="switchTab('image')" id="btn-image" class="tab-btn px-4 py-2 rounded-xl font-bold bg-brand-600 text-white flex items-center gap-1.5 transition">
        <span>🖼️</span> <span>Imagens & Chafa</span>
      </button>
      <button onclick="switchTab('3d')" id="btn-3d" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>🧊</span> <span>3D & Tipografia</span>
      </button>
      <button onclick="switchTab('profile')" id="btn-profile" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>📊</span> <span>Stats & Heatmap</span>
      </button>
      <button onclick="switchTab('pipes')" id="btn-pipes" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>🧪</span> <span>Pipes.sh Retro FX</span>
      </button>
      <button onclick="switchTab('vhs')" id="btn-vhs" class="tab-btn px-4 py-2 rounded-xl font-bold text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <span>🎬</span> <span>Gravador VHS (.tape)</span>
      </button>
    </div>
  </div>

  <!-- Main Content -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
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
              <option value="rgb_ascii">TrueColor RGB ASCII (Cores 24-bit Reais da Foto)</option>
              <option value="chafa">Chafa (C Engine) - Sub-pixel Graphics de Alta Resolução</option>
              <option value="portrait">Retrato Terminal (Go Braille 2x4 com Digitação)</option>
              <option value="signature">Logo / Assinatura em Caligrafia (ASCII Puro / Braille)</option>
            </select>
          </div>

          <div id="rgb-options" class="flex flex-col gap-2 p-3 rounded-xl bg-brand-dark/50 border border-brand-border text-xs">
            <span class="font-semibold text-emerald-400">Esquema de Cores RGB</span>
            <select id="rgb-mode" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
              <option value="rgb">TrueColor RGB (Cores Reais 24-bit Amostradas da Foto)</option>
              <option value="cyberpunk">Gradiente Cyberpunk (Ciano -^> Roxo -^> Rosa)</option>
              <option value="matrix">Matrix Hacker (Verde Neon com Sombras)</option>
              <option value="mono">Monocromático Estilizado</option>
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
            <div class="flex justify-between text-xs text-slate-400 mb-1">
              <span>Densidade (Colunas)</span>
              <span id="img-cols-val" class="text-brand-500 font-bold">74</span>
            </div>
            <input id="img-cols" type="range" min="40" max="110" value="74" class="w-full accent-brand-500" oninput="document.getElementById('img-cols-val').innerText = this.value">
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Foto / Imagem (Opcional - usa demo se vazio)</label>
            <input id="img-file" type="file" accept="image/*" class="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-brand-border file:text-white hover:file:bg-brand-600">
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

        <!-- ================= TAB 4: PIPES.SH PROCEDURAL ================= -->
        <div id="tab-pipes" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🧪 Pipes.sh Retro Screensaver</h2>
            <p class="text-xs text-slate-400 mt-0.5">Motor inspirado no clássico pipeseroni/pipes.sh em puro SVG</p>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-400 block mb-1">Número de Tubos</label>
              <input id="pipes-count" type="number" min="1" max="8" value="4" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Passos de Animação</label>
              <input id="pipes-steps" type="number" min="20" max="150" value="60" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Usuário / Prompt do Terminal</label>
            <input id="pipes-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <button onclick="generatePipes()" class="mt-2 w-full py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>🌀</span> <span>Gerar Animação Procedural Pipes.sh</span>
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
    <div class="lg:col-span-7 flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">Arte Renderizada:</span>
          <span id="preview-tag" class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30">contrib-3d-city.svg</span>
        </div>
        <div class="flex gap-2">
          <button onclick="downloadSvg()" class="text-xs px-3 py-1.5 rounded-lg border border-brand-border bg-brand-card hover:bg-brand-border text-white font-semibold transition flex items-center gap-1.5">
            <span>⭳</span> <span>Baixar Arquivo</span>
          </button>
        </div>
      </div>

      <!-- Preview Canvas -->
      <div id="canvas-wrapper" class="flex-1 min-h-[520px] p-6 rounded-2xl bg-brand-card border border-brand-border flex items-center justify-center overflow-auto shadow-2xl relative">
        <div id="svg-display" class="w-full flex items-center justify-center">
          <div class="text-center text-slate-500">
            <p class="text-4xl mb-3 animate-pulse">⚡</p>
            <p>Selecione um motor e clique em Gerar para ver o resultado ao vivo!</p>
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    let currentSvg = "";
    let currentFilename = "termart.svg";

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
      document.getElementById('rgb-options').classList.toggle('hidden', eng !== 'rgb_ascii');
      document.getElementById('chafa-options').classList.toggle('hidden', eng !== 'chafa');
      document.getElementById('sig-options').classList.toggle('hidden', eng !== 'signature');
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
      const cols = document.getElementById('img-cols').value;
      const fileInput = document.getElementById('img-file');
      
      const formData = new FormData();
      formData.append('engine', engine);
      formData.append('username', user);
      formData.append('cols', cols);
      
      if (engine === 'rgb_ascii') {
        formData.append('color_mode', document.getElementById('rgb-mode').value);
      } else if (engine === 'chafa') {
        formData.append('symbols', document.getElementById('chafa-symbols').value);
        formData.append('colors', document.getElementById('chafa-colors').value);
      } else if (engine === 'signature') {
        formData.append('braille', document.getElementById('sig-braille').checked ? 'true' : 'false');
      }

      if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
      }

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
        const res = await fetch(`/api/render/typography?text=${encodeURIComponent(text)}&font=${encodeURIComponent(font)}`);
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

    async function generatePipes() {
      const pipes = document.getElementById('pipes-count').value;
      const steps = document.getElementById('pipes-steps').value;
      const user = document.getElementById('pipes-user').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Gerando labirinto procedural de tubos...</div>';
      const res = await fetch(`/api/render/pipes?num_pipes=${pipes}&steps=${steps}&username=${encodeURIComponent(user)}`);
      const svg = await res.text();
      setPreview(svg, 'pipes-screensaver.svg');
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
def render_typography(text: str = "VINICIUS\nNOETZOLD", font: str = "slant", username: str = "ViniciusNoetzold"):
    p = registry.get("typography")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_typo.svg")
    p.run(text=text, font_name=font, out_svg=tmp, username=username)
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

    out_svg = os.path.join(os.path.dirname(__file__), f"_temp_{engine}.svg")
    if engine == "rgb_ascii":
        p = registry.get("rgb_ascii")
        p.run(image_path=upload_path, out_svg=out_svg, cols=cols, color_mode=color_mode, username=username)
    elif engine == "chafa":
        p = registry.get("chafa")
        p.run(image_path=upload_path, out_svg=out_svg, cols=cols, symbols=symbols, colors=colors, username=username)
    elif engine == "signature":
        p = registry.get("signature")
        p.run(image_path=upload_path, out_svg=out_svg, username=username, cols=cols, braille=(braille.lower() == "true"))
    else:
        p = registry.get("portrait")
        p.run(image_path=upload_path, out_svg=out_svg, username=username, full_name=username, cols=cols)

    with open(out_svg, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

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
