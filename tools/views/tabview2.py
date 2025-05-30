import tkinter as tk
import tkinter.ttk as ttk



class TabView2(ttk.Frame):
    """
    TabView2 类：管理第二个 Tab 的界面
    """
    def __init__(self, parent):
        """
        初始化 Tab 2 的视图

        Args:
            parent: Tkinter 父容器 (通常是 Notebook)
        """
        super().__init__(parent, padding="10")
        self.parent = parent

        self.input_var = tk.StringVar() # 用于输入框的 Tkinter 变量
        self.result_var = tk.StringVar(value="等待输入...") # 用于显示结果的 Tkinter 变量

        ttk.Label(self, text="请输入文本：").pack(pady=5)

        self.input_entry = ttk.Entry(self, textvariable=self.input_var, width=40)
        self.input_entry.pack(pady=5)

        # 注意：command 属性稍后由对应的 Controller 设置
        self.process_button = ttk.Button(self, text="处理输入")
        self.process_button.pack(pady=5)

        ttk.Label(self, text="处理结果：").pack(pady=5)
        self.result_label = ttk.Label(self, textvariable=self.result_var, wraplength=300)
        self.result_label.pack(pady=5)


    def get_input(self):
        """
        由 Tab2Controller 调用，获取输入框的文本
        """
        return self.input_var.get()

    def display_result(self, result_message):
        """
        由 Tab2Controller 调用，更新结果显示
        """
        print(f"TabView2: Updating result display to '{result_message}'") # 打印日志
        self.result_var.set(result_message)

    def get_process_button(self):
        """返回处理按钮控件，供 Controller 绑定事件"""
        return self.process_button

    def get_input_entry(self):
        """返回输入框控件，供 Controller 绑定事件 (如回车键)"""
        return self.input_entry