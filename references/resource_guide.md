# 资源管理指南（MySQL 风格）

## 概述

author-skill 采用**类 MySQL 数据库结构**的资源管理方式：
- 每个文件夹都有 `list.md` 作为索引表
- `list.md` 包含 **desc**（元数据）和 **data**（数据）两部分
- 支持 `schema` 命令查看表结构（类似 `DESCRIBE table`）

## list.md 格式（类 MySQL 结构）

```markdown
# 人物库索引

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
| 青云宗 | 主角所在宗门，正道大派 | 修仙体系、林远（弟子） | 第一卷第 1 章 |
```

### desc 部分说明

| 列 | 说明 | 示例 |
|----|------|------|
| 列名 | 字段英文名（程序使用） | name |
| 类型 | 数据类型 | text/number/datetime |
| 主键 | 是否主键（唯一） | YES/NO |
| 必填 | 是否必填字段 | YES/NO |
| 说明 | 字段详细描述 | 资源名（重要资源加⭐） |
| 示例 | 示例值 | 林远 ⭐ |

### data 部分说明

- 使用中文友好列名（对应 desc 中的"说明"列）
- 每行代表一个资源记录
- 重要资源在 name 列加 `⭐` 标记

## 资源管理命令

### 查看 Schema（新增）

```bash
# 查看人物库的表结构（类似 MySQL DESCRIBE）
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

### 人物管理

```bash
# 添加人物
python resource_manager.py add 仙途 D:/novel 人物库 林远 "主角，少年，坚毅" "清风（救命恩人）"

# 编辑人物（读取文件）
python resource_manager.py edit 仙途 D:/novel 人物库 林远

# 删除人物
python resource_manager.py del 仙途 D:/novel 人物库 林远

# 列出所有人物（按 schema 定义的列显示）
python resource_manager.py list 仙途 D:/novel 人物库

# 获取人物详情
python resource_manager.py get 仙途 D:/novel 人物库 林远

# 搜索人物
python resource_manager.py search 仙途 D:/novel 人物库 林
```

### 设定管理

```bash
# 添加设定
python resource_manager.py set add {书名} {项目根目录} {设定名} [概况] [相关资源]

# 示例
python resource_manager.py set add 仙途 D:/novel 青云宗 "主角所在宗门，正道大派" "修仙体系"

# 编辑设定
python resource_manager.py set edit {书名} {项目根目录} {设定名}

# 删除设定
python resource_manager.py set del {书名} {项目根目录} {设定名}

# 列出所有设定
python resource_manager.py set list {书名} {项目根目录}

# 获取设定详情
python resource_manager.py set get {书名} {项目根目录} {设定名}
```

### 伏笔管理

```bash
# 添加伏笔
python resource_manager.py vow add {书名} {项目根目录} {描述} [计划揭露]

# 示例
python resource_manager.py vow add 仙途 D:/novel "黑衣人身上的特殊标记" "第二卷第 5 章"

# 更新伏笔状态
python resource_manager.py vow update {书名} {项目根目录} {ID} {状态} [实际揭露]

# 示例
python resource_manager.py vow update 仙途 D:/novel V001 已揭露 "第二卷第 5 章"

# 删除伏笔
python resource_manager.py vow del {书名} {项目根目录} {ID}

# 列出所有伏笔
python resource_manager.py vow list {书名} {项目根目录}
```

### list.md 管理

```bash
# 读取 list.md
python list_manager.py read {书名} {项目根目录} {库名}

# 添加条目
python list_manager.py add {书名} {项目根目录} {库名} {资源名} {概况} {相关资源}

# 删除条目
python list_manager.py del {书名} {项目根目录} {库名} {资源名}

# 更新条目
python list_manager.py update {书名} {项目根目录} {库名} {资源名} {新概况} {新相关资源}

# 搜索
python list_manager.py search {书名} {项目根目录} {库名} {关键词}

