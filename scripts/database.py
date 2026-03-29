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
                'plan_chapter TEXT',
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
            project_root: 项目根目录（books 文件夹路径）
        """
        self.book_name = book_name
        self.project_root = os.path.expanduser("~") / ".books"
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

def init_database(book_name: str, project_root: str) -> ResourceDatabase:
    """初始化数据库（便捷函数）"""
    return ResourceDatabase(book_name, project_root)


if __name__ == "__main__":
    # 测试代码
    print("测试数据库初始化...")
    
    db = ResourceDatabase("测试小说", r"C:\Users\LLxy\.openclaw\workspace\books")
    
    # 添加测试数据
    db.add_character("林远 ⭐", "主角，少年，坚毅", 
                    "/人物库/林远.md", 
                    ["settings/青云宗", "characters/清风"],
                    ["卷 1 章 1", "卷 1 章 2"],
                    priority=0)
    
    # 查询测试
    important = db.get_important_characters()
    print(f"重要人物：{len(important)}人")
    
    # 检索测试
    context = db.retrieve_for_chapter("卷 1 章 1")
    print(f"检索结果：{len(context['relevant_chars'])}个相关人物")
    
    # 统计
    stats = db.get_stats()
    print(f"数据库统计：{stats}")
    
    db.close()
    print("测试完成！")
