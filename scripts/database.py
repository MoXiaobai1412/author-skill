#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database.py - 资源库 SQLite 索引数据库

架构设计：
- SQLite 存储索引和元数据（用于快速检索）
- .md 文件存储实际内容（用于详细阅读）
- AI 通过 SQLite 快速定位，读取.md 文件获取详情

数据库位置：books/<书名>/source.db
"""

import sqlite3
import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any


class ResourceDatabase:
    """资源库索引数据库管理类"""

    # 表结构定义
    TABLES = {
        'characters': {
            'name': '人物库',
            'columns': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT',
                'name TEXT NOT NULL UNIQUE',
                'summary TEXT NOT NULL',
                'relations TEXT',  # JSON 数组：["table/name", ...]
                'chapter TEXT',    # JSON 数组：["卷 1 章 1", "卷 1 章 2"]
                'priority INTEGER DEFAULT 5',  # 0-100，越小越重要
                'path TEXT NOT NULL',  # 相对路径：/人物库/林远.md
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ]
        },
        'settings': {
            'name': '设定库',
            'columns': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT',
                'name TEXT NOT NULL UNIQUE',
                'summary TEXT NOT NULL',
                'relations TEXT',
                'chapter TEXT',
                'priority INTEGER DEFAULT 5',
                'path TEXT NOT NULL',
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ]
        },
        'foreshadowing': {
            'name': '伏笔库',
            'columns': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT',
                'name TEXT NOT NULL UNIQUE',
                'summary TEXT NOT NULL',
                'relations TEXT',
                'chapter TEXT',
                'priority INTEGER DEFAULT 3',
                'path TEXT NOT NULL',
                'status TEXT DEFAULT "未揭露"',  # 未揭露/已揭露/已废弃
                'actual_chapter TEXT',
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ]
        },
        'history': {
            'name': '历史事件库',
            'columns': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT',
                'name TEXT NOT NULL UNIQUE',
                'summary TEXT NOT NULL',
                'relations TEXT',
                'chapter TEXT',
                'priority INTEGER DEFAULT 7',
                'path TEXT NOT NULL',
                'time TEXT',  # 发生时间
                'impact TEXT',  # 影响
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ]
        },
        'climax': {
            'name': '高潮事件库',
            'columns': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT',
                'name TEXT NOT NULL UNIQUE',
                'summary TEXT NOT NULL',
                'relations TEXT',
                'chapter TEXT',
                'priority INTEGER DEFAULT 2',
                'path TEXT NOT NULL',
                'type TEXT',  # 战斗/情感/反转/成长
                'volume TEXT',  # 第 X 卷
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ]
        },
        'items': {
            'name': '道具库',
            'columns': [
                'id INTEGER PRIMARY KEY AUTOINCREMENT',
                'name TEXT NOT NULL UNIQUE',
                'summary TEXT NOT NULL',
                'relations TEXT',
                'chapter TEXT',
                'priority INTEGER DEFAULT 6',
                'path TEXT NOT NULL',
                'type TEXT',  # 武器/防具/丹药/法器/其他
                'owner TEXT',  # 持有者
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            ]
        }
    }

    def __init__(self, book_name: str):
        """
        初始化数据库连接

        Args:
            book_name: 书名
        """
        self.book_name = book_name
        self.project_root = Path(os.path.expanduser("~")) / ".books"
        self.book_path = self.project_root / book_name
        self.db_path = self.book_path / "source.db"

        # 确保目录存在
        self.book_path.mkdir(parents=True, exist_ok=True)

        # 连接数据库
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # 创建表
        self.create_tables()

    def create_tables(self):
        """创建所有表"""
        for table_name, table_def in self.TABLES.items():
            columns = ', '.join(table_def['columns'])
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})'
            self.cursor.execute(sql)

        # 创建索引（加速查询）
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_chars_priority ON characters(priority)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_priority ON settings(priority)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_foreshadowing_status ON foreshadowing(status)')

        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    # ========== 通用 CRUD 操作 ==========

    def add(self, table: str, name: str, summary: str, path: str,
            relations: List[str] = None, chapter: List[str] = None,
            priority: int = 5, **kwargs) -> int:
        """
        添加资源

        Args:
            table: 表名（characters/settings/foreshadowing/history/climax/items）
            name: 资源名
            summary: 概况
            path: .md 文件路径（如：/人物库/林远.md）
            relations: 相关资源列表（["table/name", ...]）
            chapter: 出现章节列表（["卷 1 章 1", ...]）
            priority: 优先级（0-9，越小越重要）
            **kwargs: 其他字段

        Returns:
            int: 新插入的记录 ID
        """
        data = {
            'name': name,
            'summary': summary,
            'path': path,
            'relations': json.dumps(relations or [], ensure_ascii=False),
            'chapter': json.dumps(chapter or [], ensure_ascii=False),
            'priority': priority
        }
        data.update(kwargs)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])

        self.cursor.execute(
            f'INSERT INTO {table} ({columns}) VALUES ({placeholders})',
            list(data.values())
        )
        self.conn.commit()

        return self.cursor.lastrowid

    def get(self, table: str, name: str) -> Optional[Dict]:
        """获取资源详情"""
        self.cursor.execute(f'SELECT * FROM {table} WHERE name = ?', (name,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def update(self, table: str, name: str, **kwargs) -> bool:
        """更新资源"""
        if not kwargs:
            return False

        kwargs['updated_at'] = datetime.now()

        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [name]

        self.cursor.execute(
            f'UPDATE {table} SET {set_clause} WHERE name = ?',
            values
        )
        self.conn.commit()

        return self.cursor.rowcount > 0

    def delete(self, table: str, name: str) -> bool:
        """删除资源"""
        self.cursor.execute(f'DELETE FROM {table} WHERE name = ?', (name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ========== 查询操作 ==========

    def list_all(self, table: str, priority_limit: int = None,
                 order_by: str = 'priority') -> List[Dict]:
        """
        列出所有资源

        Args:
            table: 表名
            priority_limit: 优先级上限（只返回 <= 此值的记录）
            order_by: 排序字段

        Returns:
            list: 资源列表
        """
        if priority_limit is not None:
            self.cursor.execute(
                f'SELECT * FROM {table} WHERE priority <= ? ORDER BY {order_by}',
                (priority_limit,)
            )
        else:
            self.cursor.execute(f'SELECT * FROM {table} ORDER BY {order_by}')

        return [dict(row) for row in self.cursor.fetchall()]

    def search(self, table: str, keyword: str,
               fields: List[str] = None) -> List[Dict]:
        """
        搜索资源

        Args:
            table: 表名
            keyword: 关键词
            fields: 搜索字段列表（默认 ['name', 'summary', 'relations']）

        Returns:
            list: 匹配的资源列表
        """
        if fields is None:
            fields = ['name', 'summary', 'relations']

        conditions = ' OR '.join([f'{f} LIKE ?' for f in fields])
        pattern = f'%{keyword}%'

        self.cursor.execute(
            f'SELECT * FROM {table} WHERE {conditions}',
            [pattern] * len(fields)
        )

        return [dict(row) for row in self.cursor.fetchall()]

    def search_by_chapter(self, table: str, chapter: str) -> List[Dict]:
        """
        根据章节搜索

        Args:
            table: 表名
            chapter: 章节（如"卷 1 章 1"）

        Returns:
            list: 匹配的资源列表
        """
        # chapter 字段是 JSON 数组，使用 LIKE 查询
        self.cursor.execute(
            f'SELECT * FROM {table} WHERE chapter LIKE ?',
            (f'%{chapter}%',)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def search_by_priority(self, table: str, max_priority: int) -> List[Dict]:
        """
        按优先级搜索

        Args:
            table: 表名
            max_priority: 最大优先级（返回 <= 此值的记录）

        Returns:
            list: 匹配的资源列表
        """
        self.cursor.execute(
            f'SELECT * FROM {table} WHERE priority <= ? ORDER BY priority',
            (max_priority,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_path(self, table: str, path: str) -> Optional[Dict]:
        """根据路径获取资源"""
        self.cursor.execute(
            f'SELECT * FROM {table} WHERE path = ?',
            (path,)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ========== 章节管理 ==========

    def add_chapter(self, table: str, name: str, chapter: str) -> bool:
        """
        添加章节到资源的出现章节列表

        Args:
            table: 表名
            name: 资源名
            chapter: 新章节（如"卷 1 章 5"）

        Returns:
            bool: 是否成功
        """
        # 获取现有章节
        row = self.get(table, name)
        if not row:
            return False

        chapters = json.loads(row['chapter'])
        if chapter not in chapters:
            chapters.append(chapter)
            chapters.sort()  # 排序
            return self.update(table, name, chapter=json.dumps(chapters, ensure_ascii=False))

        return True

    def remove_chapter(self, table: str, name: str, chapter: str) -> bool:
        """从资源的出现章节列表中移除章节"""
        row = self.get(table, name)
        if not row:
            return False

        chapters = json.loads(row['chapter'])
        if chapter in chapters:
            chapters.remove(chapter)
            return self.update(table, name, chapter=json.dumps(chapters, ensure_ascii=False))

        return True

    # ========== 关系管理 ==========

    def add_relation(self, table: str, name: str, relation: str) -> bool:
        """
        添加相关资源

        Args:
            table: 表名
            name: 资源名
            relation: 相关资源（格式："table/name"）

        Returns:
            bool: 是否成功
        """
        row = self.get(table, name)
        if not row:
            return False

        relations = json.loads(row['relations'])
        if relation not in relations:
            relations.append(relation)
            return self.update(table, name, relations=json.dumps(relations, ensure_ascii=False))

        return True

    def get_relations(self, table: str, name: str) -> List[Dict]:
        """
        获取相关资源详情

        Args:
            table: 表名
            name: 资源名

        Returns:
            list: 相关资源列表
        """
        row = self.get(table, name)
        if not row:
            return []

        relations = json.loads(row['relations'])
        result = []

        for rel in relations:
            if '/' in rel:
                rel_table, rel_name = rel.split('/', 1)
                rel_data = self.get(rel_table, rel_name)
                if rel_data:
                    result.append(rel_data)

        return result

    # ========== 专用方法 ==========

    # 人物
    def add_character(self, name: str, summary: str, path: str,
                     relations: List[str] = None, chapter: List[str] = None,
                     priority: int = 5) -> int:
        """添加人物"""
        return self.add('characters', name, summary, path, relations, chapter, priority)

    def get_important_characters(self, max_priority: int = 3) -> List[Dict]:
        """获取重要人物（优先级 <= max_priority）"""
        return self.search_by_priority('characters', max_priority)

    # 设定
    def add_setting(self, name: str, summary: str, path: str,
                   relations: List[str] = None, chapter: List[str] = None,
                   priority: int = 5) -> int:
        """添加设定"""
        return self.add('settings', name, summary, path, relations, chapter, priority)

    def get_core_settings(self) -> List[Dict]:
        """获取核心设定（优先级 <= 3）"""
        return self.search_by_priority('settings', 3)

    # 伏笔
    def add_foreshadowing(self, name: str, summary: str, path: str,
                         relations: List[str] = None, chapter: List[str] = None,
                         priority: int = 3, status: str = '未揭露',
                         plan_chapter: str = None) -> int:
        """添加伏笔"""
        return self.add('foreshadowing', name, summary, path, relations, chapter,
                       priority, status=status, plan_chapter=plan_chapter)

    def get_active_foreshadowing(self) -> List[Dict]:
        """获取未揭露伏笔"""
        self.cursor.execute(
            "SELECT * FROM foreshadowing WHERE status = '未揭露' ORDER BY priority"
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def update_foreshadowing_status(self, name: str, status: str,
                                   actual_chapter: str = None) -> bool:
        """更新伏笔状态"""
        return self.update('foreshadowing', name, status=status,
                          actual_chapter=actual_chapter)

    # 历史事件
    def add_history(self, name: str, summary: str, path: str,
                   relations: List[str] = None, chapter: List[str] = None,
                   priority: int = 7, time: str = None,
                   impact: str = None) -> int:
        """添加历史事件"""
        return self.add('history', name, summary, path, relations, chapter,
                       priority, time=time, impact=impact)

    # 高潮事件
    def add_climax(self, name: str, summary: str, path: str,
                  relations: List[str] = None, chapter: List[str] = None,
                  priority: int = 2, type: str = None,
                  volume: str = None) -> int:
        """添加高潮事件"""
        return self.add('climax', name, summary, path, relations, chapter,
                       priority, type=type, volume=volume)

    # 道具
    def add_item(self, name: str, summary: str, path: str,
                relations: List[str] = None, chapter: List[str] = None,
                priority: int = 6, type: str = None,
                owner: str = None) -> int:
        """添加道具"""
        return self.add('items', name, summary, path, relations, chapter,
                       priority, type=type, owner=owner)

    # ========== 统计和导出 ==========

    def get_stats(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        stats = {}
        for table_name in self.TABLES.keys():
            self.cursor.execute(f'SELECT COUNT(*) as count FROM {table_name}')
            stats[table_name] = self.cursor.fetchone()['count']
        return stats

    def export_to_dict(self, table: str) -> List[Dict]:
        """导出表数据为字典列表"""
        self.cursor.execute(f'SELECT * FROM {table}')
        return [dict(row) for row in self.cursor.fetchall()]

    # ========== 智能检索（AI 查询核心） ==========

    def retrieve_for_chapter(self, chapter: str,
                            max_results: int = 50) -> Dict[str, List[Dict]]:
        """
        为某章节检索相关资源（AI 写作前使用）

        Args:
            chapter: 章节（如"卷 1 章 5"）
            max_results: 每个类别最大返回数

        Returns:
            dict: 检索结果
        """
        result = {
            'important_chars': self.get_important_characters(3)[:20],
            'relevant_chars': self.search_by_chapter('characters', chapter)[:max_results],
            'core_settings': self.get_core_settings()[:10],
            'relevant_settings': self.search_by_chapter('settings', chapter)[:max_results],
            'active_foreshadowing': self.get_active_foreshadowing()[:10],
            'relevant_history': self.search_by_chapter('history', chapter)[:max_results],
            'relevant_climax': self.search_by_chapter('climax', chapter)[:max_results],
            'relevant_items': self.search_by_chapter('items', chapter)[:max_results],
        }
        return result

    def retrieve_by_keywords(self, keywords: List[str],
                            max_results: int = 30) -> Dict[str, List[Dict]]:
        """
        根据关键词检索资源

        Args:
            keywords: 关键词列表（如["青云宗", "试炼", "筑基"]）
            max_results: 每个类别最大返回数

        Returns:
            dict: 检索结果
        """
        result = {
            'characters': [],
            'settings': [],
            'foreshadowing': [],
            'history': [],
            'climax': [],
            'items': []
        }

        for keyword in keywords:
            # 搜索各表
            result['characters'].extend(
                self.search('characters', keyword)[:max_results])
            result['settings'].extend(
                self.search('settings', keyword)[:max_results])
            result['foreshadowing'].extend(
                self.search('foreshadowing', keyword)[:max_results])
            result['history'].extend(
                self.search('history', keyword)[:max_results])
            result['climax'].extend(
                self.search('climax', keyword)[:max_results])
            result['items'].extend(
                self.search('items', keyword)[:max_results])

        # 去重
        for key in result:
            seen = set()
            unique = []
            for item in result[key]:
                if item['name'] not in seen:
                    seen.add(item['name'])
                    unique.append(item)
            result[key] = unique[:max_results]

        return result


# ========== 便捷函数 ==========

def init_database(book_name: str) -> ResourceDatabase:
    """初始化数据库（便捷函数）"""
    return ResourceDatabase(book_name)


# ========== 命令行接口 ==========

def parse_json_field(value: str) -> any:
    """解析 JSON 字段（relations, chapter）"""
    if not value:
        return []
    if value.startswith('['):
        try:
            return json.loads(value)
        except:
            pass
    # 逗号分隔
    return [v.strip() for v in value.split(',') if v.strip()]


# 以下命令函数均接收 kwargs 字典，从中提取所需字段
def cmd_create(db: ResourceDatabase, kwargs: dict):
    """
    创建资源
    用法：python script/database.py <书名> create table <表名> name <名称> summary <概况> path <路径> [relations <相关资源>] [chapter <出现章节>] [priority <优先级>] [其他字段...]
    """
    required = ['table', 'name', 'summary', 'path']
    for key in required:
        if key not in kwargs:
            print(f"错误：缺少必要参数 '{key}'")
            return

    table = kwargs.pop('table')
    name = kwargs.pop('name')
    summary = kwargs.pop('summary')
    path = kwargs.pop('path')

    relations = kwargs.pop('relations', None)
    if relations is not None:
        relations = parse_json_field(relations)
    chapter = kwargs.pop('chapter', None)
    if chapter is not None:
        chapter = parse_json_field(chapter)
    priority = int(kwargs.pop('priority', 5))

    # 调用通用 add 方法，其他字段作为额外参数传递
    db.add(table, name, summary, path, relations, chapter, priority, **kwargs)
    print(f"[OK] 已创建：{table}/{name}")
    print(f"     路径：{path}")
    print(f"     优先级：{priority}")


def cmd_delete(db: ResourceDatabase, kwargs: dict):
    """
    删除资源
    用法：python script/database.py <书名> delete table <表名> name <名称>
    """
    if 'table' not in kwargs or 'name' not in kwargs:
        print("错误：缺少必要参数 'table' 和 'name'")
        return

    table = kwargs['table']
    name = kwargs['name']

    if db.delete(table, name):
        print(f"[OK] 已删除：{table}/{name}")
    else:
        print(f"错误：资源 '{name}' 不存在")


def cmd_update(db: ResourceDatabase, kwargs: dict):
    """
    更新资源
    用法：python script/database.py <书名> update table <表名> name <名称> [字段=值 ...]
    """
    if 'table' not in kwargs or 'name' not in kwargs:
        print("错误：缺少必要参数 'table' 和 'name'")
        return

    table = kwargs.pop('table')
    name = kwargs.pop('name')

    # 剩余 kwargs 即为更新字段
    if not kwargs:
        print("错误：请提供至少一个 field=value 对")
        return

    # 处理 JSON 字段
    for key in ['relations', 'chapter']:
        if key in kwargs:
            kwargs[key] = json.dumps(parse_json_field(kwargs[key]), ensure_ascii=False)

    if db.update(table, name, **kwargs):
        print(f"[OK] 已更新：{table}/{name}")
        for k, v in kwargs.items():
            print(f"     {k} = {v}")
    else:
        print(f"错误：资源 '{name}' 不存在")


def cmd_get(db: ResourceDatabase, kwargs: dict):
    """
    获取资源详情
    用法：python script/database.py <书名> get table <表名> name <名称>
    """
    if 'table' not in kwargs or 'name' not in kwargs:
        print("错误：缺少必要参数 'table' 和 'name'")
        return

    table = kwargs['table']
    name = kwargs['name']

    row = db.get(table, name)
    if row:
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
    else:
        print(f"错误：资源 '{name}' 不存在于 {table}")


def cmd_list(db: ResourceDatabase, kwargs: dict):
    """
    列出资源
    用法：python script/database.py <书名> list table <表名> [priority_limit <上限>]
    """
    if 'table' not in kwargs:
        print("错误：缺少必要参数 'table'")
        return

    table = kwargs['table']
    priority_limit = kwargs.get('priority_limit')
    if priority_limit is not None:
        priority_limit = int(priority_limit)

    rows = db.list_all(table, priority_limit)

    if not rows:
        print(f"{table} 暂无资源")
        return

    print(f"\n## {table} 资源列表\n")
    print(f"| 优先级 | 资源名 | 概况 | 出现章节 |")
    print(f"|--------|--------|------|----------|")

    for row in rows[:50]:
        stars = "⭐" * (10 - row['priority']) if row['priority'] <= 10 else ""
        chapter = json.loads(row['chapter']) if row['chapter'] else []
        chapter_str = ', '.join(chapter[:3])
        if len(chapter) > 3:
            chapter_str += f"... (共{len(chapter)}章)"

        print(f"| {row['priority']} {stars} | {row['name']} | {row['summary'][:30]} | {chapter_str} |")

    if len(rows) > 50:
        print(f"\n... 还有 {len(rows) - 50} 条记录")

    print(f"\n共 {len(rows)} 个资源\n")


def cmd_search(db: ResourceDatabase, kwargs: dict):
    """
    搜索资源
    用法：python script/database.py <书名> search table <表名> keyword <关键词> [field <字段名>]
    """
    if 'table' not in kwargs or 'keyword' not in kwargs:
        print("错误：缺少必要参数 'table' 和 'keyword'")
        return

    table = kwargs['table']
    keyword = kwargs['keyword']
    field = kwargs.get('field')

    if field:
        rows = db.search(table, keyword, fields=[field])
    else:
        rows = db.search(table, keyword)

    if rows:
        print(f"\n## {table} 搜索结果：'{keyword}'\n")
        for row in rows:
            print(f"⭐ {row['name']} (优先级：{row['priority']})")
            print(f"   概况：{row['summary']}")
            print(f"   路径：{row['path']}")
            chapter = json.loads(row['chapter']) if row['chapter'] else []
            print(f"   章节：{', '.join(chapter)}")
            print()
    else:
        print(f"\n⚠ 在 {table} 中未找到匹配 '{keyword}' 的资源")
        print("\n【所有资源列表】（AI 请匹配最相关的资源）\n")

        all_rows = db.list_all(table)
        for row in all_rows:
            print(f"- {row['name']}: {row['summary']}")

        print("\n💡 AI 提示：请从以上资源中匹配最相关的资源名称，然后使用以下命令查询路径：")
        print(f"   python script/database.py \"{db.book_name}\" get table {table} name <资源名>")


def cmd_get_path(db: ResourceDatabase, kwargs: dict):
    """
    获取资源路径
    用法：python script/database.py <书名> get-path table <表名> name <名称>
    """
    if 'table' not in kwargs or 'name' not in kwargs:
        print("错误：缺少必要参数 'table' 和 'name'")
        return

    table = kwargs['table']
    name = kwargs['name']

    row = db.get(table, name)
    if row:
        print(f"\n【资源路径】")
        print(f"表：{table}")
        print(f"名称：{name}")
        print(f"路径：{row['path']}")
        print(f"\n【操作示例】")
        print(f"读取文件：cat {row['path']}")
        print(f"编辑文件：vim {row['path']}")
    else:
        print(f"错误：资源 '{name}' 不存在于 {table}")


def cmd_add_chapter(db: ResourceDatabase, kwargs: dict):
    """
    添加章节到资源
    用法：python script/database.py <书名> add-chapter table <表名> name <名称> chapter <章节>
    """
    if 'table' not in kwargs or 'name' not in kwargs or 'chapter' not in kwargs:
        print("错误：缺少必要参数 'table', 'name', 'chapter'")
        return

    table = kwargs['table']
    name = kwargs['name']
    chapter = kwargs['chapter']

    if db.add_chapter(table, name, chapter):
        print(f"[OK] 已添加章节 '{chapter}' 到 {table}/{name}")
    else:
        print(f"错误：资源 '{name}' 不存在于 {table}")


def cmd_set_priority(db: ResourceDatabase, kwargs: dict):
    """
    设置资源优先级
    用法：python script/database.py <书名> set-priority table <表名> name <名称> priority <优先级>
    """
    if 'table' not in kwargs or 'name' not in kwargs or 'priority' not in kwargs:
        print("错误：缺少必要参数 'table', 'name', 'priority'")
        return

    table = kwargs['table']
    name = kwargs['name']
    priority = int(kwargs['priority'])

    if db.update(table, name, priority=priority):
        print(f"[OK] 已设置 {table}/{name} 的优先级为 {priority}")
    else:
        print(f"错误：资源 '{name}' 不存在于 {table}")


def cmd_add_relation(db: ResourceDatabase, kwargs: dict):
    """
    添加相关资源
    用法：python script/database.py <书名> add-relation table <表名> name <名称> relation <相关资源>
    """
    if 'table' not in kwargs or 'name' not in kwargs or 'relation' not in kwargs:
        print("错误：缺少必要参数 'table', 'name', 'relation'")
        return

    table = kwargs['table']
    name = kwargs['name']
    relation = kwargs['relation']

    if db.add_relation(table, name, relation):
        print(f"[OK] 已添加相关资源 '{relation}' 到 {table}/{name}")
    else:
        print(f"错误：资源 '{name}' 不存在于 {table}")


def cmd_list_related(db: ResourceDatabase, kwargs: dict):
    """
    列出相关资源
    用法：python script/database.py <书名> list-related table <表名> name <名称>
    """
    if 'table' not in kwargs or 'name' not in kwargs:
        print("错误：缺少必要参数 'table' 和 'name'")
        return

    table = kwargs['table']
    name = kwargs['name']

    relations = db.get_relations(table, name)

    if relations:
        print(f"\n## {table}/{name} 的相关资源\n")
        for rel in relations:
            print(f"⭐ {rel['name']} ({rel.get('priority', 'N/A')})")
            print(f"   概况：{rel['summary']}")
            print(f"   路径：{rel['path']}")
            print()
    else:
        print(f"{table}/{name} 暂无相关资源")


def cmd_export(db: ResourceDatabase, kwargs: dict):
    """
    导出表数据为 JSON
    用法：python script/database.py <书名> export table <表名> [output_file <文件名>]
    """
    if 'table' not in kwargs:
        print("错误：缺少必要参数 'table'")
        return

    table = kwargs['table']
    output_file = kwargs.get('output_file', f"{table}_export.json")

    rows = db.export_to_dict(table)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"[OK] 已导出 {len(rows)} 条记录到 {output_file}")


def cmd_stats(db: ResourceDatabase, kwargs: dict):
    """显示统计信息"""
    stats = db.get_stats()

    print(f"\n📊 数据库统计\n")
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
        print(f"  {table_cn} ({table_en}): {count} 条")
    print()


def cmd_sql(db: ResourceDatabase, sql: str):
    """
    直接执行 SQL 语句
    用法：python database.py <书名> sql <SQL语句>
    """
    if not sql:
        print("错误：请提供 SQL 语句")
        return

    print(f"\n准备执行 SQL：\n{sql}\n")

    # 安全确认
    confirm = input("是否执行此 SQL？(y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消执行。")
        return

    try:
        cursor = db.conn.cursor()
        cursor.execute(sql)
        # 判断是否为 SELECT 语句
        if sql.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            if rows:
                print("\n查询结果：")
                for row in rows:
                    row_dict = dict(row)
                    for k, v in row_dict.items():
                        print(f"{k}: {v}")
                    print("-" * 40)
            else:
                print("没有找到记录。")
        else:
            db.conn.commit()
            print(f"执行成功，影响行数：{cursor.rowcount}")
    except sqlite3.Error as e:
        print(f"SQL 执行错误：{e}")


def print_help():
    """打印帮助信息"""
    print("""
