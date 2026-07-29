import os
import time
import json
from pathlib import Path

# Raiz do projeto: whatsapp_utils.py está em src/automation/, então sobe 2 níveis
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
SESSAO_DIR = str(_RAIZ_PROJETO / "dados" / "sessao_whatsapp")
CONFIG_PATH = str(_RAIZ_PROJETO / "dados" / "config.json")

def print_log(mensagem):
    """
    Função auxiliar para imprimir logs no terminal com o horário atual.
    
    Args:
        mensagem (str): A mensagem de texto a ser impressa.
    """
    horario = time.strftime('%H:%M:%S')
    print(f"[{horario}] {mensagem}")

def carregar_configuracoes():
    """
    Lê o arquivo 'dados/config.json' e retorna as configurações globais do projeto.
    
    Returns:
        tuple: (nome_grupo, enquetes_json) contendo o nome do grupo como string 
               e as enquetes como uma lista de dicionários.
    """
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            nome_grupo = config_data.get("nome_grupo", "")
            enquetes_json = config_data.get("enquetes", [])
            return nome_grupo, enquetes_json
    except FileNotFoundError:
        print_log(f"[ERRO] Arquivo de configuração não encontrado: {CONFIG_PATH}")
        return "", []

def iniciar_navegador(playwright_context):
    """
    Inicia o navegador Chromium usando contexto persistente para retenção do login.
    O navegador é iniciado em inglês para garantir compatibilidade dos seletores aria-label.
    
    Args:
        playwright_context (PlaywrightContextManager): Contexto do Playwright.
        
    Returns:
        tuple: (browser_context, page) O contexto do navegador e a página criada.
    """
    print_log("Iniciando navegador...")
    if not os.path.exists(SESSAO_DIR):
        os.makedirs(SESSAO_DIR)

    browser_context = playwright_context.chromium.launch_persistent_context(
        user_data_dir=SESSAO_DIR,
        headless=False,  # Precisamos ver o navegador
        locale="en-US",  # Força idioma inglês para garantir compatibilidade dos seletores
        timezone_id="America/Sao_Paulo",
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--start-maximized",
            "--lang=en-US",  # Força idioma do Chrome em inglês
        ],
        no_viewport=True
    )
    
    page = browser_context.pages[0]
    page.set_default_timeout(60000)
    
    return browser_context, page

def fechar_banner_novidades(page):
    """
    Verifica se o WhatsApp exibiu um banner de novidades após o login e,
    caso esteja presente, fecha-o clicando no botão de fechar (aria-label="Close").

    Args:
        page (Page): Instância da página do Playwright.
    """
    SELETOR_BANNER_FECHAR = 'button[aria-label="Close"]'
    try:
        botao_fechar = page.locator(SELETOR_BANNER_FECHAR).first
        botao_fechar.wait_for(state="visible", timeout=5000)
        botao_fechar.click()
        print_log("Banner de novidades detectado e fechado.")
        page.wait_for_timeout(1000)  # Pequena pausa após fechar o banner
    except Exception:
        pass  # Banner não apareceu, segue normalmente


def abrir_whatsapp_e_aguardar_login(page):
    """
    Acessa a página principal do WhatsApp Web e aguarda o carregamento do painel principal,
    comprovando que o usuário está corretamente autenticado.

    A lógica de espera é feita em duas etapas:
    1. Aguarda até 30s para saber se já há sessão salva (painel carrega direto) 
       ou se é necessário escanear o QR code.
    2. Se precisar de QR, aguarda até 10 minutos para o painel carregar após o scan.
    
    Args:
        page (Page): Instância da página do Playwright.
        
    Returns:
        bool: True se o login foi concluído e carregado, False caso contrário.
    """
    print_log("Acessando o WhatsApp Web.")
    page.goto('https://web.whatsapp.com/', wait_until='domcontentloaded')
    
    # Seletor confiável: #pane-side é o painel esquerdo com a lista de conversas,
    # que SÓ aparece quando o usuário está completamente logado.
    SELETOR_PAINEL_LOGADO = '#pane-side'
    # Seletor do canvas do QR code (aparece quando não há sessão salva)
    SELETOR_QR_CODE = 'canvas[aria-label="Scan me!"]'

    try:
        # Etapa 1: Em até 30s, detecta se há sessão salva ou se precisa de QR
        print_log("Verificando estado da sessão...")
        ja_logado = False
        try:
            page.wait_for_selector(SELETOR_PAINEL_LOGADO, timeout=30000)
            ja_logado = True
        except Exception:
            pass  # Não logou em 30s, pode ser que o QR apareceu

        if ja_logado:
            print_log("Sessão encontrada! Login automático realizado com sucesso.")
            page.wait_for_timeout(3000)  # Pausa para carregar contatos
            fechar_banner_novidades(page)
            return True

        # Etapa 2: Verifica se o QR code apareceu para ser escaneado
        print_log("Nenhuma sessão salva detectada. Aguardando leitura do QR Code...")
        try:
            page.wait_for_selector(SELETOR_QR_CODE, timeout=15000)
            print_log("QR Code visível! Por favor, escaneie com o seu celular.")
        except Exception:
            print_log("QR Code não detectado. Aguardando o painel carregar de qualquer forma...")

        # Etapa 3: Aguarda até 10 minutos pelo painel principal (após scan do QR)
        try:
            page.wait_for_selector(SELETOR_PAINEL_LOGADO, timeout=600000)
            print_log("Login no painel do WhatsApp Web concluído e carregado com sucesso!")
            page.wait_for_timeout(5000)  # Pausa para digerir carregamento dos contatos
            fechar_banner_novidades(page)
            return True
        except Exception:
            print_log("Demora excessiva ao aguardar o painel. Script abortado.")
            return False

    except Exception as e:
        print_log(f"Erro inesperado durante o login: {e}. Script abortado.")
        return False

def localizar_e_acessar_conversa(page, nome_grupo):
    """
    Usa a barra de pesquisa contida no painel esquerdo para buscar o grupo especificado
    e entra no chat para visualizar as mensagens dele.
    
    Args:
        page (Page): Instância da página do Playwright.
        nome_grupo (str): O nome do grupo ou contato a ser buscado.
        
    Returns:
        bool: True se o grupo foi encontrado e aberto, False caso contrário.
    """
    print_log(f"Procurando contato/grupo: '{nome_grupo}'...")
    try:
        campo_busca = page.locator('input[aria-label="Search or start a new chat"]').first
        if not campo_busca.is_visible():
            # Tentar outro seletor genérico para a busca (em inglês)
            campo_busca = page.locator('div[title="Search input textbox"]').first
            
        campo_busca.click()
        campo_busca.fill(nome_grupo)
        
        page.wait_for_timeout(2500) # Aguarda até travar a pesquisa
        
        chat_alvo = page.locator(f'span[title="{nome_grupo}"]').first
        chat_alvo.wait_for(state="visible", timeout=10000)
        chat_alvo.click()
        
        print_log(f"Abrindo a conversa de '{nome_grupo}'.")
        page.wait_for_timeout(3000)
        return True
        
    except Exception as e:
        print_log(f"[ERRO] Chat '{nome_grupo}' não localizado. Verifique se o nome confere. Detalhes: {e}")
        return False
