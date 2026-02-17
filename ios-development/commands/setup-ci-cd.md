---
name: setup-ci-cd
description: 配置 Fastlane 与 GitHub Actions，实现自动化构建和 TestFlight 上传。
---

# Setup CI/CD

配置 Fastlane + GitHub Actions，实现打 tag 自动上传 TestFlight。

## 触发时机

- 新项目初始化时（由 `/project-kickoff` 调用）
- 现有项目需要添加 CI/CD 时（单独调用）

## 流程

### 1. 确认项目路径和 Scheme

询问用户：
- 当前目录是否为 Xcode 项目根目录？
- App 的 Scheme 名称是什么？（如 `MyApp`）

### 2. 生成 Fastlane 配置

创建 `fastlane/Fastfile`：

```ruby
default_platform(:ios)

platform :ios do
  desc "Release to TestFlight"
  lane :release do
    setup_ci

    match(
      type: "appstore",
      readonly: true
    )

    build_app(
      scheme: "[Scheme名称]",
      export_method: "app-store"
    )

    upload_to_testflight(
      skip_waiting_for_build_processing: true
    )
  end
end
```

创建 `fastlane/Gemfile`：

```ruby
source "https://rubygems.org"

gem "fastlane"
```

### 3. 生成 GitHub Actions Workflow

创建 `.github/workflows/release.yml`：

```yaml
name: Release to TestFlight

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Install Fastlane
        run: gem install fastlane

      - name: Release to TestFlight
        env:
          FASTLANE_USER: ${{ secrets.FASTLANE_USER }}
          FASTLANE_PASSWORD: ${{ secrets.FASTLANE_PASSWORD }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
        run: fastlane release
```

### 4. 更新 .gitignore

添加 Fastlane 相关忽略：

```
# Fastlane
fastlane/report.xml
fastlane/Preview.html
fastlane/screenshots
fastlane/test_output
```

### 5. 输出配置说明

```
✅ CI/CD 配置已生成

生成文件：
- fastlane/Fastfile
- fastlane/Gemfile
- .github/workflows/release.yml
- .gitignore (已更新)

下一步配置 GitHub Secrets：

1. 在 GitHub 仓库设置中添加以下 Secrets：
   - FASTLANE_USER: Apple ID 邮箱
   - FASTLANE_PASSWORD: App-specific password（在 appleid.apple.com 生成）
   - MATCH_PASSWORD: 签名证书密码（如使用 match）

2. 配置 Fastlane Match（可选，推荐）：
   ```bash
   fastlane match init
   fastlane match appstore
   ```

3. 测试本地 release：
   ```bash
   fastlane release
   ```

4. 发布版本：
   ```bash
   git tag v1.0.0
   git push --tags
   ```
   → GitHub Actions 自动上传 TestFlight

详细文档：https://docs.fastlane.tools/
```

## 原则

1. **个人开发者优化**：只配置 tag 上传，不配置每次 push 的 CI
2. **最小配置**：只需要 3 个 GitHub Secrets
3. **本地可测试**：Fastlane 配置可以在本地运行测试