[资源库命令行工具]

用法：python database.py "<书名>" <command> [<key1> <value1> <key2> <value2> ...]
或： python database.py "<书名>" sql "<SQL语句>"

可用命令：

  create        创建资源
                必要键：table, name, summary, path
                可选键：relations, chapter, priority, 以及其他表特定字段
                示例：python database.py "三体" create table characters name "罗辑" summary "主角" path "人物库/罗辑.md" priority 0

  delete        删除资源
                必要键：table, name
                示例：python database.py "三体" delete table characters name "罗辑"

  update        更新资源
                必要键：table, name
                其他键：需要更新的字段
                示例：python database.py "三体" update table characters name "罗辑" priority 1

  get           获取资源详情
                必要键：table, name
                示例：python database.py "三体" get table characters name "罗辑"

  list          列出资源
                必要键：table
                可选键：priority_limit
                示例：python database.py "三体" list table characters priority_limit 3

  search        搜索资源
                必要键：table, keyword
                可选键：field (搜索字段)
                示例：python database.py "三体" search table characters keyword "罗"

  get-path      获取资源路径
                必要键：table, name
                示例：python database.py "三体" get-path table characters name "罗辑"

  add-chapter   添加章节
                必要键：table, name, chapter
                示例：python database.py "三体" add-chapter table characters name "罗辑" chapter "卷 1 章 1"

  set-priority  设置优先级
                必要键：table, name, priority
                示例：python database.py "三体" set-priority table characters name "罗辑" priority 0

  add-relation  添加相关资源
                必要键：table, name, relation
                示例：python database.py "三体" add-relation table characters name "罗辑" relation "settings/青云宗"

  list-related  列出相关资源
                必要键：table, name
                示例：python database.py "三体" list-related table characters name "罗辑"

  export        导出表数据为 JSON
                必要键：table
                可选键：output_file
                示例：python database.py "三体" export table characters output_file "chars.json"

  stats         显示统计信息
                无需参数
                示例：python database.py "三体" stats

  sql           直接执行 SQL 语句
                示例：python database.py "三体" sql "SELECT * FROM characters WHERE priority <= 3"

