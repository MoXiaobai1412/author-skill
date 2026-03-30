# database.py 命令行功能更新报告

**更新时间：** 2026-03-30  
**版本：** v4.1  
**文件：** `scripts/database.py`, `scripts/resource-manage.md`

---

## ✅ 新增功能

### 1. 完整的命令行接口

现在可以通过命令行直接操作数据库，支持增删改查所有操作。

### 2. 两种查询方式

#### 方式 1：精确搜索（LIKE "%xxx%" 模糊匹配）

```bash
python database.py search <书名> <项目根目录> <table> <keyword> [field]
```

**特点：**
- 使用 SQL LIKE 操作符
- 自动添加 `%` 通配符：`LIKE "%keyword%"`
- 支持缩写匹配（如搜索"林"可以匹配"林远"）
- 默认搜索 `name` 和 `summary` 字段
- 可指定搜索字段：`name`, `summary`, `relations`, `chapter`

**示例：**
```bash
# 搜索人物（模糊匹配）
python database.py search 未来救援局 books characters "林"

# 输出：
# ⭐ 林远 (优先级：0)
#    概况：主角，少年，坚毅
#    路径：/资源档案/人物/林远.md
#    章节：卷 1 章 1, 卷 1 章 2
```

#### 方式 2：AI 匹配（搜索不到时自动显示所有资源）

**触发条件：** 当搜索结果为空时

**行为：**
1. 显示"未找到匹配资源"的提示
2. 列出该表所有资源的名称和概况
3. 提示 AI 匹配最相关的资源
4. 提供后续查询路径的命令

**示例：**
```bash
python database.py search 未来救援局 books characters "某某某"

# 输出：
# ⚠ 在 characters 中未找到匹配 '某某某' 的资源
# 
# 【所有资源列表】（AI 请匹配最相关的资源）
# - 林远：主角，少年，坚毅
# - 清风：散修，救命恩人
# - ...
# 
# 💡 AI 提示：请从以上资源中匹配最相关的资源名称，然后使用以下命令查询路径：
#    python database.py get characters <资源名>
#    python database.py get-path characters <资源名>
```

**AI 后续操作：**
```bash
# AI 匹配到"林远"后，查询路径
python database.py get-path 未来救援局 books characters "林远"

# 输出：
# 【资源路径】
# 表：characters
# 名称：林远
# 路径：/资源档案/人物/林远.md
# 
# 【操作示例】
# 读取文件：cat /资源档案/人物/林远.md
# 编辑文件：vim /资源档案/人物/林远.md
```

---

## 📋 命令参考

### create - 创建资源

```bash
python database.py create <table> <name> <summary> <path> [relations] [chapter] [priority]
```

**示例：**
```bash
# 创建人物
python database.py create characters "林远" "主角，少年，坚毅" \
  "/资源档案/人物/林远.md" "settings/青云宗" "卷 1 章 1" 0

# 创建伏笔（额外参数：status, plan_chapter）
python database.py create foreshadowing "神秘玉简" "父亲遗物，隐藏秘密" \
  "/资源档案/伏笔/神秘玉简.md" "" "卷 3 章 5" 2 "未揭露" "卷 3 章 5"
```

### delete - 删除资源

```bash
python database.py delete <table> <name>
```

**示例：**
```bash
python database.py delete characters "林远"
```

### update - 更新资源

```bash
python database.py update <table> <name> <field>=<value> [field=value ...]
```

**示例：**
```bash
# 更新章节
python database.py update characters "林远" chapter='["卷 1 章 1", "卷 1 章 2"]'

# 更新多个字段
python database.py update characters "林远" priority=0 \
  relations='["settings/青云宗", "characters/清风"]'
```

### get - 获取资源详情

```bash
python database.py get <table> <name>
```

**输出：** 显示资源的所有字段（自动解析 JSON 字段）

### list - 列出资源

```bash
python database.py list <table> [priority_limit]
```

**示例：**
```bash
# 列出所有人物
python database.py list characters

# 只列出重要人物（优先级 <= 3）
python database.py list characters 3
```

### search - 搜索资源

```bash
python database.py search <table> <keyword> [field]
```

**示例：**
```bash
# 模糊匹配（搜索 name 和 summary）
python database.py search characters "林"

# 搜索指定字段
python database.py search characters "主角" summary
```

