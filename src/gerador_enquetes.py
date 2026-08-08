import os
import json
from datetime import date, timedelta

# Mapeamento de nomes de dias em português para o weekday do Python
# (0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo)
_DIAS_PT_PARA_WEEKDAY = {
    "segunda": 0,
    "terca":   1,
    "quarta":  2,
    "quinta":  3,
    "sexta":   4,
    "sabado":  5,
    "domingo": 6,
}

# Rótulos de exibição para cada dia da semana (usados nas opções da enquete)
_ROTULOS_DIAS = {
    "segunda": "Segunda",
    "terca":   "Terça",
    "quarta":  "Quarta",
    "quinta":  "Quinta",
    "sexta":   "Sexta",
    "sabado":  "Sábado",
    "domingo": "Domingo",
}

def _carregar_config_dias(config_path="dados/config.json"):
    """
    Lê o arquivo config.json e retorna o dicionário de dias configurados.

    Args:
        config_path (str): Caminho para o arquivo de configuração.

    Returns:
        dict: Mapeamento {nome_dia: {"horarios": [...]}} conforme o config.json.

    Raises:
        FileNotFoundError: Se o arquivo de configuração não existir.
        KeyError: Se a chave "dias" não estiver presente no arquivo.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["dias"]


def gerar_json(mes, ano, nome_grupo="Acólitos S. João Batista"):
    """
    Gera automaticamente as configurações de enquetes (títulos e opções de datas)
    com base no mês e ano informados, criando o arquivo 'enquetes.json' na pasta 'dados/'.

    Os dias da semana e horários são lidos dinamicamente do arquivo 'dados/config.json',
    portanto nenhuma regra de dia/horário está hardcoded nesta função.

    A lógica de agrupamento por semana é mantida: parte do primeiro sábado do mês
    e agrupa todos os dias configurados que pertencem à mesma semana
    (de sábado até a sexta-feira seguinte).

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

    # Lê os dias e horários configurados no config.json
    dias_config = _carregar_config_dias()

    # Constrói lista ordenada de (weekday, nome_dia, horarios) para uso no loop
    # Ordenada pelo offset a partir do Sábado (Sáb=0, Dom=1, Seg=2, Ter=3...)
    # para garantir ordem cronológica dentro de cada semana
    dias_ordenados = sorted(
        [
            (_DIAS_PT_PARA_WEEKDAY[nome], nome, info["horarios"])
            for nome, info in dias_config.items()
            if nome in _DIAS_PT_PARA_WEEKDAY
        ],
        key=lambda x: (x[0] - 5) % 7  # offset a partir do Sábado
    )

    # Encontra o primeiro Sábado do mês especificado
    d = date(ano, mes, 1)
    while d.weekday() != 5:  # 5 = Sábado
        d += timedelta(days=1)

    enquetes = []
    semana_num = 1

    # Continua gerando enquanto os sábados caírem dentro do mês especificado
    while d.month == mes:
        sabado = d
        titulo = f"Semana {semana_num:02d} - {nome_mes}"
        opcoes = []

        for weekday, nome_dia, horarios in dias_ordenados:
            # Calcula o offset em dias a partir do sábado desta semana
            # Sábado=5: offset 0; Domingo=6: offset 1; Segunda=0: offset 2; Terça=1: offset 3 ...
            offset = (weekday - 5) % 7
            data_dia = sabado + timedelta(days=offset)

            rotulo = _ROTULOS_DIAS.get(nome_dia, nome_dia.capitalize())

            for horario in horarios:
                opcoes.append(f"{rotulo} ({data_dia.strftime('%d/%m')}) - {horario}")

        enquetes.append({
            "titulo": titulo,
            "opcoes": opcoes
        })

        # Pula para o sábado da próxima semana
        d += timedelta(days=7)
        semana_num += 1

    # Monta o formato JSON final
    enquetes_data = {
        "nome_grupo": nome_grupo,
        "mes": mes,
        "ano": ano,
        "enquetes": enquetes
    }

    # Salva no arquivo dados/enquetes.json
    os.makedirs("dados", exist_ok=True)
    with open("dados/enquetes.json", "w", encoding="utf-8") as f:
        json.dump(enquetes_data, f, ensure_ascii=False, indent=2)

    print(f"[SUCESSO] Arquivo dados/enquetes.json atualizado para as enquetes de {nome_mes} de {ano}!")
    print(f"Foram geradas {semana_num-1} semanas de enquetes.")