表名：
  characters   - 人物库
  settings     - 设定库
  foreshadowing - 伏笔库
  history      - 历史事件库
  climax       - 高潮事件库
  items        - 道具库
""")


def main():
    import sys

    if len(sys.argv) < 2:
        print_help()
        return

    book_name = sys.argv[1]
    if len(sys.argv) < 3:
        print("错误：缺少命令")
        print_help()
        return

    command = sys.argv[2]

    # 帮助命令
    if command in ['-h', '--help', 'help']:
        print_help()
        return

    # 特殊处理 sql 命令：直接接收 SQL 语句
    if command == 'sql':
        if len(sys.argv) < 4:
            print("错误：请提供 SQL 语句")
            return
        # 将所有剩余参数拼接成 SQL 语句（可能包含空格）
        sql = ' '.join(sys.argv[3:])
        db = ResourceDatabase(book_name)
        try:
            cmd_sql(db, sql)
        finally:
            db.close()
        return

    # 其他命令：解析键值对
    args = sys.argv[3:]
    if len(args) % 2 != 0:
        print("错误：参数必须成对出现（键 值 键 值 ...）")
        return

    kwargs = {args[i]: args[i+1] for i in range(0, len(args), 2)}

    db = ResourceDatabase(book_name)

    try:
        if command == 'create':
            cmd_create(db, kwargs)
        elif command == 'delete':
            cmd_delete(db, kwargs)
        elif command == 'update':
            cmd_update(db, kwargs)
        elif command == 'get':
            cmd_get(db, kwargs)
        elif command == 'list':
            cmd_list(db, kwargs)
        elif command == 'search':
            cmd_search(db, kwargs)
        elif command == 'get-path':
            cmd_get_path(db, kwargs)
        elif command == 'add-chapter':
            cmd_add_chapter(db, kwargs)
        elif command == 'set-priority':
            cmd_set_priority(db, kwargs)
        elif command == 'add-relation':
            cmd_add_relation(db, kwargs)
        elif command == 'list-related':
            cmd_list_related(db, kwargs)
        elif command == 'export':
            cmd_export(db, kwargs)
        elif command == 'stats':
            cmd_stats(db, kwargs)
        else:
            print(f"错误：未知命令 '{command}'\n")
            print_help()
    finally:
        db.close()


if __name__ == "__main__":
    main()