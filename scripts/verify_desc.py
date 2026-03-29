#!/usr/bin/env python3
import os

print("\n验证所有 list.md 的 desc 部分\n")

count = 0
for root, dirs, files in os.walk('books'):
    if 'list.md' in files:
        list_path = os.path.join(root, 'list.md')
        with open(list_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_desc = '## desc' in content
        rel_path = root.replace('books\\', '')
        
        if has_desc:
            # 提取 desc 部分
            start = content.find('## desc')
            end = content.find('##', start+5)
            if end == -1:
                end = start + 500
            desc_preview = content[start:end].split('\n')[2:5]
            
            print(f"[OK] {rel_path}")
            # 只打印列名行，避免 emoji 编码问题
            if desc_preview:
                first_col_line = [l for l in desc_preview if '| name' in l.lower() or '| sub_lib' in l.lower() or '| volume' in l.lower() or '| file' in l.lower()]
                if first_col_line:
                    cols = first_col_line[0].split('|')[1:-1]
                    col_names = [c.strip().split()[0] if c.strip() else '' for c in cols[:4]]
                    print(f"     列：{', '.join(col_names)}")
            count += 1
        else:
            print(f"[MISS] {rel_path} - 没有 desc")

print(f"\n总计：{count} 个文件有 desc")
