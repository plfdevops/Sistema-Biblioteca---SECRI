# Feature: Refatoração do Sistema de Notificações

## Contexto

O sistema atual envia notificações de atraso via cron/schtasks para uma lista fixa de e-mails (gestores). A proposta é mudar para um modelo event-driven onde:
1. O **aluno** (quem pegou o livro) recebe e-mail automaticamente quando o empréstimo atrasa
2. O **gestor** pode disparar manualmente um relatório consolidado pelo botão na GUI

## User Stories

### US-1: Notificação automática ao aluno por atraso
WHEN um empréstimo ultrapassa a `deadline_date`  
THEN o sistema SHALL enviar um e-mail para o aluno informando o atraso

### US-2: Botão de notificação para o gestor
WHEN o gestor clica no botão "Notificar Atrasos" na GUI  
THEN o sistema SHALL enviar um e-mail consolidado para os e-mails configurados em `config.json.notify_emails` com todos os atrasos ativos

### US-3: Cadastro de e-mail do aluno no empréstimo
WHEN o gestor registra um empréstimo  
THEN o sistema SHALL solicitar o e-mail do aluno (campo obrigatório se quiser notificação automática, opcional caso contrário)

### US-4: Eliminação do agendamento cron/schtasks
WHEN o sistema é iniciado  
THEN o sistema SHALL NOT configurar tarefas agendadas no sistema operacional  
AND a verificação de atrasos será feita dentro do próprio app (ao abrir e periodicamente enquanto aberto)

### US-5: Controle de duplicidade de notificações
WHEN um e-mail de atraso já foi enviado para um aluno sobre um empréstimo específico  
THEN o sistema SHALL NOT reenviar para o mesmo empréstimo até que se passem 3 dias (configurável)

## Acceptance Criteria

- [ ] Campo `email` na tabela `loans` (opcional, preenchido no momento do empréstimo)
- [ ] Ao emprestar, diálogo pede e-mail do aluno (campo opcional com label "para receber aviso de atraso")
- [ ] Na abertura do app, verifica atrasos e envia e-mail individual para cada aluno com e-mail cadastrado
- [ ] Verificação periódica de atrasos a cada 1h enquanto o app estiver aberto (via `root.after()`)
- [ ] Coluna `notified_at` na tabela `loans` registra último envio para evitar spam
- [ ] Reenvio apenas após 3 dias do último aviso (configurável via `config.json`)
- [ ] Botão "Notificar Atrasos" continua enviando relatório consolidado para os e-mails do gestor
- [ ] Arquivo `agendar.py` removido do projeto
- [ ] `main.py` não configura mais cron/schtasks
- [ ] E-mail para o aluno tem tom educado: informa livro, data de empréstimo, prazo, e pede devolução

## Fora de escopo

- Cadastro persistente de alunos (por enquanto é texto livre + e-mail no empréstimo)
- Notificação por SMS ou WhatsApp
- Painel web — o sistema continua sendo desktop Tkinter
- Autenticação de usuários na GUI
