#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
写作流程脚本 - 执行 11 步写作流程
说明：本脚本负责流程调度和文件操作，检查/撰写等智能任务由 LLM 完成

用法：
  # 步骤 1：准备上下文（脚本完成）
  python write_chapter.py prepare {书名} {项目根目录} {卷名} {章名}
  
  # 步骤 2：LLM 检查冲突（LLM 完成）
  # LLM 读取 prepare 输出的上下文，进行冲突检测
  
  # 步骤 3：LLM 撰写章纲（LLM 完成）
  # LLM 根据上下文撰写章纲
  
  # 步骤 4：LLM 检查章纲（LLM 完成）
  # LLM 检查章纲质量
  
  # 步骤 5：LLM 撰写正文（LLM 完成）
  # LLM 根据章纲撰写正文
  
  # 步骤 6：LLM 检查正文（LLM 完成）
  # LLM 检查正文质量
  
  # 步骤 7-11：保存和更新（脚本完成）
  python write_chapter.py save {书名} {项目根目录} {卷名} {章名} --outline "章纲内容" --text "正文内容" --summary "概括内容"
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


class ChapterWorkflow:
    def __init__(self, book_name, project_root, volume, chapter):
        self.book_name = book_name
        self.project_root = project_root
        self.volume = volume
        self.chapter = chapter
        self.book_path = Path(project_root) / "库" / book_name
        
        # 路径定义
        self.resource_lib = self.book_path / "资源库"
        self.text_path = self.book_path / "正文"
        self.outline_path = self.book_path / "大纲"
        self.summary_path = self.book_path / "概括"
        self.req_path = self.book_path / "写作要求"
    
    def prepare_context(self):
        """步骤 1：准备上下文（供 LLM 使用）"""
        print(f"\n{'='*60}")
        print(f"《{self.book_name}》{self.volume}{self.chapter} 写作准备")
        print(f"{'='*60}\n")
        
        context = {
            'book_name': self.book_name,
            'volume': self.volume,
            'chapter': self.chapter,
            'timestamp': datetime.now().isoformat(),
        }
        
        # 1. 读取总设定库
        print("[步骤 1] 查阅与规划...")
        
        worldview = self._read_file(self.resource_lib / "设定库" / "世界观.md")
        total_outline = self._read_file(self.outline_path / "总纲.md")
        
        context['worldview'] = worldview
        context['total_outline'] = total_outline
        print("  [OK] 已读取世界观、总纲")
        
        # 2. 读取卷纲
        volume_outline = self._read_file(self.outline_path / self.volume / "卷纲.md")
        context['volume_outline'] = volume_outline
        print(f"  [OK] 已读取{self.volume}卷纲")
        
        # 3. 读取已写章节概括
        volume_summary_path = self.summary_path / self.volume
        previous_summaries = []
        if volume_summary_path.exists():
            for f in sorted(volume_summary_path.glob("*.md")):
                if f.name != "卷概括.md" and f.name != "list.md":
                    summary_content = self._read_file(f)
                    if summary_content:
                        previous_summaries.append({
                            'file': f.name,
                            'content': summary_content
                        })
        
        context['previous_summaries'] = previous_summaries
        print(f"  [OK] 已读取前情提要（{len(previous_summaries)}章）")
        
        # 4. 读取人物库 list.md
        char_list = self._read_list(self.resource_lib / "人物库" / "list.md")
        context['characters_index'] = char_list
        print(f"  [OK] 已读取人物库索引（{len(char_list)}人）")
        
        # 5. 读取设定库 list.md
        setting_list = self._read_list(self.resource_lib / "设定库" / "list.md")
        context['settings_index'] = setting_list
        print(f"  [OK] 已读取设定库索引（{len(setting_list)}个）")
        
        # 6. 读取伏笔库
        vow_list = self._read_list(self.resource_lib / "伏笔库" / "list.md")
        vow_data = self._read_file(self.resource_lib / "伏笔库" / "伏笔列表.md")
        context['vows_index'] = vow_list
        context['vows_data'] = vow_data
        print(f"  [OK] 已读取伏笔库（{len(vow_list)}个伏笔）")
        
        # 7. 读取写作要求
        preferences = {}
        if self.req_path.exists():
            for f in self.req_path.glob("*.md"):
                if f.name != "list.md":
                    preferences[f.stem] = self._read_file(f)
        
        context['preferences'] = preferences
        print(f"  [OK] 已读取写作要求（{len(preferences)}个文件）")
        
        # 8. 输出上下文（供 LLM 使用）
        print(f"\n{'='*60}")
        print("上下文已准备完成，以下是关键信息摘要：")
        print(f"{'='*60}\n")
        
        print(f"## 当前任务")
        print(f"书名：《{self.book_name}》")
        print(f"章节：{self.volume}{self.chapter}")
        print()
        
        print(f"## 总纲概览")
        if total_outline:
            # 提取总纲中的卷数信息
            if "全书卷数" in total_outline:
                lines = total_outline.split('\n')
                for line in lines[:10]:
                    print(f"  {line}")
        print()
        
        print(f"## {self.volume}卷纲")
        if volume_outline:
            lines = volume_outline.split('\n')
            for line in lines[:15]:
                print(f"  {line}")
        print()
        
        print(f"## 人物库（前 5 人）")
        for char in char_list[:5]:
            star = "⭐" if "⭐" in char.get('name', '') else ""
            print(f"  - {char.get('name', '')}{star}: {char.get('summary', '')}")
            print(f"    相关：{char.get('relations', '')}")
            print(f"    出现：{char.get('chapter', '未记录')}")
        if len(char_list) > 5:
            print(f"  ... 还有{len(char_list) - 5}人")
        print()
        
        print(f"## 伏笔状态")
        unrevealed = [v for v in vow_list if '未揭露' in str(v)]
        if unrevealed:
            print(f"  未揭露伏笔：{len(unrevealed)}个")
            for vow in unrevealed[:3]:
                print(f"    - {vow.get('name', '')}: {vow.get('summary', '')}")
        print()
        
        print(f"## 写作要求")
        for name, content in preferences.items():
            print(f"  - {name}.md: {len(content)}字")
        print()
        
        # 9. 输出 JSON 格式上下文（供 LLM 深入分析）
        print(f"{'='*60}")
        print("完整上下文数据（JSON 格式）：")
        print(f"{'='*60}\n")
        
        # 简化 JSON 输出（移除大文件内容）
        json_context = {
            'book_name': context['book_name'],
            'volume': context['volume'],
            'chapter': context['chapter'],
            'worldview_preview': context['worldview'][:500] if context['worldview'] else '',
            'total_outline': context['total_outline'],
            'volume_outline': context['volume_outline'],
            'previous_summaries_count': len(context['previous_summaries']),
            'previous_summaries': context['previous_summaries'][-2:],  # 最近 2 章
            'characters_index': context['characters_index'],
            'settings_index': context['settings_index'],
            'vows_index': context['vows_index'],
            'preferences_keys': list(context['preferences'].keys()),
        }
        
        print(json.dumps(json_context, ensure_ascii=False, indent=2))
        
        print(f"\n{'='*60}")
        print("LLM 任务说明：")
        print(f"{'='*60}")
        print("""
1. 【冲突检测】检查以下内容：
   - 人物身份/关系是否与已有设定矛盾
   - 时间线是否错乱
   - 伏笔状态是否正确（已揭露的不要再次铺设）
   - 新设定是否与总设定库冲突
   - 情节是否与总纲/卷纲冲突

2. 【撰写章纲】根据卷纲中本章的概括，撰写章纲，包括：
   - 核心事件
   - 出场人物及作用
   - 关键场景
   - 伏笔处理
   - 章节结尾

3. 【检查章纲】确认：
   - 逻辑连贯性
   - 伏笔已安排
   - 人物行为与设定一致
   - 符合世界观与大纲

4. 【撰写正文】根据章纲撰写约 2000 字正文

5. 【检查正文】确认符合章纲，无逻辑错误

6. 【生成概括】按格式生成章概括

7. 【更新资源】列出需要新增/更新的人物、设定、伏笔
""")
        
        return context
    
    def save_results(self, outline, text, summary, new_resources=None):
        """步骤 7-11：保存结果并更新"""
        print(f"\n{'='*60}")
        print(f"保存《{self.book_name}》{self.volume}{self.chapter} 结果")
        print(f"{'='*60}\n")
        
        # 保存章纲
        outline_file = self.outline_path / self.volume / f"{self.chapter}.md"
        self._save_file(outline_file, outline)
        print(f"[OK] 章纲已保存：{outline_file}")
        
        # 保存正文
        text_file = self.text_path / self.volume / f"{self.chapter}.md"
        self._save_file(text_file, text)
        print(f"[OK] 正文已保存：{text_file}")
        
        # 保存概括
        summary_file = self.summary_path / self.volume / f"{self.chapter}.md"
        self._save_file(summary_file, summary)
        print(f"[OK] 概括已保存：{summary_file}")
        
        # 更新大纲索引
        self._update_list(self.outline_path / self.volume / "list.md", 
                         self.chapter, "本章概括", "已完成")
        
        # 更新概括索引
        self._update_list(self.summary_path / self.volume / "list.md",
                         self.chapter, "本章概括", "已完成")
        
        # 更新资源库（如有新资源）
        if new_resources:
            print(f"\n## 更新资源库")
            for res in new_resources:
                lib_name = res.get('lib', '人物库')
                name = res.get('name', '')
                summary_text = res.get('summary', '')
                relations = res.get('relations', '')
                chapter = f"{self.volume}{self.chapter}"
                
                self._add_to_resource_list(lib_name, name, summary_text, relations, chapter)
                print(f"  ✓ 新增{lib_name}/{name}")
        
        # 更新卷纲进度
        self._update_volume_progress()
        
        print(f"\n{'='*60}")
        print(f"《{self.book_name}》{self.volume}{self.chapter} 已完成！")
        print(f"{'='*60}")
        print(f"\n提示：")
        print(f"  - 请查阅正文，如需修改请提出具体要求")
        print(f"  - 使用 /git commit 提交更改")
        print(f"  - 使用 /status 查看进度")
    
    # ========== 辅助方法 ==========
    
    def _read_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def _save_file(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _read_list(self, list_path):
        """读取 list.md 为列表"""
        content = self._read_file(list_path)
        entries = []
        
        for line in content.split('\n'):
            if line.startswith('| ') and line.count('|') >= 4:
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 3:
                    entry = {
                        'name': parts[0],
                        'summary': parts[1],
                        'relations': parts[2],
                    }
                    if len(parts) >= 4:
                        entry['chapter'] = parts[3]
                    entries.append(entry)
        
        return entries
    
    def _update_list(self, list_path, name, summary, status):
        """更新 list.md"""
        content = self._read_file(list_path)
        lines = content.split('\n')
        
        # 查找并更新
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f'| {name} |'):
                parts = line.split('|')
                if len(parts) >= 4:
                    parts[3] = f" {status} "
                    lines[i] = '|'.join(parts)
                    updated = True
                    break
        
        if not updated:
            # 添加新条目
            for i, line in enumerate(lines):
                if line.startswith('|----'):
                    new_line = f"| {name} | {summary} | {status} |"
                    lines.insert(i + 1, new_line)
                    break
        
        self._save_file(list_path, '\n'.join(lines))
    
    def _add_to_resource_list(self, lib_name, name, summary, relations, chapter):
        """添加到资源库 list.md"""
        list_path = self.resource_lib / lib_name / "list.md"
        content = self._read_file(list_path)
        lines = content.split('\n')
        
        # 检查是否有章节列
        has_chapter = any('|----' in l and l.count('|') >= 5 for l in lines)
        
        if has_chapter:
            new_line = f"| {name} | {summary} | {relations} | {chapter} |"
        else:
            new_line = f"| {name} | {summary} | {relations} |"
        
        # 找到插入位置
        for i, line in enumerate(lines):
            if line.startswith('|----'):
                lines.insert(i + 1, new_line)
                break
        
        self._save_file(list_path, '\n'.join(lines))
    
    def _update_volume_progress(self):
        """更新卷纲进度"""
        # 简化实现
        pass


