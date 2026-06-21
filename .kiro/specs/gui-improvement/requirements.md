# Feature: Melhoria da Interface Gráfica

## Contexto

A interface atual funciona mas é visualmente básica — toolbar com botões amontoados em uma linha, sem ícones, sem separação visual clara entre ações. O objetivo é tornar a GUI mais intuitiva, organizada e profissional, mantendo a stack Tkinter.

## User Stories

### US-1: Toolbar organizada por grupo de ações
WHEN o usuário abre o sistema  
THEN os botões SHALL estar agrupados logicamente (Livros | Empréstimos | Relatórios)

### US-2: Feedback visual de ações
WHEN uma operação é concluída (empréstimo, devolução, envio de notificação)  
THEN o sistema SHALL exibir feedback na status bar (não apenas em messagebox)

### US-3: Confirmação visual de atrasos
WHEN existem livros atrasados  
THEN o sistema SHALL exibir um indicador visual na barra de status com contagem de atrasos em destaque (vermelho)

### US-4: Diálogos mais limpos
WHEN o usuário abre um diálogo (adicionar, editar, emprestar)  
THEN o diálogo SHALL ter layout consistente, campos alinhados, e botão de cancelar

### US-5: Responsividade
WHEN o usuário redimensiona a janela  
THEN a Treeview e filtros SHALL se ajustar proporcionalmente

### US-6: Atalhos de teclado
WHEN o usuário pressiona Delete  
THEN o sistema SHALL acionar remoção (com confirmação)  
WHEN o usuário pressiona Ctrl+N  
THEN o sistema SHALL abrir diálogo de adicionar

## Acceptance Criteria

- [ ] Toolbar dividida em frames com separadores visuais (Livros | Empréstimos | Outros)
- [ ] Botões com texto descritivo claro (sem abreviações confusas)
- [ ] Status bar mostra último evento realizado ("Livro emprestado com sucesso", "E-mail enviado", etc)
- [ ] Contador de atrasos em vermelho na status bar (permanente, atualiza com refresh)
- [ ] Todos os diálogos têm botão "Cancelar" explícito
- [ ] Diálogos centrados em relação à janela principal
- [ ] Janela mínima 900x560, resizable
- [ ] Atalhos: Delete (remover), Ctrl+N (adicionar), F5 (refresh), Ctrl+F (buscar)
- [ ] Double-click na Treeview continua abrindo detalhes (mantido)
- [ ] Tema Catppuccin Mocha mantido (escuro)

## Fora de escopo

- Migração para outro framework (CustomTkinter, PyQt, etc.) — mantemos Tkinter puro
- Ícones gráficos (ficaria pesado para PyInstaller, mantemos texto)
- Multi-idioma
- Dark/Light mode toggle
