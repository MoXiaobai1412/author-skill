#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_database.py - 初始化书籍数据库

用法：
  python init_database.py {书名} {项目根目录}

功能：
  1. 创建 source.db 数据库文件
  2. 创建所有表结构
  3. 从现有 list.md 导入数据（如有）
"""

import sys
import os
from pathlib import Path
from database import ResourceDatabase


def import_from_list_md(db, resource_lib_path):
    """从现有的 list.md 文件导入数据到数据库"""
    
    print("\n[导入] 从 list.md 导入数据...")
    
    # 映射表名和文件夹
    table_mapping = {
        '人物库': ('characters', '人物库'),
        '设定库': ('settings', '设定库'),
        '场景库': ('scenes', '场景库'),
        '伏笔库': ('foreshadowing', '伏笔库'),
        '历史库': ('history', '历史库'),
        '人物关系库': ('character_relations', '人物关系库'),
    }
    
    total_imported = 0
    
    for folder_name, (table, _) in table_mapping.items():
        lib_path = resource_lib_path / folder_name
        if not lib_path.exists():
            continue
        
        list_path = lib_path / "list.md"
        if not list_path.exists():
            continue
        
        print(f"  导入 {folder_name}...")
        
        # 读取 list.md
        with open(list_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 data 部分
        if '## data' not in content:
            print(f"    ⚠ 没有 data 部分，跳过")
            continue
        
        data_part = content.split('## data')[1]
        lines = data_part.strip().split('\n')
        
        # 跳过表头
        data_lines = [l for l in lines if l.startswith('| ') and '|------' not in l]
        
        imported = 0
        for line in data_lines:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) < 2:
                continue
            
            try:
                name = parts[0]
                summary = parts[1] if len(parts) > 1 else ''
                relations = parts[2] if len(parts) > 2 else ''
                chapter = parts[3] if len(parts) > 3 else ''
                
                # 检查是否重要
                is_important = 1 if '⭐' in name else 0
                
                # 插入数据库
                if table == 'characters':
                    db.add_character(name, summary, relations, chapter, is_important=bool(is_important))
                elif table == 'settings':
                    db.add_setting(name, summary, relations, chapter, is_important=bool(is_important))
                elif table == 'scenes':
                    db.add_scene(name, summary, relations, chapter)
                elif table == 'foreshadowing':
                    db.add_foreshadowing(name, summary, relations, chapter)
                elif table == 'history':
                    db.add('history', name, summary, relations, chapter)
                elif table == 'character_relations':
                    db.add_character_relation(name, parts[0], parts[1], summary)
                
                imported += 1
            except Exception as e:
                print(f"    ⚠ 导入失败：{name} - {e}")
        
        print(f"    导入 {imported} 条记录")
        total_imported += imported
    
    print(f"\n[完成] 共导入 {total_imported} 条记录")
    return total_imported


def main():
    if len(sys.argv) < 3:
        print("用法：")
        print("  python init_database.py {书名} {项目根目录}")
        print()
        print("示例：")
        print("  python init_database.py 未来救援局 C:\\Users\\LLxy\\.openclaw\\workspace\\books")
        sys.exit(1)
    
    book_name = sys.argv[1]
    project_root = Path(sys.argv[2])
    
    print(f"\n[初始化] 《{book_name}》数据库\n")
    
    # 创建数据库
    db_path = project_root / book_name / "source.db"
    print(f"数据库路径：{db_path}")
    
    # 检查是否已存在
    if db_path.exists():
        print(f"⚠ 数据库已存在，是否覆盖？(y/n): ", end="")
        response = input().strip().lower()
        if response != 'y':
            print("取消操作")
            return
        db_path.unlink()
        print("已删除旧数据库")
    
    # 初始化数据库
    print("创建数据库和表结构...")
    db = ResourceDatabase(book_name, project_root)
    
    # 导入现有数据
    resource_lib = project_root / book_name / "资源库"
    if resource_lib.exists():
        import_from_list_md(db, resource_lib)
    
    # 显示统计
    stats = db.get_stats()
    print("\n[数据库统计]")
    for table, count in stats.items():
        print(f"  {table}: {count} 条记录")
    
    db.close()
    print(f"\n[OK] 数据库初始化完成！")
    print(f"位置：{db_path}")


if __name__ == "__main__":
    main()
