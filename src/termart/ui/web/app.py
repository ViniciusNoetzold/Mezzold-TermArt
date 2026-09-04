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
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,'script','dataLayer','GTM-KC94Z22H');</script>
  <!-- End Google Tag Manager -->
  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8865509480539792"
       crossorigin="anonymous"></script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mezzold TermArt Studio v2.5 — Terminal Art &amp; Profile Engine</title>

  <!-- Google Fonts: Plus Jakarta Sans (UI) & JetBrains Mono (Code/Terminal) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">

  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
  
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace']
          },
          colors: {
            brand: {
              50: '#f0f9ff',
              100: '#e0f2fe',
              200: '#bae6fd',
              300: '#7dd3fc',
              400: '#38bdf8',
              500: '#0ea5e9',
              600: '#0284c7',
              700: '#0369a1',
              dark: '#07090e',
              card: '#0d1322',
              cardElevated: '#131b2e',
              border: '#1e293b',
              borderLight: '#334155',
              accent: '#00f0ff',
              neon: '#a855f7'
            }
          },
          boxShadow: {
            'glow-cyan': '0 0 20px -3px rgba(0, 240, 255, 0.25)',
            'glow-sky': '0 0 20px -3px rgba(14, 165, 233, 0.35)',
            'glow-purple': '0 0 20px -3px rgba(168, 85, 247, 0.35)',
            'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.45)'
          }
        }
      }
    }
  </script>
  <style>
    @keyframes pulse-slow { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
    .pulse-dot { animation: pulse-slow 2s infinite ease-in-out; }
    
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: #07090e;
      background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(14, 165, 233, 0.12), transparent),
        radial-gradient(ellipse 60% 40% at 5% 30%, rgba(168, 85, 247, 0.07), transparent),
        radial-gradient(ellipse 50% 30% at 95% 70%, rgba(16, 185, 129, 0.05), transparent);
      background-attachment: fixed;
      color: #e2e8f0;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* Monospace elements use JetBrains Mono */
    .font-mono, pre, code, textarea, .code-font {
      font-family: 'JetBrains Mono', monospace !important;
    }

    /* Glassmorphism panels */
    .studio-glass {
      background: rgba(13, 19, 34, 0.82);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    }
    
    .canvas-grid {
      background-color: #090e17;
      background-image: radial-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px);
      background-size: 20px 20px;
    }

    svg {
      max-width: 100%;
      height: auto;
      display: block;
      margin: 0 auto;
      border-radius: 12px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }

    /* Ultra-sleek Cyberpunk & Glassmorphic select dropdowns */
    select {
      background-color: rgba(11, 17, 30, 0.95) !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      border-radius: 10px !important;
      color: #f1f5f9 !important;
      font-weight: 500 !important;
      letter-spacing: 0.2px;
      background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2338bdf8' stroke-width='2'%3e%3cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e") !important;
      background-position: right 0.85rem center !important;
      background-repeat: no-repeat !important;
      background-size: 1.1em 1.1em !important;
      padding-right: 2.5rem !important;
      -webkit-appearance: none;
      -moz-appearance: none;
      appearance: none;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    select:hover {
      border-color: rgba(56, 189, 248, 0.6) !important;
      background-color: rgba(16, 24, 42, 0.98) !important;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.2), 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }

    select:focus {
      outline: none !important;
      border-color: #38bdf8 !important;
      background-color: #0b111e !important;
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25), 0 0 20px rgba(56, 189, 248, 0.3) !important;
    }

    /* Option popup styling across modern browsers */
    select option {
      background-color: #0d1424 !important;
      color: #e2e8f0 !important;
      padding: 12px 14px !important;
      font-size: 12.5px !important;
      font-weight: 500 !important;
    }

    select option:checked {
      background-color: #1e293b !important;
      color: #38bdf8 !important;
      font-weight: 700 !important;
    }

    select optgroup {
      background-color: #070a12 !important;
      color: #64748b !important;
      font-weight: 700 !important;
      font-size: 11px !important;
      letter-spacing: 1px !important;
    }

    /* Form Inputs Micro-transitions */
    input, select, textarea {
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: #38bdf8 !important;
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.22) !important;
      background-color: #0b111e !important;
    }

    .tab-btn {
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.15);
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.14);
      border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.28);
    }

    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
  </style>
