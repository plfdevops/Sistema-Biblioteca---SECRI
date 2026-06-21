from nicegui import ui
from gui.library import LibraryPage
from gui.students import StudentsPage

QUASAR_PT = """<script>
document.addEventListener('DOMContentLoaded', () => {
    if (window.Quasar) {
        window.Quasar.lang.set({table:{noData:'Sem dados',noResults:'Nenhum resultado',
            pagination:(s,e,t)=>s+'-'+e+' de '+t,recordsPerPage:'Registros por página:'}})
    }
})
</script>"""


def setup_pages():
    @ui.page("/")
    def main_page():
        ui.add_head_html(QUASAR_PT)
        LibraryPage().build()

    @ui.page("/alunos")
    def students_page():
        ui.add_head_html(QUASAR_PT)
        StudentsPage().build()
