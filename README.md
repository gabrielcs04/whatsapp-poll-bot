# 🤖 WhatsApp Poll Bot (Automação de Enquetes)

Um robô construído em Python e [Playwright](https://playwright.dev/python/) projetado para automatizar totalmente o trabalho manual de criar múltiplas enquetes semanais/mensais em um grupo do WhatsApp Web e também extrair os resultados (votos) dessas enquetes de forma estruturada.

## 📌 Visão Geral

O projeto foi criado para ser amigável e modular, evitando que você precise mexer no código o tempo todo. Ele é composto por quatro scripts centrais e utilitários:

1. **O Painel Interativo (`main.py`)**: É o único arquivo que você precisa executar. Ele gerencia as perguntas no terminal e orquestra o menu principal.
2. **O Gerador Automático (`gerador_config.py`)**: Ele descobre exatamente quais são os finais de semana (e terças-feiras) de um mês e ano específicos, e prepara o cronograma montando tudo em um arquivo `config.json`.
3. **O Robô Criador (`criador_enquete.py`)**: Usa automação visual na web. Ele abre a interface, resgata a sessão salva do seu WhatsApp, pesquisa o grupo e dispara as enquetes baseadas no `config.json`.
4. **O Robô Leitor (`leitor_enquete.py`)**: Acessa a conversa, procura pelas enquetes geradas, abre os detalhes dos votos (navegando automaticamente em telas e sub-telas) e gera um relatório estruturado em `resultados_enquetes.md`.

---

## 🚀 Requisitos

- Python `3.9` ou superior instalado no seu sistema.

## ⚙️ Como Instalar e Rodar (Modo Simplificado)

Nós simplificamos todo o processo. Você não precisa mais criar e gerenciar o ambiente virtual manualmente ou baixar os navegadores por conta própria! 

Basta abrir o seu terminal na pasta do projeto e rodar o comando de inicialização automática. Ele fará a configuração da `venv`, instalação de dependências, download do navegador da automação e já iniciará o painel:

```bash
# No Windows
python run.py

# No Mac / Linux
python3 run.py
```

Pronto! **Sempre que quiser usar a ferramenta, basta rodar esse mesmo comando.** O script é inteligente e só instalará as dependências se for a primeira vez. Assim que o painel abrir:

Um menu interativo aparecerá com 3 opções principais:
- **Opção 1:** Gerar e enviar enquetes novas (onde você digita mês, ano e gera o `.json`).
- **Opção 2:** Ler resultados de enquetes existentes (o robô entrará no grupo e raspará todos os votos para um `.md`).
- **Opção 3:** Sair.

### 📱 Lendo o QR Code (Primeiro Login)

Na **primeira vez** que você deixar o robô iniciar o navegador, ele chegará na página principal do WhatsApp exigindo o **QR Code**:
- Use seu celular para ler o código tranquilamente.
- O robô possui um tempo longo de espera (até 5 min) para reconhecer que você fez o login.
- Nas execuções futuras, a pasta oculta `sessao_whatsapp` lembrará do seu dispositivo e **não vai pedir** o código novamente. O robô vai disparar no modo expresso!

---

## ⚠️ Configurações Manuais Extras

Se você precisar **mudar o nome exato do grupo** em que o robô deve entrar, você poderá informar isso diretamente no menu. Porém, se quiser mudar o valor padrão (caso o usuário aperte "Enter" direto), basta editar a variável `nome_grupo` dentro do arquivo `gerador_config.py` na primeira linha da sua definição:
`def gerar_json(mes, ano, nome_grupo="Acólitos S. João Batista"):`

Aviso: Letras maiúsculas e minúsculas no nome do grupo **importam**.
