#!/bin/bash

# 设置环境变量
export HF_HOME="$PWD/.cache/hf_download"
export MODELSCOPE_CACHE="$PWD/.cache/modelscope"
export U2NET_HOME="$PWD/models/u2net"

cd /home/syaofox/data/dev/ComfyUI

# 使用 uv 运行 main.py
source .venv/bin/activate
python main.py