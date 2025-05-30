import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrolledtext
import os
from tkinterdnd2 import DND_FILES
from tools.cores.config import config


class SwapfaceTab(ttk.Frame):
    """
    换脸Tab界面，包含参数输入、进度显示、消息显示、开始按钮
    """
    def __init__(self, parent):
        """
        初始化 Tab 1 的视图

        Args:
            parent: Tkinter 父容器 (通常是 Notebook)
        """
        super().__init__(parent, padding="10")
        self.parent = parent

        # 参数输入区
        self.char_var = tk.StringVar()
        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.repaint_hair_var = tk.BooleanVar(value=True)
        self.copy_on_error_var = tk.BooleanVar(value=True)  # 默认开启错误时复制原图
        
        # 用于保存最后一条消息
        self.message_var = tk.StringVar(value="等待任务...")
        # 消息历史记录
        self.message_history = []
        self.max_history = 100

        row = 0
        ttk.Label(self, text="人脸LoRA名").grid(row=row, column=0, sticky='w')
        
        # 使用Combobox，设置为可输入状态
        self.char_combobox = ttk.Combobox(self, textvariable=self.char_var, width=28)
        self.char_combobox.grid(row=row, column=1, sticky='ew')
        # 添加按键释放事件绑定，用于实时过滤选项
        self.char_combobox.bind('<KeyRelease>', self.filter_combobox)
        # 绑定值变更事件，用于保存配置
        self.char_var.trace_add("write", self.save_ui_config)
        # 保存完整的选项列表
        self.all_lora_options = []
        
        # 添加刷新按钮
        refresh_button = ttk.Button(self, text="刷新", width=5, command=self.refresh_lora_list)
        refresh_button.grid(row=row, column=2, padx=2)
        
        row += 1
        ttk.Label(self, text="输入文件夹").grid(row=row, column=0, sticky='w')
        self.input_entry = ttk.Entry(self, textvariable=self.input_path_var, width=30)
        self.input_entry.grid(row=row, column=1, columnspan=2, sticky='ew')
        # 为输入文件夹添加拖放支持（在initialize_dnd中实现）
        # 添加值变更跟踪
        self.input_path_var.trace_add("write", self.save_ui_config)
        
        row += 1
        ttk.Label(self, text="输出文件夹").grid(row=row, column=0, sticky='w')
        self.output_entry = ttk.Entry(self, textvariable=self.output_path_var, width=30)
        self.output_entry.grid(row=row, column=1, columnspan=2, sticky='ew')
        # 为输出文件夹添加拖放支持（在initialize_dnd中实现）
        # 添加值变更跟踪
        self.output_path_var.trace_add("write", self.save_ui_config)
        
        row += 1
        ttk.Checkbutton(self, text="重绘头发(repaint_hair)", variable=self.repaint_hair_var, 
                       command=self.save_ui_config).grid(row=row, column=0, columnspan=3, sticky='w')
        row += 1
        ttk.Checkbutton(self, text="出错时复制原图到输出目录", variable=self.copy_on_error_var,
                       command=self.save_ui_config).grid(row=row, column=0, columnspan=3, sticky='w')
        row += 1

        # 进度条
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky='ew', pady=5)
        row += 1

        # 消息显示 - 使用滚动文本框替代标签
        ttk.Label(self, text="处理日志:").grid(row=row, column=0, columnspan=3, sticky='w', pady=(5,0))
        row += 1
        self.message_text = scrolledtext.ScrolledText(self, width=40, height=10, wrap=tk.WORD)
        self.message_text.grid(row=row, column=0, columnspan=3, sticky='nsew', pady=5)
        self.message_text.insert(tk.END, "等待任务...\n")
        self.message_text.configure(state='disabled')  # 设为只读
        row += 1

        # 开始按钮
        self.start_button = ttk.Button(self, text="开始批量换脸")
        self.start_button.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1

        # 让文本区域随窗口调整大小
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(row-2, weight=1)  # 让消息文本区域可扩展
        
        # 加载UI配置
        self.load_ui_config()
        
        # 初始化加载LoRA列表
        self.refresh_lora_list()

    def initialize_dnd(self, dnd_toplevel):
        """
        初始化拖放功能，必须在主窗口完全初始化后调用
        
        Args:
            dnd_toplevel: TkinterDnD.Tk实例（主窗口）
        """
        # 为输入框添加拖放绑定
        self.input_entry.drop_target_register(DND_FILES)
        self.input_entry.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, self.input_path_var))
        
        # 为输出框添加拖放绑定
        self.output_entry.drop_target_register(DND_FILES)
        self.output_entry.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, self.output_path_var))
        
        self.update_message("已启用文件夹拖放支持")
    
    def on_drop(self, event, string_var):
        """处理文件/文件夹拖放事件"""
        # 获取拖放的文件路径
        path = event.data
        
        # Windows系统下可能返回带有花括号的路径，如: {D:/path/to/folder}
        path = path.strip('{}')
        
        # 如果是多个文件，只取第一个
        if ' ' in path:
            path = path.split(' ')[0]
        
        # 移除可能存在的引号
        path = path.strip('"')
        
        # 更新路径变量
        string_var.set(path)
        self.update_message(f"拖入路径: {path}")
        # 拖放后保存配置
        self.save_ui_config()
    
    def get_lora_files(self):
        """获取models/hyper_lora/chars目录下的所有.safetensors文件名"""
        # 通过相对路径计算绝对路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        lora_path = os.path.join(base_dir, "models", "hyper_lora", "chars")
        
        lora_files = []
        try:
            if os.path.exists(lora_path) and os.path.isdir(lora_path):
                # 获取所有.safetensors文件，并去掉扩展名
                all_files = os.listdir(lora_path)
                lora_files = [os.path.splitext(f)[0] for f in all_files 
                             if f.lower().endswith('.safetensors')]
                # 按字母顺序排序
                lora_files.sort()
                
                if lora_files:
                    self.update_message(f"找到{len(lora_files)}个人脸LoRA模型")
                else:
                    self.update_message(f"警告: 在{lora_path}中未找到.safetensors文件")
            else:
                self.update_message(f"警告: 目录不存在 - {lora_path}")
        except Exception as e:
            self.update_message(f"读取LoRA文件出错: {e}")
        
        return lora_files
    
    def filter_combobox(self, event=None):
        """根据当前输入过滤Combobox选项"""
        typed_text = self.char_var.get().lower()
        if typed_text == '':
            # 如果输入为空，显示所有选项
            self.char_combobox['values'] = self.all_lora_options
        else:
            # 过滤匹配的选项
            filtered_options = [opt for opt in self.all_lora_options 
                               if typed_text in opt.lower()]
            self.char_combobox['values'] = filtered_options
            
            if filtered_options:
                # 如果有匹配项，打开下拉列表
                self.char_combobox.event_generate('<Down>')
    
    def refresh_lora_list(self):
        """刷新LoRA文件列表"""
        current_selection = self.char_var.get()
        
        # 清空当前列表
        self.char_combobox['values'] = []
        
        # 获取新的列表
        self.lora_files = self.get_lora_files()
        
        if self.lora_files:
            # 保存完整的选项列表
            self.all_lora_options = self.lora_files
            
            # 设置下拉框选项
            self.char_combobox['values'] = self.lora_files
            
            # 尝试保持之前的选择，如果不存在则选择第一个
            if current_selection in self.lora_files:
                self.char_var.set(current_selection)
            else:
                self.char_combobox.current(0)
                self.update_message(f"已选择: {self.char_var.get()}")
        else:
            self.all_lora_options = []
            self.char_var.set('')
            self.update_message("未找到可用的LoRA模型")

    def get_params(self):
        """获取界面参数"""
        return {
            'char': self.char_var.get(),
            'input_path': self.input_path_var.get(),
            'output_path': self.output_path_var.get(),
            'repaint_hair': self.repaint_hair_var.get(),
            'copy_on_error': self.copy_on_error_var.get()  # 添加新选项到参数中
        }

    def set_progress(self, value):
        self.progress_var.set(value)

    def update_message(self, message):
        """
        由 Controller 调用，用于更新消息显示
        将新消息添加到文本框末尾
        """
        # 保存最新消息到变量
        self.message_var.set(message)
        
        # 添加到历史记录
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
            
        # 添加到文本框
        print(f"Swapface: '{message}'")  # 打印日志
        self.message_text.configure(state='normal')
        self.message_text.insert(tk.END, message + "\n")
        self.message_text.see(tk.END)  # 滚动到最新消息
        self.message_text.configure(state='disabled')  # 恢复只读

    def get_start_button(self):
        return self.start_button
        
    def set_button_start(self):
        """
        设置按钮为开始状态
        """
        self.start_button.config(text="开始批量换脸", state="normal")
        
    def set_button_stop(self):
        """
        设置按钮为停止状态
        """
        self.start_button.config(text="停止任务", state="normal")
    
    def set_button_stopping(self):
        """
        设置按钮为正在停止状态
        """
        self.start_button.config(text="正在停止...", state="disabled")

    def save_ui_config(self, *args):
        """
        保存UI控件状态到配置文件
        *args 参数是为了兼容trace_add回调
        """
        try:
            # 获取当前控件状态
            ui_config = {
                'char': self.char_var.get(),
                'input_path': self.input_path_var.get(),
                'output_path': self.output_path_var.get(),
                'repaint_hair': self.repaint_hair_var.get(),
                'copy_on_error': self.copy_on_error_var.get()
            }
            
            # 保存到配置
            config.set_section('swapface', ui_config)
        except Exception as e:
            self.update_message(f"保存配置失败: {e}")
    
    def load_ui_config(self):
        """
        从配置文件加载UI控件状态
        """
        try:
            # 获取配置
            ui_config = config.get_section('swapface')
            
            if ui_config:
                # 设置控件值
                if 'char' in ui_config and ui_config['char']:
                    self.char_var.set(ui_config['char'])
                if 'input_path' in ui_config:
                    self.input_path_var.set(ui_config['input_path'])
                if 'output_path' in ui_config:
                    self.output_path_var.set(ui_config['output_path'])
                if 'repaint_hair' in ui_config:
                    self.repaint_hair_var.set(ui_config['repaint_hair'])
                if 'copy_on_error' in ui_config:
                    self.copy_on_error_var.set(ui_config['copy_on_error'])
                
                self.update_message("已加载上次的设置")
        except Exception as e:
            self.update_message(f"加载配置失败: {e}")