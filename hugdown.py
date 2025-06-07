from huggingface_hub import snapshot_download

# 定义模型ID (repo_id)
repo_id = "ByteDance/Hyper-SD"  # 例如: "google/flan-t5-small"

# 定义参考 (ref)
# 可以是分支名 (如 "main", "dev"), 标签 (如 "v1.0"), 或 commit hash
revision = "main" # 默认通常是 "main"

# 定义要下载的自定义目录
custom_directory = "comfyui" # 例如: "data/images"

# 构造 allow_patterns 来匹配该目录下的所有文件
# 注意：你需要知道目录内可能的文件类型或模式
# 以下示例会下载 custom_directory/ 下的所有文件
# 如果你只想要某个特定类型的文件，可以更具体，例如 "path/to/your/subdirectory/*.json"
allow_patterns = f"{custom_directory}/**" # 匹配 custom_directory 及其所有子目录下的所有文件

# 定义下载到本地的目录
local_dir = r"D:\downloads\JJdown\1" # 你希望下载到本地的路径

try:
    # 使用 snapshot_download 下载
    # local_dir: 文件会下载到这个目录，并保留仓库中的目录结构
    # revision: 指定要下载的参考
    # allow_patterns: 只下载符合这些模式的文件
    downloaded_path = snapshot_download(
        repo_id=repo_id,
        revision=revision,
        allow_patterns=allow_patterns,
        local_dir=local_dir,
        local_dir_use_symlinks=False # 在某些系统上，如Windows，关闭软链接可能更稳定
    )
    print(f"目录 '{custom_directory}' 从 '{repo_id}' 的 '{revision}' 参考下成功下载到: {downloaded_path}")

except Exception as e:
    print(f"下载失败: {e}")