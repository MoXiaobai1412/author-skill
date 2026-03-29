#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按需加载上下文脚本
用法：python load_context.py {书名} {项目根目录} [--characters 人物 1,人物 2] [--settings 设定 1,设定 2]
功能：仅加载写作需要的特定人物/设定文件，避免一次性读取所有
"""

import os
import sys
import json
import argparse
from pathlib import Path


class ContextLoader:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / "库" / book_name
        
        self.context = {}
    
    def load_minimal(self, volume, chapter):
        """
        加载最小必要上下文
        仅读取当前章节写作必需的文件
        """
        print(f"[上下文加载] 《{self.book_name}》{volume}{chapter}")
        
        # 1. 总设定库（必需）
        self.context['worldview'] = self._read_optional(
            self.book_path / "总设定库" / "世界观.md"
        )
        self.context['total_outline'] = self._read_optional(
            self.book_path / "总设定库" / "总纲.md"
        )
        
        # 2. 当前卷纲（必需）
        self.context['volume_outline'] = self._read_optional(
            self.book_path / "大纲库" / f"{volume}卷纲.md"
        )
        
        # 3. 当前章纲（如果已存在）
        self.context['chapter_outline'] = self._read_optional(
            self.book_path / "大纲库" / f"{volume}章纲" / f"{chapter}章纲.md"
        )
        
        # 4. 前一章概括（用于连贯性）
        prev_chapter = self._get_previous_chapter(volume, chapter)
        if prev_chapter:
            self.context['previous_summary'] = self._read_optional(
                self.book_path / "概括库" / volume / "章概括" / f"{prev_chapter}概括.md"
            )
        
        # 5. 用户偏好
        self.context['preference'] = self._read_optional(
            self.book_path / "要求库" / "用户偏好.md"
        )
        
        return self.context
    
    def load_characters(self, character_names):
        """
        按需加载特定人物
        :param character_names: 人物名称列表
        """
        characters = {}
        
        for name in character_names:
            # 先在主要角色中查找
            main_char = self._find_character_in_main(name)
            if main_char:
                characters[name] = main_char
                continue
            
            # 再在人物库中查找
            char_file = self.book_path / "人物库" / f"{name}.md"
            if char_file.exists():
                characters[name] = self._read_file(char_file)
            else:
                characters[name] = None  # 未找到
        
        self.context['characters'] = characters
        return characters
    
    def load_settings(self, setting_names):
        """
        按需加载特定设定
        :param setting_names: 设定名称列表
        """
        settings = {}
        
        for name in setting_names:
            setting_file = self.book_path / "设定库" / f"{name}.md"
            if setting_file.exists():
                settings[name] = self._read_file(setting_file)
            else:
                settings[name] = None
        
        self.context['settings'] = settings
        return settings
    
    def load_vows(self, vow_ids=None):
        """
        加载伏笔列表
        :param vow_ids: 特定伏笔 ID 列表（可选）
        """
        vow_file = self.book_path / "伏笔库" / "伏笔列表.md"
        
        if vow_file.exists():
            content = self._read_file(vow_file)
            
            if vow_ids:
                # 只提取指定 ID 的伏笔
                filtered = self._filter_vows_by_ids(content, vow_ids)
                self.context['vows'] = filtered
            else:
                self.context['vows'] = content
        
        return self.context.get('vows', '')
    
    def load_related_chapters(self, volume, chapter, count=3):
        """
        加载前后相关章节（用于连贯性检查）
        :param count: 加载前后各多少章
        """
        related = {
            'previous': [],
            'next': []
        }
        
        chapter_num = self._extract_chapter_num(chapter)
        
        # 加载前几章
        for i in range(1, count + 1):
            prev_num = chapter_num - i
            if prev_num > 0:
                prev_chapter = f"第{prev_num}章"
                content = self._read_optional(
                    self.book_path / "正文库" / volume / f"{prev_chapter}.md"
                )
                if content:
                    related['previous'].append({
                        'chapter': prev_chapter,
                        'content': content
                    })
        
        # 加载后几章（如果是修改已有章节）
        for i in range(1, count + 1):
            next_num = chapter_num + i
            next_chapter = f"第{next_num}章"
            content = self._read_optional(
                self.book_path / "正文库" / volume / f"{next_chapter}.md"
            )
            if content:
                related['next'].append({
                    'chapter': next_chapter,
                    'content': content
                })
        
        self.context['related_chapters'] = related
        return related
    
    def get_context_summary(self):
        """生成上下文摘要（用于提示 AI）"""
        summary = []
        
        if self.context.get('worldview'):
            summary.append("✓ 世界观已加载")
        
        if self.context.get('total_outline'):
            summary.append("✓ 总纲已加载")
        
        if self.context.get('volume_outline'):
            summary.append("✓ 卷纲已加载")
        
        if self.context.get('characters'):
            loaded = sum(1 for v in self.context['characters'].values() if v)
            summary.append(f"✓ 已加载{loaded}个人物")
        
        if self.context.get('settings'):
            loaded = sum(1 for v in self.context['settings'].values() if v)
            summary.append(f"✓ 已加载{loaded}个设定")
        
        if self.context.get('previous_summary'):
            summary.append("✓ 前情提要已加载")
        
        return "\n".join(summary)
    
    # ========== 辅助方法 ==========
    
    def _read_file(self, path):
        """读取文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def _read_optional(self, path):
        """读取可选文件（不存在时返回空字符串）"""
        return self._read_file(path)
    
    def _find_character_in_main(self, name):
        """在主要角色文件中查找人物"""
        main_char_file = self.book_path / "总设定库" / "主要角色.md"
        
        if not main_char_file.exists():
            return None
        
        content = self._read_file(main_char_file)
        
        # 简化查找（实际应使用更精确的解析）
        if name in content:
            return f"[来自主要角色.md] {name} 的相关信息"
        
        return None
    
    def _get_previous_chapter(self, volume, chapter):
        """获取前一章的章号"""
        chapter_num = self._extract_chapter_num(chapter)
        
        if chapter_num > 1:
            return f"第{chapter_num - 1}章"
        
        return None
    
    def _extract_chapter_num(self, chapter):
        """从章名提取数字"""
        import re
        match = re.search(r'第 (\d+) 章', chapter)
        if match:
            return int(match.group(1))
        return 0
    
    def _filter_vows_by_ids(self, content, vow_ids):
        """根据 ID 过滤伏笔"""
        # 简化实现（实际应解析表格）
        return content
    
    def export_context(self, output_path=None):
        """导出上下文为 JSON"""
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, ensure_ascii=False, indent=2)
            print(f"✓ 上下文已导出至 {output_path}")
        
        return self.context


