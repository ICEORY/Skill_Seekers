# PDF 章节分割优化方案

## 问题描述

方案1实施后，标题检测过于敏感，导致：
- ❌ 把图示说明识别为章节
- ❌ 把子标题识别为章节
- ❌ 生成过多的独立文件（过度分割）

**期望效果**：
- ✅ 只根据**主要章节**（Chapter 1, Chapter 2...）分割文件
- ✅ 次要标题（1.1, 1.2...）保留在章节内部
- ✅ 图示说明不被识别为章节

---

## 解决方案：智能章节识别

### 核心思路

1. **定义章节层级**：
   - **主章节 (Major Chapter)**: H1 级别，用于文件分割
   - **子章节 (Sub-section)**: H2/H3 级别，保留在内容中
   - **小标题 (Minor heading)**: H4+ 级别，保留在内容中

2. **章节判定规则**：
   - 使用严格的模式匹配
   - 考虑位置（是否在页面顶部）
   - 考虑上下文（前后是否有大量文本）

---

## 实现代码

### 方案 A：改进 `detect_chapter_start()` 方法

在 `pdf_extractor_poc.py` 中修改：

```python
def detect_chapter_start(self, page_data):
    """
    检测页面是否是主章节的开始

    只识别主要章节（H1级别），忽略次要标题

    Returns:
        (is_major_chapter, chapter_title) tuple.
    """
    headings = page_data.get('headings', [])

    # === 规则 1: 检查 H1 标题 ===
    # 只有 H1 才被认为是主章节
    h1_headings = [h for h in headings if h.get('level') == 'h1']

    if h1_headings:
        # 取第一个 H1 作为章节标题
        first_h1 = h1_headings[0]
        title = first_h1['text']

        # 额外验证：排除一些误识别的情况
        # 排除过短的标题（可能是图示）
        if len(title.strip()) < 5:
            return False, None

        # 排除纯数字或特殊字符
        if re.match(r'^[\d\.\s\-_]+$', title):
            return False, None

        return True, title

    # === 规则 2: 检查特定章节模式 ===
    # 严格匹配常见的章节格式
    text = page_data.get('text', '')
    first_lines = text.split('\n')[:5]  # 只检查前5行

    chapter_patterns = [
        # "Chapter 1", "Chapter One", "第一章"
        (r'^(Chapter|CHAPTER|Part|PART|Section|SECTION|第[\d一二三四五六七八九十百]+章)\s+[\dIVXivx]+', True),
        # "1. Introduction" (但必须是整数，且在页面顶部)
        (r'^(\d{1,2})\.\s+([A-Z][A-Za-z\s]{5,50})$', True),
        # "附录 A", "Appendix A"
        (r'^(Appendix|APPENDIX|附录|Annex)\s+[A-Z]', True),
    ]

    for line in first_lines:
        line = line.strip()
        if not line:
            continue

        for pattern, is_major in chapter_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # 进一步验证：检查是否有足够的内容（不是孤立的标题）
                text_after_title = '\n'.join(first_lines[first_lines.index(line)+1:])
                if len(text_after_title.strip()) > 50:  # 至少50个字符的内容
                    return True, line.strip()

    # === 规则 3: 严格模式 - 使用字体信息 ===
    # 如果有检测方法信息，优先使用 H1
    if h1_headings:
        for h1 in h1_headings:
            # 检查是否是通过字体分析检测到的（更可靠）
            if h1.get('detection_method') == 'font_analysis':
                # 字体大小是否足够大（主章节通常字体很大）
                font_size = h1.get('font_size', 0)
                is_bold = h1.get('is_bold', False)

                # 计算页面平均字体大小（需要在调用时传入）
                avg_font_size = page_data.get('_avg_font_size', 12)

                # 主章节标题：字体大于平均1.5倍，且通常是粗体
                if font_size > avg_font_size * 1.5 and is_bold:
                    return True, h1['text']

    # 不符合任何主章节规则
    return False, None


def classify_heading_importance(self, heading):
    """
    对标题进行重要性分类

    Args:
        heading: 标题字典

    Returns:
        str: 'major_chapter' | 'sub_chapter' | 'minor_heading' | 'caption'
    """
    text = heading.get('text', '')
    level = heading.get('level', 'h3')
    font_size = heading.get('font_size', 12)
    is_bold = heading.get('is_bold', False)

    # === 主章节判断 ===
    # 条件1: H1 级别
    if level == 'h1':
        return 'major_chapter'

    # 条件2: 特定模式
    major_patterns = [
        r'^(Chapter|Part|Section|第[\d一二三四五六七八九十]+章)\s',
        r'^\d{1,2}\.\s+[A-Z]',  # "1. Introduction"
        r'^(Appendix|附录)\s+[A-Z]',
    ]

    for pattern in major_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return 'major_chapter'

    # === 子章节判断 ===
    # H2 级别，或者有编号的子标题
    if level == 'h2':
        return 'sub_chapter'

    sub_patterns = [
        r'^\d+\.\d+',  # "1.1 Overview"
        r'^[A-Z]\.\s',  # "A. Introduction"
    ]

    for pattern in sub_patterns:
        if re.match(pattern, text):
            return 'sub_chapter'

    # === 图示/表格说明判断 ===
    # 包含"图"、"表"、"Figure"、"Table"的通常是说明
    caption_keywords = ['图', '表', 'figure', 'table', 'diagram', 'chart']
    if any(kw in text.lower() for kw in caption_keywords):
        return 'caption'

    # 过短（可能是图示）
    if len(text) < 10:
        return 'caption'

    # === 默认为次要标题 ===
    return 'minor_heading'
```

