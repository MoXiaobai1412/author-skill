#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resource_manager.py - 资源管理（SQLite 版本）

用法：
  python resource_manager.py add {书名} {项目根目录} {库名} {资源名} [概况] [相关资源]
  python resource_manager.py edit {书名} {项目根目录} {库名} {资源名}
  python resource_manager.py del {书名} {项目根目录} {库名} {资源名}
  python resource_manager.py list {书名} {项目根目录} {库名}
  python resource_manager.py get {书名} {项目根目录} {库名} {资源名}
  python resource_manager.py search {书名} {项目根目录} {库名} {关键词}
  python resource_manager.py important {书名} {项目根目录} {库名} {资源名} [是/否]
  python resource_manager.py update_chapter {书名} {项目根目录} {库名} {资源名} {章节}

支持库名：人物库、设定库、场景库、伏笔库、历史库、人物关系库

数据库：books/<书名>/source.db
"""

import os
import sys
from pathlib import Path
from database import ResourceDatabase


# 库名到表名的映射
LIB_TO_TABLE = {
    '人物库': 'characters',
    '设定库': 'settings',
    '场景库': 'scenes',
    '伏笔库': 'foreshadowing',
    '历史库': 'history',
    '人物关系库': 'character_relations',
}


class ResourceManager:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.db = ResourceDatabase(book_name, project_root)
    
    def __del__(self):
        if hasattr(self, 'db') and self.db:
            self.db.close()
    
    def get_table(self, lib_name):
        """获取表名"""
        return LIB_TO_TABLE.get(lib_name)
    
    # ========== 添加资源 ==========
    
    def add(self, lib_name, resource_name, summary="", relations="", chapter="", important=False, **kwargs):
        """添加资源"""
        table = self.get_table(lib_name)
        if not table:
            print(f"错误：不支持的库名 '{lib_name}'")
            print(f"支持的库：{', '.join(LIB_TO_TABLE.keys())}")
            return False
        
        try:
            if table == 'characters':
                self.db.add_character(resource_name, summary, relations, chapter, important)
            elif table == 'settings':
                self.db.add_setting(resource_name, summary, relations, chapter, important)
            elif table == 'scenes':
                self.db.add_scene(resource_name, summary, relations, chapter)
            elif table == 'foreshadowing':
                self.db.add_foreshadowing(resource_name, summary, relations, chapter)
            else:
                self.db.add(table, resource_name, summary, relations, chapter)
            
            print(f"[OK] 资源'{resource_name}'已添加到{lib_name}")
            return True
        except Exception as e:
            print(f"错误：{e}")
            return False
    
    # ========== 编辑资源 ==========
    
    def edit(self, lib_name, resource_name):
        """编辑资源（读取详情）"""
        table = self.get_table(lib_name)
        if not table:
            return None
        
        row = self.db.get(table, resource_name)
        if not row:
            print(f"错误：资源'{resource_name}'不存在于{lib_name}")
            return None
        
        print(f"\n## {lib_name}/{resource_name}\n")
        for key in row.keys():
            if row[key]:
                print(f"{key}: {row[key]}")
        
        return dict(row)
    
    # ========== 删除资源 ==========
    
    def del_resource(self, lib_name, resource_name):
        """删除资源"""
        table = self.get_table(lib_name)
        if not table:
            return False
        
        if self.db.delete(table, resource_name):
            print(f"[OK] 资源'{resource_name}'已从{lib_name}删除")
            return True
        else:
            print(f"错误：资源'{resource_name}'不存在")
            return False
    
    # ========== 列出资源 ==========
    
    def list_resources(self, lib_name, important_only=False):
        """列出库中所有资源"""
        table = self.get_table(lib_name)
        if not table:
            return []
        
        rows = self.db.list_all(table, important_only)
        
        if not rows:
            print(f"{lib_name} 暂无资源")
            return []
        
        print(f"\n## {lib_name}资源列表（《{self.book_name}》）\n")
        print("| 资源名 | 资源概况 | 相关资源 | 出现章节 |")
        print("|--------|----------|----------|----------|")
        
        for row in rows:
            name = row['name']
            summary = row['summary'][:30] + '...' if len(row['summary']) > 30 else row['summary']
            relations = row['relations'] or ''
            chapter = row['chapter'] or ''
            
            print(f"| {name} | {summary} | {relations} | {chapter} |")
        
        print(f"\n共 {len(rows)} 个资源\n")
        return [dict(row) for row in rows]
    
    # ========== 获取资源详情 ==========
    
    def get(self, lib_name, resource_name):
        """获取资源详情"""
        return self.edit(lib_name, resource_name)
    
    # ========== 搜索资源 ==========
    
    def search(self, lib_name, keyword, field='name'):
        """搜索资源"""
        table = self.get_table(lib_name)
        if not table:
            return []
        
        rows = self.db.search(table, keyword, field)
        
        if rows:
            print(f"\n## {lib_name}搜索结果：'{keyword}'\n")
            print("| 资源名 | 资源概况 | 相关资源 | 出现章节 |")
            print("|--------|----------|----------|----------|")
            for row in rows:
                name = row['name']
                summary = row['summary'][:30] + '...' if len(row['summary']) > 30 else row['summary']
                relations = row['relations'] or ''
                chapter = row['chapter'] or ''
                print(f"| {name} | {summary} | {relations} | {chapter} |")
            print(f"\n共 {len(rows)} 个结果\n")
        else:
            print(f"在{lib_name}中未找到匹配 '{keyword}' 的资源")
        
        return [dict(row) for row in rows]
    
    # ========== 设置重要资源 ==========
    
    def set_important(self, lib_name, resource_name, important=True):
        """设置资源为重要"""
        table = self.get_table(lib_name)
        if not table:
            return False
        
        is_important = 1 if important else 0
        if self.db.update(table, resource_name, is_important=is_important):
            status = "重要" if important else "普通"
            print(f"[OK] 已标记'{resource_name}'为{status}资源")
            return True
        else:
            print(f"错误：资源'{resource_name}'不存在")
            return False
    
    # ========== 更新出现章节 ==========
    
    def update_chapter(self, lib_name, resource_name, chapter):
        """更新资源的出现章节"""
        table = self.get_table(lib_name)
        if not table:
            return False
        
        if self.db.update(table, resource_name, chapter=chapter):
            print(f"[OK] 已更新'{resource_name}'的出现章节为：{chapter}")
            return True
        else:
            print(f"错误：资源'{resource_name}'不存在")
            return False
    
    # ========== 伏笔专用方法 ==========
    
    def vow_update(self, vow_id, status, actual_chapter=""):
        """更新伏笔状态"""
        if self.db.update_foreshadowing_status(vow_id, status, actual_chapter):
            print(f"[OK] 伏笔 {vow_id} 状态已更新为：{status}")
            if actual_chapter:
                print(f"  实际揭露：{actual_chapter}")
            return True
        else:
            print(f"错误：伏笔 '{vow_id}'不存在")
            return False
    
    def vow_list(self):
        """列出所有伏笔"""
        rows = self.db.get_active_foreshadowing()
        
        if not rows:
            print("伏笔库 暂无资源")
            return []
        
        print(f"\n## 伏笔列表（《{self.book_name}》）\n")
        print("| ID | 伏笔名 | 描述 | 状态 | 计划揭露 |")
        print("|----|--------|------|------|----------|")
        for row in rows:
            name = row['name']
            summary = row['summary'][:20] + '...' if len(row['summary']) > 20 else row['summary']
            status = row['status']
            plan = row['plan_chapter'] or ''
            print(f"| {row['id']} | {name} | {summary} | {status} | {plan} |")
        print(f"\n共 {len(rows)} 个伏笔\n")
        return [dict(row) for row in rows]
    
    # ========== 统计信息 ==========
    
    def stats(self):
        """显示数据库统计"""
        stats = self.db.get_stats()
        
        print(f"\n📊 《{self.book_name}》资源库统计\n")
        for table, count in stats.items():
            lib_name = table.replace('_', '库').replace('characters', '人物').replace('settings', '设定').replace('scenes', '场景').replace('foreshadowing', '伏笔').replace('history', '历史').replace('character relations', '人物关系')
            print(f"  {lib_name}: {count} 条记录")
        print()


def main():
    if len(sys.argv) < 5:
        print("用法：")
        print("  python resource_manager.py add {书名} {项目根目录} {库名} {资源名} [概况] [相关资源]")
        print("  python resource_manager.py edit {书名} {项目根目录} {库名} {资源名}")
        print("  python resource_manager.py del {书名} {项目根目录} {库名} {资源名}")
        print("  python resource_manager.py list {书名} {项目根目录} {库名}")
        print("  python resource_manager.py get {书名} {项目根目录} {库名} {资源名}")
        print("  python resource_manager.py search {书名} {项目根目录} {库名} {关键词}")
        print("  python resource_manager.py important {书名} {项目根目录} {库名} {资源名} [是/否]")
        print("  python resource_manager.py update_chapter {书名} {项目根目录} {库名} {资源名} {章节}")
        print("  python resource_manager.py stats {书名} {项目根目录}")
        print()
        print("支持库名：人物库、设定库、场景库、伏笔库、历史库、人物关系库")
        print()
        print("数据库：books/<书名>/source.db")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    lib_name = sys.argv[4]
    
    manager = ResourceManager(book_name, project_root)
    
    # stats 命令特殊处理
    if action == "stats":
        manager.stats()
        return
    
    if action == "add":
        if len(sys.argv) < 6:
            print("错误：请提供资源名")
            sys.exit(1)
        resource_name = sys.argv[5]
        summary = sys.argv[6] if len(sys.argv) > 6 else ""
        relations = sys.argv[7] if len(sys.argv) > 7 else ""
        chapter = sys.argv[8] if len(sys.argv) > 8 else ""
        important = "--important" in sys.argv or "-i" in sys.argv
        manager.add(lib_name, resource_name, summary, relations, chapter, important)
    
    elif action == "edit":
        if len(sys.argv) < 6:
            print("错误：请提供资源名")
            sys.exit(1)
        resource_name = sys.argv[5]
        manager.edit(lib_name, resource_name)
    
    elif action == "del":
        if len(sys.argv) < 6:
            print("错误：请提供资源名")
            sys.exit(1)
        resource_name = sys.argv[5]
        manager.del_resource(lib_name, resource_name)
    
    elif action == "list":
        important_only = "--important" in sys.argv or "-i" in sys.argv
        manager.list_resources(lib_name, important_only)
    
    elif action == "get":
        if len(sys.argv) < 6:
            print("错误：请提供资源名")
            sys.exit(1)
        resource_name = sys.argv[5]
        manager.get(lib_name, resource_name)
    
    elif action == "search":
        if len(sys.argv) < 6:
            print("错误：请提供关键词")
            sys.exit(1)
        keyword = sys.argv[5]
        manager.search(lib_name, keyword)
    
    elif action == "important":
        if len(sys.argv) < 6:
            print("错误：请提供资源名")
            sys.exit(1)
        resource_name = sys.argv[5]
        is_important = sys.argv[6].lower() != "否" if len(sys.argv) > 6 else True
        manager.set_important(lib_name, resource_name, is_important)
    
    elif action == "update_chapter":
        if len(sys.argv) < 7:
            print("错误：请提供章节")
            sys.exit(1)
        resource_name = sys.argv[5]
        chapter = sys.argv[6]
        manager.update_chapter(lib_name, resource_name, chapter)
    
    elif action == "vow_update":
        if len(sys.argv) < 7:
            print("错误：请提供伏笔 ID 和状态")
            sys.exit(1)
        vow_id = sys.argv[5]
        status = sys.argv[6]
        actual_chapter = sys.argv[7] if len(sys.argv) > 7 else ""
        manager.vow_update(vow_id, status, actual_chapter)
    
    elif action == "vow_list":
        manager.vow_list()
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