</head>
<body class="bg-[#07090e] text-slate-200 font-sans min-h-screen flex flex-col antialiased selection:bg-sky-500/30 selection:text-sky-200">
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KC94Z22H"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->
  <!-- Header -->
  <header class="border-b border-white/5 bg-[#0a0f1d]/85 backdrop-blur-xl sticky top-0 z-50 px-6 py-3 shadow-lg shadow-black/20">
    <div class="max-w-[1600px] w-full mx-auto flex items-center justify-between">
      <div class="flex items-center gap-3.5">
        <div class="relative flex items-center justify-center">
          <div class="h-3.5 w-3.5 rounded-full bg-emerald-400 pulse-dot shadow-lg shadow-emerald-400/50"></div>
          <div class="absolute h-6 w-6 rounded-full bg-emerald-500/20 animate-ping"></div>
        </div>
        <div class="flex flex-col">
          <h1 class="text-sm font-extrabold text-white tracking-wide flex items-center gap-2">
            <span class="bg-gradient-to-r from-cyan-400 via-sky-400 to-indigo-400 bg-clip-text text-transparent font-black tracking-wider text-base">⚡ MEZZOLD TERMART</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 font-semibold tracking-normal font-mono">v2.5 PRO</span>
          </h1>
          <span class="text-[11px] text-slate-400 font-medium">A Suíte Definitiva de Arte em Terminal, Screensavers Arcade &amp; Perfil GitHub</span>
        </div>
      </div>
      <div class="flex items-center gap-2.5 text-xs font-medium">
        <button id="btn-sound-toggle" onclick="toggleAudioFx()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-white/10 text-xs text-slate-200 hover:text-white transition cursor-pointer shadow-sm active:scale-95" title="Ligar / Desligar Efeitos Sonoros Retrô">
          <span id="sound-icon">🔊</span>
          <span id="sound-label">Som: ON</span>
        </button>
        <button onclick="openConfigModal()" class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-white/10 text-xs text-slate-200 hover:text-white transition cursor-pointer shadow-sm active:scale-95" title="Configurar Perfil e GitHub">
          <span class="text-sky-400">⚙️</span>
          <span id="header-user-badge">Perfil: <strong class="text-white">Convidado</strong></span>
        </button>
        <a href="https://github.com/ViniciusNoetzold/Mezzold-TermArt" target="_blank" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-semibold transition shadow-md shadow-sky-600/20 flex items-center gap-1.5 active:scale-95">
          <span>GitHub Repo</span>
          <span class="text-sky-200">↗</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <div class="border-b border-white/5 bg-[#0a0f1d]/60 backdrop-blur-md px-6 py-2.5 sticky top-[57px] z-40 shadow-sm">
    <div class="max-w-[1600px] mx-auto flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 text-xs font-medium">
      <button onclick="switchTab('image')" id="btn-image" class="tab-btn px-4 py-2 rounded-xl font-semibold bg-brand-600 text-white flex items-center gap-2 transition shrink-0 shadow-md shadow-sky-500/20">
        <span>🖼️</span> <span>Imagens &amp; Chafa</span>
      </button>
      <button onclick="switchTab('3d')" id="btn-3d" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>🧊</span> <span>3D &amp; Tipografia</span>
      </button>
      <button onclick="switchTab('profile')" id="btn-profile" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>🛡️</span> <span>Widgets de Perfil</span>
      </button>
      <button onclick="switchTab('animator')" id="btn-animator" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>✨</span> <span>Animador SVG</span>
      </button>
      <button onclick="switchTab('pipes')" id="btn-pipes" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>🕹️</span> <span>Screensavers Arcade &amp; FX</span>
      </button>
      <button onclick="switchTab('vhs')" id="btn-vhs" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>🎬</span> <span>Gravador VHS &amp; AGG</span>
      </button>
      <button onclick="switchTab('badges')" id="btn-badges" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>🏷️</span> <span>Badges &amp; Tech Stack</span>
      </button>
      <button onclick="switchTab('activity')" id="btn-activity" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>🎵</span> <span>Música &amp; Atividade Dev</span>
      </button>
      <button onclick="switchTab('builder')" id="btn-builder" class="tab-btn px-4 py-2 rounded-xl font-semibold text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition shrink-0">
        <span>🚀</span> <span>Construtor de Perfil &amp; README</span>
      </button>
      <button onclick="openConfigModal()" id="btn-config" class="tab-btn px-4 py-2 rounded-xl font-semibold bg-slate-900/70 border border-white/10 text-sky-400 hover:text-sky-300 hover:border-sky-500/40 flex items-center gap-2 transition ml-auto shrink-0 shadow-sm">
        <span>⚙️</span> <span>Configurar Perfil Dev</span>
      </button>
    </div>
  </div>

  <!-- Main Content -->
  <main class="flex-1 max-w-[1600px] w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
    <!-- Left Column: Controls -->
    <div class="lg:col-span-5 flex flex-col gap-5">
      <div class="p-6 rounded-3xl studio-glass border border-white/10 flex flex-col gap-5 text-sm shadow-2xl backdrop-blur-xl">
        
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
              <button type="button" onclick="selectImgPreset('all')" class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border hover:border-brand-500 text-[10px] text-slate-300 font-medium">🎨 Todos os 13 Motores</button>
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
                <input type="checkbox" name="img_batch_eng" value="palette_swap" checked class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Palette Swap (Retrô)</span>
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
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" name="img_batch_eng" value="portrait" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Retrato Terminal</span>
              </label>
              <label class="flex items-center gap-1.5 px-2 py-1 rounded bg-brand-dark border border-brand-border/80 hover:border-brand-500 text-[11px] text-slate-300 cursor-pointer select-none col-span-2">
                <input type="checkbox" name="img_batch_eng" value="signature" class="accent-brand-500" onchange="updateImgBatchCounter()">
                <span>Assinatura / Caligrafia (ASCII &amp; Braille)</span>
              </label>
            </div>
          </div>

          <div id="rgb-options" class="flex flex-col gap-2 p-3 rounded-xl bg-brand-dark/50 border border-brand-border text-xs">
            <span class="font-semibold text-emerald-400">Esquema de Cores</span>
            <select id="rgb-mode" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200">
              <option value="vivid" selected>✨ TrueColor Vivid (Cores Reais Hi-Fi Vibrantes & Saturadas)</option>
              <option value="rgb">🎨 TrueColor RGB Natural (Cores Reais 24-bit Neutras da Foto)</option>
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
            <input id="img-user" type="text" placeholder="ex: developer" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
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
                <option value="dvd">📀 Efeito DVD Bouncing (Quicando nas Bordas &amp; Cantos com Troca de Cor)</option>
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
              <input id="city-user" type="text" placeholder="ex: seu-usuario-github" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
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
                  <option value="dvd">📀 Efeito DVD Bouncing (Quicando nas Bordas &amp; Cantos com Troca de Cor)</option>
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

        <!-- ================= TAB 3: WIDGETS DE PERFIL & GAMIFICAÇÃO ================= -->
        <div id="tab-profile" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🛡️ Widgets de Perfil & Gamificação</h2>
            <p class="text-xs text-slate-400 mt-0.5">Passaporte RPG, Git Subway, Dev Pet, Xadrez PGN, Pokémon Holo e Métricas</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Tipo de Widget</label>
            <select id="profile-widget" onchange="onProfileWidgetChange()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="btop_monitor">📟 Btop++ / Htop Cyberpunk (8-Cores, Braille, RAM & Processos)</option>
              <option value="cli_session">⌨️ CLI Terminal Session Mockup (Ghostty, Digitação & Telemetria)</option>
              <option value="git_graph">🌿 Git Commit Graph Visualizer (Árvore Neon de Branches & Commits)</option>
              <option value="cyber_id">🪪 Cyberpunk Corporate ID (Crachá Arasaka/Militech com Chip & QR)</option>
              <option value="achievement">🏆 Console Achievement Banner (Troféu Dourado 3D com Glint Xbox/Steam)</option>
              <option value="skill_tree">🌳 Developer RPG Skill Tree (Constelação de Talentos Frontend/Cloud/AI)</option>
              <option value="rpg_sheet">⚔️ Passaporte RPG do Desenvolvedor (Classes D&D, HP/Mana & Inventário)</option>
              <option value="git_subway">🗺️ Mapa de Metrô dos Commits (Git Branch Subway Line & Trens)</option>
              <option value="dev_pet">👾 Tamagotchi Virtual Dev Pet 1996 (Display LCD, Café & Bateria)</option>
              <option value="chess">♟️ Partida de Xadrez (Animação de Lances & Importador PGN!)</option>
              <option value="pokemon">🎮 Card RPG Pokémon (16 Espécies, Shiny & Níveis)</option>
              <option value="weather">⛅ Previsão do Tempo (wttr.in ASCII Radar & Cidades)</option>
              <option value="clock">⏰ TTY Digital Clock (LED Neon & Formato 12h/24h)</option>
              <option value="heatmap">📊 Heatmap em Cascata (GraphQL Real-Time Commits)</option>
              <option value="neofetch">💻 Card Neofetch macOS (Specs Técnicas & Foco)</option>
              <option value="stats">📈 GitHub Stats Card Dark (github-readme-stats)</option>
              <option value="tree">📁 Architecture File Tree (Estrutura de Pastas)</option>
              <option value="fortune">🥠 Fortune Cookie (Filosofia Hacker & Zen)</option>
            </select>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">GitHub Username / Treinador</label>
            <input id="profile-user" type="text" placeholder="ex: seu-usuario-github" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <!-- POKEMON OPTIONS -->
          <!-- BTOP MONITOR OPTIONS -->
          <div id="profile-opt-btop" class="flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <span>📟</span> <span>Configurações do Btop++ Monitor</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Tema Unixporn</label>
                <select id="btop-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="catppuccin">Catppuccin Mocha</option>
                  <option value="dracula">Dracula Dark</option>
                  <option value="tokyonight">Tokyo Night</option>
                  <option value="nord">Nord Arctic</option>
                  <option value="cyberpunk">Cyberpunk Neon</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Uptime</label>
                <input id="btop-uptime" type="text" value="42 DAYS, 13:37:00" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
            </div>
          </div>

          <!-- CLI SESSION OPTIONS -->
          <div id="profile-opt-cli" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-sky-400 flex items-center gap-1.5">
              <span>⌨️</span> <span>Sessão Interativa de Terminal</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Tema do Terminal</label>
                <select id="cli-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="ghostty">Ghostty Dark</option>
                  <option value="dracula">Dracula</option>
                  <option value="catppuccin">Catppuccin</option>
                  <option value="matrix">Matrix Green</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Título da Janela</label>
                <input id="cli-title" type="text" value="user@workstation: ~" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
            </div>
          </div>

          <!-- GIT GRAPH OPTIONS -->
          <div id="profile-opt-gitgraph" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
              <span>🌿</span> <span>Grafo de Commits Neon</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Tema de Linhas</label>
                <select id="gitgraph-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="neon_cyber">Neon Cyber Glow</option>
                  <option value="gitkraken">GitKraken Vibrant</option>
                  <option value="terminal">Green Phosphor</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Nome do Repositório</label>
                <input id="gitgraph-repo" type="text" value="core-engine" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
            </div>
          </div>

          <!-- CYBER ID OPTIONS -->
          <div id="profile-opt-cyberid" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
              <span>🪪</span> <span>Crachá Cyberpunk Holográfico</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Corporação</label>
                <select id="cyberid-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="arasaka_red">Arasaka Security</option>
                  <option value="militech_yellow">Militech Arms</option>
                  <option value="neon_matrix">NetWatch Matrix</option>
                  <option value="phantom_purple">Phantom Purple</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Nível de Autorização</label>
                <input id="cyberid-clearance" type="text" value="LEVEL 5 - ROOT" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Cargo</label>
                <input id="cyberid-role" type="text" value="Senior Lead Architect" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Departamento</label>
                <input id="cyberid-dept" type="text" value="Cyber Defense &amp; Cloud Infra" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              </div>
            </div>
          </div>

          <!-- ACHIEVEMENT OPTIONS -->
          <div id="profile-opt-achievement" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-yellow-400 flex items-center gap-1.5">
              <span>🏆</span> <span>Banner de Conquista / Troféu</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Plataforma</label>
                <select id="ach-platform" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="xbox">Xbox Rare (+Glint)</option>
                  <option value="steam">Steam Gold</option>
                  <option value="playstation">PlayStation Platinum</option>
                  <option value="cyberpunk">Cyberpunk Secret</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Pontos / Gamerscore</label>
                <input id="ach-points" type="number" value="100" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Título da Conquista</label>
              <input id="ach-title" type="text" value="LENDÁRIO CODE ARCHITECT" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Descrição</label>
              <input id="ach-desc" type="text" value="Deployou 1.000 microsserviços em produção numa sexta-feira sem quebrar" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
          </div>

          <!-- SKILL TREE OPTIONS -->
          <div id="profile-opt-skilltree" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <span>🌳</span> <span>Árvore RPG de Habilidades Dev</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Tema da Constelação</label>
                <select id="skill-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="cyber_constellation" selected>🌌 Cyber Constellation (Neon Cyan &amp; Magenta)</option>
                  <option value="diablo_arcane">🔥 Diablo IV Arcane (Carmesim &amp; Runas Ígneas)</option>
                  <option value="matrix_nodes">🟢 Matrix Grid (Verde Fosfórico &amp; Terminal)</option>
                  <option value="celestial_gold">⭐ Celestial Gold &amp; Obsidian (Dourado Cósmico)</option>
                  <option value="dracula_rpg">🧛 Dracula RPG (Roxo &amp; Tons Pastel)</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Foco Primário</label>
                <input id="skill-focus" type="text" value="Fullstack / Cloud / AI Architect" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              </div>
            </div>
          </div>

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

          <!-- RPG SHEET OPTIONS -->
          <div id="profile-opt-rpg" class="flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
              <span>⚔️</span> <span>Ficha & Atributos RPG do Desenvolvedor</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Classe RPG</label>
                <select id="rpg-class" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="alchemist">⚗️ Alchemist (Dev Full-Stack / Poções)</option>
                  <option value="sorcerer">🧙‍♂️ Sorcerer (Arquiteto Cloud / Feitiços)</option>
                  <option value="ninja">🥷 Ninja (Hacker / Low-Latency)</option>
                  <option value="paladin">🛡️ Paladin (DevSecOps / Segurança)</option>
                  <option value="shaman">🌿 Shaman (Data Science / Machine Learning)</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Nível (Level)</label>
                <input id="rpg-level" type="number" min="1" max="100" value="85" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              </div>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Nome do Personagem / Herói</label>
              <input id="rpg-name" type="text" placeholder="Ex: VINICIUS" value="VINICIUS" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div class="grid grid-cols-3 gap-2">
              <div>
                <label class="text-[10px] text-red-400 block mb-1">HP (%)</label>
                <input id="rpg-hp" type="number" min="10" max="100" value="96" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-[10px] text-cyan-400 block mb-1">Mana (%)</label>
                <input id="rpg-mana" type="number" min="10" max="100" value="91" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-[10px] text-amber-400 block mb-1">Stamina (%)</label>
                <input id="rpg-stamina" type="number" min="10" max="100" value="98" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
              </div>
            </div>
            <!-- UPLOAD DE IMAGEM / AVATAR (PNG, JPG, GIF ANIMADO, SVG) -->
            <div class="pt-2 border-t border-brand-border/40 flex flex-col gap-2">
              <div class="flex items-center justify-between">
                <label class="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <span>🖼️</span> <span>Avatar Personalizado</span>
                </label>
                <span class="text-[10px] text-purple-400 font-mono">PNG, JPG, GIF, SVG</span>
              </div>
              <p class="text-[11px] text-slate-400 leading-tight">
                Substitua a ilustração da classe por sua própria foto, avatar ou GIF animado no passaporte.
              </p>
              <div class="flex items-center gap-2">
                <label class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-purple-500/15 hover:bg-purple-500/25 border border-purple-500/30 hover:border-purple-500/50 rounded-lg cursor-pointer transition text-xs text-purple-200 font-medium">
                  <span>📁 Anexar Imagem / GIF</span>
                  <input id="rpg-avatar-input" type="file" accept="image/png,image/jpeg,image/gif,image/svg+xml,image/webp" class="hidden" onchange="handleRpgAvatarUpload(event)">
                </label>
                <button type="button" id="btn-rpg-avatar-clear" onclick="clearRpgAvatar()" class="hidden px-2.5 py-2 bg-red-500/15 hover:bg-red-500/25 border border-red-500/30 rounded-lg text-xs text-red-300 transition" title="Restaurar ilustração padrão da classe">
                  ✕ Limpar
                </button>
              </div>
              <div id="rpg-avatar-preview-box" class="hidden items-center gap-2.5 p-2 bg-brand-surface/80 rounded-lg border border-purple-500/30">
                <img id="rpg-avatar-preview-img" src="" alt="Avatar" class="w-12 h-10 object-cover rounded border border-purple-500/40 shadow-sm bg-brand-dark">
                <div class="flex-1 min-w-0">
                  <div id="rpg-avatar-preview-name" class="text-xs text-slate-200 font-medium truncate">avatar.png</div>
                  <div id="rpg-avatar-preview-size" class="text-[10px] text-purple-300 font-mono">Base64 Embutido</div>
                </div>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">✓ Ativo</span>
              </div>
            </div>
          </div>

          <!-- GIT SUBWAY OPTIONS -->
          <div id="profile-opt-subway" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <span>🗺️</span> <span>Mapa de Linhas Git Subway</span>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Nome do Repositório / Linha Principal</label>
              <input id="subway-repo" type="text" value="core-platform" placeholder="Ex: mezzold-termart" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
          </div>

          <!-- DEV PET TAMAGOTCHI OPTIONS -->
          <div id="profile-opt-pet" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
              <span>👾</span> <span>Tamagotchi Dev Pet 1996</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Mascote Pixel-Art</label>
                <select id="pet-type" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="mametchi" selected>⭐ Mametchi 1996 (Mascote Gênio #1 Bandai)</option>
                  <option value="kuchipatchi">🦆 Kuchipatchi (Comilão Bico-de-Pato)</option>
                  <option value="ginjirotchi">🐧 Ginjirotchi (Pinguim Atleta Nadador)</option>
                  <option value="maskutchi">🥷 Maskutchi (Ninja Mascarado Secreto)</option>
                  <option value="marutchi">🟢 Marutchi (Bouncing Toddler)</option>
                  <option value="babytchi">👶 Babytchi (Recém-Nascido com Topete)</option>
                  <option value="oyajitchi">👴 Oyajitchi (Bigode Clássico de Terno)</option>
                  <option value="tamatchi">🌱 Tamatchi (Jovem com Orelhinhas)</option>
                  <option value="nyorotchi">🐍 Nyorotchi (Cobra Ondulante)</option>
                  <option value="tarakotchi">👄 Tarakotchi (Bocão Alienígena)</option>
                  <option value="cat">🐱 Pixel Cat (Mametchi)</option>
                  <option value="robot">🤖 Cyber Droid (Maskutchi)</option>
                  <option value="dragon">🐲 Mini Dragão (Kuchipatchi)</option>
                  <option value="penguin">🐧 Linux Tux (Ginjirotchi)</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Nome do Pet</label>
                <input id="pet-name" type="text" value="KERNEL" placeholder="Ex: KERNEL" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">📟 Estilo da Carcaça / Aparelho</label>
                <select id="pet-casing-style" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="egg" selected>🥚 Tamagotchi Egg 1996 (Clássico Oval)</option>
                  <option value="gameboy">🎮 Game Boy Pocket (Console Portátil)</option>
                  <option value="pager">📟 Telecom Beeper Pager 90s</option>
                  <option value="star">⭐ Tamagotchi Starlight (Antena Estelar)</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">🎨 Cor do Aparelho (Shell)</label>
                <select id="pet-casing-color" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="cyber_blue" selected>🔵 Cyber Blue 90s (Translúcido)</option>
                  <option value="retro_pink">🌸 Retro Pink 1996 (Original Bandai)</option>
                  <option value="atomic_purple">🟣 Atomic Purple (Game Boy Color)</option>
                  <option value="banana_yellow">⚡ Pikachu Yellow (Amarelo 90s)</option>
                  <option value="matrix_black">🟢 Matrix Stealth Black (Terminal)</option>
                  <option value="emerald_green">🟩 Emerald Pocket Green</option>
                  <option value="vaporwave_sunset">🌇 Vaporwave Sunset (Gradiente)</option>
                  <option value="milky_white">⚪ Milky White Pearl (Pérola Japonesa)</option>
                  <option value="lava_red">🔴 Arcade Lava Red (Cereja Vivo)</option>
                  <option value="kawaii_lavender">💜 Kawaii Pastel Lavender</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Felicidade (%)</label>
                <input id="pet-happiness" type="number" min="10" max="100" value="98" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Nível de Café / Bateria (%)</label>
                <input id="pet-coffee" type="number" min="10" max="100" value="100" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
              </div>
            </div>
          </div>

          <!-- CHESS OPTIONS -->
          <div id="profile-opt-chess" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
              <span>♟️</span> <span>Partida & Xeque-Mate</span>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Partida Histórica Pré-Configurada</label>
              <select id="chess-match" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="opera">🎭 Paul Morphy (Opera Game 1858) - 17 lances, Sacrifício de Dama & Mate!</option>
                <option value="immortal">👑 The Immortal Game 1851 (Anderssen) - 23 lances, Triplo Sacrifício & Mate de Bispo!</option>
                <option value="legal">⚔️ Mate de Légal (1750) - 7 lances, Sacrifício de Dama & Triplo Ataque Menor!</option>
                <option value="scholar">⚡ Mate do Pastor (4 Lances) - Ataque veloz em f7</option>
                <option value="fools">⚡ Mate do Louco (2 Lances) - O mate mais rápido da história</option>
              </select>
            </div>
            <div class="border-t border-brand-border/60 pt-2">
              <label class="text-xs text-brand-400 font-bold block mb-1">♟️ Ou Cole o Código PGN da sua Partida (Chess.com / Lichess)</label>
              <textarea id="chess-pgn" rows="3" placeholder="Cole sua partida em PGN aqui... Ex: 1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 5. c3 Ba5 6. d4 ..." class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono"></textarea>
              <span class="text-[10px] text-slate-400 block mt-0.5">O estúdio reproduzirá automaticamente todos os lances do seu PGN no tabuleiro animado!</span>
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
                <option value="dvd">📀 Efeito DVD Bouncing (Quicando nas Bordas &amp; Cantos com Troca de Cor)</option>
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
              <option value="snake">🐍 Nokia 3310 Snake Game (Display LCD, Teclado &amp; Cobrinha em Grid)</option>
              <option value="pong">🏓 Atari 1972 Pong Arcade (Scanlines CRT, Linha Pontilhada &amp; Placar 7-Seg)</option>
              <option value="flappy">🐤 Terminal Flappy Bird 8-Bit (Canos Verdes, Pássaro 2-Frames &amp; Nuvens)</option>
              <option value="mario">🍄 Super Mario Bros NES (World 1-1 Runner &amp; Coin Jump)</option>
              <option value="space_invaders">👾 Space Invaders Arcade 1978 (Laser Cannon Defense)</option>
              <option value="pacman">ᗧ••• Pac-Man Terminal Maze 1980 (Chomp &amp; 4 Ghosts)</option>
              <option value="starfield">🌌 Starfield 3D (Hiperespaço Star Wars Warp 60fps)</option>
              <option value="cyberpunk_city">🌧️ Cyberpunk City (Chuva Noturna Neo-Tokyo em Kanji)</option>
              <option value="dvd">📀 DVD Bouncing Screensaver (Quicando nas Bordas &amp; Cantos)</option>
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

                              <!-- FX Mario options -->
          <!-- FX Snake Nokia options -->
          <div id="fx-opt-snake" class="flex flex-col gap-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Carcaça do Nokia</label>
                <select id="snake-casing" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="navy">🔵 Azul Marinho Original</option>
                  <option value="cyber_neon">🟣 Cyber Neon</option>
                  <option value="cherry_red">🔴 Cherry Red</option>
                  <option value="silver">⚪ Silver Grey</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Display LCD</label>
                <select id="snake-display" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="classic_lcd">🟢 LCD Esmeralda</option>
                  <option value="amber">🟠 Âmbar CRT</option>
                  <option value="cyber_cyan">🔵 Ciano Neon</option>
                  <option value="matrix">🟢 Terminal Verde</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Score Inicial</label>
                <input id="snake-score" type="number" value="420" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Velocidade</label>
                <select id="snake-speed" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="0.75">0.75x</option>
                  <option value="1.0" selected>1.0x (60fps)</option>
                  <option value="1.5">1.5x</option>
                </select>
              </div>
            </div>
          </div>

          <!-- FX Pong Arcade options -->
          <div id="fx-opt-pong" class="hidden flex flex-col gap-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Tema Arcade</label>
                <select id="pong-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="classic_green">🟢 Verde Arcade 1972</option>
                  <option value="b_and_w">⚪ P&amp;B Original</option>
                  <option value="cyber_neon">🟣 Cyberpunk Glow</option>
                  <option value="amber_crt">🟠 Âmbar CRT</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Velocidade</label>
                <select id="pong-speed" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="0.75">0.75x</option>
                  <option value="1.0" selected>1.0x</option>
                  <option value="1.5">1.5x</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Placar P1</label>
                <input id="pong-score1" type="number" value="7" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Placar P2</label>
                <input id="pong-score2" type="number" value="5" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
            </div>
          </div>

          <!-- FX Flappy Bird options -->
          <div id="fx-opt-flappy" class="hidden flex flex-col gap-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Paleta Visual</label>
                <select id="flappy-theme" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                  <option value="retro_arcade">🎮 Arcade Original</option>
                  <option value="terminal_green">🟢 Terminal Verde</option>
                  <option value="vaporwave">🌆 Vaporwave Sunset</option>
                  <option value="midnight">🌌 Midnight Cyberpunk</option>
                </select>
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Score</label>
                <input id="flappy-score" type="number" value="12" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">
              </div>
            </div>
          </div>

          <div id="fx-opt-mario" class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-400 block mb-1">Mundo (World)</label>
              <input id="mario-world" type="text" value="1-1" placeholder="1-1" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Pontuação</label>
              <input id="mario-score" type="number" value="2450" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
          </div>

          <!-- FX Space Invaders options -->
          <div id="fx-opt-invaders" class="hidden flex flex-col gap-2">
            <label class="text-xs text-slate-400 block mb-1">Score Inicial</label>
            <input id="invaders-score" type="number" value="1978" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <!-- FX Pacman options -->
          <div id="fx-opt-pacman" class="hidden flex flex-col gap-2">
            <label class="text-xs text-slate-400 block mb-1">Score / 1UP</label>
            <input id="pacman-score" type="number" value="333360" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <!-- FX Starfield options -->
          <div id="fx-opt-starfield" class="hidden flex flex-col gap-2">
            <label class="text-xs text-slate-400 block mb-1">Velocidade de Dobra (Warp Speed)</label>
            <select id="starfield-warp" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="0.75">Warp 5.0 (Cruzeiro Espacial)</option>
              <option value="1.0" selected>Warp 9.8 (Hiperespaço Standard)</option>
              <option value="1.5">Warp 12.0 (Velocidade da Luz)</option>
              <option value="2.0">Ludicrous Speed (Espaço Profundo)</option>
            </select>
          </div>

          <!-- FX Cyberpunk City options -->
          <div id="fx-opt-city" class="hidden flex flex-col gap-2">
            <label class="text-xs text-slate-400 block mb-1">Nome da Metrópole</label>
            <input id="city-name" type="text" value="NEO-TOKYO" placeholder="ex: NEO-TOKYO, CYBER-CITY" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <!-- FX DVD options -->
          <div id="fx-opt-dvd" class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-400 block mb-1">Texto do Logo</label>
              <input id="dvd-text" type="text" value="DVD" placeholder="ex: DVD, SEU_NOME" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Velocidade</label>
              <select id="dvd-speed" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="0.75">0.75x (Mais Lento)</option>
                <option value="1.0" selected>1.0x (Padrão Retrô)</option>
                <option value="1.5">1.5x (Rápido)</option>
                <option value="2.0">2.0x (Veloz)</option>
              </select>
            </div>
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
              <input id="qr-url" type="text" placeholder="https://github.com/seu-usuario" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Rótulo do Crachá</label>
                <input id="qr-label" type="text" value="DEV PROFILE" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
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
            <input id="fx-user" type="text" placeholder="ex: developer" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
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

        <!-- ================= TAB 7: TECH STACK & BADGES STUDIO ================= -->
        <div id="tab-badges" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🛡️ Tech Stack & Badges Studio</h2>
            <p class="text-xs text-slate-400 mt-0.5">Crie matrizes de tecnologias e badges estilizados para seu README</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Título do Banner</label>
            <input id="badge-title" type="text" value="TECH STACK & CORE ARSENAL" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Estilo Visual dos Badges</label>
            <select id="badge-style" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="neon">⚡ Cyberpunk Neon (Glow Colorido & Símbolos)</option>
              <option value="flat">🔵 Modern Flat Dark (Pills Minimalistas GitHub)</option>
              <option value="arcade">👾 Retro 8-Bit Arcade (Colchetes & Borda Pixel)</option>
            </select>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-xs text-slate-400">Presets de Tecnologias</label>
              <span class="text-[10px] text-slate-500">Clique para carregar</span>
            </div>
            <div class="grid grid-cols-4 gap-1.5 text-[11px] mb-2.5">
              <button type="button" onclick="loadTechPreset('fullstack')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">🌐 Fullstack</button>
              <button type="button" onclick="loadTechPreset('python_ai')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">🤖 Python & AI</button>
              <button type="button" onclick="loadTechPreset('devops')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">☁️ DevOps/Cloud</button>
              <button type="button" onclick="loadTechPreset('systems')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">⚡ Baixo Nível</button>
              <button type="button" onclick="loadTechPreset('mobile')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">📱 Mobile Dev</button>
              <button type="button" onclick="loadTechPreset('web3')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">💎 Web3 Crypto</button>
              <button type="button" onclick="loadTechPreset('gamedev')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">🎮 Game Dev</button>
              <button type="button" onclick="loadTechPreset('datascience')" class="px-2 py-1 rounded-lg bg-brand-dark hover:bg-sky-950/60 border border-brand-border hover:border-sky-500/50 text-slate-300 hover:text-white transition text-center font-medium">📊 Data Science</button>
            </div>

            <!-- Quick Add Chips Cloud -->
            <div class="mb-2 p-2 rounded-xl bg-brand-dark/50 border border-brand-border/60">
              <label class="text-[10px] uppercase font-bold tracking-wider text-sky-400 block mb-1.5 flex items-center justify-between">
                <span>⚡ Adicionar / Alternar Rápido (+/-):</span>
                <span class="text-[9px] text-slate-500 font-normal">Clique no chip para alternar</span>
              </label>
              <div class="flex flex-wrap gap-1 text-[10px]" id="quick-tech-chips">
                <button type="button" onclick="toggleTechChip('flutter')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Flutter</button>
                <button type="button" onclick="toggleTechChip('react_native')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ React Native</button>
                <button type="button" onclick="toggleTechChip('swift')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Swift</button>
                <button type="button" onclick="toggleTechChip('kotlin')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Kotlin</button>
                <button type="button" onclick="toggleTechChip('pytorch')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ PyTorch</button>
                <button type="button" onclick="toggleTechChip('langchain')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ LangChain</button>
                <button type="button" onclick="toggleTechChip('terraform')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Terraform</button>
                <button type="button" onclick="toggleTechChip('solidity')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Solidity</button>
                <button type="button" onclick="toggleTechChip('godot')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Godot</button>
                <button type="button" onclick="toggleTechChip('supabase')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Supabase</button>
                <button type="button" onclick="toggleTechChip('qdrant')" class="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-700 hover:border-sky-400 text-slate-300 hover:text-sky-300 transition">+ Qdrant</button>
              </div>
            </div>

            <!-- Custom Tech Input Form -->
            <div class="mb-2 p-2.5 rounded-xl bg-brand-dark/50 border border-brand-border/60">
              <label class="text-[10px] uppercase font-bold tracking-wider text-purple-400 block mb-1.5">
                ✨ Adicionar Tecnologia Personalizada
              </label>
              <div class="grid grid-cols-12 gap-1.5">
                <input id="custom-tech-cat" type="text" placeholder="Categoria (ex: Mobile, AI)" class="col-span-5 bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                <input id="custom-tech-name" type="text" placeholder="Nome da Ferramenta" class="col-span-4 bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                <button type="button" onclick="addCustomTech()" class="col-span-3 px-2 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-lg text-xs transition active:scale-95 shadow">
                  + Inserir
                </button>
              </div>
              <p class="text-[9.5px] text-slate-500 mt-1">Dica: Deixe a categoria vazia para auto-classificar, ou especifique para criar sua própria categoria!</p>
            </div>

            <label class="text-[11px] text-slate-400 block mb-1">Tecnologias selecionadas (separadas por vírgula):</label>
            <textarea id="badge-techs" rows="3" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs font-mono">python, typescript, rust, react, nextjs, fastapi, docker, postgresql, tailwind, linux, git</textarea>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">GitHub Username</label>
            <input id="badge-user" type="text" placeholder="ex: seu-usuario-github" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <div class="flex flex-col gap-2 pt-1">
            <button onclick="generateTechBadges()" class="w-full py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2 text-xs">
              <span>🛡️</span> <span>Gerar Banner de Badges (SVG)</span>
            </button>
            <button onclick="copyShieldsMarkdown()" class="w-full py-2 bg-brand-dark border border-brand-border hover:bg-brand-border text-slate-300 font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5">
              <span>📋</span> <span>Copiar Badges em Markdown (Shields.io)</span>
            </button>
          </div>
        </div>

        <!-- ================= TAB 8: MÚSICA & ATIVIDADE DEV ================= -->
        <div id="tab-activity" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-2">
            <h2 class="font-bold text-white text-base flex items-center gap-2">🎵 Dev Music & Atividade</h2>
            <p class="text-xs text-slate-400 mt-0.5">Cards do Spotify, métricas de linguagem e diagramas de arquitetura</p>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">Tipo de Card</label>
            <select id="act-widget" onchange="toggleActivityWidget()" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="music">🎵 Tocando Agora (Spotify / Cassette Player)</option>
              <option value="coding">📊 Métricas de Código (WakaTime & Streak Radar)</option>
              <option value="diagram">🗺️ Diagrama de Arquitetura (ASCII Flowchart)</option>
            </select>
          </div>

          <!-- MUSIC CONTROLS -->
          <div id="act-opt-music" class="flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-pink-400 flex items-center gap-1.5">
              <span>📻</span> <span>Opções de Música & Áudio</span>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Preset de Faixa Musical</label>
              <select id="music-preset" class="w-full bg-brand-dark border border-brand-border rounded-lg p-1.5 text-slate-200 text-xs">
                <option value="synthwave">🌆 Synthwave: HOME — Resonance</option>
                <option value="lofi">☕ Lofi Girl: Coffee Beats & Code</option>
                <option value="cyberpunk">🦾 Cyberpunk: Night City Wire</option>
                <option value="rock">🎸 Metal: Metallica — Master of Puppets</option>
                <option value="interstellar">🌌 Cinema: Hans Zimmer — Cornfield Chase</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Música (Opcional)</label>
                <input id="music-title" type="text" placeholder="Nome da faixa" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Artista (Opcional)</label>
                <input id="music-artist" type="text" placeholder="Artista / Banda" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
              </div>
            </div>
          </div>

          <!-- CODING STATS CONTROLS -->
          <div id="act-opt-coding" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <span>📊</span> <span>Métricas de Produtividade</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Horas Codadas</label>
                <input id="coding-hours" type="number" value="1480" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Dias de Streak 🔥</label>
                <input id="coding-streak" type="number" value="48" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
              </div>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Nível / Rank de Produtividade</label>
              <input id="coding-rank" type="text" value="S+ Tier (Cyber Architect)" class="w-full bg-brand-dark border border-brand-border rounded p-1.5 text-slate-200 text-xs">
            </div>
          </div>

          <!-- DIAGRAM CONTROLS -->
          <div id="act-opt-diagram" class="hidden flex flex-col gap-3 p-3 bg-brand-dark/60 rounded-xl border border-brand-border/60">
            <div class="text-[11px] font-bold uppercase tracking-wider text-amber-400 flex items-center justify-between">
              <span class="flex items-center gap-1.5"><span>🗺️</span> <span>Topologia de Arquitetura em Nuvem</span></span>
              <span class="text-[9.5px] px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 font-mono">ANIMATED BUS</span>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Topologia de Sistema</label>
              <select id="diagram-preset" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
                <option value="microservices">☁️ Nuvem Distribuída (Gateway + Microsserviços + Kafka + Postgres)</option>
                <option value="ai_agent">🤖 Agente de IA Autônomo & RAG (Prompt + Vector DB + LLM Swarm + Tools)</option>
                <option value="gitops">🚀 Pipeline GitOps Zero-Downtime (GitHub Actions + OCI + ArgoCD + K8s)</option>
                <option value="event_driven">⚡ Event-Driven CQRS & Real-time (Clients + NATS + EventStore + Redis)</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-slate-400 block mb-1">Título Personalizado (Opcional)</label>
              <input id="diagram-title" type="text" placeholder="ex: ARQUITETURA DE PRODUÇÃO E-COMMERCE" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
            </div>
          </div>

          <div>
            <label class="text-xs text-slate-400 block mb-1">GitHub Username</label>
            <input id="act-user" type="text" placeholder="ex: seu-usuario-github" class="w-full bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
          </div>

          <button onclick="generateActivityCard()" class="mt-2 w-full py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2 text-xs">
            <span>⚡</span> <span>Gerar Card de Atividade (SVG)</span>
          </button>
        </div>

        <!-- ================= TAB 8: CONSTRUTOR DE PERFIL & README ================= -->
        <div id="tab-builder" class="tab-content hidden flex flex-col gap-4">
          <div class="border-b border-brand-border pb-3 flex items-center justify-between gap-3">
            <div>
              <h2 class="text-base font-bold text-white flex items-center gap-2">
                <span class="text-brand-400">🚀</span> <span>Construtor de Perfil GitHub</span>
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Monte sua vitrine de perfil: lado a lado (50%), colunas, galerias e exporte tudo em 1 clique!</p>
            </div>
            <button type="button" onclick="openDeployInstructionsModal()" class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/40 hover:border-amber-400 text-amber-300 hover:text-white text-xs font-bold transition flex items-center gap-1.5 shadow-sm active:scale-95 shrink-0" title="Guia Passo a Passo: Como colocar na página inicial do seu GitHub">
              <span>📖</span> <span>Como Ativar no Perfil</span>
            </button>
          </div>

          <!-- Presets Rápidos de 1 Clique -->
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-300">Templates / Presets Rápidos de 1 Clique</label>
            <div class="grid grid-cols-2 gap-2 text-[11px]">
              <button type="button" onclick="applyReadmePreset('cyberpunk')" class="p-2.5 rounded-xl bg-brand-dark/80 hover:bg-brand-dark border border-cyan-500/40 text-left hover:border-cyan-400 transition shadow-sm group">
                <span class="font-bold text-cyan-400 block group-hover:underline">🌆 Cyberpunk 2077</span>
                <span class="text-slate-400 text-[10px] block mt-0.5">Banner 3D, Passaporte RPG, Cassete Synthwave, Badges &amp; Specs</span>
              </button>
              <button type="button" onclick="applyReadmePreset('matrix')" class="p-2.5 rounded-xl bg-brand-dark/80 hover:bg-brand-dark border border-emerald-500/40 text-left hover:border-emerald-400 transition shadow-sm group">
                <span class="font-bold text-emerald-400 block group-hover:underline">🟢 Matrix Hacker</span>
                <span class="text-slate-400 text-[10px] block mt-0.5">Chuva Katakana CMatrix, Neofetch MacOS, Stats &amp; Arquitetura</span>
              </button>
              <button type="button" onclick="applyReadmePreset('gamer')" class="p-2.5 rounded-xl bg-brand-dark/80 hover:bg-brand-dark border border-purple-500/40 text-left hover:border-purple-400 transition shadow-sm group">
                <span class="font-bold text-purple-400 block group-hover:underline">🕹️ Retrô Gamer 8-Bit</span>
                <span class="text-slate-400 text-[10px] block mt-0.5">Mario Runner, Dev Pet Tamagotchi, Space Invaders, Pokémon &amp; Pac-Man</span>
              </button>
              <button type="button" onclick="applyReadmePreset('minimal')" class="p-2.5 rounded-xl bg-brand-dark/80 hover:bg-brand-dark border border-amber-500/40 text-left hover:border-amber-400 transition shadow-sm group">
                <span class="font-bold text-amber-400 block group-hover:underline">⚡ Minimalista Dev</span>
                <span class="text-slate-400 text-[10px] block mt-0.5">Relógio TTY, Mapa de Metrô Git Subway, Tech Badges, Xadrez &amp; Stats</span>
              </button>
            </div>
          </div>

          <!-- Seções Ativas & Reordenação -->
          <div class="flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <label class="text-xs font-semibold text-slate-300">Seções do seu Perfil (Ordem no README)</label>
              <div class="flex items-center gap-2">
                <span class="text-[10px] text-slate-400 hidden sm:inline">⠿ Arraste para reordenar</span>
                <span class="text-[10px] text-brand-400 font-bold" id="builder-count-label">0 ativas</span>
              </div>
            </div>
            <div id="builder-sections-list" class="flex flex-col gap-2 max-h-[340px] overflow-y-auto pr-1">
              <!-- Rendered dynamically by JS -->
            </div>
          </div>

          <!-- Adicionar Novo Bloco -->
          <div class="flex gap-2 pt-1">
            <select id="builder-add-select" class="flex-1 bg-brand-dark border border-brand-border rounded-lg p-2 text-slate-200 text-xs">
              <option value="header">🌟 Banner 3D / Wordmark</option>
              <option value="badges">🛡️ Arsenal Tech Stack & Badges</option>
              <option value="heatmap">📊 Heatmap 3D de Commits</option>
              <option value="stats">📈 GitHub Stats Card</option>
              <option value="neofetch">💻 Card Neofetch Specs</option>
              <option value="pokemon">🎮 Card RPG Pokémon Holo</option>
              <option value="coding_stats">⚡ Radar de Produtividade & Streaks</option>
              <option value="music">🎵 Cassete Spotify Hi-Fi</option>
              <option value="chess">♟️ Xadrez Animado até Cheque-Mate</option>
              <option value="weather">🌦️ Previsão do Tempo em ASCII</option>
              <option value="diagram">📐 Diagrama de Topologia / Arquitetura</option>
              <option value="rpg">⚔️ Passaporte RPG do Desenvolvedor (Classes, HP/Mana &amp; Gear)</option>
              <option value="subway">🗺️ Mapa de Metrô dos Commits (Git Branch Subway)</option>
              <option value="pet">👾 Tamagotchi Dev Pet Virtual 1996</option>
              <option value="mario">🍄 Super Mario Bros NES World 1-1 Runner</option>
              <option value="invaders">👾 Space Invaders Arcade 1978</option>
              <option value="pacman">ᗧ••• Pac-Man Terminal Arcade</option>
              <option value="dvd">📀 DVD Bouncing Screensaver Retro</option>
              <option value="fortune">🥠 Biscoito da Sorte Hacker / Zen</option>
              <option value="custom_svg">🖼️ Imagem / GIF / SVG Personalizado (Upload)</option>
            </select>
            <button onclick="addBuilderBlock()" type="button" class="px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1 shrink-0">
              <span>➕</span> <span>Adicionar</span>
            </button>
            <label class="px-3 py-2 bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 hover:border-purple-500 text-purple-200 hover:text-white rounded-lg text-xs font-bold transition flex items-center gap-1 shrink-0 cursor-pointer" title="Anexar diretamente uma imagem PNG, JPG, GIF animado ou SVG no Perfil">
              <span>📎</span> <span>Anexar Imagem</span>
              <input type="file" accept="image/png,image/jpeg,image/gif,image/svg+xml,image/webp" class="hidden" onchange="handleDirectImageUploadToBuilder(event)">
            </label>
          </div>

          <!-- Botões de Ação Principal -->
          <div class="flex flex-col gap-2 pt-3 border-t border-brand-border">
            <button onclick="renderReadmePreview()" class="w-full py-2.5 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2 text-xs">
              <span>🔄</span> <span>Atualizar Pré-Visualização</span>
            </button>
            <div class="grid grid-cols-2 gap-2">
              <button onclick="downloadProfileZip()" class="py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-1.5 text-xs">
                <span>📦</span> <span>Baixar Repositório (.ZIP)</span>
              </button>
              <button onclick="copyReadmeMarkdown()" class="py-2.5 bg-brand-dark/90 hover:bg-brand-dark border border-brand-border text-slate-200 hover:text-white font-bold rounded-xl transition flex items-center justify-center gap-1.5 text-xs">
                <span>📋</span> <span>Copiar README.md</span>
              </button>
            </div>
            <button onclick="openDeployInstructionsModal()" type="button" class="text-center text-[11px] text-brand-400 hover:underline pt-1">
              📖 Como subir para o meu perfil no GitHub? (Passo a Passo)
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
          <span id="preview-tag" class="text-xs px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-300 font-mono font-medium border border-emerald-500/30 flex items-center gap-1.5 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>termart.svg</span>
          </span>
          <span id="preview-count-badge" class="hidden text-xs px-3 py-1 rounded-full bg-sky-500/15 text-sky-300 font-mono font-medium border border-sky-500/30">0 itens</span>
        </div>
        <div class="flex items-center gap-2">
          <button id="btn-global-anim" onclick="toggleGlobalAnimations()" class="text-xs px-3 py-1.5 rounded-xl border border-white/10 bg-[#0e1424] hover:bg-[#151f36] text-slate-300 font-medium transition flex items-center gap-1.5 shadow-sm active:scale-95" title="Ativar ou desativar todas as animações para economia de CPU">
            <span id="global-anim-icon">✨</span> <span id="global-anim-label">Animações: ON</span>
          </button>
          <button id="btn-download-zip" onclick="downloadAllAsZip()" class="hidden text-xs px-3.5 py-1.5 rounded-xl border border-purple-500/30 bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 font-medium transition flex items-center gap-1.5 shadow-lg shadow-purple-500/10 active:scale-95">
            <span>📦</span> <span>Baixar Todas (.ZIP)</span>
          </button>
          <button id="btn-download-gif" onclick="downloadGif()" class="text-xs px-3.5 py-1.5 rounded-xl border border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 font-medium transition flex items-center gap-1.5 shadow-md shadow-amber-500/10 active:scale-95" title="Exportar GIF animado em alta qualidade (FFmpeg)">
            <span>🎞️</span> <span>Baixar GIF</span>
          </button>
          <button id="btn-download-mp4" onclick="downloadMp4()" class="text-xs px-3.5 py-1.5 rounded-xl border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 font-medium transition flex items-center gap-1.5 shadow-md shadow-rose-500/10 active:scale-95" title="Exportar vídeo MP4 H.264 (FFmpeg)">
            <span>🎥</span> <span>Baixar MP4</span>
          </button>
          <button id="btn-download-single" onclick="downloadSvg()" class="text-xs px-3.5 py-1.5 rounded-xl border border-sky-500/30 bg-[#0e1424] hover:bg-sky-500/10 text-white font-medium transition flex items-center gap-1.5 shadow-sm active:scale-95" title="Baixar arquivo vetorial SVG">
            <span>⭳</span> <span>Baixar SVG</span>
          </button>
          <button id="btn-download-png" onclick="downloadPng()" class="text-xs px-3.5 py-1.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 font-medium transition flex items-center gap-1.5 shadow-md shadow-emerald-500/10 active:scale-95" title="Exportar arte em PNG de alta resolução (2x)">
            <span>🖼️</span> <span>Baixar PNG</span>
          </button>
          <button id="btn-pin-profile" onclick="pinCurrentToProfile()" class="text-xs px-3.5 py-1.5 rounded-xl border border-purple-500/30 bg-gradient-to-r from-purple-600/30 to-indigo-600/30 hover:from-purple-600/40 hover:to-indigo-600/40 text-purple-200 font-medium transition flex items-center gap-1.5 shadow-md shadow-purple-500/10 active:scale-95" title="Adicionar esta arte gerada diretamente ao seu perfil do GitHub">
            <span>📌</span> <span>Fixar no Perfil</span>
          </button>
        </div>
      </div>

      <!-- Preview Canvas -->
      <div id="canvas-wrapper" class="w-full min-h-[580px] p-8 rounded-3xl canvas-grid border border-white/10 flex flex-col items-center justify-center overflow-auto shadow-2xl relative backdrop-blur-md">
        <div id="svg-display" class="w-full flex items-center justify-center [&>svg]:max-w-full [&>svg]:h-auto">
          <div class="text-center text-slate-500">
            <p class="text-4xl mb-3 animate-pulse">⚡</p>
            <p>Selecione um motor e clique em Gerar para ver o resultado ao vivo!</p>
          </div>
        </div>

        <!-- Dedicated Builder Workspace -->
        <div id="builder-workspace" class="hidden w-full flex flex-col gap-4">
          <div class="flex items-center justify-between border-b border-brand-border pb-3">
            <div class="flex items-center gap-2 text-xs">
              <button onclick="switchBuilderView('visual')" id="btn-view-visual" class="px-3 py-1.5 rounded-lg bg-brand-600 text-white font-semibold transition">
                👁️ Preview do Perfil
              </button>
              <button onclick="switchBuilderView('code')" id="btn-view-code" class="px-3 py-1.5 rounded-lg bg-brand-dark/80 hover:bg-brand-dark text-slate-300 font-semibold transition">
                📝 Código README.md
              </button>
              <button onclick="switchBuilderView('tree')" id="btn-view-tree" class="px-3 py-1.5 rounded-lg bg-brand-dark/80 hover:bg-brand-dark text-slate-300 font-semibold transition">
                📁 Estrutura do Repositório
              </button>
            </div>
            <button onclick="downloadProfileZip()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1.5 shadow">
              <span>📦</span> <span>Baixar .ZIP</span>
            </button>
          </div>

          <!-- Visual Profile Preview -->
          <div id="builder-view-visual" class="w-full flex flex-col items-center gap-6 p-6 bg-[#0d1117] rounded-xl border border-brand-border/60 max-w-[860px] mx-auto shadow-inner">
            <div id="builder-visual-content" class="w-full flex flex-col items-center gap-5">
              <div class="text-slate-500 text-center py-10">Carregando preview do perfil...</div>
            </div>
          </div>

          <!-- Markdown Code Preview -->
          <div id="builder-view-code" class="hidden w-full flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <span class="text-xs text-slate-400 font-mono">README.md</span>
              <button onclick="copyReadmeMarkdown()" class="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
                <span>📋</span> <span>Copiar Markdown</span>
              </button>
            </div>
            <pre id="builder-markdown-code" class="w-full bg-brand-dark border border-brand-border rounded-xl p-4 text-xs font-mono text-slate-200 overflow-x-auto whitespace-pre-wrap max-h-[600px]"></pre>
          </div>

          <!-- Repository File Tree Preview -->
          <div id="builder-view-tree" class="hidden w-full flex flex-col gap-3">
            <div class="bg-[#0d1117] border border-brand-border/70 rounded-xl overflow-hidden font-mono text-xs">
              <div class="bg-brand-dark/90 px-4 py-2.5 border-b border-brand-border flex items-center justify-between text-slate-300 font-sans">
                <span class="flex items-center gap-2">
                  <span class="text-brand-400">📁</span>
                  <strong class="text-white" id="tree-repo-name">seu-usuario / seu-usuario</strong>
                  <span class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] border border-emerald-500/20">Public</span>
                </span>
                <span class="text-slate-500 text-[11px]" id="tree-files-count">0 arquivos gerados</span>
              </div>
              <div id="tree-files-list" class="divide-y divide-brand-border/30">
                <!-- Dynamically filled -->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Elegant Unobtrusive Sponsor / Ad Banner Container -->
    <div id="ad-container-footer" class="max-w-[1600px] w-full mx-auto px-6 py-4 mt-4">
      <div class="rounded-2xl border border-white/5 bg-[#0a0f1d]/70 backdrop-blur-md p-3.5 flex flex-col items-center justify-center min-h-[90px] text-center relative overflow-hidden shadow-lg shadow-black/20">
        <div class="flex items-center gap-2 mb-1.5">
          <span class="text-[9px] uppercase tracking-widest text-slate-500 font-semibold px-2 py-0.5 rounded bg-white/5 border border-white/5">Patrocinado • Mezzold TermArt</span>
        </div>
        <!-- Google AdSense Responsive Unit -->
        <div class="w-full flex items-center justify-center overflow-hidden">
          <ins class="adsbygoogle"
               style="display:block; min-height: 90px; width: 100%;"
               data-ad-client="ca-pub-8865509480539792"
               data-ad-slot="auto"
               data-ad-format="auto"
               data-full-width-responsive="true"></ins>
          <script>
               (adsbygoogle = window.adsbygoogle || []).push({});
          </script>
        </div>
      </div>
    </div>
  </main>

  <!-- Floating Toast Notification -->
  <div id="toast" class="fixed bottom-6 right-6 z-50 transform translate-y-20 opacity-0 transition-all duration-300 pointer-events-none px-4 py-2.5 rounded-xl bg-brand-dark/95 border border-brand-500 shadow-2xl text-xs font-semibold text-white flex items-center gap-2">
    <span id="toast-msg">Mensagem</span>
  </div>

  <!-- MODAL DE CONFIGURAÇÃO DE BLOCO DO PERFIL -->
  <div id="modal-block-config" class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-xl hidden transition-all p-4">
    <div class="bg-[#0e1424] border border-white/10 rounded-3xl p-6 max-w-lg w-full shadow-2xl flex flex-col gap-4 relative animate-fade-in">
      <div class="flex items-center justify-between border-b border-white/10 pb-3">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl" id="cfg-block-icon">⚙️</span>
          <div>
            <h3 class="text-base font-bold text-white tracking-wide" id="cfg-block-title">Configurar Bloco</h3>
            <p class="text-xs text-slate-400" id="cfg-block-subtitle">Personalize os detalhes e parâmetros desta seção</p>
          </div>
        </div>
        <button onclick="closeBlockConfigModal()" class="text-slate-400 hover:text-white text-lg p-1.5 rounded-xl hover:bg-white/5 transition">✕</button>
      </div>

      <!-- Dynamic Form Container -->
      <div id="cfg-block-form" class="flex flex-col gap-3 text-xs">
        <!-- Injected dynamically by JS based on block type -->
      </div>

      <div class="flex gap-2.5 pt-3 border-t border-white/10">
        <button onclick="saveBlockConfig()" class="flex-1 py-2.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-bold rounded-xl transition shadow-lg flex items-center justify-center gap-2 text-xs active:scale-95">
          <span>💾</span> <span>Salvar &amp; Atualizar Preview</span>
        </button>
        <button onclick="closeBlockConfigModal()" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-xl transition active:scale-95">
          Cancelar
        </button>
      </div>
    </div>
  </div>

  <!-- INSTRUÇÕES DE DEPLOY GITHUB MODAL COMPLETO -->
  <div id="modal-deploy-instructions" class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-xl hidden transition-all p-4">
    <div class="bg-[#0e1424] border border-white/10 rounded-3xl p-6 max-w-2xl w-full shadow-2xl flex flex-col gap-4 relative animate-fade-in max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b border-white/10 pb-3">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">📖</span>
          <div>
            <h3 class="text-base font-bold text-white tracking-wide">Como Ativar na Primeira Página do seu GitHub</h3>
            <p class="text-xs text-slate-400">Tutorial Completo: Faça seu perfil virar uma vitrine profissional de impacto</p>
          </div>
        </div>
        <button onclick="closeDeployInstructionsModal()" class="text-slate-400 hover:text-white text-lg p-1.5 rounded-xl hover:bg-white/5 transition">✕</button>
      </div>

      <div class="flex flex-col gap-3.5 text-xs text-slate-300">
        <!-- Passo 1 -->
        <div class="flex gap-3.5 items-start bg-slate-900/80 p-4 rounded-2xl border border-sky-500/20 shadow-sm">
          <span class="w-7 h-7 rounded-xl bg-sky-600 text-white flex items-center justify-center font-black text-sm shrink-0 shadow-md shadow-sky-600/30">1</span>
          <div class="flex flex-col gap-1">
            <strong class="text-white text-sm">Crie o Repositório Especial Secreto do GitHub</strong>
            <p class="text-slate-400">O GitHub possui uma funcionalidade especial: quando você cria um repositório com <strong>o mesmo nome do seu usuário</strong> (ex: <code class="text-sky-300 bg-black/50 px-1.5 py-0.5 rounded font-mono" id="deploy-modal-user">seu-usuario/seu-usuario</code>), o arquivo <code>README.md</code> dele vira automaticamente a apresentação oficial da sua homepage!</p>
            <div class="mt-1 flex items-center gap-2">
              <a href="https://github.com/new" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold text-[11px] transition shadow">
                <span>Criar Repositório no GitHub</span> <span class="text-sky-200">↗</span>
              </a>
              <span class="text-[11px] text-amber-400/90 font-medium">⚠️ Deve ser marcado como <strong>Public</strong>!</span>
            </div>
          </div>
        </div>

        <!-- Passo 2 -->
        <div class="flex gap-3.5 items-start bg-slate-900/80 p-4 rounded-2xl border border-purple-500/20 shadow-sm">
          <span class="w-7 h-7 rounded-xl bg-purple-600 text-white flex items-center justify-center font-black text-sm shrink-0 shadow-md shadow-purple-600/30">2</span>
          <div class="flex flex-col gap-1">
            <strong class="text-white text-sm">Exporte o Pacote Completo (.ZIP) no TermArt</strong>
            <p class="text-slate-400">Personalize a ordem e os formatos dos blocos na aba ao lado (use o botão <span class="text-sky-300 font-mono font-bold bg-slate-800 px-1.5 py-0.5 rounded">50% ⇋</span> para colocar cards lado a lado!). Em seguida, clique no botão <span class="text-emerald-400 font-bold">📦 Baixar Repositório (.ZIP)</span>.</p>
            <div class="p-2 rounded-lg bg-black/40 border border-white/5 text-[11px] text-slate-400">
              <span class="text-slate-300 font-semibold">O ZIP já inclui tudo pronto:</span>
              <ul class="list-disc list-inside mt-1 text-slate-400 space-y-0.5">
                <li><code>README.md</code> com código responsivo e centralizado</li>
                <li>Todos os arquivos <code>.svg</code> gerados em alta fidelidade</li>
                <li><code>.github/workflows/refresh-profile.yml</code> (GitHub Action de sincronização)</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Passo 3 -->
        <div class="flex gap-3.5 items-start bg-slate-900/80 p-4 rounded-2xl border border-emerald-500/20 shadow-sm">
          <span class="w-7 h-7 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-black text-sm shrink-0 shadow-md shadow-emerald-600/30">3</span>
          <div class="flex flex-col gap-1">
            <strong class="text-white text-sm">Publique os Arquivos no Repositório</strong>
            <p class="text-slate-400">Você pode publicar de duas maneiras muito simples:</p>
            <div class="grid grid-cols-2 gap-2 mt-1">
              <div class="p-2.5 rounded-xl bg-black/40 border border-white/5">
                <span class="font-bold text-sky-400 block mb-1">Método A: Via Navegador (Sem código)</span>
                <span class="text-[10px] text-slate-400">Descompacte o ZIP. No GitHub, clique em <strong>Add file</strong> → <strong>Upload files</strong>, arraste os arquivos e clique em <strong>Commit changes</strong>.</span>
              </div>
              <div class="p-2.5 rounded-xl bg-black/40 border border-white/5">
                <span class="font-bold text-purple-400 block mb-1">Método B: Via Terminal Git</span>
                <pre class="text-[9.5px] font-mono text-emerald-400 bg-black/60 p-1.5 rounded overflow-x-auto select-all">git clone https://github.com/USER/USER.git
