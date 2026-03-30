# 🎭 人物创建指引

本指引用于规范小说创作中**新人物创建**的完整流程。

---

## 📋 创建流程总览

```
① 根据模板创建人物档案 .md 文件
        ↓
② 将人物索引添加到 SQLite 数据库
        ↓
③ 双重检查（数据库 + .books 目录）
```

---

## 步骤①：创建人物档案文件

### 文件存储路径

```
~/.books/<书名>/资源库/人物库/<角色名>.md
```

**示例：**
```
~/.books/斗破苍穹/资源库/人物库/萧炎.md
~/.books/三体/资源库/人物库/罗辑.md
```

### 使用模板

参考 [人物创建模版](references/character/character-template.md) 创建人物档案。

---

## 步骤②：添加数据库索引

### 命令格式

```bash
python database.py "<书名>" create table characters name "<角色名>" summary "<概况>" path "<路径>" relations "<相关资源>" chapter "<首次章节>" priority <优先级>
```

### 参数说明

| 参数 | 说明 | 示例                       |
|------|------|--------------------------|
| `<书名>` | 小说名称 | `三体`                     |
| `<角色名>` | 角色姓名 | `罗辑`                     |
| `<概况>` | 一句话简介 | `主角，28 岁，面壁者、执剑人，肩负人类命运` |
| `<路径>` | **相对路径**（从资源库开始） | `人物库/罗辑.md`              |
| `<相关资源>` | 相关角色/设定（JSON 数组） | `["苏雨晴", "局长"]`          |
| `<首次章节>` | 首次出现的章节 | `["第一卷第 1 章"]`             |
| `<优先级>` | 0-100（数字越小越重要） | `0`（主角）                  |

> **注意**：`relations` 和 `chapter` 字段需使用 JSON 数组格式，并用单引号包裹。

### 完整示例

```bash
# 创建主角（优先级 0）
python database.py "未来救援局" create table characters name "陈渊" summary "主角，22 岁，纯人类后裔，救援队队长" path "人物库/陈渊.md" relations "[]" chapter "第一卷第 1 章" priority 0

# 创建主角团成员（优先级 1）
python database.py "未来救援局" create table characters name "苏雨晴" summary "医疗官，24 岁，温柔细心" path "人物库/苏雨晴.md" relations '["陈渊"]' chapter "第一卷第 1 章" priority 1

# 创建关键人物（优先级 2）
python database.py "未来救援局" create table characters name "局长" summary "68 岁，救援局总局长，智慧类人" path "人物库/局长.md" relations '["陈渊", "林卫国"]' chapter "第一卷第 3 章" priority 2
```

### 路径格式规范

```bash
# ✅ 正确：相对路径（从资源库开始）
path "人物库/陈渊.md"
path "设定库/青云宗.md"
path "伏笔库/神秘玉简.md"

# ❌ 错误：绝对路径
path "C:/Users/.../books/未来救援局/资源库/人物库/陈渊.md"
```

### 优先级规范

| 优先级    | 角色类型 | 示例                 |
|--------|---------|--------------------|
| **0-2** | 核心角色 | 主角、主角团成员、重要配角、关键反派 |
| **3-5** | 重要角色 | 主要配角、盟友、导师         |
| **6-8** | 普通角色 | 一般配角、龙套            |
| **9**  | 次要角色 | 背景人物、一次性角色         |
| **10** | 边缘角色 | 提及但不登场             |

---

## 步骤③：双重检查

### 检查 1：数据库中存在

```bash
# 查询角色详情
python database.py "三体" get table characters name "罗辑"

# 查询角色路径
python database.py "未来救援局" get-path table characters name "陈渊"
```

**预期输出：**
```json
{
  "name": "陈渊",
  "summary": "主角，22 岁，纯人类后裔，救援队队长",
  "path": "人物库/陈渊.md",
  "relations": [],
  "chapter": "第一卷第 1 章",
  "priority": 0
}
```

### 检查 2：文件存在

```powershell
# PowerShell 检查文件
Test-Path "$env:USERPROFILE\.books\未来救援局\资源库\人物库\陈渊.md"

# 或读取文件内容
Get-Content "$env:USERPROFILE\.books\未来救援局\资源库\人物库\陈渊.md"
```

### 检查清单

