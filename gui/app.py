import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import services
import notifier

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
        self._refresh_list()

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
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background="#313244", foreground=FG, padding=[10, 4], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", BG_LIGHT)], foreground=[("selected", ACCENT)])

    def _build_ui(self):
        ttk.Label(self.root, text="Sistema de Biblioteca", font=("Segoe UI", 16, "bold"), foreground=ACCENT).pack(pady=(15, 5))

        frame_top = ttk.Frame(self.root)
        frame_top.pack(fill="x", padx=15, pady=5)

        ttk.Button(frame_top, text="+ Adicionar", command=self._dialog_add).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Editar", command=self._dialog_edit).pack(side="left", padx=3)
        ttk.Button(frame_top, text="X Remover", command=self._remove).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Alugar", command=self._dialog_loan).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Devolver", command=self._return).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Relatórios", command=self._dialog_reports).pack(side="left", padx=3)
        ttk.Button(frame_top, text="Notificar Atrasos", command=self._notify_overdue).pack(side="left", padx=3)

        ttk.Label(frame_top, text="Categoria:").pack(side="left", padx=(15, 3))
        self.var_category = tk.StringVar(value="Todas")
        self.combo_cat = ttk.Combobox(frame_top, textvariable=self.var_category, width=15, state="readonly")
        self.combo_cat.pack(side="left", padx=3)
        self.combo_cat.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        self._refresh_categories()

        ttk.Label(frame_top, text="Status:").pack(side="left", padx=(10, 3))
        self.var_status = tk.StringVar(value="Todos")
        combo_status = ttk.Combobox(frame_top, textvariable=self.var_status, width=12, state="readonly", values=["Todos", "Disponíveis", "Alugados", "Atrasados"])
        combo_status.pack(side="left", padx=3)
        combo_status.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        self.var_search = tk.StringVar()
        entry = ttk.Entry(frame_top, textvariable=self.var_search, width=18)
        entry.pack(side="right", padx=3)
        entry.bind("<Return>", lambda e: self._search())
        ttk.Button(frame_top, text="Buscar", command=self._search).pack(side="right", padx=3)

        frame_tree = ttk.Frame(self.root)
        frame_tree.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("N", "Título", "Autor", "Categoria", "Ano", "Status")
        self.tree = ttk.Treeview(frame_tree, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("N", width=60, anchor="center")
        self.tree.column("Título", width=250)
        self.tree.column("Autor", width=180)
        self.tree.column("Categoria", width=120)
        self.tree.column("Ano", width=50, anchor="center")
        self.tree.column("Status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._details)

        self.status_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 9), foreground=YELLOW).pack(pady=(0, 10))

    def _refresh_categories(self):
        cats = ["Todas"] + services.list_categories()
        self.combo_cat["values"] = cats

    def _apply_filters(self):
        cat = self.var_category.get()
        status = self.var_status.get()
        books = services.filter_by_category(cat) if cat != "Todas" else services.list_books()
        if status == "Disponíveis":
            books = [b for b in books if b["available"]]
        elif status == "Alugados":
            books = [b for b in books if not b["available"] and not services.is_overdue(b["id"])]
        elif status == "Atrasados":
            books = [b for b in books if not b["available"] and services.is_overdue(b["id"])]
        self._refresh_list(books)

    def _refresh_list(self, books=None):
        self.tree.delete(*self.tree.get_children())
        data = books or services.list_books()
        for b in data:
            if b["available"]:
                status = "Disponível"
                tag = "available"
            elif services.is_overdue(b["id"]):
                status = "Atrasado"
                tag = "overdue"
            else:
                status = "Alugado"
                tag = "loaned"
            self.tree.insert("", "end", iid=str(b["id"]), values=(b["code"] or "", b["title"], b["author"], b["category"] or "", b["year"] or "", status), tags=(tag,))
        self.tree.tag_configure("available", foreground=GREEN)
        self.tree.tag_configure("loaned", foreground=YELLOW)
        self.tree.tag_configure("overdue", foreground=RED)
        total = len(data)
        loaned = sum(1 for b in data if not b["available"])
        overdue = sum(1 for b in data if not b["available"] and services.is_overdue(b["id"]))
        self.status_var.set(f"Total: {total} | Disponíveis: {total - loaned} | Alugados: {loaned - overdue} | Atrasados: {overdue}")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro.")
            return None
        return int(sel[0])

    def _details(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        book_id = int(sel[0])
        book = services.get_book(book_id)
        if not book:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Detalhes - {book['title']}")
        win.geometry("450x350")
        win.configure(bg=BG)
        win.transient(self.root)

        info_frame = tk.Frame(win, bg=BG_LIGHT, padx=15, pady=10)
        info_frame.pack(fill="x", padx=15, pady=10)

        if book["code"]:
            tk.Label(info_frame, text=f"N: {book['code']}", font=("Segoe UI", 9), bg=BG_LIGHT, fg=YELLOW).pack(anchor="w")
        tk.Label(info_frame, text=book["title"], font=("Segoe UI", 13, "bold"), bg=BG_LIGHT, fg=ACCENT).pack(anchor="w")
        tk.Label(info_frame, text=f"Autor: {book['author']}", font=("Segoe UI", 10), bg=BG_LIGHT, fg=FG).pack(anchor="w")
        tk.Label(info_frame, text=f"Categoria: {book['category'] or 'N/A'}  |  Ano: {book['year'] or 'N/A'}", font=("Segoe UI", 10), bg=BG_LIGHT, fg=FG).pack(anchor="w")

        if book["available"]:
            status_color, status_text = GREEN, "Disponível"
        elif services.is_overdue(book_id):
            status_color, status_text = RED, "Atrasado"
        else:
            status_color, status_text = YELLOW, "Alugado"
        tk.Label(info_frame, text=f"Status: {status_text}", font=("Segoe UI", 10, "bold"), bg=BG_LIGHT, fg=status_color).pack(anchor="w", pady=(5, 0))

        tk.Label(win, text="Histórico de Empréstimos", font=("Segoe UI", 11, "bold"), bg=BG, fg=YELLOW).pack(anchor="w", padx=15, pady=(5, 0))

        hist_frame = tk.Frame(win, bg=BG)
        hist_frame.pack(fill="both", expand=True, padx=15, pady=5)

        history = services.loan_history(book_id)
        if not history:
            tk.Label(hist_frame, text="Nenhum empréstimo registrado.", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(pady=10)
        else:
            cols_h = ("Pessoa", "Retirada", "Devolução", "Prazo")
            tree_h = ttk.Treeview(hist_frame, columns=cols_h, show="headings", height=5)
            for c in cols_h:
                tree_h.heading(c, text=c)
            tree_h.column("Pessoa", width=120)
            tree_h.column("Retirada", width=100)
            tree_h.column("Devolução", width=100)
            tree_h.column("Prazo", width=100)
            for h in history:
                ret = services.format_date(h["return_date"]) or "Pendente"
                deadline = services.format_date(h.get("deadline_date")) or "Sem prazo"
                tree_h.insert("", "end", values=(h["person"], services.format_date(h["loan_date"]), ret, deadline))
            tree_h.pack(fill="both", expand=True)

        ttk.Button(win, text="Fechar", command=win.destroy).pack(pady=8)

    def _dialog_add(self):
        win = tk.Toplevel(self.root)
        win.title("Adicionar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        fields = {}
        for i, (label, key) in enumerate([("N", "code"), ("Título*", "title"), ("Autor*", "author"), ("Categoria", "category"), ("Ano", "year")]):
            tk.Label(win, text=label, bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=i, column=0, padx=10, pady=6, sticky="e")
            var = tk.StringVar()
            ttk.Entry(win, textvariable=var, width=30).grid(row=i, column=1, padx=10, pady=6)
            fields[key] = var

        def save():
            t, a = fields["title"].get().strip(), fields["author"].get().strip()
            if not t or not a:
                messagebox.showerror("Erro", "Título e Autor são obrigatórios.", parent=win)
                return
            year = fields["year"].get().strip()
            services.add_book(t, a, fields["category"].get().strip(), int(year) if year.isdigit() else None, fields["code"].get().strip())
            win.destroy()
            self._refresh_categories()
            self._refresh_list()

        ttk.Button(win, text="Salvar", command=save).grid(row=5, column=1, pady=12, sticky="e", padx=10)

    def _dialog_edit(self):
        book_id = self._selected_id()
        if not book_id:
            return
        book = services.get_book(book_id)
        if not book:
            return

        win = tk.Toplevel(self.root)
        win.title("Editar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        fields = {}
        current = [("N", "code", book["code"] or ""), ("Título*", "title", book["title"]), ("Autor*", "author", book["author"]), ("Categoria", "category", book["category"] or ""), ("Ano", "year", str(book["year"]) if book["year"] else "")]
        for i, (label, key, value) in enumerate(current):
            tk.Label(win, text=label, bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=i, column=0, padx=10, pady=6, sticky="e")
            var = tk.StringVar(value=value)
            ttk.Entry(win, textvariable=var, width=30).grid(row=i, column=1, padx=10, pady=6)
            fields[key] = var

        def save():
            t, a = fields["title"].get().strip(), fields["author"].get().strip()
            if not t or not a:
                messagebox.showerror("Erro", "Título e Autor são obrigatórios.", parent=win)
                return
            year = fields["year"].get().strip()
            services.edit_book(book_id, t, a, fields["category"].get().strip(), int(year) if year.isdigit() else None, fields["code"].get().strip())
            win.destroy()
            self._refresh_categories()
            self._refresh_list()

        ttk.Button(win, text="Salvar", command=save).grid(row=5, column=1, pady=12, sticky="e", padx=10)

    def _remove(self):
        book_id = self._selected_id()
        if book_id and messagebox.askyesno("Confirmar", "Remover este livro e todo seu histórico?"):
            services.remove_book(book_id)
            self._refresh_categories()
            self._refresh_list()

    def _dialog_loan(self):
        book_id = self._selected_id()
        if not book_id:
            return
        win = tk.Toplevel(self.root)
        win.title("Alugar Livro")
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Nome da pessoa:", bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        var_person = tk.StringVar()
        ttk.Entry(win, textvariable=var_person, width=25).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(win, text="Data de devolução:", bg=BG, fg=FG, font=("Segoe UI", 10)).grid(row=1, column=0, padx=10, pady=6, sticky="e")
        var_deadline = tk.StringVar()
        ttk.Entry(win, textvariable=var_deadline, width=12).grid(row=1, column=1, padx=10, pady=6, sticky="w")
        tk.Label(win, text="dd/mm/aaaa (opcional)", bg=BG, fg="#6c7086", font=("Segoe UI", 9)).grid(row=1, column=1, padx=(110, 0), pady=6, sticky="w")

        def confirm():
            person = var_person.get().strip()
            if not person:
                messagebox.showerror("Erro", "Informe o nome.", parent=win)
                return
            deadline_str = var_deadline.get().strip()
            deadline_iso = None
            if deadline_str:
                try:
                    deadline_iso = services.parse_date_br(deadline_str)
                except ValueError as e:
                    messagebox.showerror("Erro", str(e), parent=win)
                    return
            try:
                services.loan_book(book_id, person, deadline_iso)
            except ValueError as e:
                messagebox.showerror("Erro", str(e), parent=win)
                return
            win.destroy()
            self._refresh_list()

        ttk.Button(win, text="Confirmar", command=confirm).grid(row=2, column=1, pady=12, sticky="e", padx=10)

    def _return(self):
        book_id = self._selected_id()
        if book_id:
            services.return_book(book_id)
            self._refresh_list()

    def _dialog_reports(self):
        win = tk.Toplevel(self.root)
        win.title("Relatorios")
        win.geometry("500x450")
        win.configure(bg=BG)
        win.transient(self.root)

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        frame_books = tk.Frame(notebook, bg=BG_LIGHT)
        notebook.add(frame_books, text="Livros mais alugados")
        cols_b = ("Título", "Autor", "Empréstimos")
        tree_b = ttk.Treeview(frame_books, columns=cols_b, show="headings", height=12)
        for c in cols_b:
            tree_b.heading(c, text=c)
        tree_b.column("Título", width=200)
        tree_b.column("Autor", width=150)
        tree_b.column("Empréstimos", width=80, anchor="center")
        for r in services.top_loaned_books():
            tree_b.insert("", "end", values=(r["title"], r["author"], r["total"]))
        tree_b.pack(fill="both", expand=True)

        frame_people = tk.Frame(notebook, bg=BG_LIGHT)
        notebook.add(frame_people, text="Alunos que mais alugaram")
        cols_p = ("Pessoa", "Empréstimos")
        tree_p = ttk.Treeview(frame_people, columns=cols_p, show="headings", height=12)
        for c in cols_p:
            tree_p.heading(c, text=c)
        tree_p.column("Pessoa", width=250)
        tree_p.column("Empréstimos", width=100, anchor="center")
        for r in services.top_borrowers():
            tree_p.insert("", "end", values=(r["person"], r["total"]))
        tree_p.pack(fill="both", expand=True)

        ttk.Button(win, text="Exportar PDF", command=self._export_report_pdf).pack(pady=8)
        ttk.Button(win, text="Fechar", command=win.destroy).pack(pady=(0, 8))

    def _notify_overdue(self):
        try:
            result = notifier.send_overdue_notification()
            messagebox.showinfo("Notificação", result)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar e-mail:\n{e}")

    def _export_report_pdf(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import date

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="relatorio_biblioteca.pdf")
        if not path:
            return

        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Relatório da Biblioteca - SECRI", styles["Title"]))
        elements.append(Paragraph(f"Gerado em: {date.today().strftime('%d/%m/%Y')}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("Livros Mais Alugados", styles["Heading2"]))
        data_books = [["Título", "Autor", "Empréstimos"]]
        for r in services.top_loaned_books():
            data_books.append([r["title"], r["author"], str(r["total"])])
        t = Table(data_books, colWidths=[250, 170, 80])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#313244")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("Alunos Que Mais Alugaram", styles["Heading2"]))
        data_people = [["Pessoa", "Empréstimos"]]
        for r in services.top_borrowers():
            data_people.append([r["person"], str(r["total"])])
        t2 = Table(data_people, colWidths=[300, 100])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#313244")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
        ]))
        elements.append(t2)

        doc.build(elements)
        messagebox.showinfo("Sucesso", f"PDF salvo em:\n{path}")

    def _search(self):
        term = self.var_search.get().strip()
        self.var_category.set("Todas")
        self.var_status.set("Todos")
        if term:
            self._refresh_list(services.search_books(term))
        else:
            self._refresh_list()
