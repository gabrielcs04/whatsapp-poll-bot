# 🧠 Planejamento de Automação - WhatsApp Web com Python

## 📌 Objetivo

Quero desenvolver uma automação simples em Python que:

1. Abra o WhatsApp Web no navegador
2. Acesse um grupo específico
3. Crie **múltiplas enquetes automaticamente** dentro desse grupo
4. Utilize dados fornecidos por mim (título da enquete + opções)

---

## ⚙️ Requisitos Funcionais

* O script deve:

  * Abrir o navegador (preferencialmente Google Chrome)
  * Acessar o WhatsApp Web
  * Aguardar login via QR Code (caso necessário)
  * Buscar e entrar em um grupo específico pelo nome
  * Criar enquetes automaticamente dentro do grupo

* Entrada de dados:

  * Lista de enquetes no seguinte formato:

```json
[
  {
    "titulo": "Qual dia é melhor?",
    "opcoes": ["Segunda", "Quarta", "Sexta"]
  },
  {
    "titulo": "Qual horário?",
    "opcoes": ["18h", "19h", "20h"]
  }
]
```

* Para cada item:

  * Criar uma enquete no WhatsApp Web
  * Preencher o título
  * Adicionar todas as opções
  * Enviar a enquete

---

## 🧪 Funcionalidades Extras (Opcional)

* Permitir configurar o nome do grupo via variável
* Log simples no terminal informando:

  * Quando entrou no grupo
  * Quando criou cada enquete
* Delay entre criação de enquetes (para evitar bloqueios)

---

## 📖 Saída Esperada

Quero que você gere:

1. Código completo funcional (`main.py`)
2. Arquivo `requirements.txt`
3. Instruções de execução (README)
4. Estrutura organizada e comentada

---

## ⚠️ Observações

* A automação deve simular comportamento humano básico
* Evitar ações muito rápidas (inserir delays)
* Compatível com WhatsApp Web atual

---

## 🎯 Objetivo Final

Rodar um script Python que, ao executar, abra o WhatsApp Web, entre no grupo desejado e crie automaticamente todas as enquetes definidas no input.
