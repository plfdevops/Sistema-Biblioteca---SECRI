import tkinter as tk
from database import init_db
from gui.app import App

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    App(root)
    root.mainloop()
