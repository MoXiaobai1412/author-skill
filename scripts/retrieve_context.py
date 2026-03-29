#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retrieve_context.py - 写作前检索相关资源

用法：
  python retrieve_context.py {书名} {项目根目录} --chapter {章节名}
  python retrieve_context.py {书名} {项目根目录} --characters "林远，清风"
  python retrieve_context.py {书名} {项目根目录} --all

功能：
  1. 根据章节名检索相关人物、场景、设定
  2. 读取相关资源文件
  3. 生成写作前检索报告
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


class ContextRetriever:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = Path(project_root)
        self.book_path = self.project_root / book_name
        self.resource_lib = self.book_path / "资源库"
    
    def retrieve_by_chapter(self, chapter_name):
        """根据章节名检索相关资源"""
        print(f"\n📖 写作前检索 - 《{self.book_name}》{chapter_name}\n")
        
        report = {
            'chapter': chapter_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'characters': [],
            'settings': [],
            'scenes': [],
            'foreshadowing': [],
            'history': [],
        }
        
        # 1. 读取大纲，获取本章信息
        outline_content = self._try_read_chapter_outline(chapter_name)
        if outline_content:
            print("📋 本章细纲")
            print(outline_content[:500])
            print()
        
        # 2. 检索人物库
        characters = self._retrieve_characters(chapter_name)
        report['characters'] = characters
        
        # 3. 检索设定库
        settings = self._retrieve_settings(chapter_name)
        report['settings'] = settings
        
        # 4. 检索场景库
        scenes = self._retrieve_scenes(chapter_name)
        report['scenes'] = scenes
        
        # 5. 检索伏笔库
        foreshadowing = self._retrieve_foreshadowing(chapter_name)
        report['foreshadowing'] = foreshadowing
        
        # 6. 检索历史库
        history = self._retrieve_history(chapter_name)
        report['history'] = history
        
        # 7. 生成检索报告
        self._print_report(report)
        
        return report
    
    def retrieve_by_characters(self, character_names):
        """根据人物名检索相关资源"""
        print(f"\n📖 写作前检索 - 《{self.book_name}》\n")
        print(f"检索人物：{', '.join(character_names)}\n")
        
        report = {
            'characters': [],
            'related_settings': [],
            'related_scenes': [],
        }
        
        # 检索每个人物
        for char_name in character_names:
            char_data = self._get_character_detail(char_name)
            if char_data:
                report['characters'].append(char_data)
        
        self._print_character_report(report)
        
        return report
    
    def retrieve_all(self):
        """检索所有资源（用于全面了解）"""
        print(f"\n📖 全面检索 - 《{self.book_name}》\n")
        
        # 读取所有 list.md
        for lib_name in ['人物库', '设定库', '场景库', '伏笔库', '历史库']:
            lib_path = self.resource_lib / lib_name
            if lib_path.exists():
                list_path = lib_path / "list.md"
                if list_path.exists():
                    print(f"\n【{lib_name}】")
                    with open(list_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 只打印 data 部分
                        if '## data' in content:
                            data_part = content.split('## data')[1]
                            lines = data_part.strip().split('\n')[:10]  # 前 10 行
                            for line in lines:
                                if line.strip():
                                    print(f"  {line}")
    
    def _try_read_chapter_outline(self, chapter_name):
        """尝试读取本章细纲"""
        # 查找章节文件夹
        for root, dirs, files in os.walk(self.book_path / "正文"):
            if chapter_name in root or any(chapter_name.replace('第', '').replace('章', '') in f for f in files):
                outline_path = Path(root) / "细纲.md"
                if outline_path.exists():
                    with open(outline_path, 'r', encoding='utf-8') as f:
                        return f.read()
        return None
    
    def _retrieve_characters(self, chapter_name):
        """检索相关人物"""
        characters = []
        char_lib = self.resource_lib / "人物库"
        
        if not char_lib.exists():
            return characters
        
        # 读取人物库 list.md
        list_path = char_lib / "list.md"
        if list_path.exists():
            with open(list_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单检索：读取所有人物
                if '## data' in content:
                    data_part = content.split('## data')[1]
                    lines = data_part.strip().split('\n')
                    for line in lines:
                        if line.startswith('| ') and '|' in line:
                            parts = [p.strip() for p in line.split('|')[1:-1]]
                            if len(parts) >= 2 and parts[0]:
                                characters.append({
                                    'name': parts[0],
                                    'summary': parts[1] if len(parts) > 1 else '',
                                })
        
        # 读取重要人物详情
        important_chars = [c for c in characters if '⭐' in c['name']]
        for char in important_chars[:5]:  # 最多 5 个重要人物
            char_detail = self._get_character_detail(char['name'].replace(' ⭐', ''))
            if char_detail:
                char['detail'] = char_detail
        
        print(f"👥 相关人物（{len(characters)}人）")
        for char in characters[:10]:  # 显示前 10 个
            print(f"  - {char['name']}: {char['summary'][:50]}")
        print()
        
        return characters
    
    def _get_character_detail(self, char_name):
        """获取人物详情"""
        char_path = self.resource_lib / "人物库" / f"{char_name}.md"
        if char_path.exists():
            with open(char_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 只返回关键信息
                lines = content.split('\n')[:30]  # 前 30 行
                return '\n'.join(lines)
        return None
    
    def _retrieve_settings(self, chapter_name):
        """检索相关设定"""
        settings = []
        setting_lib = self.resource_lib / "设定库"
        
        if not setting_lib.exists():
            return settings
        
        list_path = setting_lib / "list.md"
        if list_path.exists():
            with open(list_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '## data' in content:
                    data_part = content.split('## data')[1]
                    lines = data_part.strip().split('\n')
                    for line in lines:
                        if line.startswith('| ') and '|' in line:
                            parts = [p.strip() for p in line.split('|')[1:-1]]
                            if len(parts) >= 2 and parts[0]:
                                settings.append({
                                    'name': parts[0],
                                    'summary': parts[1] if len(parts) > 1 else '',
                                })
        
        print(f"🌍 相关设定（{len(settings)}个）")
        for setting in settings[:10]:
            print(f"  - {setting['name']}: {setting['summary'][:50]}")
        print()
        
        return settings
    
    def _retrieve_scenes(self, chapter_name):
        """检索相关场景"""
        scenes = []
        scene_lib = self.resource_lib / "场景库"
        
        if not scene_lib.exists():
            return scenes
        
        list_path = scene_lib / "list.md"
        if list_path.exists():
            with open(list_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '## data' in content:
                    data_part = content.split('## data')[1]
                    lines = data_part.strip().split('\n')
                    for line in lines:
                        if line.startswith('| ') and '|' in line:
                            parts = [p.strip() for p in line.split('|')[1:-1]]
                            if len(parts) >= 2 and parts[0]:
                                scenes.append({
                                    'name': parts[0],
                                    'summary': parts[1] if len(parts) > 1 else '',
                                })
        
        print(f"🏛️ 相关场景（{len(scenes)}个）")
        for scene in scenes[:10]:
            print(f"  - {scene['name']}: {scene['summary'][:50]}")
        print()
        
        return scenes
    
    def _retrieve_foreshadowing(self, chapter_name):
        """检索相关伏笔"""
        foreshadowing = []
        vow_lib = self.resource_lib / "伏笔库"
        
        if not vow_lib.exists():
            return foreshadowing
        
        list_path = vow_lib / "list.md"
        if list_path.exists():
            with open(list_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '## data' in content:
                    data_part = content.split('## data')[1]
                    lines = data_part.strip().split('\n')
                    for line in lines:
                        if line.startswith('| ') and '|' in line:
                            parts = [p.strip() for p in line.split('|')[1:-1]]
                            if len(parts) >= 4 and parts[0]:
                                foreshadowing.append({
                                    'name': parts[0],
                                    'status': parts[3] if len(parts) > 3 else '',  # 状态列
                                })
        
        # 只显示未揭露的伏笔
        active_vows = [v for v in foreshadowing if '未揭露' in v.get('status', '')]
        
        print(f"🎯 未揭露伏笔（{len(active_vows)}个）")
        for vow in active_vows[:10]:
            print(f"  - {vow['name']}: {vow.get('status', '')}")
        print()
        
        return active_vows
    
    def _retrieve_history(self, chapter_name):
        """检索相关历史"""
        history = []
        history_lib = self.resource_lib / "历史库"
        
        if not history_lib.exists():
            return history
        
        list_path = history_lib / "list.md"
        if list_path.exists():
            with open(list_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '## data' in content:
                    data_part = content.split('## data')[1]
                    lines = data_part.strip().split('\n')
                    for line in lines:
                        if line.startswith('| ') and '|' in line:
                            parts = [p.strip() for p in line.split('|')[1:-1]]
                            if len(parts) >= 2 and parts[0]:
                                history.append({
                                    'name': parts[0],
                                    'summary': parts[1] if len(parts) > 1 else '',
                                })
        
        print(f"📜 相关历史（{len(history)}个）")
        for hist in history[:10]:
            print(f"  - {hist['name']}: {hist['summary'][:50]}")
        print()
        
        return history
    
    def _print_report(self, report):
        """打印检索报告"""
        print("=" * 60)
        print("📊 写作前检索报告")
        print("=" * 60)
        print(f"书名：《{self.book_name}》")
        print(f"章节：{report['chapter']}")
        print(f"时间：{report['timestamp']}")
        print()
        print(f"已查阅:")
        print(f"  👥 人物：{len(report['characters'])}人")
        print(f"  🌍 设定：{len(report['settings'])}个")
        print(f"  🏛️ 场景：{len(report['scenes'])}个")
        print(f"  🎯 未揭露伏笔：{len(report['foreshadowing'])}个")
        print(f"  📜 历史：{len(report['history'])}个")
        print()
        print("✅ 可以开始写作了！")
        print("=" * 60)
    
    def _print_character_report(self, report):
        """打印人物检索报告"""
        print("=" * 60)
        print("📊 人物检索报告")
        print("=" * 60)
        print(f"书名：《{self.book_name}》")
        print()
        print(f"已查阅 {len(report['characters'])} 个人物档案")
        print()


def main():
    parser = argparse.ArgumentParser(description='写作前检索相关资源')
    parser.add_argument('book_name', help='书名')
    parser.add_argument('project_root', help='项目根目录（books 文件夹）')
    parser.add_argument('--chapter', help='章节名（如：第 01 章）')
    parser.add_argument('--characters', help='人物名列表（逗号分隔）')
    parser.add_argument('--all', action='store_true', help='检索所有资源')
    
    args = parser.parse_args()
    
    if not args.chapter and not args.characters and not args.all:
        parser.print_help()
        print("\n错误：请指定 --chapter、--characters 或 --all")
        sys.exit(1)
    
    retriever = ContextRetriever(args.book_name, args.project_root)
    
    if args.all:
        retriever.retrieve_all()
    elif args.characters:
        characters = [c.strip() for c in args.characters.split(',')]
        retriever.retrieve_by_characters(characters)
    elif args.chapter:
        retriever.retrieve_by_chapter(args.chapter)


if __name__ == "__main__":
    main()