### 方案 B：改进 `categorize_content()` 方法

在 `pdf_scraper.py` 中修改：

```python
def categorize_content(self):
    """
    基于主章节分类内容

    只使用主章节（major_chapter）进行文件分割
    """
    print(f"\n📋 Categorizing content based on major chapters...")

    categorized = {}

    # === 步骤1: 识别所有主章节 ===
    major_chapters = []

    for page in self.extracted_data['pages']:
        page_num = page['page_number']

        # 检查是否是主章节开始
        is_chapter, chapter_title = self._detect_major_chapter(page)

        if is_chapter:
            major_chapters.append({
                'title': chapter_title,
                'start_page': page_num,
                'end_page': None  # 待确定
            })

    # === 步骤2: 确定每个章节的结束页 ===
    for i, chapter in enumerate(major_chapters):
        if i < len(major_chapters) - 1:
            # 结束页是下一章节的前一页
            chapter['end_page'] = major_chapters[i + 1]['start_page'] - 1
        else:
            # 最后一章到文档末尾
            chapter['end_page'] = len(self.extracted_data['pages'])

    print(f"   Found {len(major_chapters)} major chapters")
    for ch in major_chapters:
        print(f"   - '{ch['title']}' (pages {ch['start_page']}-{ch['end_page']})")

    # === 步骤3: 如果没有找到章节，使用fallback ===
    if not major_chapters:
        print("   ⚠️  No major chapters detected, using fallback categorization")
        return self._fallback_categorization()

    # === 步骤4: 将页面分配到章节 ===
    for chapter in major_chapters:
        category_key = self._sanitize_filename(chapter['title'])
        categorized[category_key] = {
            'title': chapter['title'],
            'pages': [],
            'page_range': f"{chapter['start_page']}-{chapter['end_page']}"
        }

        # 收集该章节范围内的所有页面
        for page in self.extracted_data['pages']:
            page_num = page['page_number']
            if chapter['start_page'] <= page_num <= chapter['end_page']:
                categorized[category_key]['pages'].append(page)

    # === 步骤5: 报告统计 ===
    print(f"\n✅ Created {len(categorized)} chapter-based categories:")
    for cat_key, cat_data in categorized.items():
        page_count = len(cat_data['pages'])
        print(f"   - {cat_data['title']}: {page_count} pages ({cat_data['page_range']})")

    return categorized


def _detect_major_chapter(self, page):
    """
    检测页面是否是主章节开始（严格模式）

    Returns:
        (is_major_chapter, chapter_title)
    """
    headings = page.get('headings', [])
    text = page.get('text', '')

    # === 方法1: 检查 H1 标题 ===
    h1_headings = [h for h in headings if h.get('level') == 'h1']

    if h1_headings:
        title = h1_headings[0]['text']

        # 验证：排除误识别
        if len(title.strip()) < 5:
            return False, None
        if re.match(r'^[\d\.\s\-_]+$', title):
            return False, None

        # 排除图表标题
        if any(kw in title.lower() for kw in ['图', '表', 'figure', 'table']):
            return False, None

        return True, title

    # === 方法2: 严格模式匹配 ===
    first_lines = text.split('\n')[:3]

    major_chapter_patterns = [
        r'^(Chapter|CHAPTER|第[\d一二三四五六七八九十]+章)\s+\d+',
        r'^(Part|PART|部分)\s+[IVXivx\d]+',
        r'^(\d{1,2})\.\s+([A-Z][A-Za-z\s]{8,60})$',  # "1. Introduction" (标题要足够长)
        r'^(Appendix|APPENDIX|附录)\s+[A-Z]',
    ]

    for line in first_lines:
        line = line.strip()
        for pattern in major_chapter_patterns:
            if re.match(pattern, line):
                # 确保后面有足够内容
                remaining_text = '\n'.join(first_lines[first_lines.index(line)+1:])
                if len(remaining_text.strip()) > 30:
                    return True, line.strip()

    return False, None


def _fallback_categorization(self):
    """
    当无法检测到主章节时的fallback方案

    选项1: 按页数分块
    选项2: 使用所有H1/H2作为分类（相对宽松）
    选项3: 单一类别
    """
    # 选项1: 按页数分块（推荐）
    chunk_size = 20  # 每20页一个文件
    categorized = {}

    total_pages = len(self.extracted_data['pages'])
    num_chunks = (total_pages + chunk_size - 1) // chunk_size

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_pages)

        chunk_title = f"Section {i+1} (Pages {start_idx+1}-{end_idx})"
        category_key = f"section_{i+1}"

        categorized[category_key] = {
            'title': chunk_title,
            'pages': self.extracted_data['pages'][start_idx:end_idx],
            'page_range': f"{start_idx+1}-{end_idx}"
        }

    return categorized
```

