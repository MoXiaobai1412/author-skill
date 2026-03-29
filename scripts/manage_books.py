#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
书籍管理脚本
用法：
  python manage_books.py list {项目根目录}              # 列出所有书籍
  python manage_books.py select {书名} {项目根目录}    # 切换当前书
  python manage_books.py current {项目根目录}          # 显示当前书
"""

import os
import sys
import json
from pathlib import Path

BOOKS_INDEX_FILE = "书籍索引.json"
CURRENT_BOOK_FILE = "当前书.json"


def get_books_index(project_root):
    """获取书籍索引"""
    index_path = Path(project_root) / BOOKS_INDEX_FILE
    
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"books": []}


def save_books_index(project_root, index):
    """保存书籍索引"""
    index_path = Path(project_root) / BOOKS_INDEX_FILE
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_current_book(project_root):
    """获取当前书"""
    current_path = Path(project_root) / CURRENT_BOOK_FILE
    
    if current_path.exists():
        with open(current_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('current_book')
    return None


def set_current_book(project_root, book_name):
    """设置当前书"""
    current_path = Path(project_root) / CURRENT_BOOK_FILE
    
    data = {
        "current_book": book_name,
        "updated_at": __import__('datetime').datetime.now().isoformat()
    }
    
    with open(current_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_books(project_root):
    """列出所有书籍"""
    index = get_books_index(project_root)
    current = get_current_book(project_root)
    
    books = index.get('books', [])
    
    if not books:
        print("暂无书籍。请使用 /newbook {书名} 创建新书。")
        return
    
    print(f"\n{'='*60}")
    print("📚 书籍列表")
    print(f"{'='*60}\n")
    
    for i, book in enumerate(books, 1):
        marker = "👉" if book == current else "  "
        print(f"{marker} {i}. 《{book}》")
    
    print(f"\n共 {len(books)} 本书")
    
    if current:
        print(f"当前正在写作：《{current}》")
    else:
        print("\n⚠ 未选择当前书，请使用 /select {书名} 切换")
    
    print()


def select_book(project_root, book_name):
    """切换当前书"""
    index = get_books_index(project_root)
    books = index.get('books', [])
    
    # 检查书籍是否存在
    book_path = Path(project_root) / "库" / book_name
    
    if not book_path.exists():
        print(f"错误：未找到书籍《{book_name}》")
        print("请使用 /newbook {书名} 创建新书，或从以下书籍中选择：")
        list_books(project_root)
        return False
    
    # 如果书籍不在索引中，添加它
    if book_name not in books:
        books.append(book_name)
        index['books'] = books
        save_books_index(project_root, index)
    
    # 设置当前书
    set_current_book(project_root, book_name)
    
    print(f"✓ 已切换到《{book_name}》")
    print(f"  现在可以使用 /write 第 X 章 开始写作")
    
    return True


def add_book(project_root, book_name):
    """添加书籍到索引"""
    index = get_books_index(project_root)
    
    if book_name not in index.get('books', []):
        index.setdefault('books', []).append(book_name)
        save_books_index(project_root, index)
    
    set_current_book(project_root, book_name)


def remove_book(project_root, book_name):
    """从索引中移除书籍（不删除文件）"""
    index = get_books_index(project_root)
    books = index.get('books', [])
    
    if book_name in books:
        books.remove(book_name)
        index['books'] = books
        save_books_index(project_root, index)
        
        # 如果移除的是当前书，清除当前书设置
        current = get_current_book(project_root)
        if current == book_name:
            current_path = Path(project_root) / CURRENT_BOOK_FILE
            if current_path.exists():
                current_path.unlink()
        
        print(f"✓ 已从列表中移除《{book_name}》")
    else:
        print(f"错误：《{book_name}》不在书籍列表中")


def get_book_info(project_root, book_name):
    """获取书籍信息"""
    book_path = Path(project_root) / "库" / book_name
    
    if not book_path.exists():
        return None
    
    info = {
        'name': book_name,
        'path': str(book_path),
        'volumes': [],
        'total_chapters': 0,
        'written_chapters': 0,
    }
    
    # 扫描卷纲
    outline_path = book_path / "大纲库"
    if outline_path.exists():
        for f in outline_path.glob("*卷纲.md"):
            volume_name = f.stem.replace('卷纲', '')
            info['volumes'].append(volume_name)
    
    # 扫描正文
    text_path = book_path / "正文库"
    if text_path.exists():
        for volume_dir in text_path.iterdir():
            if volume_dir.is_dir():
                chapters = list(volume_dir.glob("*.md"))
                info['total_chapters'] += len(chapters)
                info['written_chapters'] += len(chapters)
    
    return info


def main():
    if len(sys.argv) < 3:
        print("用法：")
        print("  python manage_books.py list {项目根目录}")
        print("  python manage_books.py select {书名} {项目根目录}")
        print("  python manage_books.py current {项目根目录}")
        print("  python manage_books.py info {书名} {项目根目录}")
        sys.exit(1)
    
    action = sys.argv[1]
    project_root = sys.argv[-1]
    
    if action == "list":
        list_books(project_root)
    
    elif action == "select":
        if len(sys.argv) < 4:
            print("错误：请指定书名")
            print("用法：python manage_books.py select {书名} {项目根目录}")
            sys.exit(1)
        book_name = sys.argv[2]
        select_book(project_root, book_name)
    
    elif action == "current":
        current = get_current_book(project_root)
        if current:
            print(f"当前书：《{current}》")
        else:
            print("未选择当前书")
    
    elif action == "info":
        if len(sys.argv) < 4:
            print("错误：请指定书名")
            sys.exit(1)
        book_name = sys.argv[2]
        info = get_book_info(project_root, book_name)
        
        if info:
            print(f"\n《{info['name']}》信息：")
            print(f"  卷数：{len(info['volumes'])}")
            print(f"  已写章节：{info['written_chapters']}")
            print(f"  路径：{info['path']}")
        else:
            print(f"错误：未找到书籍《{book_name}》")
    
    else:
        print(f"未知操作：{action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
