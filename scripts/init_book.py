#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_book.py - 初始化书籍项目

用法：
  python init_book.py {书名} {项目根目录}

功能：
  1. 创建项目文件夹结构
  2. 初始化 SQLite 数据库
  3. 创建资源档案文件夹
  4. 创建基础文档（总纲、写作要求等）
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import ResourceDatabase


def create_project_structure(book_path: Path):
    """创建项目文件夹结构"""
    
    # 资源档案文件夹
    folders = [
        "资源库/人物库",
        "资源库/设定库",
        "资源库/场景库",
        "资源库/伏笔库",
        "资源库/历史库",
        "资源库/高潮库",
        "资源库/道具库",
        "正文",
        "大纲",
        "总结",
        "写作要求",
    ]
    
    for folder in folders:
        (book_path / folder).mkdir(parents=True, exist_ok=True)
    
    print(f"[OK] 创建文件夹结构")

def init_database(book_path: Path, book_name: str):
    """初始化数据库"""
    
    db_path = book_path / "source.db"
    
    # 检查是否已存在
    if db_path.exists():
        print(f"[INFO] 数据库已存在，跳过初始化")
        return None
    
    # 创建数据库
    db = ResourceDatabase(book_name)
    print(f"[OK] 创建数据库：source.db")
    
    # 显示统计
    stats = db.get_stats()
    print(f"[INFO] 数据库表结构已创建")
    
    return db

def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("  python init_book.py {书名}")
        print("示例：")
        print("  python init_book.py 未来救援局")
        sys.exit(1)

    project_root = os.path.expanduser("~") / ".books"
    book_name = sys.argv[1]
    book_path = project_root / book_name
    
    print(f"\n[初始化] 《{book_name}》项目\n")
    
    # 检查是否已存在
    if book_path.exists():
        print(f"[WARN] 项目文件夹已存在：{book_path}")
        print(f"是否继续？(y/n): ", end="")
        response = input().strip().lower()
        if response != 'y':
            print("[取消] 操作已取消")
            return
    
    # 1. 创建文件夹结构
    print("[1/2] 创建文件夹结构...")
    create_project_structure(book_path)
    
    # 2. 初始化数据库
    print("[2/2] 初始化数据库...")
    db = init_database(book_path, book_name)

    if db:
        db.close()
    
    # 完成
    print(f"\n[OK] 项目初始化完成！")
    print(f"位置：{book_path}")
    print(f"\n下一步选择：")
    print(f"  1. 编辑总纲")
    print(f"  2. 确定文笔风格")
    print(f"  3. 直接创作")


if __name__ == "__main__":
    main()
