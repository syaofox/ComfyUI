FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# 安装基础依赖
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list && \
    sed -i 's/jammy main/jammy main restricted universe multiverse/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git wget curl ca-certificates \
        build-essential pkg-config libcairo2-dev \
        libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 \
        libgomp1 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 安装 uv（负责管理 Python 和依赖）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 复制项目元数据用于安装依赖
COPY pyproject.toml uv.lock ./
COPY requirements.txt ./

# 复制核心代码（运行时其余目录通过卷挂载）
COPY main.py ./
COPY *.py ./
COPY *.yaml ./
COPY *.md ./
COPY LICENSE ./
COPY extra_model_paths.yaml.example ./
COPY comfy/ ./comfy/
COPY comfy_api/ ./comfy_api/
COPY comfy_api_nodes/ ./comfy_api_nodes/
COPY comfy_config/ ./comfy_config/
COPY comfy_execution/ ./comfy_execution/
COPY comfy_extras/ ./comfy_extras/
COPY app/ ./app/
COPY api_server/ ./api_server/
COPY middleware/ ./middleware/
COPY utils/ ./utils/
COPY input/ ./input/
COPY script_examples/ ./script_examples/
COPY run.sh ./run.sh

# 使用国内 PyPI 镜像（可按需调整）
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
ENV UV_EXTRA_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Python 与依赖
RUN uv python install 3.12 && \
    uv sync --frozen

# 运行时环境变量
ENV HF_HOME=/app/.caches/hf_download \
    MODELSCOPE_CACHE=/app/.caches/modelscope \
    OMP_NUM_THREADS=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /app/.caches/hf_download /app/.caches/modelscope /app/.cache/temp /app/output /app/models /app/custom_nodes /app/user

EXPOSE 8188

CMD ["uv", "run", "main.py", "--listen", "0.0.0.0", "--port", "8188"]