cp -r /pasta-extraida/* USER/
cd USER && git add -A && git commit -m "feat: profile art" && git push</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- Passo 4 (Dicas Pro) -->
        <div class="flex gap-3.5 items-start bg-slate-900/80 p-4 rounded-2xl border border-amber-500/20 shadow-sm">
          <span class="w-7 h-7 rounded-xl bg-amber-600 text-white flex items-center justify-center font-black text-sm shrink-0 shadow-md shadow-amber-600/30">✨</span>
          <div class="flex flex-col gap-1">
            <strong class="text-white text-sm">Dicas Pro de Layout do Mezzold TermArt</strong>
            <ul class="list-disc list-inside text-slate-400 space-y-1 text-[11px]">
              <li><strong>Lado a Lado (50% / 50%):</strong> Clique no botão de largura em 2 blocos consecutivos para deixá-los com <code class="text-sky-300">50% ⇋</code>. O README os agrupa automaticamente na mesma linha!</li>
              <li><strong>Moldura de Galeria 2x2:</strong> No ⚙️ de qualquer card, escolha <em>"🖼️ Moldura de Galeria"</em> para renderizar com cabeçalhos elegantes.</li>
              <li><strong>Acervo Colapsável:</strong> Ative <em>"📁 Colapsável (&lt;details&gt;)"</em> para criar gavetas retráteis que deixam o perfil limpo e interativo.</li>
              <li><strong>Prompt de Terminal:</strong> Adicione comandos como <code class="text-emerald-400">usuario@github ~ $ ./gallery.sh</code> no topo de qualquer seção.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="flex justify-between items-center pt-2 border-t border-white/10">
        <span class="text-[11px] text-slate-500">Pronto para transformar seu perfil no GitHub?</span>
        <button onclick="closeDeployInstructionsModal()" class="px-5 py-2.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-sky-600/20 active:scale-95">
          Entendi, vamos criar!
        </button>
      </div>
    </div>
  </div>

  <!-- PERFIL DEV & CONFIGURAÇÃO INICIAL MODAL -->
  <div id="modal-dev-profile" class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-xl hidden transition-all p-4">
    <div class="bg-[#0e1424] border border-white/10 rounded-3xl p-6 max-w-lg w-full shadow-2xl flex flex-col gap-4 relative animate-fade-in">
      <div class="flex items-center justify-between border-b border-brand-border pb-3">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">⚡</span>
          <div>
            <h3 class="text-base font-bold text-white tracking-wide">Configuração do Perfil Dev</h3>
            <p class="text-xs text-slate-400">Personalize seu estúdio com seu GitHub e informações</p>
          </div>
        </div>
        <button onclick="closeConfigModal()" class="text-slate-400 hover:text-white text-lg p-1.5 rounded-lg hover:bg-brand-dark transition">✕</button>
      </div>

      <!-- GitHub Handle with auto-fetch -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-semibold text-slate-300 flex items-center justify-between">
          <span>GitHub Username ou Link do Perfil</span>
          <span class="text-[10px] text-brand-400 font-normal">Pressione Enter ou clique em Puxar Dados</span>
        </label>
        <div class="flex gap-2">
          <div class="relative flex-1">
            <span class="absolute left-3 top-2.5 text-slate-500 text-xs">github.com/</span>
            <input id="cfg-github" type="text" placeholder="seu-usuario" class="w-full pl-24 pr-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs focus:border-brand-500 outline-none" onkeyup="if(event.key==='Enter') fetchGithubData()">
          </div>
          <button onclick="fetchGithubData()" id="btn-fetch-gh" class="px-3.5 py-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1.5 shrink-0 shadow">
            <span>🔄</span> <span>Puxar Dados</span>
          </button>
        </div>
        <span id="cfg-gh-status" class="text-[11px] text-slate-400"></span>
      </div>

      <!-- Display Name / Signature -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-semibold text-slate-300">Nome de Exibição / Assinatura de Terminal</label>
        <input id="cfg-name" type="text" placeholder="ex: Seu Nome ou Nickname" class="w-full p-2.5 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs focus:border-brand-500 outline-none">
      </div>

      <!-- City for Weather Widget -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-semibold text-slate-300">Cidade / Localização (Para Weather & Perfil)</label>
        <input id="cfg-city" type="text" placeholder="ex: São Paulo, Brazil" class="w-full p-2.5 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs focus:border-brand-500 outline-none">
      </div>

      <!-- Tech Role / Bio -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-semibold text-slate-300">Cargo / Bio Rápida (Opcional)</label>
        <input id="cfg-role" type="text" placeholder="ex: Full-Stack Engineer / DevOps" class="w-full p-2.5 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs focus:border-brand-500 outline-none">
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2.5 pt-2">
        <button onclick="saveDevProfile()" class="flex-1 py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl transition shadow-lg flex items-center justify-center gap-2 text-xs">
          <span>💾</span> <span>Salvar & Aplicar no Studio</span>
        </button>
        <button onclick="closeConfigModal()" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-xl transition">
          Fechar
        </button>
      </div>
    </div>
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


    // ==========================================
    // WEB AUDIO API NATIVE CHIPTUNE SYNTHESIZER
    // ==========================================
    let audioFxEnabled = localStorage.getItem('termart_sound_enabled') !== 'false';
    let audioCtx = null;

    function getAudioContext() {
      try {
        if (!audioCtx) {
          const AudioContext = window.AudioContext || window.webkitAudioContext;
          if (AudioContext) audioCtx = new AudioContext();
        }
        if (audioCtx && audioCtx.state === 'suspended') {
          audioCtx.resume();
        }
      } catch (e) {}
      return audioCtx;
    }

    // Auto-unlock Web Audio on any user gesture
    document.addEventListener('click', () => {
      try {
        const ctx = getAudioContext();
        if (ctx && ctx.state === 'suspended') ctx.resume();
      } catch (e) {}
    }, { passive: true });

    function playSwitchSound() {
      if (!audioFxEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(640, now);
        osc.frequency.exponentialRampToValueAtTime(180, now + 0.05);
        gain.gain.setValueAtTime(0.20, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.06);
      } catch (e) {}
    }

    function playMarioCoinSound() {
      if (!audioFxEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;
        // Note 1: B5 (987.77 Hz)
        const osc1 = ctx.createOscillator();
        const gain1 = ctx.createGain();
        osc1.type = 'square';
        osc1.frequency.setValueAtTime(987.77, now);
        gain1.gain.setValueAtTime(0.30, now);
        gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.09);
        osc1.connect(gain1);
        gain1.connect(ctx.destination);
        osc1.start(now);
        osc1.stop(now + 0.10);

        // Note 2: E6 (1318.51 Hz)
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.type = 'square';
        osc2.frequency.setValueAtTime(1318.51, now + 0.08);
        gain2.gain.setValueAtTime(0.35, now + 0.08);
        gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.42);
        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        osc2.start(now + 0.08);
        osc2.stop(now + 0.45);
      } catch (e) {}
    }

    function playGameBoyBeep() {
      if (!audioFxEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.setValueAtTime(1046.50, now + 0.06); // C6
        gain.gain.setValueAtTime(0.28, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.30);
      } catch (e) {}
    }

    function toggleAudioFx() {
      audioFxEnabled = !audioFxEnabled;
      localStorage.setItem('termart_sound_enabled', audioFxEnabled ? 'true' : 'false');
      updateSoundButtonUI();
      if (audioFxEnabled) {
        playMarioCoinSound();
      }
    }

    function updateSoundButtonUI() {
      const icon = document.getElementById('sound-icon');
      const label = document.getElementById('sound-label');
      if (icon && label) {
        icon.innerText = audioFxEnabled ? '🔊' : '🔇';
        label.innerText = audioFxEnabled ? 'Som: ON' : 'Som: MUDO';
      }
    }

    function switchTab(tabId) {
      if (typeof playSwitchSound === 'function') playSwitchSound();
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('bg-brand-600', 'text-white');
        el.classList.add('text-slate-400');
      });
      document.getElementById(`tab-${tabId}`).classList.remove('hidden');
      document.getElementById(`btn-${tabId}`).classList.add('bg-brand-600', 'text-white');
      document.getElementById(`btn-${tabId}`).classList.remove('text-slate-400');

      const svgDisp = document.getElementById('svg-display');
      const bldDisp = document.getElementById('builder-workspace');
      if (tabId === 'builder') {
        if (svgDisp) svgDisp.classList.add('hidden');
        if (bldDisp) bldDisp.classList.remove('hidden');
        renderBuilderTab();
      } else {
        if (svgDisp) svgDisp.classList.remove('hidden');
        if (bldDisp) bldDisp.classList.add('hidden');
      }
    }

    function toggleImageEngine() {
      const eng = document.getElementById('img-engine').value;
      document.getElementById('rgb-options').classList.toggle('hidden', !['rgb_ascii', 'signature', 'drawille', 'jp2a'].includes(eng));
      document.getElementById('chafa-options').classList.toggle('hidden', eng !== 'chafa');
      document.getElementById('sig-options').classList.toggle('hidden', eng !== 'signature');
    }

    function toggleFxEngine() {
      const fx = document.getElementById('fx-engine').value;
      const setH = (id, hide) => { const el = document.getElementById(id); if (el) el.classList.toggle('hidden', hide); };
      setH('fx-opt-snake', fx !== 'snake');
      setH('fx-opt-pong', fx !== 'pong');
      setH('fx-opt-flappy', fx !== 'flappy');
      setH('fx-opt-mario', fx !== 'mario');
      setH('fx-opt-invaders', fx !== 'space_invaders');
      setH('fx-opt-pacman', fx !== 'pacman');
      setH('fx-opt-starfield', fx !== 'starfield');
      setH('fx-opt-city', fx !== 'cyberpunk_city');
      const dvdEl = document.getElementById('fx-opt-dvd'); if (dvdEl) dvdEl.classList.toggle('hidden', fx !== 'dvd');
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
                <button onclick="downloadSingleBatchSvg(${idx})" class="px-2.5 py-1 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition shadow" title="Baixar SVG">
                  <span>⭳</span> <span>SVG</span>
                </button>
                <button onclick="downloadSingleBatchPng(${idx})" class="px-2.5 py-1 bg-emerald-600/30 hover:bg-emerald-600/50 border border-emerald-500/40 text-emerald-300 rounded-lg text-xs font-semibold flex items-center gap-1 transition shadow" title="Baixar PNG em Alta Resolução">
                  <span>🖼️</span> <span>PNG</span>
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
      recommended: ['chafa', 'rgb_ascii', 'palette_swap', 'drawille', 'dither'],
      all: ['chafa', 'rgb_ascii', 'palette_swap', 'drawille', 'dither', 'jp2a', 'halftone', 'edge_art', 'glitch', 'pixel_mosaic', 'rainbow_wave', 'portrait', 'signature']
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
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
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
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
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
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
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
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
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
      if (typeof playSwitchSound === 'function') playSwitchSound();
      const w = document.getElementById('profile-widget').value;
      const setH = (id, show) => { const el = document.getElementById(id); if (el) el.classList.toggle('hidden', !show); };
      setH('profile-opt-btop', w === 'btop_monitor');
      setH('profile-opt-cli', w === 'cli_session');
      setH('profile-opt-gitgraph', w === 'git_graph');
      setH('profile-opt-cyberid', w === 'cyber_id');
      setH('profile-opt-achievement', w === 'achievement');
      setH('profile-opt-skilltree', w === 'skill_tree');
      setH('profile-opt-rpg', w === 'rpg_sheet');
      setH('profile-opt-subway', w === 'git_subway');
      setH('profile-opt-pet', w === 'dev_pet');
      setH('profile-opt-pokemon', w === 'pokemon');
      setH('profile-opt-weather', w === 'weather');
      setH('profile-opt-clock', w === 'clock');
      setH('profile-opt-chess', w === 'chess');
    }

    function setWeatherCity(c) {
      const el = document.getElementById('weather-city');
      if (el) el.value = c;
    }

    async function generateProfile() {
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
      const widget = document.getElementById('profile-widget').value;
      const user = document.getElementById('profile-user').value || 'developer';
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Consultando dados em tempo real...</div>';

      let url = `/api/render/${widget}?username=${encodeURIComponent(user)}`;

      if (widget === 'btop_monitor') {
        const theme = document.getElementById('btop-theme') ? document.getElementById('btop-theme').value : 'catppuccin';
        const uptime = document.getElementById('btop-uptime') ? document.getElementById('btop-uptime').value : '42 DAYS, 13:37:00';
        url += `&theme=${encodeURIComponent(theme)}&uptime=${encodeURIComponent(uptime)}`;
      } else if (widget === 'cli_session') {
        const theme = document.getElementById('cli-theme') ? document.getElementById('cli-theme').value : 'ghostty';
        const ttl = document.getElementById('cli-title') ? document.getElementById('cli-title').value : `${user}@terminal: ~`;
        url += `&theme=${encodeURIComponent(theme)}&terminal_title=${encodeURIComponent(ttl)}`;
      } else if (widget === 'git_graph') {
        const theme = document.getElementById('gitgraph-theme') ? document.getElementById('gitgraph-theme').value : 'neon_cyber';
        const repo = document.getElementById('gitgraph-repo') ? document.getElementById('gitgraph-repo').value : `${user}/core-engine`;
        url += `&theme=${encodeURIComponent(theme)}&repo_name=${encodeURIComponent(repo)}`;
      } else if (widget === 'cyber_id') {
        const theme = document.getElementById('cyberid-theme') ? document.getElementById('cyberid-theme').value : 'arasaka_red';
        const clr = document.getElementById('cyberid-clearance') ? document.getElementById('cyberid-clearance').value : 'LEVEL 5 - ROOT';
        const role = document.getElementById('cyberid-role') ? document.getElementById('cyberid-role').value : 'Senior Lead Architect';
        const dept = document.getElementById('cyberid-dept') ? document.getElementById('cyberid-dept').value : 'Cyber Defense & Cloud Infra';
        url += `&theme=${encodeURIComponent(theme)}&clearance_level=${encodeURIComponent(clr)}&role=${encodeURIComponent(role)}&department=${encodeURIComponent(dept)}&name=${encodeURIComponent(user)}`;
      } else if (widget === 'achievement') {
        const plat = document.getElementById('ach-platform') ? document.getElementById('ach-platform').value : 'xbox';
        const pts = document.getElementById('ach-points') ? document.getElementById('ach-points').value : 100;
        const ttl = document.getElementById('ach-title') ? document.getElementById('ach-title').value : 'LENDÁRIO CODE ARCHITECT';
        const desc = document.getElementById('ach-desc') ? document.getElementById('ach-desc').value : 'Deployou 1.000 microsserviços em produção numa sexta-feira sem quebrar';
        url += `&platform=${encodeURIComponent(plat)}&theme=${encodeURIComponent(plat)}&points=${encodeURIComponent(pts)}&title=${encodeURIComponent(ttl)}&description=${encodeURIComponent(desc)}`;
      } else if (widget === 'skill_tree') {
        const theme = document.getElementById('skill-theme') ? document.getElementById('skill-theme').value : 'cyber_constellation';
        const focus = document.getElementById('skill-focus') ? document.getElementById('skill-focus').value : 'Fullstack / Cloud / AI Architect';
        url += `&theme=${encodeURIComponent(theme)}&focus=${encodeURIComponent(focus)}`;
      } else if (widget === 'rpg_sheet') {
        const cls = document.getElementById('rpg-class') ? document.getElementById('rpg-class').value : 'alchemist';
        const lvl = document.getElementById('rpg-level') ? document.getElementById('rpg-level').value : 85;
        const name = document.getElementById('rpg-name') ? document.getElementById('rpg-name').value : user;
        const hp = document.getElementById('rpg-hp') ? document.getElementById('rpg-hp').value : 96;
        const mana = document.getElementById('rpg-mana') ? document.getElementById('rpg-mana').value : 91;
        const stam = document.getElementById('rpg-stamina') ? document.getElementById('rpg-stamina').value : 98;
        url += `&cls=${encodeURIComponent(cls)}&level=${encodeURIComponent(lvl)}&name=${encodeURIComponent(name)}&hp=${encodeURIComponent(hp)}&mana=${encodeURIComponent(mana)}&stamina=${encodeURIComponent(stam)}`;
      } else if (widget === 'git_subway') {
        const repo = document.getElementById('subway-repo') ? document.getElementById('subway-repo').value : 'core-platform';
        url += `&repo=${encodeURIComponent(repo)}`;
      } else if (widget === 'dev_pet') {
        const type = document.getElementById('pet-type') ? document.getElementById('pet-type').value : 'mametchi';
        const name = document.getElementById('pet-name') ? document.getElementById('pet-name').value : 'KERNEL';
        const hap = document.getElementById('pet-happiness') ? document.getElementById('pet-happiness').value : 98;
        const cof = document.getElementById('pet-coffee') ? document.getElementById('pet-coffee').value : 100;
        const style = document.getElementById('pet-casing-style') ? document.getElementById('pet-casing-style').value : 'egg';
        const color = document.getElementById('pet-casing-color') ? document.getElementById('pet-casing-color').value : 'cyber_blue';
        url += `&type=${encodeURIComponent(type)}&name=${encodeURIComponent(name)}&happiness=${encodeURIComponent(hap)}&coffee_level=${encodeURIComponent(cof)}&casing_style=${encodeURIComponent(style)}&casing_color=${encodeURIComponent(color)}`;
      } else if (widget === 'pokemon') {
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
        const pgnVal = document.getElementById('chess-pgn') ? document.getElementById('chess-pgn').value.trim() : '';
        url += `&match=${encodeURIComponent(match)}&animated=${anim}&speed=${encodeURIComponent(speed)}`;
        if (pgnVal) {
          url += `&pgn=${encodeURIComponent(pgnVal)}`;
        }
      }

      let res;
      if (widget === 'rpg_sheet' && currentRpgAvatarDataUrl) {
        res = await fetch('/api/render/rpg_sheet_custom', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cls: document.getElementById('rpg-class') ? document.getElementById('rpg-class').value : 'alchemist',
            level: document.getElementById('rpg-level') ? document.getElementById('rpg-level').value : 85,
            name: document.getElementById('rpg-name') ? document.getElementById('rpg-name').value : user,
            hp: document.getElementById('rpg-hp') ? document.getElementById('rpg-hp').value : 96,
            mana: document.getElementById('rpg-mana') ? document.getElementById('rpg-mana').value : 91,
            stamina: document.getElementById('rpg-stamina') ? document.getElementById('rpg-stamina').value : 98,
            username: user,
            custom_avatar: currentRpgAvatarDataUrl
          })
        });
      } else {
        res = await fetch(url);
      }
      const svg = await res.text();
      setPreview(svg, `${widget}.svg`);
    }

    // RPG Sheet Custom Avatar (PNG, JPG, GIF Animado, SVG)
    let currentRpgAvatarDataUrl = null;

    function handleRpgAvatarUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      const isSvg = file.type === 'image/svg+xml' || file.name.toLowerCase().endsWith('.svg');
      const reader = new FileReader();
      reader.onload = function(evt) {
        const raw = evt.target.result;
        currentRpgAvatarDataUrl = raw;
        const box = document.getElementById('rpg-avatar-preview-box');
        const img = document.getElementById('rpg-avatar-preview-img');
        const nameEl = document.getElementById('rpg-avatar-preview-name');
        const sizeEl = document.getElementById('rpg-avatar-preview-size');
        const clearBtn = document.getElementById('btn-rpg-avatar-clear');

        if (box) {
          box.classList.remove('hidden');
          box.classList.add('flex');
        }
        if (img) img.src = isSvg ? 'data:image/svg+xml;utf8,' + encodeURIComponent(raw) : raw;
        if (nameEl) nameEl.innerText = file.name;
        if (sizeEl) sizeEl.innerText = `${Math.round(file.size / 1024)} KB • Base64 Embutido`;
        if (clearBtn) clearBtn.classList.remove('hidden');

        showToast(`✓ Avatar "${file.name}" anexado! Gerando passaporte...`);
        generateProfile();
      };

      if (isSvg) {
        reader.readAsText(file);
      } else {
        reader.readAsDataURL(file);
      }
    }

    function clearRpgAvatar() {
      currentRpgAvatarDataUrl = null;
      const box = document.getElementById('rpg-avatar-preview-box');
      const clearBtn = document.getElementById('btn-rpg-avatar-clear');
      const input = document.getElementById('rpg-avatar-input');
      if (box) {
        box.classList.add('hidden');
        box.classList.remove('flex');
      }
      if (clearBtn) clearBtn.classList.add('hidden');
      if (input) input.value = '';
      showToast("Avatar restaurado para a ilustração padrão da classe!");
      generateProfile();
    }

    function handleDirectImageUploadToBuilder(e) {
      const file = e.target.files[0];
      if (!file) return;
      const isSvg = file.type === 'image/svg+xml' || file.name.toLowerCase().endsWith('.svg');
      const reader = new FileReader();
      reader.onload = function(evt) {
        const raw = evt.target.result;
        const blockId = 'custom_' + Date.now();
        const baseName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
        let svgPayload = '';
        if (isSvg && typeof raw === 'string' && raw.trim().startsWith('<svg')) {
          svgPayload = raw;
        } else {
          svgPayload = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 800 450" width="100%" height="100%">
  <image href="${raw}" xlink:href="${raw}" x="0" y="0" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"/>
</svg>`;
        }

        const newBlock = {
          id: blockId,
          type: 'custom_svg',
          title: `Arte: ${file.name.replace(/\.[^/.]+$/, "")}`,
          file: baseName.endsWith('.svg') ? baseName : `${baseName}.svg`,
          icon: '🖼️',
          enabled: true,
          width: '100%',
          layout_mode: 'inline',
          terminal_prompt: '',
          details_summary: '',
          svg_data: svgPayload,
          preview_url: `/api/builder/custom_svg/${blockId}`,
          params: { custom_avatar: raw }
        };

        builderSections.push(newBlock);
        saveStoredBuilderSections(builderSections);
        renderReadmePreview();
        showToast(`✓ Imagem "${file.name}" anexada com sucesso ao Perfil!`, 3000);
      };

      if (isSvg) {
        reader.readAsText(file);
      } else {
        reader.readAsDataURL(file);
      }
      e.target.value = '';
    }

    window._modalRpgCustomAvatar = undefined;
    function handleModalRpgAvatarUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      const isSvg = file.type === 'image/svg+xml' || file.name.toLowerCase().endsWith('.svg');
      const reader = new FileReader();
      reader.onload = function(evt) {
        const raw = evt.target.result;
        window._modalRpgCustomAvatar = raw;
        const previewBox = document.getElementById('cfg-modal-rpg-preview-box');
        const previewImg = document.getElementById('cfg-modal-rpg-preview-img');
        const clearBtn = document.getElementById('btn-modal-rpg-avatar-clear');
        if (previewBox) {
          previewBox.classList.remove('hidden');
          previewBox.classList.add('flex');
        }
        if (previewImg) previewImg.src = isSvg ? 'data:image/svg+xml;utf8,' + encodeURIComponent(raw) : raw;
        if (clearBtn) clearBtn.classList.remove('hidden');
        showToast(`✓ Avatar "${file.name}" selecionado!`);
      };
      if (isSvg) {
        reader.readAsText(file);
      } else {
        reader.readAsDataURL(file);
      }
    }

    function clearModalRpgAvatar() {
      window._modalRpgCustomAvatar = null;
      const previewBox = document.getElementById('cfg-modal-rpg-preview-box');
      const clearBtn = document.getElementById('btn-modal-rpg-avatar-clear');
      if (previewBox) {
        previewBox.classList.add('hidden');
        previewBox.classList.remove('flex');
      }
      if (clearBtn) clearBtn.classList.add('hidden');
      showToast("Avatar restaurado para o padrão da classe!");
    }

    const TECH_PRESETS = {
      fullstack: 'typescript, javascript, react, nextjs, nodejs, express, tailwind, postgresql, docker, git',
      python_ai: 'python, fastapi, pytorch, langchain, openai, postgresql, redis, docker, linux, git',
      devops: 'docker, kubernetes, aws, terraform, ansible, linux, nginx, prometheus, grafana, git',
      systems: 'rust, go, cpp, c, csharp, linux, git, docker, sqlite, neovim',
      mobile: 'flutter, dart, react_native, typescript, swift, kotlin, android, ios',
      web3: 'solidity, ethereum, typescript, rust, react, nextjs, tailwind, nodejs',
      gamedev: 'godot, csharp, cpp, rust, python, lua, unity, git',
      datascience: 'python, pandas, numpy, scikit_learn, pytorch, spark, sql, postgresql'
    };

    function loadTechPreset(key) {
      if (TECH_PRESETS[key]) {
        document.getElementById('badge-techs').value = TECH_PRESETS[key];
        showToast(`Preset "${key}" carregado!`);
        generateTechBadges();
      }
    }

    function toggleTechChip(tech) {
      const area = document.getElementById('badge-techs');
      let current = area.value.split(',').map(s => s.trim()).filter(Boolean);
      const idx = current.findIndex(t => t.toLowerCase() === tech.toLowerCase() || t.toLowerCase().endsWith(':' + tech.toLowerCase()));
      if (idx >= 0) {
        current.splice(idx, 1);
        showToast(`Removido: ${tech}`);
      } else {
        current.push(tech);
        showToast(`Adicionado: ${tech}`);
      }
      area.value = current.join(', ');
      generateTechBadges();
    }

    function addCustomTech() {
      const cat = document.getElementById('custom-tech-cat').value.trim();
      const name = document.getElementById('custom-tech-name').value.trim();
      if (!name) {
        showToast('⚠️ Digite o nome da tecnologia!');
        return;
      }
      const full = cat ? `${cat}:${name}` : name;
      const area = document.getElementById('badge-techs');
      let current = area.value.split(',').map(s => s.trim()).filter(Boolean);
      if (!current.includes(full)) {
        current.push(full);
        area.value = current.join(', ');
        document.getElementById('custom-tech-name').value = '';
        showToast(`✨ Adicionado ao arsenal: ${full}`);
        generateTechBadges();
      } else {
        showToast('ℹ️ Essa tecnologia já está na lista!');
      }
    }

    async function generateTechBadges() {
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
      const techs = document.getElementById('badge-techs').value;
      const style = document.getElementById('badge-style').value;
      const title = document.getElementById('badge-title').value;
      const user = document.getElementById('badge-user').value;

      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Renderizando matriz de badges...</div>';
      const url = `/api/render/tech_stack?techs=${encodeURIComponent(techs)}&style=${encodeURIComponent(style)}&title=${encodeURIComponent(title)}&username=${encodeURIComponent(user)}`;
      const res = await fetch(url);
      const svg = await res.text();
      setPreview(svg, 'tech_stack.svg');
    }

    function copyShieldsMarkdown() {
      const rawTechs = document.getElementById('badge-techs').value.split(',');
      const mdList = [];
      const SHIELD_MAP = {
        python: 'Python-3776AB?style=for-the-badge&logo=python&logoColor=white',
        typescript: 'TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white',
        javascript: 'JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black',
        rust: 'Rust-DEA584?style=for-the-badge&logo=rust&logoColor=white',
        go: 'Go-00ADD8?style=for-the-badge&logo=go&logoColor=white',
        cpp: 'C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white',
        csharp: 'C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white',
        java: 'Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white',
        kotlin: 'Kotlin-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white',
        swift: 'Swift-F05138?style=for-the-badge&logo=swift&logoColor=white',
        dart: 'Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white',
        flutter: 'Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white',
        react_native: 'React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB',
        react: 'React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB',
        nextjs: 'Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white',
        vue: 'Vue.js-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white',
        angular: 'Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white',
        svelte: 'Svelte-FF3E00?style=for-the-badge&logo=svelte&logoColor=white',
        fastapi: 'FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white',
        django: 'Django-092E20?style=for-the-badge&logo=django&logoColor=white',
        nodejs: 'Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white',
        docker: 'Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white',
        kubernetes: 'Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white',
        aws: 'AWS-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white',
        postgresql: 'PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white',
        mongodb: 'MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white',
        redis: 'Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white',
        tailwind: 'Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white',
        linux: 'Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black',
        git: 'Git-F05032?style=for-the-badge&logo=git&logoColor=white',
        solidity: 'Solidity-AA6746?style=for-the-badge&logo=solidity&logoColor=white',
        godot: 'Godot_Engine-478CBF?style=for-the-badge&logo=godotengine&logoColor=white',
        pytorch: 'PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white',
        terraform: 'Terraform-844FBA?style=for-the-badge&logo=terraform&logoColor=white'
      };

      for (let t of rawTechs) {
        let clean = t.trim();
        if (clean.includes(':')) {
          clean = clean.split(':')[1].trim();
        }
        const key = clean.toLowerCase().replace('-', '_').replace(' ', '_');
        if (SHIELD_MAP[key]) {
          mdList.push(`![${clean}](https://img.shields.io/badge/${SHIELD_MAP[key]})`);
        } else if (clean) {
          const cap = clean.charAt(0).toUpperCase() + clean.slice(1);
          mdList.push(`![${cap}](https://img.shields.io/badge/${encodeURIComponent(cap)}-23272d?style=for-the-badge)`);
        }
      }

      const fullMd = '<div align="center">\n  ' + mdList.join(' ') + '\n</div>';
      navigator.clipboard.writeText(fullMd);
      showToast('📋 Códigos Markdown copiados com sucesso!');
    }

    function toggleActivityWidget() {
      const w = document.getElementById('act-widget').value;
      document.getElementById('act-opt-music').classList.toggle('hidden', w !== 'music');
      document.getElementById('act-opt-coding').classList.toggle('hidden', w !== 'coding');
      document.getElementById('act-opt-diagram').classList.toggle('hidden', w !== 'diagram');
    }

    async function generateActivityCard() {
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
      const w = document.getElementById('act-widget').value;
      const user = document.getElementById('act-user').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Renderizando card de atividade...</div>';

      let url = '';
      if (w === 'music') {
        const preset = document.getElementById('music-preset').value;
        const title = document.getElementById('music-title').value;
        const artist = document.getElementById('music-artist').value;
        const anim = globalAnimationsDisabled ? false : true;
        url = `/api/render/music?preset=${encodeURIComponent(preset)}&title=${encodeURIComponent(title)}&artist=${encodeURIComponent(artist)}&animated=${anim}&username=${encodeURIComponent(user)}`;
      } else if (w === 'coding') {
        const hours = document.getElementById('coding-hours').value;
        const streak = document.getElementById('coding-streak').value;
        const rank = document.getElementById('coding-rank').value;
        url = `/api/render/coding_stats?hours=${encodeURIComponent(hours)}&streak=${encodeURIComponent(streak)}&rank=${encodeURIComponent(rank)}&username=${encodeURIComponent(user)}`;
      } else if (w === 'diagram') {
        const preset = document.getElementById('diagram-preset').value;
        const title = document.getElementById('diagram-title') ? document.getElementById('diagram-title').value.trim() : '';
        url = `/api/render/diagram?preset=${encodeURIComponent(preset)}&title=${encodeURIComponent(title)}&username=${encodeURIComponent(user)}`;
      }

      const res = await fetch(url);
      const svg = await res.text();
      setPreview(svg, `${w}_card.svg`);
    }

    async function animateImportedSvg() {
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
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
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
      const pipes = document.getElementById('pipes-count').value;
      const steps = document.getElementById('pipes-steps').value;
      const user = document.getElementById('pipes-user').value;
      document.getElementById('svg-display').innerHTML = '<div class="text-slate-400 text-sm animate-pulse">Gerando labirinto procedural de tubos...</div>';
      const res = await fetch(`/api/render/pipes?num_pipes=${pipes}&steps=${steps}&username=${encodeURIComponent(user)}`);
      const svg = await res.text();
      setPreview(svg, 'pipes-screensaver.svg');
    }

    async function generateScreensaverFx() {
      if (typeof playGameBoyBeep === 'function') playGameBoyBeep();
      const fx = document.getElementById('fx-engine').value;
      const user = document.getElementById('fx-user').value;
      document.getElementById('svg-display').innerHTML = `<div class="text-slate-400 text-sm animate-pulse">Renderizando ${fx}...</div>`;
      
      const formData = new FormData();
      formData.append('engine', fx);
      formData.append('username', user);

      if (fx === 'snake') {
        formData.append('snake_casing', document.getElementById('snake-casing').value);
        formData.append('snake_display', document.getElementById('snake-display').value);
        formData.append('snake_score', document.getElementById('snake-score').value);
        formData.append('snake_speed', document.getElementById('snake-speed').value);
      } else if (fx === 'pong') {
        formData.append('pong_theme', document.getElementById('pong-theme').value);
        formData.append('pong_score1', document.getElementById('pong-score1').value);
        formData.append('pong_score2', document.getElementById('pong-score2').value);
        formData.append('pong_speed', document.getElementById('pong-speed').value);
      } else if (fx === 'flappy') {
        formData.append('flappy_theme', document.getElementById('flappy-theme').value);
        formData.append('flappy_score', document.getElementById('flappy-score').value);
      } else if (fx === 'mario') {
        formData.append('mario_world', document.getElementById('mario-world').value);
        formData.append('mario_score', document.getElementById('mario-score').value);
      } else if (fx === 'space_invaders') {
        formData.append('invaders_score', document.getElementById('invaders-score').value);
      } else if (fx === 'pacman') {
        formData.append('pacman_score', document.getElementById('pacman-score').value);
      } else if (fx === 'starfield') {
        formData.append('starfield_warp', document.getElementById('starfield-warp').value);
      } else if (fx === 'cyberpunk_city') {
        formData.append('city_name', document.getElementById('city-name').value);
      } else if (fx === 'dvd') {
        formData.append('dvd_text', document.getElementById('dvd-text').value);
        formData.append('dvd_speed', document.getElementById('dvd-speed').value);
      } else if (fx === 'pipes') {
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

    async function downloadGif() {
      if (!currentSvg) {
        showToast("⚠️ Gere ou selecione uma arte antes de exportar!");
        return;
      }
      showToast("🎬 Renderizando GIF animado com Chromium & ffmpeg...", 5000);
      const btn = document.getElementById('btn-download-gif');
      if (btn) btn.classList.add('animate-pulse', 'opacity-50');
      try {
        const res = await fetch('/api/export/gif', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ svg: currentSvg, duration: 2.5, fps: 16 })
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ message: 'Erro desconhecido' }));
          throw new Error(err.message || 'Falha na renderização');
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const name = (currentFilename || 'termart-animation.svg').replace(/\.svg$/i, '') + '.gif';
        a.download = name;
        a.click();
        URL.revokeObjectURL(url);
        showToast("✓ GIF animado exportado com sucesso!", 3000);
      } catch (e) {
        showToast(`❌ Erro ao exportar GIF: ${e.message}`, 4000);
      } finally {
        if (btn) btn.classList.remove('animate-pulse', 'opacity-50');
      }
    }

    async function downloadMp4() {
      if (!currentSvg) {
        showToast("⚠️ Gere ou selecione uma arte antes de exportar!");
        return;
      }
      showToast("🎥 Renderizando vídeo MP4 H.264 via ffmpeg...", 5000);
      const btn = document.getElementById('btn-download-mp4');
      if (btn) btn.classList.add('animate-pulse', 'opacity-50');
      try {
        const res = await fetch('/api/export/mp4', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ svg: currentSvg, duration: 3.0, fps: 24 })
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ message: 'Erro desconhecido' }));
          throw new Error(err.message || 'Falha na renderização');
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const name = (currentFilename || 'termart-video.svg').replace(/\.svg$/i, '') + '.mp4';
        a.download = name;
        a.click();
        URL.revokeObjectURL(url);
        showToast("✓ Vídeo MP4 gerado com sucesso!", 3000);
      } catch (e) {
        showToast(`❌ Erro ao exportar MP4: ${e.message}`, 4000);
      } finally {
        if (btn) btn.classList.remove('animate-pulse', 'opacity-50');
      }
    }

    function downloadSvg() {
      if (typeof playMarioCoinSound === 'function') playMarioCoinSound();
      if (!currentSvg) return;
      const blob = new Blob([currentSvg], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = currentFilename;
      a.click();
      URL.revokeObjectURL(url);
    }

    function convertSvgToPng(svgStr, filename, scale = 2) {
      if (!svgStr) {
        showToast("Nenhuma arte para converter!");
        return;
      }
      showToast("Renderizando imagem PNG...", 2500);

      try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgStr, "image/svg+xml");
        const svgEl = doc.documentElement;

        // 1. Unmask typewriter clipPaths so art is immediately 100% visible in static canvas
        doc.querySelectorAll('[clip-path]').forEach(el => {
          const cp = el.getAttribute('clip-path') || '';
          if (cp.includes('clp_') || cp.includes('reveal') || cp.includes('type')) {
            el.removeAttribute('clip-path');
          }
        });
        doc.querySelectorAll('clipPath').forEach(cp => {
          const id = cp.getAttribute('id') || '';
          if (id.startsWith('clp_') || id.includes('reveal') || id.includes('type')) {
            cp.remove();
          }
        });

        // 2. Remove temporary cursor animation elements
        doc.querySelectorAll('rect').forEach(r => {
          if (r.getAttribute('opacity') === '0' && r.querySelector('set[attributeName="opacity"]')) {
            r.remove();
          }
        });

        // 3. Ensure any remaining clipPath rects are not zero-width
        doc.querySelectorAll('clipPath rect').forEach(r => {
          if (r.getAttribute('width') === '0') {
            r.setAttribute('width', '100%');
          }
        });

        // 4. Freeze animation final states
        doc.querySelectorAll('animate, set').forEach(anim => {
          const attr = anim.getAttribute('attributeName');
          const toVal = anim.getAttribute('to');
          if (attr && toVal && anim.parentElement) {
            anim.parentElement.setAttribute(attr, toVal);
          }
        });

        let width = parseFloat(svgEl.getAttribute("width"));
        let height = parseFloat(svgEl.getAttribute("height"));
        const viewBox = svgEl.getAttribute("viewBox");
        if ((!width || !height || isNaN(width) || isNaN(height)) && viewBox) {
          const parts = viewBox.split(/[\s,]+/).filter(Boolean);
          if (parts.length === 4) {
            width = parseFloat(parts[2]);
            height = parseFloat(parts[3]);
          }
        }
        width = width || 800;
        height = height || 500;

        if (!svgEl.getAttribute("xmlns")) {
          svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        }

        const serialized = new XMLSerializer().serializeToString(svgEl);
        const svgBlob = new Blob([serialized], { type: "image/svg+xml;charset=utf-8" });
        const URLObj = window.URL || window.webkitURL || window;
        const blobUrl = URLObj.createObjectURL(svgBlob);

        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = function() {
          const canvas = document.createElement("canvas");
          canvas.width = Math.round(width * scale);
          canvas.height = Math.round(height * scale);
          const ctx = canvas.getContext("2d");
          ctx.fillStyle = "#0d1117";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          URLObj.revokeObjectURL(blobUrl);

          canvas.toBlob(function(blob) {
            if (!blob) {
              showToast("Erro ao gerar PNG.");
              return;
            }
            const pngUrl = URLObj.createObjectURL(blob);
            const a = document.createElement("a");
            const baseName = (filename || "termart").replace(/\.svg$/i, "");
            a.download = `${baseName}.png`;
            a.href = pngUrl;
            a.click();
            URLObj.revokeObjectURL(pngUrl);
            showToast(`✓ PNG exportado (${canvas.width}x${canvas.height})!`);
          }, "image/png");
        };
        img.onerror = function() {
          URLObj.revokeObjectURL(blobUrl);
          showToast("Erro ao rasterizar SVG para PNG.");
        };
        img.src = blobUrl;
      } catch (err) {
        showToast("Erro ao processar conversão para PNG.");
      }
    }

    function downloadPng() {
      if (typeof playMarioCoinSound === 'function') playMarioCoinSound();
      if (!currentSvg) {
        showToast("Gere uma arte primeiro para exportar em PNG!");
        return;
      }
      convertSvgToPng(currentSvg, currentFilename || "termart.svg", 2);
    }

    function downloadSingleBatchPng(idx) {
      const item = currentBatchResults[idx];
      if (!item) return;
      convertSvgToPng(item.svg, item.filename, 2);
    }


    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function getDevProfile() {
      try {
        const raw = localStorage.getItem('termart_dev_profile');
        if (raw) return JSON.parse(raw);
      } catch (e) {}
      return null;
    }

    function setDevProfile(profile) {
      localStorage.setItem('termart_dev_profile', JSON.stringify(profile));
      applyDevProfile(profile);
    }

    function applyDevProfile(profile) {
      if (!profile) return;
      const user = profile.github || profile.name || 'developer';
      const name = profile.name || profile.github || 'Developer';
      const city = profile.city || 'Curitiba, Brazil';
      const ghUrl = profile.github ? `https://github.com/${profile.github}` : 'https://github.com';

      // Update Navbar Badge
      const badge = document.getElementById('header-user-badge');
      if (badge) {
        badge.innerHTML = `Perfil: <strong class="text-brand-400">@${escapeHtml(user)}</strong>`;
      }

      // Auto-populate all inputs across all tabs
      const fields = {
        'img-user': name,
        'city-user': user,
        'profile-user': user,
        'weather-city': city,
        'qr-url': ghUrl,
        'fx-user': user,
        'badge-user': user,
        'act-user': user
      };

      for (const [id, val] of Object.entries(fields)) {
        const el = document.getElementById(id);
        if (el && val) {
          el.value = val;
        }
      }
    }

    async function fetchGithubData() {
      let rawUser = document.getElementById('cfg-github').value.trim();
      if (!rawUser) return;
      if (rawUser.includes('github.com/')) {
        rawUser = rawUser.split('github.com/')[1].split('/')[0].replace(/[@]/g, '');
        document.getElementById('cfg-github').value = rawUser;
      } else {
        rawUser = rawUser.replace(/[@]/g, '');
        document.getElementById('cfg-github').value = rawUser;
      }

      const statusEl = document.getElementById('cfg-gh-status');
      const btn = document.getElementById('btn-fetch-gh');
      if (statusEl) statusEl.innerHTML = '<span class="text-brand-400">🔍 Buscando perfil na API do GitHub...</span>';
      if (btn) btn.disabled = true;

      try {
        const res = await fetch(`https://api.github.com/users/${encodeURIComponent(rawUser)}`);
        if (res.ok) {
          const data = await res.json();
          if (data.name) {
            document.getElementById('cfg-name').value = data.name;
          } else if (data.login) {
            document.getElementById('cfg-name').value = data.login;
          }
          if (data.location) {
            document.getElementById('cfg-city').value = data.location;
          }
          if (data.bio) {
            document.getElementById('cfg-role').value = data.bio;
          }
          if (statusEl) statusEl.innerHTML = `<span class="text-emerald-400">✓ Dados de <strong>${escapeHtml(data.login)}</strong> carregados com sucesso!</span>`;
        } else {
          if (statusEl) statusEl.innerHTML = `<span class="text-amber-400">Usuário não encontrado no GitHub. Você pode preencher manualmente abaixo!</span>`;
        }
      } catch (err) {
        if (statusEl) statusEl.innerHTML = `<span class="text-slate-400">API do GitHub indisponível. Preencha os campos manualmente.</span>`;
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    function saveDevProfile() {
      let github = document.getElementById('cfg-github').value.trim();
      if (github.includes('github.com/')) {
        github = github.split('github.com/')[1].split('/')[0].replace(/[@]/g, '');
      } else {
        github = github.replace(/[@]/g, '');
      }

      const name = document.getElementById('cfg-name').value.trim() || github || 'Developer';
      const city = document.getElementById('cfg-city').value.trim() || 'Curitiba, Brazil';
      const role = document.getElementById('cfg-role').value.trim();

      const profile = { github, name, city, role };
      setDevProfile(profile);
      closeConfigModal();
      showToast(`Perfil @${github || name} configurado com sucesso!`);
    }

    function openConfigModal() {
      const modal = document.getElementById('modal-dev-profile');
      if (!modal) return;
      const p = getDevProfile();
      if (p) {
        document.getElementById('cfg-github').value = p.github || '';
        document.getElementById('cfg-name').value = p.name || '';
        document.getElementById('cfg-city').value = p.city || '';
        document.getElementById('cfg-role').value = p.role || '';
      }
      modal.classList.remove('hidden');
    }

    function closeConfigModal() {
      const modal = document.getElementById('modal-dev-profile');
      if (modal) modal.classList.add('hidden');
    }

    
    // ==========================================
    // GITHUB PROFILE & README BUILDER CONTROLLER
    // ==========================================
    let builderSections = [];
    let builderCurrentMarkdown = "";
    let activeBuilderView = "visual";

    const DEFAULT_BUILDER_BLOCKS = [
      { id: "header", type: "header", title: "Banner 3D / Wordmark", enabled: true, file: "header.svg", icon: "🌟" },
      { id: "badges", type: "badges", title: "Arsenal Tech Stack & Badges", enabled: true, file: "tech-stack.svg", icon: "🛡️" },
      { id: "heatmap", type: "heatmap", title: "Heatmap 3D de Commits", enabled: true, file: "contrib-heatmap.svg", icon: "📊" },
      { id: "stats", type: "stats", title: "Métricas & Status do GitHub", enabled: true, file: "github-stats.svg", icon: "📈" },
      { id: "neofetch", type: "neofetch", title: "Card Neofetch macOS", enabled: true, file: "info-card.svg", icon: "💻" },
      { id: "pokemon", type: "pokemon", title: "Card RPG Holográfico Pokémon", enabled: true, file: "pokemon-card.svg", icon: "🎮" },
      { id: "coding_stats", type: "coding_stats", title: "Radar de Produtividade & Streaks", enabled: true, file: "coding-stats.svg", icon: "⚡" },
      { id: "music", type: "music", title: "Cassete Spotify Hi-Fi", enabled: false, file: "music-card.svg", icon: "🎵" },
      { id: "chess", type: "chess", title: "Partida de Xadrez com Xeque-Mate", enabled: false, file: "chess-board.svg", icon: "♟️" },
      { id: "weather", type: "weather", title: "Previsão do Tempo em ASCII", enabled: false, file: "weather-card.svg", icon: "🌦️" },
      { id: "diagram", type: "diagram", title: "Topologia de Arquitetura", enabled: false, file: "architecture.svg", icon: "📐" },
      { id: "fortune", type: "fortune", title: "Biscoito da Sorte Hacker / Zen", enabled: false, file: "fortune.svg", icon: "🥠" },
      { id: "rpg", type: "rpg_sheet", title: "Passaporte RPG do Desenvolvedor", enabled: false, file: "rpg-sheet.svg", icon: "⚔️", params: { cls: "alchemist", level: 85 } },
      { id: "subway", type: "git_subway", title: "Mapa de Metrô dos Commits (Branches)", enabled: false, file: "git-subway.svg", icon: "🗺️", params: { repo: "core-platform" } },
      { id: "pet", type: "dev_pet", title: "Tamagotchi Dev Pet Virtual 1996", enabled: false, file: "dev-pet.svg", icon: "👾", params: { type: "mametchi", name: "KERNEL" } },
      { id: "mario", type: "mario", title: "Super Mario Bros NES World 1-1 Runner", enabled: false, file: "mario-runner.svg", icon: "🍄", params: { world: "1-1", score: 2450 } },
      { id: "invaders", type: "space_invaders", title: "Space Invaders Arcade 1978", enabled: false, file: "space-invaders.svg", icon: "👾", params: { score: 1978 } },
      { id: "pacman", type: "pacman", title: "Pac-Man Arcade Maze 1980", enabled: false, file: "pacman-chase.svg", icon: "ᗧ", params: { score: 333360 } },
      { id: "dvd", type: "dvd", title: "Screensaver DVD Bouncing Retro", enabled: false, file: "dvd-screensaver.svg", icon: "📀", params: { text: "DVD", speed: 1.0 } },
      { id: "snake", type: "snake", title: "Nokia 3310 Snake Game 60fps", enabled: false, file: "snake-nokia.svg", icon: "🐍", params: { casing_color: "navy", display_mode: "classic_lcd", speed: 1.0, score: 420 } },
      { id: "pong", type: "pong", title: "Atari 1972 Pong Arcade 60fps", enabled: false, file: "pong-arcade.svg", icon: "🏓", params: { theme: "classic_green", score_p1: 7, score_p2: 5, speed: 1.0 } },
      { id: "flappy", type: "flappy", title: "Terminal Flappy Bird 8-Bit 60fps", enabled: false, file: "flappy-bird.svg", icon: "🐤", params: { theme: "retro_arcade", bird_color: "#ffcc00", score: 12 } },
      { id: "btop_monitor", type: "btop_monitor", title: "Btop++ Cyberpunk System Monitor", enabled: false, file: "btop-monitor.svg", icon: "📟", params: { theme: "catppuccin", uptime: "42 DAYS, 13:37:00" } },
      { id: "cli_session", type: "cli_session", title: "CLI Terminal Session Mockup", enabled: false, file: "cli-session.svg", icon: "⌨️", params: { theme: "ghostty", terminal_title: "ghostty@terminal: ~" } },
      { id: "git_graph", type: "git_graph", title: "Git Commit Graph Visualizer", enabled: false, file: "git-graph.svg", icon: "🌿", params: { theme: "neon_cyber" } },
      { id: "cyber_id", type: "cyber_id", title: "Cyberpunk Corporate ID Access Badge", enabled: false, file: "cyber-id.svg", icon: "🪪", params: { role: "Senior Lead Architect", clearance_level: "LEVEL 5 - ROOT", theme: "arasaka_red" } },
      { id: "achievement", type: "achievement", title: "Console Achievement 3D Trophy", enabled: false, file: "achievement.svg", icon: "🏆", params: { title: "LENDÁRIO CODE ARCHITECT", points: 100, rarity: "0.1% RARO", platform: "xbox" } },
      { id: "skill_tree", type: "skill_tree", title: "Developer RPG Skill Tree", enabled: false, file: "skill-tree.svg", icon: "🌳", params: { focus: "Fullstack / Cloud / AI Architect", theme: "cyber_constellation" } },
      { id: "custom_art", type: "custom_svg", title: "Arte / Imagem / GIF Personalizado", enabled: false, file: "custom-art.svg", icon: "🖼️", params: {} }
    ];

    function getStoredBuilderSections() {
      try {
        const raw = localStorage.getItem('termart_readme_sections');
        if (raw) return JSON.parse(raw);
      } catch(e) {}
      return JSON.parse(JSON.stringify(DEFAULT_BUILDER_BLOCKS));
    }

    function saveStoredBuilderSections(sections) {
      builderSections = sections;
      localStorage.setItem('termart_readme_sections', JSON.stringify(sections));
      renderBuilderSectionsList();
    }

    function cycleBlockWidth(idx) {
      const sec = builderSections[idx];
      if (!sec) return;
      if (!sec.width || sec.width === '100%') {
        sec.width = '49%';
        showToast(`"${sec.title}" agora está em 50% (Lado a Lado)!`);
      } else if (sec.width === '49%' || sec.width === '50%') {
        sec.width = '32%';
        showToast(`"${sec.title}" agora está em 33% (3 Colunas)!`);
      } else {
        sec.width = '100%';
        showToast(`"${sec.title}" agora está em 100% (Largura Total)!`);
      }
      saveStoredBuilderSections(builderSections);
      renderReadmePreview();
    }

    let draggedBlockIdx = null;

    function renderBuilderSectionsList() {
      const listEl = document.getElementById('builder-sections-list');
      const countEl = document.getElementById('builder-count-label');
      if (!listEl) return;

      const activeCount = builderSections.filter(s => s.enabled).length;
      if (countEl) countEl.innerText = `${activeCount} ativas de ${builderSections.length}`;

      listEl.innerHTML = builderSections.map((sec, idx) => `
        <div draggable="true"
             data-index="${idx}"
             ondragstart="handleBlockDragStart(event, ${idx})"
             ondragover="handleBlockDragOver(event, ${idx})"
             ondragenter="handleBlockDragEnter(event, ${idx})"
             ondragleave="handleBlockDragLeave(event, ${idx})"
             ondrop="handleBlockDrop(event, ${idx})"
             ondragend="handleBlockDragEnd(event)"
             class="group cursor-grab active:cursor-grabbing flex items-center justify-between p-2.5 rounded-xl border ${sec.enabled ? 'bg-brand-dark/85 border-brand-border hover:border-brand-500 shadow-sm' : 'bg-brand-dark/30 border-brand-border/40 opacity-50'} transition-all select-none">
          <div class="flex items-center gap-2.5 min-w-0">
            <span class="text-slate-500 group-hover:text-brand-400 font-mono text-base px-1 tracking-tighter" title="Clique e arraste para cima ou para baixo">⠿</span>
            <span class="text-base shrink-0">${sec.icon || '⚡'}</span>
            <div class="truncate">
              <span class="text-xs font-semibold text-white block truncate">${escapeHtml(sec.title)}</span>
              <span class="text-[10px] text-slate-500 font-mono">${escapeHtml(sec.file)}</span>
            </div>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" onclick="cycleBlockWidth(${idx})" class="px-2 py-1 rounded-lg text-[10px] font-mono font-bold border transition ${sec.width === '49%' || sec.width === '50%' ? 'bg-sky-500/20 text-sky-400 border-sky-500/40' : (sec.width === '32%' || sec.width === '33%' ? 'bg-purple-500/20 text-purple-400 border-purple-500/40' : 'bg-slate-800 text-slate-400 border-slate-700')}" title="Clique para alternar: 100% (Linha Cheia) / 50% (Lado a Lado) / 33% (3 Colunas)">
              ${sec.width === '49%' || sec.width === '50%' ? '50% ⇋' : (sec.width === '32%' || sec.width === '33%' ? '33% ⇋' : '100%')}
            </button>
            <button onclick="openBlockConfigModal(${idx})" class="w-7 h-7 rounded-lg flex items-center justify-center bg-slate-800 hover:bg-brand-600/40 text-slate-300 hover:text-white border border-brand-border text-xs transition" title="Configurar Parâmetros Deste Bloco">
              ⚙️
            </button>
            <button onclick="toggleBuilderBlock(${idx})" class="w-7 h-7 rounded-lg flex items-center justify-center ${sec.enabled ? 'bg-emerald-600/25 text-emerald-400 border border-emerald-500/40 hover:bg-emerald-600/40' : 'bg-slate-800 text-slate-500 hover:bg-slate-700'} text-xs font-bold transition" title="${sec.enabled ? 'Desativar Bloco' : 'Ativar Bloco'}">
              ${sec.enabled ? '✓' : '✕'}
            </button>
            <button onclick="removeBuilderBlock(${idx})" class="w-7 h-7 rounded-lg flex items-center justify-center bg-red-600/15 hover:bg-red-600/35 border border-red-500/30 text-red-400 text-xs transition" title="Remover Bloco">
              🗑️
            </button>
          </div>
        </div>
      `).join('');
    }

    
    // ==========================================
    // BLOCK CONFIGURATION & GALLERY PINNING
    // ==========================================
    let editingBlockIdx = null;

    function openBlockConfigModal(idx) {
      editingBlockIdx = idx;
      const sec = builderSections[idx];
      if (!sec) return;

      const modal = document.getElementById('modal-block-config');
      const iconEl = document.getElementById('cfg-block-icon');
      const titleEl = document.getElementById('cfg-block-title');
      const formEl = document.getElementById('cfg-block-form');

      if (iconEl) iconEl.innerText = sec.icon || '⚙️';
      if (titleEl) titleEl.innerText = `Configurar ${sec.title}`;

      const params = sec.params || {};
      let html = '';

      if (sec.type === 'snake') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Carcaça do Nokia</label>
              <select id="cfg-snake-casing" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="navy" ${(params.casing_color || 'navy') === 'navy' ? 'selected' : ''}>🔵 Azul Marinho Original</option>
                <option value="cyber_neon" ${params.casing_color === 'cyber_neon' ? 'selected' : ''}>🟣 Cyber Neon</option>
                <option value="cherry_red" ${params.casing_color === 'cherry_red' ? 'selected' : ''}>🔴 Cherry Red</option>
                <option value="silver" ${params.casing_color === 'silver' ? 'selected' : ''}>⚪ Silver Grey</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Display LCD</label>
              <select id="cfg-snake-display" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="classic_lcd" ${(params.display_mode || 'classic_lcd') === 'classic_lcd' ? 'selected' : ''}>🟢 LCD Esmeralda</option>
                <option value="amber" ${params.display_mode === 'amber' ? 'selected' : ''}>🟠 Âmbar CRT</option>
                <option value="cyber_cyan" ${params.display_mode === 'cyber_cyan' ? 'selected' : ''}>🔵 Ciano Neon</option>
                <option value="matrix" ${params.display_mode === 'matrix' ? 'selected' : ''}>🟢 Matrix Verde</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 mt-2">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Score Inicial</label>
              <input type="number" id="cfg-snake-score" value="${params.score || 420}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Velocidade</label>
              <select id="cfg-snake-speed" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="0.75" ${params.speed === 0.75 ? 'selected' : ''}>0.75x</option>
                <option value="1.0" ${(!params.speed || params.speed === 1.0) ? 'selected' : ''}>1.0x (60fps)</option>
                <option value="1.5" ${params.speed === 1.5 ? 'selected' : ''}>1.5x</option>
              </select>
            </div>
          </div>
        `;
      } else if (sec.type === 'pong') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Tema Arcade</label>
              <select id="cfg-pong-theme" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="classic_green" ${(params.theme || 'classic_green') === 'classic_green' ? 'selected' : ''}>🟢 Verde Fosfórico 1972</option>
                <option value="b_and_w" ${params.theme === 'b_and_w' ? 'selected' : ''}>⚪ P&amp;B Original</option>
                <option value="cyber_neon" ${params.theme === 'cyber_neon' ? 'selected' : ''}>🟣 Cyberpunk Neon</option>
                <option value="amber_crt" ${params.theme === 'amber_crt' ? 'selected' : ''}>🟠 Âmbar CRT</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Placar P1 vs P2</label>
              <div class="flex gap-2">
                <input type="number" id="cfg-pong-s1" value="${params.score_p1 || 7}" class="w-1/2 p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
                <input type="number" id="cfg-pong-s2" value="${params.score_p2 || 5}" class="w-1/2 p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
              </div>
            </div>
          </div>
        `;
      } else if (sec.type === 'flappy') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Paleta Visual</label>
              <select id="cfg-flappy-theme" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="retro_arcade" ${(params.theme || 'retro_arcade') === 'retro_arcade' ? 'selected' : ''}>🎮 Arcade Original</option>
                <option value="terminal_green" ${params.theme === 'terminal_green' ? 'selected' : ''}>🟢 Terminal Green</option>
                <option value="vaporwave" ${params.theme === 'vaporwave' ? 'selected' : ''}>🌆 Vaporwave</option>
                <option value="midnight" ${params.theme === 'midnight' ? 'selected' : ''}>🌌 Midnight</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Score</label>
              <input type="number" id="cfg-flappy-score" value="${params.score || 12}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
            </div>
          </div>
        `;
      } else if (sec.type === 'btop_monitor') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Tema Unixporn</label>
              <select id="cfg-btop-theme" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="catppuccin" ${(params.theme || 'catppuccin') === 'catppuccin' ? 'selected' : ''}>Catppuccin Mocha</option>
                <option value="dracula" ${params.theme === 'dracula' ? 'selected' : ''}>Dracula Dark</option>
                <option value="tokyonight" ${params.theme === 'tokyonight' ? 'selected' : ''}>Tokyo Night</option>
                <option value="nord" ${params.theme === 'nord' ? 'selected' : ''}>Nord</option>
                <option value="cyberpunk" ${params.theme === 'cyberpunk' ? 'selected' : ''}>Cyberpunk</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Uptime</label>
              <input type="text" id="cfg-btop-uptime" value="${escapeHtml(params.uptime || '42 DAYS, 13:37:00')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
            </div>
          </div>
        `;
      } else if (sec.type === 'cli_session') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Tema Terminal</label>
              <select id="cfg-cli-theme" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="ghostty" ${(params.theme || 'ghostty') === 'ghostty' ? 'selected' : ''}>Ghostty Dark</option>
                <option value="dracula" ${params.theme === 'dracula' ? 'selected' : ''}>Dracula</option>
                <option value="catppuccin" ${params.theme === 'catppuccin' ? 'selected' : ''}>Catppuccin</option>
                <option value="matrix" ${params.theme === 'matrix' ? 'selected' : ''}>Matrix Green</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Título da Janela</label>
              <input type="text" id="cfg-cli-title" value="${escapeHtml(params.terminal_title || 'ghostty@terminal: ~')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
            </div>
          </div>
        `;
      } else if (sec.type === 'git_graph') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Tema</label>
              <select id="cfg-git-theme" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="neon_cyber" ${(params.theme || 'neon_cyber') === 'neon_cyber' ? 'selected' : ''}>Neon Cyber Glow</option>
                <option value="gitkraken" ${params.theme === 'gitkraken' ? 'selected' : ''}>GitKraken</option>
                <option value="terminal" ${params.theme === 'terminal' ? 'selected' : ''}>Terminal Green</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Nome do Repositório</label>
              <input type="text" id="cfg-git-repo" value="${escapeHtml(params.repo_name || 'core-engine')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
            </div>
          </div>
        `;
      } else if (sec.type === 'cyber_id') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Corporação</label>
              <select id="cfg-cid-theme" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="arasaka_red" ${(params.theme || 'arasaka_red') === 'arasaka_red' ? 'selected' : ''}>Arasaka Security</option>
                <option value="militech_yellow" ${params.theme === 'militech_yellow' ? 'selected' : ''}>Militech Arms</option>
                <option value="neon_matrix" ${params.theme === 'neon_matrix' ? 'selected' : ''}>NetWatch Matrix</option>
                <option value="phantom_purple" ${params.theme === 'phantom_purple' ? 'selected' : ''}>Phantom Purple</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Autorização</label>
              <input type="text" id="cfg-cid-level" value="${escapeHtml(params.clearance_level || 'LEVEL 5 - ROOT')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
            </div>
          </div>
          <div class="flex flex-col gap-1.5 mt-2">
            <label class="font-semibold text-slate-300">Cargo / Especialidade</label>
            <input type="text" id="cfg-cid-role" value="${escapeHtml(params.role || 'Senior Lead Architect')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
        `;
      } else if (sec.type === 'achievement') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Plataforma</label>
              <select id="cfg-ach-plat" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="xbox" ${(params.platform || 'xbox') === 'xbox' ? 'selected' : ''}>Xbox Rare (+Glint)</option>
                <option value="steam" ${params.platform === 'steam' ? 'selected' : ''}>Steam Gold</option>
                <option value="playstation" ${params.platform === 'playstation' ? 'selected' : ''}>PlayStation Platinum</option>
                <option value="cyberpunk" ${params.platform === 'cyberpunk' ? 'selected' : ''}>Cyberpunk Secret</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Pontos / Gamerscore</label>
              <input type="number" id="cfg-ach-pts" value="${params.points || 100}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
            </div>
          </div>
          <div class="flex flex-col gap-1.5 mt-2">
            <label class="font-semibold text-slate-300">Título da Conquista</label>
            <input type="text" id="cfg-ach-ttl" value="${escapeHtml(params.title || 'LENDÁRIO CODE ARCHITECT')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
        `;
      } else if (sec.type === 'skill_tree') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Tema da Constelação</label>
              <select id="cfg-sk-theme" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="cyber_constellation" ${(params.theme || 'cyber_constellation') === 'cyber_constellation' ? 'selected' : ''}>🌌 Cyber Constellation</option>
                <option value="diablo_arcane" ${params.theme === 'diablo_arcane' ? 'selected' : ''}>🔥 Diablo IV Arcane</option>
                <option value="matrix_nodes" ${params.theme === 'matrix_nodes' ? 'selected' : ''}>🟢 Matrix Grid</option>
                <option value="celestial_gold" ${params.theme === 'celestial_gold' ? 'selected' : ''}>⭐ Celestial Gold</option>
                <option value="dracula_rpg" ${params.theme === 'dracula_rpg' ? 'selected' : ''}>🧛 Dracula RPG</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Foco Primário</label>
              <input type="text" id="cfg-sk-focus" value="${escapeHtml(params.focus || 'Fullstack / Cloud / AI Architect')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
          </div>
        `;
      } else if (sec.type === 'chess') {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Partida Histórica de Xadrez</label>
            <select id="cfg-chess-match" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
              <option value="opera" ${params.match === 'opera' ? 'selected' : ''}>Opera Game (1858) - Paul Morphy vs Allies</option>
              <option value="immortal" ${params.match === 'immortal' ? 'selected' : ''}>The Immortal Game (1851) - Anderssen vs Kieseritzky</option>
              <option value="legal" ${params.match === 'legal' ? 'selected' : ''}>Mate de Légal (1750) - Sacrifício Lendário de Dama</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Velocidade dos Lances</label>
              <select id="cfg-chess-speed" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="0.75" ${params.speed === 0.75 ? 'selected' : ''}>0.75x (Mais Calmo)</option>
                <option value="1.0" ${(!params.speed || params.speed === 1.0) ? 'selected' : ''}>1.0x (Padrão)</option>
                <option value="1.5" ${params.speed === 1.5 ? 'selected' : ''}>1.5x (Rápido)</option>
                <option value="2.0" ${params.speed === 2.0 ? 'selected' : ''}>2.0x (Ultra Veloz)</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Animação Automática</label>
              <label class="flex items-center gap-2 mt-2 cursor-pointer text-slate-300">
                <input type="checkbox" id="cfg-chess-anim" class="accent-brand-500" ${params.animated !== false ? 'checked' : ''}>
                <span>Executar lances em loop</span>
              </label>
            </div>
          </div>
          <div class="flex flex-col gap-1.5 mt-2">
            <label class="font-semibold text-slate-300">Importar Partida Própria (Cole o PGN do Chess.com ou Lichess)</label>
            <textarea id="cfg-chess-pgn" rows="2" placeholder="Cole aqui seu PGN ex: 1. e4 e5 2. Nf3... (opcional)" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">${escapeHtml(params.pgn || '')}</textarea>
          </div>
        `;
      } else if (sec.type === 'rpg' || sec.type === 'rpg_sheet') {
        window._modalRpgCustomAvatar = params.custom_avatar;
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Classe do Desenvolvedor</label>
            <select id="cfg-rpg-cls" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
              <option value="alchemist" ${(params.cls || 'alchemist') === 'alchemist' ? 'selected' : ''}>🧙‍♂️ Fullstack Alchemist (Node + Python + Rust)</option>
              <option value="sorcerer" ${params.cls === 'sorcerer' ? 'selected' : ''}>🧙 Systems Sorcerer (C / C++ / Kernel / ASM)</option>
              <option value="ninja" ${params.cls === 'ninja' ? 'selected' : ''}>🥷 Cyber Ninja (SecOps / PenTest / Linux)</option>
              <option value="paladin" ${params.cls === 'paladin' ? 'selected' : ''}>🛡️ Data Paladin (PostgreSQL / ML / BigData)</option>
              <option value="shaman" ${params.cls === 'shaman' ? 'selected' : ''}>⚡ Cloud Shaman (K8s / Terraform / AWS)</option>
            </select>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Nível do Personagem</label>
            <input type="number" id="cfg-rpg-level" min="1" max="999" value="${params.level || 85}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
          <div class="flex flex-col gap-1.5 mt-2 pt-2 border-t border-brand-border/40">
            <label class="font-semibold text-slate-300 flex items-center justify-between">
              <span>🖼️ Foto / Avatar Personalizado</span>
              <span class="text-[10px] text-purple-400 font-mono">PNG, JPG, GIF, SVG</span>
            </label>
            <div class="flex items-center gap-2">
              <label class="flex-1 px-3 py-1.5 bg-purple-500/15 hover:bg-purple-500/25 border border-purple-500/30 rounded-lg cursor-pointer text-xs text-purple-200 text-center font-medium transition">
                📁 Escolher Nova Imagem / GIF
                <input type="file" id="cfg-rpg-avatar-input" accept="image/png,image/jpeg,image/gif,image/svg+xml,image/webp" class="hidden" onchange="handleModalRpgAvatarUpload(event)">
              </label>
              <button type="button" id="btn-modal-rpg-avatar-clear" onclick="clearModalRpgAvatar()" class="${params.custom_avatar ? '' : 'hidden'} px-2.5 py-1.5 bg-red-500/15 hover:bg-red-500/25 border border-red-500/30 rounded-lg text-xs text-red-300 transition">
                Restaurar Padrão
              </button>
            </div>
            <div id="cfg-modal-rpg-preview-box" class="${params.custom_avatar ? 'flex' : 'hidden'} items-center gap-2.5 mt-1 p-2 bg-brand-surface rounded-lg border border-purple-500/30">
              <img id="cfg-modal-rpg-preview-img" src="${params.custom_avatar || ''}" class="w-12 h-10 object-cover rounded border border-purple-500/40 bg-brand-dark">
              <div class="flex-1 min-w-0">
                <span class="text-xs text-slate-200 font-medium block truncate">Avatar Personalizado Ativo</span>
                <span class="text-[10px] text-purple-300">Base64 embutido no passaporte</span>
              </div>
            </div>
          </div>
        `;
      } else if (sec.type === 'subway' || sec.type === 'git_subway') {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Nome do Repositório / Rede</label>
            <input type="text" id="cfg-sub-repo" value="${escapeHtml(params.repo || 'core-platform')}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
        `;
      } else if (sec.type === 'pet' || sec.type === 'dev_pet') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Espécie do Pet Virtual</label>
              <select id="cfg-pet-type" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="mametchi" ${(params.type || 'mametchi') === 'mametchi' ? 'selected' : ''}>⭐ Mametchi 1996 (Mascote Gênio #1 Bandai)</option>
                <option value="kuchipatchi" ${params.type === 'kuchipatchi' ? 'selected' : ''}>🦆 Kuchipatchi (Comilão Bico-de-Pato)</option>
                <option value="ginjirotchi" ${params.type === 'ginjirotchi' ? 'selected' : ''}>🐧 Ginjirotchi (Pinguim Atleta Nadador)</option>
                <option value="maskutchi" ${params.type === 'maskutchi' ? 'selected' : ''}>🥷 Maskutchi (Ninja Mascarado Secreto)</option>
                <option value="marutchi" ${params.type === 'marutchi' ? 'selected' : ''}>🟢 Marutchi (Bouncing Toddler)</option>
                <option value="babytchi" ${params.type === 'babytchi' ? 'selected' : ''}>👶 Babytchi (Recém-Nascido com Topete)</option>
                <option value="oyajitchi" ${params.type === 'oyajitchi' ? 'selected' : ''}>👴 Oyajitchi (Bigode Clássico de Terno)</option>
                <option value="tamatchi" ${params.type === 'tamatchi' ? 'selected' : ''}>🌱 Tamatchi (Jovem com Orelhinhas)</option>
                <option value="nyorotchi" ${params.type === 'nyorotchi' ? 'selected' : ''}>🐍 Nyorotchi (Cobra Ondulante)</option>
                <option value="tarakotchi" ${params.type === 'tarakotchi' ? 'selected' : ''}>👄 Tarakotchi (Bocão Alienígena)</option>
                <option value="cat" ${params.type === 'cat' ? 'selected' : ''}>🐱 Pixel Cat (Mametchi)</option>
                <option value="robot" ${params.type === 'robot' ? 'selected' : ''}>🤖 Cyber Droid (Maskutchi)</option>
                <option value="dragon" ${params.type === 'dragon' ? 'selected' : ''}>🐲 Mini Dragão (Kuchipatchi)</option>
                <option value="penguin" ${params.type === 'penguin' ? 'selected' : ''}>🐧 Linux Tux (Ginjirotchi)</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Nome do Pet</label>
              <input type="text" id="cfg-pet-name" value="${escapeHtml(params.name || 'KERNEL')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 mt-2">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">📟 Estilo da Carcaça / Aparelho</label>
              <select id="cfg-pet-style" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="egg" ${(params.casing_style || 'egg') === 'egg' ? 'selected' : ''}>🥚 Tamagotchi Egg 1996 (Clássico Oval)</option>
                <option value="gameboy" ${params.casing_style === 'gameboy' ? 'selected' : ''}>🎮 Game Boy Pocket (Console Portátil)</option>
                <option value="pager" ${params.casing_style === 'pager' ? 'selected' : ''}>📟 Telecom Beeper Pager 90s</option>
                <option value="star" ${params.casing_style === 'star' ? 'selected' : ''}>⭐ Tamagotchi Starlight (Antena Estelar)</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">🎨 Cor do Aparelho (Shell)</label>
              <select id="cfg-pet-color" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="cyber_blue" ${(params.casing_color || 'cyber_blue') === 'cyber_blue' ? 'selected' : ''}>🔵 Cyber Blue 90s</option>
                <option value="retro_pink" ${params.casing_color === 'retro_pink' ? 'selected' : ''}>🌸 Retro Pink 1996 (Original)</option>
                <option value="atomic_purple" ${params.casing_color === 'atomic_purple' ? 'selected' : ''}>🟣 Atomic Purple</option>
                <option value="banana_yellow" ${params.casing_color === 'banana_yellow' ? 'selected' : ''}>⚡ Pikachu Yellow</option>
                <option value="matrix_black" ${params.casing_color === 'matrix_black' ? 'selected' : ''}>🟢 Matrix Stealth Black</option>
                <option value="emerald_green" ${params.casing_color === 'emerald_green' ? 'selected' : ''}>🟩 Emerald Pocket Green</option>
                <option value="vaporwave_sunset" ${params.casing_color === 'vaporwave_sunset' ? 'selected' : ''}>🌇 Vaporwave Sunset</option>
                <option value="milky_white" ${params.casing_color === 'milky_white' ? 'selected' : ''}>⚪ Milky White Pearl</option>
                <option value="lava_red" ${params.casing_color === 'lava_red' ? 'selected' : ''}>🔴 Arcade Lava Red</option>
                <option value="kawaii_lavender" ${params.casing_color === 'kawaii_lavender' ? 'selected' : ''}>💜 Kawaii Pastel Lavender</option>
              </select>
            </div>
          </div>
        `;
      } else if (sec.type === 'mario') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Mundo (World)</label>
              <input type="text" id="cfg-mario-world" value="${escapeHtml(params.world || '1-1')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Pontuação</label>
              <input type="number" id="cfg-mario-score" value="${params.score || 2450}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
          </div>
        `;
      } else if (sec.type === 'invaders' || sec.type === 'space_invaders') {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Score do Arcade Space Invaders</label>
            <input type="number" id="cfg-invaders-score" value="${params.score || 1978}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
        `;
      } else if (sec.type === 'pacman') {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Score do Pac-Man (1UP)</label>
            <input type="number" id="cfg-pacman-score" value="${params.score || 333360}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
        `;
      } else if (sec.type === 'dvd') {
        html = `
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Texto do Logo</label>
              <input type="text" id="cfg-dvd-text" value="${escapeHtml(params.text || 'DVD')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Velocidade</label>
              <select id="cfg-dvd-speed" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="0.75" ${params.speed === 0.75 ? 'selected' : ''}>0.75x</option>
                <option value="1.0" ${(!params.speed || params.speed === 1.0) ? 'selected' : ''}>1.0x</option>
                <option value="1.5" ${params.speed === 1.5 ? 'selected' : ''}>1.5x</option>
                <option value="2.0" ${params.speed === 2.0 ? 'selected' : ''}>2.0x</option>
              </select>
            </div>
          </div>
        `;
      } else if (sec.type === 'pokemon') {
        const pks = [
          ['gengar', '👻 Gengar'], ['charizard', '🔥 Charizard'], ['rayquaza', '🐉 Rayquaza'],
          ['mewtwo', '🔮 Mewtwo'], ['lucario', '⚡ Lucario'], ['dragonite', '🐲 Dragonite'],
          ['blastoise', '💧 Blastoise'], ['venusaur', '🌿 Venusaur'], ['pikachu', '⚡ Pikachu'],
          ['gyarados', '🌊 Gyarados'], ['alakazam', '🥄 Alakazam'], ['eevee', '🦊 Eevee'],
          ['snorlax', '💤 Snorlax'], ['umbreon', '🌙 Umbreon'], ['garchomp', '🦈 Garchomp'],
          ['lugia', '🕊️ Lugia']
        ];
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Espécie do Pokémon</label>
            <select id="cfg-pk-name" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
              ${pks.map(([id, label]) => `<option value="${id}" ${(params.pokemon || 'garchomp') === id ? 'selected' : ''}>${label}</option>`).join('')}
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Nível RPG</label>
              <input type="number" id="cfg-pk-level" min="1" max="100" value="${params.level || 100}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Versão Holográfica</label>
              <label class="flex items-center gap-2 mt-2 cursor-pointer text-slate-300">
                <input type="checkbox" id="cfg-pk-shiny" class="accent-brand-500" ${params.shiny !== false ? 'checked' : ''}>
                <span>✨ Modo Ultra Shiny</span>
              </label>
            </div>
          </div>
        `;
      } else if (sec.type === 'header') {
        const p = getDevProfile() || {};
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Texto do Banner / Letreiro</label>
            <input type="text" id="cfg-hdr-text" value="${escapeHtml(params.text || p.name || p.github || 'DEVELOPER')}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Estilo da Arte</label>
            <select id="cfg-hdr-font" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
              <option value="wordmark" ${(params.font || 'wordmark') === 'wordmark' ? 'selected' : ''}>Letreiro 3D em Wireframe Oscilante</option>
              <option value="slant" ${params.font === 'slant' ? 'selected' : ''}>Tipografia Slant (Alta Legibilidade)</option>
              <option value="isometric1" ${params.font === 'isometric1' ? 'selected' : ''}>Tipografia Isométrica 3D</option>
              <option value="doom" ${params.font === 'doom' ? 'selected' : ''}>Tipografia Doom (Heavy Metal)</option>
            </select>
          </div>
        `;
      } else if (sec.type === 'weather') {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Cidade / Localização</label>
            <input type="text" id="cfg-we-city" value="${escapeHtml(params.city || 'Curitiba, Brazil')}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
        `;
      } else if (sec.type === 'music') {
        html = `
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Título da Música</label>
              <input type="text" id="cfg-mu-title" placeholder="Resonance" value="${escapeHtml(params.title || '')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Artista</label>
              <input type="text" id="cfg-mu-artist" placeholder="HOME" value="${escapeHtml(params.artist || '')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Tema do Cassete</label>
            <select id="cfg-mu-preset" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
              <option value="synthwave" ${(params.preset || 'synthwave') === 'synthwave' ? 'selected' : ''}>🌆 Synthwave 80s (Rosa Neon / Roxo)</option>
              <option value="cyberpunk" ${params.preset === 'cyberpunk' ? 'selected' : ''}>⚡ Cyberpunk 2077 (Amarelo / Preto)</option>
              <option value="lofi" ${params.preset === 'lofi' ? 'selected' : ''}>☕ Lofi Chill (Verde Matcha / Pastel)</option>
              <option value="metal" ${params.preset === 'metal' ? 'selected' : ''}>🔥 Heavy Metal (Vermelho Sangue / Preto)</option>
            </select>
          </div>
        `;
      } else if (sec.type === 'badges') {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Tecnologias (separadas por vírgula)</label>
            <textarea id="cfg-bd-techs" rows="3" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">${escapeHtml(params.techs || 'python, typescript, rust, react, nextjs, fastapi, docker, postgresql, tailwind, linux, git')}</textarea>
          </div>
        `;
      } else if (sec.type === 'custom_svg') {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Título da Seção no README</label>
            <input type="text" id="cfg-cust-title" value="${escapeHtml(sec.title)}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Nome do Arquivo (no repositório GitHub)</label>
            <input type="text" id="cfg-cust-file" value="${escapeHtml(sec.file || 'custom-art.svg')}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
          </div>
          <div class="flex flex-col gap-1.5 pt-1">
            <label class="font-semibold text-slate-300 flex items-center justify-between">
              <span>Substituir Imagem / GIF / SVG</span>
              <span class="text-[10px] text-purple-400 font-mono">PNG, JPG, GIF, SVG</span>
            </label>
            <input type="file" accept="image/png,image/jpeg,image/gif,image/svg+xml,image/webp" onchange="handleCustomSvgUpload(event)" class="text-xs text-slate-400 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-purple-600/80 file:text-white file:font-semibold cursor-pointer">
            <div id="cfg-cust-preview-box" class="mt-2 p-2 bg-brand-surface rounded-lg border border-brand-border flex items-center gap-3">
              <div class="w-16 h-12 rounded border border-purple-500/30 overflow-hidden bg-brand-dark flex items-center justify-center">
                <img id="cfg-cust-preview" src="/api/builder/custom_svg/${sec.id || 'custom'}" class="max-w-full max-h-full object-contain" onerror="this.style.display='none'">
              </div>
              <div class="text-[11px] text-slate-300 flex-1">
                <span class="text-emerald-400 font-semibold block">✓ Arquivo Pronto para Exportar</span>
                <span class="text-[10px] text-slate-400">Embutido nativamente no pacote ZIP do perfil</span>
              </div>
            </div>
          </div>
        `;
      } else {
        html = `
          <div class="flex flex-col gap-1.5">
            <label class="font-semibold text-slate-300">Título no README</label>
            <input type="text" id="cfg-generic-title" value="${escapeHtml(sec.title)}" class="p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
          </div>
        `;
      }

      // Common layout & styling options for EVERY block
      const wVal = sec.width || '100%';
      const isPresetW = ['100%', '49%', '50%', '32%', '33%', '60%', '40%'].includes(wVal);
      const customW = !isPresetW ? wVal : (sec.custom_width || '');

      const layoutSectionHtml = `
        <div class="mt-4 pt-3 border-t border-brand-border/80 flex flex-col gap-3">
          <div class="text-[11px] font-bold uppercase tracking-wider text-sky-400 flex items-center justify-between">
            <span class="flex items-center gap-1.5"><span>📐</span> <span>Layout &amp; Dimensões no GitHub</span></span>
            <span class="text-[9.5px] px-2 py-0.5 rounded bg-sky-500/10 border border-sky-500/20 text-sky-300 font-mono">MULTI-COLUNA</span>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Largura / Disposição</label>
              <select id="cfg-block-width" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="100%" ${wVal === '100%' ? 'selected' : ''}>100% (Largura Total - Linha Única)</option>
                <option value="49%" ${wVal === '49%' || wVal === '50%' ? 'selected' : ''}>49% (Lado a Lado - 2 Colunas)</option>
                <option value="32%" ${wVal === '32%' || wVal === '33%' ? 'selected' : ''}>32% (Lado a Lado - 3 Colunas)</option>
                <option value="60%" ${wVal === '60%' ? 'selected' : ''}>60% (Destaque Largo)</option>
                <option value="40%" ${wVal === '40%' ? 'selected' : ''}>40% (Coluna Menor)</option>
                <option value="custom" ${!isPresetW ? 'selected' : ''}>Personalizada (px ou %)</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Largura Custom (se selecionada)</label>
              <input type="text" id="cfg-block-custom-width" placeholder="ex: 450px ou 70%" value="${escapeHtml(customW)}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Estilo de Apresentação</label>
              <select id="cfg-block-layout-mode" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
                <option value="inline" ${sec.layout_mode === 'inline' || !sec.layout_mode ? 'selected' : ''}>Padrão (Imagem Direta)</option>
                <option value="table_card" ${sec.layout_mode === 'table_card' ? 'selected' : ''}>🖼️ Moldura de Galeria (com Título)</option>
                <option value="details" ${sec.layout_mode === 'details' ? 'selected' : ''}>📁 Colapsável (&lt;details&gt;&lt;summary&gt;)</option>
              </select>
            </div>
            <div>
              <label class="font-semibold text-slate-300 block mb-1">Texto do Colapsável (se ativado)</label>
              <input type="text" id="cfg-block-details-summary" placeholder="▶ ✨ [ Clique para Expandir ]" value="${escapeHtml(sec.details_summary || '▶ ✨ [ Clique para Expandir o Acervo ]')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs">
            </div>
          </div>

          <div>
            <label class="font-semibold text-slate-300 block mb-1">Prompt de Terminal no Topo (Opcional)</label>
            <input type="text" id="cfg-block-terminal-prompt" placeholder="ex: vinicius@github ~ $ ./gallery.sh --sanctuary" value="${escapeHtml(sec.terminal_prompt || '')}" class="w-full p-2 bg-brand-dark border border-brand-border rounded-lg text-slate-200 text-xs font-mono">
          </div>
        </div>
      `;

      formEl.innerHTML = html + layoutSectionHtml;
      modal.classList.remove('hidden');
    }

    function handleCustomSvgUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      const isSvg = file.type === 'image/svg+xml' || file.name.toLowerCase().endsWith('.svg');
      const reader = new FileReader();
      reader.onload = function(evt) {
        if (editingBlockIdx !== null && builderSections[editingBlockIdx]) {
          const raw = evt.target.result;
          let svgPayload = '';
          if (isSvg && typeof raw === 'string' && raw.trim().startsWith('<svg')) {
            svgPayload = raw;
          } else {
            svgPayload = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 800 450" width="100%" height="100%">
  <image href="${raw}" xlink:href="${raw}" x="0" y="0" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"/>
</svg>`;
          }
          builderSections[editingBlockIdx].svg_data = svgPayload;
          const prev = document.getElementById('cfg-cust-preview');
          if (prev) {
            prev.src = isSvg ? 'data:image/svg+xml;utf8,' + encodeURIComponent(raw) : raw;
            prev.style.display = 'block';
          }
          showToast(`✓ Arquivo "${file.name}" carregado com sucesso!`);
        }
      };
      if (isSvg) {
        reader.readAsText(file);
      } else {
        reader.readAsDataURL(file);
      }
    }

    function saveBlockConfig() {
      if (editingBlockIdx === null || !builderSections[editingBlockIdx]) return;
      const sec = builderSections[editingBlockIdx];
      sec.params = sec.params || {};

      if (sec.type === 'snake') {
        sec.params.casing_color = document.getElementById('cfg-snake-casing') ? document.getElementById('cfg-snake-casing').value : 'navy';
        sec.params.display_mode = document.getElementById('cfg-snake-display') ? document.getElementById('cfg-snake-display').value : 'classic_lcd';
        sec.params.score = document.getElementById('cfg-snake-score') ? (parseInt(document.getElementById('cfg-snake-score').value, 10) || 420) : 420;
        sec.params.speed = document.getElementById('cfg-snake-speed') ? (parseFloat(document.getElementById('cfg-snake-speed').value) || 1.0) : 1.0;
      } else if (sec.type === 'pong') {
        sec.params.theme = document.getElementById('cfg-pong-theme') ? document.getElementById('cfg-pong-theme').value : 'classic_green';
        sec.params.score_p1 = document.getElementById('cfg-pong-s1') ? (parseInt(document.getElementById('cfg-pong-s1').value, 10) || 7) : 7;
        sec.params.score_p2 = document.getElementById('cfg-pong-s2') ? (parseInt(document.getElementById('cfg-pong-s2').value, 10) || 5) : 5;
      } else if (sec.type === 'flappy') {
        sec.params.theme = document.getElementById('cfg-flappy-theme') ? document.getElementById('cfg-flappy-theme').value : 'retro_arcade';
        sec.params.score = document.getElementById('cfg-flappy-score') ? (parseInt(document.getElementById('cfg-flappy-score').value, 10) || 12) : 12;
      } else if (sec.type === 'btop_monitor') {
        sec.params.theme = document.getElementById('cfg-btop-theme') ? document.getElementById('cfg-btop-theme').value : 'catppuccin';
        sec.params.uptime = document.getElementById('cfg-btop-uptime') ? document.getElementById('cfg-btop-uptime').value.trim() : '42 DAYS, 13:37:00';
      } else if (sec.type === 'cli_session') {
        sec.params.theme = document.getElementById('cfg-cli-theme') ? document.getElementById('cfg-cli-theme').value : 'ghostty';
        sec.params.terminal_title = document.getElementById('cfg-cli-title') ? document.getElementById('cfg-cli-title').value.trim() : 'ghostty@terminal: ~';
      } else if (sec.type === 'git_graph') {
        sec.params.theme = document.getElementById('cfg-git-theme') ? document.getElementById('cfg-git-theme').value : 'neon_cyber';
        sec.params.repo_name = document.getElementById('cfg-git-repo') ? document.getElementById('cfg-git-repo').value.trim() : 'core-engine';
      } else if (sec.type === 'cyber_id') {
        sec.params.theme = document.getElementById('cfg-cid-theme') ? document.getElementById('cfg-cid-theme').value : 'arasaka_red';
        sec.params.clearance_level = document.getElementById('cfg-cid-level') ? document.getElementById('cfg-cid-level').value.trim() : 'LEVEL 5 - ROOT';
        sec.params.role = document.getElementById('cfg-cid-role') ? document.getElementById('cfg-cid-role').value.trim() : 'Senior Lead Architect';
      } else if (sec.type === 'achievement') {
        sec.params.platform = document.getElementById('cfg-ach-plat') ? document.getElementById('cfg-ach-plat').value : 'xbox';
        sec.params.points = document.getElementById('cfg-ach-pts') ? (parseInt(document.getElementById('cfg-ach-pts').value, 10) || 100) : 100;
        sec.params.title = document.getElementById('cfg-ach-ttl') ? document.getElementById('cfg-ach-ttl').value.trim() : 'LENDÁRIO CODE ARCHITECT';
      } else if (sec.type === 'skill_tree') {
        sec.params.theme = document.getElementById('cfg-sk-theme') ? document.getElementById('cfg-sk-theme').value : 'cyber_constellation';
        sec.params.focus = document.getElementById('cfg-sk-focus') ? document.getElementById('cfg-sk-focus').value.trim() : 'Fullstack / Cloud / AI Architect';
      } else if (sec.type === 'chess') {
        sec.params.match = document.getElementById('cfg-chess-match').value;
        sec.params.speed = parseFloat(document.getElementById('cfg-chess-speed').value);
        sec.params.animated = document.getElementById('cfg-chess-anim').checked;
      } else if (sec.type === 'rpg' || sec.type === 'rpg_sheet') {
        sec.params.cls = document.getElementById('cfg-rpg-cls') ? document.getElementById('cfg-rpg-cls').value : 'alchemist';
        sec.params.level = document.getElementById('cfg-rpg-level') ? (parseInt(document.getElementById('cfg-rpg-level').value, 10) || 85) : 85;
        if (window._modalRpgCustomAvatar !== undefined) {
          sec.params.custom_avatar = window._modalRpgCustomAvatar;
        }
      } else if (sec.type === 'subway' || sec.type === 'git_subway') {
        sec.params.repo = document.getElementById('cfg-sub-repo') ? document.getElementById('cfg-sub-repo').value.trim() : 'core-platform';
      } else if (sec.type === 'pet' || sec.type === 'dev_pet') {
        sec.params.type = document.getElementById('cfg-pet-type') ? document.getElementById('cfg-pet-type').value : 'mametchi';
        sec.params.name = document.getElementById('cfg-pet-name') ? document.getElementById('cfg-pet-name').value.trim() : 'KERNEL';
        sec.params.casing_style = document.getElementById('cfg-pet-style') ? document.getElementById('cfg-pet-style').value : 'egg';
        sec.params.casing_color = document.getElementById('cfg-pet-color') ? document.getElementById('cfg-pet-color').value : 'cyber_blue';
      } else if (sec.type === 'mario') {
        sec.params.world = document.getElementById('cfg-mario-world') ? document.getElementById('cfg-mario-world').value.trim() : '1-1';
        sec.params.score = document.getElementById('cfg-mario-score') ? (parseInt(document.getElementById('cfg-mario-score').value, 10) || 2450) : 2450;
      } else if (sec.type === 'invaders' || sec.type === 'space_invaders') {
        sec.params.score = document.getElementById('cfg-invaders-score') ? (parseInt(document.getElementById('cfg-invaders-score').value, 10) || 1978) : 1978;
      } else if (sec.type === 'pacman') {
        sec.params.score = document.getElementById('cfg-pacman-score') ? (parseInt(document.getElementById('cfg-pacman-score').value, 10) || 333360) : 333360;
      } else if (sec.type === 'dvd') {
        sec.params.text = document.getElementById('cfg-dvd-text') ? document.getElementById('cfg-dvd-text').value.trim() : 'DVD';
        sec.params.speed = document.getElementById('cfg-dvd-speed') ? (parseFloat(document.getElementById('cfg-dvd-speed').value) || 1.0) : 1.0;
      } else if (sec.type === 'pokemon') {
        sec.params.pokemon = document.getElementById('cfg-pk-name').value;
        sec.params.level = parseInt(document.getElementById('cfg-pk-level').value, 10) || 100;
        sec.params.shiny = document.getElementById('cfg-pk-shiny').checked;
      } else if (sec.type === 'header') {
        sec.params.text = document.getElementById('cfg-hdr-text').value.trim();
        sec.params.font = document.getElementById('cfg-hdr-font').value;
      } else if (sec.type === 'weather') {
        sec.params.city = document.getElementById('cfg-we-city').value.trim();
      } else if (sec.type === 'music') {
        sec.params.title = document.getElementById('cfg-mu-title').value.trim();
        sec.params.artist = document.getElementById('cfg-mu-artist').value.trim();
        sec.params.preset = document.getElementById('cfg-mu-preset').value;
      } else if (sec.type === 'badges') {
        sec.params.techs = document.getElementById('cfg-bd-techs').value.trim();
      } else if (sec.type === 'custom_svg') {
        sec.title = document.getElementById('cfg-cust-title').value.trim() || 'Minha Arte SVG';
        sec.file = document.getElementById('cfg-cust-file').value.trim() || 'custom-art.svg';
      }

      // Save common layout & dimension options
      const chosenWidth = document.getElementById('cfg-block-width').value;
      const customWidth = document.getElementById('cfg-block-custom-width').value.trim();
      sec.width = chosenWidth === 'custom' && customWidth ? customWidth : chosenWidth;
      sec.custom_width = customWidth;
      sec.layout_mode = document.getElementById('cfg-block-layout-mode').value;
      sec.details_summary = document.getElementById('cfg-block-details-summary').value.trim();
      sec.terminal_prompt = document.getElementById('cfg-block-terminal-prompt').value.trim();

      saveStoredBuilderSections(builderSections);
      closeBlockConfigModal();
      renderReadmePreview();
      showToast(`✓ Bloco "${sec.title}" e layout salvos com sucesso!`);
    }

    function closeBlockConfigModal() {
      editingBlockIdx = null;
      const modal = document.getElementById('modal-block-config');
      if (modal) modal.classList.add('hidden');
    }

    // 1-Click Pin to Profile Feature
    function pinCurrentToProfile() {
      if (!currentSvg) {
        showToast("Nenhuma arte gerada no momento para fixar!");
        return;
      }

      const cleanFilename = (currentFilename || 'minha-arte.svg').replace(/[^a-zA-Z0-9._-]/g, '_');
      const blockTitle = cleanFilename.replace('.svg', '').replace(/[-_]/g, ' ').toUpperCase();

      const blockId = 'custom_' + Date.now();
      const isRpg = (currentFilename === 'rpg_sheet.svg' || currentFilename === 'rpg-sheet.svg');
      const newBlock = {
        id: blockId,
        type: isRpg ? 'rpg_sheet' : 'custom_svg',
        title: isRpg ? 'Passaporte RPG do Desenvolvedor' : `Arte: ${blockTitle}`,
        file: cleanFilename.endsWith('.svg') ? cleanFilename : `${cleanFilename}.svg`,
        icon: isRpg ? '⚔️' : '🖼️',
        enabled: true,
        width: '100%',
        layout_mode: 'inline',
        terminal_prompt: '',
        details_summary: '',
        svg_data: currentSvg,
        preview_url: `/api/builder/custom_svg/${blockId}`,
        params: {
          cls: document.getElementById('rpg-class') ? document.getElementById('rpg-class').value : 'alchemist',
          level: document.getElementById('rpg-level') ? (parseInt(document.getElementById('rpg-level').value, 10) || 85) : 85,
          custom_avatar: currentRpgAvatarDataUrl || null
        }
      };

      builderSections.push(newBlock);
      saveStoredBuilderSections(builderSections);
      showToast(`📌 Arte "${newBlock.title}" adicionada ao seu Construtor de Perfil!`, 3500);
    }

    function handleBlockDragStart(e, idx) {
      draggedBlockIdx = idx;
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', String(idx));
      const target = e.currentTarget;
      setTimeout(() => {
        if (target) {
          target.classList.add('opacity-30', 'border-brand-500', 'bg-brand-500/20', 'scale-[0.98]');
        }
      }, 0);
    }

    function handleBlockDragOver(e, idx) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    }

    function handleBlockDragEnter(e, idx) {
      e.preventDefault();
      if (idx === draggedBlockIdx) return;
      const el = e.currentTarget;
      el.classList.add('border-t-2', 'border-t-brand-400', 'bg-brand-500/10');
    }

    function handleBlockDragLeave(e, idx) {
      const el = e.currentTarget;
      el.classList.remove('border-t-2', 'border-t-brand-400', 'bg-brand-500/10');
    }

    function handleBlockDrop(e, targetIdx) {
      e.preventDefault();
      const el = e.currentTarget;
      el.classList.remove('border-t-2', 'border-t-brand-400', 'bg-brand-500/10');

      if (draggedBlockIdx === null || draggedBlockIdx === targetIdx) return;

      const item = builderSections.splice(draggedBlockIdx, 1)[0];
      builderSections.splice(targetIdx, 0, item);
      draggedBlockIdx = null;

      saveStoredBuilderSections(builderSections);
      renderReadmePreview();
      showToast(`✓ Bloco "${item.title}" reordenado!`, 1800);
    }

    function handleBlockDragEnd(e) {
      draggedBlockIdx = null;
      document.querySelectorAll('#builder-sections-list > div').forEach(el => {
        el.classList.remove('opacity-30', 'border-brand-500', 'bg-brand-500/20', 'scale-[0.98]', 'border-t-2', 'border-t-brand-400', 'bg-brand-500/10');
      });
    }

    function moveBuilderBlock(idx, dir) {
      const target = idx + dir;
      if (target < 0 || target >= builderSections.length) return;
      const temp = builderSections[idx];
      builderSections[idx] = builderSections[target];
      builderSections[target] = temp;
      saveStoredBuilderSections(builderSections);
      renderReadmePreview();
    }

    function toggleBuilderBlock(idx) {
      builderSections[idx].enabled = !builderSections[idx].enabled;
      saveStoredBuilderSections(builderSections);
      renderReadmePreview();
    }

    function removeBuilderBlock(idx) {
      builderSections.splice(idx, 1);
      saveStoredBuilderSections(builderSections);
      renderReadmePreview();
    }

    function addBuilderBlock() {
      const sel = document.getElementById('builder-add-select');
      if (!sel) return;
      const type = sel.value;
      const template = DEFAULT_BUILDER_BLOCKS.find(b => b.type === type);
      if (!template) return;

      const newBlock = JSON.parse(JSON.stringify(template));
      newBlock.enabled = true;
      if (type === 'custom_svg') {
        newBlock.id = 'custom_' + Date.now();
        newBlock.file = 'custom-art.svg';
        newBlock.icon = '🖼️';
        newBlock.title = 'Minha Arte Customizada';
        newBlock.svg_data = currentSvg || '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="100"><rect width="600" height="100" fill="#0d1117" rx="10"/><text x="300" y="55" fill="#58a6ff" text-anchor="middle" font-family="monospace">ARTE CUSTOMIZADA SVG</text></svg>';
      }
      builderSections.push(newBlock);
      saveStoredBuilderSections(builderSections);
      renderReadmePreview();
      showToast(`Bloco ${newBlock.title} adicionado!`);
    }

    function applyReadmePreset(preset) {
      if (typeof playMarioCoinSound === 'function') playMarioCoinSound();
      let ids = [];
      if (preset === 'cyberpunk') {
        ids = ['header', 'rpg', 'music', 'badges', 'coding_stats', 'neofetch'];
      } else if (preset === 'matrix') {
        ids = ['neofetch', 'coding_stats', 'badges', 'heatmap', 'diagram'];
      } else if (preset === 'gamer') {
        ids = ['mario', 'pet', 'invaders', 'pokemon', 'pacman', 'dvd', 'chess'];
      } else if (preset === 'minimal') {
        ids = ['header', 'subway', 'badges', 'chess', 'stats'];
      } else if (preset === 'devops') {
        ids = ['header', 'subway', 'badges', 'diagram', 'neofetch', 'heatmap'];
      }

      const newSections = JSON.parse(JSON.stringify(DEFAULT_BUILDER_BLOCKS));
      newSections.forEach(s => {
        s.enabled = ids.includes(s.id);
      });
      // Sort in the order of ids
      newSections.sort((a, b) => {
        const ia = ids.indexOf(a.id);
        const ib = ids.indexOf(b.id);
        if (ia !== -1 && ib !== -1) return ia - ib;
        if (ia !== -1) return -1;
        if (ib !== -1) return 1;
        return 0;
      });

      saveStoredBuilderSections(newSections);
      renderReadmePreview();
      showToast(`Template ${preset.toUpperCase()} aplicado!`);
    }

    function switchBuilderView(view) {
      activeBuilderView = view;
      ['visual', 'code', 'tree'].forEach(v => {
        document.getElementById(`builder-view-${v}`).classList.toggle('hidden', v !== view);
        const btn = document.getElementById(`btn-view-${v}`);
        if (btn) {
          if (v === view) {
            btn.classList.add('bg-brand-600', 'text-white');
            btn.classList.remove('bg-brand-dark/80', 'text-slate-300');
          } else {
            btn.classList.remove('bg-brand-600', 'text-white');
            btn.classList.add('bg-brand-dark/80', 'text-slate-300');
          }
        }
      });
    }

    async function renderReadmePreview() {
      const p = getDevProfile() || {};
      const user = p.github || p.name || 'developer';
      const name = p.name || user;
      const city = p.city || 'Curitiba, Brazil';

      // Update repo title in tree view
      const repoNameEl = document.getElementById('tree-repo-name');
      if (repoNameEl) repoNameEl.innerText = `${user} / ${user}`;

      const visualContainer = document.getElementById('builder-visual-content');
      const codeContainer = document.getElementById('builder-markdown-code');
      const treeContainer = document.getElementById('tree-files-list');

      if (visualContainer) {
        visualContainer.innerHTML = '<div class="text-brand-400 py-12 flex items-center justify-center gap-2"><span class="animate-spin text-xl">⏳</span> Carregando preview do perfil...</div>';
      }

      try {
        const res = await fetch('/api/builder/preview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: user,
            name: name,
            city: city,
            sections: builderSections
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          builderCurrentMarkdown = data.markdown;
          if (codeContainer) codeContainer.innerText = data.markdown;

          // Render Visual Cards
          const active = (data.sections && data.sections.length) ? data.sections.filter(s => s.enabled) : builderSections.filter(s => s.enabled);
          if (data.sections) {
            data.sections.forEach(ds => {
              const orig = builderSections.find(b => b.id === ds.id);
              if (orig) {
                if (orig.svg_data) ds.svg_data = orig.svg_data;
                orig.preview_url = ds.preview_url;
              }
            });
          }

          if (visualContainer) {
            visualContainer.innerHTML = `
              <div class="text-center w-full pb-3 border-b border-slate-800">
                <h1 class="text-2xl font-bold text-white mb-1">⚡ ${escapeHtml(name)}</h1>
                <p class="text-xs text-slate-400 mb-2">Software Engineer & Tech Explorer</p>
                <div class="inline-flex items-center gap-1 px-3 py-1 rounded bg-[#161b22] border border-slate-700 text-xs text-slate-300">
                  <span class="text-slate-400">GitHub:</span> <strong>@${escapeHtml(user)}</strong>
                </div>
              </div>
              <div class="w-full flex flex-col items-center gap-5">
                ${(() => {
                  // Group active blocks into rows
                  const visualRows = [];
                  let curRow = [];
                  let curWidthSum = 0;

                  function getNumWidth(w) {
                    if (!w) return 100;
                    const str = String(w).trim();
                    if (str.endsWith('%')) {
                      const parsed = parseFloat(str);
                      return isNaN(parsed) ? 100 : parsed;
                    }
                    return 100;
                  }

                  active.forEach(sec => {
                    const wNum = getNumWidth(sec.width);
                    const isDetails = sec.layout_mode === 'details';
                    if (isDetails || wNum >= 98) {
                      if (curRow.length > 0) {
                        visualRows.push(curRow);
                        curRow = [];
                        curWidthSum = 0;
                      }
                      visualRows.push([sec]);
                    } else {
                      const rowMode = curRow.length > 0 ? (curRow[0].layout_mode || 'inline') : (sec.layout_mode || 'inline');
                      if ((sec.layout_mode || 'inline') !== rowMode || (curWidthSum + wNum > 102)) {
                        if (curRow.length > 0) {
                          visualRows.push(curRow);
                          curRow = [];
                          curWidthSum = 0;
                        }
                      }
                      curRow.push(sec);
                      curWidthSum += wNum;
                    }
                  });
                  if (curRow.length > 0) visualRows.push(curRow);

                  function renderSingleVisual(s, countInRow) {
                    let imgSrc = s.preview_url;
                    if (!imgSrc) {
                      if (s.type === 'custom_svg') {
                        imgSrc = `/api/builder/custom_svg/${s.id || 'custom'}`;
                      } else if (s.type === 'header') {
                        imgSrc = `/api/render/wordmark?text=${encodeURIComponent((name || user).toUpperCase())}`;
                      } else {
                        imgSrc = `/api/render/${s.type}`;
                      }
                    }

                    const innerMedia = (s.type === 'custom_svg' && s.svg_data)
                      ? `<div class="w-full overflow-hidden flex justify-center [&>svg]:max-w-full [&>svg]:h-auto">${s.svg_data}</div>`
                      : `<img src="${imgSrc}" class="w-full h-auto rounded-lg" alt="${escapeHtml(s.title)}" />`;

                    let cssW = '100%';
                    if (countInRow === 2 || s.width === '49%' || s.width === '50%') {
                      cssW = 'calc(50% - 0.5rem)';
                    } else if (countInRow === 3 || s.width === '32%' || s.width === '33%') {
                      cssW = 'calc(33.333% - 0.5rem)';
                    } else if (s.width && s.width !== '100%') {
                      cssW = s.width;
                    }

                    if (s.layout_mode === 'table_card') {
                      return `
                        <div class="flex flex-col items-center rounded-2xl bg-slate-900/80 border border-slate-700/70 p-3 shadow-lg" style="width: ${cssW}; max-width: 100%;">
                          <div class="text-xs font-bold text-slate-200 mb-2 flex items-center gap-1.5 text-center">
                            <span>${s.icon || '🖼️'}</span> <span>${escapeHtml(s.title)}</span>
                          </div>
                          <div class="w-full overflow-hidden flex justify-center py-1">
                            ${innerMedia}
                          </div>
                        </div>
                      `;
                    }

                    return `
                      <div class="flex flex-col items-center" style="width: ${cssW}; max-width: 100%;">
                        <div class="w-full overflow-hidden flex justify-center py-1 [&>img]:shadow-md [&>img]:border [&>img]:border-slate-800/80">
                          ${innerMedia}
                        </div>
                      </div>
                    `;
                  }

                  return visualRows.map(row => {
                    const prompt = row.find(s => s.terminal_prompt)?.terminal_prompt;
                    const promptHtml = prompt ? `
                      <div class="w-full flex justify-center my-1.5">
                        <span class="px-3 py-1 rounded-xl bg-[#161b22] border border-slate-700 text-xs font-mono text-slate-300 shadow-sm">
                          <code>${escapeHtml(prompt)}</code>
                        </span>
                      </div>
                    ` : '';

                    if (row.length === 1 && row[0].layout_mode === 'details') {
                      const s = row[0];
                      const summaryTxt = s.details_summary || `▶ ✨ [ Clique para Expandir ${s.title} ]`;
                      return `
                        <div class="w-full flex flex-col items-center">
                          ${promptHtml}
                          <details class="w-full rounded-2xl bg-slate-900/60 border border-slate-800 p-3 shadow-md group">
                            <summary class="cursor-pointer font-bold text-xs text-sky-400 hover:text-sky-300 select-none py-1">
                              ${escapeHtml(summaryTxt)}
                            </summary>
                            <div class="pt-3 flex justify-center">
                              ${renderSingleVisual(s, 1)}
                            </div>
                          </details>
                        </div>
                      `;
                    }

                    return `
                      <div class="w-full flex flex-col items-center">
                        ${promptHtml}
                        <div class="w-full flex flex-row flex-wrap justify-center items-stretch gap-4 py-1">
                          ${row.map(s => renderSingleVisual(s, row.length)).join('')}
                        </div>
                      </div>
                    `;
                  }).join('');
                })()}
              </div>
              <div class="text-[11px] text-slate-500 pt-4 border-t border-slate-800 w-full text-center">
                ⚡ Built & Crafted with <a href="https://github.com/ViniciusNoetzold/Mezzold-TermArt" class="text-brand-400 hover:underline">Mezzold TermArt Studio</a>
              </div>
            `;
          }

          // Render Repository File Tree
          if (treeContainer) {
            const files = [
              { name: ".github/workflows/refresh-profile.yml", desc: "Automated telemetry sync workflow", size: "1.2 KB", type: "workflow" },
              { name: "README.md", desc: "Interactive profile showcase", size: `${(data.markdown.length / 1024).toFixed(1)} KB`, type: "md" },
              { name: ".gitignore", desc: "Python & temp files ignore", size: "32 B", type: "txt" },
              ...active.map(s => ({
                name: s.file,
                desc: `${s.title} SVG asset`,
                size: "~15 KB",
                type: "svg"
              }))
            ];

            const countEl = document.getElementById('tree-files-count');
            if (countEl) countEl.innerText = `${files.length} arquivos no repositório`;

            treeContainer.innerHTML = files.map(f => `
              <div class="flex items-center justify-between px-4 py-2.5 hover:bg-brand-card/40 transition">
                <div class="flex items-center gap-3">
                  <span class="text-slate-400">${f.type === 'svg' ? '🖼️' : (f.type === 'workflow' ? '⚙️' : '📄')}</span>
                  <span class="text-slate-200 font-bold hover:text-brand-400 transition cursor-pointer">${escapeHtml(f.name)}</span>
                </div>
                <div class="flex items-center gap-4 text-xs text-slate-500">
                  <span class="hidden sm:inline">${escapeHtml(f.desc)}</span>
                  <span class="px-2 py-0.5 rounded bg-brand-dark border border-brand-border text-slate-400 font-mono text-[10px]">${f.size}</span>
                </div>
              </div>
            `).join('');
          }
        }
      } catch (err) {
        if (visualContainer) visualContainer.innerHTML = '<div class="text-red-400 py-6">Erro ao conectar ao motor de preview. Tente novamente.</div>';
      }
    }

    async function downloadProfileZip() {
      if (typeof playMarioCoinSound === 'function') playMarioCoinSound();
      const p = getDevProfile() || {};
      const user = p.github || p.name || 'developer';
      const name = p.name || user;
      const city = p.city || 'Curitiba, Brazil';

      showToast("Criando pacote completo do repositório (.ZIP)...", 4000);

      try {
        const res = await fetch('/api/builder/download_zip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: user,
            name: name,
            city: city,
            sections: builderSections
          })
        });

        if (!res.ok) throw new Error("Falha ao gerar ZIP");

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${user}-github-profile.zip`;
        a.click();
        URL.revokeObjectURL(url);
        showToast("✓ Repositório baixado com sucesso! Extraia e faça o upload no GitHub.");
      } catch (err) {
        showToast("Erro ao gerar arquivo ZIP do repositório.", 3000);
      }
    }

    function copyReadmeMarkdown() {
      if (typeof playSwitchSound === 'function') playSwitchSound();
      if (!builderCurrentMarkdown) {
        showToast("Gere a pré-visualização primeiro!");
        return;
      }
      navigator.clipboard.writeText(builderCurrentMarkdown).then(() => {
        showToast("✓ Código do README.md copiado com sucesso!");
      }).catch(() => {
        showToast("Erro ao copiar para a área de transferência.");
      });
    }

    function openDeployInstructionsModal() {
      const p = getDevProfile() || {};
      const user = p.github || p.name || 'seu-usuario';
      const span = document.getElementById('deploy-modal-user');
      if (span) span.innerText = user;
      const modal = document.getElementById('modal-deploy-instructions');
      if (modal) modal.classList.remove('hidden');
    }

    function closeDeployInstructionsModal() {
      const modal = document.getElementById('modal-deploy-instructions');
      if (modal) modal.classList.add('hidden');
    }

    function renderBuilderTab() {
      builderSections = getStoredBuilderSections();
      renderBuilderSectionsList();
      // Switch canvas view
      document.getElementById('svg-display').classList.add('hidden');
      document.getElementById('builder-workspace').classList.remove('hidden');
      renderReadmePreview();
    }

    // Initialize defaults
    window.addEventListener('DOMContentLoaded', () => {
      loadVhsPreset();
      generate3d();
      const p = getDevProfile();
      if (p) {
        applyDevProfile(p);
      } else {
        // First access: open onboarding modal!
        openConfigModal();
      }
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/healthz")
@app.get("/health")
def healthz():
    return {"status": "ok", "service": "Mezzold TermArt", "version": "2.5.0"}

@app.get("/api/render/city")
def render_city(username: str = "developer", theme: str = "cyberpunk"):
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
    text: str = "MEZZOLD\nTERMART",
    font: str = "slant",
    theme: str = "cyberpunk",
    username: str = "developer",
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
    text = payload.get("text", "MEZZOLD\nTERMART")
    fonts = payload.get("fonts", ["slant", "isometric1", "doom"])
    theme = payload.get("theme", "cyberpunk")
    username = payload.get("username", "developer")
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
def render_heatmap(username: str = "developer"):
    p = registry.get("heatmap")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_hm.svg")
    p.run(username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/neofetch")
def render_neofetch(username: str = "developer", name: str = None, role: str = None):
    p = registry.get("neofetch")
    display_title = name if name else (username if username != "developer" else "Developer Profile")
    display_role = role if role else "Software Engineer & Terminal Enthusiast"
    rows = [
        ("Title", display_title, "#e3b341"),
        ("Role", display_role, "#c9d1d9"),
        ("Focus", "Systems, Terminal Art, Cloud & APIs", "#39c5cf"),
        ("Languages", "Python, TypeScript, Rust, Go, SQL", "#56d364"),
        ("GitHub", f"https://github.com/{username}", "#f0883e")
    ]
    tmp = os.path.join(os.path.dirname(__file__), "_temp_neo.svg")
    p.run(rows=rows, out_svg=tmp, username=username)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/stats")
def render_stats(username: str = "developer"):
    p = registry.get("stats_card")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_st.svg")
    p.run(username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/pokemon")
def render_pokemon(pokemon: str = "gengar", shiny: bool = False, level: int = 100, username: str = "trainer_vini"):
    import importlib
    from ...modules.profile import pokemon_card
    importlib.reload(pokemon_card)
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
def render_chess(match: str = "opera", animated: bool = True, speed: float = 1.0, username: str = "grandmaster", pgn: Optional[str] = None):
    import importlib
    from ...modules.profile import chess_board
    importlib.reload(chess_board)
    p = registry.get("chess_board")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_ch.svg")
    p.run(match=match, pgn=pgn, animated=animated, speed=speed, out_svg=tmp, username=username)
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
def render_pipes(num_pipes: int = 4, steps: int = 60, username: str = "developer"):
    p = registry.get("pipes")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_pi.svg")
    p.run(out_svg=tmp, username=username, num_pipes=num_pipes, steps=steps)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/tech_stack")
def render_tech_stack(techs: str = "python,typescript,rust,react,nextjs,fastapi,docker,postgresql,tailwind,linux,git", style: str = "neon", title: str = "TECH STACK & CORE ARSENAL", username: str = "developer"):
    p = registry.get("tech_stack")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_ts.svg")
    p.run(techs=techs, style=style, title=title, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/music")
def render_music(preset: str = "synthwave", title: str = None, artist: str = None, animated: bool = True, username: str = "audiophile"):
    p = registry.get("music_card")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_mu.svg")
    p.run(preset=preset, custom_title=title if title else None, custom_artist=artist if artist else None, animated=animated, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/coding_stats")
def render_coding_stats(hours: int = 1480, streak: int = 48, rank: str = "S+ Tier (Architect)", username: str = "developer"):
    p = registry.get("coding_stats")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_cs.svg")
    p.run(hours=int(hours), streak=int(streak), rank=rank, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/diagram")
def render_diagram(preset: str = "microservices", title: str = None, username: str = "architect"):
    p = registry.get("ascii_diagram")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_di.svg")
    p.run(preset=preset, title=title, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/dvd")
def render_dvd(text: str = "DVD", speed: float = 1.0, username: str = "retro_fan"):
    p = registry.get("dvd")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_dvd.svg")
    p.run(text=text, speed=float(speed), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/mario")
def render_mario(world: str = "1-1", score: int = 2450, coins: int = 14, username: str = "MARIO"):
    p = registry.get("mario")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_mario.svg")
    p.run(world=world, score=int(score), coins=int(coins), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/space_invaders")
def render_space_invaders(score: int = 1978, username: str = "defender"):
    p = registry.get("space_invaders")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_invaders.svg")
    p.run(score=int(score), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/pacman")
def render_pacman(score: int = 333360, username: str = "waka_waka"):
    p = registry.get("pacman")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_pacman.svg")
    p.run(score=int(score), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/starfield")
def render_starfield(warp_speed: float = 1.0, username: str = "skywalker"):
    p = registry.get("starfield")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_starfield.svg")
    p.run(warp_speed=float(warp_speed), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/cyberpunk_city")
@app.get("/api/render/skyline")
def render_cyberpunk_city(city_name: str = "NEO-TOKYO", username: str = "netrunner"):
    p = registry.get("cyberpunk_city")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_skyline.svg")
    p.run(city_name=city_name, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/rpg_sheet")
@app.get("/api/render/rpg")
def render_rpg_sheet(
    cls: str = "alchemist",
    level: int = 85,
    name: Optional[str] = None,
    hp: int = 96,
    mana: int = 91,
    stamina: int = 98,
    username: str = "hero",
    custom_avatar: Optional[str] = None
):
    p = registry.get("rpg_sheet")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_rpg_{os.getpid()}.svg")
    char_name = name if name else username.upper()
    p.run(
        character_name=char_name,
        rpg_class=cls,
        level=int(level),
        hp=int(hp),
        mana=int(mana),
        stamina=int(stamina),
        username=username,
        custom_avatar=custom_avatar,
        out_svg=tmp
    )
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/render/rpg_sheet")
@app.post("/api/render/rpg_sheet_custom")
def render_rpg_sheet_custom(payload: dict = Body(...)):
    p = registry.get("rpg_sheet")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_rpg_custom_{os.getpid()}.svg")
    cls = payload.get("cls", "alchemist")
    level = int(payload.get("level", 85))
    name = payload.get("name")
    hp = int(payload.get("hp", 96))
    mana = int(payload.get("mana", 91))
    stamina = int(payload.get("stamina", 98))
    username = payload.get("username", "hero")
    custom_avatar = payload.get("custom_avatar")

    char_name = name if name else username.upper()
    p.run(
        character_name=char_name,
        rpg_class=cls,
        level=level,
        hp=hp,
        mana=mana,
        stamina=stamina,
        username=username,
        custom_avatar=custom_avatar,
        out_svg=tmp
    )
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/git_subway")
@app.get("/api/render/subway")
def render_git_subway(repo: str = "core-platform", username: str = "commuter"):
    p = registry.get("git_subway")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_subway.svg")
    p.run(repo_name=repo, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/dev_pet")
@app.get("/api/render/pet")
def render_dev_pet(
    type: str = "mametchi",
    name: str = "KERNEL",
    level: int = 42,
    happiness: int = 98,
    coffee_level: int = 100,
    casing_color: str = "cyber_blue",
    casing_style: str = "egg",
    custom_color: str = None,
    username: str = "tamer"
):
    p = registry.get("dev_pet")
    tmp = os.path.join(os.path.dirname(__file__), "_temp_pet.svg")
    p.run(
        pet_name=name,
        pet_type=type,
        level=int(level),
        happiness=int(happiness),
        coffee_level=int(coffee_level),
        casing_color=casing_color,
        casing_style=casing_style,
        custom_color=custom_color,
        username=username,
        out_svg=tmp
    )
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/render/image")
async def render_image_upload(
    engine: str = Form("rgb_ascii"),
    username: str = Form("developer"),
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
        demo_src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "mezzold-logo.png" if engine == "signature" else "demo_cyber.png")
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
    username: str = Form("developer"),
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
        demo_src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "demo_cyber.png")
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
        "palette_swap": ("Palette Swap", "Catppuccin/GameBoy"),
        "rainbow_wave": ("Rainbow Wave", "Lolcat Arco-Íris"),
        "portrait": ("Retrato Terminal", "Braille Datagrama"),
        "signature": ("Caligrafia & Assinatura", "ASCII & Braille")
    }

    for eng in engine_list[:16]:
        p = registry.get(eng)
        if not p:
            continue
        try:
            tmp = os.path.join(tempfile.gettempdir(), f"_img_batch_{eng}_{os.getpid()}.svg")
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
            elif eng == "palette_swap":
                kwargs["theme"] = "catppuccin"
            elif eng == "portrait":
                kwargs["full_name"] = username
                kwargs["cols"] = min(cols, 80)

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
    engine: str = Form("mario"),
    mario_world: str = Form("1-1"),
    mario_score: int = Form(2450),
    invaders_score: int = Form(1978),
    pacman_score: int = Form(333360),
    snake_casing: str = Form("navy"),
    snake_display: str = Form("classic_lcd"),
    snake_score: int = Form(420),
    snake_speed: float = Form(1.0),
    pong_theme: str = Form("classic_green"),
    pong_score1: int = Form(7),
    pong_score2: int = Form(5),
    pong_speed: float = Form(1.0),
    flappy_theme: str = Form("retro_arcade"),
    flappy_score: int = Form(12),
    starfield_warp: float = Form(1.0),
    city_name: str = Form("NEO-TOKYO"),
    dvd_text: str = Form("DVD"),
    dvd_speed: float = Form(1.0),
    username: str = Form("developer"),
    num_pipes: int = Form(6),
    steps: int = Form(65),
    color_scheme: str = Form("matrix_green"),
    foliage_type: str = Form("sakura"),
    mascot: str = Form("cow"),
    message: str = Form("Stay curious and build epic things!"),
    url: str = Form("https://github.com"),
    label: str = Form("GITHUB PROFILE")
):
    p = registry.get(engine)
    if not p:
        p = registry.get("pipes")
    
    out_svg = os.path.join(os.path.dirname(__file__), f"_temp_fx_{engine}.svg")
    kwargs = {"out_svg": out_svg, "username": username}
    
    if engine == "snake":
        kwargs["casing_color"] = snake_casing
        kwargs["display_mode"] = snake_display
        kwargs["score"] = snake_score
        kwargs["speed"] = snake_speed
    elif engine == "pong":
        kwargs["theme"] = pong_theme
        kwargs["score_p1"] = pong_score1
        kwargs["score_p2"] = pong_score2
        kwargs["speed"] = pong_speed
    elif engine == "flappy":
        kwargs["theme"] = flappy_theme
        kwargs["score"] = flappy_score
    elif engine == "mario":
        kwargs["world"] = mario_world
        kwargs["score"] = mario_score
    elif engine == "space_invaders":
        kwargs["score"] = invaders_score
    elif engine == "pacman":
        kwargs["score"] = pacman_score
    elif engine == "starfield":
        kwargs["warp_speed"] = starfield_warp
    elif engine == "cyberpunk_city":
        kwargs["city_name"] = city_name
    elif engine == "dvd":
        kwargs["text"] = dvd_text
        kwargs["speed"] = dvd_speed
    elif engine == "pipes":
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
        demo_src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "assets", "demo_cyber.png")
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
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            port = int(env_port)
        except ValueError:
            pass
    url = f"http://localhost:{port}"
    print(f"\n[Mezzold TermArt Studio] Serving UI at {url}")
    print("Press Ctrl+C to stop the studio.\n")
    if not os.environ.get("PORT") and not os.environ.get("HEADLESS") and not os.environ.get("RENDER"):
        try:
            webbrowser.open(url)
        except Exception:
            pass
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


# ==========================================
# GITHUB PROFILE & README BUILDER ENDPOINTS
# ==========================================
from ...modules.profile import readme_builder

_BUILDER_CUSTOM_CACHE = {}

@app.get("/api/builder/custom_svg/{sec_id}")
def get_custom_svg(sec_id: str):
    svg = _BUILDER_CUSTOM_CACHE.get(sec_id, '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="60"><text x="200" y="35" fill="#58a6ff" text-anchor="middle">Custom SVG</text></svg>')
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/custom_svg")
def get_custom_svg_fallback():
    if _BUILDER_CUSTOM_CACHE:
        last_svg = list(_BUILDER_CUSTOM_CACHE.values())[-1]
        return Response(content=last_svg, media_type="image/svg+xml")
    return Response(content='<svg xmlns="http://www.w3.org/2000/svg" width="600" height="100"><rect width="600" height="100" fill="#0d1117" rx="10"/><text x="300" y="55" fill="#58a6ff" text-anchor="middle" font-family="monospace">ARTE FIXADA NO PERFIL</text></svg>', media_type="image/svg+xml")

@app.post("/api/builder/preview")
def builder_preview(payload: dict = Body(...)):
    import urllib.parse
    username = payload.get("username", "developer")
    name = payload.get("name", username)
    city = payload.get("city", "Curitiba, Brazil")
    sections = payload.get("sections", readme_builder.DEFAULT_SECTIONS)

    # Safe encoded parameters
    clean_name = name.strip() if name and name.strip() else username
    safe_name = urllib.parse.quote(clean_name.upper())
    safe_user = urllib.parse.quote(username.strip() if username else "developer")
    safe_city = urllib.parse.quote(city.strip() if city else "Curitiba, Brazil")
    
    # Generate live preview URLs for each section based on its custom params
    for sec in sections:
        stype = sec.get("type", "")
        params = sec.get("params") or {}

        if stype == "custom_svg":
            sec_id = sec.get("id", "custom")
            if sec.get("svg_data"):
                _BUILDER_CUSTOM_CACHE[sec_id] = sec.get("svg_data")
            sec["preview_url"] = f"/api/builder/custom_svg/{sec_id}"
        elif stype == "header":
            hdr_text = urllib.parse.quote((params.get("text") or clean_name).upper())
            hdr_font = params.get("font", "wordmark")
            if hdr_font == "wordmark":
                sec["preview_url"] = f"/api/render/wordmark?text={hdr_text}"
            else:
                sec["preview_url"] = f"/api/render/typography?text={hdr_text}&font={hdr_font}&username={safe_user}"
        elif stype == "badges":
            sec["preview_url"] = f"/api/render/tech_stack?username={safe_user}"
        elif stype == "heatmap":
            sec["preview_url"] = f"/api/render/heatmap?username={safe_user}"
        elif stype == "stats":
            sec["preview_url"] = f"/api/render/stats?username={safe_user}"
        elif stype == "neofetch":
            sec["preview_url"] = f"/api/render/neofetch?username={safe_user}&name={safe_name}"
        elif stype == "pokemon":
            pk = params.get("pokemon", "garchomp")
            shiny = str(params.get("shiny", True)).lower()
            lvl = params.get("level", 100)
            sec["preview_url"] = f"/api/render/pokemon?pokemon={pk}&shiny={shiny}&level={lvl}&username={safe_user}"
        elif stype == "coding_stats":
            hrs = params.get("hours", 1480)
            strk = params.get("streak", 48)
            sec["preview_url"] = f"/api/render/coding_stats?hours={hrs}&streak={strk}&username={safe_user}"
        elif stype == "music":
            preset = params.get("preset", "synthwave")
            title = urllib.parse.quote(params.get("title") or "")
            artist = urllib.parse.quote(params.get("artist") or "")
            sec["preview_url"] = f"/api/render/music?preset={preset}&title={title}&artist={artist}&username={safe_user}"
        elif stype == "chess":
            match = params.get("match", "opera")
            speed = params.get("speed", 1.0)
            anim = str(params.get("animated", True)).lower()
            sec["preview_url"] = f"/api/render/chess?match={match}&speed={speed}&animated={anim}&username={safe_user}"
        elif stype == "weather":
            w_city = urllib.parse.quote(params.get("city") or city)
            sec["preview_url"] = f"/api/render/weather?city={w_city}&username={safe_user}"
        elif stype == "diagram":
            preset = params.get("preset", "microservices")
            sec["preview_url"] = f"/api/render/diagram?preset={preset}&username={safe_user}"
        elif stype in ("rpg", "rpg_sheet"):
            r_cls = params.get("cls", "alchemist")
            r_lvl = params.get("level", 85)
            c_avatar = params.get("custom_avatar")
            if c_avatar:
                sec_id = sec.get("id", "rpg")
                p = registry.get("rpg_sheet")
                tmp = os.path.join(tempfile.gettempdir(), f"_temp_rpg_bld_{sec_id}_{os.getpid()}.svg")
                p.run(
                    character_name=clean_name.upper(),
                    rpg_class=r_cls,
                    level=int(r_lvl),
                    username=username,
                    custom_avatar=c_avatar,
                    out_svg=tmp
                )
                with open(tmp, "r", encoding="utf-8") as f:
                    _BUILDER_CUSTOM_CACHE[f"rpg_{sec_id}"] = f.read()
                sec["preview_url"] = f"/api/builder/custom_svg/rpg_{sec_id}"
            else:
                sec["preview_url"] = f"/api/render/rpg_sheet?cls={r_cls}&level={r_lvl}&name={safe_name}&username={safe_user}"
        elif stype in ("subway", "git_subway"):
            r_repo = urllib.parse.quote(params.get("repo", "core-platform"))
            sec["preview_url"] = f"/api/render/git_subway?repo={r_repo}&username={safe_user}"
        elif stype in ("pet", "dev_pet"):
            p_type = params.get("type", "mametchi")
            p_name = urllib.parse.quote(params.get("name", "KERNEL"))
            p_color = params.get("casing_color", "cyber_blue")
            p_style = params.get("casing_style", "egg")
            sec["preview_url"] = f"/api/render/dev_pet?type={p_type}&name={p_name}&casing_color={p_color}&casing_style={p_style}&username={safe_user}"
        elif stype == "mario":
            m_world = urllib.parse.quote(params.get("world", "1-1"))
            m_score = params.get("score", 2450)
            sec["preview_url"] = f"/api/render/mario?world={m_world}&score={m_score}&username={safe_user}"
        elif stype == "space_invaders":
            s_score = params.get("score", 1978)
            sec["preview_url"] = f"/api/render/space_invaders?score={s_score}&username={safe_user}"
        elif stype == "pacman":
            pa_score = params.get("score", 333360)
            sec["preview_url"] = f"/api/render/pacman?score={pa_score}&username={safe_user}"
        elif stype == "dvd":
            d_text = urllib.parse.quote(params.get("text", "DVD"))
            d_spd = params.get("speed", 1.0)
            sec["preview_url"] = f"/api/render/dvd?text={d_text}&speed={d_spd}&username={safe_user}"
        elif stype == "fortune":
            sec["preview_url"] = f"/api/render/fortune?username={safe_user}"
        elif stype == "snake":
            c_col = params.get("casing_color", "navy")
            d_mod = params.get("display_mode", "classic_lcd")
            spd = params.get("speed", 1.0)
            sc = params.get("score", 420)
            sec["preview_url"] = f"/api/render/snake?casing_color={c_col}&display_mode={d_mod}&speed={spd}&score={sc}&username={safe_user}"
        elif stype == "pong":
            thm = params.get("theme", "classic_green")
            s1 = params.get("score_p1", 7)
            s2 = params.get("score_p2", 5)
            spd = params.get("speed", 1.0)
            sec["preview_url"] = f"/api/render/pong?theme={thm}&score_p1={s1}&score_p2={s2}&speed={spd}&username={safe_user}"
        elif stype == "flappy":
            thm = params.get("theme", "retro_arcade")
            b_col = urllib.parse.quote(params.get("bird_color", "#ffcc00"))
            sc = params.get("score", 12)
            sec["preview_url"] = f"/api/render/flappy?theme={thm}&bird_color={b_col}&score={sc}&username={safe_user}"
        elif stype == "btop_monitor":
            thm = params.get("theme", "catppuccin")
            upt = urllib.parse.quote(params.get("uptime", "42 DAYS, 13:37:00"))
            sec["preview_url"] = f"/api/render/btop_monitor?theme={thm}&uptime={upt}&username={safe_user}"
        elif stype == "cli_session":
            thm = params.get("theme", "ghostty")
            ttl = urllib.parse.quote(params.get("terminal_title", f"{clean_name}@fedora: ~"))
            sec["preview_url"] = f"/api/render/cli_session?theme={thm}&terminal_title={ttl}&username={safe_user}"
        elif stype == "git_graph":
            thm = params.get("theme", "neon_cyber")
            r_repo = urllib.parse.quote(params.get("repo_name", f"{safe_user}/core-engine"))
            sec["preview_url"] = f"/api/render/git_graph?theme={thm}&repo_name={r_repo}&username={safe_user}"
        elif stype == "cyber_id":
            thm = params.get("theme", "arasaka_red")
            role = urllib.parse.quote(params.get("role", "Senior Lead Architect"))
            dept = urllib.parse.quote(params.get("department", "Cyber Defense & Cloud Infrastructure"))
            lvl = urllib.parse.quote(params.get("clearance_level", "LEVEL 5 - ROOT"))
            sec["preview_url"] = f"/api/render/cyber_id?name={safe_name}&role={role}&department={dept}&clearance_level={lvl}&theme={thm}&username={safe_user}"
        elif stype == "achievement":
            ttl = urllib.parse.quote(params.get("title", "LENDÁRIO CODE ARCHITECT"))
            pts = params.get("points", 100)
            rar = urllib.parse.quote(params.get("rarity", "0.1% RARO"))
            plat = params.get("platform", "xbox")
            sec["preview_url"] = f"/api/render/achievement?title={ttl}&points={pts}&rarity={rar}&platform={plat}&username={safe_user}"
        elif stype == "skill_tree":
            foc = urllib.parse.quote(params.get("focus", "Fullstack / Cloud / AI Architect"))
            thm = params.get("theme", "cyber_constellation")
            sec["preview_url"] = f"/api/render/skill_tree?focus={foc}&theme={thm}&username={safe_user}"

    readme_md = readme_builder.generate_readme_markdown(username, name, sections)
    return {
        "status": "success",
        "markdown": readme_md,
        "sections": sections
    }

@app.post("/api/builder/download_zip")
def builder_download_zip(payload: dict = Body(...)):
    username = payload.get("username", "developer")
    name = payload.get("name", username)
    city = payload.get("city", "Curitiba, Brazil")
    sections = payload.get("sections", readme_builder.DEFAULT_SECTIONS)
    
    zip_bytes = readme_builder.build_profile_bundle_zip(username, name, city, sections)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={username}-profile-repository.zip"}
    )


# ==========================================
# 10 EXPANDED ENGINES & MEDIA EXPORT ROUTES
# ==========================================

@app.get("/api/render/snake")
def render_snake(casing_color: str = "navy", display_mode: str = "classic_lcd", speed: float = 1.0, score: int = 420, username: str = "player"):
    p = registry.get("snake")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_snake_{os.getpid()}.svg")
    p.run(casing_color=casing_color, display_mode=display_mode, speed=float(speed), score=int(score), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/pong")
def render_pong(theme: str = "classic_green", score_p1: int = 7, score_p2: int = 5, speed: float = 1.0, username: str = "arcade"):
    p = registry.get("pong")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_pong_{os.getpid()}.svg")
    p.run(theme=theme, score_p1=int(score_p1), score_p2=int(score_p2), speed=float(speed), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/flappy")
def render_flappy(theme: str = "retro_arcade", bird_color: str = "#ffcc00", score: int = 12, username: str = "flapper"):
    p = registry.get("flappy")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_flappy_{os.getpid()}.svg")
    p.run(theme=theme, bird_color=bird_color, score=int(score), username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/btop_monitor")
def render_btop_monitor(theme: str = "catppuccin", uptime: str = "42 DAYS, 13:37:00", username: str = "root"):
    p = registry.get("btop_monitor")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_btop_{os.getpid()}.svg")
    p.run(theme=theme, uptime=uptime, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/cli_session")
def render_cli_session(theme: str = "ghostty", terminal_title: str = "ghostty@terminal: ~", username: str = "dev"):
    p = registry.get("cli_session")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_cli_{os.getpid()}.svg")
    p.run(theme=theme, terminal_title=terminal_title, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/git_graph")
def render_git_graph(repo_name: str = "core-engine", theme: str = "neon_cyber", username: str = "gitmaster"):
    p = registry.get("git_graph")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_git_graph_{os.getpid()}.svg")
    p.run(repo_name=repo_name, theme=theme, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/cyber_id")
def render_cyber_id(
    name: str = "V",
    role: str = "Senior Lead Architect",
    department: str = "Cyber Defense & Cloud Infrastructure",
    clearance_level: str = "LEVEL 5 - ROOT",
    theme: str = "arasaka_red",
    username: str = "netrunner"
):
    p = registry.get("cyber_id")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_cyber_id_{os.getpid()}.svg")
    p.run(
        name=name,
        role=role,
        department=department,
        clearance_level=clearance_level,
        theme=theme,
        username=username,
        out_svg=tmp
    )
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/achievement")
def render_achievement(
    title: str = "LENDÁRIO CODE ARCHITECT",
    description: str = "Deployou 1.000 microsserviços em produção numa sexta-feira sem quebrar",
    points: int = 100,
    rarity: str = "0.1% RARO",
    platform: str = "xbox",
    theme: Optional[str] = None,
    username: str = "gamer"
):
    p = registry.get("achievement")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_achievement_{os.getpid()}.svg")
    chosen_plat = platform or theme or "xbox"
    p.run(
        title=title,
        description=description,
        points=int(points),
        rarity=rarity,
        platform=chosen_plat,
        theme=chosen_plat,
        username=username,
        out_svg=tmp
    )
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/api/render/skill_tree")
def render_skill_tree(
    focus: str = "Fullstack / Cloud / AI Architect",
    theme: str = "cyber_constellation",
    username: str = "talents"
):
    p = registry.get("skill_tree")
    tmp = os.path.join(tempfile.gettempdir(), f"_temp_skill_tree_{os.getpid()}.svg")
    p.run(focus=focus, specialization=focus, theme=theme, username=username, out_svg=tmp)
    with open(tmp, "r", encoding="utf-8") as f:
        svg = f.read()
    return Response(content=svg, media_type="image/svg+xml")

@app.post("/api/export/gif")
def export_media_gif(payload: dict = Body(...)):
    svg_data = payload.get("svg") or payload.get("svg_data")
    if not svg_data:
        return JSONResponse({"status": "error", "message": "No SVG content provided"}, status_code=400)
    
    import time
    duration = float(payload.get("duration", 2.5))
    fps = int(payload.get("fps", 16))
    
    tmp_out = os.path.join(tempfile.gettempdir(), f"termart_{os.getpid()}_{int(time.time()*1000)}.gif")
    try:
        from ...modules.recorder.media_exporter import export_svg_to_media
        export_svg_to_media(svg_data, tmp_out, fmt="gif", duration=duration, fps=fps)
        return FileResponse(
            tmp_out,
            media_type="image/gif",
            filename="termart-animation.gif"
        )
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/export/mp4")
def export_media_mp4(payload: dict = Body(...)):
    svg_data = payload.get("svg") or payload.get("svg_data")
    if not svg_data:
        return JSONResponse({"status": "error", "message": "No SVG content provided"}, status_code=400)
    
    import time
    duration = float(payload.get("duration", 3.0))
    fps = int(payload.get("fps", 24))
    
    tmp_out = os.path.join(tempfile.gettempdir(), f"termart_{os.getpid()}_{int(time.time()*1000)}.mp4")
    try:
        from ...modules.recorder.media_exporter import export_svg_to_media
        export_svg_to_media(svg_data, tmp_out, fmt="mp4", duration=duration, fps=fps)
        return FileResponse(
            tmp_out,
            media_type="video/mp4",
            filename="termart-video.mp4"
        )
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
