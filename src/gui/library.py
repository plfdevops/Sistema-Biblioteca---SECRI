from nicegui import ui
from datetime import datetime
import services
import notifier
from gui.dialogs import (dialog_add, dialog_edit, dialog_remove,
                         dialog_loan, dialog_return, dialog_renew, dialog_reports)

ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"


class LibraryPage:
    def __init__(self):
        self.selected_id = None

    def build(self):
        ui.query("body").style("background-color: #1e1e2e")
        with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-4"):
            with ui.row().classes("w-full items-center"):
                ui.label("Biblioteca SECRI").classes("text-2xl font-bold").style(f"color: {ACCENT}")
                ui.space()
                ui.button("Alunos", on_click=lambda: ui.navigate.to("/alunos")).props("flat")

            stats = services.dashboard_stats()
            with ui.row().classes("w-full gap-4"):
                self._card("📖 Total", str(stats["total"]), ACCENT)
                self._card("✅ Disponíveis", str(stats["available"]), GREEN)
                self._card("📤 Alugados", str(stats["loaned"]), YELLOW)
                self._card("⚠️ Atrasados", str(stats["overdue"]), RED)
                self._card("🔄 Devoluções/mês", str(stats["returns_month"]), ACCENT)

            with ui.card().classes("w-full").style("background-color: #2a2a3e"):
                with ui.row().classes("w-full items-center gap-2 flex-wrap"):
                    ui.button("+ Adicionar", on_click=self._add).props("color=primary")
                    ui.button("Editar", on_click=self._edit).props("color=primary flat")
                    ui.button("Remover", on_click=self._remove).props("color=negative flat")
                    ui.separator().props("vertical").classes("h-8")
                    ui.button("Alugar", on_click=self._loan).props("color=purple")
                    ui.button("Devolver", on_click=self._return).props("color=positive")
                    ui.button("Renovar", on_click=self._renew).props("color=amber")
                    ui.separator().props("vertical").classes("h-8")
                    ui.button("Relatórios", on_click=self._reports).props("flat")
                    ui.button("Notificar Gestor", on_click=self._notify_manager).props("flat color=warning")
                    ui.space()
                    self.search_input = ui.input(placeholder="Buscar...").props("dense outlined clearable").classes("w-48")
                    self.search_input.on("keydown.enter", self._search)
                    self.search_input.on("clear", lambda: self._refresh())
                    ui.button(icon="search", on_click=self._search).props("flat dense")
                    ui.button(icon="refresh", on_click=lambda: self._refresh()).props("flat dense")

            with ui.row().classes("w-full items-center gap-4"):
                cats = ["Todas"] + services.list_categories()
                self.filter_cat = ui.select(cats, value="Todas", label="Categoria",
                                            on_change=self._apply_filters).classes("w-48")
                self.filter_status = ui.select(["Todos", "Disponíveis", "Alugados", "Atrasados"],
                                              value="Todos", label="Status",
                                              on_change=self._apply_filters).classes("w-40")
                ui.space()
                self.label_results = ui.label("").classes("text-sm").style("color: #6c7086")

            columns = [
                {"name": "code", "label": "Nº", "field": "code", "align": "center", "sortable": True},
                {"name": "title", "label": "Título", "field": "title", "align": "left", "sortable": True},
                {"name": "author", "label": "Autor", "field": "author", "align": "left", "sortable": True},
                {"name": "category", "label": "Categoria", "field": "category", "align": "left", "sortable": True},
                {"name": "person", "label": "Aluno", "field": "person", "align": "left", "sortable": True},
                {"name": "email", "label": "E-mail", "field": "email", "align": "left", "sortable": True},
                {"name": "status", "label": "Status", "field": "status", "align": "center", "sortable": True},
            ]
            self.table = ui.table(columns=columns, rows=[], row_key="id",
                                  pagination={"rowsPerPage": 20}).classes("w-full").style("background-color: #2a2a3e; color: #cdd6f4")
            self.table.on("rowClick", self._on_row_click)
            self.table.add_slot("body-cell-status", """
                <q-td :props="props">
                    <q-badge :color="props.row.status === 'Atrasado' ? 'red' : props.row.status === 'Alugado' ? 'amber' : 'green'"
                             :label="props.row.status" />
                </q-td>
            """)
            ui.add_css("""
                .selected-row { background-color: #89b4fa !important; color: #1e1e2e !important; }
                .selected-row td { color: #1e1e2e !important; }
                .q-table tbody tr { cursor: pointer; }
                .q-table tbody tr:hover { background-color: #313244 !important; }
            """)

            with ui.card().classes("w-full").style("background-color: #2a2a3e"):
                self.label_event = ui.label("").classes("text-sm").style(f"color: {GREEN}")

        self._refresh()
        ui.timer(3600, self._check_overdue)


    def _card(self, title, value, color):
        with ui.card().classes("flex-1 min-w-[140px]").style("background-color: #2a2a3e"):
            ui.label(title).classes("text-xs").style("color: #6c7086")
            ui.label(value).classes("text-2xl font-bold").style(f"color: {color}")

    def _on_row_click(self, e):
        try:
            row = e.args[1] if isinstance(e.args, list) else e.args
            self.selected_id = row.get("id") if isinstance(row, dict) else None
        except (IndexError, KeyError, TypeError):
            self.selected_id = None
        ui.run_javascript(f'''
            document.querySelectorAll(".q-table tbody tr").forEach(r => r.classList.remove("selected-row"));
            const rows = document.querySelectorAll(".q-table tbody tr");
            const idx = {e.args[2] if isinstance(e.args, list) and len(e.args) > 2 else -1};
            if (idx >= 0 && rows[idx]) rows[idx].classList.add("selected-row");
        ''')

    def _get_selected(self):
        if not self.selected_id:
            ui.notify("Selecione um livro (clique na linha).", type="warning")
            return None
        return self.selected_id

    def _set_event(self, msg):
        self.label_event.text = f"{msg}  ({datetime.now().strftime('%H:%M')})"

    def _on_done(self, msg):
        self._refresh()
        self._set_event(msg)

    def _refresh(self, books=None):
        data = books or services.list_books()
        rows = []
        for b in data:
            person = email = ""
            if not b["available"]:
                loan = services.active_loan(b["id"])
                person = (loan or {}).get("person") or ""
                email = (loan or {}).get("email") or ""
            status = "Disponível" if b["available"] else ("Atrasado" if services.is_overdue(b["id"]) else "Alugado")
            rows.append({"id": b["id"], "code": b["code"] or "", "title": b["title"],
                         "author": b["author"], "category": b["category"] or "",
                         "person": person, "email": email, "status": status})
        self.table.rows = rows
        self.table.update()
        self.label_results.text = f"{len(data)} livros"

    def _apply_filters(self, _=None):
        cat = self.filter_cat.value
        status = self.filter_status.value
        books = services.filter_by_category(cat) if cat != "Todas" else services.list_books()
        if status == "Disponíveis":
            books = [b for b in books if b["available"]]
        elif status == "Alugados":
            books = [b for b in books if not b["available"] and not services.is_overdue(b["id"])]
        elif status == "Atrasados":
            books = [b for b in books if not b["available"] and services.is_overdue(b["id"])]
        self._refresh(books)

    def _search(self, _=None):
        term = self.search_input.value.strip() if self.search_input.value else ""
        self.filter_cat.value = "Todas"
        self.filter_status.value = "Todos"
        self._refresh(services.search_books(term)) if term else self._refresh()


    def _add(self):
        dialog_add(self._on_done)

    def _edit(self):
        book_id = self._get_selected()
        if book_id:
            dialog_edit(book_id, self._on_done)

    def _remove(self):
        book_id = self._get_selected()
        if book_id:
            dialog_remove(book_id, lambda msg: (setattr(self, 'selected_id', None), self._on_done(msg)))

    def _loan(self):
        book_id = self._get_selected()
        if book_id:
            dialog_loan(book_id, self._on_done)

    def _return(self):
        book_id = self._get_selected()
        if book_id:
            dialog_return(book_id, self._on_done)

    def _renew(self):
        book_id = self._get_selected()
        if book_id:
            dialog_renew(book_id, self._on_done)

    def _reports(self):
        dialog_reports(self._set_event)

    def _notify_manager(self):
        try:
            result = notifier.send_manager_notification()
            self._set_event(result)
            ui.notify(result, type="positive")
        except Exception as e:
            ui.notify(f"Falha: {e}", type="negative")

    def _check_overdue(self):
        try:
            sent = notifier.send_student_notifications()
            if sent:
                self._set_event(f"{sent} aluno(s) notificado(s)")
        except Exception:
            pass
