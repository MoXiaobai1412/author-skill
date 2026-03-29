#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 提交工具
用法：
  python git_commit.py commit {书名} {项目根目录} {提交信息}
  python git_commit.py status {书名} {项目根目录}
  python git_commit.py push {书名} {项目根目录}
  python git_commit.py log {书名} {项目根目录} [数量]
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def run_git_command(args, cwd, capture=True):
    """运行 Git 命令"""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=capture,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if capture:
            print(f"Git 错误：{e.stderr}")
        return None
    except FileNotFoundError:
        print("错误：未找到 git 命令。请确保已安装 Git。")
        return None


def git_init(project_root):
    """初始化 Git 仓库"""
    git_dir = Path(project_root) / '.git'
    
    if git_dir.exists():
        return False  # 已存在
    
    # 创建.gitignore
    ignore_path = Path(project_root) / '.gitignore'
    with open(ignore_path, 'w', encoding='utf-8') as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# 临时文件
*.tmp
*.bak
*.log

# 编辑器
.vscode/
.idea/
*.swp
*.swo
*~

# 系统文件
.DS_Store
Thumbs.db

# 进度文件（可选）
进度.json
""")
    
    # 初始化仓库
    result = run_git_command(['init'], project_root)
    if result is not None:
        print("✓ Git 仓库已初始化")
        return True
    
    return False


def git_add(project_root, path='.'):
    """添加文件到暂存区"""
    result = run_git_command(['add', path], project_root)
    if result is not None:
        return True
    return False


def git_commit(project_root, message):
    """执行 Git 提交"""
    # 检查是否有更改
    status = run_git_command(['status', '--short'], project_root)
    
    if not status:
        print("没有需要提交的更改。")
        return False
    
    print(f"以下文件将被提交：\n{status}\n")
    
    # 执行提交
    result = run_git_command(['commit', '-m', message], project_root)
    
    if result:
        print(f"✓ git commit 完成：{message}")
        print(result)
        return True
    else:
        print("Git 提交失败。")
        return False


def git_push(project_root, remote='origin', branch='main'):
    """推送到远程仓库"""
    print(f"正在推送到 {remote}/{branch}...")
    
    result = run_git_command(['push', remote, branch], project_root, capture=False)
    
    if result is not None:
        print("✓ git push 完成")
        return True
    else:
        print("Git push 失败。请检查远程仓库配置。")
        return False


def git_status(project_root):
    """获取 Git 状态"""
    result = run_git_command(['status'], project_root)
    
    if result:
        print(result)
        return result
    return None


def git_log(project_root, count=5):
    """查看提交历史"""
    result = run_git_command(['log', f'-{count}', '--oneline'], project_root)
    
    if result:
        print(f"最近 {count} 次提交：\n")
        print(result)
        return result
    return None


def git_diff(project_root):
    """查看未提交的更改"""
    result = run_git_command(['diff'], project_root)
    
    if result:
        print("未提交的更改：\n")
        print(result)
        return result
    return None


def setup_remote(project_root, remote_url, remote_name='origin'):
    """配置远程仓库"""
    # 检查是否已有远程
    current = run_git_command(['remote', 'get-url', remote_name], project_root)
    
    if current:
        print(f"当前远程仓库：{current}")
        response = input("是否覆盖？(y/n): ")
        if response.lower() != 'y':
            return False
    
    # 添加/更新远程
    result = run_git_command(['remote', 'set-url', remote_name, remote_url], project_root)
    
    if not result:
        # 可能是新远程
        result = run_git_command(['remote', 'add', remote_name, remote_url], project_root)
    
    if result is not None:
        print(f"✓ 远程仓库已配置：{remote_name} -> {remote_url}")
        return True
    
    return False


def create_branch(project_root, branch_name):
    """创建新分支"""
    result = run_git_command(['checkout', '-b', branch_name], project_root)
    
    if result is not None:
        print(f"✓ 已创建并切换到分支：{branch_name}")
        return True
    else:
        print("创建分支失败。")
        return False


def switch_branch(project_root, branch_name):
    """切换分支"""
    result = run_git_command(['checkout', branch_name], project_root)
    
    if result is not None:
        print(f"✓ 已切换到分支：{branch_name}")
        return True
    else:
        print("切换分支失败。")
        return False


def get_current_branch(project_root):
    """获取当前分支"""
    result = run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'], project_root)
    return result


def main():
    if len(sys.argv) < 4:
        print("用法：")
        print("  python git_commit.py commit {书名} {项目根目录} {提交信息}")
        print("  python git_commit.py status {书名} {项目根目录}")
        print("  python git_commit.py push {书名} {项目根目录}")
        print("  python git_commit.py log {书名} {项目根目录} [数量]")
        print("  python git_commit.py init {书名} {项目根目录}")
        print("  python git_commit.py remote {书名} {项目根目录} {远程 URL}")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    
    # 检查 Git 仓库
    git_dir = Path(project_root) / '.git'
    
    if action == "init":
        git_init(project_root)
        return
    
    if not git_dir.exists():
        print("错误：未找到 Git 仓库。请先运行 init 或创建新书。")
        return
    
    if action == "commit":
        if len(sys.argv) < 5:
            print("错误：请提供提交信息")
            sys.exit(1)
        message = sys.argv[4]
        git_add(project_root)
        git_commit(project_root, message)
    
    elif action == "status":
        git_status(project_root)
    
    elif action == "push":
        branch = get_current_branch(project_root)
        if branch:
            print(f"当前分支：{branch}")
            git_push(project_root, branch=branch)
    
    elif action == "log":
        count = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        git_log(project_root, count)
    
    elif action == "diff":
        git_diff(project_root)
    
    elif action == "remote":
        if len(sys.argv) < 5:
            print("错误：请提供远程仓库 URL")
            sys.exit(1)
        remote_url = sys.argv[4]
        setup_remote(project_root, remote_url)
    
    elif action == "branch":
        if len(sys.argv) < 5:
            branch = get_current_branch(project_root)
            if branch:
                print(f"当前分支：{branch}")
        else:
            branch_name = sys.argv[4]
            create_branch(project_root, branch_name)
    
    elif action == "checkout":
        if len(sys.argv) < 5:
            print("错误：请提供分支名")
            sys.exit(1)
        branch_name = sys.argv[4]
        switch_branch(project_root, branch_name)
    
    else:
        print(f"未知操作：{action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
