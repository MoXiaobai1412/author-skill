# 资源库操作大全

## 命令格式说明

所有命令均采用统一的键值对格式：

```bash
python database.py "<书名>" <command> [<key1> <value1> <key2> <value2> ...]
```

**示例：**
```bash
# 创建人物
python database.py "三体" create table characters name "罗辑" summary "主角，面壁者" path "人物库/罗辑.md" priority 0

# 搜索人物
python database.py "三体" search table characters keyword "罗"

# 执行SQL
python database.py "三体" sql "SELECT * FROM characters WHERE priority <= 3"
```

数据库位置固定为：`~/.books/<书名>/source.db`

---

## 📋 常用命令速查

### 创建资源

| 资源类型 | 命令示例 |
|---------|---------|
| **人物** | `python database.py "三体" create table characters name "罗辑" summary "主角，面壁者" path "人物库/罗辑.md" priority 0` |
| **设定** | `python database.py "三体" create table settings name "黑暗森林" summary "宇宙社会学理论" path "设定库/黑暗森林.md" priority 1` |
| **伏笔** | `python database.py "三体" create table foreshadowing name "智子" summary "三体人的智能粒子" path "伏笔库/智子.md" priority 2 status "未揭露" plan_chapter "卷 2 章 1"` |
| **历史** | `python database.py "三体" create table history name "大低谷" summary "人类文明危机时期" path "历史库/大低谷.md" priority 7 time "危机纪元" impact "人口锐减"` |
| **高潮** | `python database.py "三体" create table climax name "黑暗森林打击" summary "三体世界被暴露" path "高潮库/黑暗森林打击.md" priority 2 type "反转" volume "第二卷"` |
| **道具** | `python database.py "三体" create table items name "二向箔" summary "降维打击武器" path "道具库/二向箔.md" priority 6 type "武器" owner "歌者"` |

### 查询资源

| 操作 | 命令 |
|------|------|
| **搜索（模糊匹配）** | `python database.py "三体" search table <表名> keyword "<关键词>" [field <字段名>]` |
| **获取详情** | `python database.py "三体" get table <表名> name "<资源名>"` |
| **获取路径** | `python database.py "三体" get-path table <表名> name "<资源名>"` |
| **列出所有** | `python database.py "三体" list table <表名> [priority_limit <上限>]` |
| **列出相关资源** | `python database.py "三体" list-related table <表名> name "<资源名>"` |
| **查看统计** | `python database.py "三体" stats` |
| **导出数据** | `python database.py "三体" export table <表名> [output_file <文件名>]` |

### 更新资源

| 操作 | 命令 |
|------|------|
| **更新字段** | `python database.py "三体" update table <表名> name "<资源名>" <字段>=<值> [字段=值 ...]` |
| **添加章节** | `python database.py "三体" add-chapter table <表名> name "<资源名>" chapter "<章节>"` |
| **设置优先级** | `python database.py "三体" set-priority table <表名> name "<资源名>" priority <优先级>` |
| **添加相关资源** | `python database.py "三体" add-relation table <表名> name "<资源名>" relation "<相关资源>"` |
| **更新伏笔状态** | `python database.py "三体" update table foreshadowing name "<伏笔名>" status="已揭露" actual_chapter="卷 3 章 5"` |

### 删除资源

```bash
python database.py "三体" delete table <表名> name "<资源名>"
```

### 直接执行 SQL

```bash
python database.py "三体" sql "<SQL语句>"
```

**示例：**
```bash
# 查询所有人物
python database.py "三体" sql "SELECT * FROM characters"

# 更新优先级
python database.py "三体" sql "UPDATE characters SET priority = 1 WHERE name = '罗辑'"

# 统计各表数量
python database.py "三体" sql "SELECT 'characters' as table, COUNT(*) as count FROM characters UNION SELECT 'settings', COUNT(*) FROM settings"
```

---

## 📊 表名对照

