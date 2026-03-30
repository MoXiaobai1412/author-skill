# database.py 功能增强报告

**更新时间：** 2026-03-30  
**版本：** v4.2  
**文件：** `scripts/database.py`, `references/resource-manage.md`

---

## ✅ 新增功能

### 1. add-chapter - 添加章节到资源

**用途：** 快捷地为资源添加出场章节（自动去重排序）

**命令：**
```bash
python database.py add-chapter <书名> <项目根目录> <表名> "<资源名>" "<章节>"
```

**示例：**
```bash
# 为人物添加出场章节
python database.py add-chapter 未来救援局 books characters "林远" "卷 1 章 3"

# 为设定添加出现章节
python database.py add-chapter 未来救援局 books settings "青云宗" "卷 1 章 5"
```

**输出：**
```
[OK] 已添加章节 '卷 1 章 3' 到 characters/林远
```

---

### 2. set-priority - 设置资源优先级

**用途：** 快速设置资源的重要性等级

**命令：**
```bash
python database.py set-priority <书名> <项目根目录> <表名> "<资源名>" <优先级>
```

**示例：**
```bash
# 设置主角优先级为 0（最高）
python database.py set-priority 未来救援局 books characters "林远" 0

# 设置龙套角色优先级为 50
python database.py set-priority 未来救援局 books characters "路人甲" 50
```

**输出：**
```
[OK] 已设置 characters/林远 的优先级为 0
```

---

### 3. add-relation - 添加相关资源

**用途：** 为资源添加关联资源（自动去重）

**命令：**
```bash
python database.py add-relation <书名> <项目根目录> <表名> "<资源名>" "<相关资源>"
```

**示例：**
```bash
# 为人物添加相关资源
python database.py add-relation 未来救援局 books characters "林远" "settings/青云宗"

# 添加多个相关资源（多次执行）
python database.py add-relation 未来救援局 books characters "林远" "characters/清风"
```

**输出：**
```
[OK] 已添加相关资源 'settings/青云宗' 到 characters/林远
```

---

### 4. list-related - 列出相关资源

**用途：** 查看某个资源的所有相关资源

**命令：**
```bash
python database.py list-related <书名> <项目根目录> <表名> "<资源名>"
```

**示例：**
```bash
# 查看林远的相关资源
python database.py list-related 未来救援局 books characters "林远"
```

**输出：**
```
## characters/林远 的相关资源

⭐ 青云宗 (优先级：1)
   概况：东域第一修仙宗门
   路径：/资源档案/设定/青云宗.md

⭐ 清风 (优先级：2)
   概况：散修，救命恩人
   路径：/资源档案/人物/清风.md
```

---

### 5. export - 导出表数据为 JSON

**用途：** 导出整个表的数据用于备份或分析

**命令：**
```bash
python database.py export <书名> <项目根目录> <表名> [输出文件]
```

**示例：**
```bash
# 导出所有人物
python database.py export 未来救援局 books characters characters.json

# 导出到指定文件
python database.py export 未来救援局 books settings settings_backup.json
```

**输出：**
```
[OK] 已导出 10 条记录到 characters.json
```

**导出格式：**
```json
[
  {
    "id": 1,
    "name": "林远 ⭐",
    "summary": "主角，少年，坚毅",
    "relations": "[\"settings/青云宗\"]",
    "chapter": "[\"卷 1 章 1\", \"卷 1 章 2\"]",
    "priority": 0,
    "path": "/资源档案/人物/林远.md"
  },
  ...
]
```

---

## 📋 完整命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `create` | 创建资源 | `python database.py create characters ...` |
| `delete` | 删除资源 | `python database.py delete characters "林远"` |
| `update` | 更新资源 | `python database.py update characters "林远" priority=0` |
| `get` | 获取详情 | `python database.py get characters "林远"` |
| `list` | 列出资源 | `python database.py list characters 3` |
| `search` | 搜索资源 | `python database.py search characters "林"` |
| `get-path` | 获取路径 | `python database.py get-path characters "林远"` |
| `add-chapter` | 添加章节 | `python database.py add-chapter characters "林远" "卷 1 章 3"` |
| `set-priority` | 设置优先级 | `python database.py set-priority characters "林远" 0` |
| `add-relation` | 添加相关资源 | `python database.py add-relation characters "林远" "settings/青云宗"` |
| `list-related` | 列出相关资源 | `python database.py list-related characters "林远"` |
| `export` | 导出数据 | `python database.py export characters characters.json` |
| `stats` | 查看统计 | `python database.py stats 未来救援局 books` |
| `help` | 查看帮助 | `python database.py help` |

---

## 🎯 使用场景

### 场景 1：写作后批量更新

```bash
# 1. 添加新人物
python database.py create characters 未来救援局 books "新角色" "角色概况" \
  "/资源档案/人物/新角色.md" "" "卷 1 章 5" 5

# 2. 更新主角出场章节
python database.py add-chapter 未来救援局 books characters "林远" "卷 1 章 5"

# 3. 添加相关资源
python database.py add-relation 未来救援局 books characters "林远" "characters/新角色"

# 4. 设置新角色优先级
python database.py set-priority 未来救援局 books characters "新角色" 3
```

### 场景 2：查看人物关系网

```bash
# 1. 查看主角的相关资源
python database.py list-related 未来救援局 books characters "林远"

# 2. 导出所有人物关系
python database.py export 未来救援局 books characters characters_relations.json
```

### 场景 3：数据备份

```bash
# 导出所有表
python database.py export 未来救援局 books characters characters_backup.json
python database.py export 未来救援局 books settings settings_backup.json
python database.py export 未来救援局 books foreshadowing foreshadowing_backup.json
```

---

## 📖 文档更新

**references/resource-manage.md 已更新：**
- ✅ 添加了新命令说明
- ✅ 更新了快速参考卡片
- ✅ 添加了高级操作示例
- ✅ 更新了写作后流程

---

## 🔧 技术实现

### add-chapter 实现
```python
def cmd_add_chapter(db, args):
    table, name, chapter = args[0], args[1], args[2]
    db.add_chapter(table, name, chapter)  # 自动去重排序
```

### set-priority 实现
```python
def cmd_set_priority(db, args):
    table, name, priority = args[0], args[1], int(args[2])
    db.update(table, name, priority=priority)
```

### add-relation 实现
```python
def cmd_add_relation(db, args):
    table, name, relation = args[0], args[1], args[2]
    db.add_relation(table, name, relation)  # 自动去重
```

### list-related 实现
```python
def cmd_list_related(db, args):
    table, name = args[0], args[1]
    relations = db.get_relations(table, name)
    for rel in relations:
        print(f"⭐ {rel['name']}...")
```

### export 实现
```python
def cmd_export(db, args):
    table = args[0]
    output_file = args[1] if len(args) > 1 else f"{table}_export.json"
    rows = db.export_to_dict(table)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
```

---

## ✅ 测试状态

| 功能 | 状态 | 备注 |
|------|------|------|
| add-chapter | ✅ 正常 | 自动去重排序 |
| set-priority | ✅ 正常 | |
| add-relation | ✅ 正常 | 自动去重 |
| list-related | ✅ 正常 | 显示详细信息 |
| export | ✅ 正常 | JSON 格式 |

---

**更新完成时间：** 2026-03-30  
**状态：** ✅ 完成并测试通过  
**文档位置：** `references/resource-manage.md`
