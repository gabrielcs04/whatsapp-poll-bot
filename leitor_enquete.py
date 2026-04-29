import time
import re
from playwright.sync_api import sync_playwright
from whatsapp_utils import print_log, iniciar_navegador, abrir_whatsapp_e_aguardar_login, localizar_e_acessar_conversa, carregar_configuracoes

def encontrar_enquete_e_abrir_votos(page, titulo):
    """
    Localiza a enquete no histórico da conversa e abre o modal de visualização de votos.
    
    Args:
        page (Page): Instância da página do Playwright.
        titulo (str): O título da enquete a ser localizada.
        
    Returns:
        bool: True se encontrou e abriu os votos com sucesso, False caso contrário.
    """
    print_log(f"Procurando a enquete: '{titulo}'...")
    encontrou = False
    
    # Garante que o mouse está sobre a área central das mensagens para o scroll funcionar
    try:
        page.mouse.move(800, 400)
    except:
        pass
        
    # Rola para cima tentando achar a enquete (histórico recente)
    for _ in range(40): # Aumentado o número de tentativas
        # Localiza pelo texto exato ou parcial do título
        elemento_titulo = page.locator(f'text="{titulo}"').last
        if elemento_titulo.is_visible():
            elemento_titulo.scroll_into_view_if_needed()
            encontrou = True
            break
            
        # Usa tecla PageUp e a roda do mouse para forçar a rolagem
        page.keyboard.press("PageUp")
        page.mouse.wheel(0, -4000)
        page.wait_for_timeout(800)
        
    if not encontrou:
        print_log(f"[AVISO] Enquete '{titulo}' não encontrada na tela atual.")
        return False
        
    page.wait_for_timeout(1000)
    
    # Procura a linha (row) da mensagem que contém o título
    try:
        linha_mensagem = page.locator(f'div[role="row"]:has-text("{titulo}")').last
        # Procura o botão de Ver Votos (suporte a Inglês e Português)
        botao_votos = linha_mensagem.locator('text=/View votes|Ver votos/i').first
        
        if botao_votos.is_visible():
            botao_votos.click()
            print_log(f"Botão de votos da enquete '{titulo}' clicado.")
            page.wait_for_timeout(2000)
            return True
        else:
            print_log(f"[AVISO] Botão 'View votes' não encontrado na enquete '{titulo}'.")
            return False
    except Exception as e:
        print_log(f"[ERRO] Falha ao tentar abrir votos da enquete '{titulo}': {e}")
        return False

def parse_linhas_modal(linhas, opcoes_esperadas):
    """
    Recebe as linhas de texto bruto extraídas do modal e as limpa usando Regex,
    retornando um dicionário estruturado com os votantes de cada opção.
    
    Args:
        linhas (list): Lista de strings com o texto puro do modal.
        opcoes_esperadas (list): Lista de opções conhecidas da enquete.
        
    Returns:
        dict: Dicionário no formato {opcao: [votante1, votante2, ...]}
    """
    resultados = {opcao: [] for opcao in opcoes_esperadas}
    opcao_atual = None
    
    for linha in linhas:
        linha = linha.strip()
        if not linha: continue
        
        if linha.lower() in ["poll details", "detalhes da enquete", "view votes", "ver votos", "close", "fechar", "back", "voltar"]:
            continue
            
        if linha in opcoes_esperadas:
            opcao_atual = linha
            continue
            
        if re.search(r'see all|ver tod', linha.lower()):
            continue
            
        if re.search(r'\b(votes|votos)\b', linha.lower()):
            continue
            
        if re.search(r'\d{2}:\d{2}', linha):
            continue
            
        if re.search(r'^\+\d{2,3}', linha):
            continue
            
        if linha.isdigit():
            continue
            
        if opcao_atual and len(linha) > 1:
            if linha not in resultados[opcao_atual]:
                resultados[opcao_atual].append(linha)
                
    return resultados

