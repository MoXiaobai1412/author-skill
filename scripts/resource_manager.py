#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resource_manager.py - 资源管理（SQLite 索引版）

架构：
- SQLite 存储索引（快速检索）
- .md 文件存储实际内容（详细阅读）
- AI 通过 SQLite 定位，读取.md 获取详情

用法：
  python resource_manager.py add {书名} {项目根目录} {表名} {资源名} {概况} {路径} [选项]
  python resource_manager.py list {书名} {项目根目录} {表名}
  python resource_manager.py search {书名} {项目根目录} {表名} {关键词}
  python resource_manager.py get {书名} {项目根目录} {表名} {资源名}
  python resource_manager.py del {书名} {项目根目录} {表名} {资源名}
  python resource_manager.py add_chapter {书名} {项目根目录} {表名} {资源名} {章节}
  python resource_manager.py stats {书名} {项目根目录}

表名：characters, settings, foreshadowing, history, climax, items
"""

import sys
import json
from pathlib import Path
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import ResourceDatabase


# 表名映射（中文→英文）
TABLE_MAP = {
    '人物库': 'characters',
    '人物': 'characters',
    '设定库': 'settings',
    '设定': 'settings',
    '伏笔库': 'foreshadowing',
    '伏笔': 'foreshadowing',
    '历史库': 'history',
    '历史': 'history',
    '高潮库': 'climax',
    '高潮': 'climax',
    '道具库': 'items',
    '道具': 'items',
}


class ResourceManager:
    def __init__(self, book_name: str, project_root: str):
        self.book_name = book_name
        self.project_root = Path(project_root)
        self.db = ResourceDatabase(book_name, str(project_root))
        self.book_path = self.project_root / book_name
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_table(self, table_name: str) -> str:
        """获取英文表名"""
        return TABLE_MAP.get(table_name, table_name)
    
    def add(self, table: str, name: str, summary: str, path: str,
            relations: str = None, chapter: str = None,
            priority: int = 5, **kwargs):
        """添加资源"""
        table = self.get_table(table)
        
        # 解析 relations 和 chapter（支持字符串和 JSON）
        try:
            rel_list = json.loads(relations) if relations else []
        except:
            rel_list = [r.strip() for r in relations.split(',') if r.strip()] if relations else []
        
        try:
            chap_list = json.loads(chapter) if chapter else []
        except:
            chap_list = [c.strip() for c in chapter.split(',') if c.strip()] if chapter else []
        
        # 添加
        if table == 'characters':
            self.db.add_character(name, summary, path, rel_list, chap_list, priority)
        elif table == 'settings':
            self.db.add_setting(name, summary, path, rel_list, chap_list, priority)
        elif table == 'foreshadowing':
            self.db.add_foreshadowing(name, summary, path, rel_list, chap_list, priority,
                                     kwargs.get('status', '未揭露'),
                                     kwargs.get('plan_chapter'))
        elif table == 'history':
            self.db.add_history(name, summary, path, rel_list, chap_list, priority,
                               kwargs.get('time'), kwargs.get('impact'))
        elif table == 'climax':
            self.db.add_climax(name, summary, path, rel_list, chap_list, priority,
                              kwargs.get('type'), kwargs.get('volume'))
        elif table == 'items':
            self.db.add_item(name, summary, path, rel_list, chap_list, priority,
                            kwargs.get('type'), kwargs.get('owner'))
        
        print(f"[OK] 已添加：{name} → {table}")
        print(f"     路径：{path}")
        print(f"     优先级：{priority}")
    
    def list_all(self, table: str, priority_limit: int = None):
        """列出所有资源"""
        table = self.get_table(table)
        rows = self.db.list_all(table, priority_limit)
        
        if not rows:
            print(f"{table} 暂无资源")
            return
        
        print(f"\n## {table} 资源列表\n")
        print(f"| 优先级 | 资源名 | 概况 | 出现章节 |")
        print(f"|--------|--------|------|----------|")
        
        for row in rows[:50]:  # 限制显示 50 条
            stars = "⭐" * (10 - row['priority'])
            chapter = json.loads(row['chapter']) if row['chapter'] else []
            chapter_str = ', '.join(chapter[:3])
            if len(chapter) > 3:
                chapter_str += f"... (共{len(chapter)}章)"
            
            print(f"| {row['priority']} {stars} | {row['name']} | {row['summary'][:30]} | {chapter_str} |")
        
        if len(rows) > 50:
            print(f"\n... 还有 {len(rows) - 50} 条记录")
        
        print(f"\n共 {len(rows)} 个资源\n")
    
    def search(self, table: str, keyword: str):
        """搜索资源"""
        table = self.get_table(table)
        rows = self.db.search(table, keyword)
        
        if not rows:
            print(f"在 {table} 中未找到匹配 '{keyword}' 的资源")
            return
        
        print(f"\n## {table} 搜索结果：'{keyword}'\n")
        for row in rows:
            print(f"⭐ {row['name']} (优先级：{row['priority']})")
            print(f"   概况：{row['summary']}")
            print(f"   路径：{row['path']}")
            chapter = json.loads(row['chapter']) if row['chapter'] else []
            print(f"   章节：{', '.join(chapter)}")
            print()
    
    def get(self, table: str, name: str):
        """获取资源详情"""
        table = self.get_table(table)
        row = self.db.get(table, name)
        
        if not row:
            print(f"错误：资源 '{name}' 不存在")
            return
        
        print(f"\n## {table}/{name}\n")
        for key, value in row.items():
            if value:
                # 解析 JSON 字段
                if key in ['relations', 'chapter'] and isinstance(value, str):
                    try:
                        value = json.loads(value)
                        value = ', '.join(value)
                    except:
                        pass
                print(f"{key}: {value}")
        
        # 读取.md 文件
        path = self.book_path / row['path'].lstrip('/')
        if path.exists():
            print(f"\n【档案文件】{path}")
            content = path.read_text(encoding='utf-8')
            print(f"\n{content[:500]}...")
    
    def delete(self, table: str, name: str):
        """删除资源"""
        table = self.get_table(table)
        if self.db.delete(table, name):
            print(f"[OK] 已删除：{name}")
        else:
            print(f"错误：资源 '{name}' 不存在")
    
    def add_chapter(self, table: str, name: str, chapter: str):
        """添加章节"""
        table = self.get_table(table)
        if self.db.add_chapter(table, name, chapter):
            print(f"[OK] 已添加章节 '{chapter}' 到 {name}")
        else:
            print(f"错误：资源 '{name}' 不存在")
    
    def stats(self):
        """显示统计"""
        stats = self.db.get_stats()
        
        print(f"\n📊 《{self.book_name}》资源库统计\n")
        table_names = {
            'characters': '人物',
            'settings': '设定',
            'foreshadowing': '伏笔',
            'history': '历史',
            'climax': '高潮',
            'items': '道具',
        }
        for table_en, table_cn in table_names.items():
            count = stats.get(table_en, 0)
            print(f"  {table_cn}: {count} 条")
        print()


def main():
    if len(sys.argv) < 4:
        print("用法：")
        print("  python resource_manager.py add {书名} {项目根目录} {表名} {资源名} {概况} {路径} [选项]")
        print("  python resource_manager.py list {书名} {项目根目录} {表名}")
        print("  python resource_manager.py search {书名} {项目根目录} {表名} {关键词}")
        print("  python resource_manager.py get {书名} {项目根目录} {表名} {资源名}")
        print("  python resource_manager.py del {书名} {项目根目录} {表名} {资源名}")
        print("  python resource_manager.py add_chapter {书名} {项目根目录} {表名} {资源名} {章节}")
        print("  python resource_manager.py stats {书名} {项目根目录}")
        print()
        print("表名：人物库/characters, 设定库/settings, 伏笔库/foreshadowing,")
        print("      历史库/history, 高潮库/climax, 道具库/items")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    
    manager = ResourceManager(book_name, project_root)
    
    if action == "stats":
        manager.stats()
        return
    
    if action == "add":
        if len(sys.argv) < 7:
            print("错误：参数不足")
            sys.exit(1)
        table = sys.argv[4]
        name = sys.argv[5]
        summary = sys.argv[6]
        path = sys.argv[7] if len(sys.argv) > 7 else f"/资源档案/{table}/{name}.md"
        priority = 5
        for arg in sys.argv[8:]:
            if arg.startswith('--priority='):
                priority = int(arg.split('=')[1])
        manager.add(table, name, summary, path, priority=priority)
    
    elif action == "list":
        if len(sys.argv) < 5:
            print("错误：请提供表名")
            sys.exit(1)
        table = sys.argv[4]
        manager.list_all(table)
    
    elif action == "search":
        if len(sys.argv) < 6:
            print("错误：请提供关键词")
            sys.exit(1)
        table = sys.argv[4]
        keyword = sys.argv[5]
        manager.search(table, keyword)
    
    elif action == "get":
        if len(sys.argv) < 6:
            print("错误：请提供资源名")
            sys.exit(1)
        table = sys.argv[4]
        name = sys.argv[5]
        manager.get(table, name)
    
    elif action == "del":
        if len(sys.argv) < 6:
            print("错误：请提供资源名")
            sys.exit(1)
        table = sys.argv[4]
        name = sys.argv[5]
        manager.delete(table, name)
    
    elif action == "add_chapter":
        if len(sys.argv) < 7:
            print("错误：请提供资源名和章节")
            sys.exit(1)
        table = sys.argv[4]
        name = sys.argv[5]
        chapter = sys.argv[6]
        manager.add_chapter(table, name, chapter)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
