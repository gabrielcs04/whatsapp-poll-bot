import os
import json
from datetime import date, timedelta

def gerar_json(mes, ano, nome_grupo="Acólitos S. João Batista"):
    """
    Gera automaticamente as configurações de enquetes (títulos e opções de datas)
    com base no mês e ano informados, criando o arquivo 'config.json' na pasta 'dados/'.
    Calcula os finais de semana automaticamente partindo do primeiro sábado do mês.
    
    Args:
        mes (int): O mês desejado (1 a 12).
        ano (int): O ano desejado (ex: 2026).
        nome_grupo (str, optional): O nome do grupo do WhatsApp onde serão enviadas. 
                                    Padrão é "Acólitos S. João Batista".
                                    
    Returns:
        None
    """
    meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    nome_mes = meses_pt[mes]
    
    # Encontra o primeiro Sábado do mês especificado
    d = date(ano, mes, 1)
    while d.weekday() != 5:  # 5 representa Sábado em Python (0=Seg, 6=Dom)
        d += timedelta(days=1)
        
    enquetes = []
    semana_num = 1
    
    # Continua gerando enquanto os sábados caírem dentro do mês especificado
    while d.month == mes:
        sabado = d
        domingo = sabado + timedelta(days=1)
        terca = sabado + timedelta(days=3)
        
        titulo = f"Semana {semana_num:02d} - {nome_mes}"
        
        opcoes = [
            f"Sábado ({sabado.strftime('%d/%m')}) - 18:00",
            f"Domingo ({domingo.strftime('%d/%m')}) - 07:30",
            f"Domingo ({domingo.strftime('%d/%m')}) - 09:30",
            f"Domingo ({domingo.strftime('%d/%m')}) - 18:00",
            f"Terça ({terca.strftime('%d/%m')}) - 19:30"
        ]
        
        enquetes.append({
            "titulo": titulo,
            "opcoes": opcoes
        })
        
        # Pula para o sábado da próxima semana
        d += timedelta(days=7)
        semana_num += 1
        
    # Monta o formato JSON final
    config = {
        "nome_grupo": nome_grupo,
        "mes": mes,
        "ano": ano,
        "enquetes": enquetes
    }
    
    # Salva no arquivo dados/config.json
    os.makedirs("dados", exist_ok=True)
    with open("dados/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        
    print(f"[SUCESSO] Arquivo dados/config.json atualizado para as enquetes de {nome_mes} de {ano}!")
    print(f"Foram geradas {semana_num-1} semanas de enquetes.")
