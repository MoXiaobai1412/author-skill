#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
schema_manager.py - 管理 list.md 的 desc 部分（类似 MySQL 的 DESCRIBE）

用法：
  python schema_manager.py desc {书名} {项目根目录} {路径}
  python schema_manager.py create {书名} {项目根目录} {路径} {表名} --columns "列1:类型：主键：必填：说明"
  python schema_manager.py update {书名} {项目根目录} {路径} --add "列名：类型：主键：必填：说明"
  python schema_manager.py update {书名} {项目根目录} {路径} --remove "列名"

路径示例：
  - 资源库
  - 资源库/人物库
  - 大纲
  - 大纲/第一卷
"""

import os
import sys
from pathlib import Path
from datetime import datetime


class SchemaManager:
    # 预定义 schema 模板
    SCHEMA_TEMPLATES = {
        "资源库": {
            "table_name": "资源库索引",
            "columns": [
                ("sub_lib", "text", "YES", "YES", "子库名称", "人物库"),
                ("purpose", "text", "NO", "YES", "子库作用", "存储所有角色设定"),
                ("usage", "text", "NO", "YES", "调用时机", "写作前查阅人物关系"),
            ]
        },
        "资源库/人物库": {
            "table_name": "人物库索引",
            "columns": [
                ("name", "text", "YES", "YES", "资源名（重要资源加⭐）", "林远 ⭐"),
                ("summary", "text", "NO", "YES", "资源概况", "主角，少年，坚毅"),
                ("relations", "text", "NO", "NO", "相关资源", "清风（救命恩人）"),
                ("chapter", "text", "NO", "NO", "首次出现章节", "第一卷第 1 章"),
            ]
        },
        "资源库/设定库": {
            "table_name": "设定库索引",
            "columns": [
                ("name", "text", "YES", "YES", "设定名（重要设定加⭐）", "青云宗 ⭐"),
                ("summary", "text", "NO", "YES", "设定概况", "主角所在宗门，正道大派"),
                ("relations", "text", "NO", "NO", "相关设定", "修仙体系"),
                ("chapter", "text", "NO", "NO", "首次出现章节", "第一卷第 1 章"),
            ]
        },
        "资源库/伏笔库": {
            "table_name": "伏笔库索引",
            "columns": [
                ("name", "text", "YES", "YES", "伏笔名", "飘荡的窗帘"),
                ("summary", "text", "NO", "YES", "伏笔描述", "黑衣人身上的特殊标记"),
                ("status", "text", "NO", "YES", "状态", "未揭露/已揭露/已废弃"),
                ("plan_chapter", "text", "NO", "NO", "计划揭露章节", "第二卷第 5 章"),
                ("actual_chapter", "text", "NO", "NO", "实际揭露章节", ""),
            ]
        },
        "资源库/高光库": {
            "table_name": "高光库索引",
            "columns": [
                ("name", "text", "YES", "YES", "高光场景名", "五台山大战"),
                ("summary", "text", "NO", "YES", "场景概况", "主角越级战斗，一举成名"),
                ("chapter", "text", "NO", "YES", "所在章节", "第一卷第 10 章"),
                ("type", "text", "NO", "NO", "类型", "战斗/情感/反转/成长"),
            ]
        },
        "资源库/历史库": {
            "table_name": "历史库索引",
            "columns": [
                ("name", "text", "YES", "YES", "历史事件名", "第一次企业战争"),
                ("summary", "text", "NO", "YES", "事件概况", "三大企业混战，持续十年"),
                ("time", "text", "NO", "NO", "发生时间", "新历 50-60 年"),
                ("impact", "text", "NO", "NO", "影响", "世界格局重塑"),
            ]
        },
        "大纲": {
            "table_name": "大纲索引",
            "columns": [
                ("volume", "text", "YES", "YES", "卷名", "第一卷：入道"),
                ("summary", "text", "NO", "YES", "卷概括", "主角踏上修仙之路"),
                ("status", "text", "NO", "YES", "状态", "未开始/写作中/已完成"),
            ]
        },
        "大纲/第一卷": {
            "table_name": "第一卷章纲索引",
            "columns": [
                ("chapter", "text", "YES", "YES", "章名", "第一章：灭门"),
                ("summary", "text", "NO", "YES", "章概括", "林府被灭，林远逃生"),
                ("status", "text", "NO", "YES", "状态", "未开始/写作中/已完成"),
            ]
        },
        "概括": {
            "table_name": "概括索引",
            "columns": [
                ("volume", "text", "YES", "YES", "卷名", "第一卷：入道"),
                ("summary", "text", "NO", "YES", "卷概括", "主角从凡人到筑基"),
                ("status", "text", "NO", "YES", "状态", "未完成/已完成"),
            ]
        },
        "概括/第一卷": {
            "table_name": "第一卷章概括索引",
            "columns": [
                ("chapter", "text", "YES", "YES", "章名", "第一章：灭门"),
                ("summary", "text", "NO", "YES", "章概括", "林府被灭，林远逃生"),
                ("status", "text", "NO", "YES", "状态", "未完成/已完成"),
            ]
        },
        "写作要求": {
            "table_name": "写作要求索引",
            "columns": [
                ("file", "text", "YES", "YES", "文件名", "文笔.md"),
                ("purpose", "text", "NO", "YES", "作用", "语言风格要求"),
                ("usage", "text", "NO", "YES", "调用时机", "写作时参考"),
            ]
        },
    }
    
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / book_name
    
    def get_list_path(self, path):
        """获取 list.md 路径"""
        return self.book_path / path / "list.md"
    
    def desc(self, path):
        """读取并显示 desc 部分（类似 MySQL DESCRIBE）"""
        list_path = self.get_list_path(path)
        
        if not list_path.exists():
            print(f"错误：{path}/list.md 不存在")
            return None
        
        content = self._read_file(list_path)
        desc_content = self._extract_desc(content)
        
        if not desc_content:
            print(f"⚠ {path}/list.md 没有 desc 部分")
            print("\n提示：使用以下命令创建 desc 部分：")
            print(f"  python schema_manager.py create {self.book_name} {self.project_root} {path}")
            return None
        
        print(f"\n## {path}/list.md - Schema\n")
        print(desc_content)
        return desc_content
    
    def create(self, path, table_name=None, columns=None):
        """创建 list.md 的 desc 部分"""
        list_path = self.get_list_path(path)
        
        # 使用预定义模板或自定义
        if path in self.SCHEMA_TEMPLATES:
            template = self.SCHEMA_TEMPLATES[path]
            table_name = table_name or template["table_name"]
            columns = columns or template["columns"]
        else:
            # 默认模板
            table_name = table_name or f"{path.replace('/', ' > ')} 索引"
            columns = columns or [
                ("name", "text", "YES", "YES", "名称", "示例"),
                ("summary", "text", "NO", "YES", "概括", "示例概括"),
                ("extra", "text", "NO", "NO", "额外信息", "示例"),
            ]
        
        # 生成 desc 部分
        desc_content = self._generate_desc(table_name, columns)
        
        # 检查文件是否存在
        if list_path.exists():
            content = self._read_file(list_path)
            # 如果已有 desc，询问是否覆盖
            if "## desc" in content:
                print(f"⚠ {path}/list.md 已存在 desc 部分")
                print("是否覆盖？(y/n): ", end="")
                # 非交互模式下默认不覆盖
                print("n (非交互模式，跳过覆盖)")
                return False
            
            # 在文件开头插入 desc
            new_content = desc_content + "\n" + content
        else:
            # 创建新文件
            data_header = self._generate_data_header(columns)
            new_content = desc_content + "\n" + data_header
        
        self._save_file(list_path, new_content)
        print(f"✓ 已创建 {path}/list.md 的 desc 部分")
        print(f"  表名：{table_name}")
        print(f"  列数：{len(columns)}")
        return True
    
    def update(self, path, add_column=None, remove_column=None):
        """更新 desc 部分"""
        list_path = self.get_list_path(path)
        
        if not list_path.exists():
            print(f"错误：{path}/list.md 不存在")
            return False
        
        content = self._read_file(list_path)
        
        if add_column:
            # 添加列
            col_parts = add_column.split(":")
            if len(col_parts) < 5:
                print("错误：列格式应为 '列名：类型：主键：必填：说明'")
                return False
            
            col_name = col_parts[0]
            col_type = col_parts[1] if len(col_parts) > 1 else "text"
            is_pk = col_parts[2] if len(col_parts) > 2 else "NO"
            is_required = col_parts[3] if len(col_parts) > 3 else "NO"
            description = col_parts[4] if len(col_parts) > 4 else ""
            example = col_parts[5] if len(col_parts) > 5 else ""
            
            # 添加到 desc
            content = self._add_column_to_desc(content, col_name, col_type, is_pk, is_required, description, example)
            
            # 添加到 data 表格
            content = self._add_column_to_data(content, col_name)
            
            print(f"✓ 已添加列：{col_name}")
        
        if remove_column:
            # 移除列
            content = self._remove_column_from_desc(content, remove_column)
            content = self._remove_column_from_data(content, remove_column)
            print(f"✓ 已移除列：{remove_column}")
        
        self._save_file(list_path, content)
        return True
    
    def _generate_desc(self, table_name, columns):
        """生成 desc 部分内容"""
        lines = [
            f"# {table_name}",
            "",
            "## desc",
            "| 列名 | 类型 | 主键 | 必填 | 说明 | 示例 |",
            "|------|------|------|------|------|------|",
        ]
        
        for col in columns:
            name, col_type, is_pk, is_required, desc, example = col
            lines.append(f"| {name} | {col_type} | {is_pk} | {is_required} | {desc} | {example} |")
        
        return "\n".join(lines)
    
    def _generate_data_header(self, columns):
        """生成 data 部分表头"""
        # 从列定义生成友好的列名
        friendly_names = {
            "name": "资源名",
            "summary": "资源概况",
            "relations": "相关资源",
            "chapter": "出现章节",
            "sub_lib": "子库名",
            "purpose": "作用",
            "usage": "调用时机",
            "status": "状态",
            "plan_chapter": "计划揭露章节",
            "actual_chapter": "实际揭露章节",
            "time": "时间",
            "impact": "影响",
            "volume": "卷名",
            "file": "文件名",
            "type": "类型",
            "extra": "额外信息",
        }
        
        headers = []
        for col in columns:
            col_name = col[0]
            headers.append(friendly_names.get(col_name, col_name))
        
        lines = [
            "",
            "## data",
            "| " + " | ".join(headers) + " |",
            "|" + "|".join(["------" for _ in headers]) + "|",
        ]
        
        return "\n".join(lines)
    
    def _extract_desc(self, content):
        """提取 desc 部分"""
        lines = content.split('\n')
        desc_lines = []
        in_desc = False
        
        for line in lines:
            if line.startswith("## desc"):
                in_desc = True
                continue
            if in_desc:
                if line.startswith("## "):
                    break
                desc_lines.append(line)
        
        if desc_lines:
            return "## desc\n" + "\n".join(desc_lines)
        return None
    
    def _add_column_to_desc(self, content, col_name, col_type, is_pk, is_required, desc, example):
        """在 desc 中添加列"""
        lines = content.split('\n')
        new_line = f"| {col_name} | {col_type} | {is_pk} | {is_required} | {desc} | {example} |"
        
        for i, line in enumerate(lines):
            if line.startswith("## desc"):
                # 找到表头后的分隔线
                for j in range(i+1, len(lines)):
                    if lines[j].startswith("|------"):
                        lines.insert(j+1, new_line)
                        break
                break
        
        return "\n".join(lines)
    
    def _add_column_to_data(self, content, col_name):
        """在 data 表格中添加列"""
        lines = content.split('\n')
        in_data = False
        
        for i, line in enumerate(lines):
            if line.startswith("## data"):
                in_data = True
                continue
            
            if in_data and line.startswith("| "):
                # 添加新列（空值）
                if line.count("|") >= 2:
                    # 在最后一个 | 前插入
                    parts = line.rstrip().split("|")
                    parts.insert(-1, " ")
                    lines[i] = "|".join(parts) + " |"
        
        return "\n".join(lines)
    
    def _remove_column_from_desc(self, content, col_name):
        """从 desc 中移除列"""
        lines = content.split('\n')
        in_desc = False
        
        new_lines = []
        for line in lines:
            if line.startswith("## desc"):
                in_desc = True
            elif line.startswith("## "):
                in_desc = False
            
            if in_desc and line.startswith("| ") and f"| {col_name} |" in line:
                continue  # 跳过要删除的列
            
            new_lines.append(line)
        
        return "\n".join(new_lines)
    
    def _remove_column_from_data(self, content, col_name):
        """从 data 表格中移除列（简化实现，实际需要更复杂的逻辑）"""
        # 这里简化处理，实际需要根据列位置移除
        return content
    
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
        print("  python schema_manager.py desc {书名} {项目根目录} {路径}")
        print("  python schema_manager.py create {书名} {项目根目录} {路径} [表名]")
        print("  python schema_manager.py update {书名} {项目根目录} {路径} --add '列名：类型：主键：必填：说明'")
        print("  python schema_manager.py update {书名} {项目根目录} {路径} --remove '列名'")
        print()
        print("预定义路径会自动使用模板：")
        print("  - 资源库")
        print("  - 资源库/人物库")
        print("  - 资源库/设定库")
        print("  - 资源库/伏笔库")
        print("  - 资源库/高光库")
        print("  - 资源库/历史库")
        print("  - 大纲")
        print("  - 大纲/第一卷")
        print("  - 概括")
        print("  - 概括/第一卷")
        print("  - 写作要求")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    path = sys.argv[4]
    
    manager = SchemaManager(book_name, project_root)
    
    if action == "desc":
        manager.desc(path)
    
    elif action == "create":
        table_name = sys.argv[5] if len(sys.argv) > 5 else None
        manager.create(path, table_name)
    
    elif action == "update":
        if len(sys.argv) < 6:
            print("错误：请提供 --add 或 --remove 参数")
            sys.exit(1)
        
        if sys.argv[5] == "--add":
            if len(sys.argv) < 7:
                print("错误：请提供列定义 '列名：类型：主键：必填：说明'")
                sys.exit(1)
            col_def = sys.argv[6]
            manager.update(path, add_column=col_def)
        
        elif sys.argv[5] == "--remove":
            if len(sys.argv) < 7:
                print("错误：请提供列名")
                sys.exit(1)
            col_name = sys.argv[6]
            manager.update(path, remove_column=col_name)
        
        else:
            print(f"错误：未知参数 '{sys.argv[5]}'")
            sys.exit(1)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
