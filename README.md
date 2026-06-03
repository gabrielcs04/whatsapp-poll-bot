# 🤖 WhatsApp Poll Bot (Automação de Enquetes)

Um robô construído em Python e [Playwright](https://playwright.dev/python/) projetado para automatizar totalmente o trabalho manual de criar múltiplas enquetes semanais/mensais em um grupo do WhatsApp Web e também extrair os resultados (votos) dessas enquetes de forma estruturada.

## 📌 Visão Geral e Estrutura

O projeto é organizado de forma limpa e de modo a separar o código-fonte dos dados do usuário:

```text
WhatsappBotEnquete/
├── dados/
│   ├── config.json                     # Cronograma das enquetes gerado automaticamente
│   ├── resultados_ANO_MES.csv          # Relatório final dos votos extraídos (ex: resultados_2026_06.csv)
│   └── sessao_whatsapp/                 # Credenciais de sessão do WhatsApp (evita novo QR Code)
├── src/
│   ├── main.py                          # Painel interativo / Orquestrador principal
│   ├── config/
│   │   └── gerador_config.py            # Script para calcular datas e gerar o config.json
│   └── automation/
│       ├── criador_enquete.py           # Robô que cria enquetes usando o Playwright
│       ├── leitor_enquete.py            # Robô que extrai votos das enquetes
│       └── whatsapp_utils.py            # Funções utilitárias e de conexão com o WhatsApp
├── venv/                                # Ambiente virtual Python
├── requirements.txt                     # Lista de dependências do projeto
├── run.py                               # Script de inicialização rápida
└── README.md                            # Esta documentação
```

### Componentes de Código:
1. **O Painel Interativo ([src/main.py](./src/main.py))**: Gerencia a interface no terminal e chama as automações.
2. **O Gerador Automático ([src/config/gerador_config.py](./src/config/gerador_config.py))**: Descobre os finais de semana (e terças-feiras) de um mês/ano e escreve em `dados/config.json`.
3. **O Robô Criador ([src/automation/criador_enquete.py](./src/automation/criador_enquete.py))**: Lê `dados/config.json` e envia as enquetes no grupo do WhatsApp Web.
4. **O Robô Leitor ([src/automation/leitor_enquete.py](./src/automation/leitor_enquete.py))**: Acessa a conversa, raspa os votos e gera um relatório em formato CSV (`dados/resultados_ANO_MES.csv`), organizando cada horário planejado como uma coluna e listando as pessoas respondentes logo abaixo.

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

Assim que o painel abrir:
- **Opção 1:** Gera configurações no arquivo `dados/config.json` e envia as enquetes.
- **Opção 2:** Lê as enquetes do WhatsApp e gera o relatório CSV (`dados/resultados_ANO_MES.csv`) onde as opções das enquetes são dispostas em colunas horizontais, contendo a lista de votantes correspondentes abaixo de cada uma.
- **Opção 3:** Encerra a aplicação.

### 📱 Lendo o QR Code (Primeiro Login)

Na **primeira vez** que o robô iniciar o navegador, ele carregará o WhatsApp Web exibindo o **QR Code**:
- Escaneie o código usando seu celular.
- O robô aguardará até 5 minutos pela leitura da autenticação.
- Nas execuções futuras, a sessão persistente será guardada na pasta `dados/sessao_whatsapp` e o robô conectará **sem pedir QR Code** novamente (caso a sessão expire ou o WhatsApp desconecte, basta escanear o QR Code de novo que a automação aguardará o login normalmente).

---

## ⚠️ Configurações Manuais Extras

Se você precisar alterar o nome padrão do grupo do WhatsApp que o bot busca ao apertar "Enter" direto no painel, edite o valor padrão do parâmetro `nome_grupo` na assinatura da função `gerar_json` dentro de [gerador_config.py](./src/config/gerador_config.py):
`def gerar_json(mes, ano, nome_grupo="Acólitos S. João Batista"):`

> [!IMPORTANT]
> Letras maiúsculas, minúsculas, pontuações e acentos no nome do grupo **devem coincidir exatamente** com o nome do grupo no seu WhatsApp.
