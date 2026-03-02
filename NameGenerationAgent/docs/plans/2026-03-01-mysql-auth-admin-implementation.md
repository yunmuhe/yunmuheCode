# MySQL Auth + Admin Web Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将认证切换到 MySQL、加入管理员角色、构建 Web 管理后台，并将姓名生成记录与用户关联持久化。  
**Architecture:** 在现有 Flask 应用内新增 SQLAlchemy 数据层与记录服务层；保持现有 API 路径，扩展角色/状态字段；新增 `/admin` 模板后台与管理员接口。  
**Tech Stack:** Flask, SQLAlchemy, PyMySQL, Jinja2, pytest

---

### Task 1: 建立数据库基础设施

**Files:**
- Create: `NameGenerationAgent/src/db/__init__.py`
- Create: `NameGenerationAgent/src/db/database.py`
- Create: `NameGenerationAgent/src/db/models.py`
- Modify: `NameGenerationAgent/requirements.txt`
- Modify: `NameGenerationAgent/env.example`
- Test: `NameGenerationAgent/tests/test_db_models.py`

**Step 1: Write the failing test**
- 编写 `test_db_models.py`，断言模型可建表、关键字段存在（`role`, `is_enabled`, `must_change_password`, `generation_records`）。

**Step 2: Run test to verify it fails**
- Run: `pytest NameGenerationAgent/tests/test_db_models.py -q`
- Expected: FAIL（模块/模型不存在）

**Step 3: Write minimal implementation**
- 新建数据库引擎、Session、Base 和模型定义。
- 在 `requirements.txt` 增加 `SQLAlchemy`、`PyMySQL`。

**Step 4: Run test to verify it passes**
- Run: `pytest NameGenerationAgent/tests/test_db_models.py -q`
- Expected: PASS

### Task 2: 认证服务切换到 MySQL 并支持角色/状态

**Files:**
- Modify: `NameGenerationAgent/src/core/auth_service.py`
- Test: `NameGenerationAgent/tests/test_auth_endpoints.py`
- Create: `NameGenerationAgent/tests/test_auth_roles.py`

**Step 1: Write the failing test**
- 增加用例：
  - 注册默认 `role=user`
  - 禁用用户登录失败
  - `must_change_password` 字段在 `/auth/me` 可见

**Step 2: Run test to verify it fails**
- Run: `pytest NameGenerationAgent/tests/test_auth_endpoints.py NameGenerationAgent/tests/test_auth_roles.py -q`
- Expected: FAIL（旧服务不支持）

**Step 3: Write minimal implementation**
- 将 `AuthService` 改为 SQLAlchemy 实现，保留调用接口。
- 增加管理员初始化逻辑（基于环境变量）。

**Step 4: Run test to verify it passes**
- Run: `pytest NameGenerationAgent/tests/test_auth_endpoints.py NameGenerationAgent/tests/test_auth_roles.py -q`
- Expected: PASS

### Task 3: 生成记录与用户关联持久化

**Files:**
- Create: `NameGenerationAgent/src/core/record_service.py`
- Modify: `NameGenerationAgent/src/web/app.py`
- Create: `NameGenerationAgent/tests/test_user_generation_history.py`

**Step 1: Write the failing test**
- 用例覆盖：
  - 已登录用户调用 `/generate` 后写入 `generation_records`
  - `/history/list` 仅返回当前用户记录
  - 未登录调用 `/generate` 返回 401

**Step 2: Run test to verify it fails**
- Run: `pytest NameGenerationAgent/tests/test_user_generation_history.py -q`
- Expected: FAIL

**Step 3: Write minimal implementation**
- 在 `/generate` 成功后写入记录。
- `/history/list` 改查数据库并支持关键词分页。

**Step 4: Run test to verify it passes**
- Run: `pytest NameGenerationAgent/tests/test_user_generation_history.py -q`
- Expected: PASS

### Task 4: 管理员 Web 后台与管理接口

**Files:**
- Create: `NameGenerationAgent/src/web/admin_views.py`
- Create: `NameGenerationAgent/src/web/templates/admin/login.html`
- Create: `NameGenerationAgent/src/web/templates/admin/users.html`
- Create: `NameGenerationAgent/src/web/templates/admin/user_detail.html`
- Modify: `NameGenerationAgent/src/web/app.py`
- Create: `NameGenerationAgent/tests/test_admin_web.py`

**Step 1: Write the failing test**
- 用例覆盖：
  - 非管理员访问 `/admin` 与管理 API 被拒绝
  - 管理员可查询用户列表与详情
  - 可按时间筛选记录
  - 可删除记录
  - 可禁用/启用用户
  - 可重置密码为 `123456` 且 `must_change_password=true`

**Step 2: Run test to verify it fails**
- Run: `pytest NameGenerationAgent/tests/test_admin_web.py -q`
- Expected: FAIL

**Step 3: Write minimal implementation**
- 增加管理后台会话登录与管理员校验装饰器。
- 完成页面渲染与管理 API。

**Step 4: Run test to verify it passes**
- Run: `pytest NameGenerationAgent/tests/test_admin_web.py -q`
- Expected: PASS

### Task 5: SQLite 到 MySQL 迁移脚本

**Files:**
- Create: `NameGenerationAgent/scripts/migrate_auth_sqlite_to_mysql.py`
- Create: `NameGenerationAgent/tests/test_migration_script.py`
- Modify: `NameGenerationAgent/README.md`

**Step 1: Write the failing test**
- 构造临时 SQLite + 临时目标库，断言用户与 token 迁移成功。

**Step 2: Run test to verify it fails**
- Run: `pytest NameGenerationAgent/tests/test_migration_script.py -q`
- Expected: FAIL

**Step 3: Write minimal implementation**
- 实现可复用迁移函数 + 命令行入口。
- 输出迁移统计。

**Step 4: Run test to verify it passes**
- Run: `pytest NameGenerationAgent/tests/test_migration_script.py -q`
- Expected: PASS

### Task 6: 回归验证与清理

**Files:**
- Modify: `NameGenerationAgent/docs/API-DOCUMENTATION.md`
- Modify: `NameGenerationAgent/docs/API-QUICK-REFERENCE.md`
- Modify: `NameGenerationAgent/README.md`

**Step 1: Run focused test suite**
- Run: `pytest NameGenerationAgent/tests/test_db_models.py NameGenerationAgent/tests/test_auth_endpoints.py NameGenerationAgent/tests/test_auth_roles.py NameGenerationAgent/tests/test_user_generation_history.py NameGenerationAgent/tests/test_admin_web.py NameGenerationAgent/tests/test_migration_script.py -q`
- Expected: 全部 PASS

**Step 2: Run full project tests**
- Run: `pytest NameGenerationAgent/tests -q`
- Expected: PASS（如存在既有失败，记录并说明）

**Step 3: 文档更新**
- 更新接口、环境变量、管理员初始化与迁移说明。
