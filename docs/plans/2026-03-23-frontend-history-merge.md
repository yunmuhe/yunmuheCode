# Frontend History Merge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将前端目录 `智能姓名生成系统/` 从嵌套独立仓库并入主仓库，同时保留其历史提交和当前未提交改动。

**Architecture:** 先在前端子仓库中创建一个仅用于导入的本地快照提交，确保当前工作区状态进入子仓库历史。随后在主仓库中把该子仓库作为一个本地 remote 拉取，并用 `git subtree add` 将完整历史导入到 `智能姓名生成系统/` 前缀。确认导入成功后，再移除前端目录下的嵌套 `.git`，让主仓库直接跟踪该目录。

**Tech Stack:** Git nested repository、git subtree、PowerShell

---

### Task 1: 固化子仓库当前状态

**Files:**
- Modify: `智能姓名生成系统/` 工作区

**Step 1:** 在子仓库创建临时分支，避免直接污染已有分支。

**Step 2:** 将当前未提交改动提交为本地快照提交。

**Step 3:** 记录快照提交 SHA，作为后续 subtree 导入基准。

### Task 2: 将子仓库历史并入主仓库

**Files:**
- Modify: 主仓库 `.git` 元数据

**Step 1:** 在主仓库添加一个指向前端子仓库的本地 remote。

**Step 2:** 获取该 remote 的快照分支。

**Step 3:** 用 `git subtree add --prefix="智能姓名生成系统"` 导入前端完整历史。

### Task 3: 清理嵌套仓库标记

**Files:**
- Modify: `智能姓名生成系统/.git`

**Step 1:** 确认 subtree 导入完成且主仓库能看到前端目录内容。

**Step 2:** 删除 `智能姓名生成系统/.git`，让目录转为主仓库普通子目录。

**Step 3:** 再次验证主仓库状态，确保不再把该目录视为嵌套仓库。

### Task 4: 验证

**Files:**
- Verify only

**Step 1:** 运行主仓库 `git status --short`

**Step 2:** 运行主仓库 `git log --oneline -- 智能姓名生成系统`

**Step 3:** 运行前端 `npm run build:h5`，确认并仓后目录仍可正常构建。