| 表名（英文） | 中文名 | 用途 |
|------------|--------|------|
| `characters` | 人物库 | 所有角色 |
| `settings` | 设定库 | 世界观、设定 |
| `foreshadowing` | 伏笔库 | 伏笔 |
| `history` | 历史库 | 背景历史 |
| `climax` | 高潮库 | 高潮事件 |
| `items` | 道具库 | 物品、法器 |

---

## 🎯 优先级规范

| 优先级 | 说明 | 示例 |
|--------|------|------|
| **0-2** | 核心 | 主角、世界观、高潮 |
| **3-5** | 重要 | 主要配角、重要设定、伏笔 |
| **6-10** | 普通 | 一般角色、普通设定 |
| **11-50** | 次要 | 龙套、背景 |
| **51-100** | 边缘 | 一次性提及 |

**使用示例：**
```bash
# 列出重要人物（优先级 <= 3）
python database.py "三体" list table characters priority_limit 3

# 列出核心设定（优先级 <= 5）
python database.py "三体" list table settings priority_limit 5
```

---

## ⚠️ 注意事项

### 1. 路径格式

```bash
# ✅ 正确：相对路径（相对于 ~/.books/<书名>/资源库）
path "人物库/罗辑.md"

# ❌ 错误：绝对路径
path "/home/user/.books/三体/人物库/罗辑.md"
```

### 2. JSON 字段格式

```bash
# 使用单引号包裹 JSON 数组
chapter='["卷 1 章 1", "卷 1 章 2"]'
relations='["settings/黑暗森林"]'
```

### 3. 搜索技巧

```bash
# 模糊匹配（推荐）
python database.py "三体" search table characters keyword "罗"
# 匹配：罗辑、罗宾...

# 指定字段搜索
python database.py "三体" search table characters keyword "主角" field summary
# 只在 summary 字段搜索
```

### 4. AI 匹配流程

```bash
# 1. 搜索（可能找不到精确匹配）
python database.py "三体" search table characters keyword "逻辑"

# 2. 系统返回所有资源列表
# - 罗辑：主角，面壁者
# - 罗莉：配角
# - ...

# 3. AI 匹配最相关的资源名（如"罗辑"）

# 4. 查询路径
python database.py "三体" get-path table characters name "罗辑"

# 5. 读取文件进行写作
```

### 5. SQL 安全提示

- 执行 `sql` 命令前建议先使用 `SELECT` 验证条件，再执行 `UPDATE`/`DELETE`。
- 避免执行 `DROP`、`CREATE` 等结构修改语句。

---

## 📖 快速参考卡片

### 写作前查询工作
```bash
# 检索重要人物
python database.py "三体" list table characters priority_limit 3

# 搜索相关资源
python database.py "三体" search table <表名> keyword "<关键词>"

# 获取路径
python database.py "三体" get-path table <表名> name "<资源名>"
```

### 写作后资源更新工作
```bash
# 添加新资源
python database.py "三体" create table <表名> name "<名>" summary "<概况>" path "<路径>" relations "<相关>" chapter "<章节>" priority <优先级>

# 更新章节
python database.py "三体" update table <表名> name "<名>" chapter='["当前章节"]'

# 添加章节（快捷）
python database.py "三体" add-chapter table <表名> name "<名>" chapter "<当前章节>"

# 设置优先级
python database.py "三体" set-priority table <表名> name "<名>" priority <优先级>

# 添加相关资源
python database.py "三体" add-relation table <表名> name "<名>" relation "<相关资源>"
```

### 一般查询方法
```bash
# 搜索
python database.py "三体" search table <表名> keyword "<关键词>"

# 获取详情
python database.py "三体" get table <表名> name "<资源名>"

# 列出
python database.py "三体" list table <表名> [priority_limit <上限>]

# 列出相关资源
python database.py "三体" list-related table <表名> name "<资源名>"

# 统计
python database.py "三体" stats

# 导出数据
python database.py "三体" export table <表名> [output_file <文件名>]

# 执行 SQL
python database.py "三体" sql "<SQL语句>"
```