import os
import threading
import time
import shutil
from cores.takecloth_core import run
from views.takcloth_tab import TakeClothTab


class TakeClothController:
    """
    脱衣服功能的控制器，负责处理业务逻辑和连接视图与核心处理逻辑
    """
    def __init__(self, tab: TakeClothTab):
        """
        初始化控制器
        
        Args:
            tab: TakeClothTab界面实例
        """
        self.tab = tab
        self.running = False
        self.stop_requested = False
        self.thread = None
        
        # 绑定开始按钮
        self.tab.get_start_button().config(command=self.toggle_task)
    
    def toggle_task(self):
        """
        切换任务状态：如果没有运行则开始，如果正在运行则停止
        """
        if not self.running:
            self.start_task()
        else:
            self.stop_task()
    
    def start_task(self):
        """
        开始处理任务
        """
        # 获取参数
        params = self.tab.get_params()
        input_path = params['input_path']
        output_path = params['output_path']
        copy_on_error = params['copy_on_error']
        
        # 检查参数
        if not input_path or not os.path.exists(input_path):
            self.tab.update_message(f"输入路径不存在: {input_path}")
            return
        
        if not output_path:
            self.tab.update_message("请指定输出路径")
            return
        
        # 确保输出目录存在
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            self.tab.update_message(f"创建输出目录失败: {e}")
            return
        
        # 设置状态和按钮
        self.running = True
        self.stop_requested = False
        self.tab.set_button_stop()
        self.tab.update_message("开始处理任务...")
        
        # 在新线程中启动处理
        self.thread = threading.Thread(target=self.process_task, 
                                      args=(input_path, output_path, copy_on_error))
        self.thread.daemon = True
        self.thread.start()
    
    def stop_task(self):
        """
        停止正在进行的任务
        """
        self.stop_requested = True
        self.tab.set_button_stopping()
        self.tab.update_message("正在停止任务...")
    
    def process_task(self, input_path, output_path, copy_on_error):
        """
        处理任务的主要逻辑
        
        Args:
            input_path: 输入文件夹路径
            output_path: 输出文件夹路径
            copy_on_error: 处理失败时是否复制原图
        """
        try:
            # 收集所有图片文件
            image_files = []
            input_path = os.path.normpath(input_path)
            
            if os.path.isdir(input_path):
                # 遍历目录
                for root, _, files in os.walk(input_path):
                    for file in files:
                        # 检查是否为图片文件
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                            image_files.append(os.path.join(root, file))
                
                self.tab.update_message(f"找到 {len(image_files)} 个图片文件需要处理")
            else:
                # 单个文件
                if input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    image_files.append(input_path)
                    self.tab.update_message(f"处理单个文件: {input_path}")
            
            # 处理所有图片
            total = len(image_files)
            success_count = 0
            error_count = 0
            
            for i, input_file in enumerate(image_files):
                # 检查是否请求停止
                if self.stop_requested:
                    self.tab.update_message("任务已停止")
                    break
                
                # 更新进度
                progress = int((i / total) * 100)
                self.tab.set_progress(progress)
                
                try:
                    # 构建输出文件路径
                    rel_path = os.path.relpath(input_file, input_path) if os.path.isdir(input_path) else os.path.basename(input_file)
                    output_file = os.path.join(output_path, rel_path)
                    
                    # 确保输出目录存在
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    # 调用核心处理逻辑
                    run(input_file, output_file, self.tab.update_message)
                    
                    success_count += 1
                except Exception as e:
                    self.tab.update_message(f"处理失败 {os.path.basename(input_file)}: {e}")
                    error_count += 1
                    
                    # 如果设置了复制原图
                    if copy_on_error:
                        try:
                            # 确保输出目录存在
                            os.makedirs(os.path.dirname(output_file), exist_ok=True)
                            # 复制原图到输出目录
                            shutil.copy2(input_file, output_file)
                            self.tab.update_message(f"已复制原图到 {output_file}")
                        except Exception as e:
                            self.tab.update_message(f"复制原图失败: {e}")
            
            # 处理完成，更新状态
            self.tab.set_progress(100)
            self.tab.update_message(f"任务完成! 成功: {success_count}, 失败: {error_count}")
        
        except Exception as e:
            self.tab.update_message(f"任务执行出错: {e}")
        
        finally:
            # 恢复按钮状态
            self.running = False
            self.tab.set_button_start()