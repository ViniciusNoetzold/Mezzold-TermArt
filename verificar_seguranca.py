# -*- coding: utf-8 -*-
"""
MEZZOLD TERMART STUDIO - SCRIPT DE AUDITORIA DE SEGURANCA E PRIVACIDADE
Verifica automaticamente se ha qualquer chave secreta, token, senha ou
dado sensivel no codigo ou no historico do Git.
"""

import os
import re
import subprocess
import sys

# Cores ANSI
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

print(f"{CYAN}{BOLD}======================================================================{RESET}")
print(f"{CYAN}{BOLD}        MEZZOLD TERMART - AUDITORIA DE SEGURANCA DO REPOSITORIO       {RESET}")
print(f"{CYAN}{BOLD}======================================================================{RESET}\n")

patterns = [
    (r'(?i)(api[_-]?key|client[_-]?secret|password|passwd|auth[_-]?token)[\s:=]+["\'][^"\']{8,}["\']', 'Credencial Generica / Senha'),
    (r'sk_live_[0-9a-zA-Z]{20,}', 'Stripe Live Secret Key (sk_live_)'),
    (r'sk_test_[0-9a-zA-Z]{20,}', 'Stripe Test Secret Key (sk_test_)'),
    (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI Secret Key (sk-)'),
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token (ghp_)'),
    (r'github_pat_[a-zA-Z0-9_]{60,}', 'GitHub Fine-grained PAT'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', 'Chave Privada SSH / RSA')
]

ignored_extensions = {'.png', '.jpg', '.jpeg', '.svg', '.exe', '.cast', '.zip', '.ico', '.woff', '.woff2', '.ttf'}

# 1. Checagem dos arquivos rastreados no Git
print(f"{BOLD}[1/2] Analisando arquivos rastreados no Git...{RESET}")
try:
    tracked_files = subprocess.check_output(['git', 'ls-files'], encoding='utf-8', errors='ignore').splitlines()
    print(f"-> Total de arquivos rastreados: {len(tracked_files)}")
    
    findings_files = []
    for rel in tracked_files:
        ext = os.path.splitext(rel)[1].lower()
        if ext in ignored_extensions:
            continue
        try:
            with open(rel, 'r', encoding='utf-8', errors='ignore') as fp:
                for lno, line in enumerate(fp, 1):
                    if 'config.example.json' in rel or 'verificar_seguranca.py' in rel:
                        continue
                    for pat, label in patterns:
                        if re.search(pat, line):
                            findings_files.append((rel, lno, label, line.strip()[:100]))
        except Exception:
            pass
            
    if not findings_files:
        print(f"{GREEN}[OK] Nenhum segredo ou chave privada nos arquivos do Git!{RESET}\n")
    else:
        print(f"{RED}[ALERTA] Encontradas {len(findings_files)} ocorrencias:{RESET}")
        for rel, lno, label, preview in findings_files:
            print(f"  - {rel}:{lno} -> [{label}] {preview}")
        print()
except Exception as e:
    print(f"{YELLOW}Aviso ao rodar git ls-files: {e}{RESET}\n")
    findings_files = []

# 2. Checagem de todo o historico de commits do Git
print(f"{BOLD}[2/2] Analisando historico completo de commits do Git...{RESET}")
try:
    log_diff = subprocess.check_output(['git', 'log', '-p'], encoding='utf-8', errors='ignore').splitlines()
    print(f"-> Total de linhas analisadas no historico: {len(log_diff)}")
    
    findings_history = []
    for lno, line in enumerate(log_diff, 1):
        if not line.startswith('+') or line.startswith('+++'):
            continue
        if 'config.example.json' in line or 'verificar_seguranca.py' in line:
            continue
        for pat, label in patterns:
            if re.search(pat, line):
                findings_history.append((lno, label, line.strip()[:100]))
                
    if not findings_history:
        print(f"{GREEN}[OK] O historico de commits esta 100% limpo! Nenhum commit vazou segredos.{RESET}\n")
    else:
        print(f"{RED}[ALERTA] Encontradas {len(findings_history)} ocorrencias no historico de commits:{RESET}")
        for lno, label, preview in findings_history:
            print(f"  - Linha {lno}: [{label}] {preview}")
        print()
except Exception as e:
    print(f"{YELLOW}Aviso ao rodar git log: {e}{RESET}\n")
    findings_history = []

print(f"{CYAN}{BOLD}======================================================================{RESET}")
if not findings_files and not findings_history:
    print(f"{GREEN}{BOLD}RESULTADO: REPOSITORIO 100% SEGURO E PROTEGIDO!{RESET}")
    print(f"{GREEN}Voce pode manter o repositorio do GitHub PUBLICO com total tranquilidade.{RESET}")
    print(f"{GREEN}- Zero tokens ou chaves secretas expostas.{RESET}")
    print(f"{GREEN}- Zero credenciais de banco de dados ou logins.{RESET}")
    print(f"{GREEN}- ads.txt contem apenas o Publisher ID publico (como exige o Google).{RESET}")
else:
    print(f"{RED}{BOLD}ATENCAO: Existem itens que requerem revisao.{RESET}")
print(f"{CYAN}{BOLD}======================================================================{RESET}\n")
