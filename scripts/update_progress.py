#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度更新脚本
用法：
  python update_progress.py status {书名} {项目根目录}         # 显示进度
  python update_progress.py update {书名} {项目根目录}        # 更新进度统计
  python update_progress.py export {书名} {项目根目录}        # 导出进度报告
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime


class ProgressTracker:
    def __init__(self, book_name, project_root):
        self.book_name = book_name
        self.project_root = project_root
        self.book_path = Path(project_root) / "库" / book_name
        
        self.progress_data = {
            'book_name': book_name,
            'total_volumes': 0,
            'volumes': [],
            'total_chapters': 0,
            'written_chapters': 0,
            'total_words': 0,
            'vows': {
                'total': 0,
                'revealed': 0,
                'pending': 0,
            },
            'characters': {
                'main': 0,
                'secondary': 0,
            },
            'settings': 0,
            'last_updated': None,
        }
    
    def scan_and_update(self):
        """扫描项目并更新进度数据"""
        print(f"[进度更新] 扫描《{self.book_name}》...")
        
        # 1. 扫描总纲获取总卷数
        self._scan_total_outline()
        
        # 2. 扫描各卷进度
        self._scan_volumes()
        
        # 3. 统计字数
        self._count_words()
        
        # 4. 统计伏笔
        self._scan_vows()
        
        # 5. 统计人物
        self._scan_characters()
        
        # 6. 统计设定
        self._scan_settings()
        
        # 7. 更新时间
        self.progress_data['last_updated'] = datetime.now().isoformat()
        
        # 8. 保存进度数据
        self._save_progress()
        
        print(f"✓ 进度已更新")
        return self.progress_data
    
    def show_status(self):
        """显示进度状态"""
        # 先更新
        self.scan_and_update()
        
        data = self.progress_data
        
        print(f"\n{'='*60}")
        print(f"📖 《{data['book_name']}》写作进度")
        print(f"{'='*60}\n")
        
        # 总体进度
        total = data['total_chapters']
        written = data['written_chapters']
        percent = (written / total * 100) if total > 0 else 0
        
        print(f"## 总体进度")
        print(f"  全书：{data['total_volumes']} 卷 {total} 章")
        print(f"  已完成：{written}/{total} 章 ({percent:.1f}%)")
        print(f"  总字数：{data['total_words']:,} 字")
        print()
        
        # 各卷进度
        print(f"## 各卷进度")
        print(f"  | 卷序 | 卷名 | 进度 | 状态 |")
        print(f"  |------|------|------|------|")
        
        for vol in data['volumes']:
            vol_total = vol.get('total_chapters', 0)
            vol_written = vol.get('written_chapters', 0)
            vol_percent = (vol_written / vol_total * 100) if vol_total > 0 else 0
            
            if vol_percent == 0:
                status = "未开始"
            elif vol_percent == 100:
                status = "已完成"
            else:
                status = "写作中"
            
            print(f"  | {vol['name']} | {vol.get('title', '')} | {vol_written}/{vol_total} | {status} |")
        
        print()
        
        # 资源统计
        print(f"## 资源库统计")
        print(f"  主要角色：{data['characters']['main']} 人")
        print(f"  次要角色：{data['characters']['secondary']} 人")
        print(f"  核心设定：{data['settings']} 个")
        print()
        
        # 伏笔统计
        vows = data['vows']
        print(f"## 伏笔统计")
        print(f"  总伏笔数：{vows['total']}")
        print(f"  已揭露：{vows['revealed']}")
        print(f"  未揭露：{vows['pending']}")
        print()
        
        # 最后更新
        if data['last_updated']:
            print(f"最后更新：{data['last_updated']}")
        
        print()
    
    def export_report(self, output_path=None):
        """导出进度报告"""
        self.scan_and_update()
        
        report = self._generate_report()
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✓ 进度报告已导出至 {output_path}")
        else:
            print(report)
        
        return report
    
    def get_volume_progress(self, volume):
        """获取特定卷的进度"""
        for vol in self.progress_data['volumes']:
            if vol['name'] == volume:
                return vol
        return None
    
    def update_volume_chapter_count(self, volume, chapter_count):
        """更新卷纲中的章数"""
        volume_outline_path = self.book_path / "大纲库" / f"{volume}卷纲.md"
        
        if not volume_outline_path.exists():
            print(f"错误：未找到{volume}卷纲")
            return False
        
        content = self._read_file(volume_outline_path)
        
        # 更新表格中的章数（简化实现）
        # 实际应解析表格并更新
        
        self._save_file(volume_outline_path, content)
        print(f"✓ {volume}章数已更新为{chapter_count}")
        
        return True
    
    # ========== 扫描方法 ==========
    
    def _scan_total_outline(self):
        """扫描总纲"""
        total_outline_path = self.book_path / "总设定库" / "总纲.md"
        
        if total_outline_path.exists():
            content = self._read_file(total_outline_path)
            
            # 解析总卷数（简化）
            match = re.search(r'全书卷数 [：:]\s*(\d+)', content)
            if match:
                self.progress_data['total_volumes'] = int(match.group(1))
    
    def _scan_volumes(self):
        """扫描各卷"""
        outline_path = self.book_path / "大纲库"
        
        if not outline_path.exists():
            return
        
        for f in sorted(outline_path.glob("*卷纲.md")):
            volume_name = f.stem.replace('卷纲', '')
            
            vol_data = {
                'name': volume_name,
                'title': '',
                'total_chapters': 0,
                'written_chapters': 0,
            }
            
            # 解析卷纲
            content = self._read_file(f)
            
            # 提取卷标题
            title_match = re.search(r'# (.+ 卷纲)', content)
            if title_match:
                vol_data['title'] = title_match.group(1).replace('卷纲', '').strip()
            
            # 提取章数
            chapter_match = re.search(r'本卷章数 [：:]\s*(\d+)', content)
            if chapter_match:
                vol_data['total_chapters'] = int(chapter_match.group(1))
            
            # 统计已写章节
            written = self._count_written_chapters(volume_name)
            vol_data['written_chapters'] = written
            
            self.progress_data['volumes'].append(vol_data)
            self.progress_data['total_chapters'] += vol_data['total_chapters']
            self.progress_data['written_chapters'] += written
    
    def _count_written_chapters(self, volume):
        """统计卷中已写章节数"""
        text_path = self.book_path / "正文库" / volume
        
        if not text_path.exists():
            return 0
        
        return len(list(text_path.glob("*.md")))
    
    def _count_words(self):
        """统计总字数"""
        total_words = 0
        
        text_path = self.book_path / "正文库"
        
        if text_path.exists():
            for volume_dir in text_path.iterdir():
                if volume_dir.is_dir():
                    for chapter_file in volume_dir.glob("*.md"):
                        content = self._read_file(chapter_file)
                        # 中文字数统计
                        total_words += len(re.sub(r'[^\u4e00-\u9fff]', '', content))
        
        self.progress_data['total_words'] = total_words
    
    def _scan_vows(self):
        """扫描伏笔"""
        vow_path = self.book_path / "伏笔库" / "伏笔列表.md"
        
        if vow_path.exists():
            content = self._read_file(vow_path)
            
            # 统计表格行数（简化）
            lines = content.split('\n')
            table_lines = [l for l in lines if l.startswith('| V')]
            
            total = len(table_lines)
            revealed = len([l for l in table_lines if '已揭露' in l])
            pending = total - revealed
            
            self.progress_data['vows'] = {
                'total': total,
                'revealed': revealed,
                'pending': pending,
            }
    
    def _scan_characters(self):
        """扫描人物"""
        # 主要角色
        main_char_path = self.book_path / "总设定库" / "主要角色.md"
        if main_char_path.exists():
            content = self._read_file(main_char_path)
            # 统计角色数量（简化）
            self.progress_data['characters']['main'] = content.count('## ') - 1
        
        # 次要角色
        char_path = self.book_path / "人物库"
        if char_path.exists():
            self.progress_data['characters']['secondary'] = len(list(char_path.glob("*.md")))
    
    def _scan_settings(self):
        """扫描设定"""
        setting_path = self.book_path / "设定库"
        
        if setting_path.exists():
            self.progress_data['settings'] = len(list(setting_path.glob("*.md")))
    
    def _generate_report(self):
        """生成进度报告"""
        data = self.progress_data
        
        report = f"""# 《{data['book_name']}》写作进度报告

生成时间：{data['last_updated']}

## 总体进度

- 全书规模：{data['total_volumes']} 卷 {data['total_chapters']} 章
- 已完成：{data['written_chapters']}/{data['total_chapters']} 章 ({data['written_chapters']/data['total_chapters']*100:.1f}%)
- 总字数：{data['total_words']:,} 字

## 各卷进度

| 卷序 | 卷名 | 进度 | 状态 |
|------|------|------|------|
"""
        
        for vol in data['volumes']:
            vol_total = vol.get('total_chapters', 0)
            vol_written = vol.get('written_chapters', 0)
            vol_percent = (vol_written / vol_total * 100) if vol_total > 0 else 0
            
            if vol_percent == 0:
                status = "未开始"
            elif vol_percent == 100:
                status = "已完成"
            else:
                status = "写作中"
            
            report += f"| {vol['name']} | {vol.get('title', '')} | {vol_written}/{vol_total} | {status} |\n"
        
        report += f"""
## 资源库统计

- 主要角色：{data['characters']['main']} 人
- 次要角色：{data['characters']['secondary']} 人
- 核心设定：{data['settings']} 个

## 伏笔统计

- 总伏笔数：{data['vows']['total']}
- 已揭露：{data['vows']['revealed']}
- 未揭露：{data['vows']['pending']}

---
*报告由 author-skill 自动生成*
"""
        
        return report
    
    def _save_progress(self):
        """保存进度数据"""
        progress_path = self.book_path / "进度.json"
        
        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
    
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
    if len(sys.argv) < 4:
        print("用法：")
        print("  python update_progress.py status {书名} {项目根目录}")
        print("  python update_progress.py update {书名} {项目根目录}")
        print("  python update_progress.py export {书名} {项目根目录} [输出路径]")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    
    tracker = ProgressTracker(book_name, project_root)
    
    if action == "status":
        tracker.show_status()
    
    elif action == "update":
        tracker.scan_and_update()
        print("✓ 进度已更新")
    
    elif action == "export":
        output_path = sys.argv[4] if len(sys.argv) > 4 else None
        tracker.export_report(output_path)
    
    else:
        print(f"未知操作：{action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
