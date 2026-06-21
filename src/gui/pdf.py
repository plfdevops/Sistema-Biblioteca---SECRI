from nicegui import ui
from datetime import date
import services


def export_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import tempfile
    import os

    path = os.path.join(tempfile.gettempdir(), "relatorio_biblioteca.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Sec", parent=styles["Heading2"],
                              textColor=colors.HexColor("#1e1e2e"), spaceAfter=10))
    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8, leading=10)
    def P(t): return Paragraph(str(t), cell_style)

    ts = TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#313244")),
                     ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                     ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                     ("FONTSIZE", (0, 0), (-1, 0), 9), ("FONTSIZE", (0, 1), (-1, -1), 8),
                     ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                     ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                     ("VALIGN", (0, 0), (-1, -1), "TOP"),
                     ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)])

    elements = [Paragraph("Relatório da Biblioteca SECRI", styles["Title"]),
                Paragraph(f"Gerado em: {date.today().strftime('%d/%m/%Y')}", styles["Normal"]),
                Spacer(1, 20)]

    overdue = services.overdue_loans()
    if overdue:
        data = [["Livro", "Aluno", "E-mail", "Prazo"]]
        for r in overdue:
            data.append([P(r["title"]), P(r["person"]), P(r.get("email") or "—"),
                         services.format_date(r["deadline_date"])])
        t = Table(data, colWidths=[170, 100, 160, 65])
        t.setStyle(ts)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f38ba8"))]))
        elements.append(KeepTogether([Paragraph("Livros Atrasados", styles["Sec"]), t]))
    else:
        elements.append(Paragraph("Nenhum atraso no momento.", styles["Normal"]))
    elements.append(Spacer(1, 20))

    data = [["Título", "Autor", "Qtd"]]
    for r in services.top_loaned_books():
        data.append([P(r["title"]), P(r["author"]), str(r["total"])])
    t = Table(data, colWidths=[210, 180, 50])
    t.setStyle(ts)
    elements.append(KeepTogether([Paragraph("Livros Mais Alugados", styles["Sec"]), t]))
    elements.append(Spacer(1, 20))

    data = [["Aluno", "Qtd"]]
    for r in services.top_borrowers():
        data.append([P(r["person"]), str(r["total"])])
    t = Table(data, colWidths=[380, 50])
    t.setStyle(ts)
    elements.append(KeepTogether([Paragraph("Alunos Que Mais Alugaram", styles["Sec"]), t]))

    doc.build(elements)
    ui.download(path)
