import os
import sys
import subprocess
import venv
from pathlib import Path

def print_step(msg):
    """
    Imprime mensagens de log formatadas com cor azul clara/ciano no terminal (se suportado).
    
    Args:
        msg (str): A mensagem a ser impressa na tela.
        
    Returns:
        None
    """
    # Imprime com cor azul clara/ciano no terminal (se suportado)
    print(f"\n\033[1;36m>>> {msg}\033[0m")

def main():
    """
    Ponto de entrada do script de inicialização do bot.
    Garante que um ambiente virtual (.venv) local seja criado, que as dependências 
    estejam instaladas, que o Chromium do Playwright esteja configurado e, 
    por fim, inicia o script principal (main.py).
    
    Returns:
        None
    """
    base_dir = Path(__file__).resolve().parent
    venv_dir = base_dir / "venv"
    
    # Determina o caminho do executável do Python dentro da venv de acordo com o OS
    if os.name == 'nt': # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_playwright = venv_dir / "Scripts" / "playwright.exe"
    else: # Mac/Linux
        venv_python = venv_dir / "bin" / "python"
        venv_playwright = venv_dir / "bin" / "playwright"

    # 1. Cria a venv se não existir
    if not venv_dir.exists():
        print_step("Criando o ambiente virtual (venv) isolado...")
        venv.create(venv_dir, with_pip=True)
    else:
        print_step("Ambiente virtual encontrado.")

    # 2. Instala/Atualiza as dependências
    print_step("Verificando e instalando dependências...")
    # Atualiza o pip primeiro de forma silenciosa
    subprocess.check_call([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "-q"])
    # Instala o requirements.txt
    subprocess.check_call([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"])

    # 3. Instala os navegadores do Playwright (Chromium)
    print_step("Verificando navegador para automação (Playwright Chromium)...")
    try:
        # Chama a versão do playwright instalada dentro da venv
        subprocess.check_call([str(venv_playwright), "install", "chromium"])
    except Exception as e:
        print(f"Aviso: Houve um pequeno problema na instalação automática do navegador. Detalhe: {e}")

    # 4. Roda o script principal do projeto
    print_step("Iniciando o WhatsApp Bot Enquete...\n")
    main_script = base_dir / "main.py"
    if not main_script.exists():
        print("Erro: O arquivo 'main.py' não foi encontrado na pasta do projeto.")
        sys.exit(1)
        
    try:
        # Repassa o controle da execução para o main.py rodando dentro da venv
        subprocess.check_call([str(venv_python), str(main_script)])
    except KeyboardInterrupt:
        print("\n\nProcesso finalizado com sucesso pelo usuário.")
    except subprocess.CalledProcessError as e:
        print(f"\nO processo foi encerrado ou encontrou um erro.")

if __name__ == "__main__":
    main()
