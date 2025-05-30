import tkinter as tk
import tkinter.ttk as ttk

class MainView:
    """
    MainView 类：管理主窗口和 Notebook 结构
    """
    def __init__(self, root):
        """
        初始化主视图

        Args:
            root: Tkinter 根窗口
        """
        self.root = root
        self.root.title("Comfyui Tools")
        self.root.geometry("700x400")

        # 创建 Notebook (Tab 控件)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

    def add_tab(self, frame, text):
        """
        向 Notebook 添加一个 Tab

        Args:
            frame: 要添加到 Tab 中的 Tkinter Frame (通常是一个 TabView 实例)
            text: Tab 的标题文本
        """
        self.notebook.add(frame, text=text)