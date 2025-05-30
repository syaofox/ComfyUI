import random
from models.swapface_model import SwapfaceModel

class AppModel:
    """
    模型类：管理应用的数据和业务逻辑
    """
    def __init__(self):
        self._message_for_tab1 = "Initial message for Tab 1"
        self._input_for_tab2 = ""
        self._result_for_tab2 = "No input yet."
        self.swapface_model = SwapfaceModel()

    def get_message_for_tab1(self):
        """获取 Tab 1 的消息"""
        return self._message_for_tab1

    def refresh_message_for_tab1(self):
        """模拟刷新 Tab 1 的消息"""
        messages = [
            "Hello from Model!",
            "Data updated!",
            "Another message.",
            "Random message: " + str(random.randint(1, 100))
        ]
        self._message_for_tab1 = random.choice(messages)
        print(f"Model: Message refreshed to '{self._message_for_tab1}'") # 打印日志

    def set_input_for_tab2(self, user_input):
        """设置 Tab 2 的输入数据，并模拟处理"""
        self._input_for_tab2 = user_input
        if user_input:
            self._result_for_tab2 = f"Processed: {user_input.upper()}" # 简单的处理逻辑
        else:
            self._result_for_tab2 = "Input is empty."
        print(f"Model: Input set to '{self._input_for_tab2}', Result is '{self._result_for_tab2}'") # 打印日志

    def get_result_for_tab2(self):
        """获取 Tab 2 的处理结果"""
        return self._result_for_tab2