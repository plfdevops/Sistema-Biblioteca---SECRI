# Tasks: Refatoração do Sistema de Notificações

- [x] Task 1: Migração do banco — adicionar colunas `email` e `notified_at` em `loans` (em `database.py`, bloco de migrations idempotentes)
- [x] Task 2: Atualizar `services.loan_book()` para aceitar parâmetro `email` e persistir
- [x] Task 3: Atualizar `services.overdue_loans()` para retornar campos `email` e `notified_at`
- [x] Task 4: Refatorar `notifier.py` — separar em `send_manager_notification()` e `send_student_notifications()`
- [x] Task 5: Adicionar `notify_cooldown_days` ao `config.json` (default 3)
- [x] Task 6: Atualizar diálogo de empréstimo na GUI — campo "E-mail do aluno (opcional)"
- [x] Task 7: Implementar timer periódico na GUI — `root.after(3600000)` chamando verificação de atrasos
- [x] Task 8: Atualizar botão "Notificar Atrasos" para usar `send_manager_notification()`
- [x] Task 9: Remover `agendar.py` e remover chamada em `main.py`
- [x] Task 10: Atualizar `seed.py` — incluir e-mails fictícios nos empréstimos de exemplo
- [x] Task 11: Testar fluxo completo (empréstimo com e-mail → atraso → notificação enviada → cooldown respeitado)