---

## 配置选项

在 `config.json` 中添加章节检测配置：

```json
{
  "name": "myskill",
  "pdf_path": "manual.pdf",
  "extract_options": {
    "heading_detection": {
      "enable_font_analysis": true,
      "enable_pattern_analysis": true
    },

    // 新增：章节分割配置
    "chapter_detection": {
      "mode": "strict",  // 'strict' | 'moderate' | 'loose'
      "only_major_chapters": true,  // 只用主章节分割
      "min_chapter_pages": 3,  // 章节最少页数
      "fallback_chunk_size": 20  // 无法检测章节时的分块大小
    }
  }
}
```

### 模式说明

| 模式 | 说明 | 适用场景 |
|-----|------|---------|
| **strict** | 只识别 Chapter/Part/Appendix 等明确的章节标记 | 格式规范的技术手册 |
| **moderate** | 识别 H1 + 章节模式 | 大部分 PDF 文档（推荐） |
| **loose** | 识别 H1 + H2 作为分割点 | 结构不规范的文档 |

---

## 使用示例

### 配置文件示例

```json
{
  "name": "python_manual",
  "pdf_path": "python_reference.pdf",
  "extract_options": {
    "chapter_detection": {
      "mode": "strict",
      "only_major_chapters": true,
      "min_chapter_pages": 5
    }
  }
}
```

### 运行命令

```bash
# 使用严格模式（只识别主章节）
python3 pdf_scraper.py --pdf manual.pdf --name myskill --strict-chapters

# 查看章节检测结果（不生成文件）
python3 pdf_scraper.py --pdf manual.pdf --name myskill --dry-run --show-chapters
```

---

## 对比效果

### 改进前（过度分割）

```
output/myskill/references/
├── chapter_1_introduction.md
├── 1_1_overview.md              ❌ 不应该独立
├── 1_2_prerequisites.md         ❌ 不应该独立
├── figure_1_1_architecture.md   ❌ 图示被误识别
├── chapter_2_installation.md
├── 2_1_windows.md               ❌ 不应该独立
├── 2_2_linux.md                 ❌ 不应该独立
├── table_2_1_requirements.md    ❌ 表格被误识别
└── ...
```

共生成 **20+ 个文件**，过于分散。

### 改进后（合理分割）

```
output/myskill/references/
├── chapter_1_introduction.md     ✅ 主章节
│   包含：
│   - ## 1.1 Overview          （子章节在内部）
│   - ## 1.2 Prerequisites     （子章节在内部）
│   - ### Figure 1.1: ...      （图示在内部）
│
├── chapter_2_installation.md    ✅ 主章节
│   包含：
│   - ## 2.1 Windows          （子章节在内部）
│   - ## 2.2 Linux            （子章节在内部）
│   - ### Table 2.1: ...      （表格在内部）
│
├── chapter_3_usage.md           ✅ 主章节
├── appendix_a_reference.md      ✅ 附录
└── index.md
```

