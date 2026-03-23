# Theme Token And TS Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为前端补齐正式主题状态 token，并把当前可控的前端 `.js` 源码迁移为 `.ts`，同时保持现有构建和基础测试可用。

**Architecture:** 主题部分继续沿用 `common/theme.ts` 的运行时 palette + CSS 变量方案，只补充缺失的 warning/disabled 状态 token，并替换生成页对应硬编码颜色。TS 迁移部分只覆盖前端源码中的 `main.js`、`uni.promisify.adaptor.js`、`phoneMask.js` 和 `phoneMask.test.js`，不触碰构建产物和依赖目录。

**Tech Stack:** uni-app Vue 3、TypeScript、Node.js 22、H5 build

---

### Task 1: 先写失败测试

**Files:**
- Create: `智能姓名生成系统/common/theme.test.ts`
- Modify: `智能姓名生成系统/common/phoneMask.test.js`

**Step 1:** 新增 `theme.test.ts`，断言 `createThemeCssVars` 返回 `--warning-soft`、`--warning-border`、`--disabled-bg`、`--disabled-text`、`--disabled-icon`。

**Step 2:** 先运行 `node --experimental-strip-types common/theme.test.ts`，确认因 token 尚未实现而失败。

**Step 3:** 将 `phoneMask.test.js` 迁移目标定为 `.ts` 入口，并先运行目标测试命令，确认在迁移前失败。

### Task 2: 实现主题 token

**Files:**
- Modify: `智能姓名生成系统/common/theme.ts`
- Modify: `智能姓名生成系统/pages/Generate/Generate.vue`

**Step 1:** 在 `ThemePalette` 和 `createThemeCssVars` 中新增 warning/disabled 相关字段。

**Step 2:** 为 light/dark palette 分别给出稳定取值。

**Step 3:** 将生成页 pending/disabled/error 的剩余颜色切换到正式 token。

### Task 3: 迁移前端 JS 到 TS

**Files:**
- Create: `智能姓名生成系统/tsconfig.json`
- Create: `智能姓名生成系统/main.ts`
- Create: `智能姓名生成系统/uni.promisify.adaptor.ts`
- Create: `智能姓名生成系统/common/phoneMask.ts`
- Create: `智能姓名生成系统/common/phoneMask.test.ts`
- Modify: `智能姓名生成系统/package.json`
- Delete: `智能姓名生成系统/main.js`
- Delete: `智能姓名生成系统/uni.promisify.adaptor.js`
- Delete: `智能姓名生成系统/common/phoneMask.js`
- Delete: `智能姓名生成系统/common/phoneMask.test.js`

**Step 1:** 将入口和工具函数迁成显式类型的 `.ts` 文件。

**Step 2:** 调整 `package.json` 的 `main` 指向与新增一个可运行 TS 测试的脚本。

**Step 3:** 保持现有页面对 `phoneMask` 的导入兼容。

### Task 4: 验证

**Files:**
- Verify only

**Step 1:** 运行 `node --experimental-strip-types common/theme.test.ts`

**Step 2:** 运行 `node --experimental-strip-types common/phoneMask.test.ts`

**Step 3:** 运行 `npm run build:h5`

**Step 4:** 如果全部通过，再做一次全量变更复查，确保仓库可控前端源码中不再残留 `.js` 文件。
