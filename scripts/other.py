def create_base_documents(book_path: Path, book_name: str):
    """创建基础文档"""

    config_path = book_path / "config.md"
    if not config_path.exists():
        outline_content = f"""# 《{book_name}》写作要求

## 基本信息
- **书名**：{book_name}
- **题材**：
- **每章字数**：
- **
## 世界观
（世界观设定）

## 主线剧情
（主线剧情概述）

## 主要人物
（主要人物列表）

## 卷纲
（各卷概述）
"""
        outline_path.write_text(outline_content, encoding='utf-8')
        print(f"[OK] 创建总纲")

    # 总纲
    outline_path = book_path / "大纲" / "总纲.md"
    if not outline_path.exists():
        outline_content = f"""# 《{book_name}》总纲

## 基本信息
- **书名**：{book_name}
- **题材**：

## 世界观
（世界观设定）

## 主线剧情
（主线剧情概述）

## 主要人物
（主要人物列表）

## 卷纲
（各卷概述）
"""
        outline_path.write_text(outline_content, encoding='utf-8')
        print(f"[OK] 创建总纲")

    # 写作要求
    req_path = book_path / "写作要求" / "文笔风格.md"
    if not req_path.exists():
        req_content = """# 文笔风格要求

## 语言风格
- 简洁明快，避免过度修饰
- 对话自然，符合人物身份
- 动作描写具体，避免抽象陈述

## 叙事节奏
- 开头快速进入冲突
- 张弛有度，高低潮交替
- 每章结尾设置悬念

## 禁忌事项
- 避免天气开场
- 避免日常流程描写
- 避免信息倾倒
"""
        req_path.write_text(req_content, encoding='utf-8')
        print(f"[OK] 创建写作要求")

