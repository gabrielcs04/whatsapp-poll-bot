import sys
import subprocess
from gerador_config import gerar_json

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

def orquestrar():
    """
    Função principal que exibe o menu interativo e orquestra a execução dos sub-scripts
    (criador e leitor de enquetes) utilizando a biblioteca subprocess.
    
    Returns:
        None
    """
    print("="*60)
    print(" BEM-VINDO AO ORQUESTRADOR DE ENQUETES DO WHATSAPP")
    print("="*60)
    
    print("\nEscolha uma opção:")
    print("1 - Gerar novas enquetes e enviar no WhatsApp")
    print("2 - Ler resultados de enquetes existentes")
    print("3 - Sair")
    
    opcao = pedir_entrada_inteira("-> Digite a opção desejada: ", 1, 3)
    
    if opcao == 1:
        print("\nVamos gerar o seu arquivo de configuração (config.json) primeiro.")
        mes = pedir_entrada_inteira("-> Qual MÊS você deseja gerar? (Ex: 5 para Maio): ", 1, 12)
        ano = pedir_entrada_inteira("-> Qual ANO você deseja gerar? (Ex: 2026): ", 2000, 2100)
        
        nome_grupo_input = input("-> Qual o NOME DO GRUPO? (Deixe em branco para usar o padrão 'Acólitos S. João Batista'): ").strip()
        
        print("\n[Orquestrador] -> Iniciando o gerador_config...")
        if nome_grupo_input:
            gerar_json(mes, ano, nome_grupo_input)
        else:
            gerar_json(mes, ano)
        
        print("-" * 60)
        while True:
            iniciar_agora = input("As configurações estão prontas! Deseja abrir o navegador e enviar as enquetes AGORA? (S/N): ").strip().upper()
            if iniciar_agora in ['S', 'N']:
                break
            print("Digite apenas 'S' para sim ou 'N' para não.")
            
        if iniciar_agora == 'S':
            print("\n[Orquestrador] -> Executando o criador_enquete.py...")
            subprocess.run([sys.executable, "criador_enquete.py"])
            print("\n[Orquestrador] -> Fim da execução do robô.")
        else:
            print("\n[Orquestrador] -> Processo finalizado! Você pode rodar o 'criador_enquete.py' manualmente depois.")

    elif opcao == 2:
        print("\n[Orquestrador] -> Iniciando o leitor_enquete.py...")
        subprocess.run([sys.executable, "leitor_enquete.py"])
        print("\n[Orquestrador] -> Fim da leitura. O arquivo resultados_enquetes.txt foi gerado (ou atualizado) com sucesso.")
        
    elif opcao == 3:
        print("\nEncerrando...")
        sys.exit(0)

if __name__ == "__main__":
    orquestrar()
