import tkinter as tk
from database import init_db
from gui.app import App
from agendar import main as agendar_notificacao

if __name__ == "__main__":
    init_db()
    try:
        agendar_notificacao()
    except Exception:
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()
