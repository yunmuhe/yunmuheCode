# KEYHUB

KEYHUB 是一个本地 Web UI + CLI 工具，用来集中管理多套 AI API Key，并一键把“当前选中 Key”写入到各家官方 CLI（Codex / Claude Code / Gemini）的配置中。

## 安全提示（重要）

- `keys.json` 会保存明文 Key，请务必妥善保管，不要提交到 Git，不要发到 Issue/群里，不要截图分享。
- 建议把配置文件权限收紧：`chmod 600 ~/keys.json`
- 如果你使用了“执行写入”，KEYHUB 可能会把 Key 写入到各 CLI 的本地配置/环境变量中；不再使用时请按本文档的卸载/回滚方式清理。

它解决的问题：
- 多个 Key（不同提供商/不同用途）来回切换麻烦
- 想直观看到当前选中/已应用（APPLIED）的 Key
- 换机器时希望只迁移一份配置文件（`keys.json`）

## 功能

- Keys 管理：新增/编辑/删除，支持备注、分类、余量等字段
- Providers 管理：维护服务提供商（名称、模型、API URL、官网等）
- CLI Target：支持 `codex` / `claude` / `gemini`
- 一键写入（执行写入）：把当前 Key 导出/写入到目标 CLI
- Claude `apiKeyHelper` 自动配置：导出 Claude 时自动更新 `~/.claude/settings.json` 的 `apiKeyHelper` 并生成 helper 脚本

## 快速开始

### 方式 A：推荐（pip + venv，跨平台通用）

在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r projects/KEYHUB/requirements.txt
python3 projects/KEYHUB/run_keyhub_web.py --no-debug
```

然后打开：`http://127.0.0.1:5000`

### 方式 B：一键启动脚本

#### Windows

- 启动：双击 [KEYHUB-Start-Windows.bat](KEYHUB-Start-Windows.bat)
- 打开：`http://127.0.0.1:5000`
- 停止/重启：双击 [KEYHUB-Stop-Windows.bat](KEYHUB-Stop-Windows.bat) / [KEYHUB-Restart-Windows.bat](KEYHUB-Restart-Windows.bat)

#### macOS

- 启动：双击 [KEYHUB-Start-macOS.command](KEYHUB-Start-macOS.command)
- 打开：`http://127.0.0.1:5000`
- 停止：双击 [KEYHUB-Stop-macOS.command](KEYHUB-Stop-macOS.command)
- 重启：双击 [KEYHUB-Restart-macOS.command](KEYHUB-Restart-macOS.command)

> 说明：Stop/Restart 依赖同目录下的 `.keyhub.pid`，只能停止由启动脚本启动的那次进程。

## 配置文件（keys.json）

- KEYHUB 默认配置路径：`~/keys.json`（见 [keyhub_models.py:12](keyhub_models.py#L12)）
- 推荐：用环境变量 `KEYHUB_CONFIG` 指向你自己的配置文件路径（这样迁移/多机器更稳，也更容易把配置放到更安全的位置）
- Claude helper 会优先读取 `KEYHUB_CONFIG` 指向的文件；未设置时会尝试读取 `~/keys.json`

## CLI 生效位置（Codex / Claude / Gemini）

- Codex：写入 `~/.codex/auth.json` 的 `OPENAI_API_KEY`
- Claude Code：通过 `~/.claude/settings.json` 的 `apiKeyHelper` 获取 key（KEYHUB 会生成 `~/.claude/keyhub_api_key_helper.py`）
- Gemini：写入 shell profile（macOS/Linux）或用户级环境变量（Windows），需要新开一个终端会话才会对新进程生效

## Claude Helper（apiKeyHelper）

KEYHUB 会在你执行 Claude 的“执行写入”时：
- 生成 `~/.claude/keyhub_api_key_helper.py`
- 在 `~/.claude/settings.json` 写入/更新 `apiKeyHelper`

手动卸载（撤销 Helper）：
- 编辑 `~/.claude/settings.json`，删除 `apiKeyHelper` 字段
- 删除 `~/.claude/keyhub_api_key_helper.py`

## 版本更新（Changelog）

- 2026-02
  - 增加 Windows/macOS 启动/停止/重启脚本三件套
  - 文档补充 Claude helper 跨环境迁移说明（推荐 `KEYHUB_CONFIG`）
  - 修复 UI：选中状态下点击“新增 KEY”不再自动关闭弹窗
