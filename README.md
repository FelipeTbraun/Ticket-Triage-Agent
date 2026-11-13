# 🎫 ticket-triage-agent

> ⚠️ **Projeto de estudos, em desenvolvimento.**
> Este repositório é um projeto de aprendizado. Ele ainda está evoluindo, não foi feito para produção e a estrutura pode mudar. O histórico de commits e Pull Requests faz parte do estudo.

Ferramenta de linha de comando em Python que usa um modelo de IA (LLM) para **triar chamados de suporte técnico**: classifica categoria e prioridade, resume o problema, sugere uma ação e gera um relatório em Markdown.

---

## 🎯 Objetivo do projeto

Praticar, na prática:

- Integração de **LLMs via API** em uma aplicação real
- **CLI em Python** com código separado em módulos
- **Validação de dados** com Pydantic e tratamento de respostas imprevisíveis de IA
- Persistência com **SQLite**
- **Testes automatizados** com `pytest` e integração contínua com **GitHub Actions**
- Fluxo profissional de **Git/GitHub**: branches, Pull Requests, Issues e Conventional Commits

O tema vem da minha experiência em suporte técnico de TI.

## ⚙️ Como funciona

```
CSV → loader → classifier (IA) → storage (SQLite) → report (Markdown)
```

1. Lê os chamados de um arquivo CSV e valida cada linha (linhas inválidas são reportadas, sem derrubar a leitura)
2. Envia cada chamado ao modelo de IA e recebe **categoria**, **prioridade**, **resumo** e **ação sugerida**
3. Valida a resposta. Se vier em formato errado, tenta de novo. Se o serviço recusar por limite de requisições ou sobrecarga (erros 429 e 503), espera e tenta de novo com *backoff* exponencial
4. Salva o resultado em SQLite (rodar de novo classifica **apenas os chamados que faltam**)
5. Gera um relatório em Markdown. Veja um [exemplo de relatório](docs/exemplo-relatorio.md)

## 🚧 Status

| Etapa | Status |
|---|---|
| Estrutura inicial do repositório | ✅ |
| Modelos de dados e leitura do CSV | ✅ |
| Provedor de IA (Gemini) e classificador | ✅ |
| Validação da resposta, retry e controle de limite de requisições | ✅ |
| Armazenamento em SQLite | ✅ |
| Relatório em Markdown | ✅ |
| Testes automatizados + CI (GitHub Actions) | ✅ |
| Teste de ponta a ponta com a API real do Gemini | ✅ |
| *(Fase 2)* Transformar em agente com *function calling* | ⬜ |

## 🛠️ Tecnologias

- **Python 3.11+**
- **Google Gemini API** com o SDK `google-genai` (testado com o modelo `gemini-3.5-flash`)
- **Pydantic** para validação
- **SQLite** para armazenamento
- **pytest** para testes e **GitHub Actions** para CI

## ▶️ Como rodar

### 1. Clonar e preparar o ambiente

```bash
git clone https://github.com/FelipeTbraun/ticket-triage-agent.git
cd ticket-triage-agent
python -m venv .venv
```

Ativar o ambiente virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

Instalar as dependências e o projeto:

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Testar sem chave e sem internet (provedor falso)

O provedor `fake` classifica por palavras-chave. **Não é IA**, serve para testar o fluxo:

```bash
triage run --provider fake
triage report
```

### 3. Usar o Gemini

