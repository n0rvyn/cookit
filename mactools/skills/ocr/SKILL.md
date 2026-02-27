---
name: ocr
description: 使用 macOS Vision 框架对图片和扫描件 PDF 进行 OCR 文字识别。当用户需要从图片、截图、扫描件中提取文字时使用。关键词：OCR、文字识别、图片文字、截图文字、扫描件、识别。
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/ocr/scripts/*)
---

# Vision OCR

使用 macOS Vision 框架从图片和扫描件 PDF 中提取文字，支持中英文等多语言识别。

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/ocr/scripts" ] || SKILLS_ROOT="$BASE/cookit/mactools/skills"
```

## 工具

### OCR 脚本（解释执行）

```bash
swift ${SKILLS_ROOT}/ocr/scripts/ocr.swift <file_path> [options]
```

### OCR 二进制（编译后，更快）

首次使用前需编译：

```bash
bash ${SKILLS_ROOT}/ocr/scripts/build_ocr.sh
```

编译后使用：

```bash
${SKILLS_ROOT}/ocr/scripts/ocr <file_path> [options]
```

优先使用编译后的二进制。如果二进制不存在，先运行 build_ocr.sh 编译，再执行。

## 支持格式

| 格式 | 说明 |
|------|------|
| png, jpg, jpeg | 常见图片 |
| tiff | 高质量扫描件 |
| bmp, gif | 其他图片格式 |
| heic | Apple HEIC 格式（iPhone 照片） |
| pdf | 扫描件 PDF（自动渲染每页后 OCR；含文字层的 PDF 直接提取文字） |

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<file_path>` | 必需，图片或 PDF 文件路径 | - |
| `--lang <languages>` | 识别语言，逗号分隔 | `zh-Hans,en-US` |
| `--max-pages <n>` | PDF 最大处理页数 | `20` |

### 常用语言代码

| 代码 | 语言 |
|------|------|
| `zh-Hans` | 简体中文 |
| `zh-Hant` | 繁体中文 |
| `en-US` | 英语 |
| `ja` | 日语 |
| `ko` | 韩语 |
| `de` | 德语 |
| `fr` | 法语 |
| `es` | 西班牙语 |

## 使用示例

### 识别截图文字

```bash
swift ${SKILLS_ROOT}/ocr/scripts/ocr.swift ~/Desktop/screenshot.png
```

### 识别扫描件 PDF

```bash
swift ${SKILLS_ROOT}/ocr/scripts/ocr.swift ~/Documents/scanned.pdf
```

### 指定识别语言

```bash
# 仅英文
swift ${SKILLS_ROOT}/ocr/scripts/ocr.swift image.png --lang en-US

# 中日英混合
swift ${SKILLS_ROOT}/ocr/scripts/ocr.swift image.png --lang zh-Hans,en-US,ja
```

### 限制 PDF 处理页数

```bash
swift ${SKILLS_ROOT}/ocr/scripts/ocr.swift large.pdf --max-pages 5
```

## 工作流程

### Step 1: 确认文件路径

用户提供文件路径后，确认文件存在。如果用户说"桌面上的截图"但未给路径，可以用 Spotlight 搜索或列出桌面文件来定位。

### Step 2: 检查二进制是否存在

优先使用编译后的二进制（更快）。如果不存在，先编译：

```bash
bash ${SKILLS_ROOT}/ocr/scripts/build_ocr.sh
```

### Step 3: 执行 OCR

```bash
${SKILLS_ROOT}/ocr/scripts/ocr <file_path>
```

如果二进制不可用，回退到解释执行：

```bash
swift ${SKILLS_ROOT}/ocr/scripts/ocr.swift <file_path>
```

### Step 4: 返回结果

将提取的文字返回给用户。如果用户有进一步需求（翻译、整理、分析），基于提取的文字继续处理。

## 与 Spotlight 联合使用

Spotlight 搜索找到图片文件后，用 OCR 提取图中文字：

```bash
# 1. 用 Spotlight 找到图片文件
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search -t image "会议"

# 2. 对搜索到的图片执行 OCR
${SKILLS_ROOT}/ocr/scripts/ocr /path/to/found_image.png
```

也可以对 Spotlight 搜出的扫描件 PDF 执行 OCR（spotlight extract_text.py 无法处理扫描件，OCR 可以）：

```bash
# 1. Spotlight 搜索 PDF
${SKILLS_ROOT}/spotlight/scripts/spotlight.sh search -t pdf "合同"

# 2. 如果 extract_text.py 提示 "no extractable text"，用 OCR
${SKILLS_ROOT}/ocr/scripts/ocr /path/to/scanned.pdf
```

## 注意事项

- OCR 准确率取决于图片质量；模糊、低分辨率图片识别效果较差
- 扫描件 PDF 会逐页渲染后 OCR，处理时间与页数成正比
- 含文字层的 PDF 直接提取嵌入文字（速度快、更准确），不会做 OCR
- 大 PDF 文件默认只处理前 20 页，通过 --max-pages 调整
- 输出文字为纯文本，不保留原始排版格式
- 首次使用解释执行（swift ocr.swift）启动较慢，建议编译后使用
