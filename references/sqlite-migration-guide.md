# 🗄️ SQLite 数据库迁移指南

**版本：** v4.0 (SQLite)  
**迁移时间：** 2026-03-29

---

## 📊 重大变更

### 存储方式变更

**变更前：**
```
books/<书名>/
├── 资源库/
│   ├── 人物库/
│   │   ├── list.md
│   │   └── 林远.md
│   └── 设定库/
│       ├── list.md
│       └── 青云宗.md
```

**变更后：**
```
books/<书名>/
├── source.db（SQLite 数据库）
└── 资源档案/（可选，存储详细档案）
    ├── 人物/
    │   └── 林远.md
    └── 设定/
        └── 青云宗.md
```

---

## ✅ 迁移步骤

### 步骤 1：备份现有数据

```bash
# 备份整个书籍文件夹
cp -r books/<书名> books/<书名>_backup_$(date +%Y%m%d)
```

### 步骤 2：初始化数据库

```bash
cd skills/author-skill
python scripts/init_database.py <书名> <项目根目录>

# 示例
python scripts/init_database.py 未来救援局 C:\Users\LLxy\.openclaw\workspace\books
```

**功能：**
- 创建 `source.db` 数据库
- 自动从现有 `list.md` 导入数据
- 显示导入统计

### 步骤 3：验证数据

```bash
# 查看统计
python scripts/resource_manager.py stats <书名> <项目根目录>

# 列出人物
python scripts/resource_manager.py list <书名> <项目根目录> 人物库

# 搜索
python scripts/resource_manager.py search <书名> <项目根目录> 人物库 林
```

### 步骤 4：更新工作流

**旧命令（Markdown 文件）：**
```bash
# 不再使用
python scripts/list_manager.py ...
python scripts/schema_manager.py ...
```

**新命令（SQLite）：**
```bash
# 使用新命令
python scripts/resource_manager.py list ...
python scripts/resource_manager.py search ...
```

---

## 🗂️ 数据库结构

### 表结构

#### 1. characters（人物库）
```sql
CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    relations TEXT,
    chapter TEXT,
    is_important INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 2. settings（设定库）
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    relations TEXT,
    chapter TEXT,
    is_important INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 3. scenes（场景库）
```sql
CREATE TABLE scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    relations TEXT,
    chapter TEXT,
    location TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 4. foreshadowing（伏笔库）
```sql
CREATE TABLE foreshadowing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    relations TEXT,
    chapter TEXT,
    status TEXT DEFAULT '未揭露',
    plan_chapter TEXT,
    actual_chapter TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 5. history（历史库）
```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    relations TEXT,
    chapter TEXT,
    time TEXT,
    impact TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 6. character_relations（人物关系库）
```sql
CREATE TABLE character_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    relations TEXT,
    chapter TEXT,
    char_a TEXT,
    char_b TEXT,
    relation_type TEXT,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 7. resource_files（资源档案索引）
```sql
CREATE TABLE resource_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_type TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(resource_type, resource_name)
);
```

---

## 🛠️ 新命令参考

### 资源管理

```bash
# 添加资源
python scripts/resource_manager.py add <书名> <项目根目录> <库名> <资源名> "概况" "相关资源" "章节"

# 列出资源
python scripts/resource_manager.py list <书名> <项目根目录> <库名>
python scripts/resource_manager.py list <书名> <项目根目录> <库名> --important

# 搜索资源
python scripts/resource_manager.py search <书名> <项目根目录> <库名> <关键词>

# 获取详情
python scripts/resource_manager.py get <书名> <项目根目录> <库名> <资源名>

# 编辑资源
python scripts/resource_manager.py edit <书名> <项目根目录> <库名> <资源名>

# 删除资源
python scripts/resource_manager.py del <书名> <项目根目录> <库名> <资源名>
```

### 特殊操作

```bash
# 设置重要资源
python scripts/resource_manager.py important <书名> <项目根目录> <库名> <资源名> 是

# 更新章节
python scripts/resource_manager.py update_chapter <书名> <项目根目录> <库名> <资源名> "第 1,2,3,5 章"

# 查看统计
python scripts/resource_manager.py stats <书名> <项目根目录>

# 伏笔管理
python scripts/resource_manager.py vow_list <书名> <项目根目录>
python scripts/resource_manager.py vow_update <书名> <项目根目录> <伏笔 ID> <状态> [实际揭露章节]
```

---

## 📊 Python API 使用

### 基本使用

```python
from database import ResourceDatabase

# 连接数据库
db = ResourceDatabase("未来救援局", r"C:\Users\LLxy\.openclaw\workspace\books")

# 添加人物
db.add_character("林远 ⭐", "主角，少年，坚毅", "清风（救命恩人）", "第 1,2,3 章", is_important=True)

# 查询
char = db.get_character("林远")
print(char['summary'])

# 搜索
results = db.search('characters', '林')

# 获取重要人物
important = db.get_important_characters()

# 更新章节
db.update_character_chapters("林远", "第 1,2,3,5 章")

# 统计
stats = db.get_stats()

