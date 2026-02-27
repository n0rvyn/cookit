---
name: spotlight
description: 通过 macOS Spotlight 全局检索本地文件并读取内容，作为私有知识库使用。支持 Word、Excel、PPT、PDF、Markdown 等格式的文本提取。当用户要求搜索本地文件、查找文档、检索电脑上的资料、查看本地文件内容时使用。关键词：搜索文件、找文件、本地搜索、Spotlight、知识库、电脑上、磁盘上、硬盘上、本地文档。
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/spotlight/scripts/*)
---

# Spotlight 本地私有知识库

通过 macOS Spotlight 索引全局检索本地文件，提取文档内容，搜索 + 阅读 + 理解。

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/spotlight/scripts" ] || SKILLS_ROOT="$BASE/cookit/mactools/skills"
```

## 工具

### 1. 搜索工具

```
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh
```

### 2. 文本提取工具

```
python3 ${SKILLS_ROOT}/spotlight/scripts/extract_text.py <file_path> [--max-chars N]
```

支持提取的格式：

| 格式 | 提取方式 | 说明 |
|------|---------|------|
| doc/docx/rtf/odt/pages | textutil | macOS 原生，提取质量高 |
| xlsx | openpyxl | 按 Sheet 输出，保留表格结构 |
| xls | textutil/strings | 旧格式，尽力提取 |
| pptx | zipfile XML | 按 Slide 输出文本 |
| ppt | textutil/strings | 旧格式，尽力提取 |
| pdf | pdftotext | 文字型 PDF 效果好；扫描件无法提取 |
| txt/md/csv/json/yaml/code | 直接读取 | 支持 UTF-8/GBK 编码 |

`--max-chars` 默认 50000，可根据需要调整。

## 搜索模式

### 内容搜索（默认）

```bash
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search "关键词"
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search -d ~/Documents "关键词"
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search -t md "关键词"
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search -t pdf -d ~/Downloads "机器学习"
```

### 文件名搜索

```bash
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search -name "README"
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search -name -d ~/Code -t swift "ViewModel"
```

### 最近修改的文件

```bash
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh recent 7
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh recent -d ~/Code -t md 3
```

### 文件元数据

```bash
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh meta /path/to/file
```

## 搜索参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-d <dir>` | 限定搜索目录 | `-d ~/Documents` |
| `-t <type>` | 文件类型过滤 | `-t pdf` |
| `-n <count>` | 最大结果数（默认 20） | `-n 10` |
| `-name` | 只匹配文件名 | `-name` |

## 支持的文件类型过滤

| 短名 | 文件类型 |
|------|---------|
| `md` | Markdown |
| `pdf` | PDF |
| `swift` | Swift 源码 |
| `py` | Python 脚本 |
| `txt` | 纯文本 |
| `doc`/`docx` | Word 文档 |
| `xls`/`xlsx` | Excel 表格 |
| `ppt`/`pptx` | PowerPoint |
| `pages` | Apple Pages |
| `keynote` | Apple Keynote |
| `numbers` | Apple Numbers |
| `html` | HTML |
| `json` | JSON |
| `yaml` | YAML |
| `csv` | CSV |
| `code` | 所有源代码（广义匹配） |
| `image` | 所有图片 |
| `audio` | 所有音频 |
| `video` | 所有视频 |

## 工作流程

### Step 1: 分析意图，选择搜索策略

从用户问题中判断：
- **搜什么**：关键词、文件名、还是某类文件
- **搜哪里**：全盘、特定目录、还是特定项目
- **什么类型**：是否限定文件类型
- **是否需要读取内容**：用户只是找文件，还是需要从文件中提取信息回答问题

### Step 2: 执行搜索

用 Bash 调用 spotlight.sh，根据意图组合参数。

如果结果太多，缩小范围（加 `-d`、`-t`、减小 `-n`）。
如果结果太少，扩大范围（去掉 `-t`、去掉 `-d`、换关键词）。

### Step 3: 提取文件内容

从搜索结果中选择最相关的文件，用 extract_text.py 提取内容。

**选择标准**：
- 文件名与查询意图匹配度
- 修改时间（越新越可能相关）
- 文件大小（过小可能无实质内容，过大可能是生成文件）

**提取命令**：
```bash
# 提取单个文件
python3 ${SKILLS_ROOT}/spotlight/scripts/extract_text.py "/path/to/file.xlsx"

# 限制提取长度（大文件时使用）
python3 ${SKILLS_ROOT}/spotlight/scripts/extract_text.py "/path/to/large.docx" --max-chars 20000
```

**对于纯文本格式**（txt/md/code 等），也可以直接用 Read 工具读取。extract_text.py 的优势在于处理二进制文档格式（Office/PDF）。

**如果需要从多个文件中提取信息**，可以并行调用多个 extract_text.py 命令。

### Step 4: 整合回答

基于提取的文件内容回答用户问题。回答时注明信息来源：

```
根据本地文件 [文件名]（路径：/path/to/file）：

[整合后的回答]
```

如果提取结果显示 `[Info] PDF contains no extractable text`，说明是扫描件/图片型 PDF，告知用户该文件无法提取文字。

## 高级用法：直接使用 mdfind

spotlight.sh 覆盖常见场景。遇到复杂查询时，可以直接使用 mdfind：

```bash
# 按作者搜索
mdfind "kMDItemAuthors == '*张三*'"

# 按文件大小（大于 10MB）
mdfind "kMDItemFSSize > 10485760"

# 组合条件：最近 30 天修改的 PDF 且包含 "AI"
mdfind "kMDItemContentModificationDate >= \$time.today(-30) && kMDItemContentType == 'com.adobe.pdf' && kMDItemTextContent == '*AI*'c"

# 搜索 Xcode 项目文件
mdfind "kMDItemContentType == 'com.apple.xcode.project'"
```

## 注意事项

- Spotlight 索引覆盖用户目录下大多数文件，但外接硬盘、部分 .gitignore 的目录可能未索引
- 搜索结果依赖 Spotlight 索引的实时性，刚创建的文件可能短暂延迟
- 扫描件 PDF（图片型）无法提取文字，会提示 "no extractable text"
- 二进制文件（图片、视频）只能按文件名或元数据搜索，无法搜内容
- 对于非常大的文件，使用 `--max-chars` 限制提取长度，避免输出过长
