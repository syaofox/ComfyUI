FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu22.04

ARG USERNAME=comfy
ARG USER_UID=1000
ARG USER_GID=1000

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

RUN groupadd --gid ${USER_GID} ${USERNAME} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${USERNAME} && \
    mkdir -p /app && chown ${USERNAME}:${USERNAME} /app

# 安装 uv（负责管理 Python 和依赖）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 复制项目元数据用于安装依赖
COPY --chown=${USERNAME}:${USERNAME} pyproject.toml requirements.txt ./

# 复制核心代码（运行时其余目录通过卷挂载）
COPY --chown=${USERNAME}:${USERNAME} main.py ./
COPY --chown=${USERNAME}:${USERNAME} *.py ./
COPY --chown=${USERNAME}:${USERNAME} *.yaml ./
COPY --chown=${USERNAME}:${USERNAME} *.md ./
COPY --chown=${USERNAME}:${USERNAME} LICENSE ./
COPY --chown=${USERNAME}:${USERNAME} extra_model_paths.yaml.example ./
COPY --chown=${USERNAME}:${USERNAME} comfy/ ./comfy/
COPY --chown=${USERNAME}:${USERNAME} comfy_api/ ./comfy_api/
COPY --chown=${USERNAME}:${USERNAME} comfy_api_nodes/ ./comfy_api_nodes/
COPY --chown=${USERNAME}:${USERNAME} comfy_config/ ./comfy_config/
COPY --chown=${USERNAME}:${USERNAME} comfy_execution/ ./comfy_execution/
COPY --chown=${USERNAME}:${USERNAME} comfy_extras/ ./comfy_extras/
COPY --chown=${USERNAME}:${USERNAME} app/ ./app/
COPY --chown=${USERNAME}:${USERNAME} api_server/ ./api_server/
COPY --chown=${USERNAME}:${USERNAME} middleware/ ./middleware/
COPY --chown=${USERNAME}:${USERNAME} utils/ ./utils/
COPY --chown=${USERNAME}:${USERNAME} input/ ./input/
COPY --chown=${USERNAME}:${USERNAME} script_examples/ ./script_examples/
COPY --chown=${USERNAME}:${USERNAME} run.sh ./run.sh

# 使用国内 PyPI 镜像（可按需调整）
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
ENV UV_EXTRA_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV TORCH_CUDA_ARCH_LIST="8.6"

# 使用非 root 用户安装 Python 与依赖
USER ${USERNAME}

# 安装 Python 与依赖
RUN uv python install 3.12 && \
    uv --preview-features extra-build-dependencies sync

# 运行时环境变量
ENV HF_HOME=/app/.caches/hf_download \
    MODELSCOPE_CACHE=/app/.caches/modelscope \
    OMP_NUM_THREADS=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /app/.caches/hf_download /app/.caches/modelscope /app/.cache/temp /app/output /app/models /app/custom_nodes /app/user /app/input /app/temp

EXPOSE 8188

CMD ["uv", "run", "main.py", "--listen", "0.0.0.0", "--port", "8188"]