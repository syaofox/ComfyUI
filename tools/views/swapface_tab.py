import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext


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
        self.copy_on_error_var = tk.BooleanVar(value=True)  # 默认开启错误时复制原图
        
        # 用于保存最后一条消息
        self.message_var = tk.StringVar(value="等待任务...")
        # 消息历史记录
        self.message_history = []
        self.max_history = 100

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
        ttk.Checkbutton(self, text="出错时复制原图到输出目录", variable=self.copy_on_error_var).grid(row=row, column=0, columnspan=2, sticky='w')
        row += 1

        # 进度条
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        # 消息显示 - 使用滚动文本框替代标签
        ttk.Label(self, text="处理日志:").grid(row=row, column=0, columnspan=2, sticky='w', pady=(5,0))
        row += 1
        self.message_text = scrolledtext.ScrolledText(self, width=40, height=10, wrap=tk.WORD)
        self.message_text.grid(row=row, column=0, columnspan=2, sticky='nsew', pady=5)
        self.message_text.insert(tk.END, "等待任务...\n")
        self.message_text.configure(state='disabled')  # 设为只读
        row += 1

        # 开始按钮
        self.start_button = ttk.Button(self, text="开始批量换脸")
        self.start_button.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        # 让文本区域随窗口调整大小
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(row-2, weight=1)  # 让消息文本区域可扩展

    def get_params(self):
        """获取界面参数"""
        return {
            'char': self.char_var.get(),
            'input_path': self.input_path_var.get(),
            'output_path': self.output_path_var.get(),
            'repaint_hair': self.repaint_hair_var.get(),
            'copy_on_error': self.copy_on_error_var.get()  # 添加新选项到参数中
        }

    def set_progress(self, value):
        self.progress_var.set(value)

    def update_message(self, message):
        """
        由 Controller 调用，用于更新消息显示
        将新消息添加到文本框末尾
        """
        # 保存最新消息到变量
        self.message_var.set(message)
        
        # 添加到历史记录
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
            
        # 添加到文本框
        print(f"Swapface: '{message}'")  # 打印日志
        self.message_text.configure(state='normal')
        self.message_text.insert(tk.END, message + "\n")
        self.message_text.see(tk.END)  # 滚动到最新消息
        self.message_text.configure(state='disabled')  # 恢复只读

    def get_start_button(self):
        return self.start_button