
class takeclothController:
    """
    Tab2Controller 类：管理 Tab 2 的逻辑
    """
    def __init__(self, model, view):
        """
        初始化 Tab 2 的控制器

        Args:
            model: AppModel 实例
            view: TabView2 实例
        """
        self.model = model
        self.view = view

        # 绑定 View 中按钮和输入框的事件
        self.view.get_process_button().config(command=self.process_input)
        # 绑定输入框的回车键事件 (可选)
        self.view.get_input_entry().bind('<Return>', lambda event=None: self.process_input())

        # 初始更新 View 显示 (显示初始结果)
        self.update_view()

    def process_input(self):
        """
        处理 Tab 2 中处理按钮点击或回车事件
        """
        print("Tab2Controller: '处理输入' 事件触发") # 打印日志
        # 从 View 获取用户输入
        user_input = self.view.get_input()
        # 调用 Model 的方法更新数据（并进行处理）
        self.model.set_input_for_tab2(user_input)
        # 更新 View 显示 (从 Model 获取处理结果)
        self.update_view()

    def update_view(self):
        """
        从 Model 获取 Tab 2 相关的数据，并调用 View 的方法更新显示
        """
        result_message = self.model.get_result_for_tab2()
        self.view.display_result(result_message)