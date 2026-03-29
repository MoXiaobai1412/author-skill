#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
写作要求管理脚本
用法：
  python requirement_manager.py add {书名} {项目根目录} {文件名} [标题]
  python requirement_manager.py edit {书名} {项目根目录} {文件名}
  python requirement_manager.py del {书名} {项目根目录} {文件名}
  python requirement_manager.py list {书名} {项目根目录}
  python requirement_manager.py get {书名} {项目根目录} {文件名}
"""

import os
import sys
from pathlib import Path


class RequirementManager:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / "库" / book_name
        self.req_path = self.book_path / "写作要求"
    
    def add(self, filename, title=""):
        """添加写作要求"""
        if not filename.endswith('.md'):
            filename += '.md'
        
        req_file = self.req_path / filename
        
        if req_file.exists():
            print(f"⚠ 文件'{filename}'已存在")
            return False
        
        # 创建文件
        content = self._create_requirement_template(filename.replace('.md', ''), title)
        self._save_file(req_file, content)
        
        # 更新 list.md
        list_path = self.req_path / "list.md"
        self._add_to_list(list_path, filename, title or f"{filename.replace('.md', '')}要求", "写作时参考")
        
        print(f"✓ 写作要求'{filename}'已添加")
        print(f"  文件：写作要求/{filename}")
        print(f"  索引：写作要求/list.md 已更新")
        return True
    
    def edit(self, filename):
        """编辑写作要求"""
        if not filename.endswith('.md'):
            filename += '.md'
        
        req_file = self.req_path / filename
        
        if not req_file.exists():
            print(f"错误：文件'{filename}'不存在")
            return None
        
        content = self._read_file(req_file)
        print(f"## 写作要求/{filename}\n")
        print(content)
        print("\n提示：请使用文本编辑器修改后保存")
        return content
    
    def del_requirement(self, filename):
        """删除写作要求"""
        if not filename.endswith('.md'):
            filename += '.md'
        
        req_file = self.req_path / filename
        
        if not req_file.exists():
            print(f"错误：文件'{filename}'不存在")
            return False
        
        # 删除文件
        req_file.unlink()
        
        # 从 list.md 移除
        list_path = self.req_path / "list.md"
        self._remove_from_list(list_path, filename)
        
        print(f"✓ 写作要求'{filename}'已删除")
        return True
    
    def list_requirements(self):
        """列出所有写作要求"""
        list_path = self.req_path / "list.md"
        
        if not list_path.exists():
            print("写作要求/list.md 不存在")
            return []
        
        entries = self._read_list(list_path)
        
        if not entries:
            print("写作要求 暂无条目")
            return []
        
        print(f"\n## 写作要求列表（《{self.book_name}》）\n")
        print("| 文件名 | 作用 | 调用时机 |")
        print("|--------|------|----------|")
        
        for entry in entries:
            if entry['name'].strip():
                print(f"| {entry['name']} | {entry['summary']} | {entry['extra']} |")
        
        print(f"\n共 {len([e for e in entries if e['name'].strip()])} 个要求\n")
        return entries
    
    def get(self, filename):
        """获取写作要求详情"""
        if not filename.endswith('.md'):
            filename += '.md'
        
        req_file = self.req_path / filename
        
        if not req_file.exists():
            print(f"错误：文件'{filename}'不存在")
            return None
        
        content = self._read_file(req_file)
        print(f"\n## 写作要求/{filename}\n")
        print(content)
        return content
    
    def _create_requirement_template(self, name, title=""):
        """创建写作要求模板"""
        templates = {
            "文笔": self._create_writing_style_template,
            "对话风格": self._create_dialogue_style_template,
            "叙事视角": self._create_pov_template,
            "节奏控制": self._create_pacing_template,
            "描写规范": self._create_description_template,
        }
        
        creator = templates.get(name, self._create_custom_template)
        return creator(name if not title else title)
    
    def _create_writing_style_template(self, title):
        return f"""# {title}

## 语言风格
- 整体风格：（如：简洁/华丽/幽默/严肃）
- 叙事视角：（如：第三人称限知/全知）
- 描写重点：（如：动作/心理/环境）

## 禁用表达
- （列出不推荐的词汇或表达）

## 特殊要求
- （其他个性化要求）
"""
    
    def _create_dialogue_style_template(self, title):
        return f"""# {title}

## 整体风格
- （如：现代/古风/简洁/详细）

## 人物对话特点
| 人物类型 | 对话特点 |
|----------|----------|
| 主角 | |
| 配角 | |

## 禁用表达
- （列出不推荐的对话表达）

## 特殊要求
- （如：方言使用、称呼规范等）
"""
    
    def _create_pov_template(self, title):
        return f"""# {title}

## 主要视角
- （如：主角视角、多视角切换）

## 视角切换规则
- （何时可以切换视角）

## 注意事项
- （避免视角混乱的规则）
"""
    
    def _create_pacing_template(self, title):
        return f"""# {title}

## 节奏要求
- （如：张弛有度、高潮密集）

## 章节长度
- 平均每章字数：
- 最短/最长限制：

## 高潮分布
- （如：每 3 章一个小高潮，每 10 章一个大高潮）
"""
    
    def _create_description_template(self, title):
        return f"""# {title}

## 环境描写
- （描写规范和重点）

## 人物描写
- （外貌、动作、心理描写规范）

## 战斗描写
- （如有，战斗场景的描写规范）

## 禁用套路
- （列出避免的描写套路）
"""
    
    def _create_custom_template(self, title):
        return f"""# {title}

## 要求内容


## 示例


## 注意事项

"""
    
    def _add_to_list(self, list_path, name, summary="", extra=""):
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
    
    def _remove_from_list(self, list_path, name):
        content = self._read_file(list_path)
        
        lines = content.split('\n')
        new_lines = [l for l in lines if not l.startswith(f'| {name} |')]
        
        if len(new_lines) == len(lines):
            return False
        
        self._save_file(list_path, '\n'.join(new_lines))
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
    if len(sys.argv) < 5:
        print("用法：")
        print("  python requirement_manager.py add {书名} {项目根目录} {文件名} [标题]")
        print("  python requirement_manager.py edit {书名} {项目根目录} {文件名}")
        print("  python requirement_manager.py del {书名} {项目根目录} {文件名}")
        print("  python requirement_manager.py list {书名} {项目根目录}")
        print("  python requirement_manager.py get {书名} {项目根目录} {文件名}")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    
    manager = RequirementManager(book_name, project_root)
    
    if action == "add":
        filename = sys.argv[4]
        title = sys.argv[5] if len(sys.argv) > 5 else ""
        manager.add(filename, title)
    
    elif action == "edit":
        filename = sys.argv[4]
        manager.edit(filename)
    
    elif action == "del":
        filename = sys.argv[4]
        manager.del_requirement(filename)
    
    elif action == "list":
        manager.list_requirements()
    
    elif action == "get":
        filename = sys.argv[4]
        manager.get(filename)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
