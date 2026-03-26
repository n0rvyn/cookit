---
name: setup-ci-cd
description: "Use when setting up CI/CD for the first time, or the user says 'setup CI', 'configure CI', 'Xcode Cloud', 'auto version', '版本自动化', '配置 CI'. Configures Xcode Cloud build number management and GitHub Actions automatic version bumping based on conventional commits."
compatibility: "Requires macOS and Xcode"
disable-model-invocation: true
---

# Setup CI/CD

配置 Xcode Cloud + GitHub Actions，实现自动版本管理和分发。

**职责分工**：
- **GitHub Actions**（ubuntu-latest）：根据 conventional commit 自动 bump `MARKETING_VERSION`（semver）
- **Xcode Cloud**（Apple 托管）：构建时自动设置 `CURRENT_PROJECT_VERSION`（build number），分发到 TestFlight / App Store

## 触发时机

- 新项目初始化时（由 `/project-kickoff` 步骤 9.10 调用）
- 现有项目需要添加版本自动化时（单独调用）

## 前置知识

| 概念 | Build Setting | 格式 | 管理方 | 说明 |
|------|--------------|------|--------|------|
| 版本号 | `MARKETING_VERSION` | semver `1.2.0` | GitHub Actions | 用户在 App Store 看到的版本 |
| 构建号 | `CURRENT_PROJECT_VERSION` | 整数 `42` | Xcode Cloud | ASC 内部区分同版本的不同构建 |

## 流程

### 1. 检测项目环境

```bash
# 找到 .xcodeproj
xcodeproj=$(find . -maxdepth 2 -name "*.xcodeproj" -not -path "*/DerivedData/*" | head -1)
project_name=$(basename "$xcodeproj" .xcodeproj)
pbxproj="${xcodeproj}/project.pbxproj"

# 提取当前版本号（所有 target）
grep -n 'MARKETING_VERSION\|CURRENT_PROJECT_VERSION' "$pbxproj"

# 检查 Apple Generic versioning
grep 'VERSIONING_SYSTEM' "$pbxproj"
```

如果找不到 `.xcodeproj`，终止并提示用户确认目录。

展示检测结果表格：

| Target | MARKETING_VERSION | CURRENT_PROJECT_VERSION |
|--------|------------------|----------------------|
| {从 pbxproj 解析} | ... | ... |

### 2. 修复版本一致性

**条件判断后执行**，不需要全部执行：

#### 2.1 统一 MARKETING_VERSION

如果各 target 值不一致，以主 app target 的值为准，用 `sed` 全局替换。

如果当前是两位格式（如 `1.0`），询问用户是否迁移到三位（`1.0.0`）：

**询问用户**（使用 AskUserQuestion）：

> 当前 MARKETING_VERSION 是 `{current}`，是否迁移到三位 semver？
>
> - **迁移到 {current}.0** — 推荐，支持 patch 级别的版本管理
> - **保持当前格式** — 不改变

#### 2.2 统一 CURRENT_PROJECT_VERSION

如果各 target 值不一致，取最大值，用 `sed` 替换较小的值。

注意：`sed` 替换 `CURRENT_PROJECT_VERSION = 1;` 时必须精确匹配 `= 1;`（带空格和分号），避免误替换 `= 11;` 等值。如果存在多个不同的小值（如 1 和 5），需要逐个替换。

#### 2.3 启用 Apple Generic Versioning

如果 `grep VERSIONING_SYSTEM` 无结果，需要在项目级（非 target 级）的 Debug 和 Release buildSettings 中添加：

```
VERSIONING_SYSTEM = "apple-generic";
```

**定位方式**：在 pbxproj 中找到项目级 `XCBuildConfiguration` 的 `buildSettings` 块（通常包含 `ALWAYS_SEARCH_USER_PATHS`、`CLANG_ANALYZER_NONNULL` 等全局设置），在其中添加 `VERSIONING_SYSTEM`。

添加后验证：

```bash
cd "$(dirname "$xcodeproj")"
agvtool what-version
agvtool what-marketing-version
```

两个命令都应返回正确的值。如果 `agvtool` 报错，说明 Apple Generic 未正确启用。

### 3. 选择触发分支

**询问用户**（使用 AskUserQuestion）：

> GitHub Actions auto-version workflow 在哪些分支触发？
>
> - **main + dev**（推荐） — 两个分支的 push 都自动 bump 版本
> - **仅 main** — 只在合并到 main 时 bump
> - **自定义** — 指定分支列表

### 4. 创建 GitHub Actions auto-version workflow

Read `references/auto-version-template.yml`，替换占位符后写入 `.github/workflows/auto-version.yml`：

| 占位符 | 替换为 | 来源 |
|--------|--------|------|
| `__BRANCHES__` | 用户选择的分支列表 | 步骤 3 |
| `__PBXPROJ_PATH__` | pbxproj 相对路径 | 步骤 1 检测结果 |

创建目录（如果不存在）：`mkdir -p .github/workflows`

### 5. 创建 Xcode Cloud ci_post_clone.sh

Read `references/ci-post-clone-template.sh`，写入 `ci_scripts/ci_post_clone.sh`。

```bash
mkdir -p ci_scripts
# 写入文件内容
chmod +x ci_scripts/ci_post_clone.sh
```

### 6. 验证

```bash
# 1. 版本一致性
grep 'MARKETING_VERSION\|CURRENT_PROJECT_VERSION' "$pbxproj"

# 2. Apple Generic
grep 'VERSIONING_SYSTEM' "$pbxproj"

# 3. agvtool
agvtool what-version
agvtool what-marketing-version

# 4. ci_post_clone.sh 可执行
ls -la ci_scripts/ci_post_clone.sh

# 5. workflow 文件存在
cat .github/workflows/auto-version.yml | head -5
```

### 7. 输出配置结果和 Xcode Cloud 指引

```
✅ 版本自动化配置完成

已创建/修改：
- .github/workflows/auto-version.yml — 自动版本 bump
- ci_scripts/ci_post_clone.sh — Xcode Cloud 构建号
- {project}.xcodeproj — 版本统一 + Apple Generic

版本管理方式：
- MARKETING_VERSION：push 到 {branches} 时，根据 commit 类型自动 bump
  - feat: → minor（1.0.0 → 1.1.0）
  - fix: → patch（1.0.0 → 1.0.1）
  - feat!: / BREAKING CHANGE → major（1.0.0 → 2.0.0）
- CURRENT_PROJECT_VERSION：Xcode Cloud 每次构建自动递增

下一步 — 配置 Xcode Cloud（需在 Xcode 中操作）：

1. 打开 Xcode → Product → Xcode Cloud → Create Workflow
2. 首次需关联 Git 仓库

推荐创建两个 Workflow：

【Dev to TestFlight】
- 触发：Branch Changes → dev
- Actions：Build → Archive
- Post-Action：TestFlight Internal Testing
- 自动取消构建：开启

【Main to App Store】
- 触发：Branch Changes → main
- Actions：Build → Test → Archive
- Post-Action：TestFlight External + App Store Connect
- 自动取消构建：关闭
```

## 原则

1. **零 Secret**：不需要配置任何 GitHub Secret 或 API Key
2. **ubuntu-latest**：GitHub Actions 版本管理不需要 macOS runner（10x 成本差异）
3. **职责分离**：GitHub Actions 管版本号（轻量），Xcode Cloud 管构建和分发（重量）
4. **所有 target 同步**：sed 全局替换 + agvtool -all 保证版本一致
5. **Sonnet 友好**：流程化操作，无需复杂推理
