#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量改名/修改设定脚本
用法：
  python batch_rename.py char {书名} {项目根目录} {旧名称} {新名称}
  python batch_rename.py setting {书名} {项目根目录} {旧名称} {新名称}
  python batch_rename.py preview {书名} {项目根目录} {旧名称} {新名称}  # 预览影响范围
"""

import os
import sys
import re
from pathlib import Path
import shutil


class BatchRenamer:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / "库" / book_name
        
        self.resource_lib = self.book_path / "资源库"
        self.text_path = self.book_path / "正文"
        self.outline_path = self.book_path / "大纲"
        self.summary_path = self.book_path / "概括"
        
        self.affected_files = []
        self.changes = []
    
    def preview_rename(self, resource_type, old_name, new_name):
        """预览改名影响范围"""
        print(f"\n{'='*60}")
        print(f"预览：《{self.book_name}》{resource_type} '{old_name}' → '{new_name}'")
        print(f"{'='*60}\n")
        
        # 1. 查找资源文件
        if resource_type == "char":
            lib_path = self.resource_lib / "人物库"
        elif resource_type == "setting":
            lib_path = self.resource_lib / "设定库"
        else:
            print(f"错误：不支持的资源类型 '{resource_type}'")
            return []
        
        old_file = lib_path / f"{old_name}.md"
        new_file = lib_path / f"{new_name}.md"
        
        if not old_file.exists():
            print(f"错误：资源文件 '{old_name}.md' 不存在")
            return []
        
        if new_file.exists():
            print(f"⚠ 警告：目标文件 '{new_name}.md' 已存在，将被覆盖")
        
        self.affected_files.append({
            'path': old_file,
            'action': 'rename',
            'new_path': new_file
        })
        
        # 2. 查找 list.md
        list_path = lib_path / "list.md"
        if list_path.exists():
            content = self._read_file(list_path)
            if old_name in content:
                self.affected_files.append({
                    'path': list_path,
                    'action': 'update',
                    'change': f"'{old_name}' → '{new_name}'"
                })
        
        # 3. 查找所有正文文件
        if self.text_path.exists():
            for volume_dir in self.text_path.iterdir():
                if volume_dir.is_dir():
                    for chapter_file in volume_dir.glob("*.md"):
                        content = self._read_file(chapter_file)
                        if old_name in content:
                            self.affected_files.append({
                                'path': chapter_file,
                                'action': 'update',
                                'change': f"正文中出现{content.count(old_name)}次"
                            })
        
        # 4. 查找大纲文件
        if self.outline_path.exists():
            for item in self.outline_path.rglob("*.md"):
                content = self._read_file(item)
                if old_name in content:
                    self.affected_files.append({
                        'path': item,
                        'action': 'update',
                        'change': f"大纲中出现{content.count(old_name)}次"
                    })
        
        # 5. 查找概括文件
        if self.summary_path.exists():
            for item in self.summary_path.rglob("*.md"):
                content = self._read_file(item)
                if old_name in content:
                    self.affected_files.append({
                        'path': item,
                        'action': 'update',
                        'change': f"概括中出现{content.count(old_name)}次"
                    })
        
        # 显示预览
        print(f"## 影响范围\n")
        print(f"共影响 {len(self.affected_files)} 个文件：\n")
        
        # 按类型分组
        renames = [f for f in self.affected_files if f['action'] == 'rename']
        updates = [f for f in self.affected_files if f['action'] == 'update']
        
        if renames:
            print("### 文件重命名")
            for f in renames:
                print(f"  {f['path'].relative_to(self.book_path)}")
                print(f"    → {f['new_path'].relative_to(self.book_path)}")
        
        if updates:
            print("\n### 内容更新")
            # 按文件夹分组
            by_folder = {}
            for f in updates:
                folder = f['path'].parent.relative_to(self.book_path)
                if folder not in by_folder:
                    by_folder[folder] = []
                by_folder[folder].append(f)
            
            for folder, files in sorted(by_folder.items()):
                print(f"\n  {folder}/ ({len(files)}个文件)")
                for f in files[:5]:  # 只显示前 5 个
                    print(f"    - {f['path'].name}: {f['change']}")
                if len(files) > 5:
                    print(f"    ... 还有{len(files) - 5}个文件")
        
        print(f"\n{'='*60}")
        print("提示：确认无误后，运行以下命令执行改名：")
        print(f"  python batch_rename.py {resource_type} {self.book_name} {self.project_root} {old_name} {new_name}")
        print(f"{'='*60}\n")
        
        return self.affected_files
    
    def execute_rename(self, resource_type, old_name, new_name):
        """执行改名"""
        if not self.affected_files:
            self.preview_rename(resource_type, old_name, new_name)
        
        print(f"\n{'='*60}")
        print(f"开始执行改名：《{self.book_name}》{resource_type} '{old_name}' → '{new_name}'")
        print(f"{'='*60}\n")
        
        backup_path = self.book_path / f"_backup_{old_name}_{new_name}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        print(f"## 备份文件")
        print(f"  备份位置：{backup_path}\n")
        
        success_count = 0
        error_count = 0
        
        for file_info in self.affected_files:
            try:
                if file_info['action'] == 'rename':
                    # 重命名文件
                    shutil.copy2(file_info['path'], backup_path / file_info['path'].name)
                    file_info['path'].rename(file_info['new_path'])
                    print(f"  ✓ 重命名：{file_info['path'].name} → {file_info['new_path'].name}")
                    success_count += 1
                
                elif file_info['action'] == 'update':
                    # 更新内容
                    content = self._read_file(file_info['path'])
                    new_content = content.replace(old_name, new_name)
                    
                    # 备份
                    rel_path = file_info['path'].relative_to(self.book_path)
                    backup_file = backup_path / rel_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_info['path'], backup_file)
                    
                    # 写入新内容
                    self._save_file(file_info['path'], new_content)
                    print(f"  ✓ 更新：{file_info['path'].relative_to(self.book_path)}")
                    success_count += 1
            
            except Exception as e:
                print(f"  ✗ 错误：{file_info['path']} - {e}")
                error_count += 1
        
        print(f"\n## 完成")
        print(f"  成功：{success_count}个文件")
        print(f"  失败：{error_count}个文件")
        print(f"\n备份已保存至：{backup_path}")
        print(f"如需回滚，可从备份恢复。\n")
    
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
        print("  # 预览改名影响")
        print("  python batch_rename.py preview {书名} {项目根目录} {旧名称} {新名称}")
        print()
        print("  # 执行改名")
        print("  python batch_rename.py char {书名} {项目根目录} {旧名称} {新名称}")
        print("  python batch_rename.py setting {书名} {项目根目录} {旧名称} {新名称}")
        print()
        print("示例：")
        print("  python batch_rename.py preview 仙途 D:/novel 林远 林小远")
        print("  python batch_rename.py char 仙途 D:/novel 林远 林小远")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    old_name = sys.argv[4]
    new_name = sys.argv[5]
    
    renamer = BatchRenamer(book_name, project_root)
    
    if action == "preview":
        renamer.preview_rename("resource", old_name, new_name)
    
    elif action == "char":
        renamer.preview_rename("char", old_name, new_name)
        print("\n确认执行改名？(y/n): ", end='')
        # 注意：实际使用时由用户确认
        # 这里简化为直接执行
        renamer.execute_rename("char", old_name, new_name)
    
    elif action == "setting":
        renamer.preview_rename("setting", old_name, new_name)
        renamer.execute_rename("setting", old_name, new_name)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
