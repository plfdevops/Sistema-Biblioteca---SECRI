import tkinter as tk
from tkinter import ttk, messagebox
import services

# Cores
BG = "#1e1e2e"
BG_LIGHT = "#2a2a3e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Biblioteca")
        self.root.geometry("900x560")
        self.root.configure(bg=BG)
        self._setup_style()
        self._build_ui()
        self._atualizar_lista()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, fieldbackground=BG_LIGHT)
        style.configure("TButton", background=ACCENT, foreground="#11111b", padding=6, font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#74c7ec")])
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground=BG_LIGHT, foreground=FG)
        style.configure("Treeview", background=BG_LIGHT, foreground=FG, fieldbackground=BG_LIGHT, rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#313244", foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#45475a")])

    def _build_ui(self):
        # Título
        ttk.Label(self.root, text="Sistema de Biblioteca", font=("Segoe UI", 16, "bold"), foreground=ACCENT).pack(pady=(15, 5))

        # Frame de ações
        frame_top = ttk.Frame(self.root)
        frame_top.pack(fill="x", padx=15, pady=5)

        ttk.Button(frame_top, text="+ Adicionar", command=self._dialog_adicionar).pack(side="left", padx=3)
        ttk.Button(frame_top, text="X Remover", command=self._remover).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Alugar", command=self._dialog_alugar).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Devolver", command=self._devolver).pack(side="left", padx=3)

        # Busca
        self.var_busca = tk.StringVar()
        entry = ttk.Entry(frame_top, textvariable=self.var_busca, width=22)
        entry.pack(side="right", padx=3)
        entry.bind("<Return>", lambda e: self._buscar())
        ttk.Button(frame_top, text="Buscar", command=self._buscar).pack(side="right", padx=3)
        ttk.Button(frame_top, text="Todos", command=lambda: self._atualizar_lista()).pack(side="right", padx=3)

        # Tabela
        frame_tree = ttk.Frame(self.root)
        frame_tree.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("ID", "Título", "Autor", "Categoria", "Ano", "Status")
        self.tree = ttk.Treeview(frame_tree, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Título", width=250)
        self.tree.column("Autor", width=180)
        self.tree.column("Categoria", width=120)
        self.tree.column("Ano", width=50, anchor="center")
        self.tree.column("Status", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Duplo clique para detalhes
        self.tree.bind("<Double-1>", self._detalhes_livro)

        # Barra de status
        self.status_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 9), foreground=YELLOW).pack(pady=(0, 10))

    def _atualizar_lista(self, livros=None):
        self.tree.delete(*self.tree.get_children())
        dados = livros or services.listar_livros()
        for l in dados:
            status = "Disponível" if l["disponivel"] else "Alugado"
            tag = "disponivel" if l["disponivel"] else "alugado"
            self.tree.insert("", "end", values=(l["id"], l["titulo"], l["autor"], l["categoria"] or "", l["ano"] or "", status), tags=(tag,))
        self.tree.tag_configure("disponivel", foreground=GREEN)
        self.tree.tag_configure("alugado", foreground=RED)
        total = len(dados)
        alugados = sum(1 for l in dados if not l["disponivel"])
        self.status_var.set(f"Total: {total} livros | Disponíveis: {total - alugados} | Alugados: {alugados}")

    def _selecionado_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro.")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _detalhes_livro(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        valores = self.tree.item(sel[0])["values"]
        livro_id = int(valores[0])

        win = tk.Toplevel(self.root)
        win.title(f"Detalhes - {valores[1]}")
        win.geometry("450x350")
        win.configure(bg=BG)
        win.transient(self.root)

        # Info do livro
        info_frame = tk.Frame(win, bg=BG_LIGHT, padx=15, pady=10)
        info_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(info_frame, text=str(valores[1]), font=("Segoe UI", 13, "bold"), bg=BG_LIGHT, fg=ACCENT).pack(anchor="w")
        tk.Label(info_frame, text=f"Autor: {valores[2]}", font=("Segoe UI", 10), bg=BG_LIGHT, fg=FG).pack(anchor="w")
        tk.Label(info_frame, text=f"Categoria: {valores[3] or 'N/A'}  |  Ano: {valores[4] or 'N/A'}", font=("Segoe UI", 10), bg=BG_LIGHT, fg=FG).pack(anchor="w")
        is_disponivel = str(valores[5]) == "Disponível"
        status_color = GREEN if is_disponivel else RED
        status_text = "✅ Disponível" if is_disponivel else "🔴 Alugado"
        tk.Label(info_frame, text=f"Status: {status_text}", font=("Segoe UI", 10, "bold"), bg=BG_LIGHT, fg=status_color).pack(anchor="w", pady=(5, 0))

        # Histórico de empréstimos
        tk.Label(win, text="Histórico de Empréstimos", font=("Segoe UI", 11, "bold"), bg=BG, fg=YELLOW).pack(anchor="w", padx=15, pady=(5, 0))

        hist_frame = tk.Frame(win, bg=BG)
        hist_frame.pack(fill="both", expand=True, padx=15, pady=5)

        historico = services.historico_emprestimos(livro_id)
        if not historico:
            tk.Label(hist_frame, text="Nenhum empréstimo registrado.", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(pady=10)
        else:
            cols_h = ("Pessoa", "Retirada", "Devolução")
            tree_h = ttk.Treeview(hist_frame, columns=cols_h, show="headings", height=5)
            for c in cols_h:
                tree_h.heading(c, text=c)
                tree_h.column(c, width=130)
            for h in historico:
                dev = h["data_devolucao"] or "⏳ Pendente"
                tree_h.insert("", "end", values=(h["pessoa"], h["data_retirada"], dev))
            tree_h.pack(fill="both", expand=True)

        ttk.Button(win, text="Fechar", command=win.destroy).pack(pady=8)

    def _dialog_adicionar(self):
        win = tk.Toplevel(self.root)
        win.title("Adicionar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        campos = {}
        for i, (label, key) in enumerate([("Título*", "titulo"), ("Autor*", "autor"), ("Categoria", "categoria"), ("Ano", "ano")]):
            tk.Label(win, text=label, bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=i, column=0, padx=10, pady=6, sticky="e")
            var = tk.StringVar()
            ttk.Entry(win, textvariable=var, width=30).grid(row=i, column=1, padx=10, pady=6)
            campos[key] = var

        def salvar():
            t, a = campos["titulo"].get().strip(), campos["autor"].get().strip()
            if not t or not a:
                messagebox.showerror("Erro", "Título e Autor são obrigatórios.", parent=win)
                return
            ano = campos["ano"].get().strip()
            services.adicionar_livro(t, a, campos["categoria"].get().strip(), int(ano) if ano.isdigit() else None)
            win.destroy()
            self._atualizar_lista()

        ttk.Button(win, text="Salvar", command=salvar).grid(row=4, column=1, pady=12, sticky="e", padx=10)

    def _remover(self):
        lid = self._selecionado_id()
        if lid and messagebox.askyesno("Confirmar", "Remover este livro e todo seu histórico?"):
            services.remover_livro(lid)
            self._atualizar_lista()

    def _dialog_alugar(self):
        lid = self._selecionado_id()
        if not lid:
            return
        win = tk.Toplevel(self.root)
        win.title("Alugar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Nome da pessoa:", bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=12)
        var = tk.StringVar()
        ttk.Entry(win, textvariable=var, width=25).grid(row=0, column=1, padx=10, pady=12)

        def confirmar():
            pessoa = var.get().strip()
            if not pessoa:
                messagebox.showerror("Erro", "Informe o nome.", parent=win)
                return
            try:
                services.alugar_livro(lid, pessoa)
            except ValueError as e:
                messagebox.showerror("Erro", str(e), parent=win)
                return
            win.destroy()
            self._atualizar_lista()

        ttk.Button(win, text="Confirmar", command=confirmar).grid(row=1, column=1, pady=12, sticky="e", padx=10)

    def _devolver(self):
        lid = self._selecionado_id()
        if lid:
            services.devolver_livro(lid)
            self._atualizar_lista()

    def _buscar(self):
        termo = self.var_busca.get().strip()
        if termo:
            self._atualizar_lista(services.buscar_livros(termo))
        else:
            self._atualizar_lista()
