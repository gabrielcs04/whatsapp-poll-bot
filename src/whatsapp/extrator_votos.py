import re
import os
import csv
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright
from utils import print_log, iniciar_navegador, abrir_whatsapp_e_aguardar_login, localizar_e_acessar_conversa, carregar_enquetes

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

def extrair_dados_do_modal(page, opcoes_esperadas):
    """
    Extrai votos do modal de detalhes de enquete, iterando por cada container de opção
    (data-testid="poll-details-option-N") e lendo os nomes de votantes a partir do
    atributo `title` dos elementos span[dir="auto"] dentro de cell-frame-title.

    Lógica:
    - Cada opção da enquete tem seu próprio div container com data-testid="poll-details-option-N".
    - O nome da opção está em span[data-testid="selectable-text"] dentro do container.
    - Os votantes estão em div[data-testid="cell-frame-title"] span[dir="auto"] (atributo title).
    - O botão "See all" só aparece DENTRO do container de uma opção quando há mais votantes
      do que os exibidos. Opções com poucos votos simplesmente não têm esse botão — e isso
      é o comportamento esperado, não um erro.

    Args:
        page (Page): Instância da página do Playwright.
        opcoes_esperadas (list): Lista de opções contendo os textos base da enquete.

    Returns:
        dict: Dicionário no formato {opcao: [votante1, votante2, ...]}
    """
    print_log("Extraindo dados do modal de votos...")
    resultados = {opcao: [] for opcao in opcoes_esperadas}
    try:
        modal = page.locator('div[data-testid="poll-details-drawer"]').first
        if not modal.is_visible():
            modal = page.locator('div[role="dialog"]').first
        modal.wait_for(state="visible", timeout=10000)

        # Conta quantas opções existem no modal (poll-details-option-0, -1, -2, ...)
        qtd_opcoes = modal.locator('div[data-testid^="poll-details-option-"]').count()
        print_log(f"Encontradas {qtd_opcoes} opção(ões) no modal.")

        for i in range(qtd_opcoes):
            # Re-localiza o container a cada iteração para evitar referências stale ao DOM
            opcao_div = modal.locator('div[data-testid^="poll-details-option-"]').nth(i)

            # Lê o nome da opção a partir do elemento estrutural span[data-testid="selectable-text"]
            try:
                nome_opcao = opcao_div.locator('span[data-testid="selectable-text"]').first.inner_text().strip()
            except Exception as e:
                print_log(f"[AVISO] Não foi possível ler o nome da opção #{i}: {e}")
                continue

            if nome_opcao not in resultados:
                print_log(f"[AVISO] Opção '{nome_opcao}' não está entre as esperadas, ignorando.")
                continue

            print_log(f"Processando opção: '{nome_opcao}'")

            # Verifica se existe botão "See all" DENTRO deste container de opção específico.
            # Esse botão SÓ existe quando há mais votantes do que os exibidos na tela principal.
            # Para opções com poucos votos, o botão simplesmente não existe — isso é correto.
            botao_see_all = opcao_div.locator('button').filter(
                has_text=re.compile(r'See all|Ver tod', re.IGNORECASE)
            )

            if botao_see_all.count() > 0 and botao_see_all.first.is_visible():
                # --- Opção com muitos votos: abre sub-tela expandida ---
                try:
                    botao_see_all.first.click(timeout=3000)
                    page.wait_for_timeout(1500)  # Aguarda animação de abertura da sub-tela

                    # Na sub-tela expandida, todos os votantes aparecem em cell-frame-title
                    nomes_els = modal.locator('div[data-testid="cell-frame-title"] span[dir="auto"]')
                    for j in range(nomes_els.count()):
                        try:
                            nome = nomes_els.nth(j).get_attribute("title") or nomes_els.nth(j).inner_text()
                            nome = nome.strip()
                            if nome and nome not in resultados[nome_opcao]:
                                resultados[nome_opcao].append(nome)
                        except Exception:
                            pass

                    # Volta para a tela principal do modal
                    botao_voltar = modal.locator('span[data-icon="back"], span[data-icon="arrow-left"]').first
                    if not botao_voltar.is_visible():
                        botao_voltar = modal.locator('button[aria-label="Back"], button[aria-label="Voltar"]').first
                    if not botao_voltar.is_visible():
                        botao_voltar = modal.locator('button').first
                    botao_voltar.click()
                    page.wait_for_timeout(1500)  # Aguarda animação de retorno

                except Exception as e:
                    print_log(f"[AVISO] Erro ao expandir 'See all' para '{nome_opcao}': {e}")
                    try:
                        modal.locator('button').first.click(timeout=1000)
                    except Exception:
                        pass
                    page.wait_for_timeout(1000)

            else:
                # --- Opção com poucos votos: lê diretamente do container da opção ---
                nomes_els = opcao_div.locator('div[data-testid="cell-frame-title"] span[dir="auto"]')
                for j in range(nomes_els.count()):
                    try:
                        nome = nomes_els.nth(j).get_attribute("title") or nomes_els.nth(j).inner_text()
                        nome = nome.strip()
                        if nome and nome not in resultados[nome_opcao]:
                            resultados[nome_opcao].append(nome)
                    except Exception:
                        pass

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

