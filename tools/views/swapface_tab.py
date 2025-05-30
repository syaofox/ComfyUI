import tkinter as tk
import tkinter.ttk as ttk


class SwapfaceTab(ttk.Frame):
    """
    TabView1 类：管理第一个 Tab 的界面
    """
    def __init__(self, parent):
        """
        初始化 Tab 1 的视图

        Args:
            parent: Tkinter 父容器 (通常是 Notebook)
        """
        super().__init__(parent, padding="10")
        self.parent = parent

        self.message_var = tk.StringVar(value="Loading...") # 用于显示消息的 Tkinter 变量

        self.message_label = ttk.Label(self, textvariable=self.message_var, wraplength=300)
        self.message_label.pack(pady=10)

        # 注意：command 属性稍后由对应的 Controller 设置
        self.refresh_button = ttk.Button(self, text="刷新消息")
        self.refresh_button.pack(pady=5)

    def update_message(self, message):
        """
        由 Tab1Controller 调用，用于更新消息显示
        """
        print(f"TabView1: Updating message display to '{message}'") # 打印日志
        self.message_var.set(message)

    def get_refresh_button(self):
        """返回刷新按钮控件，供 Controller 绑定事件"""
        return self.refresh_button