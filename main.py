import sys
import subprocess
from gerador_config import gerar_json

def pedir_entrada_inteira(mensagem, minimo, maximo):
    """
    Função auxiliar para garantir que o usuário digite um número válido.
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
    print("="*60)
    print(" BEM-VINDO AO ORQUESTRADOR DE ENQUETES DO WHATSAPP")
    print("="*60)
    
    # 1. Pergunta os dados da configuração
    print("\nVamos gerar o seu arquivo de configuração (config.json) primeiro.")
    mes = pedir_entrada_inteira("-> Qual MÊS você deseja gerar? (Ex: 5 para Maio): ", 1, 12)
    ano = pedir_entrada_inteira("-> Qual ANO você deseja gerar? (Ex: 2026): ", 2000, 2100)
    
    nome_grupo_input = input("-> Qual o NOME DO GRUPO? (Deixe em branco para usar o padrão 'ARQUIVOS IMPORTANTES'): ").strip()
    
    print("\n[Orquestrador] -> Iniciando o gerador_config...")
    
    # Chama a função geradora que está no outro arquivo
    if nome_grupo_input:
        gerar_json(mes, ano, nome_grupo_input)
    else:
        gerar_json(mes, ano)
    
    # 2. Pergunta sobre iniciar o bot
    print("-" * 60)
    while True:
        iniciar_agora = input("As configurações estão prontas! Deseja abrir o navegador e enviar as enquetes AGORA? (S/N): ").strip().upper()
        if iniciar_agora in ['S', 'N']:
            break
        print("Digite apenas 'S' para sim ou 'N' para não.")
        
    if iniciar_agora == 'S':
        print("\n[Orquestrador] -> Executando o criador_enquete.py...")
        # Usa subprocess para rodar o bot de forma limpa, forçando ele a ler o arquivo config.json recém atualizado
        subprocess.run([sys.executable, "criador_enquete.py"])
        print("\n[Orquestrador] -> Fim da execução do robô.")
    else:
        print("\n[Orquestrador] -> Processo finalizado! Você pode rodar o 'criador_enquete.py' manualmente depois.")

if __name__ == "__main__":
    orquestrar()
