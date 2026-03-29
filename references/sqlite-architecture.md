# 🗄️ SQLite 索引架构说明

**版本：** v4.0 (SQLite 索引 + MD 内容)  
**架构设计：** 2026-03-29

---

## 🎯 核心设计理念

**SQLite 用于索引，.md 文件用于内容**

```
┌─────────────────────────────────────┐
│  AI 检索流程                        │
├─────────────────────────────────────┤
│ 1. AI 生成查询命令                   │
│    ↓                               │
│ 2. SQLite 查询索引（毫秒级）         │
│    ↓                               │
│ 3. 获取资源 path                   │
│    ↓                               │
│ 4. 读取.md 文件获取详细内容         │
└─────────────────────────────────────┘
```

---

## 📊 架构对比

### ❌ 旧架构（纯 Markdown）

```
books/<书名>/
└── 资源库/
    ├── 人物库/
    │   ├── list.md（索引）
    │   └── 林远.md（内容）
    └── 设定库/
        ├── list.md（索引）
        └── 青云宗.md（内容）
```

**问题：**
- 查询需要解析多个 list.md 文件
- 复杂查询困难（JOIN、WHERE）
- 性能慢（文本解析）

### ✅ 新架构（SQLite 索引 + MD 内容）

```
books/<书名>/
├── source.db（SQLite 索引）
└── 资源档案/
    ├── 人物/
    │   └── 林远.md（详细内容）
    └── 设定/
        └── 青云宗.md（详细内容）
```

**优势：**
- SQLite 索引查询（毫秒级）
- 支持复杂 SQL 查询
- .md 文件存储详细内容
- 两者结合，优势互补

---

## 🗂️ 数据库表结构

### 6 个核心表

| 表名 | 中文名 | 用途 |
|------|--------|------|
| characters | 人物表 | 所有角色索引 |
| settings | 设定表 | 世界观、设定索引 |
| foreshadowing | 伏笔表 | 伏笔索引 |
| history | 历史事件表 | 背景历史索引 |
| climax | 高潮事件表 | 高潮/名场面索引 |
| items | 道具表 | 物品/法器索引 |

### 通用字段（所有表）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | INTEGER | 主键 | 1 |
| name | TEXT | 资源名（唯一） | 林远 ⭐ |
| summary | TEXT | 概况 | 主角，少年，坚毅 |
| relations | TEXT | 相关资源（JSON 数组） | `["settings/青云宗", "characters/清风"]` |
| chapter | TEXT | 出现章节（JSON 数组） | `["卷 1 章 1", "卷 1 章 2"]` |
| priority | INTEGER | 优先级（0-9，越小越重要） | 0（主角） |
| path | TEXT | .md 文件路径 | `/资源档案/人物/林远.md` |
| created_at | TIMESTAMP | 创建时间 | 2026-03-29 13:00:00 |
| updated_at | TIMESTAMP | 更新时间 | 2026-03-29 13:30:00 |

### 特殊字段

**伏笔表：**
- status（状态：未揭露/已揭露/已废弃）
- plan_chapter（计划揭露章节）
- actual_chapter（实际揭露章节）

**历史事件表：**
- time（发生时间）
- impact（影响）

**高潮事件表：**
- type（类型：战斗/情感/反转/成长）
- volume（所属卷）

**道具表：**
- type（类型：武器/防具/丹药/法器/其他）
- owner（持有者）

---

## 🛠️ 工作流程

### 1. 初始化项目

```bash
python scripts/init_book.py 未来救援局 C:\Users\LLxy\.openclaw\workspace\books
```

**创建：**
- 文件夹结构
- source.db 数据库
- 基础文档（总纲、写作要求）

### 2. 添加资源

```bash
# 添加人物
python scripts/resource_manager.py add 未来救援局 C:\Users\LLxy\.openclaw\workspace\books \
  characters "林远 ⭐" "主角，少年，坚毅" \
  "/资源档案/人物/林远.md" --priority=0

# 创建.md 文件（手动或自动）
# 位置：books/未来救援局/资源档案/人物/林远.md
```

### 3. 写作前检索

**AI 执行：**

```python
from database import ResourceDatabase

db = ResourceDatabase("未来救援局", project_root)

# 检索第 5 章相关资源
context = db.retrieve_for_chapter("卷 1 章 5")

# 获取重要人物
for char in context['important_chars']:
    print(f"{char['name']}: {char['summary']}")
    # 读取详细档案
    path = book_path / char['path'].lstrip('/')
    content = path.read_text(encoding='utf-8')
    print(content)

# 检索关键词
context = db.retrieve_by_keywords(["青云宗", "试炼", "筑基"])
```

