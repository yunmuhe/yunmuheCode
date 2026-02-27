# KEYHUB 项目进度与要点（Claude）

> 目标：重做并优化 KEYHUB 的 Web UI/UX（暗黑极简风），补齐 Key / Provider 管理能力与 CLI 集成，并提供 Windows 一键启动体验。项目文件统一放在 `projects/KEYHUB/`。

## 当前已完成

### 1) Keys 模块（列表 + 交互 + 数据）
- Keys 列表底部增加 footer，并显示：`Total：{{ config.keys | length }} Keys`。
- 删除 Key 后 ID 自动重排为连续 `1..N`，并同步更新 `current` 映射；加载配置时也会 normalize 旧数据（修复跳号/重复）。
- Keys 选中交互：点击整行触发选中（提交 `/use/<cli>/<key_id>`），当前选中行整行高亮。
- 表格列调整：新增 `余量` 列，KeyRecord 新增字段 `quota_remaining`，支持新增/编辑保存与展示。
- KEY 安全展示：列表中 KEY 脱敏显示，保留前缀与后 4 位（后 4 位高亮），便于识别。
- 新增/编辑弹窗：KEY 输入不隐藏（明文），编辑时会回填当前 key 供核对。

### 2) Providers 模块（独立面板 + CRUD）
- CLI Target 下方新增独立的「服务提供商」面板，样式与 Keys 一致。
- Provider 字段：ID、名称、AI 应用(models)、API URL、官方网站、添加时间、状态、操作（Edit/Del）。
- Provider 数据模型升级：`ProviderRecord.website` 支持；兼容旧字段 `homepage`；旧 models 值 `codex` 自动映射到 `openai`。
- Provider CRUD 路由已接入：`/providers/add`、`/providers/edit/<id>`、`/providers/delete/<id>`。

### 3) CLI Target 与导出（Applied 检测）
- 支持多个 CLI：`codex` / `claude` / `gemini`。
- 页面显示 APPLIED 状态：
  - Codex：读取 `~/.codex/auth.json` 的 `OPENAI_API_KEY`（匹配 keys.json 里的 key 值）。
  - Claude：通过 Claude Code 的 `apiKeyHelper` 机制读取（KEYHUB 会在导出 Claude 时自动配置本机 `~/.claude/settings.json`）。

#### 跨环境迁移（推荐做法）
- 不要直接复制 `~/.claude/settings.json` 到新机器（里面可能包含本机路径/插件配置，且 `apiKeyHelper` 命令会写入当前 Python 路径）。
- 把可迁移资产收敛成 1 个文件：你的 KEYHUB 配置（`keys.json`），并用环境变量 `KEYHUB_CONFIG` 指向它。
- 新机器恢复步骤：
  1) 安装 Python（能运行 KEYHUB 即可）
  2) 设置 `KEYHUB_CONFIG` 指向迁移后的 `keys.json`
  3) 打开 KEYHUB，执行一次 Claude 的「执行写入」（会自动生成/更新 `~/.claude/keyhub_api_key_helper.py` 与 `~/.claude/settings.json:apiKeyHelper`）

#### 手动卸载（撤销 Helper）
- 编辑 `~/.claude/settings.json`，删除 `apiKeyHelper` 字段
- 删除 `~/.claude/keyhub_api_key_helper.py`

### 4) 启动体验（Windows/macOS）
- `projects/KEYHUB/run_keyhub_web.py`：可在任意目录启动 Web（自动把 KEYHUB 加入 `sys.path`）。
- Windows：双击 `projects/KEYHUB/KEYHUB-Start-Windows.bat`（停止/重启：`KEYHUB-Stop-Windows.bat` / `KEYHUB-Restart-Windows.bat`）。
- macOS/Linux：运行 `projects/KEYHUB/KEYHUB-Start-macOS.sh`（停止/重启：`KEYHUB-Stop-macOS.sh` / `KEYHUB-Restart-macOS.sh`）。

### 5) UI/CSS 管理
- 将 `index.html` 内联 CSS 抽离为独立文件：`projects/KEYHUB/templates/keyhub.css`。
- Flask 提供 CSS：`GET /assets/keyhub.css`（`keyhub_app.py` 内实现）。

### 6) 弹窗体验（防误触 + 保存反馈）
- 弹窗 overlay 不再因为鼠标移到框外就关闭（只保留右上角 ✕ 与 ESC）。
- 保存按钮文案统一为「保存」。
- 保存后给弹窗加绿色高亮框（`.modal.saved`）并把按钮改为「保存成功」：
  - 后端通过 cookie `kh_saved` 标记保存动作；
  - 前端 `DOMContentLoaded` 读取 cookie 并自动打开对应弹窗显示成功态。

## 关键文件索引
- Web 模板（UI + JS）：`projects/KEYHUB/templates/index.html`
- 样式（独立 CSS）：`projects/KEYHUB/templates/keyhub.css`
- Flask 应用（路由/渲染/保存反馈 cookie/CSS 路由）：`projects/KEYHUB/keyhub_app.py`
- 数据模型与持久化（Key/Provider/重排逻辑）：`projects/KEYHUB/keyhub_models.py`
- CLI 导出（Codex/Claude 读写）：`projects/KEYHUB/keyhub_export.py`
- 启动器：`projects/KEYHUB/run_keyhub_web.py`
  - Windows：`projects/KEYHUB/KEYHUB-Start-Windows.bat` / `KEYHUB-Stop-Windows.bat` / `KEYHUB-Restart-Windows.bat`
  - macOS/Linux：`projects/KEYHUB/KEYHUB-Start-macOS.sh` / `KEYHUB-Stop-macOS.sh` / `KEYHUB-Restart-macOS.sh`

## 当前交互约定（重要）
- KEY 列表：显示脱敏值；编辑弹窗显示明文 key；新增弹窗输入明文 key。
- 状态列：已简化为绿点（active）/ `—`（无）。
- 弹窗关闭：当前允许 `✕` 与 `ESC`；不再支持点击遮罩关闭。

## 待办 / 下一步建议
- 是否完全禁用 `ESC` 关闭弹窗（只允许右上角 ✕）。
- 优化“保存成功”状态持续时长与回退（例如自动 1.2s 后恢复按钮文字）。
- 进一步统一中英文文案（例如 modal 标题 Create Key / Edit Key / Add Provider）。
- 将 CSS 放入 `projects/KEYHUB/static/` 并使用 Flask static（如果后续需要缓存控制与资源组织）。
- 安全：当前编辑弹窗会回填明文 key（为核对便利）；如需更安全可改为“点击显示/复制”模式。
