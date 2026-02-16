#!/bin/bash

# ComfyUI Custom Nodes 自动更新脚本
# 功能: 检测 custom_nodes 目录下的 git 仓库更新，自动执行 git pull 并更新依赖

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
CUSTOM_NODES_DIR="/mnt/github/ComfyUI/custom_nodes"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAX_RETRIES=3        # 失败时最大重试次数
RETRY_DELAY=2        # 重试间隔（秒）

# 统计变量
total_repos=0
updated_repos=0
failed_repos=0
requirements_updated=0

# 错误记录数组
declare -a errors=()
declare -a repos_to_update=()
declare -a repos_with_requirements=()

echo -e "${BLUE}=== ComfyUI Custom Nodes 更新检查器 ===${NC}"
echo "检查目录: $CUSTOM_NODES_DIR"
echo ""

# 检查 custom_nodes 目录是否存在
if [ ! -d "$CUSTOM_NODES_DIR" ]; then
    echo -e "${RED}错误: custom_nodes 目录不存在: $CUSTOM_NODES_DIR${NC}"
    exit 1
fi

# 函数: 获取当前分支名
get_current_branch() {
    local repo_dir="$1"
    cd "$repo_dir"
    git branch --show-current 2>/dev/null || echo "unknown"
}

# 函数: 检查仓库是否有更新
check_repo_updates() {
    local repo_dir="$1"
    local repo_name="$(basename "$repo_dir")"
    
    echo -e "${YELLOW}检查仓库: $repo_name${NC}"
    
    # 检查是否为 git 仓库
    if [ ! -d "$repo_dir/.git" ]; then
        echo "  → 跳过 (不是 git 仓库)"
        return 1
    fi
    
    cd "$repo_dir"
    
    # 检查是否有远程仓库
    if ! git remote -v | grep -q "origin"; then
        echo "  → 跳过 (没有远程仓库)"
        return 1
    fi
    
    total_repos=$((total_repos + 1))
    
    # 获取当前分支
    local current_branch
    current_branch=$(get_current_branch "$repo_dir")
    
    if [ "$current_branch" = "unknown" ]; then
        echo "  → 跳过 (无法确定当前分支)"
        return 1
    fi
    
    # 检查是否有对应的远程分支
    if ! git ls-remote --heads origin "$current_branch" | grep -q "$current_branch"; then
        echo "  → 跳过 (远程没有对应分支: $current_branch)"
        return 1
    fi
    
    # 获取远程更新（带重试）
    local fetch_attempt=1
    while [ $fetch_attempt -le $MAX_RETRIES ]; do
        if git fetch origin "$current_branch" >/dev/null 2>&1; then
            break
        fi
        if [ $fetch_attempt -lt $MAX_RETRIES ]; then
            echo "  → 获取远程更新失败，${RETRY_DELAY} 秒后重试 ($((MAX_RETRIES - fetch_attempt)) 次剩余)..."
            sleep $RETRY_DELAY
        else
            errors+=("$repo_name: 无法获取远程更新 (已重试 $MAX_RETRIES 次)")
            echo "  → 错误: 无法获取远程更新"
            return 1
        fi
        fetch_attempt=$((fetch_attempt + 1))
    done
    
    # 检查是否有更新
    local commits_behind
    commits_behind=$(git rev-list HEAD..origin/"$current_branch" --count 2>/dev/null || echo "0")
    
    if [ "$commits_behind" -gt 0 ]; then
        echo -e "  → ${GREEN}发现 $commits_behind 个新提交${NC}"
        
        # 获取将要更新的文件列表
        local updated_files
        updated_files=$(git diff --name-only HEAD origin/"$current_branch" 2>/dev/null || echo "")
        
        # 检查是否包含 requirements.txt
        if echo "$updated_files" | grep -q "requirements.txt"; then
            repos_with_requirements+=("$repo_name|$repo_dir")
            echo "    → 包含 requirements.txt 更新"
        fi
        
        repos_to_update+=("$repo_name|$repo_dir")
        return 0
    else
        echo "  → 已是最新版本"
        return 1
    fi
}

# 函数: 执行仓库更新（带重试）
update_repo() {
    local repo_name="$1"
    local repo_dir="$2"
    
    echo -e "${BLUE}更新仓库: $repo_name${NC}"
    
    cd "$repo_dir"
    
    # 获取当前分支
    local current_branch
    current_branch=$(get_current_branch "$repo_dir")
    
    # 执行 git pull（带重试）
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        if git pull origin "$current_branch"; then
            echo -e "  → ${GREEN}更新成功${NC}"
            updated_repos=$((updated_repos + 1))
            return 0
        fi
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo -e "  → ${YELLOW}第 $attempt 次失败，${RETRY_DELAY} 秒后重试 ($((MAX_RETRIES - attempt)) 次剩余)...${NC}"
            sleep $RETRY_DELAY
        fi
        attempt=$((attempt + 1))
    done
    
    local error_msg="git pull 失败 (已重试 $MAX_RETRIES 次)"
    errors+=("$repo_name: $error_msg")
    echo -e "  → ${RED}更新失败: $error_msg${NC}"
    failed_repos=$((failed_repos + 1))
    return 1
}

