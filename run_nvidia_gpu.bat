@REM set HF_ENDPOINT=https://hf-mirror.com
set HF_HOME=%CD%\.cache\hf_download
set MODELSCOPE_CACHE=%CD%\.cache\modelscope
set U2NET_HOME=%CD%\models\u2net


call conda activate comfyui
python main.py
pause