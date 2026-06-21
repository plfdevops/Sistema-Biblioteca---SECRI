# Biblioteca SECRI

Sistema de gerenciamento de biblioteca com interface web moderna.

## Como rodar

```bash
docker compose up -d
```

Acesse: **http://localhost:8080**

O container reinicia automaticamente se a máquina reiniciar.

## Funcionalidades

- Cadastro de livros (título, autor, categoria, ano, código)
- Empréstimo com prazo de devolução e e-mail do aluno
- Devolução com confirmação
- Renovação de empréstimo
- Detecção automática de atrasos
- Notificação por e-mail para alunos com atraso (a cada 1h, cooldown de 7 dias)
- Notificação manual para o gestor (relatório consolidado)
- Cadastro de alunos (página /alunos) com autocomplete no empréstimo
- Busca por título, autor ou categoria
- Filtros por categoria e status
- Relatórios (top livros, top alunos)
- Exportação de relatório em PDF
- Dashboard com métricas (total, disponíveis, alugados, atrasados, devoluções/mês)

## Configuração

Copie `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
```

## Popular com dados de teste

```bash
docker exec library-biblioteca-1 python seed.py
```

## Rodar testes

```bash
docker run --rm -v $(pwd):/app -w /app python:3.11-slim sh -c \
  "pip install -q pytest reportlab nicegui && pytest tests/ -v"
```

## Estrutura

```
├── src/
│   ├── main.py              # Servidor NiceGUI
│   ├── database.py          # Banco SQLite + migrations
│   ├── notifier.py          # Envio de e-mails
│   ├── services/
│   │   ├── books.py         # CRUD livros
│   │   ├── loans.py         # Empréstimos, devoluções, renovação
│   │   ├── students.py      # CRUD alunos
│   │   ├── stats.py         # Dashboard
│   │   └── utils.py         # Formatação, validação
│   └── gui/
│       ├── app.py           # Rotas
│       ├── library.py       # Página principal
│       ├── dialogs.py       # Diálogos (adicionar, editar, alugar...)
│       ├── students.py      # Página de alunos
│       └── pdf.py           # Exportação PDF
├── tests/                   # 52 testes (pytest)
├── data/                    # Banco SQLite (volume Docker, gitignored)
├── seed.py                  # Dados de teste
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Stack

- Python 3.11
- NiceGUI (interface web)
- SQLite (banco de dados)
- ReportLab (PDF)
- Docker (deploy)
