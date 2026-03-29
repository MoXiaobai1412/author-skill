# MySQL 风格资源管理指南

## 📚 概述

author-skill 现已升级为**类 MySQL 数据库结构**的资源管理系统，让资源管理更加规范、直观和强大。

### 核心改进

1. **每个 list.md 都有 desc 部分** - 自描述的表结构定义
2. **类 MySQL 命令** - 使用熟悉的数据库操作方式
3. **智能 schema 推断** - 自动为现有项目添加 desc
4. **向后兼容** - 支持旧格式，平滑迁移

---

## 🗂️ list.md 结构

每个 `list.md` 文件由两部分组成：

```markdown
# {表名}

## desc
| 列名 | 类型 | 主键 | 必填 | 说明 | 示例 |
|------|------|------|------|------|------|
| name | text | YES | YES | 资源名（重要资源加⭐） | 林远 ⭐ |
| summary | text | NO | YES | 资源概况 | 主角，少年，坚毅 |
| relations | text | NO | NO | 相关资源 | 清风（救命恩人） |
| chapter | text | NO | NO | 首次出现章节 | 第一卷第 1 章 |

## data
| 资源名 | 资源概况 | 相关资源 | 出现章节 |
|--------|----------|----------|----------|
| 林远 ⭐ | 主角，少年，坚毅 | 清风（救命恩人）、林父（父亲） | 第一卷第 1 章 |
| 清风 | 散修，路过救下林远 | 林远（救命恩人） | 第一卷第 1 章 |
```

### desc 部分（元数据区）

类似 MySQL 的 `DESCRIBE table` 命令输出：

| 列 | 说明 | 值 |
|----|------|-----|
| 列名 | 字段英文名（程序内部使用） | name, summary, relations |
| 类型 | 数据类型 | text, number, datetime |
| 主键 | 是否主键（值必须唯一） | YES, NO |
| 必填 | 是否必填字段 | YES, NO |
| 说明 | 字段的详细描述（中文友好名称） | 资源名（重要资源加⭐） |
| 示例 | 示例值 | 林远 ⭐ |

### data 部分（数据区）

实际的数据表格，列名使用 desc 中"说明"列的中文友好名称。

---

## 🛠️ 命令参考

### 查看 Schema

```bash
# 查看人物库的表结构
python resource_manager.py schema 仙途 D:/novel 人物库

# 或使用 list_manager
python list_manager.py schema 仙途 D:/novel 资源库/人物库

# 输出示例：
## 人物库 Schema
| 列名 | 类型 | 主键 | 必填 | 说明 | 示例 |
|------|------|------|------|------|------|
| name | text | YES | YES | 资源名（重要资源加⭐） | 林远 ⭐ |
| summary | text | NO | YES | 资源概况 | 主角，少年，坚毅 |
| relations | text | NO | NO | 相关资源 | 清风（救命恩人） |
| chapter | text | NO | NO | 首次出现章节 | 第一卷第 1 章 |
```

### 资源管理

```bash
# 添加资源
python resource_manager.py add 仙途 D:/novel 人物库 林远 "主角，少年，坚毅" "清风（救命恩人）"

# 列出资源（按 schema 定义的列显示）
python resource_manager.py list 仙途 D:/novel 人物库

# 搜索资源
python resource_manager.py search 仙途 D:/novel 人物库 林

# 获取资源详情
python resource_manager.py get 仙途 D:/novel 人物库 林远

# 编辑资源
python resource_manager.py edit 仙途 D:/novel 人物库 林远

# 删除资源
python resource_manager.py del 仙途 D:/novel 人物库 林远
```

### Schema 管理

```bash
# 创建 desc（为新项目）
python schema_manager.py create 仙途 D:/novel 资源库/人物库

# 添加列
python schema_manager.py update 仙途 D:/novel 资源库/人物库 --add "tags:text:NO:NO:标签：修仙"

# 移除列
python schema_manager.py update 仙途 D:/novel 资源库/人物库 --remove "tags"

# 批量初始化现有项目
python init_schema.py 仙途 D:/novel
```

