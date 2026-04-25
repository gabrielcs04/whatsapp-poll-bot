# 🤖 WhatsApp Poll Bot (Automação de Enquetes)

Um robô construído em Python e [Playwright](https://playwright.dev/python/) projetado para automatizar totalmente o trabalho manual de criar múltiplas enquetes semanais ou mensais em um grupo do WhatsApp Web.

## 📌 Visão Geral

O projeto foi criado para ser amigável e modular, evitando que você precise mexer no código o tempo todo. Ele é composto por três etapas interligadas:

1. **O Painel Interativo (`main.py`)**: É o único arquivo que você precisa executar. Ele gerencia as perguntas no terminal e orquestra o fluxo de todo o resto.
2. **O Gerador Automático (`gerador_config.py`)**: Ele descobre exatamente quais são os finais de semana (e terças-feiras) de um mês e ano específicos, e prepara o cronograma montando tudo em um arquivo `config.json`.
3. **O Robô (`criador_enquete.py`)**: Usa automação visual na web. Ele abre a interface, resgata a sessão salva do seu WhatsApp, pesquisa o grupo e dispara as enquetes do arquivo de configuração, simulando perfeitamente a digitação humana.

---

## 🚀 Requisitos

- Python `3.9` ou superior instalado no seu sistema.

## ⚙️ Instalação Passo a Passo

Abra o seu terminal na pasta do projeto e execute os passos abaixo.

**1. Crie e ative um ambiente virtual** *(Recomendado para não conflitar com outras versões na sua máquina)*
```bash
# No Windows:
python -m venv venv
venv\Scripts\activate

# No Mac / Linux:
python3 -m venv venv
source venv/bin/activate
```

**2. Instale as dependências Python**
```bash
pip install -r requirements.txt
```

**3. Instale o motor do navegador (Playwright)**
Esse comando fará o download da instância invisível/visível do Chromium (Chrome) para a automação:
```bash
playwright install chromium
```

---

## 🎮 Como Usar

Com o ambiente virtual ativado, rode sempre o arquivo principal:

```bash
python main.py
```

O terminal interativo aparecerá:
1. Responda qual **mês (ex: 5)** e qual **ano (ex: 2026)** você deseja gerar as reuniões.
2. O arquivo `config.json` será imediatamente atualizado nos bastidores.
3. Você será perguntado se deseja disparar os envios agora (`S/N`).

### 📱 Lendo o QR Code (Primeiro Login)

Na **primeira vez** que você deixar o robô iniciar o navegador, ele chegará na página principal do WhatsApp exigindo o **QR Code**:
- Use seu celular para ler o código tranquilamente.
- O robô possui um tempo longo de espera (até 5 min) para reconhecer que você fez o login.
- Nas execuções futuras, a pasta oculta `sessao_whatsapp` lembrará do seu dispositivo e **não vai pedir** o código novamente. O robô vai disparar no modo expresso!

---

## ⚠️ Configurações Manuais Extras

Se você precisar **mudar o nome exato do grupo** em que o robô deve entrar, basta editar a variável `nome_grupo` dentro do arquivo base ou diretamente no `gerador_config.py` na primeira linha da sua definição:
`def gerar_json(mes, ano, nome_grupo="ARQUIVOS IMPORTANTES"):`

Aviso: Letras maiúsculas e minúsculas no nome do grupo **importam**.
