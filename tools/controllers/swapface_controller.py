
class SwapfaceController:
    """
    Tab1Controller 类：管理 Tab 1 的逻辑
    """
    def __init__(self, model, view):
        """
        初始化 Tab 1 的控制器

        Args:
            model: AppModel 实例
            view: TabView1 实例
        """
        self.model = model
        self.view = view

        # 绑定 View 中按钮的事件
        self.view.get_refresh_button().config(command=self.refresh_button_clicked)

        # 初始更新 View 显示
        self.update_view()

    def refresh_button_clicked(self):
        """
        处理 Tab 1 中刷新按钮的点击事件
        """
        print("Tab1Controller: '刷新消息' 按钮被点击") # 打印日志
        # 调用 Model 的方法更新数据
        self.model.refresh_message_for_tab1()
        # 更新 View 显示 (从 Model 获取最新数据)
        self.update_view()

    def update_view(self):
        """
        从 Model 获取 Tab 1 相关的数据，并调用 View 的方法更新显示
        """
        message = self.model.get_message_for_tab1()
        self.view.update_message(message)