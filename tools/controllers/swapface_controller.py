import threading
import time

class SwapfaceController:
    """
    SwapfaceTab 控制器：管理换脸Tab的逻辑
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
        self._refresh_interval = 500  # ms
        self._running = False

        # 绑定开始按钮事件
        self.view.get_start_button().config(command=self.start_swapface_task)

        # 初始更新 View 显示
        self.update_view()

    def start_swapface_task(self):
        if self.model.is_running():
            self.view.update_message('任务正在运行中...')
            return
        params = self.view.get_params()
        self.model.set_params(
            params['char'],
            params['input_path'],
            params['output_path'],
            params['repaint_hair']
        )
        self.model.start_swapface()
        self._running = True
        self._schedule_refresh()

    def _schedule_refresh(self):
        if self._running:
            self.update_view()
            # Tkinter after方法定时刷新
            self.view.after(self._refresh_interval, self._schedule_refresh)

    def update_view(self):
        """
        从 Model 获取 Tab 1 相关的数据，并调用 View 的方法更新显示
        """
        progress = self.model.get_progress()
        message = self.model.get_message()
        self.view.set_progress(progress)
        self.view.update_message(message)
        if not self.model.is_running():
            self._running = False