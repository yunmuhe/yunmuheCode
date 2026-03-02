# MySQL 认证与管理员后台设计

**目标**
- 将注册/登录数据从 SQLite 切换为 MySQL 持久化。
- 引入 `admin` / `user` 角色与账户状态管理（启用/禁用、强制改密）。
- 将姓名生成记录与用户关联持久化。
- 提供 Flask Web 管理后台（浏览器访问）。

**边界与约束**
- 沿用现有 Flask 应用，不拆分独立服务。
- 管理后台使用 Flask 模板渲染，不使用 uni-app。
- 现有 SQLite `auth.db` 中仅 `users` 和 `user_tokens` 可迁移；历史记录原在 session，不存在可迁移历史表。

**核心架构**
- 新增数据库层：
  - `src/db/database.py`: SQLAlchemy 引擎、会话工厂、基础类、初始化入口。
  - `src/db/models.py`: `User`、`UserToken`、`GenerationRecord` 三类模型。
- 新增服务层：
  - `src/core/auth_service.py`: 改为 MySQL 实现，保留原有接口签名并扩展角色/状态字段。
  - `src/core/record_service.py`: 负责生成记录写入、按用户分页查询、管理员查询/删除。
- 新增管理后台模块：
  - `src/web/admin_views.py` + `src/web/templates/admin/*`。
  - 管理员登录态使用 server-side session，普通 API 鉴权继续沿用 Bearer token。

**数据模型**
- `users`
  - `id, phone(unique), password_hash`
  - `role(enum: admin/user)`
  - `is_enabled(bool)`
  - `must_change_password(bool)`
  - `created_at, updated_at, last_login_at`
- `user_tokens`
  - `token(pk), user_id(fk), created_at, expires_at, revoked`
- `generation_records`
  - `id(pk), user_id(fk), description, cultural_style, gender, age`
  - `request_count, api_name, model, names_json`
  - `created_at`

**鉴权与角色规则**
- 注册默认 `role=user`、`is_enabled=true`、`must_change_password=false`。
- 登录前校验 `is_enabled`，禁用用户拒绝登录。
- 管理员重置密码：
  - 统一改为 `123456`
  - 置 `must_change_password=true`
- 系统启动时通过 `.env` 自动创建管理员（不存在则创建，存在则确保角色为 admin）。

**接口变更**
- 保持现有 `/auth/register`、`/auth/login`、`/auth/me`、`/auth/logout` 路径不变。
- `/auth/me` 返回用户角色和状态字段。
- `/generate` 要求登录；成功后写入 `generation_records`。
- `/history/list` 改为查当前登录用户的 `generation_records`。
- 新增管理接口（示例）：
  - `GET /admin/api/users`
  - `GET /admin/api/users/<id>`
  - `POST /admin/api/users/<id>/enable`
  - `POST /admin/api/users/<id>/disable`
  - `POST /admin/api/users/<id>/reset-password`
  - `DELETE /admin/api/records/<id>`

**Web 管理后台页面**
- `/admin/login`: 管理员登录页。
- `/admin`: 用户列表 + 搜索（手机号/角色/状态）。
- `/admin/users/<id>`: 用户详情、用户生成历史、按时间筛选、删除记录。

**迁移方案**
- 新增脚本 `scripts/migrate_auth_sqlite_to_mysql.py`：
  - 输入 SQLite 路径与 MySQL 连接信息。
  - 迁移 `users`、`user_tokens`。
  - 迁移前后输出统计。
- 历史记录无法从旧 session 迁移，改造后开始累积。

**测试策略**
- 保留并改造现有认证流测试。
- 新增测试：
  - 角色与状态（禁用、强制改密）。
  - 生成记录入库与按用户隔离。
  - 管理员接口授权与核心行为（查询/禁用启用/重置密码/删除记录）。
  - 迁移脚本最小数据迁移验证。

**风险与应对**
- MySQL 连接不可用：通过环境变量与启动时连通性检查给出明确错误。
- 历史数据迁移预期偏差：在文档和日志中明确“旧 session 历史不可迁移”。
- 后台越权访问：统一管理员校验装饰器并覆盖测试。
