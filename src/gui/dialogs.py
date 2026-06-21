from nicegui import ui
import services
from gui.pdf import export_pdf

ACCENT = "#89b4fa"


def dialog_add(on_done):
    with ui.dialog() as dlg, ui.card().style("width: 400px"):
        ui.label("Adicionar Livro").classes("text-lg font-bold").style(f"color: {ACCENT}")
        code = ui.input("Nº")
        title = ui.input("Título *")
        author = ui.input("Autor *")
        category = ui.input("Categoria")
        year = ui.input("Ano")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancelar", on_click=dlg.close).props("flat")
            def save():
                if not title.value.strip() or not author.value.strip():
                    ui.notify("Título e Autor obrigatórios", type="negative")
                    return
                y = int(year.value) if year.value.strip().isdigit() else None
                services.add_book(title.value.strip(), author.value.strip(),
                                  category.value.strip(), y, code.value.strip())
                dlg.close()
                on_done("Livro adicionado")
            ui.button("Salvar", on_click=save).props("color=primary")
    dlg.open()


def dialog_edit(book_id, on_done):
    book = services.get_book(book_id)
    if not book:
        return
    with ui.dialog() as dlg, ui.card().style("width: 400px"):
        ui.label("Editar Livro").classes("text-lg font-bold").style(f"color: {ACCENT}")
        code = ui.input("Nº", value=book["code"] or "")
        title = ui.input("Título *", value=book["title"])
        author = ui.input("Autor *", value=book["author"])
        category = ui.input("Categoria", value=book["category"] or "")
        year = ui.input("Ano", value=str(book["year"]) if book["year"] else "")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancelar", on_click=dlg.close).props("flat")
            def save():
                if not title.value.strip() or not author.value.strip():
                    ui.notify("Título e Autor obrigatórios", type="negative")
                    return
                y = int(year.value) if year.value.strip().isdigit() else None
                services.edit_book(book_id, title.value.strip(), author.value.strip(),
                                   category.value.strip(), y, code.value.strip())
                dlg.close()
                on_done("Livro editado")
            ui.button("Salvar", on_click=save).props("color=primary")
    dlg.open()


def dialog_remove(book_id, on_done):
    with ui.dialog() as dlg, ui.card():
        ui.label("Remover este livro e todo seu histórico?")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancelar", on_click=dlg.close).props("flat")
            def confirm():
                services.remove_book(book_id)
                dlg.close()
                on_done("Livro removido")
            ui.button("Remover", on_click=confirm).props("color=negative")
    dlg.open()


def dialog_loan(book_id, on_done):
    students = services.list_students()
    student_names = [s["name"] for s in students]
    student_map = {s["name"]: s.get("email") or "" for s in students}

    with ui.dialog() as dlg, ui.card().style("width: 440px"):
        ui.label("Alugar Livro").classes("text-lg font-bold").style(f"color: {ACCENT}")
        person = ui.input("Nome *", autocomplete=student_names)
        email = ui.input("E-mail").props("type=email")
        def fill_email():
            if person.value in student_map and student_map[person.value]:
                email.value = student_map[person.value]
        person.on("blur", fill_email)
        deadline = ui.input("Devolução").props('mask="##/##/####"')
        ui.label("dd/mm/aaaa").classes("text-xs").style("color: #6c7086")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancelar", on_click=dlg.close).props("flat")
            def confirm():
                if not person.value.strip():
                    ui.notify("Informe o nome", type="negative")
                    return
                deadline_iso = None
                if deadline.value.strip():
                    try:
                        deadline_iso = services.parse_date_br(deadline.value.strip(), must_be_future=True)
                    except ValueError as e:
                        ui.notify(str(e), type="negative")
                        return
                em = email.value.strip() or None
                if em and not services.validate_email(em):
                    ui.notify("E-mail inválido", type="negative")
                    return
                try:
                    services.loan_book(book_id, person.value.strip(), deadline_iso, em)
                except ValueError as e:
                    ui.notify(str(e), type="negative")
                    return
                dlg.close()
                on_done(f"Emprestado para {person.value.strip()}")
            ui.button("Confirmar", on_click=confirm).props("color=purple")
    dlg.open()


def dialog_return(book_id, on_done):
    loan = services.active_loan(book_id)
    if not loan:
        ui.notify("Livro não está emprestado", type="warning")
        return
    with ui.dialog() as dlg, ui.card():
        ui.label(f"Confirmar devolução de \"{services.get_book(book_id)['title']}\"?")
        ui.label(f"Aluno: {loan['person']}").classes("text-sm")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancelar", on_click=dlg.close).props("flat")
            def confirm():
                services.return_book(book_id)
                dlg.close()
                on_done("Livro devolvido")
            ui.button("Devolver", on_click=confirm).props("color=positive")
    dlg.open()


def dialog_renew(book_id, on_done):
    loan = services.active_loan(book_id)
    if not loan:
        ui.notify("Este livro não está emprestado", type="warning")
        return
    with ui.dialog() as dlg, ui.card().style("width: 380px"):
        ui.label("Renovar Empréstimo").classes("text-lg font-bold").style(f"color: {ACCENT}")
        ui.label(f"Aluno: {loan['person']}")
        ui.label(f"Prazo atual: {services.format_date(loan.get('deadline_date')) or 'Sem prazo'}")
        new_deadline = ui.input("Novo prazo").props('mask="##/##/####"')
        ui.label("dd/mm/aaaa").classes("text-xs").style("color: #6c7086")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancelar", on_click=dlg.close).props("flat")
            def confirm():
                if not new_deadline.value.strip():
                    ui.notify("Informe a nova data", type="negative")
                    return
                try:
                    iso = services.parse_date_br(new_deadline.value.strip(), must_be_future=True)
                    services.renew_loan(book_id, iso)
                except ValueError as e:
                    ui.notify(str(e), type="negative")
                    return
                dlg.close()
                on_done("Empréstimo renovado")
            ui.button("Renovar", on_click=confirm).props("color=amber")
    dlg.open()


def dialog_reports(on_event):
    with ui.dialog() as dlg, ui.card().style("width: 560px; max-height: 80vh"):
        ui.label("Relatórios").classes("text-lg font-bold").style(f"color: {ACCENT}")
        with ui.tabs().classes("w-full") as tabs:
            tab_b = ui.tab("Top Livros")
            tab_p = ui.tab("Top Alunos")
        with ui.tab_panels(tabs).classes("w-full"):
            with ui.tab_panel(tab_b):
                cols = [{"name": "title", "label": "Título", "field": "title", "align": "left"},
                        {"name": "author", "label": "Autor", "field": "author", "align": "left"},
                        {"name": "total", "label": "Qtd", "field": "total", "align": "center", "sortable": True}]
                rows = [{"title": r["title"], "author": r["author"], "total": r["total"]} for r in services.top_loaned_books()]
                ui.table(columns=cols, rows=rows).classes("w-full")
            with ui.tab_panel(tab_p):
                cols = [{"name": "person", "label": "Aluno", "field": "person", "align": "left"},
                        {"name": "total", "label": "Qtd", "field": "total", "align": "center", "sortable": True}]
                rows = [{"person": r["person"], "total": r["total"]} for r in services.top_borrowers()]
                ui.table(columns=cols, rows=rows).classes("w-full")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Exportar PDF", on_click=lambda: (export_pdf(), on_event("PDF exportado"))).props("flat")
            ui.button("Fechar", on_click=dlg.close).props("flat")
    dlg.open()
