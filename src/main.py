import sys
import subprocess
from pathlib import Path
from config.gerador_config import gerar_json

def pedir_entrada_inteira(mensagem, minimo, maximo):
    """
    Função auxiliar para solicitar e validar a entrada numérica do usuário.
    Garante que o valor digitado esteja dentro do intervalo permitido.
    
    Args:
        mensagem (str): A mensagem/prompt a ser exibida para o usuário.
        minimo (int): O valor mínimo aceito.
        maximo (int): O valor máximo aceito.
        
    Returns:
        int: O valor validado escolhido pelo usuário.
    """
    while True:
        try:
            valor = input(mensagem).strip()
            # Permite cancelamento
            if valor.lower() == 'sair':
                sys.exit(0)
                
            valor = int(valor)
            if minimo <= valor <= maximo:
                return valor
            else:
                print(f"[!] Por favor, insira um valor numérico entre {minimo} e {maximo}.")
        except ValueError:
            print("[!] Entrada inválida. Digite apenas números.")

def gerar_enquetes():
    """
    Solicita mês, ano e nome do grupo ao usuário, e executa a geração das enquetes,
    salvando o resultado em 'dados/enquetes.json'.
    Não realiza nenhum envio pelo WhatsApp.
    
    Returns:
        None
    """
    print("\nVamos gerar as enquetes para o mês desejado.")
    mes = pedir_entrada_inteira("-> Qual MÊS você deseja gerar? (Ex: 5 para Maio): ", 1, 12)
    ano = pedir_entrada_inteira("-> Qual ANO você deseja gerar? (Ex: 2026): ", 2000, 2100)
    
    nome_grupo_input = input("-> Qual o NOME DO GRUPO? (Deixe em branco para usar o padrão 'Acólitos S. João Batista'): ").strip()
    
    print("\n[Orquestrador] -> Iniciando a geração das enquetes...")
    if nome_grupo_input:
        gerar_json(mes, ano, nome_grupo_input)
    else:
        gerar_json(mes, ano)
    
    print("\n[Orquestrador] -> Enquetes geradas com sucesso em 'dados/enquetes.json'.")
    print("[Orquestrador] -> Revise o arquivo e use a opção 2 para enviar pelo WhatsApp.")

def enviar_enquetes(base_path):
    """
    Lê as enquetes já geradas em 'dados/enquetes.json' e executa o envio
    pelo WhatsApp via automação do navegador.
    Não gera novas enquetes.
    
    Args:
        base_path (Path): Caminho base do diretório 'src/'.
        
    Returns:
        None
    """
    print("\n[Orquestrador] -> Executando o envio das enquetes pelo WhatsApp...")
    subprocess.run([sys.executable, str(base_path / "automation" / "criador_enquete.py")])
    print("\n[Orquestrador] -> Fim da execução do robô.")

def orquestrar():
    """
    Função principal que exibe o menu interativo e orquestra a execução das etapas
    de geração e envio de enquetes, além da leitura de resultados.
    
    Returns:
        None
    """
    print("="*60)
    print(" BEM-VINDO AO ORQUESTRADOR DE ENQUETES DO WHATSAPP")
    print("="*60)
    
    base_path = Path(__file__).parent
    
    while True:
        print("\n+--------------------------------------------------------+")
        print("|  Escolha uma opção:                                    |")
        print("|    1 - Gerar novas enquetes                            |")
        print("|    2 - Enviar as enquetes existentes pelo WhatsApp     |")
        print("|    3 - Ler resultados de enquetes existentes           |")
        print("|    4 - Sair                                            |")
        print("+--------------------------------------------------------+")
        
        opcao = pedir_entrada_inteira("-> Digite a opção desejada: ", 1, 4)
        
        if opcao == 1:
            gerar_enquetes()
            
        elif opcao == 2:
            enviar_enquetes(base_path)

        elif opcao == 3:
            print("\n[Orquestrador] -> Iniciando o leitor_enquete.py...")
            subprocess.run([sys.executable, str(base_path / "automation" / "leitor_enquete.py")])
            print("\n[Orquestrador] -> Fim da leitura. O arquivo .csv foi gerado (ou atualizado) com sucesso.")
            
        elif opcao == 4:
            print("\nEncerrando...")
            sys.exit(0)

if __name__ == "__main__":
    orquestrar()
