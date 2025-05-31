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
        self._refresh_interval = 100  # ms，减少刷新间隔以更快捕获消息
        self._running = False

        # 绑定开始/停止按钮事件
        self.view.get_start_button().config(command=self.toggle_swapface_task)

        # 初始更新 View 显示
        self.update_view()

    def toggle_swapface_task(self):
        """切换开始/停止任务"""
        if self.model.is_running():
            # 如果正在运行，则停止任务
            if self.model.stop_swapface():
                self.view.update_message('正在停止任务，等待当前图片处理完成...')
                # 更新按钮文本为"正在停止..."，并禁用按钮直到完全停止
                self.view.set_button_stopping()
        else:
            # 如果没有运行，则开始任务
            params = self.view.get_params()
            self.model.set_params(
                params['char'],
                params['input_path'],
                params['output_path'],
                params['sub_body'],
                params['copy_on_error']
            )
            self.model.start_swapface()
            self._running = True
            # 更新按钮文本为"停止任务"
            self.view.set_button_stop()
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
        # 更新进度条
        progress = self.model.get_progress()
        self.view.set_progress(progress)
        
        # 处理队列中的所有消息
        try:
            # 非阻塞方式检查是否有新消息
            while not self.model.output_queue.empty():
                message = self.model.output_queue.get(block=False)
                self.view.update_message(message)
        except Exception as e:
            print(f"获取消息出错: {e}")
        
        # 显示当前消息状态（如果队列为空）
        if not self.view.message_var.get():
            message = self.model.get_message()
            self.view.update_message(message)
            
        # 更新按钮状态
        if self.model.is_running():
            # 如果任务正在运行，确保按钮显示"停止任务"
            if self.model.is_stop_requested():
                # 如果已请求停止但还未完全停止
                self.view.set_button_stopping()
            else:
                # 正常运行中
                self.view.set_button_stop()
        else:
            # 如果任务未运行，恢复按钮为"开始批量换脸"
            self.view.set_button_start()
            self._running = False