---

## 📋 预定义 Schema 模板

以下路径会自动使用预定义的 schema 模板：

### 资源库级别

| 路径 | 表名 | 主要列 |
|------|------|--------|
| 资源库 | 资源库索引 | sub_lib, purpose, usage |

### 子库级别

| 路径 | 表名 | 主要列 |
|------|------|--------|
| 资源库/人物库 | 人物库索引 | name, summary, relations, chapter |
| 资源库/设定库 | 设定库索引 | name, summary, relations, chapter |
| 资源库/伏笔库 | 伏笔库索引 | name, summary, status, plan_chapter, actual_chapter |
| 资源库/高光库 | 高光库索引 | name, summary, chapter, type |
| 资源库/历史库 | 历史库索引 | name, summary, time, impact |

### 大纲/概括级别

| 路径 | 表名 | 主要列 |
|------|------|--------|
| 大纲 | 大纲索引 | volume, summary, status |
| 大纲/{卷名} | {卷名}章纲索引 | chapter, summary, status |
| 概括 | 概括索引 | volume, summary, status |
| 概括/{卷名} | {卷名}章概括索引 | chapter, summary, status |

### 其他

| 路径 | 表名 | 主要列 |
|------|------|--------|
| 写作要求 | 写作要求索引 | file, purpose, usage |

---

## 🔄 迁移指南

### 为新项目初始化

```bash
# 1. 创建新书（会自动创建带 desc 的 list.md）
python init_book.py 仙途 D:/novel

# 2. 或使用 schema_manager 手动创建
python schema_manager.py create 仙途 D:/novel 资源库/人物库
```

### 为现有项目批量添加 desc

```bash
# 一键初始化所有 list.md 的 desc 部分
python init_schema.py 仙途 D:/novel

# 输出：
# 📚 开始为《仙途》初始化 schema
# ✓ 已备份到：D:/novel/库/仙途_backup_20260329_112500
# 找到 10 个 list.md 文件
# ✓ 资源库 - desc 已创建
# ✓ 资源库/人物库 - desc 已创建
# ...
# ✅ 初始化完成！
#    更新：10 个文件
#    跳过：0 个文件
#    备份：D:/novel/库/仙途_backup_20260329_112500
```

### 手动迁移单个文件

1. 查看现有列结构
2. 使用 `schema_manager.py create` 创建 desc
3. 验证 data 部分与 desc 匹配

---

## 💡 最佳实践

### 1. 先查看 schema，再操作

```bash
# 操作前先了解表结构
python resource_manager.py schema 仙途 D:/novel 人物库

# 确认列名和必填字段后再添加资源
python resource_manager.py add 仙途 D:/novel 人物库 林远 "主角，少年，坚毅" "清风"
```

### 2. 保持 desc 与 data 一致

- 添加新列时，先更新 desc，再更新 data
- 使用 `schema_manager.py update` 自动同步

### 3. 使用预定义模板

- 预定义模板已优化列结构
- 避免手动创建导致的不一致

### 4. 定期同步检查

```bash
# 检查 list.md 与实际文件是否一致
python list_manager.py sync 仙途 D:/novel 资源库/人物库
```

### 5. 重要资源标记

- 在 name 列加 `⭐` 标记重要资源
- 如：主角、贯穿全文的伏笔、核心设定

---

## 🎯 优势对比

### 旧格式

```markdown
# 人物库索引

| 资源名 | 资源概况 | 相关资源 |
|--------|----------|----------|
| 林远 | 主角，少年，坚毅 | 清风（救命恩人） |
```

**问题：**
- ❌ 列含义不明确
- ❌ 不知道哪些列是必填的
- ❌ 无法验证数据完整性
- ❌ 新增列时需要手动修改所有地方

### 新格式（MySQL 风格）

