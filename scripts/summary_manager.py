#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
概括管理脚本
用法：
  python summary_manager.py add_volume {书名} {项目根目录} {卷名} {概括}
  python summary_manager.py add_chapter {书名} {项目根目录} {卷名} {章名} {概括}
  python summary_manager.py list {书名} {项目根目录} [路径]
  python summary_manager.py get {书名} {项目根目录} {卷名} [章名]
"""

import os
import sys
from pathlib import Path


class SummaryManager:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / "库" / book_name
        self.summary_path = self.book_path / "概括"
    
    def add_volume_summary(self, volume_name, summary):
        """添加卷概括"""
        volume_path = self.summary_path / volume_name
        volume_path.mkdir(parents=True, exist_ok=True)
        
        # 创建卷概括.md
        summary_file = volume_path / "卷概括.md"
        content = self._create_volume_summary_template(volume_name, summary)
        self._save_file(summary_file, content)
        
        # 更新概括/list.md
        list_path = self.summary_path / "list.md"
        self._add_to_list(list_path, volume_name, summary, "已完成")
        
        # 创建卷的 list.md
        volume_list_path = volume_path / "list.md"
        self._create_chapter_list(volume_list_path, volume_name)
        
        print(f"✓ 卷概括'{volume_name}'已添加")
        print(f"  文件：概括/{volume_name}/卷概括.md")
        print(f"  索引：概括/list.md 已更新")
        return True
    
    def add_chapter_summary(self, volume_name, chapter_name, summary):
        """添加章概括"""
        volume_path = self.summary_path / volume_name
        chapter_path = volume_path / "章概括"
        chapter_path.mkdir(parents=True, exist_ok=True)
        
        # 创建章概括.md
        summary_file = chapter_path / f"{chapter_name}.md"
        content = self._create_chapter_summary_template(chapter_name, summary)
        self._save_file(summary_file, content)
        
        # 更新卷/章概括/list.md
        list_path = chapter_path / "list.md"
        self._add_to_list(list_path, chapter_name, summary, "已完成")
        
        print(f"✓ 章概括'{chapter_name}'已添加到{volume_name}")
        print(f"  文件：概括/{volume_name}/章概括/{chapter_name}.md")
        return True
    
    def list_summaries(self, path=""):
        """列出概括"""
        if path:
            list_path = self.summary_path / path / "list.md"
            title = f"概括/{path}"
        else:
            list_path = self.summary_path / "list.md"
            title = "概括"
        
        if not list_path.exists():
            print(f"错误：{title}/list.md 不存在")
            return []
        
        entries = self._read_list(list_path)
        
        if not entries:
            print(f"{title} 暂无条目")
            return []
        
        print(f"\n## {title}索引\n")
        print("| 名称 | 概括 | 状态 |")
        print("|------|------|------|")
        
        for entry in entries:
            if entry['name'].strip():
                print(f"| {entry['name']} | {entry['summary']} | {entry['extra']} |")
        
        print(f"\n共 {len([e for e in entries if e['name'].strip()])} 个条目\n")
        return entries
    
    def get_summary(self, volume_name, chapter_name=None):
        """获取概括内容"""
        if chapter_name:
            summary_file = self.summary_path / volume_name / "章概括" / f"{chapter_name}.md"
        else:
            summary_file = self.summary_path / volume_name / "卷概括.md"
        
        if not summary_file.exists():
            print(f"错误：概括不存在")
            return None
        
        content = self._read_file(summary_file)
        print(f"\n## 概括/{volume_name}" + (f"/章概括/{chapter_name}" if chapter_name else "/卷概括"))
        print(content)
        return content
    
    def _create_volume_summary_template(self, volume_name, summary):
        """创建卷概括模板"""
        return f"""# {volume_name}卷概括

## 整卷内容概括
{summary}

## 未揭露伏笔清单
| 伏笔 ID | 描述 | 铺设章节 | 预计揭露卷数 |
|---------|------|----------|--------------|
| | | | |

## 后续人物预估
| 人物 | 预计再次出现卷数 | 作用 |
|------|------------------|------|
| | | |

## 与下一卷衔接点
（本卷结尾如何引出下卷主线）

## 本卷大事记
| 章节 | 事件 |
|------|------|
| | |

## 备注

"""
    
    def _create_chapter_summary_template(self, chapter_name, summary):
        """创建章概括模板"""
        return f"""# {chapter_name}概括

## 本章内容
{summary}

## 新增人物
| 姓名 | 性别 | 特征 | 行为目的 | 性格 | 后续情节 | 与主角关系 | 暗藏伏笔 | 是否贯穿全文 |
|------|------|------|----------|------|----------|------------|----------|--------------|
| | | | | | | | | |

## 新增概念
| 名称 | 类型 | 简要描述 | 对本章的作用 | 是否贯穿全文 |
|------|------|----------|--------------|--------------|
| | | | | |

## 伏笔
| 伏笔 ID | 描述 | 首次出现 | 计划揭露方式 |
|--------|------|----------|--------------|
| | | 本章 | |

## 本章小结
（可选：作者备注、写作感受等）

"""
    
    def _create_chapter_list(self, list_path, volume_name):
        """创建卷的 list.md"""
        content = f"""# {volume_name}章概括索引

| 章名 | 概括 | 状态 |
|------|------|------|
| | | |

---
*章概括在章节完成后自动生成*
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
        for line in content.split('\n'):
            if line.startswith(f'| {name} |'):
                return True
        return False
    
    def _read_list(self, list_path):
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
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def _save_file(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    if len(sys.argv) < 4:
        print("用法：")
        print("  python summary_manager.py add_volume {书名} {项目根目录} {卷名} {概括}")
        print("  python summary_manager.py add_chapter {书名} {项目根目录} {卷名} {章名} {概括}")
        print("  python summary_manager.py list {书名} {项目根目录} [路径]")
        print("  python summary_manager.py get {书名} {项目根目录} {卷名} [章名]")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    
    manager = SummaryManager(book_name, project_root)
    
    if action == "add_volume":
        if len(sys.argv) < 6:
            print("错误：请提供卷名和概括")
            sys.exit(1)
        manager.add_volume_summary(sys.argv[4], sys.argv[5])
    
    elif action == "add_chapter":
        if len(sys.argv) < 7:
            print("错误：请提供卷名、章名和概括")
            sys.exit(1)
        manager.add_chapter_summary(sys.argv[4], sys.argv[5], sys.argv[6])
    
    elif action == "list":
        path = sys.argv[4] if len(sys.argv) > 4 else ""
        manager.list_summaries(path)
    
    elif action == "get":
        if len(sys.argv) < 5:
            print("错误：请提供卷名")
            sys.exit(1)
        volume_name = sys.argv[4]
        chapter_name = sys.argv[5] if len(sys.argv) > 5 else None
        manager.get_summary(volume_name, chapter_name)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