# 函数: 更新依赖（带重试）
update_dependencies() {
    local repo_name="$1"
    local repo_dir="$2"
    local requirements_file="$repo_dir/requirements.txt"
    
    echo -e "${BLUE}更新依赖: $repo_name${NC}"
    
    if [ -f "$requirements_file" ]; then
        # 切换到主项目目录执行 uv add
        cd "$SCRIPT_DIR"
        
        # 执行 uv add（带重试）
        local attempt=1
        while [ $attempt -le $MAX_RETRIES ]; do
            if uv add -r "$requirements_file"; then
                echo -e "  → ${GREEN}依赖更新成功${NC}"
                requirements_updated=$((requirements_updated + 1))
                return 0
            fi
            if [ $attempt -lt $MAX_RETRIES ]; then
                echo -e "  → ${YELLOW}第 $attempt 次失败，${RETRY_DELAY} 秒后重试 ($((MAX_RETRIES - attempt)) 次剩余)...${NC}"
                sleep $RETRY_DELAY
            fi
            attempt=$((attempt + 1))
        done
        
        local error_msg="uv add 失败 (已重试 $MAX_RETRIES 次)"
        errors+=("$repo_name: $error_msg")
        echo -e "  → ${RED}依赖更新失败: $error_msg${NC}"
        return 1
    else
        echo "  → 跳过 (requirements.txt 不存在)"
        return 1
    fi
}

# 主逻辑开始

echo "开始扫描 custom_nodes 目录..."

# 遍历所有子目录
for dir in "$CUSTOM_NODES_DIR"/*; do
    if [ -d "$dir" ]; then
        check_repo_updates "$dir" || true  # 忽略函数返回的错误码
    fi
done

echo ""
echo -e "${BLUE}=== 扫描完成 ===${NC}"
echo "总仓库数: $total_repos"
echo "需要更新的仓库数: ${#repos_to_update[@]}"

# 如果没有需要更新的仓库，退出
if [ ${#repos_to_update[@]} -eq 0 ]; then
    echo -e "${GREEN}所有仓库都已是最新版本！${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}需要更新的仓库列表:${NC}"
for repo_info in "${repos_to_update[@]}"; do
    IFS='|' read -r repo_name repo_dir <<< "$repo_info"
    echo "  - $repo_name"
done

if [ ${#repos_with_requirements[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}包含 requirements.txt 更新的仓库:${NC}"
    for req_info in "${repos_with_requirements[@]}"; do
        IFS='|' read -r repo_name repo_dir <<< "$req_info"
        echo "  - $repo_name"
    done
fi

echo ""
read -p "是否继续执行更新？(y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "更新已取消"
    exit 0
fi

echo ""
echo -e "${BLUE}=== 开始更新 ===${NC}"

# 执行仓库更新
for repo_info in "${repos_to_update[@]}"; do
    IFS='|' read -r repo_name repo_dir <<< "$repo_info"
    update_repo "$repo_name" "$repo_dir"
    echo ""
done

# 执行依赖更新
if [ ${#repos_with_requirements[@]} -gt 0 ]; then
    echo -e "${BLUE}=== 更新依赖 ===${NC}"
    for req_info in "${repos_with_requirements[@]}"; do
        IFS='|' read -r repo_name repo_dir <<< "$req_info"
        update_dependencies "$repo_name" "$repo_dir"
        echo ""
    done
fi

# 输出汇总信息
echo -e "${BLUE}=== 更新汇总 ===${NC}"
echo "总仓库数: $total_repos"
echo -e "更新成功: ${GREEN}$updated_repos${NC}"
echo -e "更新失败: ${RED}$failed_repos${NC}"
echo -e "依赖更新: ${GREEN}$requirements_updated${NC}"

# 输出错误信息
if [ ${#errors[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}=== 错误汇总 ===${NC}"
    for error in "${errors[@]}"; do
        echo "  - $error"
    done
fi

echo ""
if [ $failed_repos -eq 0 ] && [ ${#errors[@]} -eq 0 ]; then
    echo -e "${GREEN}所有更新都成功完成！${NC}"
    exit 0
else
    echo -e "${YELLOW}更新完成，但有一些错误，请检查上面的错误汇总。${NC}"
    exit 1
fi