```markdown
# 人物库索引

## desc
| 列名 | 类型 | 主键 | 必填 | 说明 | 示例 |
|------|------|------|------|------|------|
| name | text | YES | YES | 资源名（重要资源加⭐） | 林远 ⭐ |
| summary | text | NO | YES | 资源概况 | 主角，少年，坚毅 |
| relations | text | NO | NO | 相关资源 | 清风（救命恩人） |

## data
| 资源名 | 资源概况 | 相关资源 |
|--------|----------|----------|
| 林远 ⭐ | 主角，少年，坚毅 | 清风（救命恩人） |
```

**优势：**
- ✅ 自文档化 - desc 清晰定义每列含义
- ✅ 类型安全 - 明确定义必填性和数据类型
- ✅ 易于扩展 - 添加新列时先更新 desc
- ✅ 类 MySQL 体验 - 使用熟悉的数据库概念
- ✅ 向后兼容 - 支持旧格式 list.md

---

## 📖 示例：完整工作流程

### 场景：添加新人物

```bash
# 1. 查看 schema，了解需要哪些字段
python resource_manager.py schema 仙途 D:/novel 人物库

# 输出：
# | 列名 | 类型 | 主键 | 必填 | 说明 | 示例 |
# |------|------|------|------|------|------|
# | name | text | YES | YES | 资源名（重要资源加⭐） | 林远 ⭐ |
# | summary | text | NO | YES | 资源概况 | 主角，少年，坚毅 |
# | relations | text | NO | NO | 相关资源 | 清风（救命恩人） |
# | chapter | text | NO | NO | 首次出现章节 | 第一卷第 1 章 |

# 2. 添加人物（必填字段：name, summary）
python resource_manager.py add 仙途 D:/novel 人物库 清风 "散修，路过救下林远" "林远（救命恩人）"

# 3. 验证添加成功
python resource_manager.py list 仙途 D:/novel 人物库

# 4. 更新出现章节（可选字段）
python resource_manager.py update_chapter 仙途 D:/novel 人物库 清风 "第一卷第 1 章"

# 5. 标记为重要资源（可选）
python resource_manager.py important 仙途 D:/novel 人物库 清风 是
```

### 场景：自定义扩展

```bash
# 为人物库添加"标签"列
python schema_manager.py update 仙途 D:/novel 资源库/人物库 --add "tags:text:NO:NO:标签（用逗号分隔）:修仙，主角"

# 查看更新后的 schema
python resource_manager.py schema 仙途 D:/novel 人物库

# 现在添加人物时可以带标签
python resource_manager.py add 仙途 D:/novel 人物库 林远 "主角，少年，坚毅" "清风" "第一卷第 1 章" "修仙，主角"
```

---

## 🔧 故障排除

### Q: list.md 没有 desc 部分怎么办？

```bash
# 方法 1：批量初始化
python init_schema.py 仙途 D:/novel

# 方法 2：手动创建
python schema_manager.py create 仙途 D:/novel 资源库/人物库
```

### Q: desc 和 data 列数不匹配？

```bash
# 检查 schema
python resource_manager.py schema 仙途 D:/novel 人物库

# 手动编辑 list.md，确保 data 列数与 desc 一致
# 或使用 sync 命令
python list_manager.py sync 仙途 D:/novel 资源库/人物库
```

### Q: 如何恢复备份？

```bash
# init_schema.py 会自动创建备份
# 备份路径：D:/novel/库/仙途_backup_YYYYMMDD_HHMMSS

# 手动恢复
cp -r D:/novel/库/仙途_backup_20260329_112500/* D:/novel/库/仙途/
```

---

## 📝 总结

通过引入 MySQL 风格的 desc 部分，author-skill 的资源管理现在：

1. **更规范** - 每个 list.md 都有清晰的表结构定义
2. **更安全** - 必填字段和类型检查减少错误
3. **更易用** - 类 MySQL 命令降低学习成本
4. **更灵活** - 支持自定义扩展和模板

开始使用吧！

```bash
# 快速开始
python init_schema.py 你的书名 你的项目根目录
```
