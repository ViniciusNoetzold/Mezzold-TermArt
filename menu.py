#!/usr/bin/env python3
"""
Mezzold TermArt Suite - Interactive Terminal Hub
Beautiful interactive console for generating terminal art, 3D animations, and profile cards.
"""
import os
import sys
import subprocess
import webbrowser

# Enable ANSI colors in Windows terminal
os.system("")

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = f"""{CYAN}
 =============================================================================
   __  __                         _      _____                     _         _   
  |  \/  |                       | |    |_   _|                   / \   _ __| |_ 
  | |\/| | ___ ___________  _  __| |______| | ___ _ __ _ __ ___  / _ \ | '__| __|
  | |  | |/ _ \_  /_  / _ \| |/ _` |______| |/ _ \ '__| '_ ` _ \/ ___ \| |  | |_ 
  |_|  |_|\___//__//__\___/|_|\__,_|      |_|\___/_|  |_| |_| /_/   \_\_|   \__|
{RESET}{BOLD}              Mezzold Studios — Ultimate Terminal Profile Suite v2.0{RESET}
{CYAN} ============================================================================={RESET}
"""

MENU = f"""
  {YELLOW}[1]{RESET}  {WHITE}Iniciar Web Studio no Navegador{RESET} {DIM}(Dashboard visual interativo){RESET}
  {YELLOW}[2]{RESET}  {WHITE}Gerar Cidade 3D Isométrica de Commits{RESET} {DIM}(contrib-3d-city.svg){RESET}
  {YELLOW}[3]{RESET}  {WHITE}Gerar Letreiro 3D em Wireframe Oscilante{RESET} {DIM}(wordmark.svg){RESET}
  {YELLOW}[4]{RESET}  {WHITE}Gerar Heatmap em Cascata em Tempo Real{RESET} {DIM}(contrib-heatmap.svg){RESET}
  {YELLOW}[5]{RESET}  {WHITE}Gerar Banner com Nome em Tipografia ASCII Slant{RESET} {DIM}(name-banner.svg){RESET}
  {YELLOW}[6]{RESET}  {WHITE}Gerar Card de Specs Neofetch{RESET} {DIM}(info-card.svg){RESET}
  {YELLOW}[7]{RESET}  {WHITE}Gerar Card de Estatísticas Dark Mode{RESET} {DIM}(stats-card.svg){RESET}
  {YELLOW}[8]{RESET}  {WHITE}Gerar Animação Procedural dos Tubos Retrô{RESET} {DIM}(pipes.svg){RESET}
  {YELLOW}[9]{RESET}  {WHITE}Listar Todos os Motores & Plugins Registrados{RESET}
  {CYAN}[T]{RESET}  {WHITE}Abrir Prompt de Comando Livre (CLI){RESET}
  {MAGENTA}[0]{RESET}  {WHITE}Sair{RESET}
{CYAN} ============================================================================={RESET}
"""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def run_cmd(cmd):
    print(f"\n{DIM}[Executando: {cmd}]{RESET}")
    subprocess.run(cmd, shell=True)

def main():
    while True:
        clear()
        print(BANNER)
        print(MENU)
        try:
            choice = input(f" {BOLD}Escolha uma opção [0-9 ou T]: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAté logo!")
            break

        if choice == "1":
            print(f"\n{GREEN}✓ Abrindo Web Studio em http://localhost:7860...{RESET}")
            webbrowser.open("http://localhost:7860")
            run_cmd("python termstudio.py")
        elif choice == "2":
            user = input(f" Usuário GitHub {DIM}[Enter para ViniciusNoetzold]{RESET}: ").strip() or "ViniciusNoetzold"
            run_cmd(f"python termart.py city {user} --out contrib-3d-city.svg")
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice == "3":
            text = input(f" Texto do Letreiro 3D {DIM}[Enter para MEZZOLD\\nSTUDIOS]{RESET}: ").strip() or r"MEZZOLD\nSTUDIOS"
            run_cmd(f'python termart.py wordmark --text "{text}" --out wordmark.svg')
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice == "4":
            user = input(f" Usuário GitHub {DIM}[Enter para ViniciusNoetzold]{RESET}: ").strip() or "ViniciusNoetzold"
            run_cmd(f"python termart.py heatmap {user} --out contrib-heatmap.svg")
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice == "5":
            text = input(f" Nome em ASCII {DIM}[Enter para VINICIUS\\nNOETZOLD]{RESET}: ").strip() or r"VINICIUS\nNOETZOLD"
            run_cmd(f'python termart.py text --text "{text}" --font slant --out name-banner.svg')
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice == "6":
            user = input(f" Usuário GitHub {DIM}[Enter para ViniciusNoetzold]{RESET}: ").strip() or "ViniciusNoetzold"
            run_cmd(f"python termart.py neofetch --username {user} --out info-card.svg")
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice == "7":
            user = input(f" Usuário GitHub {DIM}[Enter para ViniciusNoetzold]{RESET}: ").strip() or "ViniciusNoetzold"
            run_cmd(f"python termart.py stats {user} --out stats-card.svg")
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice == "8":
            run_cmd("python termart.py pipes --out pipes.svg")
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice == "9":
            clear()
            run_cmd("python termart.py plugins")
            input(f"\n{DIM}Pressione Enter para voltar ao menu...{RESET}")
        elif choice.upper() == "T":
            clear()
            print(f"{CYAN}Modo Terminal Livre - Digite comandos termart diretamente (ex: python termart.py --help){RESET}")
            print(f"{DIM}Digite 'exit' para retornar ao menu.{RESET}\n")
            if os.name == "nt":
                subprocess.run('cmd /k "prompt termart$G "', shell=True)
            else:
                subprocess.run("bash", shell=True)
        elif choice == "0":
            print(f"\n{GREEN}Obrigado por usar Mezzold TermArt Suite!{RESET}\n")
            break
        else:
            print(f"\n{YELLOW}Opção inválida! Escolha de 0 a 9 ou T.{RESET}")
            input(f"{DIM}Pressione Enter para continuar...{RESET}")

if __name__ == "__main__":
    main()
