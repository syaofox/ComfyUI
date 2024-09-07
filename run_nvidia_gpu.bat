set HF_ENDPOINT=https://hf-mirror.com
set HF_HOME=%CD%\hf_download
set U2NET_HOME=%CD%\models\u2net

call conda activate comfyui
python main.py
pause
