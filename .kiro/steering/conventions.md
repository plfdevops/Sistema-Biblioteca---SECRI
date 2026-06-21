# Convenções do Projeto — Biblioteca SECRI

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.8+ |
| Interface | NiceGUI (web UI via browser) |
| Deploy | Docker Compose (restart: always) |
| Banco | SQLite3 (stdlib) |
| E-mail | smtplib + Gmail SMTP |
| Relatórios | ReportLab |
| Build | PyInstaller → .exe |

## Regras de código

- GUI usa NiceGUI (web-based, acesso via browser em localhost:8080)
- Toda lógica de negócio em `services.py` — GUI nunca acessa o banco diretamente
- Conexões SQLite: abrir, operar, fechar (sem pool, sem ORM)
- Migrações de schema em `database.py` usando `ALTER TABLE` com try/except (idempotentes)
- Datas internas sempre ISO 8601 (`YYYY-MM-DD`); exibição sempre `dd/mm/aaaa`
- Config sensível (SMTP) em `config.json` (no `.gitignore`, nunca commitado)

## Padrões de arquitetura

- 3 camadas: GUI → Services → Database
- GUI é View+Controller; services é Model
- Notifier é serviço auxiliar (não acessa GUI)

## Convenções de GUI

- Tema: Catppuccin Mocha (cores definidas como constantes no topo de `gui/app.py`)
- Todos os diálogos: `Toplevel` + `transient` + `grab_set` + centrado
- Feedback de ações via status bar (não usar messagebox para sucesso rotineiro)
- Messagebox apenas para erros e confirmações destrutivas

## Proibições

- Não adicionar dependências sem justificativa (projeto é distribuído como .exe)
- Não usar threads para operações de banco (SQLite single-thread é suficiente)
- Não instalar cron/schtasks — agendamento é interno ao app via `root.after()`
- Não hardcodar e-mails ou senhas no código-fonte
- Não usar `import *`

## Estrutura de diretórios

```
Library/
├── main.py           # Servidor NiceGUI (ponto de entrada)
├── database.py       # Conexão + schema + migrations
├── services.py       # Toda lógica de negócio
├── notifier.py       # Envio de e-mail
├── config.json       # Config SMTP (não commitado)
├── gui/
│   ├── __init__.py
│   └── app.py        # Interface web NiceGUI
├── seed.py           # Dados de teste
├── Dockerfile        # Build da imagem
├── docker-compose.yml # Deploy com restart: always
├── requirements.txt  # Dependências pip
├── biblioteca.db     # Banco SQLite (não commitado)
└── .kiro/specs/      # Especificações SDD
```

## Como rodar

```bash
docker compose up -d
# Acesse: http://localhost:8080
```