def main():
    if len(sys.argv) < 5:
        print("用法：")
        print("  # 步骤 1：准备上下文")
        print("  python write_chapter.py prepare {书名} {项目根目录} {卷名} {章名}")
        print()
        print("  # 步骤 7-11：保存结果（LLM 完成后调用）")
        print("  python write_chapter.py save {书名} {项目根目录} {卷名} {章名}")
        print("    --outline \"章纲内容\"")
        print("    --text \"正文内容\"")
        print("    --summary \"概括内容\"")
        print("    --resources \"新资源 JSON\"")
        sys.exit(1)
    
    action = sys.argv[1]
    book_name = sys.argv[2]
    project_root = sys.argv[3]
    volume = sys.argv[4]
    chapter = sys.argv[5]
    
    workflow = ChapterWorkflow(book_name, project_root, volume, chapter)
    
    if action == "prepare":
        workflow.prepare_context()
    
    elif action == "save":
        # 解析参数
        outline = ""
        text = ""
        summary = ""
        resources = None
        
        i = 6
        while i < len(sys.argv):
            if sys.argv[i] == "--outline" and i + 1 < len(sys.argv):
                outline = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--text" and i + 1 < len(sys.argv):
                text = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--summary" and i + 1 < len(sys.argv):
                summary = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--resources" and i + 1 < len(sys.argv):
                resources = json.loads(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        workflow.save_results(outline, text, summary, resources)
    
    else:
        print(f"错误：未知操作 '{action}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