def extrair_dados_do_modal(page, opcoes_esperadas):
    """
    Responsável por extrair todos os dados de votantes de dentro do modal aberto,
    navegando pelas sub-telas de opções (clicando em "See all") quando necessário.
    
    Args:
        page (Page): Instância da página do Playwright.
        opcoes_esperadas (list): Lista de opções contendo os textos base da enquete.
        
    Returns:
        dict: Dicionário compilado e finalizado com todos os votantes limpos.
    """
    print_log("Extraindo dados do modal de votos...")
    try:
        modal = page.locator('div[data-testid="poll-details-drawer"]').first
        if not modal.is_visible():
            modal = page.locator('div[role="dialog"]').first
        modal.wait_for(state="visible", timeout=10000)
        
        # 1. Extrai da tela principal primeiro (garante pegar opções que não têm "See all")
        texto_puro = modal.inner_text()
        resultados = parse_linhas_modal(texto_puro.split('\n'), opcoes_esperadas)
        
        # 2. Verifica se existem botões "See all"
        qtd_botoes = modal.locator('text=/See all|Ver tod/i').count()
        
        # 3. Itera sobre cada botão "See all" navegando para a sub-tela e voltando
        for i in range(qtd_botoes):
            botoes = modal.locator('text=/See all|Ver tod/i')
            if i < botoes.count():
                try:
                    botoes.nth(i).click(timeout=2000)
                    page.wait_for_timeout(1500) # Aguarda animação de slide da sub-tela
                    
                    texto_sub = modal.inner_text()
                    resultados_sub = parse_linhas_modal(texto_sub.split('\n'), opcoes_esperadas)
                    
                    # Atualiza o dicionário principal com os dados completos da sub-tela
                    for opc, votantes in resultados_sub.items():
                        if votantes:
                            # Junta as listas evitando duplicatas
                            for v in votantes:
                                if v not in resultados[opc]:
                                    resultados[opc].append(v)
                                    
                    # Voltar para a tela principal do modal
                    botao_voltar = modal.locator('span[data-icon="back"], span[data-icon="arrow-left"]').first
                    if not botao_voltar.is_visible():
                        botao_voltar = modal.locator('button[aria-label="Back"], button[aria-label="Voltar"]').first
                        
                    if not botao_voltar.is_visible():
                        # O primeiro botão do drawer costuma ser o de voltar
                        botao_voltar = modal.locator('button').first
                        
                    botao_voltar.click()
                    page.wait_for_timeout(1500) # Aguarda animação de volta
                    
                except Exception as e:
                    print_log(f"[AVISO] Erro ao navegar na sub-tela da opção: {e}")
                    # Se der erro, tenta garantir que apertamos voltar para não quebrar a próxima
                    try:
                        modal.locator('button').first.click(timeout=1000)
                    except:
                        pass
                    page.wait_for_timeout(1000)
                    
        # Fecha o modal
        botao_fechar = modal.locator('span[data-icon="x"]').first
        if not botao_fechar.is_visible():
            botao_fechar = modal.locator('button[aria-label="Close"], button[aria-label="Fechar"]').first
            
        if botao_fechar.is_visible():
            botao_fechar.click()
        else:
            page.keyboard.press("Escape")
            
        page.wait_for_timeout(1000)
        return resultados
    except Exception as e:
        print_log(f"[ERRO] Erro ao extrair dados do modal: {e}")
        page.keyboard.press("Escape")
        return {}

def salvar_relatorio(todos_resultados):
    """
    Formata e salva o relatório final de votos em um arquivo .md (Markdown).
    
    Args:
        todos_resultados (dict): Dicionário contendo os dados extraídos de todas as enquetes.
    """
    print_log("Salvando relatório em resultados_enquetes.md...")
    try:
        with open("resultados_enquetes.md", "w", encoding="utf-8") as f:
            f.write("# 📊 Relatório de Enquetes\n\n")
            f.write(f"**Gerado em:** `{time.strftime('%d/%m/%Y %H:%M:%S')}`\n\n")
            
            for titulo, opcoes_votos in todos_resultados.items():
                f.write(f"## 📝 {titulo}\n\n")
                if not opcoes_votos:
                    f.write("> *Nenhum dado extraído ou enquete sem votos.*\n\n")
                else:
                    for opcao, votantes in opcoes_votos.items():
                        f.write(f"### 📌 {opcao}\n\n")
                        if not votantes:
                            f.write("- *Nenhum voto*\n\n")
                        else:
                            for votante in votantes:
                                f.write(f"- {votante}\n")
                        f.write("\n")
        print_log("Relatório salvo com sucesso!")
    except Exception as e:
        print_log(f"[ERRO] Falha ao salvar relatório: {e}")

def main():
    """
    Ponto de orquestração do leitor de enquetes. Controla todo o fluxo:
    Leitura do JSON -> Login -> Scroll na conversa -> Extração -> Salvamento.
    """
    print_log("Iniciando Leitor de Enquetes...")
    nome_grupo, enquetes_json = carregar_configuracoes()
    
    if not nome_grupo or not enquetes_json:
        print_log("Configurações inválidas ou vazias. Abortando.")
        return

    todos_resultados = {}

    with sync_playwright() as p:
        browser_context, page = iniciar_navegador(p)
        
        if not abrir_whatsapp_e_aguardar_login(page):
            browser_context.close()
            return
            
        if not localizar_e_acessar_conversa(page, nome_grupo):
            browser_context.close()
            return
            
        # Percorre as enquetes buscando os dados
        for enquete in enquetes_json:
            titulo = enquete["titulo"]
            opcoes_esperadas = enquete["opcoes"]
            
            sucesso = encontrar_enquete_e_abrir_votos(page, titulo)
            if sucesso:
                dados = extrair_dados_do_modal(page, opcoes_esperadas)
                todos_resultados[titulo] = dados
            else:
                todos_resultados[titulo] = {}
                
        # Salva o resultado final no arquivo .txt
        salvar_relatorio(todos_resultados)
        
        print_log("Leitura finalizada! Fechando em 3 segundos...")
        page.wait_for_timeout(3000)
        browser_context.close()

if __name__ == "__main__":
    main()
