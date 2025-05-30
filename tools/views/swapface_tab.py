import tkinter as tk
import tkinter.ttk as ttk


class SwapfaceTab(ttk.Frame):
    """
    换脸Tab界面，包含参数输入、进度显示、消息显示、开始按钮
    """
    def __init__(self, parent):
        """
        初始化 Tab 1 的视图

        Args:
            parent: Tkinter 父容器 (通常是 Notebook)
        """
        super().__init__(parent, padding="10")
        self.parent = parent

        # 参数输入区
        self.char_var = tk.StringVar()
        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.repaint_hair_var = tk.BooleanVar(value=True)

        row = 0
        ttk.Label(self, text="人脸LoRA名(char)").grid(row=row, column=0, sticky='w')
        ttk.Entry(self, textvariable=self.char_var, width=30).grid(row=row, column=1, sticky='ew')
        row += 1
        ttk.Label(self, text="输入文件夹").grid(row=row, column=0, sticky='w')
        ttk.Entry(self, textvariable=self.input_path_var, width=30).grid(row=row, column=1, sticky='ew')
        row += 1
        ttk.Label(self, text="输出文件夹").grid(row=row, column=0, sticky='w')
        ttk.Entry(self, textvariable=self.output_path_var, width=30).grid(row=row, column=1, sticky='ew')
        row += 1
        ttk.Checkbutton(self, text="重绘头发(repaint_hair)", variable=self.repaint_hair_var).grid(row=row, column=0, columnspan=2, sticky='w')
        row += 1

        # 进度条
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # 消息显示
        self.message_var = tk.StringVar(value="等待任务...")
        self.message_label = ttk.Label(self, textvariable=self.message_var, wraplength=300)
        self.message_label.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        # 开始按钮
        self.start_button = ttk.Button(self, text="开始批量换脸")
        self.start_button.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        self.columnconfigure(1, weight=1)

    def get_params(self):
        """获取界面参数"""
        return {
            'char': self.char_var.get(),
            'input_path': self.input_path_var.get(),
            'output_path': self.output_path_var.get(),
            'repaint_hair': self.repaint_hair_var.get()
        }

    def set_progress(self, value):
        self.progress_var.set(value)

    def update_message(self, message):
        """
        由 Tab1Controller 调用，用于更新消息显示
        """
        print(f"Swapface: '{message}'") # 打印日志
        self.message_var.set(message)

    def get_start_button(self):
        return self.start_button