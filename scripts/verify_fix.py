#!/usr/bin/env python3
import os
from pathlib import Path

resource_lib = Path(r"C:\Users\LLxy\.openclaw\workspace\books\未来救援局\资源库")

print("\n=== 人物关系库检查 ===")
relations_path = resource_lib / "人物关系库"
if relations_path.exists():
    print("[OK] 人物关系库文件夹已创建")
    list_path = relations_path / "list.md"
    if list_path.exists():
        print("[OK] list.md 已创建")
        with open(list_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_desc = "## desc" in content
            print(f"{'[OK]' if has_desc else '[ERROR]'} list.md {'有' if has_desc else '没有'} desc 部分")
            # 显示前 20 行
            lines = content.split('\n')[:20]
            print("\n前 20 行内容:")
            for i, line in enumerate(lines, 1):
                print(f"{i:2}: {line}")
    else:
        print("[ERROR] list.md 不存在")
else:
    print("[ERROR] 人物关系库文件夹不存在")

print("\n=== 各库 list.md desc 检查 ===")

libs = ["人物库", "设定库", "场景库", "伏笔库", "历史库"]
for lib_name in libs:
    lib_path = resource_lib / lib_name
    if not lib_path.exists():
        print(f"[SKIP] {lib_name} 不存在")
        continue
    
    list_path = lib_path / "list.md"
    if not list_path.exists():
        print(f"[SKIP] {lib_name}/list.md 不存在")
        continue
    
    with open(list_path, 'r', encoding='utf-8') as f:
        content = f.read()
        has_desc = "## desc" in content
        print(f"{'[OK]' if has_desc else '[FIX]'} {lib_name}: {'有 desc' if has_desc else '无 desc'}")

print("\n=== 检查完成 ===\n")
