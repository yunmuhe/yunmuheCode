# 名字生成智能体

本仓库包含智能姓名生成系统的后端服务、前端应用和少量任务留档。项目说明入口统一收敛到这份根目录 `README.md`，其他已跟踪说明文档不再保留。

## 仓库概览

- 后端位于 `NameGenerationAgent/`，基于 Flask，负责姓名生成、模型发现、认证、收藏、历史记录和管理员后台。
- 前端位于 `智能姓名生成系统/`，基于 uni-app，负责多端界面与用户交互。
- 后端核心能力包括多平台 AI 适配、自动降级、语料库增强、模型动态发现、用户认证和生成记录持久化。

## 目录结构

```text
.
├── README.md
├── NameGenerationAgent/
│   ├── config/
│   ├── src/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── data/
│   │   ├── utils/
│   │   └── web/
│   ├── data/
│   ├── deploy/
│   ├── logs/
│   ├── scripts/
│   ├── tests/
│   ├── env.example
│   ├── main.py
│   ├── quick_start.bat
│   ├── setup_domain.bat
│   └── start_natapp.bat
├── 智能姓名生成系统/
│   ├── common/api.ts
│   ├── pages/Generate/Generate.vue
│   └── package.json
└── docs/plans/
```

## 快速开始

后端相关命令都在 `NameGenerationAgent/` 目录执行。

```bash
cd NameGenerationAgent

# Windows
..\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化环境变量
copy env.example .env

# 启动服务
quick_start.bat
# 或
python main.py

# 基础检查
curl http://127.0.0.1:5000/health
```

前端开发：

```bash
cd 智能姓名生成系统
npm install
npm run dev:h5
npm run dev:mp-weixin
```

## 开发与协作约定

- Python 目标版本为 3.8+。
- 后端代码风格使用 4 空格缩进，函数和变量使用 `snake_case`，类使用 `PascalCase`。
- 为避免循环依赖，优先使用延迟导入。
- 适配器异常统一使用 `APIException`。
- 日志优先走 `src/utils/logger.py`，适配器内部兼容 `src/utils/logging_helper.py`。
- 测试框架使用 `pytest`，测试文件位于 `NameGenerationAgent/tests/`，命名遵循 `test_*.py`。
- Git 提交约定建议使用 Conventional Commits，例如 `feat:`、`fix:`、`docs:`、`refactor:`、`test:`。

常用测试命令：

```bash
cd NameGenerationAgent
python -m pytest tests/ -v
python -m pytest tests/test_basic.py::TestNameGenerator::test_get_available_options -v
python -m pytest tests/test_corpus_integration.py -v
python tests/test_model_discovery.py
```

## 系统架构

后端采用分层结构：

```text
Web 层   -> src/web/app.py, src/web/admin_views.py
Core 层  -> src/core/name_generator.py, auth_service.py, record_service.py
API 层   -> src/api/adapters/, unified_client.py, router_strategy.py, model_manager.py
Data 层  -> src/data/corpus_loader.py, src/db/
Utils 层 -> src/utils/logger.py, validation.py, cache_manager.py
```

核心机制：

- 适配器模式：不同 AI 平台通过 `src/api/adapters/*_adapter.py` 统一暴露 `generate_names()`。
- 路由策略：`PriorityRouterStrategy`、`WeightedRouterStrategy`、`RoundRobinRouterStrategy`、`CapabilityRouterStrategy`。
- 自动降级：首选平台失败后切换下一个可用平台。
- 语料库增强：通过 `data/names_corpus.db` 提供中文姓名示例和命名偏好增强。
- 缓存：生成结果和模型列表都有缓存，减少重复请求和第三方调用。

当前接入的平台：

- `aliyun`
- `siliconflow`
- `openai`
- `gemini`
- `paiou`
- `aistudio`

## 核心 API

### 公开接口

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回系统信息和主要端点 |
| `/health` | GET | 健康检查 |
| `/options` | GET | 获取风格、性别、年龄、平台等选项 |
| `/models` | GET | 获取所有平台或单个平台的模型列表 |
| `/stats` | GET | 返回系统统计信息 |

