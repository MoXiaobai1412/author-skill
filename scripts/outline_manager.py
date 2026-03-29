#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大纲管理脚本
用法：
  python outline_manager.py add_volume {书名} {项目根目录} {卷名} {概括}
  python outline_manager.py add_chapter {书名} {项目根目录} {卷名} {章名} {概括}
  python outline_manager.py list {书名} {项目根目录} [路径]
  python outline_manager.py get {书名} {项目根目录} {卷名} [章名]
  python outline_manager.py update {书名} {项目根目录} {卷名} {章名} {新概括}
"""

import os
import sys
from pathlib import Path


class OutlineManager:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / "库" / book_name
        self.outline_path = self.book_path / "大纲"
    
    def add_volume(self, volume_name, summary):
        """添加卷纲"""
        volume_path = self.outline_path / volume_name
        volume_path.mkdir(parents=True, exist_ok=True)
        
        # 创建卷纲.md
        outline_file = volume_path / "卷纲.md"
        content = self._create_volume_outline_template(volume_name, summary)
        self._save_file(outline_file, content)
        
        # 更新大纲/list.md
        list_path = self.outline_path / "list.md"
        self._add_to_list(list_path, volume_name, summary, "未开始")
        
        # 创建卷的 list.md
        volume_list_path = volume_path / "list.md"
        self._create_chapter_list(volume_list_path, volume_name)
        
        print(f"✓ 卷纲'{volume_name}'已添加")
        print(f"  文件：大纲/{volume_name}/卷纲.md")
        print(f"  索引：大纲/list.md 已更新")
        return True
    
    def add_chapter(self, volume_name, chapter_name, summary):
        """添加章纲"""
        volume_path = self.outline_path / volume_name
        
        if not volume_path.exists():
            print(f"错误：卷'{volume_name}'不存在")
            return False
        
        # 创建章纲.md
        chapter_file = volume_path / f"{chapter_name}.md"
        content = self._create_chapter_outline_template(chapter_name, summary)
        self._save_file(chapter_file, content)
        
        # 更新卷/list.md
        list_path = volume_path / "list.md"
        self._add_to_list(list_path, chapter_name, summary, "未开始")
        
        print(f"✓ 章纲'{chapter_name}'已添加到{volume_name}")
        print(f"  文件：大纲/{volume_name}/{chapter_name}.md")
        print(f"  索引：大纲/{volume_name}/list.md 已更新")
        return True
    
    def list_outlines(self, path=""):
        """列出大纲"""
        if path:
            # 列出特定卷的章纲
            list_path = self.outline_path / path / "list.md"
            title = f"大纲/{path}"
        else:
            # 列出卷纲
            list_path = self.outline_path / "list.md"
            title = "大纲"
        
        if not list_path.exists():
            print(f"错误：{title}/list.md 不存在")
            return []
        
        entries = self._read_list(list_path)
        
        if not entries:
            print(f"{title} 暂无条目")
            return []
        
        print(f"\n## {title}索引\n")
        if path:
            print("| 章名 | 概括 | 状态 |")
            print("|------|------|------|")
        else:
            print("| 卷名 | 概括 | 状态 |")
            print("|------|------|------|")
        
        for entry in entries:
            if entry['name'].strip():
                print(f"| {entry['name']} | {entry['summary']} | {entry['extra']} |")
        
        print(f"\n共 {len([e for e in entries if e['name'].strip()])} 个条目\n")
        return entries
    
    def get_outline(self, volume_name, chapter_name=None):
        """获取大纲内容"""
        if chapter_name:
            # 获取章纲
            outline_file = self.outline_path / volume_name / f"{chapter_name}.md"
        else:
            # 获取卷纲
            outline_file = self.outline_path / volume_name / "卷纲.md"
        
        if not outline_file.exists():
            print(f"错误：大纲不存在")
            return None
        
        content = self._read_file(outline_file)
        print(f"\n## 大纲/{volume_name}" + (f"/{chapter_name}" if chapter_name else "/卷纲"))
        print(content)
        return content
    
    def update_outline(self, volume_name, chapter_name, new_summary):
        """更新大纲"""
        if chapter_name:
            # 更新章纲
            list_path = self.outline_path / volume_name / "list.md"
        else:
            # 更新卷纲
            list_path = self.outline_path / "list.md"
            chapter_name = volume_name
            volume_name = ""
        
        if not list_path.exists():
            print(f"错误：list.md 不存在")
            return False
        
        content = self._read_file(list_path)
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith(f'| {chapter_name} |'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 2:
                    parts[1] = new_summary
                    lines[i] = '| ' + ' | '.join(parts) + ' |'
                    updated = True
                    break
        
        if updated:
            self._save_file(list_path, '\n'.join(lines))
            print(f"✓ 已更新：{chapter_name}")
        else:
            print(f"错误：条目'{chapter_name}'不存在")
        
        return updated
    
    def _create_volume_outline_template(self, volume_name, summary):
        """创建卷纲模板"""
        return f"""# {volume_name}卷纲

