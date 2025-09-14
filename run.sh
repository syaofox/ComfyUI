#!/bin/bash

# =========================================================
# 启动 ComfyUI 的脚本
# 自动处理路径和虚拟环境，提高脚本的健壮性和可移植性。
# =========================================================

# 当任何命令执行失败时，立即退出脚本
set -e

# 获取脚本所在的目录，并切换到该目录
# 这使得脚本可以从任何位置被调用
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 设定 Hugging Face 和 ModelScope 的缓存路径，避免占用用户主目录空间
export HF_HOME="$PWD/.cache/hf_download"
export MODELSCOPE_CACHE="$PWD/.cache/modelscope"

# U2Net 模型目录，根据 ComfyUI 的要求设定
export U2NET_HOME="$PWD/models/u2net"

echo "Using cache directories:"
echo "  HF_HOME: $HF_HOME"
echo "  MODELSCOPE_CACHE: $MODELSCOPE_CACHE"
echo "  U2NET_HOME: $U2NET_HOME"

# 检查 Python 虚拟环境是否存在
VENV_PATH="./.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please create it first (e.g., python3 -m venv .venv)."
    exit 1
fi

# 激活 Python 虚拟环境
echo "Activating Python virtual environment..."
source "$VENV_PATH/bin/activate"

# 启动 ComfyUI
echo "Starting ComfyUI..."
python main.py

echo "ComfyUI script finished."