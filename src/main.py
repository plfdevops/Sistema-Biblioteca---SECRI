import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from gui.app import setup_pages
from nicegui import ui

init_db()
setup_pages()
ui.run(host="0.0.0.0", port=8080, title="Biblioteca SECRI", dark=True, reload=False)
