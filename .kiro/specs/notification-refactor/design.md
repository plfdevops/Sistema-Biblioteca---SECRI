# Design: Refatoração do Sistema de Notificações

## Arquitetura

```
┌────────────────────────────────────────────────────────────────┐
│                         gui/app.py                              │
│  ┌──────────────┐              ┌──────────────────────────┐    │
│  │Botão Gestor  │──────────────▶ notifier.send_manager()  │    │
│  └──────────────┘              └──────────────────────────┘    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ root.after(3600000) → notifier.send_student_overdue()    │  │
│  │ (verifica atrasos a cada 1h + na abertura)                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                       notifier.py                               │
│                                                                 │
│  send_manager_notification()     → e-mail consolidado (gestor) │
│  send_student_notifications()    → e-mail individual (alunos)  │
│  _should_notify(loan) → bool     → checa notified_at + cooldown│
│  _mark_notified(loan_id)         → atualiza notified_at        │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                       services.py                               │
│                                                                 │
│  overdue_loans()          → já existe (retorna atrasos)        │
│  loan_book(..., email)    → recebe e-mail do aluno             │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                       database.py                               │
│                                                                 │
│  Migração: ALTER TABLE loans ADD COLUMN email TEXT              │
│  Migração: ALTER TABLE loans ADD COLUMN notified_at TEXT        │
└────────────────────────────────────────────────────────────────┘
```

## Componentes modificados

| Componente | Mudança |
|-----------|---------|
| `database.py` | Adicionar migração para colunas `email` e `notified_at` em `loans` |
| `services.py` | `loan_book()` aceita parâmetro `email`; `overdue_loans()` retorna `email` e `notified_at` |
| `notifier.py` | Refatorar em duas funções: gestor (consolidado) e aluno (individual) |
| `gui/app.py` | Campo e-mail no diálogo de empréstimo; timer periódico; botão mantido |
| `main.py` | Remover chamada a `agendar.main()` |
| `agendar.py` | **Deletar** |
| `config.json` | Adicionar campo `notify_cooldown_days` (default: 3) |

## Migração do banco

```sql
-- Idempotente (mesmo padrão já usado em database.py)
ALTER TABLE loans ADD COLUMN email TEXT;
ALTER TABLE loans ADD COLUMN notified_at TEXT;
```

## Fluxo: Notificação automática ao aluno

```
1. App abre → _check_overdue_students() executa
2. Busca overdue_loans() onde email IS NOT NULL
3. Para cada empréstimo:
   a. Se notified_at IS NULL ou (today - notified_at) >= cooldown_days:
      - Envia e-mail individual ao aluno
      - UPDATE loans SET notified_at = today WHERE id = ?
4. Agenda próxima verificação: root.after(3600000, _check_overdue_students)
```

## Fluxo: Botão do gestor (mantido)

```
1. Gestor clica "Notificar Atrasos"
2. Chama notifier.send_manager_notification()
3. Monta corpo com TODOS os atrasos (mesmo sem e-mail cadastrado)
4. Envia para config.notify_emails
5. Mostra resultado em messagebox
```

## Template de e-mail para o aluno

```
Assunto: [Biblioteca SECRI] Devolução pendente - {título}

Olá {pessoa},

O livro "{título}" emprestado em {data_empréstimo} tinha prazo de devolução
para {deadline}. Por favor, devolva o quanto antes na biblioteca.

Atenciosamente,
Biblioteca SECRI
```

## Invariantes

- Nunca enviar mais de 1 e-mail por empréstimo dentro do período de cooldown
- Empréstimos sem e-mail cadastrado são ignorados pela notificação automática (mas aparecem no relatório do gestor)
- Se o envio SMTP falhar, não atualizar `notified_at` (garante retry na próxima verificação)
- O timer usa `root.after()` (non-blocking, roda na thread principal do Tkinter)

## Dependências externas

| Serviço | Propósito |
|---------|-----------|
| Gmail SMTP (smtp.gmail.com:587) | Envio de e-mails (já existente) |
