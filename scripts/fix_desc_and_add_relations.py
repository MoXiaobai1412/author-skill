#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_desc_and_add_relations.py - 修复 desc 并添加人物关系库

功能：
1. 检查所有子库 list.md 是否有 desc，没有则添加
2. 创建人物关系库
"""

import os
from pathlib import Path


# 各库的 desc 模板
DESC_TEMPLATES = {
    "人物库": {
        "table_name": "人物库索引",
        "columns": [
            ("name", "text", "YES", "YES", "资源名（重要资源加⭐）", "林远 ⭐"),
            ("summary", "text", "NO", "YES", "资源概况", "主角，少年，坚毅"),
            ("relations", "text", "NO", "NO", "相关资源", "清风（救命恩人）"),
            ("chapter", "text", "NO", "NO", "首次出现章节", "第一卷第 1 章"),
        ]
    },
    "设定库": {
        "table_name": "设定库索引",
        "columns": [
            ("name", "text", "YES", "YES", "设定名（重要设定加⭐）", "青云宗 ⭐"),
            ("summary", "text", "NO", "YES", "设定概况", "主角所在宗门，正道大派"),
            ("relations", "text", "NO", "NO", "相关设定", "修仙体系"),
            ("chapter", "text", "NO", "NO", "首次出现章节", "第一卷第 1 章"),
        ]
    },
    "场景库": {
        "table_name": "场景库索引",
        "columns": [
            ("name", "text", "YES", "YES", "场景名", "青云宗山门"),
            ("summary", "text", "NO", "YES", "场景概况", "云雾缭绕，台阶 999 级"),
            ("location", "text", "NO", "NO", "位置", "东域"),
            ("chapter", "text", "NO", "NO", "首次出现章节", "第一卷第 1 章"),
        ]
    },
    "伏笔库": {
        "table_name": "伏笔库索引",
        "columns": [
            ("name", "text", "YES", "YES", "伏笔名", "飘荡的窗帘"),
            ("summary", "text", "NO", "YES", "伏笔描述", "黑衣人身上的特殊标记"),
            ("status", "text", "NO", "YES", "状态", "未揭露/已揭露/已废弃"),
            ("plan_chapter", "text", "NO", "NO", "计划揭露章节", "第二卷第 5 章"),
            ("actual_chapter", "text", "NO", "NO", "实际揭露章节", ""),
        ]
    },
    "历史库": {
        "table_name": "历史库索引",
        "columns": [
            ("name", "text", "YES", "YES", "历史事件名", "第一次企业战争"),
            ("summary", "text", "NO", "YES", "事件概况", "三大企业混战，持续十年"),
            ("time", "text", "NO", "NO", "发生时间", "新历 50-60 年"),
            ("impact", "text", "NO", "NO", "影响", "世界格局重塑"),
        ]
    },
    "人物关系库": {
        "table_name": "人物关系库索引",
        "columns": [
            ("char_a", "text", "YES", "YES", "人物 A", "林远"),
            ("char_b", "text", "YES", "YES", "人物 B", "清风"),
            ("relation", "text", "NO", "YES", "关系类型", "救命恩人"),
            ("description", "text", "NO", "NO", "关系描述", "清风救下林远，成为好友"),
            ("chapter", "text", "NO", "NO", "关系建立章节", "第一卷第 1 章"),
        ]
    },
}


def generate_desc(table_name, columns):
    """生成 desc 部分"""
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


def add_desc_to_list(list_path, template):
    """为 list.md 添加 desc"""
    with open(list_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有 desc
    if "## desc" in content:
        return False, "已有 desc"
    
    # 生成 desc
    desc_content = generate_desc(template["table_name"], template["columns"])
    
    # 插入到文件开头
    new_content = desc_content + "\n\n" + content
    
    # 保存
    with open(list_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, "desc 已添加"


def create_relations_lib(resource_lib_path):
    """创建人物关系库"""
    relations_path = resource_lib_path / "人物关系库"
    
    if relations_path.exists():
        return False, "人物关系库已存在"
    
    # 创建文件夹
    relations_path.mkdir(parents=True, exist_ok=True)
    
    # 创建 list.md
    list_path = relations_path / "list.md"
    template = DESC_TEMPLATES["人物关系库"]
    desc_content = generate_desc(template["table_name"], template["columns"])
    
    # 添加示例数据
    data_content = """
## data
| 人物 A | 人物 B | 关系类型 | 关系描述 | 关系建立章节 |
|--------|--------|----------|----------|--------------|
| 林远 | 清风 | 救命恩人 | 清风救下林远，成为好友 | 第一卷第 1 章 |
| 林远 | 林父 | 父子 | 林远之父，为保护儿子而死 | 第一卷第 1 章 |
"""
    
    with open(list_path, 'w', encoding='utf-8') as f:
        f.write(desc_content + "\n" + data_content)
    
    # 创建示例关系档案
    example_path = relations_path / "林远 - 清风.md"
    example_content = """# 林远与清风的关系

## 关系类型
救命恩人 → 好友

## 关系建立
第一卷第 1 章

## 关系描述
清风在危急时刻救下林远，两人成为生死之交。

## 互动记录
| 章节 | 互动 | 关系变化 |
|------|------|----------|
| 第一卷第 1 章 | 清风救林远 | 陌生人 → 恩人 |
| 第一卷第 2 章 | 同行 | 恩人 → 好友 |

## 相关人物
- 林远：主角
- 清风：散修

## 备注
"""
    
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(example_content)
    
    return True, "人物关系库已创建"


def main():
    # 项目路径
    project_root = Path(r"C:\Users\LLxy\.openclaw\workspace\books\未来救援局")
    resource_lib = project_root / "资源库"
    
    print("\n[任务 1] 修复各库 list.md 的 desc\n")
    
    # 修复各库的 desc
    libs_to_fix = ["人物库", "设定库", "场景库", "伏笔库", "历史库"]
    
    for lib_name in libs_to_fix:
        lib_path = resource_lib / lib_name
        if not lib_path.exists():
            print(f"[SKIP] {lib_name} 不存在")
            continue
        
        list_path = lib_path / "list.md"
        if not list_path.exists():
            print(f"[SKIP] {lib_name}/list.md 不存在")
            continue
        
        template = DESC_TEMPLATES.get(lib_name)
        if not template:
            print(f"[SKIP] {lib_name} 没有模板")
            continue
        
        success, msg = add_desc_to_list(list_path, template)
        status = "[OK]" if success else "[WARN]"
        print(f"{status} {lib_name}: {msg}")
    
    print("\n[任务 2] 创建人物关系库\n")
    
    # 创建人物关系库
    success, msg = create_relations_lib(resource_lib)
    status = "[OK]" if success else "[WARN]"
    print(f"{status} 人物关系库：{msg}")
    
    print("\n[任务 3] 为人物关系库添加到资源库索引\n")
    
    # 更新资源库总索引
    main_list_path = resource_lib / "list.md"
    if main_list_path.exists():
        with open(main_list_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "人物关系库" not in content:
            # 添加到 data 部分
            if "## data" in content:
                parts = content.split("## data")
                new_line = "| 人物关系库 | 存储人物间关系设定 | 写作人物互动时查阅 |\n"
                parts[1] = new_line + parts[1]
                content = "## data".join(parts)
                
                with open(main_list_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("[OK] 人物关系库已添加到资源库总索引")
            else:
                print("[WARN] 资源库总索引格式异常")
        else:
            print("[INFO] 人物关系库已在总索引中")
    else:
        print("[WARN] 资源库总索引不存在")
    
    print("\n[OK] 所有任务完成！\n")


if __name__ == "__main__":
    main()
