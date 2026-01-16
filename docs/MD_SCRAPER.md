# Markdown Scraper 使用指南

## 概述

`md_scraper.py` 是一个用于将 Markdown 格式文档转换为 Claude Skill 的工具。它参考了 `pdf_scraper.py` 的实现模式，提供了完整的 Markdown 解析和 Skill 构建功能。

## 功能特性

- ✅ 解析 Markdown 文档，提取标题、内容、代码块
- ✅ 自动检测代码语言
- ✅ 代码质量评分
- ✅ 自动提取可执行脚本
- ✅ 内容分类和索引生成
- ✅ 生成完整的 Skill 结构（references、scripts、SKILL.md）

## 使用方法

### 1. 命令行使用

#### 从 Markdown 文件创建 Skill

```bash
python3 md_scraper.py --md path/to/documentation.md --name my_skill
```

#### 使用配置文件

```bash
python3 md_scraper.py --config configs/my_md_config.json
```

#### 从已提取的 JSON 构建 Skill

```bash
python3 md_scraper.py --from-json output/my_skill_extracted.json
```

### 2. Python API 使用

#### 基本用法

```python
from skill_seekers.cli.md_scraper import MarkdownToSkillConverter

config = {
    'name': 'my_skill',
    'md_path': 'documentation.md',
    'description': 'Use when working with my documentation',
    'save_dir': 'output'
}

converter = MarkdownToSkillConverter(config)
converter.extract_markdown()
converter.build_skill()
```

#### 从字符串内容创建

```python
markdown_content = """
# My Documentation

## Introduction
Content here...

```python
def example():
    pass
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
```

#### 仅解析 Markdown（不构建 Skill）

```python
from skill_seekers.cli.md_scraper import MarkdownParser

parser = MarkdownParser(markdown_content)
result = parser.parse()

print(f"Pages: {result['total_pages']}")
print(f"Code blocks: {result['total_code_blocks']}")
print(f"Languages: {result['languages_detected']}")
```

## 配置文件格式

```json
{
  "name": "my_skill",
  "md_path": "path/to/documentation.md",
  "description": "Use when working with my documentation",
  "save_dir": "output",
  "scripts_config": {
    "line_threshold": 30,
    "min_quality_score": 6.0,
    "max_display_lines": 5
  },
  "categories": {
    "getting_started": ["introduction", "getting started", "quick start"],
    "api_reference": ["api", "reference", "function", "method"],
    "examples": ["example", "tutorial", "guide"]
  }
}
```

### 配置项说明

- `name`: Skill 名称（必需）
- `md_path`: Markdown 文件路径（与 `md_content` 二选一）
- `md_content`: Markdown 内容字符串（与 `md_path` 二选一）
- `description`: Skill 描述（可选，会自动从内容推断）
- `save_dir`: 输出目录（默认: "output"）
- `scripts_config`: 脚本提取配置
  - `line_threshold`: 提取脚本的最小行数（默认: 30）
  - `min_quality_score`: 最小质量分数（默认: 6.0）
  - `max_display_lines`: 在 reference 中显示的最大行数（默认: 5）
- `categories`: 内容分类配置（可选）
  - 键为分类名称，值为关键词列表

## 输出结构

生成的 Skill 目录结构：

```
output/my_skill/
├── SKILL.md                    # 主 Skill 文件
├── references/
│   ├── index.md               # 索引文件
│   ├── getting_started.md     # 分类参考文件
│   └── api_reference.md
└── scripts/
    ├── README.md              # 脚本说明
    ├── example_function.py    # 提取的脚本文件
    └── ...
```

## 解析功能

### 提取的内容

- **标题**: 所有级别的标题（h1-h6）
- **代码块**: 自动检测语言和代码质量
- **文本内容**: 段落和文本内容
- **图片**: 图片引用（路径和 alt 文本）

### 代码质量评分

代码质量评分基于以下因素：
- 代码长度（行数）
- 语法完整性（括号匹配等）
- 语言特定模式（函数定义、类定义等）

评分范围：0-10

### 语言检测

支持自动检测以下语言：
- Python
- JavaScript/TypeScript
- Java/C++/C/C#
- Go
- Rust
- Ruby
- PHP
- 以及其他常见语言

## 与 PDF Scraper 的对比

| 特性 | PDF Scraper | Markdown Scraper |
|------|-------------|------------------|
| 输入格式 | PDF 文件 | Markdown 文件/字符串 |
| 解析方式 | PDF 提取 | Markdown 解析 |
| 代码提取 | ✅ | ✅ |
| 图片处理 | ✅ 提取图片数据 | ✅ 提取图片引用 |
| 脚本提取 | ✅ | ✅ |
| 内容分类 | ✅ | ✅ |

## 注意事项

1. **大文件处理**: 对于非常大的 Markdown 文件，建议先分割或使用分类配置
2. **代码块格式**: 确保代码块使用标准的 Markdown 格式（```language\ncode\n```）
3. **图片路径**: 图片引用会被保留，但图片文件本身不会被复制（需要手动处理）
4. **编码**: 确保 Markdown 文件使用 UTF-8 编码

## 示例

完整示例请参考：
- `examples/md_scraper_example.py`

## 相关文件

- `pdf_scraper.py`: PDF 文档转换器（参考实现）
- `llms_txt_parser.py`: llms.txt 解析器（部分参考）
- `language_detector.py`: 语言检测器（可选依赖）