### 需要 Bearer Token 的接口

| 路径 | 方法 | 说明 |
|------|------|------|
| `/generate` | POST | 生成姓名并持久化记录 |
| `/history` | GET | 获取最近一次历史记录 |
| `/history/list` | GET | 分页获取当前用户历史记录 |
| `/favorites` | GET/POST/DELETE | 获取、写入、删除当前用户收藏 |
| `/auth/me` | GET | 获取当前登录用户信息 |
| `/auth/logout` | POST | 注销当前 token |
| `/auth/change-password` | POST | 修改当前用户密码 |

### 认证接口

| 路径 | 方法 | 说明 |
|------|------|------|
| `/auth/register` | POST | 手机号注册 |
| `/auth/login` | POST | 手机号登录并返回 token 与用户信息 |

`/generate` 常用参数：

- `description`：角色描述，必填
- `count`：生成数量，范围 1 到 20
- `cultural_style`：文化风格
- `gender`：性别
- `age`：年龄段
- `preferred_api`：首选平台
- `model`：指定模型
- `use_cache`：是否启用缓存
- `preferred_surname` / `surname_weight`：偏好姓氏与权重
- `preferred_era` / `era_weight`：偏好时代与权重

## 前端接入

前端项目位于 `智能姓名生成系统/`，主要接口封装在 `智能姓名生成系统/common/api.ts`，生成页实现位于 `智能姓名生成系统/pages/Generate/Generate.vue`。

建议接入顺序：

1. 页面启动时请求 `/options` 获取选项。
2. 如需模型选择器，请请求 `/models`。
3. 用户登录后，将 token 作为 `Authorization: Bearer <token>` 发送到需要鉴权的接口。
4. 生成页调用 `/generate`，历史页调用 `/history/list`，收藏页调用 `/favorites`。

跨域通过 `ALLOWED_ORIGINS` 控制，开发环境可在 `.env` 中配置本地 H5 域名。

## 模型发现与模型选择

系统支持通过 `/models` 动态返回可用模型列表。

支持方式：

- OpenAI：动态拉取模型列表
- 硅基流动：动态拉取模型列表
- Gemini：动态拉取模型列表
- 阿里云、派欧云、AI Studio：使用预定义列表作为稳定回退

接口形式：

```bash
# 获取所有平台模型
GET /models

# 获取特定平台模型
GET /models?api=aliyun

# 强制刷新缓存
GET /models?api=aliyun&refresh=true
```

说明：

- 模型列表按平台缓存，默认缓存 1 小时。
- 生成时可在 `/generate` 请求中加入 `model` 字段指定模型。
- 前端已有模型选择能力，切换平台后可刷新对应模型列表。

## 认证、MySQL 与管理后台现状

当前认证和后台能力已进入项目主流程，不只是设计稿：

- 支持用户注册、登录、登出、改密和 `/auth/me` 查询。
- 用户字段包含 `role`、`is_enabled`、`must_change_password`。
- 禁用用户会被拒绝登录。
- 管理员重置密码后，目标账户密码会被改为 `123456`，同时 `must_change_password=true`。
- `/generate`、`/history/list`、`/favorites` 都基于登录用户隔离数据。

数据库配置方式：

- 优先使用 `DATABASE_URL`
- 或使用以下拆分变量：
  - `DB_DIALECT`
  - `MYSQL_HOST`
  - `MYSQL_PORT`
  - `MYSQL_USER`
  - `MYSQL_PASSWORD`
  - `MYSQL_DATABASE`

管理员自举：

- `ADMIN_PHONE`
- `ADMIN_PASSWORD`

管理员后台入口：

- `/admin/login`
- `/admin`
- `/admin/users/<id>`
- `/admin/users/<id>/enable`
- `/admin/users/<id>/disable`
- `/admin/users/<id>/reset-password`
- `/admin/records/<id>/delete`

SQLite 到 MySQL 的迁移脚本：

