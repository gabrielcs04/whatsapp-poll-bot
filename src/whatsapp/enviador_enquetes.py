# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright
from utils import print_log, iniciar_navegador, abrir_whatsapp_e_aguardar_login, localizar_e_acessar_conversa, carregar_enquetes

def criar_uma_enquete(page, titulo, opcoes):
    """
    Executa a criação de uma única enquete dentro da aba da conversa atualmente focalizada.
    Realiza interações visuais (clique, texto) dentro de campos de entrada na tela.
    
    Args:
        page (Page): Instância da página do Playwright.
        titulo (str): O título/pergunta da enquete.
        opcoes (list): Lista de strings com as opções da enquete.
        
    Returns:
        bool: True se a enquete foi enviada com sucesso, False em caso de falha.
    """
    print_log(f"Criando enquete: '{titulo}'...")
    
    # 1. Abre o menu vertical de anexos
    try:
        botao_anexo = page.locator('span[data-icon="ic-attach-file"]').first
        if not botao_anexo.is_visible():
            botao_anexo = page.locator('span[data-icon="attach-menu-plus"]').first
        botao_anexo.click()
    except Exception as e:
        print_log(f"Erro momentâneo ao abrir menu de anexos: {e}")
        return False

    page.wait_for_timeout(1000)
    
    # 2. Seleciona "Enquete"
    try:
        page.locator('button[aria-label="Poll"]').first.click()
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
    page.locator('div[aria-label="Send"]').first.click()
    print_log(f"Enquete '{titulo}' enviada com sucesso!")
    
    # Delay entre enquetes para agir de forma orgânica
    page.wait_for_timeout(4000)
    return True


def main():
    """
    Ponto de orquestração do programa criador de enquetes.
    Controla o fluxo cronológico entre a inicialização, login, navegação e envios.
    """
    print_log("Iniciando Automação do WhatsApp Web via Playwright...")
    
    nome_grupo, enquetes = carregar_enquetes()
    if not nome_grupo or not enquetes:
        print_log("[ERRO] Enquetes inválidas ou vazias. Abortando criação.")
        return
        
    with sync_playwright() as p:
        # Passo 1: Boot de contexto e navegação primária
        browser_context, page = iniciar_navegador(p)
        
        # Passo 2: Validar estado global de Autenticação/Conexão
        login_ok = abrir_whatsapp_e_aguardar_login(page)
        if not login_ok:
            browser_context.close()
            return
            
        # Passo 3: Navegar para a conversa em foco
        grupo_aberto = localizar_e_acessar_conversa(page, nome_grupo)
        if not grupo_aberto:
            browser_context.close()
            return
            
        # Passo 4: Executar loop de inserção de múltiplas tarefas (Enquetes)
        for enquete in enquetes:
            criar_uma_enquete(page, enquete['titulo'], enquete['opcoes'])

        # Passo Fim
        print_log("Todas as enquetes foram geradas e enviadas no chat desejado!")
        print_log("Finalizando e fechando instâncias em 5 segundos...")
        page.wait_for_timeout(5000)
        browser_context.close()

if __name__ == "__main__":
    main()
