# Design: Melhoria da Interface Gráfica

## Layout proposto

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Sistema de Biblioteca SECRI                                              │
├──────────────────────────────────────────────────────────────────────────┤
│ [+ Adicionar] [Editar] [Remover] │ [Alugar] [Devolver] │ [Relatórios] [Notificar] │
│  ─── Livros ───                    ─── Empréstimos ───    ─── Outros ───           │
├──────────────────────────────────────────────────────────────────────────┤
│  Categoria: [▼ Todas]  Status: [▼ Todos]              [___Buscar___] [🔍] │
├──────────────────────────────────────────────────────────────────────────┤
│  N  │ Título              │ Autor          │ Categoria │ Ano  │ Status   │
│─────┼─────────────────────┼────────────────┼───────────┼──────┼──────────│
│  01 │ Dom Casmurro         │ Machado de A.  │ Romance   │ 1899 │●Disponív.│
│  02 │ O Cortiço            │ Aluísio Azev.  │ Romance   │ 1890 │●Alugado  │
│  03 │ Memórias Póstumas    │ Machado de A.  │ Romance   │ 1881 │●Atrasado │
├──────────────────────────────────────────────────────────────────────────┤
│  Total: 170 │ Disponíveis: 155 │ Alugados: 10 │ ⚠ Atrasados: 5        │
│  Último: "Livro emprestado com sucesso" (14:30)                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Componentes da refatoração

| Componente | Mudança |
|-----------|---------|
| Toolbar | Dividir em 3 frames com `ttk.Separator(orient=VERTICAL)` entre eles |
| Status bar | Duas linhas: contadores + mensagem do último evento com timestamp |
| Diálogos | Centralizar (`win.geometry(f"+{x}+{y}")`), adicionar botão Cancelar |
| Treeview | Usar `pack(fill=BOTH, expand=True)` garantindo resize correto |
| Bindings | Adicionar `<Delete>`, `<Control-n>`, `<F5>`, `<Control-f>` |

## Status bar — nova estrutura

```python
# Frame inferior com 2 labels
frame_status = ttk.Frame(root)
  ├── label_counts   → "Total: X │ Disponíveis: Y │ Alugados: Z │ ⚠ Atrasados: W"
  └── label_event    → "Último: <ação> (HH:MM)" — foreground dinâmico
```

O contador de "Atrasados" é renderizado em vermelho (`RED`) quando > 0.

## Diálogos — padrão consistente

Todos os diálogos seguirão:
1. `Toplevel` com `transient(root)` + `grab_set()`
2. Centralizado sobre a janela pai
3. Grid com labels à esquerda, entries à direita
4. Rodapé com `[Cancelar]` à esquerda e `[Confirmar/Salvar]` à direita
5. Tecla Escape fecha o diálogo

```python
def _center_dialog(win, width, height):
    x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
    y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")
```

## Atalhos de teclado

| Tecla | Ação | Método |
|-------|------|--------|
| `Delete` | Remover livro selecionado | `_remove()` |
| `Ctrl+N` | Abrir diálogo adicionar | `_dialog_add()` |
| `F5` | Refresh da lista | `_refresh_list()` |
| `Ctrl+F` | Focar campo de busca | `entry_search.focus_set()` |
| `Escape` (em diálogo) | Fechar diálogo | `win.destroy()` |

## Invariantes

- Tema Catppuccin Mocha inalterado (mesmas cores)
- Nenhuma funcionalidade removida — apenas reorganização visual
- Todos os fluxos existentes continuam funcionando da mesma forma
- Compatível com PyInstaller (sem dependências novas)