- [ ] 人物档案 .md 文件已创建
- [ ] 文件位于正确的目录（`~/.books/<书名>/资源库/人物库/`）
- [ ] 数据库索引已添加（`database.py create`）
- [ ] 路径格式正确（相对路径）
- [ ] 优先级设置合理
- [ ] 首次章节已记录
- [ ] 相关资源已关联（如有）

---

## 🔧 常用操作速查

### 创建新人物

```bash
# 1. 创建 .md 文件（手动或脚本）
# ~/.books/<书名>/资源库/人物库/<角色名>.md

# 2. 添加到数据库
python database.py "<书名>" create table characters name "<角色名>" summary "<概况>" path "人物库/<角色名>.md" relations "[]" chapter "<章节>" priority <优先级>

# 3. 验证
python database.py "<书名>" get table characters name "<角色名>"
```

### 更新人物信息

```bash
# 更新出现章节（JSON 数组）
python database.py "<书名>" update table characters name "<角色名>" chapter='["第一卷第 1 章", "第一卷第 5 章"]'

# 添加相关资源
python database.py "<书名>" add-relation table characters name "<角色名>" relation "<相关角色名>"

# 设置优先级
python database.py "<书名>" set-priority table characters name "<角色名>" priority <新优先级>
```

### 查询人物

```bash
# 搜索（模糊匹配）
python database.py "<书名>" search table characters keyword "<关键词>"

# 获取详情
python database.py "<书名>" get table characters name "<角色名>"

# 列出所有人物
python database.py "<书名>" list table characters

# 列出重要人物（优先级 <= 3）
python database.py "<书名>" list table characters priority_limit 3

# 查看统计
python database.py "<书名>" stats
```

### 删除人物

```bash
# 从数据库删除
python database.py "<书名>" delete table characters name "<角色名>"

# ⚠️ 手动删除 .md 文件
Remove-Item "$env:USERPROFILE\.books\<书名>\资源库\人物库\<角色名>.md"
```

---

## 📖 完整示例：创建“林卫国”角色

### 步骤 1：创建档案文件

**文件路径：** `~/.books/未来救援局/资源库/人物库/林卫国.md`

参考 [人物模版](character-template.md) 的格式在对应文件路径创建人物资料。

### 步骤 2：添加数据库索引

```bash
python database.py "未来救援局" create table characters name "林卫国" summary "前救援队成员，陈渊之父，失踪" path "人物库/林卫国.md" relations '["陈渊", "局长"]' chapter "第一卷第 5 章" priority 1
```

### 步骤 3：验证

```bash
# 检查数据库
python database.py "未来救援局" get table characters name "林卫国"

# 检查文件
Test-Path "$env:USERPROFILE\.books\未来救援局\资源库\人物库\林卫国.md"
```

---

## ⚠️ 注意事项

### 1. 路径必须是相对路径

```bash
# ✅ 正确
path "人物库/陈渊.md"

# ❌ 错误
path "C:/Users/.../人物库/陈渊.md"
path "books/未来救援局/资源库/人物库/陈渊.md"
```

### 2. JSON 字段使用单引号

```bash
# ✅ 正确
chapter='["第一卷第 1 章", "第一卷第 2 章"]'
relations='["苏雨晴", "局长"]'

# ❌ 错误（PowerShell 可能解析失败）
chapter="["第一卷第 1 章"]"
```

### 3. 角色名唯一性

- 同一本书内角色名必须唯一
- 如有重名，使用别名区分（如“林远（青年）”、“林远（中年）”）

### 4. 优先级一致性

- 主角/核心角色：0-2
- 重要配角：3-5
- 普通角色：6-10
- 不要给龙套角色设置过高优先级

### 5. 资源更改

**人物更新时，需要同时更新 `数据库存储`、`Markdown文件`和`对应人物所有章节处的相关内容`。**

#### 流程示例
1. 用户想要更新角色`程心`的名称为`高心`。
2. 修改Markdown文件中的内容。
3. 修改数据库中的索引。
4. 根据数据库中索引出的`chapter`词条，逐条筛查文章章节，更改其中的`程心`为`高心`。

### 6. 相关资源格式

```bash
# 空数组（无相关资源）
relations "[]"

# 单个相关资源
relations '["苏雨晴"]'

# 多个相关资源
relations '["苏雨晴", "局长", "林卫国"]'
```
