import os
import time
import json

SESSAO_DIR = "dados/sessao_whatsapp"

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
        with open('dados/config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            nome_grupo = config_data.get("nome_grupo", "")
            enquetes_json = config_data.get("enquetes", [])
            return nome_grupo, enquetes_json
    except FileNotFoundError:
        print_log("[ERRO] Arquivo dados/config.json não encontrado!")
        return "", []

def iniciar_navegador(playwright_context):
    """
    Inicia o navegador Chromium usando contexto persistente para retenção do login.
    
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
        headless=False, # Precisamos ver o navegador
        args=["--no-sandbox", "--disable-setuid-sandbox", "--start-maximized"],
        no_viewport=True
    )
    
    page = browser_context.pages[0]
    page.set_default_timeout(60000)
    
    return browser_context, page

def abrir_whatsapp_e_aguardar_login(page):
    """
    Acessa a página principal do WhatsApp Web e aguarda o carregamento global da lista de chats,
    comprovando que o usuário está corretamente autenticado.
    
    Args:
        page (Page): Instância da página do Playwright.
        
    Returns:
        bool: True se o login foi concluído e carregado, False caso contrário.
    """
    print_log("Acessando o WhatsApp Web.")
    page.goto('https://web.whatsapp.com/', wait_until='domcontentloaded')
    
    print_log("Favor realizar a leitura do QR Code pelo seu celular (caso já esteja logado, só aguardar!)...")
    
    try:
        # A barra de buscar os contatos no painel esquerdo indica que o aplicativo abriu integralmente.
        page.wait_for_selector('div[dir="ltr"]', timeout=300000) # Até 5 min parado aqui.
        print_log("Login no painel do Web concluído e carregado com sucesso!")
        page.wait_for_timeout(5000) # Pausa pra digerir carregamento dos contatos
        return True
    except Exception:
        print_log("Demora excessiva em aguardar o painel ou encerramento manual da página. Script abortado.")
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
