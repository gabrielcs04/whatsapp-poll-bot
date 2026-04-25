# Robô de Enquetes - WhatsApp Web

Este script Python permite a automação no WhatsApp Web para acessar grupos e gerar múltiplas enquetes automaticamente. Ele utiliza a robusta biblioteca [Playwright](https://playwright.dev/python/) para executar simulações de comportamento de digitação e cliques visuais sobre uma instância de navegação que se recusa a perder seu estado de login.

## Requisitos
- Você precisa ter o Python Instalado (recomendamos a versão > `3.9`).

## 1. Instalação e Configuração

*Abra um terminal na pasta onde este projeto se encontra e execute os comandos:*

1. Crie seu ambiente virtual (Altamente recomendado):
```bash
python -m venv venv
venv\Scripts\activate  # No Windows
```

2. Instale o framework:
```bash
pip install -r requirements.txt
```

3. Instale os Navegadores Nativos acoplados ao Playwright (Obrigatório!):
```bash
playwright install chromium
```

## 2. Como Utilizar o Bot

Abra no seu editor o arquivo central: `main.py`! 
Lá no topo, estão as configurações. Você deve alterar as opções `NOME_GRUPO` para baterem **idênticas ao nome do grupo que existe no seu Whatsapp**! A caixa baixa e a caixa alta importam.

Você também pode e **deve** atualizar a const `ENQUETES_JSON` adicionando os títulos e as opções que você quiser para a automações que vão ocorrer.

E então as coisas estão prontas...
No seu terminal basta rodar:

```bash
python main.py
```

### O Primeiro Login (Aviso de QRCode!)

Na **primeira vez** que você rodar, um Chrome enorme vai se abrir para a página inicial do WhatsApp Web pedindo o Código Leitor de QR (`WhatsApp >Aparelhos Conectados`).
1. Faça a leitura confortavelmente;
2. Espere a barrinha lateral da sua lista de conversas carregar.
3. Não use a aba paralela enquanto o robô clica e digita para poder visualizar a perfeição e o auto-send.

Na segunda vez adiante, devido a pasta local que deixamos rodada com o cache ali ("./sessao_whatsapp"), **o script não mais lhe pedirá o leitor de Qr Code**. Vai entrar focado diretamente!
