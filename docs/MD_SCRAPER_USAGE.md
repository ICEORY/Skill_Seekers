# Markdown Scraper 使用指南 - 文本输入和文件输入

## 概述

`md_scraper.py` 现在支持两种输入方式：
1. **文件输入**：从 markdown 文件读取
2. **文本输入**：直接提供 markdown 内容字符串

## 使用方法

### 1. 文件输入（推荐）

#### 命令行方式

```bash
# 基本用法
python md_scraper.py --md document.md --name my_skill

# 指定描述
python md_scraper.py --md document.md --name my_skill --description "Use when working with my documentation"

# 使用配置文件
python md_scraper.py --config config.json
```

#### Python API 方式

```python
from skill_seekers.cli.md_scraper import MarkdownToSkillConverter

# 方式1: 使用配置文件中的 md_path
config = {
    'name': 'my_skill',
    'md_path': 'document.md',
    'description': 'Use when working with my documentation'
}
converter = MarkdownToSkillConverter(config)
converter.extract_markdown()
converter.build_skill()

# 方式2: 使用方法参数覆盖
config = {
    'name': 'my_skill',
    'description': 'Use when working with my documentation'
}
converter = MarkdownToSkillConverter(config)
converter.extract_markdown(md_path='document.md')  # 覆盖配置
converter.build_skill()
```

### 2. 文本输入（新功能）

#### 命令行方式

```bash
# 方式1: 从标准输入读取
cat document.md | python md_scraper.py --text --name my_skill

# 方式2: 使用管道
echo "# My Document\n\nContent here" | python md_scraper.py --text --name my_skill

# 方式3: 使用 --content 参数
python md_scraper.py --content "$(cat document.md)" --name my_skill
```

#### Python API 方式

```python
from skill_seekers.cli.md_scraper import MarkdownToSkillConverter

# 方式1: 使用配置文件中的 md_content
markdown_content = """
# My Documentation

## Introduction
This is a sample documentation.

```python
def hello_world():
    print("Hello, World!")
```
"""

config = {
    'name': 'my_skill',
    'md_content': markdown_content,
    'description': 'Use when working with my documentation'
}
converter = MarkdownToSkillConverter(config)
converter.extract_markdown()
converter.build_skill()

# 方式2: 使用方法参数覆盖
config = {
    'name': 'my_skill',
    'description': 'Use when working with my documentation'
}
converter = MarkdownToSkillConverter(config)
converter.extract_markdown(md_content=markdown_content)  # 覆盖配置
converter.build_skill()

# 方式3: 从文件读取内容后传入
with open('document.md', 'r', encoding='utf-8') as f:
    content = f.read()

config = {
    'name': 'my_skill',
    'description': 'Use when working with my documentation'
}
converter = MarkdownToSkillConverter(config)
converter.extract_markdown(md_content=content)
converter.build_skill()
```

### 3. 混合方式

可以在配置文件中指定文件路径，然后在方法调用时用文本内容覆盖：

```python
config = {
    'name': 'my_skill',
    'md_path': 'document.md',  # 默认路径
    'description': 'Use when working with my documentation'
}
converter = MarkdownToSkillConverter(config)

# 如果需要，可以用文本内容覆盖
converter.extract_markdown(md_content=custom_content)
converter.build_skill()
```

## 接口说明

### MarkdownToSkillConverter.extract_markdown()

```python
def extract_markdown(self, md_path: str = None, md_content: str = None):
    """
    Extract content from markdown file or content string.
    
    Args:
        md_path: Path to markdown file (optional, can override config)
        md_content: Markdown content string (optional, can override config)
    
    Returns:
        bool: True if extraction succeeded
    """
```

**参数说明：**
- `md_path`: Markdown 文件路径（可选，会覆盖配置中的 `md_path`）
- `md_content`: Markdown 内容字符串（可选，会覆盖配置中的 `md_content`）

**优先级：**
1. 方法参数（`md_path` 或 `md_content`）
2. 配置文件中的 `md_path` 或 `md_content`

**注意：**
- `md_path` 和 `md_content` 不能同时提供
- 如果两者都未提供，将从配置中获取

## 示例场景

### 场景1：处理动态生成的 markdown

```python
# 从数据库或 API 获取内容
import requests
response = requests.get('https://api.example.com/docs')
markdown_content = response.text

# 直接转换为 skill
config = {
    'name': 'api_docs',
    'description': 'API documentation'
}
converter = MarkdownToSkillConverter(config)
converter.extract_markdown(md_content=markdown_content)
converter.build_skill()
```

### 场景2：批量处理多个 markdown 文件

```python
import os
from skill_seekers.cli.md_scraper import MarkdownToSkillConverter

md_files = ['doc1.md', 'doc2.md', 'doc3.md']

for md_file in md_files:
    skill_name = os.path.splitext(md_file)[0]
    config = {
        'name': skill_name,
        'description': f'Use when working with {skill_name}'
    }
    converter = MarkdownToSkillConverter(config)
    converter.extract_markdown(md_path=md_file)
    converter.build_skill()
    print(f"✅ Processed {md_file}")
```

### 场景3：从字符串模板生成

```python
template = """
# {title}

## Overview
{overview}

## Code Example
```python
{code}
```
"""

# 填充模板
content = template.format(
    title="My Skill",
    overview="This is a great skill",
    code="def example():\n    pass"
)

# 转换为 skill
config = {
    'name': 'template_skill',
    'description': 'Template-based skill'
}
converter = MarkdownToSkillConverter(config)
converter.extract_markdown(md_content=content)
converter.build_skill()
```

## 最佳实践

1. **文件输入**：适用于静态文档文件，推荐用于大多数场景
2. **文本输入**：适用于动态生成的内容、API 返回的内容、或需要程序化处理的内容
3. **优先级**：方法参数 > 配置文件，便于灵活覆盖默认配置

## 错误处理

```python
try:
    converter.extract_markdown(md_path='document.md')
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
except ValueError as e:
    print(f"参数错误: {e}")
except RuntimeError as e:
    print(f"提取失败: {e}")
```

## 相关文档

- [MD_SCRAPER.md](./MD_SCRAPER.md) - 完整的功能文档
- [examples/md_scraper_example.py](../examples/md_scraper_example.py) - 更多示例代码
