# 🤖 WhatsApp Poll Bot (Automação de Enquetes)

Um robô construído em Python e [Playwright](https://playwright.dev/python/) projetado para automatizar totalmente o trabalho manual de criar múltiplas enquetes semanais/mensais em um grupo do WhatsApp Web e também extrair os resultados (votos) dessas enquetes de forma estruturada.

## 📌 Visão Geral e Estrutura

O projeto é organizado de forma limpa e de modo a separar o código-fonte dos dados do usuário:

```text
WhatsappBotEnquete/
├── dados/
│   ├── config.json                     # Configuração estática base (dias da semana e horários)
│   ├── enquetes.json                   # Enquetes geradas para um mês/ano específico
│   ├── resultados_ANO_MES.csv          # Relatório final dos votos extraídos (ex: resultados_2026_06.csv)
│   └── sessao_whatsapp/                 # Credenciais de sessão do WhatsApp (evita novo QR Code)
├── src/
│   ├── main.py                          # Painel interativo / Orquestrador principal
│   ├── gerador_enquetes.py              # Script para calcular datas e gerar o enquetes.json
│   └── whatsapp/
│       ├── enviador_enquetes.py         # Robô que cria as enquetes geradas usando o Playwright
│       ├── extrator_votos.py            # Robô que extrai votos das enquetes
│       └── utils.py                     # Funções utilitárias e de conexão com o WhatsApp
├── venv/                                # Ambiente virtual Python
├── requirements.txt                     # Lista de dependências do projeto
├── run.py                               # Script de inicialização rápida
└── README.md                            # Esta documentação
```

### Componentes de Código:
1. **O Painel Interativo ([src/main.py](./src/main.py))**: Gerencia a interface no terminal e chama as automações através de um menu em loop.
2. **O Gerador Automático ([src/gerador_enquetes.py](./src/gerador_enquetes.py))**: Lê a configuração do `dados/config.json`, calcula as datas reais para um mês/ano informado e escreve as enquetes prontas em `dados/enquetes.json`.
3. **O Enviador de Enquetes ([src/whatsapp/enviador_enquetes.py](./src/whatsapp/enviador_enquetes.py))**: Lê o `dados/enquetes.json` e envia as enquetes no grupo do WhatsApp Web.
4. **O Extrator de Votos ([src/whatsapp/extrator_votos.py](./src/whatsapp/extrator_votos.py))**: Acessa a conversa, raspa os votos e gera um relatório em formato CSV (`dados/resultados_ANO_MES.csv`), organizando cada horário planejado como uma coluna e listando as pessoas respondentes logo abaixo.

---

## 🚀 Requisitos

- Python `3.9` ou superior instalado no seu sistema.

## ⚙️ Como Instalar e Rodar (Modo Simplificado)

Configuramos o projeto para fazer toda a preparação do ambiente virtual, instalação de dependências e configuração do navegador Playwright de forma automática e rápida.

Basta abrir o seu terminal na pasta raiz do projeto e rodar o comando:

```bash
# No Windows
python run.py

# No Mac / Linux
python3 run.py
```

O script é inteligente e utiliza cache local: ele só instalará as dependências caso detecte modificações no arquivo `requirements.txt` ou se a pasta `venv` for excluída, tornando a inicialização do dia a dia quase instantânea.

Assim que o painel abrir, um menu contínuo será exibido:

- **Opção 1 (Gerar novas enquetes):** Utiliza o `config.json` para criar os textos das enquetes de um determinado mês e os salva em `enquetes.json`. Esta opção não realiza envio no WhatsApp, apenas prepara os dados.
- **Opção 2 (Enviar as enquetes existentes):** Lê o arquivo `enquetes.json` e inicia o Playwright para criar fisicamente as enquetes no WhatsApp.
- **Opção 3 (Ler resultados de enquetes existentes):** Lê as enquetes do WhatsApp e gera o relatório CSV (`dados/resultados_ANO_MES.csv`).
- **Opção 4 (Sair):** Encerra a aplicação normalmente.

### 📱 Lendo o QR Code (Primeiro Login)

Na **primeira vez** que o robô iniciar o navegador (opção 2 ou 3), ele carregará o WhatsApp Web exibindo o **QR Code**:
- Escaneie o código usando seu celular.
- O robô aguardará até 5 minutos pela leitura da autenticação.
- Nas execuções futuras, a sessão persistente será guardada na pasta `dados/sessao_whatsapp` e o robô conectará **sem pedir QR Code** novamente.

---

## 📅 Configuração e Geração de Enquetes

O comportamento do bot baseia-se em dois arquivos fundamentais:

1. **`dados/config.json`**: Contém a regra de negócio do bot (quais dias da semana e horários terão missas/enquetes). Este arquivo não possui datas reais, apenas padrões.
    ```json
    {
      "dias": {
        "sabado": { "horarios": ["18:30"] },
        "domingo": { "horarios": ["07:00", "09:00", "19:00"] },
        "terca": { "horarios": ["19:30"] }
      }
    }
    ```
2. **`dados/enquetes.json`**: Ao executar a **Opção 1** no menu, o sistema pede o mês e o ano e usa o `config.json` para gerar este arquivo. É ele quem armazena os dados finais já com os dias exatos calculados, e que será efetivamente lido pela **Opção 2** para o envio.

> [!IMPORTANT]
> Se o envio falhar ou você quiser alterar um texto específico antes de postar, basta rodar a Opção 1, editar manualmente o `enquetes.json` no editor de textos e, só então, rodar a Opção 2.

## ⚠️ Configurações Manuais Extras

Se você precisar alterar o nome padrão do grupo do WhatsApp que o bot busca ao apertar "Enter" direto no painel, edite o valor padrão do parâmetro `nome_grupo` na assinatura da função `gerar_json` dentro de [gerador_enquetes.py](./src/gerador_enquetes.py):
`def gerar_json(mes, ano, nome_grupo="Acólitos S. João Batista"):`

> [!IMPORTANT]
> Letras maiúsculas, minúsculas, pontuações e acentos no nome do grupo **devem coincidir exatamente** com o nome do grupo no seu WhatsApp.