## 本卷概括
{summary}

## 本卷章数
X 章（已写：0/X）

## 各章概览
| 章序 | 章名 | 一句话概括 | 状态 |
|------|------|------------|------|
| 第一章 | | | 未写 |
| 第二章 | | | 未写 |
| ... | ... | ... | ... |

## 本卷核心冲突
（简要说明本卷的主要矛盾、目标、结局走向等）

## 主要人物
| 人物 | 作用 | 状态变化 |
|------|------|----------|
| | | |

## 重要设定
| 设定 | 作用 |
|------|------|
| | |

## 伏笔处理
| 伏笔 ID | 操作 | 说明 |
|---------|------|------|
| | 铺设/回收 | |

"""
    
    def _create_chapter_outline_template(self, chapter_name, summary):
        """创建章纲模板"""
        return f"""# {chapter_name}章纲

## 本章概括
{summary}

## 核心事件
（本章核心事件描述）

## 出场人物
| 人物 | 作用 | 关键行为 |
|------|------|----------|
| | | |

## 关键场景
（场景梗概）

## 伏笔处理
| 伏笔 ID | 操作 | 说明 |
|---------|------|------|
| | 铺设/回收 | |

## 章节结尾
（结尾方式）

## 备注

"""
    
    def _create_chapter_list(self, list_path, volume_name):
        """创建卷的 list.md"""
        content = f"""# {volume_name}章纲索引

| 章名 | 概括 | 状态 |
|------|------|------|
| | | |

---
*使用 `/outline chapter add {volume_name} {{章名}} {{概括}}` 添加章纲*
*状态：未开始/写作中/已完成*
"""
        self._save_file(list_path, content)
    
    def _add_to_list(self, list_path, name, summary="", extra=""):
        """添加条目到 list.md"""
        content = self._read_file(list_path)
        
        if self._entry_exists(content, name):
            return False
        
        lines = content.split('\n')
        new_line = f"| {name} | {summary} | {extra} |"
        
        insert_pos = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('|----'):
                insert_pos = i + 1
                break
        
        lines.insert(insert_pos, new_line)
        
        self._save_file(list_path, '\n'.join(lines))
        return True
    
    def _entry_exists(self, content, name):
        """检查条目是否存在"""
        for line in content.split('\n'):
            if line.startswith(f'| {name} |'):
                return True
        return False
    
    def _read_list(self, list_path):
        """读取 list.md"""
        content = self._read_file(list_path)
        entries = []
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('| ') and line.count('|') >= 4:
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 3:
                    entries.append({
                        'name': parts[0],
                        'summary': parts[1],
                        'extra': parts[2],
                    })
        
        return entries
    
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
    if len(sys.argv) < 4:
        print("用法：")
        print("  python outline_manager.py add_volume {书名} {项目根目录} {卷名} {概括}")
        print("  python outline_manager.py add_chapter {书名} {项目根目录} {卷名} {章名} {概括}")
        print("  python outline_manager.py list {书名} {项目根目录} [路径]")
        print("  python outline_manager.py get {书名} {项目根目录} {卷名} [章名]")
        print("  python outline_manager.py update {书名} {项目根目录} {卷名} {章名} {新概括}")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    
    manager = OutlineManager(book_name, project_root)
    
    if action == "add_volume":
        if len(sys.argv) < 6:
            print("错误：请提供卷名和概括")
            sys.exit(1)
        volume_name = sys.argv[4]
        summary = sys.argv[5]
        manager.add_volume(volume_name, summary)
    
    elif action == "add_chapter":
        if len(sys.argv) < 7:
            print("错误：请提供卷名、章名和概括")
            sys.exit(1)
        volume_name = sys.argv[4]
        chapter_name = sys.argv[5]
        summary = sys.argv[6]
        manager.add_chapter(volume_name, chapter_name, summary)
    
    elif action == "list":
        path = sys.argv[4] if len(sys.argv) > 4 else ""
        manager.list_outlines(path)
    
    elif action == "get":
        if len(sys.argv) < 5:
            print("错误：请提供卷名")
            sys.exit(1)
        volume_name = sys.argv[4]
        chapter_name = sys.argv[5] if len(sys.argv) > 5 else None
        manager.get_outline(volume_name, chapter_name)
    
    elif action == "update":
        if len(sys.argv) < 7:
            print("错误：请提供卷名、章名和新概括")
            sys.exit(1)
        volume_name = sys.argv[4]
        chapter_name = sys.argv[5]
        new_summary = sys.argv[6]
        manager.update_outline(volume_name, chapter_name, new_summary)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
