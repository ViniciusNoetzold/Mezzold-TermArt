"""
Mezzold TermArt - Visual Web Studio
FastAPI + TailwindCSS interactive visual studio for configuring, previewing, and exporting terminal art.
"""
import os
import sys
import webbrowser
from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from ...core.registry import registry

app = FastAPI(title="Mezzold TermArt Studio", version="2.0.0")

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mezzold TermArt Studio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 500: '#58a6ff', 600: '#1f6feb', dark: '#0d1117', card: '#161b22', border: '#30363d' }
          }
        }
      }
    }
  </script>
  <style>
    @keyframes pulse-slow { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    .pulse-dot { animation: pulse-slow 2s infinite ease-in-out; }
    svg { max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 12px; }
  </style>
</head>
<body class="bg-brand-dark text-slate-200 font-mono min-h-screen flex flex-col">
  <!-- Top Navigation -->
  <header class="border-b border-brand-border bg-brand-card/70 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="h-3 w-3 rounded-full bg-emerald-500 pulse-dot"></div>
      <h1 class="text-lg font-bold text-white tracking-wider flex items-center gap-2">
        <span>⚡ MEZZOLD</span>
        <span class="text-brand-500">TERMART STUDIO</span>
        <span class="text-xs px-2 py-0.5 rounded bg-brand-border text-slate-400">v2.0</span>
      </h1>
    </div>
    <div class="flex items-center gap-4 text-xs">
      <span class="text-slate-400">Owner: <strong class="text-white">Vinícius Noetzold</strong></span>
      <a href="https://github.com/ViniciusNoetzold/Mezzold-TermArt" target="_blank" class="px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold transition">GitHub Repo ↗</a>
    </div>
  </header>

  <!-- Main Studio -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
    <!-- Left: Controls & Generator -->
    <div class="lg:col-span-4 flex flex-col gap-5">
      <!-- Tabs -->
      <div class="grid grid-cols-3 gap-1 p-1 bg-brand-card rounded-xl border border-brand-border text-xs">
        <button onclick="switchTab('portrait')" id="btn-portrait" class="py-2 rounded-lg font-semibold bg-brand-600 text-white">Retrato/Logo</button>
        <button onclick="switchTab('3d')" id="btn-3d" class="py-2 rounded-lg font-semibold text-slate-400 hover:text-white">3D & City</button>
        <button onclick="switchTab('profile')" id="btn-profile" class="py-2 rounded-lg font-semibold text-slate-400 hover:text-white">Stats & Heatmap</button>
      </div>

      <!-- Controls Container -->
      <div class="p-5 rounded-2xl bg-brand-card border border-brand-border flex flex-col gap-4 text-sm">
        <!-- Tab 1: Portrait / Signature -->
        <div id="tab-portrait" class="flex flex-col gap-4">
          <h2 class="font-bold text-white text-base">🖼️ Conversão de Imagem & SVG</h2>
          <div>
            <label class="text-xs text-slate-400 block mb-1">Tipo de Componente</label>
            <select id="img-type" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2.5 text-slate-200">
              <option value="portrait">Retrato Terminal (Digitação com Cursor)</option>
              <option value="signature">Assinatura / Logo em Caligrafia Braille HD</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400 block mb-1">Nome / Usuário</label>
            <input id="img-username" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200">
          </div>
          <div>
            <label class="text-xs text-slate-400 block mb-1">Colunas (Densidade)</label>
            <input id="img-cols" type="range" min="40" max="110" value="76" class="w-full accent-brand-500" oninput="document.getElementById('cols-val').innerText = this.value">
            <span class="text-xs text-slate-500 float-right"><span id="cols-val">76</span> colunas</span>
          </div>
          <div>
            <label class="text-xs text-slate-400 block mb-1">Imagem</label>
            <input id="img-file" type="file" accept="image/*" class="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-brand-border file:text-white hover:file:bg-brand-600">
          </div>
          <button onclick="generateImage()" class="mt-2 w-full py-3 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition">Gerar SVG</button>
        </div>

        <!-- Tab 2: 3D & City -->
        <div id="tab-3d" class="hidden flex flex-col gap-4">
          <h2 class="font-bold text-white text-base">🧊 3D Wireframe & Voxel City</h2>
          <div>
            <label class="text-xs text-slate-400 block mb-1">Modo 3D</label>
            <select id="mode-3d" onchange="toggle3dInputs()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2.5 text-slate-200">
              <option value="city">Cidade 3D Isométrica de Commits</option>
              <option value="wordmark">Letreiro 3D em Wireframe Oscilante</option>
            </select>
          </div>
          <div id="city-inputs">
            <label class="text-xs text-slate-400 block mb-1">GitHub Username</label>
            <input id="city-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200">
          </div>
          <div id="wordmark-inputs" class="hidden">
            <label class="text-xs text-slate-400 block mb-1">Texto (use \n para nova linha)</label>
            <textarea id="wordmark-text" rows="2" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200">MEZZOLD\nSTUDIOS</textarea>
          </div>
          <button onclick="generate3d()" class="mt-2 w-full py-3 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition">Renderizar 3D</button>
        </div>

        <!-- Tab 3: Profile & Heatmap -->
        <div id="tab-profile" class="hidden flex flex-col gap-4">
          <h2 class="font-bold text-white text-base">📊 Contribuições & Neofetch</h2>
          <div>
            <label class="text-xs text-slate-400 block mb-1">Componente</label>
            <select id="profile-type" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2.5 text-slate-200">
              <option value="heatmap">Heatmap em Cascata (Live Commits)</option>
              <option value="neofetch">Card de Specs Neofetch</option>
              <option value="stats">Stats Card Dark Mode</option>
              <option value="pipes">Screensaver Pipes Procedural</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400 block mb-1">GitHub Username</label>
            <input id="profile-user" type="text" value="ViniciusNoetzold" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200">
          </div>
          <button onclick="generateProfile()" class="mt-2 w-full py-3 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-lg transition">Gerar Widget</button>
        </div>
      </div>
    </div>

    <!-- Right: Live Canvas Preview -->
    <div class="lg:col-span-8 flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">Preview ao Vivo:</span>
          <span id="preview-tag" class="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-semibold">contrib-3d-city.svg</span>
        </div>
        <div class="flex gap-2">
          <button onclick="downloadSvg()" class="text-xs px-3 py-1.5 rounded-lg border border-brand-border bg-brand-card hover:bg-brand-border text-white font-semibold transition">Baixar SVG ⭳</button>
        </div>
      </div>

      <!-- Live Display Box -->
      <div id="canvas-wrapper" class="flex-1 min-h-[500px] p-6 rounded-2xl bg-brand-card border border-brand-border flex items-center justify-center overflow-auto shadow-2xl relative">
        <div id="svg-display" class="w-full flex items-center justify-center">
          <div class="text-center text-slate-500">
            <p class="text-4xl mb-3">🎨</p>
            <p>Selecione um componente e clique em Gerar para ver o SVG renderizado ao vivo!</p>
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    let currentSvg = "";
    let currentFilename = "termart.svg";

    function switchTab(tab) {
      ['portrait', '3d', 'profile'].forEach(t => {
        document.getElementById(`tab-${t}`).classList.add('hidden');
        document.getElementById(`btn-${t}`).classList.remove('bg-brand-600', 'text-white');
        document.getElementById(`btn-${t}`).classList.add('text-slate-400');
      });
      document.getElementById(`tab-${tab}`).classList.remove('hidden');
      document.getElementById(`btn-${tab}`).classList.add('bg-brand-600', 'text-white');
      document.getElementById(`btn-${tab}`).classList.remove('text-slate-400');
    }

    function toggle3dInputs() {
      const mode = document.getElementById('mode-3d').value;
      if (mode === 'city') {
        document.getElementById('city-inputs').classList.remove('hidden');
        document.getElementById('wordmark-inputs').classList.add('hidden');
      } else {
        document.getElementById('city-inputs').classList.add('hidden');
        document.getElementById('wordmark-inputs').classList.remove('hidden');
      }
    }

    function setPreview(svgContent, filename) {
      currentSvg = svgContent;
      currentFilename = filename;
      document.getElementById('preview-tag').innerText = filename;
      document.getElementById('svg-display').innerHTML = svgContent;
    }

    async function generate3d() {
      const mode = document.getElementById('mode-3d').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Renderizando 3D...</div>';
      if (mode === 'city') {
        const user = document.getElementById('city-user').value;
        const res = await fetch(`/api/render/city?username=${encodeURIComponent(user)}`);
        const svg = await res.text();
        setPreview(svg, `${user}-3d-city.svg`);
      } else {
        const text = document.getElementById('wordmark-text').value;
        const res = await fetch(`/api/render/wordmark?text=${encodeURIComponent(text)}`);
        const svg = await res.text();
        setPreview(svg, `wordmark-3d.svg`);
      }
    }

    async function generateProfile() {
      const type = document.getElementById('profile-type').value;
      const user = document.getElementById('profile-user').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Gerando widget...</div>';
      const res = await fetch(`/api/render/${type}?username=${encodeURIComponent(user)}`);
      const svg = await res.text();
      setPreview(svg, `${type}.svg`);
    }

    async function generateImage() {
      const type = document.getElementById('img-type').value;
      const user = document.getElementById('img-username').value;
      const cols = document.getElementById('img-cols').value;
      const fileInput = document.getElementById('img-file');
      
      const formData = new FormData();
      formData.append('type', type);
      formData.append('username', user);
      formData.append('cols', cols);
      if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
      }
      
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Processando imagem em ASCII/Braille...</div>';
      const res = await fetch('/api/render/image', { method: 'POST', body: formData });
      const svg = await res.text();
      setPreview(svg, `${type}.svg`);
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

    // Auto load 3D city on start
    window.addEventListener('DOMContentLoaded', () => {
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
def render_city(username: str = "ViniciusNoetzold"):
    p = registry.get("isometric_city")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_city.svg")
    p.run(username=username, out_svg=tmp)
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
def render_pipes(username: str = "ViniciusNoetzold"):
    p = registry.get("pipes")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_pi.svg")
    p.run(out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/render/image")
async def render_image_upload(
    type: str = Form("portrait"),
    username: str = Form("ViniciusNoetzold"),
    cols: int = Form(76),
    file: UploadFile = File(None)
):
    upload_path = os.path.join(os.path.dirname(__file__), "_upload_temp.png")
    if file:
        content = await file.read()
        with open(upload_path, "wb") as f:
            f.write(content)
    else:
        # Fallback to demo photo
        demo_src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "signature.png" if type == "signature" else "photo.jpg")
        with open(demo_src, "rb") as sf, open(upload_path, "wb") as df:
            df.write(sf.read())

    out_svg = os.path.join(os.path.dirname(__file__), f"_temp_{type}.svg")
    if type == "signature":
        p = registry.get("signature")
        p.run(image_path=upload_path, out_svg=out_svg, username=username, cols=cols)
    else:
        p = registry.get("portrait")
        p.run(image_path=upload_path, out_svg=out_svg, username=username, full_name=username, cols=cols)

    with open(out_svg, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

def launch_studio(port: int = 7860):
    url = f"http://localhost:{port}"
    print(f"\n[Mezzold TermArt Studio] Serving UI at {url}")
    print("Press Ctrl+C to stop the studio.\n")
    webbrowser.open(url)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