# 关闭连接
db.close()
```

### LLM 检索流程

```python
from database import ResourceDatabase

def retrieve_context(book_name, project_root, chapter_keywords):
    """
    LLM 写作前检索
    
    Args:
        book_name: 书名
        project_root: 项目根目录
        chapter_keywords: 章节关键词 ["第 5 章", "青云宗"]
    
    Returns:
        dict: 检索结果
    """
    db = ResourceDatabase(book_name, project_root)
    
    result = {
        'important_chars': [],
        'relevant_chars': [],
        'relevant_settings': [],
        'active_foreshadowing': []
    }
    
    # 1. 获取重要人物
    important = db.get_important_characters()
    result['important_chars'] = [dict(row) for row in important[:20]]
    
    # 2. 搜索相关人物
    for keyword in chapter_keywords:
        chars = db.search('characters', keyword, 'chapter')
        result['relevant_chars'].extend([dict(row) for row in chars])
    
    # 3. 搜索相关设定
    for keyword in chapter_keywords:
        settings = db.search('settings', keyword, 'chapter')
        result['relevant_settings'].extend([dict(row) for row in settings])
    
    # 4. 获取未揭露伏笔
    vows = db.get_active_foreshadowing()
    result['active_foreshadowing'] = [dict(row) for row in vows[:10]]
    
    db.close()
    return result

# 使用
context = retrieve_context("未来救援局", r"C:\Users\LLxy\.openclaw\workspace\books", ["第 5 章", "青云宗"])
```

---

## 🎯 优势对比

| 特性 | Markdown 文件 | SQLite 数据库 |
|------|-------------|--------------|
| **查询速度** | 慢（文本解析） | ✅ 快（SQL 索引） |
| **复杂查询** | ❌ 困难 | ✅ 简单（JOIN、WHERE） |
| **数据一致性** | ❌ 易出错 | ✅ 事务保证 |
| **并发访问** | ❌ 不支持 | ✅ 支持 |
| **文件大小** | 多个文件 | ✅ 单个文件 |
| **Schema 管理** | 需要 desc | ✅ 表结构自带 |
| **备份** | 多个文件 | ✅ 单个文件 |
| **编码问题** | ⚠️ UTF-8/GBK | ✅ 原生支持 |

---

## ⚠️ 注意事项

### 1. 数据库文件位置

```
books/<书名>/source.db
```

**必须确保：**
- ✅ 数据库文件在书籍文件夹内
- ✅ 与 `资源档案/` 文件夹同级
- ✅ 不要手动修改 .db 文件

### 2. 资源档案文件

**可选但推荐：**
```
books/<书名>/
├── source.db
└── 资源档案/
    ├── 人物/
    │   └── 林远.md
    └── 设定/
        └── 青云宗.md
```

**优势：**
- 详细档案仍然用 Markdown
- 数据库只存储索引和概况
- 结合两者优势

### 3. 迁移后清理

**可选：**
```bash
# 确认数据库正常后，可以归档旧 list.md 文件
mv books/<书名>/资源库 books/<书名>/资源库_backup
```

**建议：**
- 保留 1-2 周
- 确认无问题后再删除

---

## 📝 常见问题

### Q: 如何查看数据库内容？

```bash
# 使用 SQLite 命令行
sqlite3 books/<书名>/source.db

# 查看表
.tables

# 查询人物
SELECT * FROM characters;

# 退出
.quit
```

### Q: 如何备份数据库？

```bash
# 简单复制
cp books/<书名>/source.db books/<书名>/source.db.backup

# 或使用 SQLite 备份
sqlite3 books/<书名>/source.db ".backup 'backup.db'"
```

### Q: 数据库损坏怎么办？

```bash
# 1. 从备份恢复
cp books/<书名>/source.db.backup books/<书名>/source.db

# 2. 重新初始化
python scripts/init_database.py <书名> <项目根目录>
```

### Q: 如何导出为 Markdown？

```python
from database import ResourceDatabase

db = ResourceDatabase("书名", "项目根目录")

# 导出人物库
chars = db.export_to_dict('characters')
for char in chars:
    print(f"{char['name']}: {char['summary']}")

db.close()
```

---

## 🚀 快速开始

```bash
# 1. 初始化数据库
python scripts/init_database.py 未来救援局 C:\Users\LLxy\.openclaw\workspace\books

# 2. 查看统计
python scripts/resource_manager.py stats 未来救援局 C:\Users\LLxy\.openclaw\workspace\books

# 3. 添加新人物
python scripts/resource_manager.py add 未来救援局 C:\Users\LLxy\.openclaw\workspace\books 人物库 "新角色" "角色概况" "相关人物" "第 1 章" --important

# 4. 搜索
python scripts/resource_manager.py search 未来救援局 C:\Users\LLxy\.openclaw\workspace\books 人物库 林

# 5. 列出重要人物
python scripts/resource_manager.py list 未来救援局 C:\Users\LLxy\.openclaw\workspace\books 人物库 --important
```

---

**版本：** v4.0 (SQLite)  
**最后更新：** 2026-03-29  
**状态：** ✅ 可用
