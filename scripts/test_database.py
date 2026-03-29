#!/usr/bin/env python3
"""测试 SQLite 数据库功能"""

import sys
sys.path.insert(0, 'scripts')

from database import ResourceDatabase

print("\n=== SQLite 数据库测试 ===\n")

# 测试参数
book_name = "未来救援局"
project_root = r"C:\Users\LLxy\.openclaw\workspace\books"

print(f"书名：{book_name}")
print(f"项目根目录：{project_root}\n")

# 创建数据库连接
db = ResourceDatabase(book_name, project_root)

# 测试 1: 数据库统计
print("[测试 1] 数据库统计")
stats = db.get_stats()
for table, count in stats.items():
    print(f"  {table}: {count} 条记录")
print()

# 测试 2: 获取重要人物
print("[测试 2] 获取重要人物")
important = db.get_important_characters()
print(f"  重要人物数量：{len(important)}")
for char in important[:5]:
    print(f"    - {char['name']}: {char['summary'][:30]}")
print()

# 测试 3: 搜索人物
print("[测试 3] 搜索人物（关键词：林）")
results = db.search('characters', '林')
print(f"  找到：{len(results)}个")
for r in results[:3]:
    print(f"    - {r['name']}: {r['summary'][:30]}")
print()

# 测试 4: 获取未揭露伏笔
print("[测试 4] 获取未揭露伏笔")
vows = db.get_active_foreshadowing()
print(f"  未揭露伏笔：{len(vows)}个")
for vow in vows[:3]:
    print(f"    - {vow['name']}: {vow['summary'][:30]} (状态：{vow['status']})")
print()

# 测试 5: 获取人物关系
print("[测试 5] 获取人物关系")
if important:
    first_char = important[0]['name'].replace(' ⭐', '')
    relations = db.get_relations_for_character(first_char)
    print(f"  {first_char} 的关系：{len(relations)}个")
    for rel in relations[:3]:
        print(f"    - {rel['char_a']} ↔ {rel['char_b']}: {rel['relation_type']}")
print()

# 测试 6: 按章节搜索
print("[测试 6] 按章节搜索（第 1 章）")
chapter_chars = db.search_chapter('characters', '第 1 章')
print(f"  第 1 章出场人物：{len(chapter_chars)}个")
for char in chapter_chars[:5]:
    print(f"    - {char['name']}: {char['chapter']}")
print()

db.close()

print("=== 测试完成 ===\n")