共生成 **4-6 个文件**，结构清晰。

---

## 实施步骤

### Step 1: 添加章节重要性分类

在 `pdf_extractor_poc.py` 中添加 `classify_heading_importance()` 方法。

### Step 2: 修改章节检测

将 `detect_chapter_start()` 改为 `detect_major_chapter()`，使用更严格的规则。

### Step 3: 改进分类逻辑

修改 `pdf_scraper.py` 中的 `categorize_content()` 方法。

### Step 4: 测试验证

```python
# 测试脚本
def test_chapter_detection():
    extractor = PDFExtractor('test.pdf')
    result = extractor.extract_all()

    # 检查章节识别
    chapters = result['chapters']
    print(f"Detected {len(chapters)} major chapters:")
    for ch in chapters:
        print(f"  - {ch['title']} (pages {ch['start_page']}-{ch['end_page']})")

    # 验证是否过度分割
    assert len(chapters) < 20, "Too many chapters detected (over-segmentation)"
    assert len(chapters) > 0, "No chapters detected"
```

---

## 调试技巧

### 1. 启用章节检测日志

```python
def detect_major_chapter(self, page):
    """带详细日志的版本"""
    headings = page.get('headings', [])

    self.log(f"\n=== Page {page['page_number']} ===")
    self.log(f"  Total headings: {len(headings)}")

    for h in headings:
        importance = self.classify_heading_importance(h)
        self.log(f"  - [{h['level']}] {h['text']} -> {importance}")

    # ... 检测逻辑 ...
```

### 2. 生成章节分析报告

```python
def generate_chapter_report(self, output_file='chapter_analysis.txt'):
    """生成章节识别报告，帮助调试"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Chapter Detection Analysis\n")
        f.write("=" * 60 + "\n\n")

        for page in self.extracted_data['pages']:
            page_num = page['page_number']
            is_chapter, title = self._detect_major_chapter(page)

            f.write(f"Page {page_num}:\n")
            f.write(f"  Is Major Chapter: {is_chapter}\n")
            if is_chapter:
                f.write(f"  Chapter Title: {title}\n")

            f.write(f"  Headings:\n")
            for h in page.get('headings', []):
                importance = self.classify_heading_importance(h)
                f.write(f"    - [{h['level']}] {h['text']} ({importance})\n")
            f.write("\n")

    print(f"📊 Chapter analysis saved to: {output_file}")
```

运行：

```bash
python3 pdf_scraper.py --pdf manual.pdf --analyze-chapters
```

会生成 `chapter_analysis.txt`，可以查看每页的标题识别情况。

---

## 常见问题

### Q1: 有些章节没有"Chapter"字样，怎么办？

**A**: 调整模式为 `moderate`，会识别所有 H1 标题：

```json
{
  "chapter_detection": {
    "mode": "moderate"
  }
}
```

### Q2: 文档没有明确章节，全是 H2/H3，怎么办？

**A**: 使用 fallback 分块模式：

```json
{
  "chapter_detection": {
    "fallback_chunk_size": 15  // 每15页一个文件
  }
}
```

### Q3: 如何手动指定章节分割点？

**A**: 在 config 中手动定义章节：

```json
{
  "manual_chapters": [
    {"title": "Introduction", "start_page": 1, "end_page": 10},
    {"title": "Installation", "start_page": 11, "end_page": 25},
    {"title": "Usage", "start_page": 26, "end_page": 50}
  ]
}
```

---

## 总结

### 关键改进

1. ✅ **严格的章节判定** - 只识别主章节（H1 + 特定模式）
2. ✅ **标题重要性分类** - major_chapter / sub_chapter / minor_heading / caption
3. ✅ **智能 fallback** - 无法检测章节时按页数分块
4. ✅ **调试工具** - 章节分析报告

### 预期效果

| 指标 | 改进前 | 改进后 |
|-----|-------|-------|
| 生成文件数 | 15-30 个 | 4-8 个 |
| 文件大小 | 500-2000 字符 | 5000-15000 字符 |
| 结构清晰度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### 建议配置

**大部分文档**：
```json
{"mode": "moderate", "only_major_chapters": true}
```

**格式规范的技术手册**：
```json
{"mode": "strict", "only_major_chapters": true}
```

**结构混乱的文档**：
```json
{"mode": "loose", "fallback_chunk_size": 20}
```