```bash
cd NameGenerationAgent
python scripts/migrate_auth_sqlite_to_mysql.py \
  --sqlite-path data/auth.db \
  --target-db-url mysql+pymysql://name_agent_app:123456@127.0.0.1:3306/name_generation_agent?charset=utf8mb4
```

## 调试与故障排查

### 启动时显示 0 个 API 适配器

- 确认 `NameGenerationAgent/.env` 存在。
- 至少配置一个平台的 API Key。
- 检查 `config/api_config.py` 与 `src/api/adapters/__init__.py` 的注册逻辑。

### `/generate`、`/history/list`、`/favorites` 返回 401

- 这些接口要求 Bearer Token。
- 先调用 `/auth/login`，再在请求头里附带 `Authorization: Bearer <token>`。

### 登录返回 403

- 用户可能已被管理员禁用。

### 语料库未加载

- 检查 `NameGenerationAgent/data/names_corpus.db` 是否存在。
- 必要时在 `NameGenerationAgent/data/` 下运行 `python convert_csv_to_sqlite.py`。

### 模型列表为空或刷新失败

- 检查目标平台是否配置了 API Key。
- 某些平台依赖外网或代理。
- 可先使用缓存结果，或用 `refresh=true` 强制刷新。

### 查看日志

```bash
cd NameGenerationAgent
Get-Content .\logs\app.log -Wait -Tail 50
Get-Content .\logs\app.log -Wait -Tail 50 | Select-String -Pattern "ERROR|WARNING"
```

## 部署与性能

本仓库已保留几个现成入口：

- 内网穿透：`NameGenerationAgent/start_natapp.bat`
- 域名配置：`NameGenerationAgent/setup_domain.bat`
- 服务快速启动：`NameGenerationAgent/quick_start.bat`
- 服务器部署：`NameGenerationAgent/deploy/deploy_to_server.sh`

性能侧重点：

- 缓存命中可显著降低响应时间。
- 首次模型发现或远端模型查询明显慢于缓存命中。
- 生成接口耗时主要取决于目标平台响应时间。
- 若需压测，可使用 `NameGenerationAgent/tests/locustfile.py` 和 `NameGenerationAgent/tests/locustfile_cache_comparison.py`。

## 扩展开发

### 添加新的 AI 适配器

1. 在 `NameGenerationAgent/src/api/adapters/` 下新增 `*_adapter.py`。
2. 继承 `BaseAPIAdapter` 并实现 `generate_names()`。
3. 如需动态模型发现，实现 `list_models()`。
4. 在 `NameGenerationAgent/config/api_config.py` 中新增配置类并注册。
5. 在 `NameGenerationAgent/src/api/adapters/__init__.py` 中补充导入和工厂注册。
6. 根据需要更新路由优先级与默认模型。

### 添加新的路由策略

1. 在 `src/api/router_strategy.py` 中新增策略类。
2. 实现优先级计算逻辑。
3. 通过 `ROUTER_STRATEGY` 和 `ROUTER_WEIGHTS` 暴露配置。

### 扩展记录或后台能力

- 记录写入逻辑位于 `src/core/record_service.py`
- 认证逻辑位于 `src/core/auth_service.py`
- 后台蓝图位于 `src/web/admin_views.py`

## 关键文件

- `NameGenerationAgent/main.py`
- `NameGenerationAgent/config/api_config.py`
- `NameGenerationAgent/config/settings.py`
- `NameGenerationAgent/src/api/unified_client.py`
- `NameGenerationAgent/src/api/model_manager.py`
- `NameGenerationAgent/src/core/name_generator.py`
- `NameGenerationAgent/src/core/auth_service.py`
- `NameGenerationAgent/src/core/record_service.py`
- `NameGenerationAgent/src/db/database.py`
- `NameGenerationAgent/src/db/models.py`
- `NameGenerationAgent/src/web/app.py`
- `NameGenerationAgent/src/web/admin_views.py`
- `NameGenerationAgent/scripts/migrate_auth_sqlite_to_mysql.py`

## License

MIT
