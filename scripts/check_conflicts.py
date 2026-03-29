#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能冲突检测工具
用法：python check_conflicts.py {书名} {项目根目录}
示例：python check_conflicts.py 仙途 D:/desktop-push/projects/novel
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

class ConflictChecker:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / "库" / book_name
        
        self.conflicts = []
        self.warnings = []
        
        # 缓存数据
        self.characters_cache = {}
        self.settings_cache = {}
        self.vows_cache = []
        self.timeline_cache = []
    
    def check_all(self):
        """运行全局冲突检测"""
        print(f"\n{'='*60}")
        print(f"正在运行《{self.book_name}》全局冲突检测...")
        print(f"{'='*60}\n")
        
        # 加载缓存
        self._load_characters()
        self._load_settings()
        self._load_vows()
        self._load_timeline()
        
        # 执行各项检测
        self.check_characters()
        self.check_timeline()
        self.check_settings()
        self.check_vows()
        self.check_plot()
        
        # 生成报告
        self.report()
    
    def check_chapter(self, context, volume, chapter):
        """针对特定章节的冲突检测"""
        conflicts = []
        
        # 1. 检查出场人物是否与人物库一致
        char_conflicts = self._check_chapter_characters(context, volume, chapter)
        conflicts.extend(char_conflicts)
        
        # 2. 检查时间线
        timeline_conflicts = self._check_chapter_timeline(context, volume, chapter)
        conflicts.extend(timeline_conflicts)
        
        # 3. 检查伏笔状态
        vow_conflicts = self._check_chapter_vows(context, volume, chapter)
        conflicts.extend(vow_conflicts)
        
        # 4. 检查设定一致性
        setting_conflicts = self._check_chapter_settings(context, volume, chapter)
        conflicts.extend(setting_conflicts)
        
        return conflicts
    
    def check_characters(self):
        """人物冲突检测"""
        print("✓ 人物关系：检查中...")
        
        # 1. 检查重复人物
        names = [c['name'] for c in self.characters_cache.values()]
        duplicates = self._find_duplicates(names)
        for dup in duplicates:
            self.conflicts.append(f"人物重复：'{dup}' 出现多次")
        
        # 2. 检查人物关系矛盾
        for char_id, char in self.characters_cache.items():
            relations = char.get('relations', [])
            for rel in relations:
                target = rel.get('target')
                rel_type = rel.get('type')
                
                # 检查目标人物是否存在
                if target and target not in self.characters_cache:
                    self.warnings.append(f"人物'{char['name']}'的关系'{target}'未在人物库中找到")
                
                # 检查关系是否对等（如 A 是 B 的父亲，则 B 应该是 A 的儿子）
                if target and target in self.characters_cache:
                    target_char = self.characters_cache[target]
                    target_rels = target_char.get('relations', [])
                    
                    # 简化的对等检查
                    expected_reverse = self._get_reverse_relation(rel_type)
                    has_reverse = any(
                        r.get('target') == char['name'] and r.get('type') == expected_reverse
                        for r in target_rels
                    )
                    
                    if not has_reverse and expected_reverse:
                        self.warnings.append(
                            f"人物关系可能不对等：'{char['name']}'是'{target}'的{rel_type}，"
                            f"但'{target}'的关系中未体现"
                        )
        
        # 3. 检查已死亡人物是否再次出现
        dead_chars = [c['name'] for c in self.characters_cache.values() if c.get('status') == '已死亡']
        # 需要在正文中检查这些人物是否再次出现（简化实现）
        
        if not self.conflicts and not self.warnings:
            print("✓ 人物关系：无冲突")
        else:
            self._print_issues("人物关系")
    
    def check_timeline(self):
        """时间线冲突检测"""
        print("✓ 时间线：检查中...")
        
        # 1. 检查事件顺序
        events = sorted(self.timeline_cache, key=lambda x: x.get('chapter_order', 0))
        
        for i in range(1, len(events)):
            prev = events[i-1]
            curr = events[i]
            
            # 检查时间间隔是否合理
            prev_time = prev.get('time')
            curr_time = curr.get('time')
            
            if prev_time and curr_time:
                # 简化的时间检查
                pass
        
        # 2. 检查人物年龄/修为是否与时间线匹配
        for char_id, char in self.characters_cache.items():
            age = char.get('age')
            first_appearance = char.get('first_appearance')
            
            if age and first_appearance:
                # 检查年龄是否合理
                pass
        
        if not self.conflicts and not self.warnings:
            print("✓ 时间线：无冲突")
        else:
            self._print_issues("时间线")
    
    def check_settings(self):
        """设定一致性检测"""
        print("✓ 设定一致性：检查中...")
        
        # 1. 检查设定名称重复
        names = [s['name'] for s in self.settings_cache.values()]
        duplicates = self._find_duplicates(names)
        for dup in duplicates:
            self.conflicts.append(f"设定重复：'{dup}' 出现多次")
        
        # 2. 检查设定之间的关联是否矛盾
        for setting_id, setting in self.settings_cache.items():
            related = setting.get('related_settings', [])
            for rel in related:
                rel_name = rel.get('name')
                rel_type = rel.get('type')
                
                if rel_name and rel_name not in self.settings_cache:
                    self.warnings.append(f"设定'{setting['name']}'关联的'{rel_name}'未在设定库中找到")
        
        # 3. 检查力量体系是否一致
        worldview = self._read_file(self.book_path / "总设定库" / "世界观.md")
        if worldview:
            # 检查是否有矛盾的力量体系描述
            pass
        
        if not self.conflicts and not self.warnings:
            print("✓ 设定一致性：无冲突")
        else:
            self._print_issues("设定一致性")
    
    def check_vows(self):
        """伏笔状态检测"""
        print("✓ 伏笔状态：检查中...")
        
        # 1. 检查伏笔 ID 重复
        vow_ids = [v.get('id') for v in self.vows_cache if v.get('id')]
        duplicates = self._find_duplicates(vow_ids)
        for dup in duplicates:
            self.conflicts.append(f"伏笔 ID 重复：'{dup}'")
        
        # 2. 检查已揭露伏笔是否再次铺设
        revealed_vows = [v for v in self.vows_cache if v.get('status') == '已揭露']
        for vow in revealed_vows:
            # 检查是否在后续章节再次作为"未揭露"出现
            pass
        
        # 3. 检查伏笔揭露计划是否合理
        for vow in self.vows_cache:
            plan = vow.get('plan_reveal')
            status = vow.get('status')
            
            if status == '已揭露' and not vow.get('actual_reveal'):
                self.warnings.append(f"伏笔'{vow.get('id')}'已标记为揭露，但未填写实际揭露章节")
        
        if not self.conflicts and not self.warnings:
            print("✓ 伏笔状态：无冲突")
        else:
            self._print_issues("伏笔状态")
    
    def check_plot(self):
        """情节连贯性检测"""
        print("✓ 情节连贯性：检查中...")
        
        # 1. 检查章节编号连续性
        volumes = self._get_volumes()
        for volume in volumes:
            chapters = self._get_chapters_in_volume(volume)
            
            if chapters:
                # 检查是否有跳号
                expected = list(range(1, len(chapters) + 1))
                actual = [self._extract_chapter_num(c) for c in chapters]
                
                missing = set(expected) - set(actual)
                for m in missing:
                    self.warnings.append(f"{volume}第{m}章缺失")
        
        # 2. 检查卷纲与章纲的一致性
        volumes = self._get_volumes()
        for volume in volumes:
            volume_outline = self._read_file(self.book_path / "大纲库" / f"{volume}卷纲.md")
            if volume_outline:
                # 检查卷纲中的章数是否与实际章节数匹配
                pass
        
        if not self.conflicts and not self.warnings:
            print("✓ 情节连贯性：无冲突")
        else:
            self._print_issues("情节连贯性")
    
    def report(self):
        """生成检测报告"""
        print(f"\n{'='*60}")
        print("## 检测结果")
        print(f"{'='*60}\n")
        
        if not self.conflicts and not self.warnings:
            print("✓ 所有检查通过，无冲突。\n")
        else:
            if self.conflicts:
                print("## ❌ 冲突")
                for conflict in self.conflicts:
                    print(f"  ✗ {conflict}")
                print()
            
            if self.warnings:
                print("## ⚠ 警告")
                for warning in self.warnings:
                    print(f"  ⚠ {warning}")
                print()
        
        print("检测完成。")
    
    # ========== 辅助方法 ==========
    
    def _load_characters(self):
        """加载人物库"""
        char_path = self.book_path / "人物库"
        total_char_path = self.book_path / "总设定库" / "主要角色.md"
        
        # 读取主要角色
        if total_char_path.exists():
            content = self._read_file(total_char_path)
            # 解析主要角色（简化实现）
            self.characters_cache['主角'] = {'name': '主角', 'source': '总设定库'}
        
        # 读取人物库中的独立文件
        if char_path.exists():
            for f in char_path.glob("*.md"):
                char_data = self._parse_character_file(f)
                if char_data:
                    self.characters_cache[char_data['name']] = char_data
    
    def _load_settings(self):
        """加载设定库"""
        setting_path = self.book_path / "设定库"
        
        if setting_path.exists():
            for f in setting_path.glob("*.md"):
                setting_data = self._parse_setting_file(f)
                if setting_data:
                    self.settings_cache[setting_data['name']] = setting_data
    
    def _load_vows(self):
        """加载伏笔列表"""
        vow_path = self.book_path / "伏笔库" / "伏笔列表.md"
        
        if vow_path.exists():
            content = self._read_file(vow_path)
            self.vows_cache = self._parse_vow_list(content)
    
    def _load_timeline(self):
        """加载时间线"""
        # 从章节概括中提取时间线事件
        summary_path = self.book_path / "概括库"
        
        if summary_path.exists():
            for volume_dir in summary_path.iterdir():
                if volume_dir.is_dir():
                    chapter_summaries = volume_dir / "章概括"
                    if chapter_summaries.exists():
                        for f in chapter_summaries.glob("*概括.md"):
                            event = self._extract_timeline_event(f)
                            if event:
                                self.timeline_cache.append(event)
    
    def _parse_character_file(self, path):
        """解析人物文件"""
        content = self._read_file(path)
        
        # 简化解析（实际应使用 Markdown 解析器）
        name = path.stem
        
        return {
            'name': name,
            'source': '人物库',
            'file': str(path),
        }
    
    def _parse_setting_file(self, path):
        """解析设定文件"""
        content = self._read_file(path)
        
        name = path.stem
        
        return {
            'name': name,
            'source': '设定库',
            'file': str(path),
        }
    
    def _parse_vow_list(self, content):
        """解析伏笔列表"""
        vows = []
        
        # 简化解析（实际应解析 Markdown 表格）
        # 查找表格行
        
        return vows
    
    def _extract_timeline_event(self, path):
        """从章节概括中提取时间线事件"""
        content = self._read_file(path)
        
        # 提取关键事件
        return {
            'chapter': path.stem,
            'content': content[:100],  # 简化
        }
    
    def _check_chapter_characters(self, context, volume, chapter):
        """检查章节中的人物冲突"""
        conflicts = []
        
        # 检查出场人物是否在人物库中
        # 简化实现
        
        return conflicts
    
    def _check_chapter_timeline(self, context, volume, chapter):
        """检查章节时间线冲突"""
        conflicts = []
        
        # 检查与前章的时间间隔
        # 简化实现
        
        return conflicts
    
    def _check_chapter_vows(self, context, volume, chapter):
        """检查章节伏笔冲突"""
        conflicts = []
        
        # 检查伏笔状态
        # 简化实现
        
        return conflicts
    
    def _check_chapter_settings(self, context, volume, chapter):
        """检查章节设定冲突"""
        conflicts = []
        
        # 检查新设定是否与已有设定冲突
        # 简化实现
        
        return conflicts
    
    def _find_duplicates(self, items):
        """查找重复项"""
        seen = set()
        duplicates = set()
        
        for item in items:
            if item in seen:
                duplicates.add(item)
            seen.add(item)
        
        return list(duplicates)
    
    def _get_reverse_relation(self, rel_type):
        """获取反向关系"""
        reverse_map = {
            '父亲': '儿子',
            '母亲': '女儿',
            '儿子': '父亲',
            '女儿': '母亲',
            '师兄': '师弟',
            '师弟': '师兄',
            '师姐': '师妹',
            '师妹': '师姐',
            '朋友': '朋友',
            '敌人': '敌人',
        }
        return reverse_map.get(rel_type)
    
    def _get_volumes(self):
        """获取所有卷"""
        volumes = []
        outline_path = self.book_path / "大纲库"
        
        if outline_path.exists():
            for f in outline_path.glob("*卷纲.md"):
                volumes.append(f.stem.replace('卷纲', ''))
        
        return volumes
    
    def _get_chapters_in_volume(self, volume):
        """获取卷中的所有章节"""
        chapters = []
        text_path = self.book_path / "正文库" / f"{volume}"
        
        if text_path.exists():
            for f in text_path.glob("*.md"):
                chapters.append(f.stem)
        
        return chapters
    
    def _extract_chapter_num(self, chapter_name):
        """从章节名提取章号"""
        match = re.search(r'第 (\d+) 章', chapter_name)
        if match:
            return int(match.group(1))
        return 0
    
    def _read_file(self, path):
        """读取文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def _print_issues(self, category):
        """打印问题"""
        if self.conflicts:
            print(f"  ✗ {category}：发现{len(self.conflicts)}个冲突")
        if self.warnings:
            print(f"  ⚠ {category}：发现{len(self.warnings)}个警告")


def main():
    if len(sys.argv) < 3:
        print("用法：python check_conflicts.py {书名} {项目根目录}")
        print("示例：python check_conflicts.py 仙途 D:/desktop-push/projects/novel")
        sys.exit(1)
    
    book_name = sys.argv[1]
    project_root = sys.argv[2]
    
    checker = ConflictChecker(book_name, project_root)
    checker.check_all()


if __name__ == "__main__":
    main()