### 4. 写作后更新

```bash
# 添加出场章节
python scripts/resource_manager.py add_chapter \
  未来救援局 C:\Users\LLxy\.openclaw\workspace\books \
  characters "林远" "卷 1 章 5"

# 更新数据库索引
# （自动，无需手动操作）
```

---

## 📋 优先级规范

| 优先级 | 说明 | 示例 |
|--------|------|------|
| **0** | 核心中的核心 | 主角、世界观 |
| **1-2** | 非常重要 | 主要配角、核心设定、高潮事件 |
| **3-4** | 重要 | 配角、重要设定、伏笔 |
| **5-6** | 普通 | 一般角色、普通设定、道具 |
| **7-9** | 次要 | 龙套、背景设定 |

**查询优化：**
```python
# 只获取重要资源（优先级 <= 3）
important = db.search_by_priority('characters', 3)
```

---

## 🔍 查询示例

### 基础查询

```python
# 获取重要人物
chars = db.get_important_characters(max_priority=3)

# 搜索关键词
results = db.search('characters', '林')

# 按章节查询
chapter_5 = db.search_by_chapter('characters', '卷 1 章 5')

# 获取未揭露伏笔
vows = db.get_active_foreshadowing()
```

### 智能检索（写作前）

```python
# 为某章节检索所有相关资源
context = db.retrieve_for_chapter("卷 1 章 5")

# context 包含：
# - important_chars: 重要人物（20 个）
# - relevant_chars: 本章相关人物
# - core_settings: 核心设定
# - relevant_settings: 本章相关设定
# - active_foreshadowing: 未揭露伏笔
# - relevant_history: 本章相关历史
# - relevant_climax: 本章相关高潮
# - relevant_items: 本章相关道具
```

### 关键词检索

```python
# 根据关键词检索
context = db.retrieve_by_keywords(["青云宗", "试炼", "筑基"])

# 返回所有相关资源
```

---

## 📝 .md 文件规范

### 人物档案模板

```markdown
# 林远

## 基本信息
| 项目 | 内容 |
|------|------|
| 姓名 | 林远 |
| 性别 | 男 |
| 年龄 | 16 |
| 身份 | 青云宗弟子 |
| 性格 | 坚毅、重情义 |
| 目标 | 成为最强修士 |

## 外貌特征
少年模样，眼神坚毅

## 人物关系
| 人物 | 关系 | 说明 |
|------|------|------|
| 清风 | 救命恩人 | 第 1 章救下林远 |
| 林父 | 父亲 | 已故 |

## 重要经历
| 章节 | 事件 |
|------|------|
| 卷 1 章 1 | 家族灭门 |
| 卷 1 章 2 | 被清风所救 |

## 经典台词
- "我命由我不由天"

## 备注
```

### 设定档案模板

```markdown
# 青云宗

## 类型
宗门组织

## 描述
东域第一修仙宗门

## 历史
建立于千年前

## 结构
- 宗主
- 长老会
- 内门弟子
- 外门弟子

## 相关设定
- 修仙体系
- 功法库

## 备注
```

---

## ⚠️ 注意事项

### 1. 路径规范

```
✅ 正确：/资源档案/人物/林远.md
❌ 错误：books/未来救援局/资源档案/人物/林远.md
```

**path 字段存储相对路径**（相对于书籍文件夹）

### 2. JSON 格式

```python
# relations 字段
["settings/青云宗", "characters/清风"]

# chapter 字段
["卷 1 章 1", "卷 1 章 2", "卷 2 章 5"]
```

### 3. 优先级设置

```python
# 主角：priority=0
# 重要配角：priority=1-2
# 普通角色：priority=5
# 龙套：priority=8-9
```

### 4. 备份策略

```bash
# 定期备份数据库
cp books/<书名>/source.db books/<书名>/source.db.backup

# .md 文件用 Git 管理
git add books/<书名>/资源档案/
```

---

## 🚀 优势总结

| 维度 | 纯 Markdown | SQLite 索引 + MD |
|------|-----------|------------------|
| **查询速度** | 慢（秒级） | ✅ 快（毫秒级） |
| **复杂查询** | ❌ 困难 | ✅ 简单（SQL） |
| **内容阅读** | ✅ 方便 | ✅ 方便 |
| **数据一致性** | ❌ 易出错 | ✅ 事务保证 |
| **备份** | 多文件 | ✅ 单文件 + Git |
| **扩展性** | ❌ 差 | ✅ 优秀 |

---

**版本：** v4.0  
**最后更新：** 2026-03-29  
**状态：** ✅ 可用
