from views.main_view import MainView
from views.swapface_tab import SwapfaceTab
from views.takcloth_tab import TakeClothTab
from models.swapface_model import SwapfaceModel
from models.takecloth_model import TakeClothModel
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
        self.swapface_model = SwapfaceModel()
        self.takecloth_model = TakeClothModel()
        self.main_view = MainView(root)

        # --- 创建 Tab 的 View ---
        self.tabview_swapface = SwapfaceTab(self.main_view.notebook)
        self.tabview_takecloth = TakeClothTab(self.main_view.notebook)

        # --- 将 Tab 的 View 添加到 Notebook ---
        self.main_view.add_tab(self.tabview_swapface, "换脸")
        self.main_view.add_tab(self.tabview_takecloth, "脱衣")

        # --- 初始化拖放功能 ---
        self.tabview_swapface.initialize_dnd(root)

        # --- 创建并关联 Tab 的 Controller ---
        self.swapface_controller = SwapfaceController(self.swapface_model, self.tabview_swapface)
        self.takecloth_controller = takeclothController(self.takecloth_model, self.tabview_takecloth)

        print("MainController: Application initialized.") # 打印日志