# 同步（修复 list.md 与实际文件的不一致）
python list_manager.py sync {书名} {项目根目录} {库名}
```

## 工作流程

### 新增人物时的完整流程

1. **创建人物文件**
   ```bash
   python resource_manager.py char add 仙途 D:/novel 林远 "主角，少年，坚毅" ""
   ```
   - 自动创建 `人物库/林远.md`
   - 自动更新 `人物库/list.md`

2. **编辑人物详情**
   ```bash
   python resource_manager.py char edit 仙途 D:/novel 林远
   ```
   - 读取人物文件内容
   - 使用文本编辑器修改后保存

3. **查看人物列表**
   ```bash
   python resource_manager.py char list 仙途 D:/novel
   ```

4. **同步检查**
   ```bash
   python list_manager.py sync 仙途 D:/novel 人物库
   ```
   - 确保 list.md 与实际文件一致

### 写作时查阅资源

1. **通过 list.md 快速定位**
   ```bash
   python list_manager.py search 仙途 D:/novel 人物库 林远
   ```

2. **获取人物详情**
   ```bash
   python resource_manager.py char get 仙途 D:/novel 林远
   ```

3. **或使用 load_context.py 按需加载**
   ```bash
   python load_context.py 仙途 D:/novel --volume 第一卷 --chapter 第 1 章 --characters 林远，清风
   ```

## 最佳实践

### 1. 保持 list.md 同步

每次增删改资源后，确保 list.md 已更新：

```bash
# 检查同步状态
python list_manager.py sync 仙途 D:/novel 人物库
python list_manager.py sync 仙途 D:/novel 设定库
```

### 2. 填写概况和相关资源

添加资源时尽量填写完整信息：

```bash
# 好的示例
python resource_manager.py char add 仙途 D:/novel 林远 "主角，少年，坚毅，林府灭门唯一幸存者" "清风（救命恩人）、林父（父亲）、黑衣人（仇人）"

# 不好的示例（信息不完整）
python resource_manager.py char add 仙途 D:/novel 林远
```

### 3. 定期搜索检查

定期搜索资源，确保没有重复或冲突：

```bash
# 搜索相似名称
python list_manager.py search 仙途 D:/novel 人物库 林
python list_manager.py search 仙途 D:/novel 设定库 宗
```

### 4. 伏笔状态管理

及时更新伏笔状态：

```bash
# 铺设伏笔
python resource_manager.py vow add 仙途 D:/novel "玉简中的神秘信息" "第三卷揭晓"

# 揭露伏笔
python resource_manager.py vow update 仙途 D:/novel V001 已揭露 "第三卷第 10 章"
```

## 常见问题

### Q: list.md 和实际文件不一致怎么办？

A: 使用 sync 命令同步：
```bash
python list_manager.py sync 仙途 D:/novel 人物库
```

### Q: 如何批量添加多个人物？

A: 可以编写脚本循环调用：
```python
import subprocess

characters = [
    ("林远", "主角，少年，坚毅", "清风、林父"),
    ("清风", "散修，路过救下林远", "林远"),
    ("林父", "林远之父，为保护儿子而死", "林远"),
]

for name, summary, relations in characters:
    subprocess.run([
        "python", "resource_manager.py", "char", "add",
        "仙途", "D:/novel", name, summary, relations
    ])
```

### Q: 如何迁移旧项目到新结构？

A: 运行迁移脚本（需手动创建）：
1. 为每个库文件夹创建 list.md
2. 扫描现有文件，生成索引条目
3. 使用 sync 命令验证

## 文件结构回顾

```
库/{书名}/
├── 人物库/
│   ├── list.md        ← 索引（必须）
│   ├── 林远.md        ← 人物文件
│   └── 清风.md
├── 设定库/
│   ├── list.md        ← 索引（必须）
│   ├── 青云宗.md      ← 设定文件
│   └── 修仙体系.md
└── ...
```

**核心原则：**
- list.md 是唯一索引
- 所有操作先更新 list.md
- 定期 sync 确保一致性