1. Gere uma chave no [Google AI Studio](https://aistudio.google.com).
2. Crie o arquivo `.env` a partir do modelo e cole a chave:

```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```

```
GEMINI_API_KEY=sua_chave_aqui
```

3. Rode:

```bash
triage run --limite 5     # comece com poucos chamados
triage run                # classifica o restante
triage report
```

O modelo padrão é `gemini-3.5-flash`. Os nomes de modelo do Gemini mudam com frequência e variam conforme a conta. Se aparecer erro de modelo não encontrado (404), defina `GEMINI_MODEL` no `.env` com um nome válido listado no AI Studio.

### Opções do `triage run`

| Opção | O que faz |
|---|---|
| `--csv CAMINHO` | arquivo de chamados (padrão: `data/tickets_sample.csv`) |
| `--db CAMINHO` | banco SQLite (padrão: `data/triage.db`) |
| `--provider gemini\|fake` | provedor de IA (padrão: `gemini`) |
| `--pausa SEGUNDOS` | espera entre chamadas (padrão: 4 s no Gemini, para respeitar o limite por minuto) |
| `--limite N` | classifica no máximo N chamados |
| `--reprocessar` | classifica de novo os que já estão no banco |

### Solução de problemas

| Sintoma | O que fazer |
|---|---|
| `triage` não é reconhecido | Ative o ambiente virtual e rode `pip install -e .`. Alternativa: `python -m triage ...` |
| `GEMINI_API_KEY não encontrada` | Confira se o `.env` está na raiz do projeto |
| Erro 404 de modelo | Defina `GEMINI_MODEL` no `.env` com um modelo disponível na sua conta |
| Falhas por limite ou sobrecarga | Espere alguns minutos e rode `triage run` de novo (ele só tenta os que faltam), ou use `--pausa 10` |
| "Nenhum chamado novo para classificar" | Os chamados já estão no banco. Use `--reprocessar` ou apague `data/triage.db` |

## 📁 Estrutura

```
ticket-triage-agent/
├── src/triage/
│   ├── cli.py            # comandos: run e report
│   ├── models.py         # Ticket e Classificacao (Pydantic)
│   ├── loader.py         # leitura e validação do CSV
│   ├── classifier.py     # prompt, validação da resposta, retry e backoff
│   ├── providers/
│   │   ├── base.py       # interface do provedor + exceções
│   │   ├── gemini.py     # provedor real
│   │   └── fake.py       # provedor falso, para testes e demonstração
│   ├── storage.py        # SQLite
│   └── report.py         # relatório em Markdown
├── data/tickets_sample.csv   # 50 chamados fictícios
├── docs/exemplo-relatorio.md
├── tests/
├── .github/workflows/ci.yml
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## 🧠 Decisões técnicas

- **Provedor atrás de uma interface.** O classificador só conhece `gerar(prompt) -> str`. Trocar o Gemini por outro serviço (ou por um modelo local) é criar uma classe nova, sem mexer no resto.
- **Resposta validada com Pydantic.** Categoria e prioridade são `Enum`s. Qualquer valor fora da lista é rejeitado e a chamada é repetida.
- **Limite de requisições e sobrecarga.** Pausa entre chamadas e, em caso de erro 429 ou 503, espera com *backoff* exponencial.
- **Idempotência.** Rodar o comando de novo só processa o que falta, sem gastar cota à toa.
- **Testes sem rede.** Toda a suíte (e o CI) roda sem chave de API, usando o provedor falso e um cliente simulado.
- **Conteúdo do chamado é dado não confiável.** O prompt instrui o modelo a não seguir instruções escritas dentro do texto do chamado.

## 🧪 Testes

```bash
python -m pytest
```

## 🔐 Dados e segurança

- Todos os chamados de exemplo são **fictícios**. **Não use dados reais** de empresas ou clientes.
- Na camada gratuita de APIs de IA, o conteúdo enviado pode ser usado pelo provedor para melhorar seus produtos.
- A chave de API fica no arquivo `.env`, que **não é versionado**. O repositório só tem o `.env.example`.

## 📚 O que estou aprendendo

<!-- Preencha com suas palavras. Sugestões do que contar:
     - como o Pydantic converte e valida tipos
     - por que o provedor de IA fica atrás de uma interface
     - o que é backoff exponencial e por que usar
     - o que deu errado no caminho (modelo inexistente, CSV vazio, erro 503) e como resolvi -->

## 🤝 Contribuições

Como é um projeto de estudo pessoal, ainda não aceito contribuições. Sugestões são bem-vindas nas **Issues**.

## 📄 Licença

A definir.

---

Feito por [Felipe Braun](https://github.com/FelipeTbraun) 👨‍💻