def main():
    parser = argparse.ArgumentParser(description='按需加载写作上下文')
    parser.add_argument('book_name', help='书名')
    parser.add_argument('project_root', help='项目根目录')
    parser.add_argument('--volume', help='卷号（如：第一卷）')
    parser.add_argument('--chapter', help='章号（如：第 1 章）')
    parser.add_argument('--characters', help='要加载的人物（逗号分隔）')
    parser.add_argument('--settings', help='要加载的设定（逗号分隔）')
    parser.add_argument('--vows', help='要加载的伏笔 ID（逗号分隔）')
    parser.add_argument('--related', type=int, default=0, help='加载前后相关章节数')
    parser.add_argument('--output', help='导出上下文到文件')
    
    args = parser.parse_args()
    
    loader = ContextLoader(args.book_name, args.project_root)
    
    # 加载最小上下文
    if args.volume and args.chapter:
        loader.load_minimal(args.volume, args.chapter)
    
    # 按需加载人物
    if args.characters:
        char_list = [c.strip() for c in args.characters.split(',')]
        loader.load_characters(char_list)
    
    # 按需加载设定
    if args.settings:
        setting_list = [s.strip() for s in args.settings.split(',')]
        loader.load_settings(setting_list)
    
    # 加载伏笔
    if args.vows:
        vow_list = [v.strip() for v in args.vows.split(',')]
        loader.load_vows(vow_list)
    
    # 加载相关章节
    if args.related > 0 and args.volume and args.chapter:
        loader.load_related_chapters(args.volume, args.chapter, args.related)
    
    # 显示摘要
    print("\n" + "="*60)
    print("上下文加载完成")
    print("="*60)
    print(loader.get_context_summary())
    print()
    
    # 导出
    if args.output:
        loader.export_context(args.output)


if __name__ == "__main__":
    main()