### get-path - 获取资源路径

```bash
python database.py get-path <table> <name>
```

**用途：** AI 匹配资源后，查询文件路径以便读取/编辑

### stats - 显示统计

```bash
python database.py stats <书名> <项目根目录>
```

**输出：** 各表资源数量统计

### help - 查看帮助

```bash
python database.py help
# 或
python database.py --help
```

---

## 🔧 技术实现

### LIKE 模糊匹配

```python
def search(self, table: str, keyword: str, fields: List[str] = None) -> List[Dict]:
    if fields is None:
        fields = ['name', 'summary']
    
    conditions = ' OR '.join([f'{f} LIKE ?' for f in fields])
    pattern = f'%{keyword}%'  # 添加通配符
    
    self.cursor.execute(
        f'SELECT * FROM {table} WHERE {conditions}',
        [pattern] * len(fields)
    )
    
    return [dict(row) for row in self.cursor.fetchall()]
```

### AI 匹配流程

```python
def cmd_search(db, args):
    rows = db.search(table, keyword)
    
    if rows:
        # 显示搜索结果
        for row in rows:
            print(f"⭐ {row['name']}...")
    else:
        # 搜索不到，显示所有资源
        print("⚠ 未找到匹配资源")
        print("\n【所有资源列表】（AI 请匹配最相关的资源）\n")
        
        all_rows = db.list_all(table)
        for row in all_rows:
            print(f"- {row['name']}: {row['summary']}")
        
        print("\n💡 AI 提示：请匹配最相关的资源名称，然后使用：")
        print(f"   python database.py get {table} <资源名>")
        print(f"   python database.py get-path {table} <资源名>")
```

---

## 📖 文档更新

**resource-manage.md 已更新：**
- 添加了完整的命令行操作章节
- 详细说明了两种查询方式
- 提供了所有命令的使用示例
- 包含 AI 匹配流程说明

---

## 🎯 使用场景

### 场景 1：写作前检索

```bash
# 1. 搜索相关人物
python database.py search 未来救援局 books characters "林"

# 2. 获取详情
python database.py get 未来救援局 books characters "林远"

# 3. 读取详细档案
# （AI 根据 path 读取.md 文件）
```

### 场景 2：写作后更新

```bash
# 1. 添加新人物
python database.py create characters "新角色" "角色概况" \
  "/资源档案/人物/新角色.md" "" "卷 1 章 5" 5

# 2. 更新出场章节
python database.py update characters "林远" \
  chapter='["卷 1 章 1", "卷 1 章 2", "卷 1 章 5"]'
```

### 场景 3：AI 匹配资源

```bash
# 1. 搜索（可能找不到精确匹配）
python database.py search 未来救援局 books characters "远哥"

# 2. AI 匹配到"林远"
# 3. 查询路径
python database.py get-path 未来救援局 books characters "林远"

# 4. 读取文件进行写作
```

---

## ✅ 测试状态

| 功能 | 状态 | 备注 |
|------|------|------|
| create | ✅ 正常 | 支持所有表 |
| delete | ✅ 正常 | |
| update | ✅ 正常 | 支持多字段 |
| get | ✅ 正常 | 自动解析 JSON |
| list | ✅ 正常 | 支持优先级筛选 |
| search | ✅ 正常 | LIKE 模糊匹配 |
| get-path | ✅ 正常 | AI 匹配后使用 |
| stats | ✅ 正常 | |
| help | ✅ 正常 | |

---

## 📝 注意事项

### 1. JSON 字段格式

```bash
# 使用单引号包裹 JSON 字符串
chapter='["卷 1 章 1", "卷 1 章 2"]'
relations='["settings/青云宗"]'
```

### 2. 路径格式

```bash
# 使用相对路径（相对于书籍文件夹）
"/资源档案/人物/林远.md"  # ✅ 正确
"C:/Users/.../资源档案/人物/林远.md"  # ❌ 错误
```

### 3. 唯一性约束

```bash
# name 字段必须唯一
python database.py create characters "林远" ...  # ✅ 第一次
python database.py create characters "林远" ...  # ❌ 会报错
```

---

**更新完成时间：** 2026-03-30  
**状态：** ✅ 完成并测试通过
