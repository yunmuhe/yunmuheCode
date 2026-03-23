# Custom Nav Bar Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 抽出一个共享的自定义导航栏组件，统一安全区、返回行为和公共样式，替换当前 7 个页面里重复维护的导航结构。

**Architecture:** 新增 `components/CustomNavBar.vue`，组件内统一处理左侧返回按钮、中间标题、右侧默认占位或具名插槽，以及顶部安全区。业务页面只负责传标题和右侧操作，不再重复维护 `.nav-bar/.back-btn/.page-title/.placeholder` 结构和样式。

**Tech Stack:** uni-app Vue 3、`<script setup>`、H5 构建验证

---

### Task 1: 新增共享导航组件

**Files:**
- Create: `智能姓名生成系统/components/CustomNavBar.vue`

**Steps:**
1. 创建组件，支持 `title`、`fallbackUrl`、`fallbackMode`、`showBack` 属性。
2. 提供右侧具名插槽，没有插槽时渲染固定宽度占位。
3. 组件内部统一处理安全区和默认返回逻辑。

### Task 2: 替换简单导航页面

**Files:**
- Modify: `智能姓名生成系统/pages/History/History.vue`
- Modify: `智能姓名生成系统/pages/Settings/Settings.vue`
- Modify: `智能姓名生成系统/pages/Admin/Admin.vue`
- Modify: `智能姓名生成系统/pages/agreement/agreement.vue`
- Modify: `智能姓名生成系统/pages/feedback/feedback.vue`

**Steps:**
1. 用共享组件替换页面顶部原始导航结构。
2. 删除页面内重复的导航样式和返回按钮图标导入。
3. 保留各页面原有业务逻辑和内容区样式。

### Task 3: 替换带右侧操作的导航页面

**Files:**
- Modify: `智能姓名生成系统/pages/Favorites/Favorites.vue`
- Modify: `智能姓名生成系统/pages/Generate/Generate.vue`

**Steps:**
1. 用共享组件替换页面顶部导航。
2. 通过右侧具名插槽保留编辑按钮和批量按钮。
3. 删除旧导航样式，仅保留右侧操作按钮自己的样式。

### Task 4: 验证

**Files:**
- Verify only

**Steps:**
1. 运行 `npm run build:h5`。
2. 搜索目标页面中的 `.nav-bar/.back-btn/.page-title/.placeholder`，确认重复代码已明显减少。
