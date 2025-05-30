import tkinter as tk
import tkinter.ttk as ttk

from controllers.main_controller import MainController



if __name__ == "__main__":
    root = tk.Tk() 

    app = MainController(root)

    root.mainloop()