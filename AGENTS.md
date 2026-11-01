# Repository Guidelines

## 项目结构与模块组织
本仓库包含两个主要子项目。`NameGenerationAgent/` 是 Python 后端，核心代码位于 `src/`，配置在 `config/`，测试在 `tests/`，运行数据与日志分别在 `data/`、`logs/`。`智能姓名生成系统/` 是 uni-app 前端，页面放在 `pages/`，应用入口相关文件为 `App.vue`、`main.ts`、`index.html`，共享逻辑在 `common/`，静态资源在 `static/`，测试在 `tests/`。根目录 `docs/design/` 存放正式设计文档，`docs/plans/` 仅用于本地 AI 规划草稿且不纳入版本控制。开始修改前，先确认变更落在正确子项目内。

## 构建、测试与开发命令
后端命令在 `NameGenerationAgent/` 目录执行：

```bash
pip install -r requirements.txt
python main.py
python -m pytest tests/ -v
python -m pytest tests/test_basic.py::TestNameGenerator::test_get_available_options -v
```

`python main.py` 用于本地启动服务，`pytest` 用于全量或定点回归。启动前从 `.env.example` 复制出 `.env` 并填写所需 API Key；仓库不再提供 Windows `.bat` 启动脚本，Windows 环境直接执行同一组 Python 命令即可。

前端命令在 `智能姓名生成系统/` 目录执行：

```bash
npm install
npm run dev
npm run build

npm run test:theme
npm run test:phone-mask
npm run test:settings
```

`npm run dev` 启动本地开发服务，`npm run build` 生成发布产物。原有 npm 脚本使用 Windows 风格的 `set VAR=...` 写法，非 Windows 环境可在命令前显式设置 `UNI_INPUT_DIR=.`（例如 `UNI_INPUT_DIR=. npx uni build -p h5`）。

## 代码风格与命名规范
Python 统一使用 4 空格缩进，函数与变量使用 `snake_case`，类名使用 `PascalCase`，异常优先复用现有 `APIException`。前端沿用现有 uni-app / Vue 3 写法，页面目录名、路由名和文件名保持一致，避免无意义缩写。修改日志相关逻辑时，优先复用后端现有日志工具，不要自行分散打印方式。

## 测试规范
后端测试框架为 `pytest`，测试文件命名遵循 `test_*.py`。新增或修复后端行为时，优先补充与改动模块对应的测试，例如适配器改动放入 `tests/test_*adapter.py`，认证改动放入 `tests/test_auth_*.py`。前端使用 `tsx` 运行 `tests/` 下的 TypeScript 测试（见上面的 `npm run test:*` 命令）。提交前至少完成这些测试和关键页面与接口联调。

## 提交与 Pull Request 规范
提交信息遵循 Conventional Commits，并建议带上作用域，例如 `feat(adapter): ...`、`fix(admin): ...`、`docs(admin): ...`。Pull Request 应说明变更目的、影响范围、验证命令；涉及后台界面或前端页面时，附截图；涉及配置变更时，注明 `.env`、数据库或部署影响。

## Agent 协作说明
与仓库相关的协作说明统一使用简体中文。优先使用现有命令、配置和项目工具完成任务，只有在现有手段无法解决时才新增脚本。不要提交密钥、真实凭证或本地环境专用配置文件。
