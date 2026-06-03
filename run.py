import os
import sys
import subprocess
import venv
import hashlib
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
    new_venv = False
    if not venv_dir.exists():
        print_step("Criando o ambiente virtual (venv) isolado...")
        venv.create(venv_dir, with_pip=True)
        new_venv = True
    else:
        print_step("Ambiente virtual encontrado.")

    # 2. Verifica se as dependências já estão instaladas comparando o hash de requirements.txt
    requirements_file = base_dir / "requirements.txt"
    hash_file = venv_dir / "requirements.hash"
    
    current_hash = ""
    if requirements_file.exists():
        try:
            current_hash = hashlib.sha256(requirements_file.read_bytes()).hexdigest()
        except Exception:
            pass

    needs_install = True
    if not new_venv and hash_file.exists() and current_hash:
        try:
            saved_hash = hash_file.read_text().strip()
            if saved_hash == current_hash:
                needs_install = False
        except Exception:
            pass

    if needs_install:
        print_step("Instalando/Atualizando dependências...")
        # Atualiza o pip primeiro de forma silenciosa
        try:
            subprocess.check_call([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "-q"])
        except Exception as e:
            print(f"Aviso ao atualizar pip: {e}")
        
        # Instala o requirements.txt
        subprocess.check_call([str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)])

        # 3. Instala os navegadores do Playwright (Chromium)
        print_step("Verificando navegador para automação (Playwright Chromium)...")
        try:
            # Chama a versão do playwright instalada dentro da venv
            subprocess.check_call([str(venv_playwright), "install", "chromium"])
        except Exception as e:
            print(f"Aviso: Houve um pequeno problema na instalação automática do navegador. Detalhe: {e}")
            
        # Salva o hash para evitar instalações redundantes no futuro
        if current_hash:
            try:
                hash_file.write_text(current_hash)
            except Exception:
                pass
    else:
        print_step("Dependências e navegador já validados (usando cache de dependências).")

    # 4. Roda o script principal do projeto
    print_step("Iniciando o WhatsApp Bot Enquete...\n")
    main_script = base_dir / "src" / "main.py"
    if not main_script.exists():
        print("Erro: O arquivo 'main.py' não foi encontrado na pasta 'src' do projeto.")
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
