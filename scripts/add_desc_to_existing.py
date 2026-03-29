#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为现有 list.md 文件批量添加 desc 部分
"""

import os
from pathlib import Path


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
    "资源库/用户自定义库": {
        "table_name": "用户自定义库索引",
        "columns": [
            ("name", "text", "YES", "YES", "资源名", "自定义资源"),
            ("summary", "text", "NO", "YES", "资源概况", "描述"),
            ("relations", "text", "NO", "NO", "相关资源", ""),
            ("chapter", "text", "NO", "NO", "出现章节", ""),
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


def generate_desc(table_name, columns):
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


def infer_schema(path_str, content):
    """根据路径推断 schema"""
    # 根据路径关键词推断
    if "人物库" in path_str:
        return SCHEMA_TEMPLATES["资源库/人物库"]
    elif "设定库" in path_str:
        return SCHEMA_TEMPLATES["资源库/设定库"]
    elif "伏笔库" in path_str:
        return SCHEMA_TEMPLATES["资源库/伏笔库"]
    elif "高光库" in path_str:
        return SCHEMA_TEMPLATES["资源库/高光库"]
    elif "历史库" in path_str:
        return SCHEMA_TEMPLATES["资源库/历史库"]
    elif "用户自定义库" in path_str:
        return SCHEMA_TEMPLATES["资源库/用户自定义库"]
    elif "资源库" in path_str:
        return SCHEMA_TEMPLATES["资源库"]
    elif "大纲" in path_str:
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
            return SCHEMA_TEMPLATES["大纲"]
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
            return SCHEMA_TEMPLATES["概括"]
    elif "写作要求" in path_str:
        return SCHEMA_TEMPLATES["写作要求"]
    
    return None


def add_desc_to_file(list_path):
    """为单个 list.md 文件添加 desc"""
    # 读取现有内容
    with open(list_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有 desc
    if "## desc" in content:
        print(f"  [SKIP] 已有 desc")
        return False
    
    # 计算相对路径（简化）
    path_str = str(list_path)
    if '资源库' in path_str:
        if '人物库' in path_str:
            relative_path = '资源库/人物库'
        elif '设定库' in path_str:
            relative_path = '资源库/设定库'
        elif '伏笔库' in path_str:
            relative_path = '资源库/伏笔库'
        elif '高光库' in path_str:
            relative_path = '资源库/高光库'
        elif '历史库' in path_str:
            relative_path = '资源库/历史库'
        elif '用户自定义库' in path_str:
            relative_path = '资源库/用户自定义库'
        else:
            relative_path = '资源库'
    elif '大纲' in path_str:
        relative_path = '大纲'
    elif '概括' in path_str:
        relative_path = '概括'
    elif '写作要求' in path_str:
        relative_path = '写作要求'
    else:
        relative_path = ''
    
    # 推断 schema
    template = infer_schema(relative_path, content)
    
    if not template:
        # 使用默认模板
        template = {
            "table_name": f"{relative_path.replace('/', ' > ')} 索引",
            "columns": [
                ("name", "text", "YES", "YES", "名称", "示例"),
                ("summary", "text", "NO", "YES", "概括", "示例概括"),
                ("extra", "text", "NO", "NO", "额外信息", "示例"),
            ]
        }
    
    # 生成 desc
    desc_content = generate_desc(template["table_name"], template["columns"])
    
    # 插入到文件开头
    new_content = desc_content + "\n\n" + content
    
    # 保存
    with open(list_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  [OK] 已添加 desc: {template['table_name']}")
    return True


def main():
    # 使用相对路径扫描
    books_path = "books"
    
    print(f"\n[INIT] 为所有书籍添加 desc 部分\n")
    
    # 扫描所有 list.md - 使用 os.walk
    list_files = []
    for root, dirs, files in os.walk(books_path):
        if "list.md" in files:
            list_files.append(os.path.join(root, "list.md"))
    
    print(f"找到 {len(list_files)} 个 list.md 文件\n")
    
    # 逐个处理
    updated = 0
    skipped = 0
    
    for list_path_str in list_files:
        list_path = Path(list_path_str)
        # 计算相对路径
        parts = list_path.parts
        if '水调歌头之夜' in str(list_path):
            rel_parts = parts[parts.index('水调歌头之夜')+1:-1]
            rel_path = '/'.join(rel_parts)
        else:
            rel_path = str(list_path)
        
        print(f"处理：{rel_path}")
        
        if add_desc_to_file(list_path):
            updated += 1
        else:
            skipped += 1
    
    print(f"\n[OK] 完成！")
    print(f"   更新：{updated} 个文件")
    print(f"   跳过：{skipped} 个文件")


if __name__ == "__main__":
    main()
