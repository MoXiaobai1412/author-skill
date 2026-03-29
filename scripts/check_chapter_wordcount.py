#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_chapter_wordcount.py - 检查章节字数

用法：
  python check_chapter_wordcount.py {章节文件路径}
  python check_chapter_wordcount.py --all {书籍路径}
  python check_chapter_wordcount.py {章节文件路径} {最小字数}
"""

import os
import sys
import re
from pathlib import Path


def count_chinese_words(text):
    """统计中文字数（只统计汉字）"""
    # 移除所有空白字符
    text = re.sub(r'\s+', '', text)
    # 统计汉字
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars)


def check_file(file_path, min_words=3000):
    """检查单个文件字数"""
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在：{file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    word_count = count_chinese_words(content)
    status = "✅" if word_count >= min_words else "❌"
    
    print(f"{status} {os.path.basename(file_path)}: {word_count}字", end='')
    
    if word_count < min_words:
        print(f" (不足{min_words}字，差{min_words - word_count}字)")
        return False
    else:
        print()
        return True


def check_all_chapters(book_path, min_words=3000):
    """检查书籍所有章节"""
    print(f"\n📊 检查《{os.path.basename(book_path)}》所有章节字数\n")
    
    zhengwen_path = book_path / "正文"
    if not zhengwen_path.exists():
        print(f"❌ 正文文件夹不存在：{zhengwen_path}")
        return
    
    total = 0
    passed = 0
    failed = 0
    
    # 遍历所有章节
    for root, dirs, files in os.walk(zhengwen_path):
        if "正文.md" in files:
            total += 1
            file_path = Path(root) / "正文.md"
            if check_file(file_path, min_words):
                passed += 1
            else:
                failed += 1
    
    print(f"\n总计：{total}章 | 通过：{passed}章 | 不足：{failed}章")
    
    if failed > 0:
        print(f"\n⚠ 有{failed}章字数不足，需要扩充")
        print("提示：使用 references/content-expansion.md 的扩充技巧")


def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("  python check_chapter_wordcount.py {章节文件路径}")
        print("  python check_chapter_wordcount.py --all {书籍路径}")
        print("  python check_chapter_wordcount.py {章节文件路径} {最小字数}")
        print()
        print("示例：")
        print("  python check_chapter_wordcount.py books/未来救援局/正文/第一卷/第 01 章/正文.md")
        print("  python check_chapter_wordcount.py --all books/未来救援局")
        print("  python check_chapter_wordcount.py books/未来救援局/正文/第一卷/第 01 章/正文.md 3500")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        if len(sys.argv) < 3:
            print("错误：请提供书籍路径")
            sys.exit(1)
        
        book_path = Path(sys.argv[2])
        min_words = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
        check_all_chapters(book_path, min_words)
    else:
        file_path = Path(sys.argv[1])
        min_words = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
        check_file(file_path, min_words)


if __name__ == "__main__":
    main()
