import subprocess
import threading
import queue
import os
from cores import swapface_hyperlora_core

class SwapfaceModel:
    def __init__(self):
        self.char = ''
        self.input_path = ''
        self.output_path = ''
        self.repaint_hair = True
        self.output_queue = queue.Queue()
        self.progress = 0
        self.message = ''
        self._worker_thread = None
        self._is_running = False

    def set_params(self, char, input_path, output_path, repaint_hair=True):
        self.char = char
        self.input_path = input_path
        self.output_path = output_path
        self.repaint_hair = repaint_hair

    def start_swapface(self):
        if self._is_running:
            self.message = '任务正在运行中...'
            self.output_queue.put('任务正在运行中...')
            return
        self._is_running = True
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
            swapface_hyperlora_core.run(
                char=self.char,
                input_path=self.input_path,
                output_path=self.output_path,
                repaint_hair=self.repaint_hair,
                progress_callback=self._progress_callback,
                message_callback=self._message_callback
            )
            self._is_running = False
            self.message = '任务完成'
            self.output_queue.put('任务完成')
        except Exception as e:
            error_msg = f'任务异常: {e}'
            self.message = error_msg
            self.output_queue.put(error_msg)
            self._is_running = False

    def get_progress(self):
        return self.progress

    def get_message(self):
        return self.message

    def is_running(self):
        return self._is_running