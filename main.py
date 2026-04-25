import os
import time
from playwright.sync_api import sync_playwright

# =========================================================================
# CONFIGURAÇÕES
# =========================================================================

# Certifique-se de configurar perfeitamente o nome do Grupo ou Contato 
NOME_GRUPO = "ARQUIVOS IMPORTANTES"

# Lista de enquetes que o script preencherá e criará automaticamente
ENQUETES_JSON = [
    {
        "titulo": "Qual dia é melhor para a reunião de alinhamento?",
        "opcoes": ["Segunda", "Quarta", "Sexta", "Nenhum"]
    },
    {
        "titulo": "Qual horário funcionaria melhor?",
        "opcoes": ["18:00", "19:00", "20:00"]
    }
]

# Diretório base para persistir o login e não pedir QRCode repetidas vezes
SESSAO_DIR = "./sessao_whatsapp"

# =========================================================================

def print_log(mensagem):
    """
    Função auxiliar para imprimir logs com horário.
    """
    horario = time.strftime('%H:%M:%S')
    print(f"[{horario}] {mensagem}")


def iniciar_navegador(playwright_context):
    """
    Inicia o navegador Chromium usando contexto persistente para retenção do login.
    Retorna o browser_context gerado e a page correspondente.
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
    comprovando que o usuário está corretamente autenticado (seja no primeiro login ou cache local).
    Retorna True em caso de sucesso.
    """
    print_log("Acessando o WhatsApp Web.")
    page.goto('https://web.whatsapp.com/', wait_until='domcontentloaded')
    
    print_log("Favor realizar a leitura do QR Code pelo seu celular (caso já esteja logado, só aguardar!)...")
    
    try:
        # A barra de buscar os contatos no painel esquerdo indica que o aplicativo abriu integralmente.
        page.wait_for_selector('div[contenteditable="true"]', timeout=300000) # Até 5 min parado aqui.
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
    """
    print_log(f"Procurando contato/grupo: '{nome_grupo}'...")
    try:
        campo_busca = page.locator('div[contenteditable="true"]').first
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


def criar_uma_enquete(page, titulo, opcoes):
    """
    Executa a criação de uma única enquete dentro da aba da conversa atualmente focalizada.
    Realiza interações visuais (clique, texto) dentro de campos textboxes na tela.
    """
    print_log(f"Criando enquete: '{titulo}'...")
    
    # 1. Abre o menu vertical de anexos
    try:
        botao_anexo = page.locator('span[data-icon="plus"]').first
        if not botao_anexo.is_visible():
            botao_anexo = page.locator('span[data-icon="attach-menu-plus"]').first
        botao_anexo.click()
    except Exception as e:
        print_log(f"Erro momentâneo ao abrir menu de anexos: {e}")
        return False

    page.wait_for_timeout(1000)
    
    # 2. Seleciona "Enquete"
    try:
        page.locator('span[data-icon="poll"]').first.click()
    except Exception as e:
        print_log(f"Erro ao clicar na funcionalidade enquete: {e}")
        return False

    page.wait_for_timeout(1500)
    
    # 3. Preenche a janela da Enquete
    textboxes = page.get_by_role("textbox")
    
    # O item 0 é a Pergunta principal
    textboxes.nth(0).fill(titulo)
    page.wait_for_timeout(500)
    
    # O item 1, 2, ... são as opções sequenciais para marcação
    for i, opcao in enumerate(opcoes):
        textboxes.nth(i + 1).fill(opcao)
        page.wait_for_timeout(400)
        
    # 4. Finaliza e Envia
    page.locator('span[data-icon="send"]').first.click()
    print_log(f"Enquete '{titulo}' enviada com firmeza!")
    
    # Delay entre enquetes para agir de forma orgânica
    page.wait_for_timeout(4000)
    return True


def main():
    """
    Ponto de orquestração do programa.
    Controla o fluxo cronológico entre os diferentes métodos.
    """
    print_log("Iniciando Automação do WhatsApp Web via Playwright...")
    
    with sync_playwright() as p:
        # Passo 1: Boot de contexto e navegação primária
        browser_context, page = iniciar_navegador(p)
        
        # Passo 2: Validar estado global de Autenticação/Conexão
        login_ok = abrir_whatsapp_e_aguardar_login(page)
        if not login_ok:
            browser_context.close()
            return
            
        # Passo 3: Navegar para a conversa em foco na variável global
        grupo_aberto = localizar_e_acessar_conversa(page, NOME_GRUPO)
        if not grupo_aberto:
            browser_context.close()
            return
            
        # Passo 4: Executar loop de inserção de múltiplas tarefas (Enquetes)
        for enquete in ENQUETES_JSON:
            criar_uma_enquete(page, enquete['titulo'], enquete['opcoes'])

        # Passo Fim
        print_log("Todas as enquetes foram geradas e enviadas no chat desejado!")
        print_log("Finalizando e fechando instâncias em 5 segundos...")
        page.wait_for_timeout(5000)
        browser_context.close()


if __name__ == "__main__":
    main()
