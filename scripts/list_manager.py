#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
list.md 索引管理脚本（支持 MySQL 风格 desc）

用法：
  python list_manager.py read {书名} {项目根目录} {路径}
  python list_manager.py add {书名} {项目根目录} {路径} {名称} {概括} {状态/相关资源}
  python list_manager.py del {书名} {项目根目录} {路径} {名称}
  python list_manager.py update {书名} {项目根目录} {路径} {名称} {新概括} {新状态}
  python list_manager.py search {书名} {项目根目录} {路径} {关键词}
  python list_manager.py sync {书名} {项目根目录} {路径}
  python list_manager.py schema {书名} {项目根目录} {路径}  # 查看 desc

路径示例：
  - 资源库
  - 资源库/人物库
  - 正文
  - 大纲
  - 大纲/第一卷
  - 概括
  - 概括/第一卷
  - 写作要求

list.md 结构：
  ## desc  - 元数据区，定义列名、类型、主键等（类似 MySQL DESCRIBE）
  ## data  - 数据区，实际资源列表
"""

import os
import sys
from pathlib import Path


class ListManager:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / book_name
    
    def get_list_path(self, path):
        """获取 list.md 路径"""
        return self.book_path / path / "list.md"
    
    def get_folder_path(self, path):
        """获取文件夹路径"""
        return self.book_path / path
    
    def get_schema(self, path):
        """获取 list.md 的 desc 部分（schema 定义）"""
        list_path = self.get_list_path(path)
        
        if not list_path or not list_path.exists():
            return None
        
        content = self._read_file(list_path)
        return self._parse_desc(content)
    
    def _parse_desc(self, content):
        """解析 desc 部分，返回列定义"""
        lines = content.split('\n')
        columns = []
        in_desc = False
        
        for line in lines:
            if line.startswith("## desc"):
                in_desc = True
                continue
            if in_desc:
                if line.startswith("## "):
                    break
                if line.startswith("| ") and "列名" not in line and "|------" not in line:
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 5:
                        columns.append({
                            'name': parts[0],
                            'type': parts[1],
                            'primary_key': parts[2],
                            'required': parts[3],
                            'description': parts[4],
                            'example': parts[5] if len(parts) > 5 else '',
                        })
        
        return columns if columns else None
    
    def read_list(self, path):
        """读取 list.md"""
        list_path = self.get_list_path(path)
        
        if not list_path.exists():
            print(f"错误：{path}/list.md 不存在")
            return []
        
        content = self._read_file(list_path)
        entries = []
        
        # 解析表格
        lines = content.split('\n')
        for line in lines:
            if line.startswith('| ') and line.count('|') >= 4:
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 3:
                    entries.append({
                        'name': parts[0],
                        'summary': parts[1],
                        'extra': parts[2],  # 状态或相关资源
                    })
        
        return entries
    
    def add_entry(self, path, name, summary="", extra=""):
        """添加条目到 list.md"""
        list_path = self.get_list_path(path)
        
        if not list_path.exists():
            print(f"错误：{path}/list.md 不存在")
            return False
        
        content = self._read_file(list_path)
        
        # 检查是否已存在
        if self._entry_exists(content, name):
            print(f"⚠ 条目'{name}'已存在")
            return False
        
        # 找到表格最后一行前插入
        lines = content.split('\n')
        new_line = f"| {name} | {summary} | {extra} |"
        
        # 找到表格开始位置
        insert_pos = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('|----'):
                insert_pos = i + 1
                break
        
        lines.insert(insert_pos, new_line)
        
        self._save_file(list_path, '\n'.join(lines))
        print(f"✓ 已添加：{name}")
        return True
    
    def del_entry(self, path, name):
        """从 list.md 删除条目"""
        list_path = self.get_list_path(path)
        
        if not list_path.exists():
            print(f"错误：{path}/list.md 不存在")
            return False
        
        content = self._read_file(list_path)
        
        lines = content.split('\n')
        new_lines = [l for l in lines if not l.startswith(f'| {name} |')]
        
        if len(new_lines) == len(lines):
            print(f"错误：条目'{name}'不存在")
            return False
        
        self._save_file(list_path, '\n'.join(new_lines))
        print(f"✓ 已删除：{name}")
        return True
    
    def update_entry(self, path, name, new_summary=None, new_extra=None):
        """更新 list.md 中的条目"""
        list_path = self.get_list_path(path)
        
        if not list_path.exists():
            print(f"错误：{path}/list.md 不存在")
            return False
        
        content = self._read_file(list_path)
        
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith(f'| {name} |'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                
                if new_summary is not None and len(parts) >= 2:
                    parts[1] = new_summary
                if new_extra is not None and len(parts) >= 3:
                    parts[2] = new_extra
                
                lines[i] = '| ' + ' | '.join(parts) + ' |'
                updated = True
                break
        
        if updated:
            self._save_file(list_path, '\n'.join(lines))
            print(f"✓ 已更新：{name}")
        else:
            print(f"错误：条目'{name}'不存在")
        
        return updated
    
    def search(self, path, keyword):
        """搜索 list.md"""
        entries = self.read_list(path)
        
        results = []
        for entry in entries:
            if (keyword.lower() in entry['name'].lower() or
                keyword.lower() in entry['summary'].lower() or
                keyword.lower() in entry['extra'].lower()):
                results.append(entry)
        
        return results
    
    def sync(self, path):
        """同步 list.md 与实际文件/文件夹"""
        list_path = self.get_list_path(path)
        
        if not list_path.exists():
            print(f"错误：{path}/list.md 不存在")
            return False
        
        folder_path = self.get_folder_path(path)
        
        # 获取实际子文件夹/文件
        actual_items = set()
        
        # 检查是文件还是文件夹
        for item in folder_path.iterdir():
            if item.name == "list.md":
                continue
            if item.is_file() and item.suffix == '.md':
                actual_items.add(item.stem)
            elif item.is_dir():
                actual_items.add(item.name)
        
        # 获取 list.md 中的条目
        entries = self.read_list(path)
        list_names = set(e['name'] for e in entries if e['name'].strip())
        
        # 找出差异
        missing_in_list = actual_items - list_names
        missing_in_files = list_names - actual_items
        
        if not missing_in_list and not missing_in_files:
            print(f"✓ {path} 已同步")
            return True
        
        # 添加缺失的条目
        for name in sorted(missing_in_list):
            self.add_entry(path, name, "（待补充概括）", "（待补充）")
            print(f"  + 添加：{name}")
        
        # 删除不存在的条目
        for name in sorted(missing_in_files):
            self.del_entry(path, name)
            print(f"  - 删除：{name}")
        
        print(f"✓ {path} 同步完成")
        return True
    
    def print_list(self, path, title=None):
        """打印 list.md 内容（支持 desc 格式）"""
        entries = self.read_list(path)
        columns = self.get_schema(path)
        
        if not entries:
            print(f"{path} 暂无条目")
            return
        
        display_title = title or path.replace('/', ' > ')
        print(f"\n## {display_title}索引\n")
        
        if columns:
            # 根据 desc 显示列名
            headers = [col['name'] for col in columns]
            print("| " + " | ".join(headers) + " |")
            print("|" + "|".join(["------" for _ in headers]) + "|")
            
            for entry in entries:
                row_values = [entry.get(col['name'], '') for col in columns]
                print("| " + " | ".join(row_values) + " |")
        else:
            # 兼容旧格式
            print("| 名称 | 概括 | 状态/相关资源 |")
            print("|------|------|---------------|")
            
            for entry in entries:
                if entry.get('name', '').strip():
                    print(f"| {entry['name']} | {entry['summary']} | {entry['extra']} |")
        
        print(f"\n共 {len([e for e in entries if e.get('name', '').strip()])} 个条目\n")
    
    # ========== 辅助方法 ==========
    
    def _entry_exists(self, content, name):
        """检查条目是否存在"""
        for line in content.split('\n'):
            if line.startswith(f'| {name} |'):
                return True
        return False
    
    def _read_file(self, path):
        """读取文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def _save_file(self, path, content):
        """保存文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    if len(sys.argv) < 5:
        print("用法：")
        print("  python list_manager.py read {书名} {项目根目录} {路径}")
        print("  python list_manager.py add {书名} {项目根目录} {路径} {名称} {概括} {状态/相关资源}")
        print("  python list_manager.py del {书名} {项目根目录} {路径} {名称}")
        print("  python list_manager.py update {书名} {项目根目录} {路径} {名称} {新概括} {新状态}")
        print("  python list_manager.py search {书名} {项目根目录} {路径} {关键词}")
        print("  python list_manager.py sync {书名} {项目根目录} {路径}")
        print("  python list_manager.py schema {书名} {项目根目录} {路径}  # 查看 desc")
        print()
        print("路径示例：")
        print("  - 资源库")
        print("  - 资源库/人物库")
        print("  - 正文")
        print("  - 大纲")
        print("  - 大纲/第一卷")
        print("  - 概括")
        print("  - 概括/第一卷")
        print("  - 写作要求")
        print()
        print("list.md 结构：")
        print("  ## desc  - 元数据区，定义列名、类型、主键等（类似 MySQL DESCRIBE）")
        print("  ## data  - 数据区，实际资源列表")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    path = sys.argv[4]
    
    manager = ListManager(book_name, project_root)
    
    # schema 命令 - 查看 desc
    if action == "schema":
        columns = manager.get_schema(path)
        if columns:
            print(f"\n## {path}/list.md Schema\n")
            print("| 列名 | 类型 | 主键 | 必填 | 说明 | 示例 |")
            print("|------|------|------|------|------|------|")
            for col in columns:
                print(f"| {col['name']} | {col['type']} | {col['primary_key']} | {col['required']} | {col['description']} | {col['example']} |")
            print()
        else:
            print(f"⚠ {path}/list.md 没有 desc 部分")
            print("\n提示：使用 schema_manager.py 创建 desc：")
            print(f"  python schema_manager.py create {book_name} {project_root} {path}")
        return
    
    if action == "read":
        manager.print_list(path)
    
    elif action == "add":
        if len(sys.argv) < 8:
            print("错误：请提供名称、概括、状态/相关资源")
            sys.exit(1)
        name = sys.argv[5]
        summary = sys.argv[6]
        extra = sys.argv[7]
        manager.add_entry(path, name, summary, extra)
    
    elif action == "del":
        if len(sys.argv) < 6:
            print("错误：请提供名称")
            sys.exit(1)
        name = sys.argv[5]
        manager.del_entry(path, name)
    
    elif action == "update":
        if len(sys.argv) < 7:
            print("错误：请提供名称和新概括")
            sys.exit(1)
        name = sys.argv[5]
        new_summary = sys.argv[6]
        new_extra = sys.argv[7] if len(sys.argv) > 7 else None
        manager.update_entry(path, name, new_summary, new_extra)
    
    elif action == "search":
        if len(sys.argv) < 6:
            print("错误：请提供关键词")
            sys.exit(1)
        keyword = sys.argv[5]
        results = manager.search(path, keyword)
        
        if results:
            print(f"\n## {path}搜索结果：'{keyword}'\n")
            print("| 名称 | 概括 | 状态/相关资源 |")
            print("|------|------|---------------|")
            for r in results:
                print(f"| {r['name']} | {r['summary']} | {r['extra']} |")
            print(f"\n共 {len(results)} 个结果\n")
        else:
            print(f"在{path}中未找到匹配 '{keyword}' 的条目")
    
    elif action == "sync":
        manager.sync(path)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
