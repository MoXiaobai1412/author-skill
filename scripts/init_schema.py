#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_schema.py - 为现有项目初始化所有 list.md 的 desc 部分

用法：
  python init_schema.py {书名} {项目根目录}
  python init_schema.py 仙途 D:/novel

功能：
  1. 扫描所有 list.md 文件
  2. 检查是否有 desc 部分
  3. 为没有 desc 的文件自动创建（使用预定义模板或智能推断）
  4. 备份原有文件
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


class SchemaInitializer:
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
        "概括": {
            "table_name": "概括索引",
            "columns": [
                ("volume", "text", "YES", "YES", "卷名", "第一卷：入道"),
                ("summary", "text", "NO", "YES", "卷概括", "主角从凡人到筑基"),
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
        self.backup_path = self.book_path.parent / f"{book_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def init_all(self):
        """初始化所有 list.md 的 desc 部分"""
        print(f"\n[INIT] 开始为《{self.book_name}》初始化 schema\n")
        
        # 备份现有文件
        self._backup()
        
        # 扫描所有 list.md
        list_files = self._scan_list_files()
        
        print(f"找到 {len(list_files)} 个 list.md 文件\n")
        
        # 逐个处理
        updated = 0
        skipped = 0
        
        for list_path in list_files:
            relative_path = list_path.relative_to(self.book_path)
            path_str = str(relative_path.parent).replace('\\', '/')
            
            # 检查是否已有 desc
            if self._has_desc(list_path):
                print(f"[SKIP] {path_str} - 已有 desc，跳过")
                skipped += 1
                continue
            
            # 创建 desc
            if self._create_desc(list_path, path_str):
                print(f"[OK] {path_str} - desc 已创建")
                updated += 1
            else:
                print(f"[WARN] {path_str} - 创建失败")
        
        print(f"\n[OK] 初始化完成！")
        print(f"   更新：{updated} 个文件")
        print(f"   跳过：{skipped} 个文件")
        print(f"   备份：{self.backup_path}")
    
    def _backup(self):
        """备份现有文件"""
        if self.book_path.exists():
            shutil.copytree(self.book_path, self.backup_path)
            print(f"[BACKUP] 已备份到：{self.backup_path}\n")
    
    def _scan_list_files(self):
        """扫描所有 list.md 文件"""
        list_files = []
        
        for root, dirs, files in os.walk(self.book_path):
            if "list.md" in files:
                list_files.append(Path(root) / "list.md")
        
        return list_files
    
    def _has_desc(self, list_path):
        """检查 list.md 是否有 desc 部分"""
        content = self._read_file(list_path)
        return "## desc" in content
    
    def _create_desc(self, list_path, path_str):
        """为 list.md 创建 desc 部分"""
        content = self._read_file(list_path)
        
        # 查找匹配的模板
        template = None
        for template_path, tmpl in self.SCHEMA_TEMPLATES.items():
            if path_str == template_path or path_str.endswith("/" + template_path):
                template = tmpl
                break
        
        # 如果没有精确匹配，尝试模糊匹配
        if not template:
            template = self._infer_schema(path_str, content)
        
        if not template:
            # 使用默认模板
            template = {
                "table_name": f"{path_str.replace('/', ' > ')} 索引",
                "columns": [
                    ("name", "text", "YES", "YES", "名称", "示例"),
                    ("summary", "text", "NO", "YES", "概括", "示例概括"),
                    ("extra", "text", "NO", "NO", "额外信息", "示例"),
                ]
            }
        
        # 生成 desc 部分
        desc_content = self._generate_desc(template["table_name"], template["columns"])
        
        # 插入到文件开头
        new_content = desc_content + "\n\n" + content
        
        # 保存
        self._save_file(list_path, new_content)
        return True
    
    def _infer_schema(self, path_str, content):
        """根据路径和内容推断 schema"""
        # 根据路径关键词推断
        if "人物" in path_str:
            return self.SCHEMA_TEMPLATES["资源库/人物库"]
        elif "设定" in path_str:
            return self.SCHEMA_TEMPLATES["资源库/设定库"]
        elif "伏笔" in path_str:
            return self.SCHEMA_TEMPLATES["资源库/伏笔库"]
        elif "高光" in path_str:
            return self.SCHEMA_TEMPLATES["资源库/高光库"]
        elif "历史" in path_str:
            return self.SCHEMA_TEMPLATES["资源库/历史库"]
        elif "大纲" in path_str:
            # 检查是卷索引还是章索引
            if "第一卷" in path_str or "第二卷" in path_str:
                return {
                    "table_name": f"{path_str.split('/')[-1]}章纲索引",
                    "columns": [
                        ("chapter", "text", "YES", "YES", "章名", "第一章"),
                        ("summary", "text", "NO", "YES", "章概括", "灭门"),
                        ("status", "text", "NO", "YES", "状态", "未开始/写作中/已完成"),
                    ]
                }
            else:
                return self.SCHEMA_TEMPLATES["大纲"]
        elif "概括" in path_str:
            if "第一卷" in path_str or "第二卷" in path_str:
                return {
                    "table_name": f"{path_str.split('/')[-1]}章概括索引",
                    "columns": [
                        ("chapter", "text", "YES", "YES", "章名", "第一章"),
                        ("summary", "text", "NO", "YES", "章概括", "灭门"),
                        ("status", "text", "NO", "YES", "状态", "未完成/已完成"),
                    ]
                }
            else:
                return self.SCHEMA_TEMPLATES["概括"]
        
        # 根据现有表格列数推断
        lines = content.split('\n')
        for line in lines:
            if line.startswith('| ') and line.count('|') >= 4:
                col_count = line.count('|') - 1
                
                if col_count == 3:
                    return {
                        "table_name": f"{path_str.replace('/', ' > ')} 索引",
                        "columns": [
                            ("name", "text", "YES", "YES", "名称", "示例"),
                            ("summary", "text", "NO", "YES", "概括", "示例"),
                            ("extra", "text", "NO", "NO", "额外信息", "示例"),
                        ]
                    }
                elif col_count == 4:
                    return {
                        "table_name": f"{path_str.replace('/', ' > ')} 索引",
                        "columns": [
                            ("name", "text", "YES", "YES", "名称", "示例"),
                            ("summary", "text", "NO", "YES", "概括", "示例"),
                            ("extra", "text", "NO", "NO", "额外信息", "示例"),
                            ("chapter", "text", "NO", "NO", "章节", "第一卷第 1 章"),
                        ]
                    }
        
        return None
    
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
    if len(sys.argv) < 3:
        print("用法：")
        print("  python init_schema.py {书名} {项目根目录}")
        print()
        print("示例：")
        print("  python init_schema.py 仙途 D:/novel")
        print()
        print("功能：")
        print("  1. 扫描所有 list.md 文件")
        print("  2. 检查是否有 desc 部分")
        print("  3. 为没有 desc 的文件自动创建（使用预定义模板或智能推断）")
        print("  4. 备份原有文件到带时间戳的备份文件夹")
        sys.exit(1)
    
    book_name = sys.argv[1]
    project_root = sys.argv[2]
    
    initializer = SchemaInitializer(book_name, project_root)
    initializer.init_all()


if __name__ == "__main__":
    main()
