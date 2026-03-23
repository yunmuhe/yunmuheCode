# Today Generated Stats Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让后端 `/stats` 直接返回当前登录用户的 `today_generated`，并让首页优先使用这个字段而不是前端翻页累计。

**Architecture:** 在 `RecordService` 增加一个面向用户的“今日生成计数”查询方法，`web/app.py` 的 `/stats` 接口在已登录场景下把这个值并入返回结果。前端首页继续调用现有 `/stats`，但只消费后端给出的准确统计值，不再自己翻页计算。

**Tech Stack:** Flask、SQLAlchemy、pytest、uni-app Vue 3

---

### Task 1: 为后端统计补失败测试

**Files:**
- Modify: `NameGenerationAgent/tests/test_user_generation_history.py`

**Steps:**
1. 增加一个测试，登录用户后创建多条生成记录，并断言 `/stats` 返回 `today_generated`。
2. 先运行这条测试，确认它因字段缺失而失败。

### Task 2: 实现后端今日生成统计

**Files:**
- Modify: `NameGenerationAgent/src/core/record_service.py`
- Modify: `NameGenerationAgent/src/web/app.py`

**Steps:**
1. 在 `RecordService` 中添加按当前自然日统计用户生成记录数的方法。
2. 在 `/stats` 中结合当前用户身份返回 `today_generated`，未登录时返回默认值。
3. 运行新增测试，确认通过。

### Task 3: 首页改回直接消费后端统计

**Files:**
- Modify: `智能姓名生成系统/pages/Index/Index.vue`

**Steps:**
1. 去掉首页的前端分页累计逻辑。
2. 首页改为并行请求 `/stats` 和 `/favorites`，直接使用 `stats.today_generated`。
3. 运行前端构建，确认通过。

### Task 4: 回归验证

**Files:**
- Verify only

**Steps:**
1. 运行后端相关测试。
2. 运行前端 `npm run build:h5`。
3. 记录结果与剩余风险。
