import json
from datetime import date, timedelta
import sys

# =====================================================================
# GERADOR AUTOMÁTICO DE ENQUETES (CONFIG.JSON)
# =====================================================================

def gerar_json(mes, ano, nome_grupo="ARQUIVOS IMPORTANTES"):
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
        "enquetes": enquetes
    }
    
    # Salva no arquivo config.json
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        
    print(f"[SUCESSO] Arquivo config.json atualizado para as enquetes de {nome_mes} de {ano}!")
    print(f"Foram geradas {semana_num-1} semanas de enquetes.")

if __name__ == "__main__":
    # Você pode alterar o mês e o ano aqui antes de rodar o script
    MES = 5
    ANO = 2026
    
    gerar_json(MES, ANO)
