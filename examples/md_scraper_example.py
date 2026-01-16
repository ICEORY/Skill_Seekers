#!/usr/bin/env python3
"""
Markdown Scraper 使用示例

演示如何使用 md_scraper.py 将 Markdown 文档转换为 Claude Skill
"""

import sys
import os
import json

# 添加路径以便导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from skill_seekers.cli.md_scraper import MarkdownToSkillConverter, MarkdownParser


def example_from_file():
    """从文件读取 Markdown 并转换"""
    config = {
        'name': 'example_skill',
        'md_path': 'path/to/your/documentation.md',
        'description': 'Use when working with example documentation',
        'save_dir': 'output',
        'scripts_config': {
            'line_threshold': 30,
            'min_quality_score': 6.0,
            'max_display_lines': 5
        },
        'categories': {
            'getting_started': ['introduction', 'getting started', 'quick start'],
            'api_reference': ['api', 'reference', 'function', 'method'],
            'examples': ['example', 'tutorial', 'guide']
        }
    }
    
    converter = MarkdownToSkillConverter(config)
    converter.extract_markdown()
    converter.build_skill()


def example_from_content():
    """从字符串内容直接转换"""
    markdown_content = """
# My Documentation

## Introduction

This is a sample documentation.

## Code Example

Here's a Python example:

```python
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```

## JavaScript Example

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet("World"));
```
"""
    
    config = {
        'name': 'example_skill',
        'md_content': markdown_content,
        'description': 'Use when working with example documentation',
        'save_dir': 'output'
    }
    
    converter = MarkdownToSkillConverter(config)
    converter.extract_markdown()
    converter.build_skill()


def example_parse_only():
    """仅解析 Markdown，不构建 Skill"""
    markdown_content = """
# Documentation Title

## Section 1

Some content here.

```python
def example():
    pass
```
"""
    
    parser = MarkdownParser(markdown_content)
    result = parser.parse()
    
    print(f"Total pages: {result['total_pages']}")
    print(f"Total code blocks: {result['total_code_blocks']}")
    print(f"Languages detected: {result['languages_detected']}")
    
    # 保存解析结果
    with open('parsed_output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("\nParsed data saved to parsed_output.json")


if __name__ == '__main__':
    print("Markdown Scraper 示例")
    print("=" * 50)
    print("\n选择示例:")
    print("1. 从文件读取 (example_from_file)")
    print("2. 从内容字符串 (example_from_content)")
    print("3. 仅解析 (example_parse_only)")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    if choice == '1':
        example_from_file()
    elif choice == '2':
        example_from_content()
    elif choice == '3':
        example_parse_only()
    else:
        print("无效选择")