def salvar_relatorio(todos_resultados, enquetes_json, mes, ano):
    """
    Formata e salva o relatório final de votos em um arquivo CSV.
    Cada combinação de Enquete + Opção vira uma coluna, e os nomes dos votantes
    são listados logo abaixo.
    
    Args:
        todos_resultados (dict): Dicionário contendo os dados extraídos de todas as enquetes.
        enquetes_json (list): Lista de dicionários de enquetes geradas.
        mes (int): O mês correspondente.
        ano (int): O ano correspondente.
    """
    filename = f"dados/resultados/resultados_{ano}_{mes:02d}.csv"
    print_log(f"Salvando relatório em {filename}...")
    try:
        headers = []
        colunas_votos = {}
        
        for enquete in enquetes_json:
            titulo = enquete["titulo"]
            opcoes = enquete["opcoes"]
            dados_enquete = todos_resultados.get(titulo, {})
            
            for opcao in opcoes:
                col_name = opcao
                headers.append(col_name)
                votantes = dados_enquete.get(opcao, [])
                colunas_votos[col_name] = votantes

        # Determina o máximo de linhas de dados a serem geradas
        max_linhas = 0
        for col_name in headers:
            max_linhas = max(max_linhas, len(colunas_votos[col_name]))

        # Transpõe as colunas de votantes em linhas horizontais para escrita no CSV
        rows = []
        for i in range(max_linhas):
            linha = []
            for col_name in headers:
                votantes = colunas_votos[col_name]
                if i < len(votantes):
                    linha.append(votantes[i])
                else:
                    linha.append("")
            rows.append(linha)

        os.makedirs("dados", exist_ok=True)
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(headers)
            writer.writerows(rows)
                            
        print_log(f"Relatório CSV (por colunas) salvo com sucesso em {filename}!")
    except Exception as e:
        print_log(f"[ERRO] Falha ao salvar relatório CSV: {e}")

def main():
    """
    Ponto de orquestração do leitor de enquetes. Controla todo o fluxo:
    Leitura do JSON -> Login -> Scroll na conversa -> Extração -> Salvamento.
    """
    print_log("Iniciando Leitor de Enquetes...")
    nome_grupo, enquetes_json = carregar_enquetes()
    
    if not nome_grupo or not enquetes_json:
        print_log("Enquetes inválidas ou vazias. Abortando.")
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
                
        # Tenta carregar mês e ano para o nome do arquivo dinâmico
        import json
        mes, ano = None, None
        try:
            with open('dados/enquetes.json', 'r', encoding='utf-8') as f:
                enquetes_data = json.load(f)
                mes = enquetes_data.get("mes")
                ano = enquetes_data.get("ano")
        except Exception:
            pass
            
        if not mes or not ano:
            import datetime
            now = datetime.datetime.now()
            mes = mes or now.month
            ano = ano or now.year

        # Salva o resultado final no arquivo .csv
        salvar_relatorio(todos_resultados, enquetes_json, mes, ano)
        
        print_log("Leitura finalizada! Fechando em 3 segundos...")
        page.wait_for_timeout(3000)
        browser_context.close()

if __name__ == "__main__":
    main()
