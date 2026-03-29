#!/usr/bin/env python3
"""测试资源库查询功能"""

import sys
sys.path.insert(0, 'scripts')

from resource_manager import ResourceManager

# 测试参数
book_name = "未来救援局"
project_root = r"C:\Users\LLxy\.openclaw\workspace\books"
lib_name = "人物库"

print(f"\n=== 测试资源库查询 ===")
print(f"书名：{book_name}")
print(f"项目根目录：{project_root}")
print(f"库名：{lib_name}\n")

# 创建管理器
manager = ResourceManager(book_name, project_root)

# 测试 1: 查看 schema
print("[测试 1] 查看 desc 结构")
columns = manager.get_schema(lib_name)
if columns:
    print(f"[OK] desc 读取成功，共{len(columns)}列")
    for col in columns[:4]:  # 只显示前 4 列
        print(f"  - {col['name']}: {col['description']}")
else:
    print("[FAIL] desc 读取失败")

print()

# 测试 2: 列出资源
print("[测试 2] 列出所有人物")
entries = manager.list_resources(lib_name)
if entries:
    print(f"[OK] 资源列表读取成功，共{len(entries)}个资源")
    # 显示前 5 个
    for entry in entries[:5]:
        name = entry.get('name', 'Unknown')
        summary = entry.get('summary', '')[:30]
        chapter = entry.get('chapter', '')
        print(f"  - {name}: {summary}... (出现：{chapter})")
else:
    print("[FAIL] 资源列表读取失败")

print()

# 测试 3: 搜索资源
print("[测试 3] 搜索关键词")
keyword = "林"  # 搜索包含"林"的人物
results = manager.search(lib_name, keyword)
if results:
    print(f"[OK] 搜索成功，找到{len(results)}个匹配")
    for r in results[:3]:
        name = r.get('name', 'Unknown')
        summary = r.get('summary', '')[:30]
        print(f"  - {name}: {summary}...")
else:
    print("[FAIL] 搜索失败或未找到匹配")

print()

# 测试 4: 读取具体档案
print("[测试 4] 读取人物档案")
# 尝试读取第一个人物
if entries:
    first_char = entries[0]['name'].replace(' ⭐', '').replace(' ', '')
    print(f"尝试读取：{first_char}.md")
    content = manager.get(lib_name, first_char)
    if content:
        print(f"[OK] 档案读取成功，前 200 字:")
        print(content[:200])
    else:
        print("[FAIL] 档案读取失败")

print("\n=== 测试完成 ===\n")
