import tkinter as tk
import tkinter.ttk as ttk
from tkinterdnd2 import TkinterDnD

from controllers.main_controller import MainController



if __name__ == "__main__":
    root = TkinterDnD.Tk() 

    app = MainController(root)

    root.mainloop()