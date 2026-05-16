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
ORANGE = "#fab387"


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
        style.configure("TCombobox", fieldbackground=BG_LIGHT, foreground=FG)
        style.configure("Treeview", background=BG_LIGHT, foreground=FG, fieldbackground=BG_LIGHT, rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#313244", foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#45475a")])

    def _build_ui(self):
        # Titulo
        ttk.Label(self.root, text="Sistema de Biblioteca", font=("Segoe UI", 16, "bold"), foreground=ACCENT).pack(pady=(15, 5))

        # Frame de acoes
        frame_top = ttk.Frame(self.root)
        frame_top.pack(fill="x", padx=15, pady=5)

        ttk.Button(frame_top, text="+ Adicionar", command=self._dialog_adicionar).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Editar", command=self._dialog_editar).pack(side="left", padx=3)
        ttk.Button(frame_top, text="X Remover", command=self._remover).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Alugar", command=self._dialog_alugar).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Devolver", command=self._devolver).pack(side="left", padx=3)

        # Filtro por categoria
        ttk.Label(frame_top, text="Categoria:").pack(side="left", padx=(15, 3))
        self.var_categoria = tk.StringVar(value="Todas")
        self.combo_cat = ttk.Combobox(frame_top, textvariable=self.var_categoria, width=15, state="readonly")
        self.combo_cat.pack(side="left", padx=3)
        self.combo_cat.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())
        self._atualizar_categorias()

        # Filtro por status
        ttk.Label(frame_top, text="Status:").pack(side="left", padx=(10, 3))
        self.var_status = tk.StringVar(value="Todos")
        combo_status = ttk.Combobox(frame_top, textvariable=self.var_status, width=12, state="readonly", values=["Todos", "Disponiveis", "Alugados", "Pendentes"])
        combo_status.pack(side="left", padx=3)
        combo_status.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Busca
        self.var_busca = tk.StringVar()
        entry = ttk.Entry(frame_top, textvariable=self.var_busca, width=18)
        entry.pack(side="right", padx=3)
        entry.bind("<Return>", lambda e: self._buscar())
        ttk.Button(frame_top, text="Buscar", command=self._buscar).pack(side="right", padx=3)

        # Tabela
        frame_tree = ttk.Frame(self.root)
        frame_tree.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("ID", "Titulo", "Autor", "Categoria", "Ano", "Status")
        self.tree = ttk.Treeview(frame_tree, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Titulo", width=250)
        self.tree.column("Autor", width=180)
        self.tree.column("Categoria", width=120)
        self.tree.column("Ano", width=50, anchor="center")
        self.tree.column("Status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Duplo clique para detalhes
        self.tree.bind("<Double-1>", self._detalhes_livro)

        # Barra de status
        self.status_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 9), foreground=YELLOW).pack(pady=(0, 10))

    def _atualizar_categorias(self):
        cats = ["Todas"] + services.listar_categorias()
        self.combo_cat["values"] = cats

    def _filtrar_categoria(self):
        self._aplicar_filtros()

    def _aplicar_filtros(self):
        cat = self.var_categoria.get()
        status = self.var_status.get()
        if cat == "Todas":
            livros = services.listar_livros()
        else:
            livros = services.filtrar_por_categoria(cat)
        if status == "Disponiveis":
            livros = [l for l in livros if l["disponivel"]]
        elif status == "Alugados":
            livros = [l for l in livros if not l["disponivel"] and not services.esta_atrasado(l["id"])]
        elif status == "Pendentes":
            livros = [l for l in livros if not l["disponivel"] and services.esta_atrasado(l["id"])]
        self._atualizar_lista(livros)

    def _atualizar_lista(self, livros=None):
        self.tree.delete(*self.tree.get_children())
        dados = livros or services.listar_livros()
        for l in dados:
            if l["disponivel"]:
                status = "Disponivel"
                tag = "disponivel"
            elif services.esta_atrasado(l["id"]):
                status = "Pendente"
                tag = "pendente"
            else:
                status = "Alugado"
                tag = "alugado"
            self.tree.insert("", "end", values=(l["id"], l["titulo"], l["autor"], l["categoria"] or "", l["ano"] or "", status), tags=(tag,))
        self.tree.tag_configure("disponivel", foreground=GREEN)
        self.tree.tag_configure("alugado", foreground=RED)
        self.tree.tag_configure("pendente", foreground=ORANGE)
        total = len(dados)
        alugados = sum(1 for l in dados if not l["disponivel"])
        pendentes = sum(1 for l in dados if not l["disponivel"] and services.esta_atrasado(l["id"]))
        self.status_var.set(f"Total: {total} | Disponiveis: {total - alugados} | Alugados: {alugados - pendentes} | Pendentes: {pendentes}")

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

        status_str = str(valores[5])
        if status_str == "Disponivel":
            status_color = GREEN
        elif status_str == "Pendente":
            status_color = ORANGE
        else:
            status_color = RED
        tk.Label(info_frame, text=f"Status: {status_str}", font=("Segoe UI", 10, "bold"), bg=BG_LIGHT, fg=status_color).pack(anchor="w", pady=(5, 0))

        # Historico de emprestimos
        tk.Label(win, text="Historico de Emprestimos", font=("Segoe UI", 11, "bold"), bg=BG, fg=YELLOW).pack(anchor="w", padx=15, pady=(5, 0))

        hist_frame = tk.Frame(win, bg=BG)
        hist_frame.pack(fill="both", expand=True, padx=15, pady=5)

        historico = services.historico_emprestimos(livro_id)
        if not historico:
            tk.Label(hist_frame, text="Nenhum emprestimo registrado.", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(pady=10)
        else:
            cols_h = ("Pessoa", "Retirada", "Devolucao", "Prazo")
            tree_h = ttk.Treeview(hist_frame, columns=cols_h, show="headings", height=5)
            for c in cols_h:
                tree_h.heading(c, text=c)
            tree_h.column("Pessoa", width=120)
            tree_h.column("Retirada", width=100)
            tree_h.column("Devolucao", width=100)
            tree_h.column("Prazo", width=70)
            for h in historico:
                dev = h["data_devolucao"] or "Pendente"
                prazo = f"{h['prazo_dias']} dias" if h.get("prazo_dias") else "Sem prazo"
                tree_h.insert("", "end", values=(h["pessoa"], h["data_retirada"], dev, prazo))
            tree_h.pack(fill="both", expand=True)

        ttk.Button(win, text="Fechar", command=win.destroy).pack(pady=8)

    def _dialog_adicionar(self):
        win = tk.Toplevel(self.root)
        win.title("Adicionar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        campos = {}
        for i, (label, key) in enumerate([("Titulo*", "titulo"), ("Autor*", "autor"), ("Categoria", "categoria"), ("Ano", "ano")]):
            tk.Label(win, text=label, bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=i, column=0, padx=10, pady=6, sticky="e")
            var = tk.StringVar()
            ttk.Entry(win, textvariable=var, width=30).grid(row=i, column=1, padx=10, pady=6)
            campos[key] = var

        def salvar():
            t, a = campos["titulo"].get().strip(), campos["autor"].get().strip()
            if not t or not a:
                messagebox.showerror("Erro", "Titulo e Autor sao obrigatorios.", parent=win)
                return
            ano = campos["ano"].get().strip()
            services.adicionar_livro(t, a, campos["categoria"].get().strip(), int(ano) if ano.isdigit() else None)
            win.destroy()
            self._atualizar_categorias()
            self._atualizar_lista()

        ttk.Button(win, text="Salvar", command=salvar).grid(row=4, column=1, pady=12, sticky="e", padx=10)

    def _remover(self):
        lid = self._selecionado_id()
        if lid and messagebox.askyesno("Confirmar", "Remover este livro e todo seu historico?"):
            services.remover_livro(lid)
            self._atualizar_categorias()
            self._atualizar_lista()

    def _dialog_editar(self):
        lid = self._selecionado_id()
        if not lid:
            return
        livro = services.obter_livro(lid)
        if not livro:
            return

        win = tk.Toplevel(self.root)
        win.title("Editar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        campos = {}
        valores_atuais = [("Titulo*", "titulo", livro["titulo"]), ("Autor*", "autor", livro["autor"]), ("Categoria", "categoria", livro["categoria"] or ""), ("Ano", "ano", str(livro["ano"]) if livro["ano"] else "")]
        for i, (label, key, valor) in enumerate(valores_atuais):
            tk.Label(win, text=label, bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=i, column=0, padx=10, pady=6, sticky="e")
            var = tk.StringVar(value=valor)
            ttk.Entry(win, textvariable=var, width=30).grid(row=i, column=1, padx=10, pady=6)
            campos[key] = var

        def salvar():
            t, a = campos["titulo"].get().strip(), campos["autor"].get().strip()
            if not t or not a:
                messagebox.showerror("Erro", "Titulo e Autor sao obrigatorios.", parent=win)
                return
            ano = campos["ano"].get().strip()
            services.editar_livro(lid, t, a, campos["categoria"].get().strip(), int(ano) if ano.isdigit() else None)
            win.destroy()
            self._atualizar_categorias()
            self._atualizar_lista()

        ttk.Button(win, text="Salvar", command=salvar).grid(row=4, column=1, pady=12, sticky="e", padx=10)

    def _dialog_alugar(self):
        lid = self._selecionado_id()
        if not lid:
            return
        win = tk.Toplevel(self.root)
        win.title("Alugar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Nome da pessoa:", bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        var_pessoa = tk.StringVar()
        ttk.Entry(win, textvariable=var_pessoa, width=25).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(win, text="Prazo (dias):", bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=1, column=0, padx=10, pady=6, sticky="e")
        var_prazo = tk.StringVar()
        ttk.Entry(win, textvariable=var_prazo, width=10).grid(row=1, column=1, padx=10, pady=6, sticky="w")
        tk.Label(win, text="(opcional)", bg=BG, fg="#6c7086", font=("Segoe UI", 9)).grid(row=1, column=1, padx=(100, 0), pady=6, sticky="w")

        def confirmar():
            pessoa = var_pessoa.get().strip()
            if not pessoa:
                messagebox.showerror("Erro", "Informe o nome.", parent=win)
                return
            prazo_str = var_prazo.get().strip()
            prazo = int(prazo_str) if prazo_str.isdigit() else None
            try:
                services.alugar_livro(lid, pessoa, prazo)
            except ValueError as e:
                messagebox.showerror("Erro", str(e), parent=win)
                return
            win.destroy()
            self._atualizar_lista()

        ttk.Button(win, text="Confirmar", command=confirmar).grid(row=2, column=1, pady=12, sticky="e", padx=10)

    def _devolver(self):
        lid = self._selecionado_id()
        if lid:
            services.devolver_livro(lid)
            self._atualizar_lista()

    def _buscar(self):
        termo = self.var_busca.get().strip()
        self.var_categoria.set("Todas")
        if termo:
            self._atualizar_lista(services.buscar_livros(termo))
        else:
            self._atualizar_lista()
