import subprocess
import threading
import queue
import os
import shutil
from cores import swapface_hyperlora_core

class SwapfaceModel:
    def __init__(self):
        self.char = ''
        self.input_path = ''
        self.output_path = ''
        self.sub_body = True
        self.copy_on_error = True  # 默认开启错误时复制原图
        self.output_queue = queue.Queue()
        self.progress = 0
        self.message = ''
        self._worker_thread = None
        self._is_running = False
        self._current_processing_file = None  # 记录当前正在处理的文件
        self._stop_requested = False  # 标记是否请求停止任务

    def set_params(self, char, input_path, output_path, sub_body=True, expression_edit=False, copy_on_error=True):
        self.char = char
        self.input_path = input_path
        self.output_path = output_path
        self.sub_body = sub_body
        self.expression_edit = expression_edit
        self.copy_on_error = copy_on_error

    def start_swapface(self):
        if self._is_running:
            self.message = '任务正在运行中...'
            self.output_queue.put('任务正在运行中...')
            return
        self._is_running = True
        self._stop_requested = False  # 重置停止标志
        self.progress = 0
        self.message = '任务启动中...'
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except:
                pass
        self.output_queue.put('任务启动中...')
        self._worker_thread = threading.Thread(target=self._run_process, daemon=True)
        self._worker_thread.start()

    def stop_swapface(self):
        """请求停止换脸任务，会等待当前图片处理完成"""
        if self._is_running:
            self._stop_requested = True
            self.output_queue.put('已请求停止任务，等待当前图片处理完成...')
            self.message = '正在停止任务...'
            return True
        return False

    def _progress_callback(self, current, total):
        self.progress = int(current / total * 100)
        msg = f'总进度 [{current}/{total}]'
        self.message = msg
        self.output_queue.put(msg)

    def _message_callback(self, msg):
        self.message = msg
        self.output_queue.put(msg)


    def _run_process(self):
        try:
            self.output_queue.put('开始处理换脸任务...')
            # 获取文件列表
            file_list = [f for f in os.listdir(self.input_path) 
                         if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))]
            total = len(file_list)
            os.makedirs(self.output_path, exist_ok=True)
            
            for idx, file in enumerate(file_list):
                # 检查是否请求停止
                if self._stop_requested:
                    self.message = '任务已被用户停止'
                    self.output_queue.put('任务已被用户停止')
                    break
                
                in_path = os.path.join(self.input_path, file)
                out_path = os.path.join(self.output_path, file)
                
                # 记录当前处理的文件
                self._current_processing_file = in_path
                self.output_queue.put(f'开始处理文件: {file}')
                
                # 处理单个图片的逻辑
                try:
                    # 直接调用核心处理逻辑，传入单个文件路径
                    swapface_hyperlora_core.run(
                        char=self.char,
                        input_file=in_path,
                        output_file=out_path,
                        sub_body=self.sub_body,
                        expression_edit=self.expression_edit,
                        message_callback=self._message_callback
                    )
                except Exception as e:
                    error_msg = f'{file} 处理失败: {e}'
                    self.message = error_msg
                    self.output_queue.put(error_msg)
                    
                    # 如果启用了错误复制选项，复制原图到输出目录
                    if self.copy_on_error:
                        try:
                            shutil.copy2(in_path, out_path)
                            self.output_queue.put(f'处理失败，已复制原图 {file} 到输出目录')
                        except Exception as copy_err:
                            self.output_queue.put(f'复制原图失败: {copy_err}')
                
                # 更新进度
                self.progress = int((idx + 1) / total * 100)
                self.output_queue.put(f'总进度 [{idx + 1}/{total}]')
            
            # 任务正常结束或被停止
            self._is_running = False
            if not self._stop_requested:
                self.message = '任务完成'
                self.output_queue.put('任务完成')
            self._stop_requested = False  # 重置停止标志
            
        except Exception as e:
            error_msg = f'任务异常: {e}'
            self.message = error_msg
            self.output_queue.put(error_msg)
            self._is_running = False
            self._stop_requested = False  # 重置停止标志

    def get_progress(self):
        return self.progress

    def get_message(self):
        return self.message

    def is_running(self):
        return self._is_running
        
    def is_stop_requested(self):
        """返回是否已请求停止任务"""
        return self._stop_requested