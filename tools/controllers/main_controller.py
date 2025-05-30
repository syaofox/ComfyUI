from models.app_model import AppModel
from views.main_view import MainView
from views.swapface_tab import SwapfaceTab
from views.takcloth_tab import TakeClothTab
from controllers.swapface_controller import SwapfaceController
from controllers.takecloth_controller import takeclothController




class MainController:
    """
    MainController 类：应用的主控制器，负责初始化和协调
    """
    def __init__(self, root):
        """
        初始化主控制器

        Args:
            root: Tkinter 根窗口
        """
        self.root = root

        # --- 创建 MVC 组件实例 ---
        self.model = AppModel()
        self.main_view = MainView(root)

        # --- 创建 Tab 的 View ---
        self.tabview_swapface = SwapfaceTab(self.main_view.notebook)
        self.tab2_view = TakeClothTab(self.main_view.notebook)

        # --- 将 Tab 的 View 添加到 Notebook ---
        self.main_view.add_tab(self.tabview_swapface, "换脸")
        self.main_view.add_tab(self.tab2_view, "脱衣")

        # --- 创建并关联 Tab 的 Controller ---
        self.tab1_controller = SwapfaceController(self.model, self.tabview_swapface)
        self.tab2_controller = takeclothController(self.model, self.tab2_view)

        print("MainController: Application initialized.") # 打印日志
