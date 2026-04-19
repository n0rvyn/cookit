---
name: netease-cloud-music
description: "操作网易云音乐云盘，基于维护中的 ncmctl CLI 进行 Cookie 登录、CookieCloud 登录与云盘上传。兼容用户可能说的 netease-music-cloud。Use when the user asks about NetEase Cloud Music cloud drive, 网易云音乐云盘, ncmctl, cookie login, CookieCloud login, or cloud uploads. Keywords: 网易云音乐, 云盘, netease-cloud-music, netease-music-cloud, ncmctl, CookieCloud."
context: fork
model: haiku
allowed-tools: Bash(*skills/netease-cloud-music/scripts/*)
---

# NetEase Cloud Music

通过 `ncmctl` 调用网易云音乐的社区实现接口，优先走已维护 CLI，而不是直接在 skill 里拼逆向请求。

## 已验证的选型结论

- `Binaryify/NeteaseCloudMusicApi` 是历史上最主流的 Node 方案，但主仓库已归档
- `pyncm` 仍在发版，适合 Python 集成
- `chaunsin/netease-cloud-music` 的 `ncmctl` 已把登录、CookieCloud、云盘上传整成 CLI；作为日常操作入口更顺手

## 前提条件

- 本机已安装 `ncmctl`
- 需要网易云音乐登录态
- 推荐优先使用 Cookie 或 CookieCloud

## 工具

```bash
${CLAUDE_SKILL_DIR}/scripts/netease_cloud_music_doctor.sh
${CLAUDE_SKILL_DIR}/scripts/netease_cloud_music.sh
```

## 推荐流程

### 1. 先检查环境

```bash
${CLAUDE_SKILL_DIR}/scripts/netease_cloud_music_doctor.sh
```

### 2. 登录

Cookie 文件导入：

```bash
${CLAUDE_SKILL_DIR}/scripts/netease_cloud_music.sh login cookie -f cookie.txt
```

CookieCloud：

```bash
${CLAUDE_SKILL_DIR}/scripts/netease_cloud_music.sh login cookiecloud -u <用户名> -p <密码> -s http://127.0.0.1:8088
```

说明：

- CookieCloud 比手工复制 Cookie 更省事
- 二维码登录不是主推路径；上游 README 已标注风控导致 `8821`

### 3. 上传到云盘

上传单文件：

```bash
${CLAUDE_SKILL_DIR}/scripts/netease_cloud_music.sh cloud '/path/to/music.mp3'
```

上传目录：

```bash
${CLAUDE_SKILL_DIR}/scripts/netease_cloud_music.sh cloud '/path/to/music/'
```

目录上传说明：

- 上游 README 标注支持并行批量上传
- 目录深度不要超过 3 层
- 更多过滤条件看 `ncmctl cloud -h`

## 风险边界

- 这是社区逆向方案，不是网易云音乐官方开放平台
- 风控是真实存在的；上游 2025-06-03 明确提示高风险行为会触发警告
- skill 默认面向“登录、导入 Cookie、上传云盘”，不鼓励刷任务或高频调用

## 不做的事

- 不声称网易云官方提供个人云盘公开 API
- 不在本 skill 里重写上传协议
- 不自动安装 `ncmctl`；如未安装，doctor 会直接报缺失
