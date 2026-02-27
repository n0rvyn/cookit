---
name: photos
description: 搜索和查看 Apple Photos 照片库。当用户需要查找照片、浏览相册、获取照片信息时使用。关键词：照片、Photos、相册、图片搜索、相片。
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/photos/scripts/*)
---

# Photos 照片库搜索

通过直接查询 Apple Photos 的 SQLite 数据库来搜索和浏览照片，支持关键词搜索、按时间浏览、相册管理和照片导出。

## 前提条件

- macOS 系统，且已使用 Apple Photos
- **Full Disk Access**：终端/Claude 需要 Full Disk Access 权限才能读取 Photos 数据库（System Settings > Privacy & Security > Full Disk Access）
- 只读操作，不会修改 Photos 数据库

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/photos/scripts" ] || SKILLS_ROOT="$BASE/cookit/mactools/skills"
```

## 工具

```
python3 ${SKILLS_ROOT}/photos/scripts/photos.py
```

## 命令

### 搜索照片

```bash
python3 ${SKILLS_ROOT}/photos/scripts/photos.py search "关键词"
python3 ${SKILLS_ROOT}/photos/scripts/photos.py search "关键词" -n 10
```

按文件名、标题匹配搜索照片。

### 最近照片

```bash
# 最近 7 天（默认）
python3 ${SKILLS_ROOT}/photos/scripts/photos.py recent

# 最近 30 天，最多 50 条
python3 ${SKILLS_ROOT}/photos/scripts/photos.py recent 30 -n 50
```

### 列出所有相册

```bash
python3 ${SKILLS_ROOT}/photos/scripts/photos.py albums
```

### 查看相册内照片

```bash
python3 ${SKILLS_ROOT}/photos/scripts/photos.py album "相册名称"
python3 ${SKILLS_ROOT}/photos/scripts/photos.py album "相册名称" -n 50
```

支持精确匹配和模糊匹配。

### 查看照片详细信息

```bash
# 按 UUID
python3 ${SKILLS_ROOT}/photos/scripts/photos.py info "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

# 按文件名
python3 ${SKILLS_ROOT}/photos/scripts/photos.py info "IMG_1234.HEIC"
```

显示：日期、尺寸、GPS 坐标、相机型号、镜头、焦距、文件大小等。

### 导出照片

```bash
# 导出到指定路径
python3 ${SKILLS_ROOT}/photos/scripts/photos.py export "UUID" "/tmp/output.heic"

# 导出到目录（自动使用原文件名）
python3 ${SKILLS_ROOT}/photos/scripts/photos.py export "UUID" "/tmp/"
```

## 输出格式

```
1. IMG_1234.HEIC
   UUID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
   Date: 2026-02-10 14:30:00
   Size: 4032x3024
   Location: 38.4872, 106.2309
   Path: ~/Pictures/Photos Library.photoslibrary/originals/A/IMG_1234.HEIC
```

## 工作流程

### Step 1: 理解搜索意图

从用户问题中判断：
- 搜什么：关键词、时间范围、特定相册
- 需要什么信息：找到照片即可，还是需要查看详情/导出

### Step 2: 执行搜索

根据意图选择合适的命令。如果结果太多，减小 `-n`；如果没找到，换关键词或扩大时间范围。

### Step 3: 深入查看或导出

对感兴趣的照片用 `info` 查看详情，或用 `export` 导出。

## 与 OCR 集成

找到的照片可以导出后交给 `mactools:ocr` 进行文字识别，适用于：
- 白板照片的文字提取
- 文档扫描件的内容识别
- 截图中的文字提取

流程：
1. 用 `search` 或 `recent` 找到目标照片
2. 用 `export` 导出到临时路径（如 `/tmp/photo.heic`）
3. 用 `mactools:ocr` 对导出的文件进行文字识别

## 注意事项

- 需要 Full Disk Access 权限才能访问 Photos 数据库
- 仅支持本地存储的照片；iCloud 未下载的照片无法导出（会提示）
- 照片路径基于 Photos 数据库记录，实际文件可能在 `originals/` 或 `masters/` 目录下
- 数据库结构可能因 macOS 版本不同有差异，脚本会自动适配
- Photos.app 运行时数据库可能被锁定，通常仍可读取
